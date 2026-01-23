#!/usr/bin/env python3
import os
import sys

os.environ.setdefault('DATABASE_URL', os.getenv('DATABASE_URL', ''))

from app import create_app
from models import db

def init_database():
    print("Initialisation de la base de données DevisPro...")
    print("-" * 50)
    
    app = create_app()
    
    with app.app_context():
        print("Création des tables...")
        db.create_all()
        print("Tables créées avec succès!")
        
        print("\nTables disponibles:")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        for table in sorted(tables):
            print(f"  - {table}")
        
        print(f"\nTotal: {len(tables)} tables")
        print("-" * 50)
        print("Base de données initialisée avec succès!")
        print("\nDonnées de démarrage:")
        
        from models import Role, BPULibrary, QuestionTemplate, User, Company
        
        roles_count = Role.query.count()
        print(f"  - Rôles: {roles_count}")
        
        libraries_count = BPULibrary.query.count()
        print(f"  - Bibliothèques BPU: {libraries_count}")
        
        questions_count = QuestionTemplate.query.count()
        print(f"  - Modèles de questions: {questions_count}")
        
        users_count = User.query.count()
        print(f"  - Utilisateurs: {users_count}")
        
        companies_count = Company.query.count()
        print(f"  - Entreprises: {companies_count}")
        
        print("-" * 50)
        
        demo_email = os.environ.get('DEMO_SUPERADMIN_EMAIL', 'admin@devispro.com')
        demo_user = User.query.filter_by(email=demo_email).first()
        if demo_user:
            print(f"\nCompte démo disponible:")
            print(f"  Email: {demo_email}")
            print(f"  Mot de passe: (voir variable DEMO_SUPERADMIN_PASSWORD)")
        
        print("\nL'application est prête à démarrer!")


if __name__ == '__main__':
    init_database()
