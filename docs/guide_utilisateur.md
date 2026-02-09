# Guide Utilisateur

Ce document décrit les principaux flux de travail de l'application, de la création d'un projet à l'export du devis final.

## 1. Tableau de Bord (Dashboard)

À la connexion, vous arrivez sur le tableau de bord principal. Cette vue centralise :
*   Les **projets récents** : Accès rapide aux derniers dossiers travaillés.
*   L'**activité récente** : Historique des actions (création de devis, modifications de plans, etc.) via le journal d'audit.
*   Les **notifications** : Alertes sur les tâches en attente ou les statuts de validation.

## 2. Gestion des Projets

Le projet est l'entité centrale. Il regroupe les informations client, les plans techniques et les devis associés.

### Créer un Projet
1.  Cliquez sur "Nouveau Projet" depuis le menu ou le tableau de bord.
2.  Remplissez les informations du client (Nom, Adresse, Email).
3.  Sélectionnez le **Type de Projet** (Construction Neuve, Rénovation, Extension...) et la **Typologie** (Maison Individuelle, Immeuble...).
4.  Une référence unique (ex: `PRJ-2023-0042`) est générée automatiquement.

### Ajouter des Plans
1.  Dans la vue du projet, allez dans l'onglet "Plans".
2.  Cliquez sur "Uploader un plan".
3.  Formats acceptés : **PDF, DWG, DXF**.
4.  Une fois uploadé, le plan est prêt pour le calibrage et le métré.

## 3. Module Métrés & Calibrage

Avant de mesurer, il faut définir l'échelle du plan.

### Étape 1 : Calibrage
1.  Ouvrez le plan en mode "Calibrage".
2.  Repérez une cote connue sur le plan (ex: un mur de 5.00m).
3.  Tracez une ligne correspondant à cette cote.
4.  Saisissez la longueur réelle (ex: 5).
5.  Le système calcule le **facteur d'échelle** (pixels par mètre).

### Étape 2 : Prise de Mesures
1.  Ouvrez le plan en mode "Métré".
2.  Utilisez les outils disponibles :
    *   **Polygone** : Cliquez point par point pour détourer une pièce. Double-cliquez ou fermez la forme pour terminer.
    *   **Ligne** : Pour mesurer des longueurs linéaires (cloisons, plinthes).
    *   **Baguette Magique (Auto)** : Cliquez au centre d'une pièce pour tenter une détection automatique des contours (nécessite des murs nets).
3.  Une fois la forme tracée, une fenêtre latérale s'ouvre.
4.  Nommez la pièce (ex: "Salon", "Chambre 1") et définissez son type.
5.  La surface (m²) et le périmètre (ml) sont calculés instantanément.
6.  Cliquez sur "Enregistrer". La pièce s'ajoute à la liste du projet.

## 4. Génération de Devis

Le module de devis utilise les métrés et la bibliothèque de prix (BPU) pour chiffrer le projet.

### Créer un Devis
1.  Depuis la page du projet, cliquez sur "Créer un devis".
2.  Choisissez la **Gamme de Prix** (Éco, Standard, Premium). Cela sélectionnera automatiquement les tarifs correspondants dans la BPU.
3.  Le devis est généré en version "Brouillon" (Draft).

### Édition et Versioning
*   **Modifier** : Vous pouvez ajuster les quantités, ajouter des lignes manuelles ou modifier des descriptions.
*   **Versions** : Si le client demande des modifications majeures, créez une **Nouvelle Version** (V1 -> V2). L'historique des anciennes versions est conservé intact.
*   **Hypothèses** : Ajoutez des notes techniques ou exclusions spécifiques à cette version.

### Export
Une fois le devis validé, vous pouvez l'exporter :
*   **PDF** : Document formel avec en-tête de l'entreprise, détails techniques et conditions générales.
*   **Excel (DQE)** : Détail Quantitatif Estimatif pour analyse ou import dans d'autres outils.

## 5. Administration

### Profil Entreprise
Gérez votre logo, vos coordonnées et vos mentions légales qui apparaîtront sur les PDF.

### Configuration Fiscale
Définissez vos profils de TVA (taux réduit, normal) applicables selon le type de travaux.

### Gestion des Utilisateurs
(Fonction réservée aux administrateurs)
Ajoutez des collaborateurs et assignez des rôles (Admin, Chef de Projet, Utilisateur) pour contrôler l'accès aux fonctionnalités sensibles.
