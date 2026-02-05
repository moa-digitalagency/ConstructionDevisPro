from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from models import db, BPULibrary, BPUArticle, CompanyBPUOverride, CompanyBPUArticle
from security.decorators import require_permission
from security.audit import log_action
from services.bpu_service import BPUService
import io

bpu_bp = Blueprint('bpu', __name__)


@bpu_bp.route('/')
@login_required
def index():
    company = current_user.company
    
    library = BPULibrary.query.filter_by(country=company.country, is_active=True)\
        .order_by(BPULibrary.version.desc()).first()
    
    if not library:
        flash('Aucune bibliothèque BPU disponible pour votre pays.', 'warning')
        return render_template('bpu/index.html', library=None, categories=[])
    
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = BPUArticle.query.filter_by(library_id=library.id)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            db.or_(
                BPUArticle.code.ilike(f'%{search}%'),
                BPUArticle.designation.ilike(f'%{search}%')
            )
        )
    
    articles = query.order_by(BPUArticle.category, BPUArticle.sort_order).all()
    
    categories = db.session.query(BPUArticle.category)\
        .filter_by(library_id=library.id)\
        .distinct()\
        .order_by(BPUArticle.category)\
        .all()
    categories = [c[0] for c in categories]
    
    overrides = {o.article_id: o for o in company.bpu_overrides.all()}
    
    return render_template('bpu/index.html',
        library=library,
        articles=articles,
        categories=categories,
        overrides=overrides,
        current_category=category,
        search_term=search
    )


@bpu_bp.route('/custom')
@login_required
def custom_articles():
    company = current_user.company
    articles = company.custom_articles.filter_by(is_active=True).order_by(CompanyBPUArticle.category, CompanyBPUArticle.sort_order).all()
    return render_template('bpu/custom.html', articles=articles)


@bpu_bp.route('/custom/new', methods=['GET', 'POST'])
@login_required
@require_permission('can_manage_bpu')
def new_custom_article():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        category = request.form.get('category', '').strip()
        subcategory = request.form.get('subcategory', '').strip()
        designation = request.form.get('designation', '').strip()
        unit = request.form.get('unit', '').strip()
        price_eco = request.form.get('price_eco', type=float)
        price_std = request.form.get('price_std', type=float)
        price_prem = request.form.get('price_prem', type=float)
        
        if not all([code, category, designation, unit]):
            flash('Tous les champs obligatoires doivent être remplis.', 'error')
            return render_template('bpu/custom_form.html', article=None)
        
        existing = CompanyBPUArticle.query.filter_by(
            company_id=current_user.company_id,
            code=code
        ).first()
        
        if existing:
            flash('Un article avec ce code existe déjà.', 'error')
            return render_template('bpu/custom_form.html', article=None)
        
        article = CompanyBPUArticle(
            company_id=current_user.company_id,
            code=code,
            category=category,
            subcategory=subcategory,
            designation=designation,
            unit=unit,
            unit_price_eco=price_eco,
            unit_price_standard=price_std,
            unit_price_premium=price_prem
        )
        db.session.add(article)
        db.session.commit()
        
        log_action('create', 'bpu_article', article.id, None, {'code': code, 'designation': designation})
        
        flash('Article créé avec succès!', 'success')
        return redirect(url_for('bpu.custom_articles'))
    
    categories = db.session.query(CompanyBPUArticle.category)\
        .filter_by(company_id=current_user.company_id)\
        .distinct().all()
    categories = sorted([c[0] for c in categories])

    return render_template('bpu/custom_form.html', article=None, categories=categories)


