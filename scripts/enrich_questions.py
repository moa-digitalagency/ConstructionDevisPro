from app import create_app
from models import db, QuestionTemplate

def enrich_questions():
    app = create_app()
    with app.app_context():
        print("Enriching questions...")

        new_questions = [
            # Kitchen
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
            # Bathrooms
            {
                'code': 'sanitary_brand',
                'category': 'Sanitaires',
                'question_text': 'Marque/Gamme des sanitaires ?',
                'question_type': 'select',
                'options': ['Standard local (Roca...)', 'Intermédiaire (Grohe, Geberit)', 'Luxe (Villeroy & Boch, Hansgrohe)'],
                'default_value': 'Standard local (Roca...)',
                'sort_order': 30
            },
            # Electricity
            {
                'code': 'home_automation',
                'category': 'Électricité',
                'question_text': 'Domotique souhaitée ?',
                'question_type': 'select',
                'options': ['Aucune', 'Partielle (Volets, Lumières)', 'Complète (Smart Home)'],
                'default_value': 'Aucune',
                'sort_order': 40
            },
            # Exterior
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

        count = 0
        for q in new_questions:
            existing = QuestionTemplate.query.filter_by(code=q['code']).first()
            if not existing:
                template = QuestionTemplate(
                    code=q['code'],
                    category=q['category'],
                    question_text=q['question_text'],
                    question_type=q['question_type'],
                    options=q.get('options'),
                    default_value=q.get('default_value'),
                    sort_order=q.get('sort_order', 0)
                )
                db.session.add(template)
                count += 1

        db.session.commit()
        print(f"Added {count} new questions.")

if __name__ == '__main__':
    enrich_questions()
