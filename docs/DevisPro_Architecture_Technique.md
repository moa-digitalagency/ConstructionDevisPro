# DevisPro - Architecture Technique

## 1. Vue d'Ensemble
DevisPro est une application monolithique modulaire construite sur le framework **Flask** (Python). Elle implémente une architecture **MVC (Modèle-Vue-Contrôleur)** stricte, séparant clairement la logique métier, l'accès aux données et l'interface utilisateur.

L'application est conçue pour être **Multi-Tenant** (multi-entreprise) par isolation logique des données (`company_id`).

## 2. Stack Technologique

### 2.1 Backend (Python 3.11+)
*   **Core Framework** : `Flask 3.1.x`.
*   **ORM** : `SQLAlchemy 2.0` avec `Flask-SQLAlchemy`. Gestion des relations complexes et lazy loading.
*   **Authentification** : `Flask-Login` pour la gestion de session.
*   **Moteur PDF** : `ReportLab` pour la génération programmatique de documents vectoriels (Devis).
*   **Tests E2E** : `Playwright` (Python) pour la validation des scénarios critiques.

### 2.2 Frontend
*   **Templates** : `Jinja2` (Rendu côté serveur).
*   **Styles** : `Tailwind CSS` (Classes utilitaires).
*   **Interactivité** : JavaScript Vanilla (ES6+).
*   **Composants Critiques** :
    *   `PDF.js` (Mozilla) : Rendu des plans vectoriels.
    *   `HTML5 Canvas` : Surcouche de dessin pour le métré (Polygones, Lignes).

### 2.3 Base de Données
*   **SGBD** : PostgreSQL (Production) / SQLite (Dev).
*   **Schéma** : Relationnel normalisé (3NF).
*   **Migration** : Système de migration automatique au démarrage (`init_db.py`) qui inspecte les tables et ajoute les colonnes manquantes (Non-destructive).

## 3. Architecture Logicielle

### 3.1 Structure des Dossiers
```
/
├── app.py                 # Application Factory & Configuration
├── models/                # Couche Données (SQLAlchemy Models)
│   ├── base.py            # Modèle de base (TimestampMixin)
│   ├── company.py         # Branding, Tiers, Multi-tenant
│   ├── bpu.py             # Bibliothèque de Prix (Hierarchy)
│   ├── quote.py           # Logique de chiffrage (Version, Lignes)
│   └── project.py         # Données CRM & Métrés
├── routes/                # Couche Contrôleur (Blueprints)
│   ├── auth.py            # Login/Register/Logout
│   ├── quotes.py          # Workflow Devis
│   └── projects.py        # Workflow Projets
├── services/              # Couche Service (Business Logic)
│   ├── quote_generator.py # Algorithme de chiffrage intelligent
│   ├── export_service.py  # Moteur PDF ReportLab
│   └── plan_reader.py     # Logique d'analyse de plans
├── templates/             # Couche Vue (Jinja2)
└── static/                # Assets & Uploads
```

### 3.2 Flux de Données (Data Flow)
1.  **Requête HTTP** : Arrive sur une route Flask (ex: `POST /quotes/generate`).
2.  **Sécurité** : Middleware `@login_required` et `@require_permission`.
3.  **Contrôleur** : Valide les entrées, appelle le Service.
4.  **Service** (`QuoteGenerator`) :
    *   Charge les modèles (`Project`, `Room`, `BPUArticle`).
    *   Applique les règles métier (Calculs, Surcharges).
    *   Persiste le résultat (`QuoteVersion`).
5.  **Vue** : Renvoie le template HTML ou le fichier PDF généré.

## 4. Modèle de Données (Deep Dive)

### 4.1 Multi-Tenant & Isolation
L'entité `Company` est la racine. Toutes les entités critiques (`User`, `Project`, `BPUOverride`) possèdent une Foreign Key `company_id`. Les requêtes SQLAlchemy doivent toujours filtrer par ce champ pour éviter les fuites de données entre locataires.

### 4.2 Système de Prix (BPU Hierarchy)
Le système de prix utilise un mécanisme de surcharge (Override) en cascade :
1.  **Article Custom (`CompanyBPUArticle`)** : Priorité absolue. Article créé par l'entreprise.
2.  **Surcharge (`CompanyBPUOverride`)** : Redéfinition locale d'un article standard (Prix ou Désignation).
3.  **Standard (`BPUArticle`)** : Bibliothèque nationale par défaut.

Le tout est modulé par les **Pricing Tiers** (Gammes) qui sélectionnent la colonne de prix cible (`price_eco`, `price_std`, `price_prem`) ou appliquent un coefficient global.

### 4.3 Versioning des Devis
L'entité `Quote` agit comme un conteneur. Les données réelles sont dans `QuoteVersion`.
*   `Quote` : ID, Référence, Statut global.
*   `QuoteVersion` : Snapshot immuable contenant les lignes (`QuoteLine`) et les totaux à un instant T.
Ceci permet de conserver l'historique complet des propositions commerciales envoyées au client.

## 5. Sécurité

*   **Mots de Passe** : Hachage fort (`pbkdf2:sha256`) avec sel unique.
*   **CSRF** : Protection systématique sur tous les formulaires POST.
*   **Fichiers** :
    *   Validation stricte des extensions (`.pdf`, `.dwg`).
    *   Renommage UUID pour éviter les collisions et les injections de chemin.
    *   Stockage hors de la racine web (sauf lien symbolique contrôlé).
*   **Audit** : Traçabilité immuable via `AuditLog` (Qui, Quoi, Quand, Diff).
