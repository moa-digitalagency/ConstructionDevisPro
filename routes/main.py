from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Project, Quote, ProjectStatus
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if not current_user.company.onboarding_completed:
            return redirect(url_for('onboarding.index'))
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.company.onboarding_completed:
        return redirect(url_for('onboarding.index'))
    
    company = current_user.company
    
    total_projects = Project.query.filter_by(company_id=company.id).count()
    active_projects = Project.query.filter(
        Project.company_id == company.id,
        Project.status.in_([ProjectStatus.DRAFT, ProjectStatus.IN_PROGRESS, ProjectStatus.PENDING_QUESTIONS])
    ).count()
    
    total_quotes = Quote.query.join(Project).filter(Project.company_id == company.id).count()
    
    recent_projects = Project.query.filter_by(company_id=company.id)\
        .order_by(Project.updated_at.desc()).limit(5).all()
    
    recent_quotes = Quote.query.join(Project).filter(Project.company_id == company.id)\
        .order_by(Quote.updated_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
        total_projects=total_projects,
        active_projects=active_projects,
        total_quotes=total_quotes,
        recent_projects=recent_projects,
        recent_quotes=recent_quotes
    )
