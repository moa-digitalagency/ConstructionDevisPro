from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Project, ProjectPlan, Room, Measurement, BPUArticle, CompanyBPUArticle, QuoteLine, QuoteVersion
from decimal import Decimal

api_bp = Blueprint('api', __name__)


@api_bp.route('/projects/<int:project_id>/rooms', methods=['GET'])
@login_required
def get_rooms(project_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    rooms = Room.query.filter_by(project_id=project_id).all()
    
    return jsonify([{
        'id': room.id,
        'name': room.name,
        'room_type': room.room_type,
        'level': room.level,
        'area': float(room.area) if room.area else 0,
        'perimeter': float(room.perimeter) if room.perimeter else 0,
        'ceiling_height': float(room.ceiling_height) if room.ceiling_height else 2.8
    } for room in rooms])


@api_bp.route('/projects/<int:project_id>/rooms', methods=['POST'])
@login_required
def create_room(project_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    
    data = request.get_json()
    
    room = Room(
        project_id=project_id,
        plan_id=data.get('plan_id'),
        name=data.get('name', 'Nouvelle pièce'),
        room_type=data.get('room_type'),
        level=data.get('level', 0),
        area=data.get('area'),
        perimeter=data.get('perimeter'),
        ceiling_height=data.get('ceiling_height', 2.80),
        polygon_data=data.get('polygon_data')
    )
    db.session.add(room)
    db.session.commit()
    
    return jsonify({
        'id': room.id,
        'name': room.name,
        'area': float(room.area) if room.area else 0
    }), 201


@api_bp.route('/projects/<int:project_id>/rooms/<int:room_id>', methods=['PUT'])
@login_required
def update_room(project_id, room_id):
    project = Project.query.filter_by(id=project_id, company_id=current_user.company_id).first_or_404()
    room = Room.query.filter_by(id=room_id, project_id=project_id).first_or_404()
    
    data = request.get_json()
    
    if 'name' in data:
        room.name = data['name']
    if 'room_type' in data:
        room.room_type = data['room_type']
    if 'level' in data:
        room.level = data['level']
    if 'area' in data:
        room.area = data['area']
    if 'perimeter' in data:
        room.perimeter = data['perimeter']
    if 'ceiling_height' in data:
        room.ceiling_height = data['ceiling_height']
    if 'polygon_data' in data:
        room.polygon_data = data['polygon_data']
    
    db.session.commit()
    
    return jsonify({'success': True})


@api_bp.route('/plans/<int:plan_id>/calibrate', methods=['POST'])
@login_required
def calibrate_plan(plan_id):
    plan = ProjectPlan.query.join(Project).filter(
        ProjectPlan.id == plan_id,
        Project.company_id == current_user.company_id
    ).first_or_404()
    
    data = request.get_json()
    
    point1 = data.get('point1')
    point2 = data.get('point2')
    real_distance = data.get('real_distance')
    
    if not all([point1, point2, real_distance]):
        return jsonify({'error': 'Données de calibration manquantes'}), 400
    
    import math
    pixel_distance = math.sqrt(
        (point2['x'] - point1['x'])**2 + 
        (point2['y'] - point1['y'])**2
    )
    
    if pixel_distance > 0:
        scale_factor = float(real_distance) / pixel_distance
    else:
        return jsonify({'error': 'Distance pixels invalide'}), 400
    
    plan.scale_factor = scale_factor
    plan.is_calibrated = True
    plan.calibration_data = {
        'point1': point1,
        'point2': point2,
        'real_distance': real_distance,
        'pixel_distance': pixel_distance
    }
    db.session.commit()
    
    return jsonify({
        'success': True,
        'scale_factor': scale_factor
    })


@api_bp.route('/plans/<int:plan_id>/measurements', methods=['POST'])
@login_required
def add_measurement(plan_id):
    plan = ProjectPlan.query.join(Project).filter(
        ProjectPlan.id == plan_id,
        Project.company_id == current_user.company_id
    ).first_or_404()
    
    data = request.get_json()
    
    measurement = Measurement(
        plan_id=plan_id,
        room_id=data.get('room_id'),
        measurement_type=data.get('measurement_type', 'area'),
        unit=data.get('unit', 'm²'),
        quantity=data.get('quantity', 0),
        confidence=data.get('confidence', 'medium'),
        source='manual',
        polygon_data=data.get('polygon_data'),
        created_by_id=current_user.id
    )
    db.session.add(measurement)
    db.session.commit()
    
    return jsonify({
        'id': measurement.id,
        'quantity': float(measurement.quantity),
        'unit': measurement.unit
    }), 201


@api_bp.route('/bpu/search')
@login_required
def search_bpu():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    from models import BPULibrary
    
    library = BPULibrary.query.filter_by(
        country=current_user.company.country,
        is_active=True
    ).order_by(BPULibrary.version.desc()).first()
    
    if not library:
        return jsonify([])
    
    articles_query = BPUArticle.query.filter_by(library_id=library.id)
    
    if query:
        articles_query = articles_query.filter(
            db.or_(
                BPUArticle.code.ilike(f'%{query}%'),
                BPUArticle.designation.ilike(f'%{query}%')
            )
        )
    
    if category:
        articles_query = articles_query.filter_by(category=category)
    
    articles = articles_query.limit(50).all()
    
    return jsonify([{
        'id': a.id,
        'code': a.code,
        'category': a.category,
        'designation': a.designation,
        'unit': a.unit,
        'price_eco': float(a.unit_price_eco) if a.unit_price_eco else 0,
        'price_std': float(a.unit_price_standard) if a.unit_price_standard else 0,
        'price_prem': float(a.unit_price_premium) if a.unit_price_premium else 0
    } for a in articles])


@api_bp.route('/quotes/<int:quote_id>/versions/<int:version_id>/lines', methods=['POST'])
@login_required
def add_quote_line(quote_id, version_id):
    from models import Quote, Project
    
    quote = Quote.query.join(Project).filter(
        Quote.id == quote_id,
        Project.company_id == current_user.company_id
    ).first_or_404()
    
    version = QuoteVersion.query.filter_by(id=version_id, quote_id=quote_id).first_or_404()
    
    data = request.get_json()
    
    quantity = Decimal(str(data.get('quantity', 0)))
    unit_price = Decimal(str(data.get('unit_price', 0)))
    total_price = quantity * unit_price
    
    line = QuoteLine(
        version_id=version_id,
        article_id=data.get('article_id'),
        custom_article_id=data.get('custom_article_id'),
        category=data.get('category'),
        designation=data.get('designation'),
        unit=data.get('unit'),
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price,
        room_id=data.get('room_id'),
        quantity_source=data.get('quantity_source', 'manual'),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(line)
    
    version.subtotal_ht = sum(l.total_price for l in version.lines) + total_price
    version.vat_amount = version.subtotal_ht * (version.vat_rate or Decimal('20')) / 100
    version.total_ttc = version.subtotal_ht + version.vat_amount
    
    db.session.commit()
    
    return jsonify({
        'id': line.id,
        'total_price': float(line.total_price)
    }), 201


@api_bp.route('/quotes/<int:quote_id>/versions/<int:version_id>/lines/<int:line_id>', methods=['DELETE'])
@login_required
def delete_quote_line(quote_id, version_id, line_id):
    from models import Quote, Project
    
    quote = Quote.query.join(Project).filter(
        Quote.id == quote_id,
        Project.company_id == current_user.company_id
    ).first_or_404()
    
    version = QuoteVersion.query.filter_by(id=version_id, quote_id=quote_id).first_or_404()
    line = QuoteLine.query.filter_by(id=line_id, version_id=version_id).first_or_404()
    
    db.session.delete(line)
    
    version.subtotal_ht = sum(l.total_price for l in version.lines if l.id != line_id)
    version.vat_amount = version.subtotal_ht * (version.vat_rate or Decimal('20')) / 100
    version.total_ttc = version.subtotal_ht + version.vat_amount
    
    db.session.commit()
    
    return jsonify({'success': True})
