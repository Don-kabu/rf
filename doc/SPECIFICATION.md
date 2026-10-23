# Spécification fonctionnelle

## 1. Objet

Construire un prototype pédagogique reproductible pour classifier des unités spatiales à partir d’images Sentinel‑2. La zone pilote retenue est un carré d’environ 10 × 10 km centré sur Mbanza‑Ngungu, Kongo Central, défini dans `data/aoi/mbanza_ngungu_10km.geojson`. Le centroïde et les quatre coins contrôlés tombent dans l’AEZ 4010 de WorldCereal. Le produit annuel `temporarycrops` est le candidat principal pour un label binaire ; la saison principale maïs `tc-maize-main` est également définie dans cette AEZ (DOY 43–214). ESA WorldCover 2021 reste une source de labels généraux. Le cahier fourni mentionne aussi quatre classes (maïs, arboriculture, prairies/savane, sols nus/surfaces bâties) : les cartes globales candidates ne fournissent pas directement cette nomenclature complète. L’audit et l’accord avec l’encadrement détermineront si le TP garde ces quatre classes avec des annotations compatibles, ou démontre le pipeline sur une nomenclature proxy plus simple. Le pipeline visé est : contrôle des images → segmentation SLIC → caractéristiques spectrales/temporelles → attribution de labels → Random Forest → évaluation → carte.

Le périmètre est celui d’un **TP et d’un démonstrateur local**, pas d’un service de production : priorité à une chaîne courte, reproductible et explicable pendant la soutenance.

L’application comprend un client Vue.js et une API FastAPI. Dans le prototype actuel, l’API expose une simulation déterministe de résultats afin de valider l’interface et le contrat d’échange. Cette simulation ne charge pas d’images et n’entraîne aucun classifieur.

## 2. Utilisateurs et besoins

- **Étudiant développeur :** configurer le traitement, comprendre les entrées/sorties et obtenir des résultats reproductibles.
- **Étudiant présentateur :** expliquer le rôle de SLIC, des caractéristiques, de Random Forest et de l’évaluation.
- **Enseignant/jury :** vérifier les données, les choix méthodologiques, les résultats et les limites.

## 3. Objectifs mesurables

1. Lancer le client et l’API localement à partir des instructions du dépôt.
2. Montrer un parcours de démonstration avec paramètres, carte synthétique, matrice de confusion et métriques cohérentes entre elles.
3. Afficher en permanence que les résultats du mode démonstration sont fictifs.
4. Définir un contrat stable pour remplacer le simulateur par le vrai pipeline plus tard.
5. Lorsque les données seront intégrées, garantir un test indépendant par bloc spatial, rapporter les métriques par classe et qualifier les cartes ESA de références cartographiques indirectes, non de relevés terrain.

Aucun objectif chiffré d’accuracy n’est fixé pour le futur modèle avant l’analyse des données de référence.

## 4. Périmètre par version

### V0 — prototype disponible

- client Vue.js/Vite pour sélectionner quelques paramètres de démonstration ;
- serveur FastAPI avec vérification d’état et endpoint de simulation ;
- résultat synthétique déterministe ;
- affichage d’une carte catégorielle illustrative, métriques, matrice de confusion et importances illustratives ;
- tests du contrat API et des formules de métriques ;
- documentation Markdown dans `doc/`.

### V1 — pipeline géospatial (à développer après contrôle des pixels et produits)

- étude pilote dans l’emprise GeoJSON d’environ 10 × 10 km centrée sur Mbanza‑Ngungu (Kongo Central, AEZ WorldCereal 4010) ;
- lecture d’images Sentinel‑2 L2A de 2021 et audit des pixels des produits WorldCereal/WorldCover ;
- harmonisation spatiale et masquage des nuages/ombres ;
- SLIC de référence appliqué de façon cohérente aux dates ;
- extraction des bandes B2, B3, B4, B8, B11, B12, NDVI et indice NIR–SWIR ;
- labels proxy dérivés du produit réellement choisi ; ne pas mélanger des nomenclatures ESA pour prétendre avoir les quatre classes du cahier ; si les quatre classes sont exigées, obtenir des annotations locales compatibles ; contrôle de confiance/pureté et exclusion du NoData ;
- partitionnement indépendant par parcelle ou bloc géographique ;
- entraînement Random Forest, évaluation et export géographique.

Les scores calculés contre WorldCereal ou WorldCover mesureront l’accord du modèle avec ces cartes, pas une précision vérifiée par des relevés de terrain indépendants. Ces cartes sont dérivées de données d’observation de la Terre ; cette dépendance doit être signalée. Le produit maïs, s’il est utilisé, ne permettra pas d’identifier toutes les cultures locales. Une validation de terrain indépendante reste nécessaire pour revendiquer une précision agricole réelle.

### Hors périmètre initial

Acquisition automatique, délimitation cadastrale, estimation de rendement, hébergement public, authentification, traitement distribué, historique persistant des runs et garantie d’une précision minimale. Le client Vue et l’API FastAPI servent uniquement à présenter la démonstration locale.

## 5. Exigences fonctionnelles

### Données et configuration

- Les chemins, dates, bandes, CRS, résolution, seuils qualité et paramètres SLIC sont configurables ; aucun chemin machine ne doit être codé en dur.
- Les images sources sont préservées ; les sorties vont dans un dossier distinct.
- Les fichiers incompatibles, dates manquantes et valeurs invalides déclenchent un diagnostic lisible.
- Les référentiels indiquent au minimum la source, la date, la licence et la méthode de création des labels.

