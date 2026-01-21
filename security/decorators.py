from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Veuillez vous connecter.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.is_company_owner:
                return f(*args, **kwargs)
            
            if not current_user.has_permission(permission):
                flash('Vous n\'avez pas la permission d\'accéder à cette page.', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Veuillez vous connecter.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.is_company_owner:
                return f(*args, **kwargs)
            
            user_roles = current_user.get_role_names()
            if role_name not in user_roles:
                flash('Vous n\'avez pas la permission d\'accéder à cette page.', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.company or not current_user.company.is_active:
            flash('Votre entreprise n\'est pas active.', 'error')
            return redirect(url_for('auth.logout'))
        
        return f(*args, **kwargs)
    return decorated_function
