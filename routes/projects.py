from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Project, ProjectPlan, Room, Measurement, PricingTier, ProjectType, ProjectTypology, ProjectStatus
from werkzeug.utils import secure_filename
from security.decorators import require_permission
from security.audit import log_action
import os
import uuid

projects_bp = Blueprint('projects', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'dwg', 'dxf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@projects_bp.route('/')
@login_required
def index():
    company = current_user.company
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    
    query = Project.query.filter_by(company_id=company.id)
    
    if status_filter:
        try:
            status = ProjectStatus(status_filter)
            query = query.filter_by(status=status)
        except ValueError:
            pass
    
    if type_filter:
        try:
            project_type = ProjectType(type_filter)
            query = query.filter_by(project_type=project_type)
        except ValueError:
            pass
    
    projects = query.order_by(Project.updated_at.desc()).all()
    
    return render_template('projects/index.html', 
        projects=projects,
        project_types=ProjectType,
        project_statuses=ProjectStatus,
        current_status=status_filter,
        current_type=type_filter
    )


@projects_bp.route('/new', methods=['GET', 'POST'])
@login_required
@require_permission('can_manage_projects')
def new():
    company = current_user.company
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        client_name = request.form.get('client_name', '').strip()
        client_email = request.form.get('client_email', '').strip()
        client_phone = request.form.get('client_phone', '').strip()
        client_address = request.form.get('client_address', '').strip()
        project_type = request.form.get('project_type')
        typology = request.form.get('typology')
        tier_id = request.form.get('tier_id')
        notes = request.form.get('notes', '').strip()
        
        if not name:
            flash('Le nom du projet est requis.', 'error')
            return render_template('projects/new.html', 
                tiers=company.pricing_tiers.all(),
                project_types=ProjectType,
                typologies=ProjectTypology
            )
        
        try:
            project_type_enum = ProjectType(project_type)
            typology_enum = ProjectTypology(typology)
        except ValueError:
            flash('Type ou typologie invalide.', 'error')
            return render_template('projects/new.html',
                tiers=company.pricing_tiers.all(),
                project_types=ProjectType,
                typologies=ProjectTypology
            )
        
        project = Project(
            company_id=company.id,
            name=name,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            client_address=client_address,
            project_type=project_type_enum,
            typology=typology_enum,
            default_tier_id=int(tier_id) if tier_id else None,
            notes=notes,
            status=ProjectStatus.DRAFT
        )
        project.generate_reference()
        
        db.session.add(project)
        db.session.commit()
        
        log_action('create', 'project', project.id, None, {'name': name, 'type': project_type})
        
        flash('Projet créé avec succès!', 'success')
        return redirect(url_for('projects.view', project_id=project.id))
    
    return render_template('projects/new.html',
        tiers=company.pricing_tiers.all(),
        project_types=ProjectType,
        typologies=ProjectTypology
    )


@projects_bp.route('/<int:project_id>')
@login_required
def view(project_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    return render_template('projects/view.html', project=project)


@projects_bp.route('/<int:project_id>/plans', methods=['GET', 'POST'])
@login_required
@require_permission('can_manage_projects')
def plans(project_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    
    if request.method == 'POST':
        if 'plan_file' not in request.files:
            flash('Aucun fichier sélectionné.', 'error')
            return redirect(url_for('projects.plans', project_id=project_id))
        
        file = request.files['plan_file']
        if file.filename == '':
            flash('Aucun fichier sélectionné.', 'error')
            return redirect(url_for('projects.plans', project_id=project_id))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            upload_dir = os.path.join('static', 'uploads', str(current_user.company_id), str(project_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            file_type = filename.rsplit('.', 1)[1].lower()
            
            plan = ProjectPlan(
                project_id=project_id,
                name=request.form.get('plan_name', filename),
                file_path=file_path,
                file_type=file_type,
                file_size=os.path.getsize(file_path)
            )
            db.session.add(plan)
            db.session.commit()
            
            log_action('upload', 'plan', plan.id, None, {'filename': filename, 'type': file_type})
            
            flash('Plan uploadé avec succès!', 'success')
            return redirect(url_for('projects.calibrate', project_id=project_id, plan_id=plan.id))
        else:
            flash('Type de fichier non autorisé. Utilisez PDF, DWG ou DXF.', 'error')
    
    return render_template('projects/plans.html', project=project)


@projects_bp.route('/<int:project_id>/plans/<int:plan_id>/calibrate')
@login_required
@require_permission('can_manage_projects')
def calibrate(project_id, plan_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    plan = ProjectPlan.query.filter_by(id=plan_id, project_id=project_id).first_or_404()
    return render_template('projects/calibrate.html', project=project, plan=plan)


@projects_bp.route('/<int:project_id>/plans/<int:plan_id>/measure')
@login_required
@require_permission('can_manage_projects')
def measure(project_id, plan_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    plan = ProjectPlan.query.filter_by(id=plan_id, project_id=project_id).first_or_404()
    return render_template('projects/measure.html', project=project, plan=plan)


@projects_bp.route('/<int:project_id>/questions')
@login_required
def questions(project_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    return render_template('projects/questions.html', project=project)


@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
@require_permission('can_manage_projects')
def delete(project_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    
    project_name = project.name
    db.session.delete(project)
    db.session.commit()
    
    log_action('delete', 'project', project_id, {'name': project_name}, None)
    
    flash('Projet supprimé.', 'success')
    return redirect(url_for('projects.index'))