@bpu_bp.route('/custom/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('can_manage_bpu')
def edit_custom_article(article_id):
    article = CompanyBPUArticle.query.filter_by(
        id=article_id,
        company_id=current_user.company_id
    ).first_or_404()

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        category = request.form.get('category', '').strip()
        subcategory = request.form.get('subcategory', '').strip()
        designation = request.form.get('designation', '').strip()
        unit = request.form.get('unit', '').strip()
        price_eco = request.form.get('price_eco', type=float)
        price_std = request.form.get('price_std', type=float)
        price_prem = request.form.get('price_prem', type=float)

        if not all([code, category, designation, unit]):
            flash('Tous les champs obligatoires doivent être remplis.', 'error')
            return render_template('bpu/custom_form.html', article=article)

        # Check uniqueness of code only if changed
        if code != article.code:
            existing = CompanyBPUArticle.query.filter_by(
                company_id=current_user.company_id,
                code=code
            ).first()
            if existing:
                flash('Un article avec ce code existe déjà.', 'error')
                return render_template('bpu/custom_form.html', article=article)

        old_values = {
            'code': article.code,
            'category': article.category,
            'designation': article.designation,
            'price_std': float(article.unit_price_standard) if article.unit_price_standard else None
        }

        article.code = code
        article.category = category
        article.subcategory = subcategory
        article.designation = designation
        article.unit = unit
        article.unit_price_eco = price_eco
        article.unit_price_standard = price_std
        article.unit_price_premium = price_prem

        db.session.commit()

        log_action('update', 'bpu_article', article.id, old_values, {'code': code})

        flash('Article modifié avec succès!', 'success')
        return redirect(url_for('bpu.custom_articles'))

    categories = db.session.query(CompanyBPUArticle.category)\
        .filter_by(company_id=current_user.company_id)\
        .distinct().all()
    categories = sorted([c[0] for c in categories])

    return render_template('bpu/custom_form.html', article=article, categories=categories)


@bpu_bp.route('/custom/<int:article_id>/delete', methods=['POST'])
@login_required
@require_permission('can_manage_bpu')
def delete_custom_article(article_id):
    article = CompanyBPUArticle.query.filter_by(
        id=article_id,
        company_id=current_user.company_id
    ).first_or_404()

    # Soft delete
    article.is_active = False
    db.session.commit()

    log_action('delete', 'bpu_article', article.id, None, {'code': article.code})

    flash('Article supprimé.', 'success')
    return redirect(url_for('bpu.custom_articles'))


@bpu_bp.route('/article/<int:article_id>/override', methods=['POST'])
@login_required
@require_permission('can_manage_bpu')
def override_article(article_id):
    article = BPUArticle.query.get_or_404(article_id)
    company = current_user.company
    
    override = CompanyBPUOverride.query.filter_by(
        company_id=company.id,
        article_id=article_id
    ).first()
    
    if not override:
        override = CompanyBPUOverride(company_id=company.id, article_id=article_id)
        db.session.add(override)
    
    old_values = {
        'price_eco': float(override.unit_price_eco) if override.unit_price_eco else None,
        'price_std': float(override.unit_price_standard) if override.unit_price_standard else None,
        'price_prem': float(override.unit_price_premium) if override.unit_price_premium else None,
        'disabled': override.is_disabled
    }
    
    designation = request.form.get('designation', '').strip()
    price_eco = request.form.get('price_eco', type=float)
    price_std = request.form.get('price_std', type=float)
    price_prem = request.form.get('price_prem', type=float)
    is_disabled = request.form.get('is_disabled') == 'on'
    
    if designation:
        override.designation_override = designation
    override.unit_price_eco = price_eco
    override.unit_price_standard = price_std
    override.unit_price_premium = price_prem
    override.is_disabled = is_disabled
    
    db.session.commit()
    
    new_values = {
        'price_eco': price_eco,
        'price_std': price_std,
        'price_prem': price_prem,
        'disabled': is_disabled
    }
    
    log_action('override', 'bpu_article', article_id, old_values, new_values)
    
    flash('Modification enregistrée.', 'success')
    return redirect(url_for('bpu.index'))


@bpu_bp.route('/export')
@login_required
@require_permission('can_export')
def export_excel():
    company = current_user.company
    bpu_service = BPUService(company)
    excel_buffer = bpu_service.export_to_excel()
    
    log_action('export', 'bpu', None, None, {'format': 'excel'})
    
    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name=f"BPU_{company.slug}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@bpu_bp.route('/import', methods=['POST'])
@login_required
@require_permission('can_manage_bpu')
def import_excel():
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné.', 'error')
        return redirect(url_for('bpu.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Aucun fichier sélectionné.', 'error')
        return redirect(url_for('bpu.index'))
    
    if not file.filename.endswith('.xlsx'):
        flash('Format de fichier invalide. Utilisez un fichier Excel (.xlsx).', 'error')
        return redirect(url_for('bpu.index'))
    
    bpu_service = BPUService(current_user.company)
    result = bpu_service.import_from_excel(file)
    
    if result['success']:
        log_action('import', 'bpu', None, None, result['stats'])
        flash(f"Import réussi: {result['stats']['created']} créés, {result['stats']['updated']} mis à jour.", 'success')
    else:
        flash(f"Erreur lors de l'import: {result['error']}", 'error')
    
    return redirect(url_for('bpu.index'))


@bpu_bp.route('/categories')
@login_required
def categories():
    company = current_user.company

    # Get categories from Standard BPU (Library)
    library = BPULibrary.query.filter_by(country=company.country, is_active=True)\
        .order_by(BPULibrary.version.desc()).first()

    lib_categories = []
    if library:
        lib_cats = db.session.query(BPUArticle.category)\
            .filter_by(library_id=library.id)\
            .distinct().all()
        lib_categories = [c[0] for c in lib_cats]

    # Get categories from Custom BPU
    custom_cats = db.session.query(CompanyBPUArticle.category)\
        .filter_by(company_id=company.id, is_active=True)\
        .distinct().all()
    custom_categories = [c[0] for c in custom_cats]

    # Merge and sort
    all_categories = sorted(list(set(lib_categories + custom_categories)))

    return render_template('bpu/categories.html', categories=all_categories)


@bpu_bp.route('/categories/rename', methods=['POST'])
@login_required
@require_permission('can_manage_bpu')
def rename_category():
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')

    if not old_name or not new_name:
        flash('Noms invalides.', 'error')
        return redirect(url_for('bpu.categories'))

    # Update Custom Articles
    count = CompanyBPUArticle.query.filter_by(
        company_id=current_user.company_id,
        category=old_name
    ).update({CompanyBPUArticle.category: new_name})

    db.session.commit()

    if count > 0:
        flash(f'{count} articles personnalisés mis à jour.', 'success')
    else:
        flash('Aucun article personnalisé trouvé dans cette catégorie (les catégories standard ne peuvent pas être renommées).', 'warning')

    return redirect(url_for('bpu.categories'))


@bpu_bp.route('/categories/delete', methods=['POST'])
@login_required
@require_permission('can_manage_bpu')
def delete_category():
    name = request.form.get('name')

    # Soft delete all custom articles in this category
    count = CompanyBPUArticle.query.filter_by(
        company_id=current_user.company_id,
        category=name
    ).update({CompanyBPUArticle.is_active: False})

    db.session.commit()

    if count > 0:
        flash(f'Catégorie supprimée ({count} articles archivés).', 'success')
    else:
        flash('Aucun article personnalisé trouvé dans cette catégorie (les catégories standard ne peuvent pas être supprimées).', 'warning')

    return redirect(url_for('bpu.categories'))
