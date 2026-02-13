# DevisPro - Modèle Économique & Tarification

Ce document explique les concepts fondamentaux qui régissent le calcul des prix, la gestion des marges et la personnalisation des devis au sein de la plateforme.

## 1. Structure Multi-Locataire (Tenant)

Chaque entreprise inscrite sur DevisPro possède son propre environnement isolé. Cela signifie :
*   **Base Clients** : Privée.
*   **Base Prix (BPU)** : Personnalisable (Surcharges).
*   **Identité Visuelle** : Logo, Couleurs, CGV.
*   **Configuration Fiscale** : TVA, Délais de paiement.

## 2. Stratégie de Prix (Pricing Tiers)

L'application gère nativement la notion de "Gamme" pour s'adapter au budget du client final.
Par défaut, 3 niveaux sont configurés pour chaque entreprise :
1.  **Économique (ECO)** : Matériaux standards, finitions basiques. Cible : Investissement locatif, petit budget.
2.  **Standard (STD)** : Bon rapport qualité/prix. Cible : Rénovation classique, résidence principale.
3.  **Premium (PREM)** : Matériaux nobles, finitions haut de gamme. Cible : Luxe, Architecte.

### 2.1 Mécanisme Technique
Chaque `PricingTier` est associé à une logique de sélection de prix dans la BPU :
*   Le Tier "Eco" -> Colonne `unit_price_eco`.
*   Le Tier "Standard" -> Colonne `unit_price_standard`.
*   Le Tier "Premium" -> Colonne `unit_price_premium`.

Il est également possible d'appliquer un **Coefficient Multiplicateur** global (ex: x1.10) sur une gamme pour ajuster rapidement les marges sans modifier chaque article.

## 3. La Base de Prix Unitaire (BPU)

Le cœur du système est une bibliothèque d'ouvrages intelligente structurée en 3 couches (Layered Architecture).

### Couche 1 : Bibliothèque Nationale (Read-Only)
Maintenue par la plateforme, elle contient des milliers d'articles de référence (`BPUArticle`).
*   *Exemple* : `SO-PEINT-BLANC` - Peinture blanche mate 2 couches.
*   *Prix* : Moyenne nationale constatée.

### Couche 2 : Surcharges Entreprise (Override)
L'entreprise peut "surcharger" n'importe quel article de la bibliothèque nationale.
*   *Usage* : Vous achetez votre peinture moins cher ? Vous mettez plus de temps ?
*   *Action* : Crée un enregistrement `CompanyBPUOverride` qui remplace le prix ou le libellé standard pour **votre** entreprise uniquement.
*   *Résultat* : Le devis utilisera votre prix, pas celui de la plateforme.

### Couche 3 : Articles Personnalisés (Custom)
L'entreprise peut créer ses propres articles qui n'existent pas au niveau national.
*   *Exemple* : Forfait "Nettoyage Fin de Chantier - T3".
*   *Stockage* : Table `CompanyBPUArticle`. Priorité absolue sur les couches 1 et 2.

## 4. Algorithme de Calcul du Devis

Lorsqu'un devis est généré, le moteur (`QuoteGenerator`) exécute la séquence suivante pour chaque ligne :
1.  **Identification** : Quel ouvrage est nécessaire ? (ex: Peinture Murs).
2.  **Quantification** : Quelle surface ? (ex: 45m² issus du métré).
3.  **Résolution du Prix Unitaire** :
    *   Cherche un *Article Custom* correspondant.
    *   Sinon, cherche une *Surcharge* active.
    *   Sinon, prend l'*Article Standard*.
4.  **Application de la Gamme** :
    *   Sélectionne la colonne de prix (Eco/Std/Prem) correspondant au choix du devis.
    *   Applique le coefficient éventuel de la gamme.
5.  **Calcul Final** : `Prix Total Ligne = Quantité x Prix Unitaire (Résolu)`.

## 5. Gestion de la TVA & Rentabilité

### 5.1 Profils Fiscaux
Chaque projet est lié à un contexte fiscal (Neuf, Rénovation énergétique...).
*   **Neuf** : TVA 20%.
*   **Rénovation** : TVA 10% (selon éligibilité).
*   **Énergie** : TVA 5.5%.
Le système ventile automatiquement les lignes selon leur catégorie (Main d'œuvre vs Matériaux) si nécessaire, ou applique le taux du projet.

### 5.2 Marge Théorique
Le système conserve (en interne) la part "Main d'œuvre" et "Fourniture" de chaque article. Cela permet, lors de l'export Excel, de calculer une marge théorique estimée :
`Marge = Prix Vente HT - (Coût Main d'œuvre + Coût Matériaux)`.
