#!/usr/bin/env python3
import os
import sys
from sqlalchemy import text, inspect

# Ensure a valid DATABASE_URL is set
if not os.environ.get('DATABASE_URL'):
    # Default to local SQLite if not provided
    print("DATABASE_URL non défini, utilisation par défaut: sqlite:///devispro.db")
    os.environ['DATABASE_URL'] = 'sqlite:///devispro.db'

from app import create_app
from models import db

def update_schema(app):
    """
    Checks for missing columns in existing tables and adds them.
    This ensures the database schema is up-to-date without losing data.
    """
    print("\nVérification de la structure de la base de données (Migrations)...")

    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        # Iterate over all models defined in SQLAlchemy metadata
        for table_name, table in db.metadata.tables.items():
            if table_name in existing_tables:
                print(f"  - Vérification de la table '{table_name}'...")
                existing_columns = [c['name'] for c in inspector.get_columns(table_name)]

                for column in table.columns:
                    if column.name not in existing_columns:
                        print(f"    ! Colonne manquante détectée: {column.name}")
                        print(f"    -> Ajout de la colonne '{column.name}' à la table '{table_name}'...")

                        # Construct ALTER TABLE statement
                        # We use the column type compilation to get the SQL type representation
                        col_type = column.type.compile(db.engine.dialect)

                        # Basic handling for nullable/defaults
                        # Note: SQLite has limitations on ADD COLUMN with NOT NULL constraints
                        nullable = "NULL" if column.nullable else "NOT NULL"
                        default = ""

                        # If we are strictly on SQLite and adding a NOT NULL column without default, it will fail.
                        # We'll try to handle it gracefully or rely on the DB engine to complain.
                        # For robustness, if it's NOT NULL and no default, we might need to set a default or allow NULL temporarily.

                        # Simple approach: ALTER TABLE <table> ADD COLUMN <name> <type>
                        stmt = f'ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}'

                        try:
                            with db.engine.connect() as conn:
                                conn.execute(text(stmt))
                                conn.commit()
                            print(f"    [OK] Colonne ajoutée avec succès.")
                        except Exception as e:
                            print(f"    [ERREUR] Impossible d'ajouter la colonne: {e}")
                            # Fallback: try adding as nullable if it failed (likely due to NOT NULL constraint on existing rows)
                            if "NOT NULL" in str(e) or "Constraint" in str(e):
                                print("    -> Tentative d'ajout en tant que NULLable pour compatibilité...")
                                try:
                                    stmt_fallback = f'ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type} NULL'
                                    with db.engine.connect() as conn:
                                        conn.execute(text(stmt_fallback))
                                        conn.commit()
                                    print(f"    [OK] Colonne ajoutée (mode dégradé NULLable).")
                                except Exception as e2:
                                    print(f"    [ECHEC] Abandon de l'ajout de la colonne: {e2}")

def init_database():
    print("Initialisation de la base de données DevisPro...")
    print("-" * 50)
    
    app = create_app()
    
    # Check and update schema first
    update_schema(app)

    with app.app_context():
        print("\nCréation des tables manquantes...")
        db.create_all()
        print("Tables vérifiées/créées!")
        
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
