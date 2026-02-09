import os
from models import db, Role, BPULibrary, BPUArticle, QuestionTemplate, Company, User, UserRole, PricingTier
from datetime import date


def seed_initial_data():
    seed_roles()
    seed_bpu_library()
    seed_question_templates()
    seed_demo_superadmin()
    fix_existing_companies_tiers()


def fix_existing_companies_tiers():
    """Ensure all companies have pricing tiers."""
    companies = Company.query.all()
    for company in companies:
        if PricingTier.query.filter_by(company_id=company.id).count() == 0:
            print(f"Adding default pricing tiers for company: {company.name}")
            tiers = [
                PricingTier(company_id=company.id, name='Économique', code='ECO', coefficient=0.85, is_default=False, sort_order=1),
                PricingTier(company_id=company.id, name='Standard', code='STD', coefficient=1.00, is_default=True, sort_order=2),
                PricingTier(company_id=company.id, name='Premium', code='PREM', coefficient=1.25, is_default=False, sort_order=3),
            ]
            for tier in tiers:
                db.session.add(tier)
            db.session.commit()


def seed_demo_superadmin():
    email = os.environ.get('DEMO_SUPERADMIN_EMAIL', 'admin@devispro.com')
    password = os.environ.get('DEMO_SUPERADMIN_PASSWORD', 'Admin123!')
    
    existing = User.query.filter_by(email=email).first()
    if existing:
        return
    
    owner_role = Role.query.filter_by(name='owner').first()
    if not owner_role:
        return
    
    company = Company(
        name='DevisPro Demo',
        slug='devispro-demo',
        country='MA',
        currency='MAD',
        onboarding_completed=True
    )
    db.session.add(company)
    db.session.flush()
    
    user = User(
        email=email,
        first_name='Admin',
        last_name='Demo',
        company_id=company.id,
        is_company_owner=True,
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    
    user_role = UserRole(user_id=user.id, role_id=owner_role.id)
    db.session.add(user_role)

    # Create default pricing tiers for the demo company
    tiers = [
        PricingTier(company_id=company.id, name='Économique', code='ECO', coefficient=0.85, is_default=False, sort_order=1),
        PricingTier(company_id=company.id, name='Standard', code='STD', coefficient=1.00, is_default=True, sort_order=2),
        PricingTier(company_id=company.id, name='Premium', code='PREM', coefficient=1.25, is_default=False, sort_order=3),
    ]
    for tier in tiers:
        db.session.add(tier)

    db.session.commit()


def seed_roles():
    existing = Role.query.first()
    if existing:
        return
    
    roles = [
        Role(
            name='owner',
            description='Propriétaire de l\'entreprise',
            can_manage_users=True,
            can_manage_bpu=True,
            can_manage_projects=True,
            can_manage_quotes=True,
            can_export=True,
            can_view_only=False
        ),
        Role(
            name='admin',
            description='Administrateur',
            can_manage_users=True,
            can_manage_bpu=True,
            can_manage_projects=True,
            can_manage_quotes=True,
            can_export=True,
            can_view_only=False
        ),
        Role(
            name='metreur',
            description='Métreur',
            can_manage_users=False,
            can_manage_bpu=True,
            can_manage_projects=True,
            can_manage_quotes=False,
            can_export=True,
            can_view_only=False
        ),
        Role(
            name='commercial',
            description='Commercial',
            can_manage_users=False,
            can_manage_bpu=False,
            can_manage_projects=True,
            can_manage_quotes=True,
            can_export=True,
            can_view_only=False,
            max_margin_percentage=15.00
        ),
        Role(
            name='readonly',
            description='Lecture seule',
            can_manage_users=False,
            can_manage_bpu=False,
            can_manage_projects=False,
            can_manage_quotes=False,
            can_export=False,
            can_view_only=True
        )
    ]
    
    for role in roles:
        db.session.add(role)
    
    db.session.commit()


def seed_bpu_library():
    existing = BPULibrary.query.filter_by(country='MA').first()
    if existing:
        return
    
    library = BPULibrary(
        country='MA',
        version='2025.1',
        name='Bibliothèque BPU Maroc 2025',
        description='Prix de référence pour le marché marocain',
        is_active=True,
        effective_date=date(2025, 1, 1)
    )
    db.session.add(library)
    db.session.flush()
    
    articles = [
        {'code': 'GO-001', 'category': 'Gros Œuvre', 'subcategory': 'Fondations', 'designation': 'Fouilles en rigoles', 'unit': 'm³', 'eco': 150, 'std': 180, 'prem': 220},
        {'code': 'GO-002', 'category': 'Gros Œuvre', 'subcategory': 'Fondations', 'designation': 'Béton armé pour semelles', 'unit': 'm³', 'eco': 2200, 'std': 2600, 'prem': 3200},
        {'code': 'GO-003', 'category': 'Gros Œuvre', 'subcategory': 'Fondations', 'designation': 'Béton de propreté', 'unit': 'm³', 'eco': 800, 'std': 950, 'prem': 1150},
        {'code': 'GO-010', 'category': 'Gros Œuvre', 'subcategory': 'Structure', 'designation': 'Murs en agglos 20x20x50', 'unit': 'm²', 'eco': 280, 'std': 350, 'prem': 450},
        {'code': 'GO-011', 'category': 'Gros Œuvre', 'subcategory': 'Structure', 'designation': 'Murs en briques creuses', 'unit': 'm²', 'eco': 220, 'std': 280, 'prem': 360},
        {'code': 'GO-020', 'category': 'Gros Œuvre', 'subcategory': 'Dalle', 'designation': 'Plancher corps creux 16+5', 'unit': 'm²', 'eco': 380, 'std': 450, 'prem': 550},
        {'code': 'GO-021', 'category': 'Gros Œuvre', 'subcategory': 'Dalle', 'designation': 'Plancher corps creux 20+5', 'unit': 'm²', 'eco': 420, 'std': 500, 'prem': 620},
        {'code': 'GO-030', 'category': 'Gros Œuvre', 'subcategory': 'Etanchéité', 'designation': 'Étanchéité terrasse multicouche', 'unit': 'm²', 'eco': 180, 'std': 250, 'prem': 350},
        
        {'code': 'SO-001', 'category': 'Second Œuvre', 'subcategory': 'Enduits', 'designation': 'Enduit intérieur au mortier', 'unit': 'm²', 'eco': 45, 'std': 55, 'prem': 70},
        {'code': 'SO-002', 'category': 'Second Œuvre', 'subcategory': 'Enduits', 'designation': 'Enduit extérieur tyrolien', 'unit': 'm²', 'eco': 65, 'std': 80, 'prem': 100},
        {'code': 'SO-010', 'category': 'Second Œuvre', 'subcategory': 'Revêtements sols', 'designation': 'Carrelage grès cérame 60x60', 'unit': 'm²', 'eco': 180, 'std': 280, 'prem': 450},
        {'code': 'SO-011', 'category': 'Second Œuvre', 'subcategory': 'Revêtements sols', 'designation': 'Carrelage marbre', 'unit': 'm²', 'eco': 450, 'std': 650, 'prem': 950},
        {'code': 'SO-012', 'category': 'Second Œuvre', 'subcategory': 'Revêtements sols', 'designation': 'Parquet contrecollé', 'unit': 'm²', 'eco': 280, 'std': 380, 'prem': 550},
        {'code': 'SO-020', 'category': 'Second Œuvre', 'subcategory': 'Peinture', 'designation': 'Peinture acrylique murs', 'unit': 'm²', 'eco': 35, 'std': 50, 'prem': 75},
        {'code': 'SO-021', 'category': 'Second Œuvre', 'subcategory': 'Peinture', 'designation': 'Peinture plafond', 'unit': 'm²', 'eco': 40, 'std': 55, 'prem': 80},
        
        {'code': 'MN-001', 'category': 'Menuiserie', 'subcategory': 'Portes', 'designation': 'Porte intérieure isoplane', 'unit': 'u', 'eco': 1200, 'std': 1800, 'prem': 2800},
        {'code': 'MN-002', 'category': 'Menuiserie', 'subcategory': 'Portes', 'designation': 'Porte d\'entrée blindée', 'unit': 'u', 'eco': 4500, 'std': 7000, 'prem': 12000},
        {'code': 'MN-010', 'category': 'Menuiserie', 'subcategory': 'Fenêtres', 'designation': 'Fenêtre aluminium double vitrage', 'unit': 'm²', 'eco': 1800, 'std': 2400, 'prem': 3500},
        {'code': 'MN-011', 'category': 'Menuiserie', 'subcategory': 'Fenêtres', 'designation': 'Fenêtre PVC double vitrage', 'unit': 'm²', 'eco': 1400, 'std': 1900, 'prem': 2600},
        {'code': 'MN-012', 'category': 'Menuiserie', 'subcategory': 'Fenêtres', 'designation': 'Baie vitrée coulissante alu', 'unit': 'm²', 'eco': 2200, 'std': 3000, 'prem': 4200},
        
        {'code': 'PL-001', 'category': 'Plomberie', 'subcategory': 'Sanitaires', 'designation': 'WC suspendu complet', 'unit': 'u', 'eco': 3500, 'std': 5500, 'prem': 9000},
        {'code': 'PL-002', 'category': 'Plomberie', 'subcategory': 'Sanitaires', 'designation': 'Lavabo avec meuble', 'unit': 'u', 'eco': 2500, 'std': 4000, 'prem': 7000},
        {'code': 'PL-003', 'category': 'Plomberie', 'subcategory': 'Sanitaires', 'designation': 'Douche italienne complète', 'unit': 'u', 'eco': 4500, 'std': 7500, 'prem': 15000},
        {'code': 'PL-004', 'category': 'Plomberie', 'subcategory': 'Sanitaires', 'designation': 'Baignoire avec robinetterie', 'unit': 'u', 'eco': 5500, 'std': 9000, 'prem': 18000},
        {'code': 'PL-010', 'category': 'Plomberie', 'subcategory': 'Réseau', 'designation': 'Alimentation eau froide/chaude', 'unit': 'ml', 'eco': 85, 'std': 110, 'prem': 150},
        {'code': 'PL-011', 'category': 'Plomberie', 'subcategory': 'Réseau', 'designation': 'Évacuation PVC', 'unit': 'ml', 'eco': 65, 'std': 85, 'prem': 120},
        
        {'code': 'EL-001', 'category': 'Électricité', 'subcategory': 'Installation', 'designation': 'Point lumineux', 'unit': 'u', 'eco': 350, 'std': 450, 'prem': 650},
        {'code': 'EL-002', 'category': 'Électricité', 'subcategory': 'Installation', 'designation': 'Prise de courant', 'unit': 'u', 'eco': 180, 'std': 250, 'prem': 380},
        {'code': 'EL-003', 'category': 'Électricité', 'subcategory': 'Installation', 'designation': 'Interrupteur simple', 'unit': 'u', 'eco': 150, 'std': 220, 'prem': 350},
        {'code': 'EL-010', 'category': 'Électricité', 'subcategory': 'Tableau', 'designation': 'Tableau électrique complet', 'unit': 'u', 'eco': 3500, 'std': 5500, 'prem': 9000},
        
        {'code': 'CV-001', 'category': 'CVC', 'subcategory': 'Climatisation', 'designation': 'Split mural 12000 BTU', 'unit': 'u', 'eco': 6500, 'std': 8500, 'prem': 12000},
        {'code': 'CV-002', 'category': 'CVC', 'subcategory': 'Climatisation', 'designation': 'Split mural 18000 BTU', 'unit': 'u', 'eco': 8500, 'std': 11000, 'prem': 16000},
        {'code': 'CV-003', 'category': 'CVC', 'subcategory': 'Climatisation', 'designation': 'Climatisation gainable', 'unit': 'u', 'eco': 25000, 'std': 35000, 'prem': 55000},
        {'code': 'CV-010', 'category': 'CVC', 'subcategory': 'Chauffage', 'designation': 'Chauffe-eau solaire 200L', 'unit': 'u', 'eco': 8000, 'std': 12000, 'prem': 18000},
        
        {'code': 'PI-001', 'category': 'Piscine', 'subcategory': 'Structure', 'designation': 'Piscine béton armé', 'unit': 'm²', 'eco': 3000, 'std': 4000, 'prem': 6000},
        {'code': 'PI-002', 'category': 'Piscine', 'subcategory': 'Revêtement', 'designation': 'Liner piscine', 'unit': 'm²', 'eco': 350, 'std': 500, 'prem': 800},
        {'code': 'PI-003', 'category': 'Piscine', 'subcategory': 'Revêtement', 'designation': 'Carrelage piscine', 'unit': 'm²', 'eco': 550, 'std': 850, 'prem': 1400},
        {'code': 'PI-010', 'category': 'Piscine', 'subcategory': 'Équipement', 'designation': 'Système filtration complet', 'unit': 'u', 'eco': 15000, 'std': 25000, 'prem': 45000},
        
        {'code': 'AM-001', 'category': 'Aménagement', 'subcategory': 'Cuisine', 'designation': 'Cuisine équipée standard', 'unit': 'ml', 'eco': 4500, 'std': 7500, 'prem': 15000},
        {'code': 'AM-002', 'category': 'Aménagement', 'subcategory': 'Dressing', 'designation': 'Dressing sur mesure', 'unit': 'ml', 'eco': 2500, 'std': 4000, 'prem': 7500},
        {'code': 'AM-010', 'category': 'Aménagement', 'subcategory': 'Extérieur', 'designation': 'Clôture muret + grille', 'unit': 'ml', 'eco': 1200, 'std': 1800, 'prem': 3000},
        {'code': 'AM-011', 'category': 'Aménagement', 'subcategory': 'Extérieur', 'designation': 'Portail motorisé', 'unit': 'u', 'eco': 15000, 'std': 25000, 'prem': 45000},
    ]
    
    for i, art in enumerate(articles):
        article = BPUArticle(
            library_id=library.id,
            code=art['code'],
            category=art['category'],
            subcategory=art['subcategory'],
            designation=art['designation'],
            unit=art['unit'],
            unit_price_eco=art['eco'],
            unit_price_standard=art['std'],
            unit_price_premium=art['prem'],
            sort_order=i
        )
        db.session.add(article)
    
    db.session.commit()


def seed_question_templates():
    existing = QuestionTemplate.query.first()
    if existing:
        return
    
    questions = [
        {
            'code': 'ceiling_height',
            'category': 'Général',
            'question_text': 'Quelle est la hauteur sous plafond souhaitée ?',
            'question_type': 'select',
            'options': ['2.60 m', '2.80 m', '3.00 m', '3.20 m', 'Autre'],
            'default_value': '2.80 m',
            'unit': 'm',
            'is_required': True,
            'applies_to_rooms': True,
            'sort_order': 1
        },
        {
            'code': 'window_type',
            'category': 'Menuiseries',
            'question_text': 'Quel type de menuiseries pour les fenêtres ?',
            'question_type': 'select',
            'options': ['Aluminium', 'PVC', 'Bois'],
            'default_value': 'Aluminium',
            'is_required': True,
            'sort_order': 2,
            'bpu_category_trigger': 'Menuiserie'
        },
        {
            'code': 'glazing_type',
            'category': 'Menuiseries',
            'question_text': 'Quel type de vitrage ?',
            'question_type': 'select',
            'options': ['Simple vitrage', 'Double vitrage', 'Triple vitrage'],
            'default_value': 'Double vitrage',
            'is_required': True,
            'sort_order': 3
        },
        {
            'code': 'floor_type',
            'category': 'Revêtements',
            'question_text': 'Quel revêtement de sol principal ?',
            'question_type': 'select',
            'options': ['Carrelage grès cérame', 'Carrelage marbre', 'Parquet', 'Béton ciré'],
            'default_value': 'Carrelage grès cérame',
            'is_required': True,
            'applies_to_rooms': True,
            'sort_order': 4,
            'bpu_category_trigger': 'Second Œuvre'
        },
        {
            'code': 'bathroom_wall',
            'category': 'Revêtements',
            'question_text': 'Revêtement mural pour les salles de bain ?',
            'question_type': 'select',
            'options': ['Faïence standard', 'Faïence grand format', 'Marbre', 'Tadelakt'],
            'default_value': 'Faïence standard',
            'is_required': True,
            'sort_order': 5
        },
        {
            'code': 'bathroom_wall_height',
            'category': 'Revêtements',
            'question_text': 'Hauteur du revêtement mural SDB ?',
            'question_type': 'select',
            'options': ['1.20 m (douche)', '1.80 m (standard)', '2.20 m (toute hauteur)'],
            'default_value': '1.80 m (standard)',
            'is_required': True,
            'sort_order': 6
        },
        {
            'code': 'clim',
            'category': 'CVC',
            'question_text': 'Quel système de climatisation ?',
            'question_type': 'select',
            'options': ['Aucune', 'Splits muraux', 'Gainable'],
            'default_value': 'Splits muraux',
            'is_required': True,
            'sort_order': 7,
            'bpu_category_trigger': 'CVC'
        },
        {
            'code': 'clim_qty',
            'category': 'CVC',
            'question_text': 'Combien d\'unités de climatisation ?',
            'question_type': 'number',
            'default_value': '4',
            'unit': 'unités',
            'is_required': False,
            'sort_order': 8
        },
        {
            'code': 'demolition',
            'category': 'Démolition',
            'question_text': 'Y a-t-il des travaux de démolition ?',
            'question_type': 'select',
            'options': ['Non', 'Oui - Accès facile', 'Oui - Accès difficile'],
            'default_value': 'Non',
            'is_required': True,
            'applies_to_project_types': ['renovation', 'extension'],
            'sort_order': 9
        },
        {
            'code': 'piscine',
            'category': 'Piscine',
            'question_text': 'Le projet inclut-il une piscine ?',
            'question_type': 'select',
            'options': ['Non', 'Oui'],
            'default_value': 'Non',
            'is_required': True,
            'sort_order': 10,
            'bpu_category_trigger': 'Piscine'
        },
        {
            'code': 'piscine_dims',
            'category': 'Piscine',
            'question_text': 'Dimensions de la piscine (L x l) ?',
            'question_type': 'dimensions',
            'default_value': '8x4',
            'unit': 'm',
            'is_required': False,
            'sort_order': 11,
            'help_text': 'Indiquez les dimensions en mètres (longueur x largeur)'
        },
        {
            'code': 'piscine_system',
            'category': 'Piscine',
            'question_text': 'Système de filtration piscine ?',
            'question_type': 'select',
            'options': ['Filtration à sable', 'Filtration à cartouche', 'Électrolyse au sel'],
            'default_value': 'Filtration à sable',
            'is_required': False,
            'sort_order': 12
        },
        {
            'code': 'kitchen_standing',
            'category': 'Cuisine',
            'question_text': 'Quel standing pour la cuisine ?',
            'question_type': 'select',
            'options': ['Économique (Mélaminé)', 'Standard (MDF Laqué)', 'Premium (Bois massif / Import)'],
            'default_value': 'Standard (MDF Laqué)',
            'sort_order': 20
        },
        {
            'code': 'kitchen_worktop',
            'category': 'Cuisine',
            'question_text': 'Type de plan de travail ?',
            'question_type': 'select',
            'options': ['Granit local', 'Quartz / Silestone', 'Marbre', 'Céramique'],
            'default_value': 'Granit local',
            'sort_order': 21
        },
        {
            'code': 'sanitary_brand',
            'category': 'Sanitaires',
            'question_text': 'Marque/Gamme des sanitaires ?',
            'question_type': 'select',
            'options': ['Standard local (Roca...)', 'Intermédiaire (Grohe, Geberit)', 'Luxe (Villeroy & Boch, Hansgrohe)'],
            'default_value': 'Standard local (Roca...)',
            'sort_order': 30
        },
        {
            'code': 'home_automation',
            'category': 'Électricité',
            'question_text': 'Domotique souhaitée ?',
            'question_type': 'select',
            'options': ['Aucune', 'Partielle (Volets, Lumières)', 'Complète (Smart Home)'],
            'default_value': 'Aucune',
            'sort_order': 40
        },
        {
            'code': 'garden_landscaping',
            'category': 'Aménagements Extérieurs',
            'question_text': 'Aménagement paysager requis ?',
            'question_type': 'select',
            'options': ['Non', 'Gazon et arrosage simple', 'Paysagisme complet'],
            'default_value': 'Non',
            'sort_order': 50
        }
    ]
    
    for q in questions:
        template = QuestionTemplate(
            code=q['code'],
            category=q['category'],
            question_text=q['question_text'],
            question_type=q['question_type'],
            options=q.get('options'),
            default_value=q.get('default_value'),
            unit=q.get('unit'),
            is_required=q.get('is_required', True),
            applies_to_rooms=q.get('applies_to_rooms', False),
            applies_to_project_types=q.get('applies_to_project_types'),
            sort_order=q.get('sort_order', 0),
            help_text=q.get('help_text'),
            bpu_category_trigger=q.get('bpu_category_trigger')
        )
        db.session.add(template)
    
    db.session.commit()
