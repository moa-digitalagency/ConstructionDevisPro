# Modèle Économique et Tarification

Ce document explique la structure des coûts, la gestion des prix et le fonctionnement de la base de données tarifaire (BPU).

## 1. Structure Multi-Entreprise

L'application est conçue pour être utilisée par plusieurs entités (Entreprises Générales, Artisans, Architectes). Chaque **Entreprise** (`Company`) est cloisonnée :
*   Elle possède ses propres clients.
*   Elle gère ses propres projets.
*   Elle dispose de sa propre configuration de marque (Logo, adresse, SIRET).
*   Elle applique ses propres règles fiscales (Profils de TVA).

## 2. Niveaux de Gamme (Pricing Tiers)

Pour s'adapter à différents standings de projets (logement social, résidentiel standard, luxe), l'application utilise le concept de **Pricing Tiers** (Niveaux de Gamme).

Par défaut, trois niveaux sont configurés :
1.  **Économique** : Matériaux d'entrée de gamme, finitions basiques.
2.  **Standard** : Matériaux de qualité courante, bon rapport qualité/prix.
3.  **Premium** : Matériaux nobles, finitions haut de gamme, prestations complexes.

Chaque niveau est associé à une colonne de prix spécifique dans la Base de Prix Unitaire.

## 3. La Base de Prix Unitaire (BPU)

La BPU est le catalogue central des ouvrages. Chaque article (`BPUArticle`) est défini par :
*   Un code unique.
*   Une désignation technique.
*   Une unité de mesure (m², ml, u, ens).
*   Une catégorie (ex: "Gros Œuvre", "Électricité", "Peinture").

### Structure des Prix
Contrairement à un prix unique, chaque article possède trois prix de vente, correspondant aux niveaux de gamme :
*   `price_eco` : Prix de vente pour la gamme Économique.
*   `price_std` : Prix de vente pour la gamme Standard.
*   `price_premium` : Prix de vente pour la gamme Premium.

### Surcharge des Prix (Overrides)
Une entreprise peut décider de personnaliser les prix d'un article de la bibliothèque standard via les `CompanyBPUOverride`. Cela permet d'ajuster ses marges ou ses coûts spécifiques sans altérer la bibliothèque globale partagée.

## 4. Calcul des Devis

Lors de la création d'un devis pour un projet, l'utilisateur sélectionne le **Niveau de Gamme** applicable (ex: Standard).

Le moteur de calcul procède alors comme suit :
1.  Il récupère les métrés (quantités) validés dans le projet.
2.  Pour chaque ouvrage nécessaire (défini par les règles métier ou saisi manuellement), il cherche l'article correspondant dans la BPU.
3.  Il applique le prix unitaire correspondant à la gamme choisie (`price_std` dans notre exemple).
4.  Le montant de la ligne est calculé : `Montant HT = Quantité x Prix Unitaire`.
5.  La TVA est appliquée selon le profil fiscal du projet (ex: 20% pour le neuf, 10% pour la rénovation).

## 5. Marges et Rentabilité

Bien que non visible sur le devis client, le système peut gérer en interne les coûts de revient (Fourniture + Main d'œuvre) pour calculer la marge brute estimée par chantier. Cette fonctionnalité permet aux gestionnaires de vérifier la rentabilité avant d'envoyer l'offre.
