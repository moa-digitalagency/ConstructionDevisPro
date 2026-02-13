# DevisPro - Guide Utilisateur

Ce manuel vous accompagne pas à pas dans l'utilisation de la plateforme DevisPro, de la gestion de vos projets à l'envoi de vos devis.

## 1. Démarrage Rapide

### 1.1 Le Tableau de Bord (Dashboard)
Votre centre de contrôle. Il affiche :
*   **Projets Récents** : Accès direct aux 5 derniers dossiers ouverts.
*   **KPIs** : Nombre de devis en attente, chiffre d'affaires potentiel.
*   **Activité** : Journal des dernières actions (qui a modifié quoi).

### 1.2 Navigation
Le menu latéral vous permet d'accéder aux modules :
*   **Projets** : Vos dossiers clients.
*   **Devis** : Tous vos chiffrages.
*   **Bibliothèque (BPU)** : Votre catalogue de prix.
*   **Paramètres** : Configuration de votre entreprise (Logo, Taxes, Utilisateurs).

## 2. Création d'un Projet

Le "Projet" est le dossier qui contient tout : client, plans, métrés et devis.

1.  Cliquez sur **"Nouveau Projet"**.
2.  **Infos Client** : Saisissez le nom, l'email et l'adresse du chantier.
3.  **Typologie** :
    *   *Type* : Rénovation, Neuf, Extension.
    *   *Bien* : Maison, Appartement, Commerce.
    *   *Note* : Ces choix influencent les suggestions du moteur de devis.
4.  Validez. Une référence unique (ex: `PRJ-2023-0042`) est créée.

## 3. Gestion des Plans & Métrés

C'est le cœur de l'application. Vous allez transformer un plan PDF en données chiffrables.

### 3.1 Upload
Dans l'onglet **"Plans"** du projet, glissez-déposez vos fichiers (PDF, DWG, DXF).

### 3.2 L'Interface de Mesure
Cliquez sur un plan pour l'ouvrir. L'interface se compose de :
*   **Vue Plan** : Navigation fluide (Zoom molette, Panoramique clic-droit/drag).
*   **Barre d'Outils** : Calibrage, Polygone, Ligne.
*   **Volet Latéral** : Liste des pièces mesurées.

### 3.3 Étape Clé : Le Calibrage
**Impératif avant toute mesure !**
1.  Sélectionnez l'outil **"Règle de Calibrage"**.
2.  Repérez une cote lisible sur le plan (ex: un mur coté à 4.50m).
3.  Tracez une ligne précise sur ce mur.
4.  Dans la fenêtre qui s'ouvre, entrez la valeur réelle : `4.5`.
5.  Le logiciel calcule l'échelle. Vous pouvez maintenant mesurer.

### 3.4 Tracer les Pièces
1.  Sélectionnez l'outil **"Polygone"**.
2.  Cliquez sur chaque coin de la pièce (le tracé suit votre souris).
3.  Pour fermer la forme, revenez au point de départ ou double-cliquez.
4.  **Qualification** : Une fenêtre s'ouvre.
    *   *Nom* : Ex: "Chambre Parents".
    *   *Type* : Ex: "Chambre" (Important pour le devis auto).
    *   *HSP* : Hauteur sous plafond (par défaut 2.50m).
5.  La surface (m²) et le périmètre (ml) sont sauvegardés.

## 4. Génération & Édition du Devis

### 4.1 Le Moteur Intelligent
1.  Allez dans l'onglet **"Devis"** du projet.
2.  Cliquez sur **"Générer un Devis"**.
3.  Choisissez la **Gamme** (Éco, Standard, Premium).
4.  Le système analyse vos métrés et génère une **Version 1 (Brouillon)**.
    *   *Exemple* : Il voit 45m² de "Chambre" -> Il ajoute 45m² de "Peinture" et "Sol".

### 4.2 Personnalisation
Le devis généré est une base modifiable :
*   **Modifier** : Cliquez sur une ligne pour changer la quantité ou le prix.
*   **Ajouter** : Insérez une ligne manuelle ou depuis la BPU.
*   **Organiser** : Utilisez les poignées (drag & drop) pour réordonner les lignes.
*   **Supprimer** : Retirez les prestations inutiles.

### 4.3 Versioning
Le client veut changer le sol ? Ne modifiez pas la V1 !
1.  Cliquez sur **"Créer une Nouvelle Version"**.
2.  La V2 est créée (copie de la V1).
3.  Faites vos modifications. L'historique V1 reste intact pour comparaison.

## 5. Export & Finalisation

Une fois le devis prêt :
1.  Passez le statut à **"Envoyé"** (fige la version).
2.  Cliquez sur **"Télécharger PDF"**.
    *   Le document contient votre logo, les mentions légales, le détail HT/TTC et les conditions de paiement.
3.  Optionnel : Exportez en **Excel** pour vos calculs de marge internes.
