# DevisPro - Bible des Fonctionnalités (Features Full List)

Ce document recense de manière exhaustive et technique l'ensemble des fonctionnalités de l'application DevisPro. Il sert de référence pour le développement, le test et la maintenance.

## 1. Noyau & Sécurité

### 1.1 Authentification
*   **Login :** Authentification par email et mot de passe via `Flask-Login`.
*   **Hashage :** Les mots de passe sont hashés avec `Werkzeug.security` (PBKDF2:SHA256) avant stockage.
*   **Session :** Gestion des sessions serveur sécurisées (clé secrète rotative via variables d'environnement).
*   **Protection Routes :** Utilisation du décorateur `@login_required` sur toutes les routes protégées. Redirection automatique vers `/login` avec paramètre `next` pour préserver la navigation.
*   **Logout :** Invalidation immédiate de la session utilisateur.

### 1.2 Sécurité Applicative
*   **CSRF :** Protection globale contre les requêtes inter-sites via `Flask-WTF` (tokens synchronisés).
*   **Input Validation :** Nettoyage des entrées utilisateur (échappement automatique Jinja2 contre XSS).
*   **Secure Filename :** Utilisation de `werkzeug.utils.secure_filename` pour assainir les noms de fichiers uploadés (suppression des caractères spéciaux, chemins relatifs).
*   **RBAC (Role-Based Access Control) :** Système de permissions granulaires.
    *   Rôles : `ADMIN`, `MANAGER`, `USER`.
    *   Permissions : Définies dans `models/user.py` et vérifiées via le décorateur `@require_permission`.

### 1.3 Audit & Traçabilité
*   **AuditLog :** Enregistrement systématique des actions critiques (CREATE, UPDATE, DELETE, EXPORT) dans la table `audit_logs`.
*   **Données loggées :** Timestamp, `user_id`, `action_type`, `entity_type`, `entity_id`, et payload JSON des modifications (diff).
*   **Visualisation :** Interface dédiée dans les vues de détail (ex: historique d'un devis) affichant "Qui a fait Quoi et Quand".

## 2. Gestion Multi-Entreprise (Tenant)

### 2.1 Configuration Entreprise (`Company`)
*   **Isolation :** Chaque utilisateur appartient à une `Company`. Toutes les requêtes (Projets, Devis, BPU) sont filtrées par `company_id`.
*   **Branding :** Personnalisation complète des documents générés.
    *   Logo (chemin fichier local), Couleurs primaires/secondaires (Hex).
    *   Coordonnées légales (SIRET, RCS, TVA Intra).
    *   Pied de page et Conditions Générales de Vente (CGV) par défaut.
*   **Profil Fiscal (`TaxProfile`) :**
    *   Configuration du taux de TVA par défaut (ex: 20%).
    *   Mode TVA incluse/exclue.
    *   Mentions légales de paiement (délai, acompte %).

### 2.2 Stratégie Tarifaire (`PricingTier`)
*   **Niveaux de Gamme :** Création illimitée de gammes (ex: Économique, Standard, Premium).
*   **Coefficients :** Chaque gamme applique un coefficient multiplicateur global (ex: x1.0, x1.2) sur les prix de base ou mappe vers une colonne spécifique de la BPU (`price_eco`, `price_std`, `price_prem`).
*   **Défaut :** Possibilité de définir une gamme par défaut pour les nouveaux projets.

## 3. Gestion de Projets (CRM)

### 3.1 Fiche Projet
*   **Référence Unique :** Génération automatique au format `PRJ-{YEAR}-{SEQ}` (ex: PRJ-2023-0042) via `models/project.py`. Séquence réinitialisée annuellement par entreprise.
*   **Données Client :** Stockage structuré (Nom, Email, Tel, Adresse Chantier).
*   **Typologie :** Classification pour statistiques et règles métier (Neuf/Rénovation, Maison/Appartement).
*   **Statut :** Workflow d'état (Brouillon -> En cours -> Devis Prêt -> Terminé -> Archivé).

### 3.2 Gestion des Plans (`ProjectPlan`)
*   **Upload :** Support des formats PDF, DWG, DXF.
*   **Stockage :** Organisation physique sur disque : `static/uploads/{company_id}/{project_id}/{uuid}.ext`.
*   **Versioning :** Gestion des révisions de plans (V1, V2...) sans écraser les fichiers originaux.
*   **Méta-données :** Extraction automatique de la taille du fichier et du type MIME.

## 4. Module de Métré & Analyse (Plan Reader)

### 4.1 Visualisation
*   **Moteur de Rendu :** Intégration de `PDF.js` pour le rendu vectoriel haute performance dans le navigateur (Canvas HTML5).
*   **Navigation :** Zoom (molette), Panoramique (drag), Rotation.

### 4.2 Outils de Mesure (Canvas Overlay)
*   **Calibrage :** Définition de l'échelle par l'utilisateur (tracer une ligne sur une cote connue -> saisir la longueur réelle). Calcul du ratio `px/m`.
*   **Polygone (Surface) :**
    *   Tracé point par point avec fermeture automatique.
    *   Calcul temps réel de l'aire (m²) et du périmètre (ml).
    *   Comportement magnétique (snap) aux points existants (prévu).
*   **Ligne (Linéaire) :** Mesure de segments simples ou cumulés (plinthes, cloisons).
*   **Typologie Pièce :** Assignation d'un type (Salon, Chambre, SdB) à chaque mesure pour le regroupement dans le devis.

### 4.3 Données Métrées (`Room`, `Measurement`)
*   **Persistance :** Sauvegarde des coordonnées JSON du polygone pour ré-édition future.
*   **Calculs :** Stockage des valeurs calculées (Surface, Périmètre) et saisies manuelles (Hauteur sous plafond).

## 5. Moteur de Devis (`QuoteGenerator`)

### 5.1 Logique de Génération
Le service `QuoteGenerator` (`services/quote_generator.py`) orchestre la création du devis :
1.  **Récupération du Contexte :** Projet, Gamme de prix sélectionnée (Tier), Réponses au questionnaire.
2.  **Analyse des Métrés :** Agrégation des surfaces par type de pièce ou globalement.
3.  **Application des Règles Métier :**
    *   *Gros Œuvre :* Basé sur la surface totale (Fondations, Murs).
    *   *Second Œuvre :* Basé sur les ratios ou réponses spécifiques (ex: Type de sol -> Carrelage vs Parquet).
    *   *Équipements :* Basé sur le comptage (ex: Nombre de climatisations).
4.  **Lookup BPU (Base de Prix) :**
    *   Recherche par Code Article (ex: `SO-SOL-CARR`).
    *   Priorité 1 : Article Personnalisé Entreprise (`CompanyBPUArticle`).
    *   Priorité 2 : Surcharge Entreprise (`CompanyBPUOverride`).
    *   Priorité 3 : Bibliothèque Standard (`BPUArticle`).
5.  **Calcul Prix :** Application du prix unitaire (selon gamme) x Quantité.

### 5.2 Versioning & Édition
*   **Versions (`QuoteVersion`) :** Chaque modification majeure crée une nouvelle version (V1, V2...) préservant l'historique commercial.
*   **Éditeur de Lignes :**
    *   Modification libre des désignations, quantités et prix unitaires (surcharge locale).
    *   Ajout de lignes manuelles hors BPU.
    *   Réorganisation par Drag & Drop (champ `sort_order`).
*   **Hypothèses :** Ajout de clauses textuelles spécifiques (inclus/exclus) liées à la version.

### 5.3 Calculs Financiers
*   **TVA :** Calcul multi-taux (lignes à 20%, 10%, 5.5%) et consolidation par taux.
*   **Totaux :** HT, TVA, TTC.
*   **Remises :** Application de remises globales (%) ou montant fixe.
*   **Marge :** (Interne) Calcul du coût de revient vs prix de vente pour analyse de rentabilité.

## 6. Base de Prix (BPU)

### 6.1 Structure Hybride
*   **Bibliothèque Nationale (`BPULibrary`) :** Catalogue de référence maintenu par la plateforme (non modifiable par les utilisateurs).
*   **Articles (`BPUArticle`) :** Structure riche (Code, Désignation, Unité, Prix Eco/Std/Prem, Part Main d'œuvre/Matériaux).

### 6.2 Personnalisation (`CompanyBPUOverride`)
*   **Surcharge :** Une entreprise peut redéfinir le prix ou la désignation d'un article standard.
*   **Masquage :** Possibilité de désactiver un article standard pour qu'il n'apparaisse jamais dans les devis.
*   **Articles Custom (`CompanyBPUArticle`) :** Création d'articles propres à l'entreprise, inexistants dans la base nationale.

## 7. Exports & Documents

### 7.1 Génération PDF
*   **Technologie :** `ReportLab` (Python) pour une génération vectorielle précise.
*   **Mise en page :**
    *   En-tête dynamique (Logo, infos entreprise).
    *   Bloc Client & Chantier.
    *   Tableau des prestations (Désignation, U, Qte, PU, Total).
    *   Récapitulatif TVA.
    *   Pied de page légal.
*   **Stockage :** Les PDF générés sont archivés sur le serveur (`static/generated/`).

### 7.2 Export Excel (DQE)
*   **Format :** `.xlsx` natif.
*   **Contenu :** Détail Quantitatif Estimatif complet pour import dans d'autres ERP ou analyse fine.
