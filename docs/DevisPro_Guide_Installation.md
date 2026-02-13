# DevisPro - Guide d'Installation & Configuration

Ce guide détaille les étapes pour installer, configurer et démarrer l'application DevisPro en environnement de développement et de production.

## 1. Prérequis

Avant de commencer, assurez-vous de disposer des outils suivants :
*   **Python 3.11+** (Requis pour certaines fonctionnalités de type hinting et performance).
*   **pip** (Gestionnaire de paquets Python).
*   **Git** (Pour cloner le dépôt).
*   **PostgreSQL** (Recommandé pour la production, SQLite par défaut en dev).

## 2. Installation (Pas à Pas)

### 2.1 Cloner le Projet
```bash
git clone https://github.com/votre-orga/devispro.git
cd devispro
```

### 2.2 Créer un Environnement Virtuel
Il est fortement recommandé d'isoler les dépendances du projet.
```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 2.3 Installer les Dépendances
```bash
pip install -r requirements.txt
```
*Note : Si vous utilisez `uv` pour la gestion rapide des paquets, vous pouvez faire `uv pip install -r requirements.txt`.*

## 3. Configuration

L'application se configure via des variables d'environnement. Créez un fichier `.env` à la racine (ou exportez les variables dans votre shell).

### Variables Essentielles
| Variable | Description | Valeur par défaut (Dev) |
| :--- | :--- | :--- |
| `FLASK_APP` | Point d'entrée de l'application | `app.py` |
| `FLASK_ENV` | Mode d'exécution | `development` |
| `FLASK_SECRET_KEY` | Clé secrète pour signer les sessions | `dev-secret-key...` (Changez-la !) |
| `DATABASE_URL` | Chaîne de connexion à la BDD | `sqlite:///devispro.db` |

**Exemple `.env` pour PostgreSQL :**
```ini
FLASK_APP=app.py
FLASK_ENV=production
FLASK_SECRET_KEY=super-secret-key-change-me
DATABASE_URL=postgresql://user:password@localhost:5432/devispro
```

## 4. Base de Données

L'application inclut un script d'initialisation intelligent qui crée les tables et, si elles existent déjà, tente d'ajouter les colonnes manquantes (migration soft).

### 4.1 Initialiser le Schéma
```bash
python init_db.py
```
Ce script va :
1.  Se connecter à la base définie dans `DATABASE_URL`.
2.  Créer toutes les tables définies dans `models/`.
3.  Vérifier l'intégrité du schéma.

### 4.2 Peupler les Données (Seed)
Le script `seed_data.py` est appelé automatiquement au premier démarrage via `app.py` (dans le contexte `create_app`), mais vous pouvez le forcer ou l'inspecter dans `scripts/seed_data.py`. Il crée :
*   L'utilisateur Admin par défaut.
*   Les catégories BPU de base.
*   Les Pricing Tiers (Éco, Standard, Premium).

## 5. Démarrage

### 5.1 Mode Développement
```bash
flask run --host=0.0.0.0 --port=5000
# Ou directement via Python
python app.py
```
L'application sera accessible sur `http://localhost:5000`.

### 5.2 Mode Production (Gunicorn)
Pour un déploiement robuste, utilisez le serveur WSGI Gunicorn (déjà dans `requirements.txt`).
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```
*   `-w 4` : Lance 4 processus workers (ajustez selon vos CPU).
*   `-b` : Bind sur le port 8000.

## 6. Dépannage

*   **Erreur de Migration** : Si vous modifiez un modèle existant de manière incompatible (ex: renommage de colonne), le script `init_db.py` peut échouer. Dans ce cas, connectez-vous manuellement à la BDD pour ajuster la table ou supprimez le fichier `devispro.db` (en dev uniquement !) pour repartir de zéro.
*   **Problème PDF** : Si la génération de PDF échoue, vérifiez que le dossier `static/generated/` existe et est accessible en écriture par l'utilisateur exécutant l'application.
