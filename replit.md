# DevisPro - Application de Devis Construction/Rénovation

## Overview
DevisPro is a multi-tenant SaaS application for construction and renovation quotation management. Built with Python Flask backend and vanilla JavaScript frontend with Tailwind CSS.

## Architecture

### Technology Stack
- **Backend**: Python 3.11, Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML, Tailwind CSS (CDN), Vanilla JavaScript
- **PDF Processing**: PyPDF2, pdf.js (client-side)
- **Exports**: ReportLab (PDF), openpyxl (Excel)

### Directory Structure
```
/algorithms     - Calculation engines (measurements, pricing)
/docs           - Documentation
/lang           - Internationalization (future)
/models         - SQLAlchemy database models
/routes         - Flask blueprints (auth, projects, quotes, bpu, admin)
/scripts        - Database seeding and utilities
/security       - RBAC decorators, audit logging
/services       - Business logic (quote generation, exports, BPU)
/static         - CSS, JS, uploaded files
/templates      - Jinja2 HTML templates
/utils          - Helper functions
```

### Key Models
- **Company**: Multi-tenant isolation, branding, tax profiles
- **User**: Authentication, RBAC with roles
- **Project**: Construction/renovation projects with plans
- **BPU**: Bill of Quantities library with company overrides
- **Quote**: Versioned quotations with line items

## Features Implemented

### Core Features (MVP)
1. Multi-tenant architecture with company isolation
2. Role-based access control (Owner, Admin, Métreur, Commercial, Read-only)
3. Company onboarding wizard (country, tax, BPU, tiers, branding)
4. Project creation with type/typology selection
5. PDF plan upload with 2-point scale calibration
6. Polygon drawing tools for quantity takeoff (Canvas API)
7. Question engine for project specifications
8. BPU library by country with version management
9. Company-specific BPU customization (overrides, custom articles)
10. Pricing tiers (Eco/Standard/Premium) with coefficients
11. Quote generation with versioning
12. PDF and Excel export functionality
13. Audit logging for critical changes
14. User management interface

### Database
- PostgreSQL accessed via DATABASE_URL environment variable
- Models auto-create on first run via db.create_all()
- Seed data includes roles, BPU library (Morocco), question templates

## Running the Application
```bash
python app.py
```
The server runs on port 5000.

## Default Seed Data
- **Countries**: Morocco (MA), France (FR), Tunisia (TN), Algeria (DZ), Senegal (SN), Côte d'Ivoire (CI)
- **BPU Library**: Morocco 2025.1 with ~40 articles across categories
- **Roles**: owner, admin, metreur, commercial, readonly
- **Question Templates**: Ceiling height, windows, flooring, HVAC, pool, etc.

## User Preferences
- Language: French (fr)
- Currency: MAD (Moroccan Dirham) default
- VAT: 20% default

## Demo Account
- **Email**: admin@devispro.com
- **Password**: Admin123!
- Auto-created via environment variables DEMO_SUPERADMIN_EMAIL and DEMO_SUPERADMIN_PASSWORD

## Recent Changes
- January 2026: Initial project setup
- Full MVP implementation with all core features
- Added favicon on all pages
- Improved design with color-coded blocks (gradients by section)
- Added plan reader service for DWG/DXF/PDF analysis
- Added BPU service for library management and Excel import/export
- Fixed settings page for new companies without branding/tax profiles