### Segmentation

- Une segmentation de référence provient d’une image/composition représentative.
- Les mêmes identifiants de superpixels servent à extraire toutes les dates de la série.
- Les bandes utilisées pour SLIC sont mises à une échelle comparable ; les pixels masqués ne contribuent pas au calcul.
- Le nombre approximatif de régions, compacité, résolution et méthode de validation visuelle sont consignés.
- Les superpixels sont explicitement présentés comme unités d’analyse, pas comme parcelles cadastrales garanties.

### Caractéristiques

Pour chaque superpixel et date, calculer des statistiques des bandes disponibles. Le minimum recommandé est la médiane des bandes ; moyenne, écart-type et proportion valide sont des compléments.

Formules de base :

- `NDVI = (B8 - B4) / (B8 + B4)` ;
- `NDMI_B8_B11 = (B8 - B11) / (B8 + B11)`.

Le terme NDWI étant ambigu selon la formule retenue, le code doit conserver le nom `NDMI_B8_B11` ou documenter explicitement l’alias imposé par l’encadrement. Dénominateurs proches de zéro et dates manquantes doivent être traités explicitement.

### Labels et apprentissage

- Classes candidates V1 : `culture temporaire / hors culture temporaire` à partir de WorldCereal ; éventuellement `maïs / non-maïs dans le masque des cultures temporaires` à partir du produit saisonnier ; sinon `cultivé / autre couverture valide` à partir de WorldCover classe 40. Valider la disponibilité locale, la confiance et le masque avant d’entraîner. Exclure les pixels sans donnée ou de confiance insuffisante.
- L’étiquette d’un superpixel est déterminée par la classe dominante du raster de référence retenu ; la confiance/pureté et le nombre d’éléments écartés sont enregistrés. Les segments trop mixtes sont rejetés selon un seuil documenté.
- La séparation train/validation/test se fait par parcelle ou bloc spatial. Aucun groupe ne doit apparaître dans plusieurs partitions.
- Le jeu de test ne sert pas au choix des variables ou des hyperparamètres.
- Random Forest est le classifieur principal. Le Z-score n’est pas une obligation pour ce modèle ; il est ajusté sur train uniquement si une méthode sensible à l’échelle est ajoutée.

### Évaluation

Produire : matrice de confusion (orientation documentée), accuracy globale, précision/rappel/F1 par classe, F1 macro, effectifs par classe, et distribution des classes par partition. L’accuracy seule n’est pas suffisante en cas de déséquilibre.

### Client et API

- Le client permet de lancer le scénario de démonstration, visualiser les paramètres envoyés et lire le résultat retourné par l’API.
- Les erreurs réseau et API sont affichées clairement ; le chargement et l’état vide sont gérés.
- L’indicateur « Simulation synthétique » reste visible avec les résultats de démonstration.
- Les réponses sont typées/validées côté API et retournées en JSON.
- Pour chaque réponse, l’ordre des classes définit l’ordre des lignes et colonnes de la matrice ; les identifiants restent uniques et les métriques doivent correspondre aux comptes de cette matrice.

## 6. Exigences non fonctionnelles

- **Reproductibilité :** configuration conservée, graine définie, versions de bibliothèques fixées dans les fichiers de dépendances.
- **Traçabilité :** chaque sortie doit pouvoir être associée aux données, paramètres et versions utilisés.
- **Lisibilité :** les cartes, métriques et classes comportent titres, unités/légendes et explication de la matrice.
- **Sécurité locale :** CORS limité aux origines locales de développement ; aucun secret ou jeton requis dans le prototype.
- **Évolutivité :** garder séparés API, simulateur, futur pipeline géospatial et client.

## 7. Critères d’acceptation

- [ ] L’API démarre localement et répond à `/api/v1/health`.
- [ ] Le client Vue.js démarre et peut joindre l’API locale.
- [ ] Le clic de simulation affiche un résultat déterministe et marque explicitement le résultat comme synthétique.
- [ ] La somme de la diagonale de la matrice de confusion correspond au nombre de prédictions correctes et l’accuracy affichée est recalculable depuis cette matrice.
- [ ] Précision, rappel et F1 sont cohérents avec la matrice et l’ordre des classes affiché.
- [ ] Le cas d’une API indisponible est présenté à l’utilisateur sans bloquer l’interface.
- [ ] Les tests automatiques de l’API passent.
- [ ] Le schéma rejette une matrice non carrée, des classes incohérentes et des métriques incompatibles avec les comptes.
- [ ] Le README et les documents de `doc/` permettent de lancer le projet et de comprendre ce qui est simulé.
- [ ] Pour V1, les partitions sont indépendantes par groupe spatial et le rapport ne présente aucun score simulé comme résultat réel.

## 8. Hypothèses et questions ouvertes

À décider avant V1 : disponibilité effective et confiance des pixels WorldCereal sur l’emprise, date ou composite de 2021, conventions de bandes, méthode de blocs spatiaux, résolution finale et volume de scènes. L’emprise et l’AEZ 4010 sont fixées ; les produits WorldCereal sont le premier choix et WorldCover le repli. Une résolution initiale de 20 m est proposée si B11/B12 sont nécessaires ; elle devra être harmonisée avec le raster de référence à 10 m.
