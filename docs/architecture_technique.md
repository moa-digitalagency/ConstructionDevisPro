# Architecture Technique

## Vue d'ensemble
L'application est une solution monolithique basée sur le framework Flask (Python), conçue pour la gestion de projets de construction, le métré sur plans PDF et la génération de devis. Elle utilise une architecture MVC (Modèle-Vue-Contrôleur) classique adaptée au web.

## Stack Technologique

### Backend
- **Langage** : Python 3.11+
- **Framework Web** : Flask
- **ORM (Object-Relational Mapping)** : SQLAlchemy
- **Authentification** : Flask-Login
- **Gestion des dépendances** : `requirements.txt` / `uv`

### Frontend
- **Moteur de Template** : Jinja2 (intégré à Flask)
- **Styles** : Tailwind CSS (déduit des classes utilitaires)
- **Icones** : FontAwesome
- **Manipulation PDF & Canvas** :
    - `PDF.js` (Mozilla) pour le rendu des plans PDF dans le navigateur.
    - API Canvas HTML5 pour les outils de dessin (lignes, polygones) et le calcul de surfaces.

### Base de Données
- **Système** : SQLite (développement/défaut) ou PostgreSQL (production via `DATABASE_URL`).
- **Migration** : Gestion via `init_db.py` qui inspecte et met à jour le schéma (ajout de colonnes manquantes).

## Structure du Projet

```
/
├── app.py                 # Point d'entrée, configuration de l'application (Factory pattern)
├── models/                # Définitions des modèles de données (SQLAlchemy)
│   ├── company.py         # Entreprises, Branding, Tiers tarifaires
│   ├── project.py         # Projets, Plans, Pièces, Mesures
│   ├── quote.py           # Devis, Versions, Lignes, Hypothèses
│   ├── user.py            # Utilisateurs, Rôles, AuditLogs
│   └── ...
├── routes/                # Contrôleurs (Blueprints Flask)
│   ├── projects.py        # Gestion des projets et plans
│   ├── quotes.py          # Gestion des devis et exports
│   └── ...
├── services/              # Logique métier complexe
│   ├── quote_generator.py # Génération de devis
│   ├── export_service.py  # Export PDF/Excel (via ReportLab/Pandas ou openpyxl)
│   └── ...
├── templates/             # Vues (Fichiers HTML Jinja2)
│   ├── projects/          # Vues liées aux projets (liste, création, mesure)
│   ├── quotes/            # Vues liées aux devis
│   └── ...
├── static/                # Fichiers statiques (CSS, JS, Images, Uploads)
│   └── uploads/           # Stockage des fichiers plans (organisé par company_id/project_id)
└── scripts/               # Scripts utilitaires (seed_data, enrich_questions)
```

## Modèle de Données (Clés)

### Entités Principales
1.  **Company (Entreprise)** : Entité racine pour l'isolation des données (multi-tenant logique).
    *   Possède des `PricingTier` (Éco, Standard, Premium).
    *   Possède des `TaxProfile`.
2.  **Project (Projet)** : Appartient à une Company.
    *   Contient des `ProjectPlan` (fichiers PDF/DWG).
    *   Contient des `Room` (Pièces définies par des mesures).
3.  **Quote (Devis)** : Lié à un Projet.
    *   Possède des `QuoteVersion` (gestion de l'historique V1, V2...).
    *   Chaque version contient des `QuoteLine` (lignes de devis) et des `QuoteAssumption`.

### Flux de Données "Métré"
1.  L'utilisateur upload un plan (PDF).
2.  Le plan est stocké dans `static/uploads/`.
3.  Dans l'interface "Mesure" (`templates/projects/measure.html`), PDF.js rend le fichier sur un `<canvas>`.
4.  Un second `<canvas>` transparent permet à l'utilisateur de dessiner des polygones.
5.  Les coordonnées (pixels) sont converties en mesures réelles (mètres/m²) via un `scale_factor` (facteur d'échelle) défini lors de la calibration.
6.  Les données (surface, périmètre, points du polygone) sont envoyées via l'API (`/api/projects/...`) et stockées dans le modèle `Room`.

## Sécurité & Permissions

- **Authentification** : Basée sur des sessions serveur sécurisées.
- **Contrôle d'Accès (RBAC)** :
    - Décorateur `@require_permission('permission_name')` utilisé sur les routes.
    - Rôles définis dans `models/user.py` (`Role`, `UserRole`).
- **Audit** : Toutes les actions critiques (création, modification, suppression, export) sont enregistrées dans la table `audit_logs` via la fonction `log_action`.
- **Validation** : Nettoyage des noms de fichiers (`secure_filename`) et vérification des extensions autorisées pour les uploads.

## Génération de Documents

La génération de PDF (Devis) est gérée côté serveur, probablement via la bibliothèque **ReportLab** (basé sur les imports typiques de ce genre de stack Python), permettant de créer des documents vectoriels précis incluant le branding de l'entreprise.
