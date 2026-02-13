# DevisPro : Solution de Métré & Devis BTP

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)
![Version](https://img.shields.io/badge/Version-1.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)

**DevisPro** est une application web métier conçue pour les professionnels du bâtiment (Entreprises Générales, Artisans, Architectes). Elle simplifie radicalement le processus de chiffrage en intégrant le métré sur plan (PDF) directement à la génération de devis.

---

## 📚 Table des Matières
- [Pourquoi DevisPro ?](#-pourquoi-devispro-)
- [Fonctionnalités Clés](#-fonctionnalités-clés)
- [Stack Technique](#-stack-technique)
- [Installation Rapide](#-installation-rapide)
- [Documentation Complète](#-documentation-complète)

---

## 🚀 Pourquoi DevisPro ?

Les outils traditionnels séparent le métré (sur plan papier ou AutoCAD) du chiffrage (Excel). **DevisPro unifie les deux.**

1.  **Importez** vos plans PDF.
2.  **Mesurez** les surfaces directement dans le navigateur.
3.  **Générez** un devis instantané basé sur votre bibliothèque de prix.
4.  **Exportez** le PDF client prêt à l'envoi.

**Gain de temps estimé : 70% sur la phase d'avant-projet.**

---

## ✨ Fonctionnalités Clés

*   **Gestion Multi-Entreprise (SaaS)** : Isolation totale des données, branding personnalisé (Logo, CGV).
*   **Moteur de Métré Intégré** :
    *   Visualisation fluide des plans (PDF.js).
    *   Outils de mesure précis (Polygone, Ligne) avec échelle calibrable.
    *   Calcul automatique des surfaces (m²) et périmètres.
*   **Générateur de Devis Intelligent** :
    *   Conversion automatique *Métré -> Lignes de Devis*.
    *   Gestion des variantes (V1, V2...).
    *   Application de gammes de prix (Éco, Standard, Premium).
*   **Bibliothèque de Prix (BPU)** :
    *   Catalogue national de référence.
    *   Système de surcharge (Override) pour personnaliser vos tarifs.
*   **Exports Professionnels** : Génération de PDF vectoriels via ReportLab et exports Excel détaillés.

---

## 🛠 Stack Technique

Une architecture robuste et éprouvée, taillée pour la performance et la maintenance.

*   **Backend** : Python 3.11, Flask, SQLAlchemy (ORM).
*   **Base de Données** : PostgreSQL (Prod) / SQLite (Dev).
*   **Frontend** : Jinja2, Tailwind CSS, Vanilla JS.
*   **Moteur Graphique** : PDF.js + HTML5 Canvas.
*   **Authentification** : Flask-Login + Hachage Argon2/PBKDF2.
*   **Tests** : Playwright (E2E).

---

## ⚡ Installation Rapide

Prérequis : `Python 3.11+`, `pip`, `git`.

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-orga/devispro.git
cd devispro

# 2. Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Ou .venv\Scripts\activate sous Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Initialiser la base de données
python init_db.py

# 5. Lancer le serveur de développement
flask run
```
Accédez à l'application sur `http://localhost:5000`.

---

## 📖 Documentation Complète

Pour aller plus loin, consultez la documentation détaillée dans le dossier `docs/` :

| Document | Description | Cible |
| :--- | :--- | :--- |
| **[Bible des Fonctionnalités](docs/features_full_list.md)** | Liste exhaustive de toutes les features et règles métier. | Tout le monde |
| **[Architecture Technique](docs/DevisPro_Architecture_Technique.md)** | Détails sur le code, la BDD, la sécurité et les flux. | Développeurs |
| **[Guide d'Installation](docs/DevisPro_Guide_Installation.md)** | Procédures complètes de déploiement (Dev/Prod). | DevOps / Devs |
| **[Guide Utilisateur](docs/DevisPro_Guide_Utilisateur.md)** | Manuel d'utilisation pas à pas (Métré, Devis...). | Utilisateurs Finaux |
| **[Modèle Économique](docs/DevisPro_Modele_Economique.md)** | Explication des Pricing Tiers et de la BPU. | Managers / Business |

---

*Développé avec passion pour le BTP.*
