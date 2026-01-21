from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Role, UserRole, AuditLog, Company
from security.decorators import require_permission
from security.audit import log_action

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@require_permission('can_manage_users')
def index():
    company = current_user.company
    users = User.query.filter_by(company_id=company.id).order_by(User.created_at.desc()).all()
    return render_template('admin/index.html', users=users)


@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@require_permission('can_manage_users')
def new_user():
    roles = Role.query.all()
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '')
        role_ids = request.form.getlist('roles')
        
        if not email or not password:
            flash('Email et mot de passe sont requis.', 'error')
            return render_template('admin/user_form.html', user=None, roles=roles)
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'error')
            return render_template('admin/user_form.html', user=None, roles=roles)
        
        user = User(
            company_id=current_user.company_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        for role_id in role_ids:
            user_role = UserRole(user_id=user.id, role_id=int(role_id))
            db.session.add(user_role)
        
        db.session.commit()
        
        log_action('create', 'user', user.id, None, {'email': email, 'roles': role_ids})
        
        flash('Utilisateur créé avec succès!', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/user_form.html', user=None, roles=roles)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('can_manage_users')
def edit_user(user_id):
    user = User.query.filter_by(id=user_id, company_id=current_user.company_id).first_or_404()
    roles = Role.query.all()
    
    if request.method == 'POST':
        user.first_name = request.form.get('first_name', '').strip()
        user.last_name = request.form.get('last_name', '').strip()
        user.is_active = request.form.get('is_active') == 'on'
        
        new_password = request.form.get('password', '').strip()
        if new_password:
            user.set_password(new_password)
        
        role_ids = request.form.getlist('roles')
        
        UserRole.query.filter_by(user_id=user.id).delete()
        for role_id in role_ids:
            user_role = UserRole(user_id=user.id, role_id=int(role_id))
            db.session.add(user_role)
        
        db.session.commit()
        
        log_action('update', 'user', user.id, None, {'roles': role_ids})
        
        flash('Utilisateur mis à jour.', 'success')
        return redirect(url_for('admin.index'))
    
    user_role_ids = [ur.role_id for ur in user.roles]
    
    return render_template('admin/user_form.html', user=user, roles=roles, user_role_ids=user_role_ids)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@require_permission('can_manage_users')
def toggle_user(user_id):
    user = User.query.filter_by(id=user_id, company_id=current_user.company_id).first_or_404()
    
    if user.is_company_owner:
        flash('Impossible de désactiver le propriétaire de l\'entreprise.', 'error')
        return redirect(url_for('admin.index'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activé' if user.is_active else 'désactivé'
    log_action('toggle', 'user', user.id, None, {'is_active': user.is_active})
    flash(f'Utilisateur {status}.', 'success')
    
    return redirect(url_for('admin.index'))


@admin_bp.route('/audit-log')
@login_required
@require_permission('can_manage_users')
def audit_log():
    company = current_user.company
    page = request.args.get('page', 1, type=int)
    
    logs = AuditLog.query.filter_by(company_id=company.id)\
        .order_by(AuditLog.created_at.desc())\
        .paginate(page=page, per_page=50, error_out=False)
    
    return render_template('admin/audit_log.html', logs=logs)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@require_permission('can_manage_users')
def settings():
    from models import CompanyBranding, TaxProfile
    
    company = current_user.company
    
    if not company.branding:
        branding = CompanyBranding(company_id=company.id)
        db.session.add(branding)
        db.session.commit()
    branding = company.branding
    
    if not company.tax_profile:
        tax_profile = TaxProfile(company_id=company.id)
        db.session.add(tax_profile)
        db.session.commit()
    tax_profile = company.tax_profile
    
    if request.method == 'POST':
        section = request.form.get('section')
        
        if section == 'company':
            company.name = request.form.get('name', '').strip()
            branding.legal_name = request.form.get('legal_name', '').strip()
            branding.address = request.form.get('address', '').strip()
            branding.phone = request.form.get('phone', '').strip()
            branding.email = request.form.get('email', '').strip()
            branding.website = request.form.get('website', '').strip()
            branding.registration_number = request.form.get('registration_number', '').strip()
            branding.tax_id = request.form.get('tax_id', '').strip()
        
        elif section == 'tax':
            tax_profile.default_vat_rate = request.form.get('vat_rate', type=float) or 20.00
            tax_profile.payment_terms_days = request.form.get('payment_terms', type=int) or 30
            tax_profile.deposit_percentage = request.form.get('deposit', type=float) or 30.00
            tax_profile.payment_conditions = request.form.get('payment_conditions', '').strip()
        
        elif section == 'branding':
            branding.primary_color = request.form.get('primary_color', '#1a56db')
            branding.secondary_color = request.form.get('secondary_color', '#1e40af')
            branding.quote_footer = request.form.get('quote_footer', '').strip()
            branding.quote_terms = request.form.get('quote_terms', '').strip()
            branding.bank_details = request.form.get('bank_details', '').strip()
            
            if 'logo' in request.files:
                logo = request.files['logo']
                if logo.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(logo.filename)
                    upload_dir = os.path.join('static', 'uploads', str(company.id))
                    os.makedirs(upload_dir, exist_ok=True)
                    logo_path = os.path.join(upload_dir, f'logo_{filename}')
                    logo.save(logo_path)
                    branding.logo_path = logo_path
        
        db.session.commit()
        
        log_action('update', 'settings', company.id, None, {'section': section})
        flash('Paramètres enregistrés.', 'success')
        
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', company=company, branding=branding, tax_profile=tax_profile)
