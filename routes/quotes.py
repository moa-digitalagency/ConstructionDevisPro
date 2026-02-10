from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models import db, Quote, QuoteVersion, QuoteLine, QuoteAssumption, Project, QuoteStatus, AuditLog
from security.decorators import require_permission
from security.audit import log_action
from services.quote_generator import QuoteGenerator
from services.export_service import ExportService
from datetime import datetime, timedelta

quotes_bp = Blueprint('quotes', __name__)


@quotes_bp.route('/')
@login_required
def index():
    company = current_user.company
    status_filter = request.args.get('status', '')
    
    query = Quote.query.join(Project).filter(Project.company_id == company.id)
    
    if status_filter:
        try:
            status = QuoteStatus(status_filter)
            query = query.filter(Quote.status == status)
        except ValueError:
            pass
    
    quotes = query.order_by(Quote.updated_at.desc()).all()
    
    return render_template('quotes/index.html',
        quotes=quotes,
        quote_statuses=QuoteStatus,
        current_status=status_filter
    )


@quotes_bp.route('/project/<int:project_id>/new', methods=['GET', 'POST'])
@login_required
@require_permission('can_manage_quotes')
def new(project_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    
    if request.method == 'POST':
        tier_id = request.form.get('tier_id')
        valid_days = int(request.form.get('valid_days', 30))
        notes = request.form.get('notes', '').strip()
        
        quote = Quote(
            project_id=project_id,
            status=QuoteStatus.DRAFT,
            valid_until=datetime.utcnow().date() + timedelta(days=valid_days),
            notes=notes
        )
        quote.generate_reference()
        db.session.add(quote)
        db.session.flush()
        
        generator = QuoteGenerator(project, tier_id)
        version = generator.generate_version(quote)
        
        db.session.commit()
        
        log_action('create', 'quote', quote.id, None, {'reference': quote.reference})
        
        flash('Devis créé avec succès!', 'success')
        return redirect(url_for('quotes.view', quote_id=quote.id))
    
    # Ensure tiers exist before rendering to avoid empty dropdown
    current_user.company.ensure_default_tiers()

    return render_template('quotes/new.html',
        project=project,
        tiers=current_user.company.pricing_tiers.all()
    )


@quotes_bp.route('/<int:quote_id>')
@login_required
def view(quote_id):
    quote = Quote.query.join(Project).filter(
        Quote.id == quote_id,
        Project.company_id == current_user.company_id
    ).first_or_404()
    
    current_version = quote.versions.filter_by(version_number=quote.current_version).first()
    
    logs = AuditLog.query.filter_by(
        entity_type='quote',
        entity_id=quote.id
    ).order_by(AuditLog.created_at.desc()).all()

    return render_template('quotes/view.html', quote=quote, current_version=current_version, logs=logs)


@quotes_bp.route('/<int:quote_id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('can_manage_quotes')
def edit(quote_id):
    quote = Quote.query.join(Project).filter(
        Quote.id == quote_id,
        Project.company_id == current_user.company_id
    ).first_or_404()
    
    current_version = quote.versions.filter_by(version_number=quote.current_version).first()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'save':
            quote.notes = request.form.get('notes', '').strip()
            quote.internal_notes = request.form.get('internal_notes', '').strip()
            db.session.commit()
            flash('Devis enregistré.', 'success')
        
        elif action == 'new_version':
            new_version_number = quote.current_version + 1
            
            new_version = QuoteVersion(
                quote_id=quote.id,
                version_number=new_version_number,
                tier_id=current_version.tier_id,
                vat_rate=current_version.vat_rate,
                created_by_id=current_user.id
            )
            db.session.add(new_version)
            db.session.flush()
            
            for line in current_version.lines:
                new_line = QuoteLine(
                    version_id=new_version.id,
                    article_id=line.article_id,
                    custom_article_id=line.custom_article_id,
                    category=line.category,
                    designation=line.designation,
                    unit=line.unit,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    total_price=line.total_price,
                    measurement_id=line.measurement_id,
                    room_id=line.room_id,
                    quantity_source=line.quantity_source,
                    sort_order=line.sort_order
                )
                db.session.add(new_line)
            
            for assumption in current_version.assumptions:
                new_assumption = QuoteAssumption(
                    version_id=new_version.id,
                    category=assumption.category,
                    description=assumption.description,
                    value=assumption.value,
                    is_confirmed=assumption.is_confirmed,
                    source=assumption.source
                )
                db.session.add(new_assumption)
            
            quote.current_version = new_version_number
            
            new_version.subtotal_ht = sum(line.total_price for line in new_version.lines)
            new_version.vat_amount = new_version.subtotal_ht * (new_version.vat_rate or 20) / 100
            new_version.total_ttc = new_version.subtotal_ht + new_version.vat_amount
            
            db.session.commit()
            
            log_action('new_version', 'quote', quote.id, 
                {'old_version': current_version.version_number}, 
                {'new_version': new_version_number}
            )
            
            flash(f'Nouvelle version V{new_version_number} créée.', 'success')
            return redirect(url_for('quotes.edit', quote_id=quote.id))
        
        return redirect(url_for('quotes.view', quote_id=quote.id))
    
    return render_template('quotes/edit.html', quote=quote, current_version=current_version)


@quotes_bp.route('/<int:quote_id>/export/pdf')
@login_required
@require_permission('can_export')
def export_pdf(quote_id):
    quote = Quote.query.join(Project).filter(
        Quote.id == quote_id,
        Project.company_id == current_user.company_id
    ).first_or_404()
    
    current_version = quote.versions.filter_by(version_number=quote.current_version).first()
    
    export_service = ExportService(current_user.company)
    pdf_path = export_service.generate_pdf(quote, current_version)
    
    log_action('export_pdf', 'quote', quote.id, None, {'version': current_version.version_number})
    
    return send_file(pdf_path, as_attachment=True, download_name=f"{quote.reference}_V{current_version.version_number}.pdf")


@quotes_bp.route('/<int:quote_id>/export/excel')
@login_required
@require_permission('can_export')
def export_excel(quote_id):
    quote = Quote.query.join(Project).filter(
        Quote.id == quote_id,
        Project.company_id == current_user.company_id
    ).first_or_404()
    
    current_version = quote.versions.filter_by(version_number=quote.current_version).first()
    
    export_service = ExportService(current_user.company)
    excel_path = export_service.generate_excel(quote, current_version)
    
    log_action('export_excel', 'quote', quote.id, None, {'version': current_version.version_number})
    
    return send_file(excel_path, as_attachment=True, download_name=f"{quote.reference}_DQE_V{current_version.version_number}.xlsx")


@quotes_bp.route('/<int:quote_id>/status', methods=['POST'])
@login_required
@require_permission('can_manage_quotes')
def update_status(quote_id):
    quote = Quote.query.join(Project).filter(
        Quote.id == quote_id,
        Project.company_id == current_user.company_id
    ).first_or_404()
    
    new_status = request.form.get('status')
    
    try:
        old_status = quote.status.value
        quote.status = QuoteStatus(new_status)
        db.session.commit()
        
        log_action('status_change', 'quote', quote.id, 
            {'old_status': old_status}, 
            {'new_status': new_status}
        )
        
        flash('Statut mis à jour.', 'success')
    except ValueError:
        flash('Statut invalide.', 'error')
    
    return redirect(url_for('quotes.view', quote_id=quote.id))
