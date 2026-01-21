from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, BPULibrary, CompanyBranding, TaxProfile, PricingTier
from werkzeug.utils import secure_filename
import os

onboarding_bp = Blueprint('onboarding', __name__)

COUNTRIES = {
    'MA': {'name': 'Maroc', 'currency': 'MAD', 'vat': 20.00},
    'FR': {'name': 'France', 'currency': 'EUR', 'vat': 20.00},
    'TN': {'name': 'Tunisie', 'currency': 'TND', 'vat': 19.00},
    'DZ': {'name': 'Algérie', 'currency': 'DZD', 'vat': 19.00},
    'SN': {'name': 'Sénégal', 'currency': 'XOF', 'vat': 18.00},
    'CI': {'name': 'Côte d\'Ivoire', 'currency': 'XOF', 'vat': 18.00},
}


@onboarding_bp.route('/')
@login_required
def index():
    company = current_user.company
    
    if company.onboarding_completed:
        return redirect(url_for('main.dashboard'))
    
    step = company.onboarding_step
    
    if step == 1:
        return redirect(url_for('onboarding.step_country'))
    elif step == 2:
        return redirect(url_for('onboarding.step_tax'))
    elif step == 3:
        return redirect(url_for('onboarding.step_bpu'))
    elif step == 4:
        return redirect(url_for('onboarding.step_tiers'))
    elif step == 5:
        return redirect(url_for('onboarding.step_branding'))
    else:
        return redirect(url_for('onboarding.step_complete'))


@onboarding_bp.route('/country', methods=['GET', 'POST'])
@login_required
def step_country():
    company = current_user.company
    
    if request.method == 'POST':
        country = request.form.get('country', 'MA')
        
        if country in COUNTRIES:
            company.country = country
            company.currency = COUNTRIES[country]['currency']
            company.onboarding_step = 2
            
            tax_profile = company.tax_profile
            if tax_profile:
                tax_profile.default_vat_rate = COUNTRIES[country]['vat']
            
            db.session.commit()
            
            flash('Pays configuré avec succès!', 'success')
            return redirect(url_for('onboarding.step_tax'))
        else:
            flash('Pays invalide.', 'error')
    
    return render_template('onboarding/country.html', countries=COUNTRIES, current_country=company.country)


@onboarding_bp.route('/tax', methods=['GET', 'POST'])
@login_required
def step_tax():
    company = current_user.company
    tax_profile = company.tax_profile
    
    if request.method == 'POST':
        tax_profile.default_vat_rate = request.form.get('vat_rate', type=float) or 20.00
        tax_profile.vat_included = request.form.get('vat_included') == 'on'
        tax_profile.payment_terms_days = request.form.get('payment_terms', type=int) or 30
        tax_profile.deposit_percentage = request.form.get('deposit', type=float) or 30.00
        tax_profile.payment_conditions = request.form.get('payment_conditions', '').strip()
        
        company.onboarding_step = 3
        db.session.commit()
        
        flash('Profil fiscal configuré!', 'success')
        return redirect(url_for('onboarding.step_bpu'))
    
    return render_template('onboarding/tax.html', tax_profile=tax_profile)


@onboarding_bp.route('/bpu', methods=['GET', 'POST'])
@login_required
def step_bpu():
    company = current_user.company
    
    libraries = BPULibrary.query.filter_by(country=company.country, is_active=True)\
        .order_by(BPULibrary.version.desc()).all()
    
    if request.method == 'POST':
        company.onboarding_step = 4
        db.session.commit()
        
        flash('Bibliothèque BPU activée!', 'success')
        return redirect(url_for('onboarding.step_tiers'))
    
    return render_template('onboarding/bpu.html', libraries=libraries)


@onboarding_bp.route('/tiers', methods=['GET', 'POST'])
@login_required
def step_tiers():
    company = current_user.company
    tiers = company.pricing_tiers.order_by(PricingTier.sort_order).all()
    
    if request.method == 'POST':
        for tier in tiers:
            coef_key = f'coefficient_{tier.id}'
            round_key = f'rounding_{tier.id}'
            default_key = f'default_{tier.id}'
            
            if coef_key in request.form:
                tier.coefficient = request.form.get(coef_key, type=float) or 1.00
            if round_key in request.form:
                tier.rounding = request.form.get(round_key, type=int) or 2
            
            tier.is_default = (request.form.get('default_tier') == str(tier.id))
        
        company.onboarding_step = 5
        db.session.commit()
        
        flash('Gammes de prix configurées!', 'success')
        return redirect(url_for('onboarding.step_branding'))
    
    return render_template('onboarding/tiers.html', tiers=tiers)


@onboarding_bp.route('/branding', methods=['GET', 'POST'])
@login_required
def step_branding():
    company = current_user.company
    branding = company.branding
    
    if request.method == 'POST':
        branding.legal_name = request.form.get('legal_name', '').strip() or company.name
        branding.address = request.form.get('address', '').strip()
        branding.phone = request.form.get('phone', '').strip()
        branding.email = request.form.get('email', '').strip()
        branding.website = request.form.get('website', '').strip()
        branding.registration_number = request.form.get('registration_number', '').strip()
        branding.tax_id = request.form.get('tax_id', '').strip()
        branding.bank_details = request.form.get('bank_details', '').strip()
        branding.quote_footer = request.form.get('quote_footer', '').strip()
        branding.quote_terms = request.form.get('quote_terms', '').strip()
        
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo.filename:
                filename = secure_filename(logo.filename)
                upload_dir = os.path.join('static', 'uploads', str(company.id))
                os.makedirs(upload_dir, exist_ok=True)
                logo_path = os.path.join(upload_dir, f'logo_{filename}')
                logo.save(logo_path)
                branding.logo_path = logo_path
        
        company.onboarding_step = 6
        db.session.commit()
        
        flash('Identité visuelle configurée!', 'success')
        return redirect(url_for('onboarding.step_complete'))
    
    return render_template('onboarding/branding.html', branding=branding)


@onboarding_bp.route('/complete', methods=['GET', 'POST'])
@login_required
def step_complete():
    company = current_user.company
    
    if request.method == 'POST':
        company.onboarding_completed = True
        db.session.commit()
        
        flash('Configuration terminée! Bienvenue dans votre espace.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('onboarding/complete.html')
