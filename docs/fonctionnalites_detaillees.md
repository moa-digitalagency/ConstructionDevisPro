# Liste Détaillée des Fonctionnalités

Ce document recense de manière exhaustive toutes les fonctionnalités implémentées dans l'application.

## 1. Sécurité et Gestion des Accès

### Authentification
- **Connexion Sécurisée** : Formulaire de login (email/mot de passe) avec gestion des sessions serveur.
- **Protection CSRF** : Protection contre les attaques Cross-Site Request Forgery sur tous les formulaires.
- **Hashage des Mots de Passe** : Utilisation de `werkzeug.security` (pbkdf2:sha256) pour le stockage sécurisé.

### Contrôle d'Accès (RBAC)
- **Rôles Utilisateurs** :
    - `ADMIN` : Accès complet à la configuration de l'entreprise et aux utilisateurs.
    - `MANAGER` : Gestion des projets, devis et plans.
    - `USER` : Consultation et actions limitées.
- **Décorateurs de Permission** : `@require_permission` pour sécuriser les routes critiques côté backend.

### Audit et Traçabilité
- **Journal d'Audit (AuditLog)** : Enregistrement automatique des actions sensibles (création, modification, suppression, export).
- **Détails Loggés** : Utilisateur, Date/Heure, Type d'action, Entité concernée, Valeurs avant/après modification.
- **Visualisation** : Affichage de l'historique des modifications dans la vue détaillée des Devis (`templates/quotes/view.html`).

## 2. Gestion de l'Entreprise (Multi-Tenant)

### Configuration
- **Branding** : Personnalisation du logo, nom, adresse, téléphone, email et site web de l'entreprise (utilisé sur les PDF).
- **Mentions Légales** : Texte libre pour les pieds de page des documents officiels (SIRET, RCS, Capital...).
- **Profils de Taxes** : Gestion de multiples taux de TVA (ex: 20%, 10%, 5.5%) applicables par projet.

### Tarification (Pricing Tiers)
- **Niveaux de Gamme** : Configuration de niveaux de prix multiples (Éco, Standard, Premium).
- **Mapping BPU** : Association de chaque niveau à une colonne de prix spécifique dans la base de données.

## 3. Gestion de Projets (CRM Léger)

### Création et Suivi
- **Fiche Projet** : Nom du projet, Type (Neuf, Rénovation), Typologie (Maison, Appartement), Notes internes.
- **Fiche Client** : Nom, Email, Téléphone, Adresse du chantier.
- **Référence Unique** : Génération automatique (format `DEV-YYYY-XXXX` ou similaire).
- **Statuts** : Brouillon, En cours, Terminé, Archivé.

### Recherche et Filtres
- **Liste des Projets** : Vue tabulaire avec tri par date de mise à jour.
- **Filtres** : Filtrage par Statut et par Type de projet via l'interface utilisateur.

## 4. Gestion des Plans et Documents

### Upload de Fichiers
- **Formats Supportés** : PDF, DWG, DXF.
- **Sécurisation** : Renommage unique (UUID) et validation des extensions côté serveur.
- **Organisation** : Stockage structuré par `company_id/project_id` dans le système de fichiers.

### Visualisation
- **Visionneuse PDF** : Intégration de `PDF.js` pour le rendu vectoriel haute fidélité dans le navigateur.
- **Zoom et Panoramique** : Navigation fluide dans les plans de grande taille.

## 5. Module de Métré (Outils de Mesure)

### Calibrage (Mise à l'échelle)
- **Outil de Calibrage** : Définition de l'échelle en traçant une ligne de référence sur une cote connue.
- **Calcul Automatique** : Conversion pixels -> mètres (scale factor).

### Outils de Dessin (Canvas HTML5)
- **Polygone** : Tracé de formes complexes point par point pour les surfaces (m²).
- **Ligne** : Tracé de segments pour les longueurs linéaires (ml).
- **Baguette Magique (Auto)** : Algorithme de détection automatique des contours d'une pièce à partir d'un clic central (simulation actuelle, extensible via vision par ordinateur).
- **Édition** : Déplacement des points existants par glisser-déposer (Drag & Drop) pour ajuster la précision.
- **Annulation** : Suppression du tracé en cours ou effacement complet.

### Gestion des Pièces (Rooms)
- **Calcul Temps Réel** : Affichage instantané de la surface et du périmètre pendant le dessin.
- **Typologie des Pièces** : Catégorisation (Salon, Cuisine, Chambre, SdB...).
- **Sauvegarde** : Enregistrement des métrés dans la base de données liés au projet.
- **Liste des Pièces** : Vue récapitulative des pièces métrées avec leurs surfaces respectives et total général.

## 6. Gestion des Devis (Chiffrage)

### Création et Édition
- **Générateur Intelligent** : Création automatique d'un devis basé sur les métrés du projet et le niveau de gamme choisi.
- **Versioning** : Système complet de versions (V1, V2...) permettant de conserver l'historique des propositions commerciales.
- **Éditeur de Lignes** :
    - Modification des quantités et prix unitaires.
    - Ajout/Suppression de lignes.
    - Saisie de remises ou majorations.
- **Hypothèses** : Ajout de clauses textuelles spécifiques à une version (exclusions, validité).

### Workflow de Validation
- **Statuts** : Brouillon -> Envoyé -> Accepté / Refusé / Expiré.
- **Transition d'État** : Actions boutons pour changer le statut, déclenchant des logs d'audit.

### Export et Documents
- **Export PDF** : Génération côté serveur (ReportLab) d'un document PDF professionnel incluant :
    - En-tête avec logo entreprise.
    - Coordonnées client et chantier.
    - Tableau détaillé des prestations (Désignation, U, Qte, PU, Total).
    - Totaux HT, TVA (par taux), TTC.
    - Mentions légales et pied de page.
- **Export Excel (DQE)** : Génération d'un fichier `.xlsx` détaillé pour exploitation externe.

## 7. Base de Prix (BPU)

### Bibliothèque
- **Structure Hierarchique** : Organisation par Corps d'État (Maçonnerie, Plomberie...) et Familles.
- **Articles Riches** : Code, Libellé court, Descriptif long, Unité.

### Surcharge et Personnalisation
- **Overrides** : Mécanisme permettant à chaque entreprise de redéfinir le prix ou le libellé d'un article standard sans affecter les autres utilisateurs de la plateforme.
