from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Company, CompanyBranding, TaxProfile, PricingTier, Role, UserRole
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_slug(name):
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug[:50]


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if not current_user.company.onboarding_completed:
            return redirect(url_for('onboarding.index'))
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Veuillez remplir tous les champs.', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Votre compte a été désactivé.', 'error')
                return render_template('auth/login.html')
            
            if not user.company.is_active:
                flash('L\'entreprise a été désactivée.', 'error')
                return render_template('auth/login.html')
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            
            next_page = request.args.get('next')
            if not user.company.onboarding_completed:
                return redirect(url_for('onboarding.index'))
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        
        flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        errors = []
        
        if not company_name:
            errors.append('Le nom de l\'entreprise est requis.')
        if not email or not is_valid_email(email):
            errors.append('Email invalide.')
        if len(password) < 8:
            errors.append('Le mot de passe doit contenir au moins 8 caractères.')
        if password != password_confirm:
            errors.append('Les mots de passe ne correspondent pas.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Cet email est déjà utilisé.')
        
        slug = create_slug(company_name)
        if Company.query.filter_by(slug=slug).first():
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        company = Company(
            name=company_name,
            slug=slug,
            country='MA',
            currency='MAD',
            onboarding_completed=False,
            onboarding_step=1
        )
        db.session.add(company)
        db.session.flush()
        
        branding = CompanyBranding(company_id=company.id)
        db.session.add(branding)
        
        tax_profile = TaxProfile(company_id=company.id)
        db.session.add(tax_profile)
        
        tiers = [
            PricingTier(company_id=company.id, name='Économique', code='ECO', coefficient=0.85, is_default=False, sort_order=1),
            PricingTier(company_id=company.id, name='Standard', code='STD', coefficient=1.00, is_default=True, sort_order=2),
            PricingTier(company_id=company.id, name='Premium', code='PREM', coefficient=1.25, is_default=False, sort_order=3),
        ]
        for tier in tiers:
            db.session.add(tier)
        
        user = User(
            company_id=company.id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_company_owner=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        owner_role = Role.query.filter_by(name='owner').first()
        if owner_role:
            user_role = UserRole(user_id=user.id, role_id=owner_role.id)
            db.session.add(user_role)
        
        db.session.commit()
        
        login_user(user)
        flash('Compte créé avec succès! Complétez la configuration de votre entreprise.', 'success')
        return redirect(url_for('onboarding.index'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))
