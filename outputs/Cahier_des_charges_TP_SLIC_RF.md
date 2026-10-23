# Cahier des charges de développement

## Classification de parcelles agricoles par superpixels SLIC
### Variante B — caractéristiques spectrales et temporelles + Random Forest

**Version :** 1.0 — base de développement préparatoire  
**Date :** 22 octobre 2026  
**Statut :** prêt à être adapté après le choix des données d’étude

---

## 1. Objet du projet

Le projet consiste à réaliser un prototype reproductible de classification supervisée de zones agricoles à partir d’images Sentinel‑2. L’image est d’abord découpée en superpixels avec SLIC. Des caractéristiques spectrales et temporelles sont ensuite calculées pour chaque superpixel, puis une forêt aléatoire (Random Forest) prédit sa classe.

Le projet porte sur la **classification de couverture/culture**. Un superpixel est une unité de calcul issue de l’image ; il ne doit pas être présenté automatiquement comme une parcelle cadastrale complète. La qualité du résultat dépendra des données, des étiquettes de référence, de la saison observée et de la séparation correcte des données d’évaluation.

## 2. Objectifs et résultats attendus

### Objectif général

Produire un pipeline qui transforme des rasters Sentinel‑2 préparés et des références de terrain documentées en une carte de classes géoréférencée, avec une évaluation quantitative et des éléments permettant de reproduire le traitement.

### Objectifs spécifiques

1. Vérifier les dates, bandes, projections, résolutions, masques qualité et étiquettes disponibles.
2. Harmoniser les images sur une grille commune et masquer les pixels invalides, nuages et ombres.
3. Générer une segmentation SLIC de référence et l’appliquer de façon cohérente à toute la série temporelle.
4. Calculer les statistiques spectrales, les indices et des résumés temporels par superpixel.
5. Associer les superpixels aux classes de référence en contrôlant la pureté des étiquettes.
6. Entraîner et régler une Random Forest avec une partition spatiale/par parcelle sans fuite d’information.
7. Évaluer le modèle par classe et exporter les prédictions et les résultats nécessaires au rapport de TP.

### Résultats attendus

- une carte raster de prédiction géoréférencée ;
- une segmentation SLIC et une table de caractéristiques ;
- une matrice de confusion et les métriques par classe ;
- la configuration, le modèle entraîné, les journaux et une procédure d’exécution ;
- des figures et une explication du pipeline adaptées à la soutenance.

Aucun seuil de précision n’est fixé avant de connaître le jeu de données et d’exécuter les expériences. Les performances devront être rapportées comme observées, sans résultat annoncé à l’avance.

## 3. Périmètre

### Version minimale (obligatoire)

- une zone d’étude et une saison documentées ;
- images Sentinel‑2 de réflectance de surface déjà téléchargées ou fournies ;
- bandes B2, B3, B4, B8, B11 et B12 lorsqu’elles sont disponibles ;
- masque qualité fourni ou produit à partir des métadonnées/couches qualité ;
- segmentation SLIC ;
- statistiques spectrales par superpixel et par date ;
- NDVI et indice NIR–SWIR défini dans la section 5 ;
- étiquettes provenant de polygones ou d’un échantillon fiable ;
- entraînement Random Forest, prédiction cartographique et évaluation ;
- code et paramètres reproductibles.

### Hors périmètre de la première version

- acquisition automatique auprès d’un service satellite ;
- détection cadastrale ou garantie que les superpixels suivent exactement les limites des champs ;
- prédiction de rendement, diagnostic de santé des cultures ou conseil agronomique ;
- déploiement d’un service Web ou d’une application de production ;
- projection de Sammon, ACP obligatoire ou comparaison exhaustive de nombreux classifieurs.

Ces éléments pourront être ajoutés après obtention d’une première chaîne fonctionnelle.

## 4. Données d’entrée et conventions

### 4.1 Images

Entrées attendues : rasters GeoTIFF ou format équivalent, un fichier par date et bande ou un cube multibande, avec métadonnées de projection, transformée géographique, date, valeur NoData et unité/échelle radiométrique.

Les données devront être documentées : source, produit, licence, emprise, dates, saison, bandes, système de coordonnées et traitement déjà appliqué. Les réflectances de surface sont à privilégier. Si les données sont fournies en valeurs entières mises à l’échelle, le facteur d’échelle doit être consigné avant le calcul des indices.

### 4.2 Résolution et alignement

La version de base utilisera une grille projetée locale commune à **20 m**, afin d’aligner les bandes SWIR B11/B12 sur leur résolution native sans prétendre créer du détail supplémentaire. Les bandes à 10 m seront agrégées vers cette grille avec une méthode documentée adaptée aux données continues. Les images de dates différentes devront avoir exactement la même emprise, projection, résolution et alignement de pixels.

La résolution de travail reste un paramètre de configuration si le jeu de données impose un autre choix. Les masques et classes catégorielles seront rééchantillonnés avec une méthode préservant les catégories ; les réflectances continues auront une méthode distincte documentée.

### 4.3 Références de classe

Les étiquettes seront fournies de préférence comme polygones géoréférencés (GeoPackage ou Shapefile) ou comme raster de classes, avec provenance et date. La nomenclature proposée est :

| Code | Classe |
|---:|---|
| 1 | Maïs |
| 2 | Arboriculture (ex. manguiers) |
| 3 | Prairies / savane |
| 4 | Sols nus / surfaces bâties |

Si une classe n’est pas présente dans les données, elle ne devra pas être inventée. La nomenclature réellement disponible sera consignée et appliquée de façon identique à l’entraînement, à l’évaluation et à la carte.

## 5. Prétraitement et caractéristiques

### 5.1 Contrôle qualité

Le programme doit vérifier les fichiers manquants, les dimensions incompatibles, les systèmes de coordonnées, les valeurs NoData, les plages anormales et les dates. Les nuages, ombres et autres pixels invalides doivent être exclus des statistiques. Si aucun masque fiable n’est fourni, cette limite doit apparaître dans le journal et le rapport.

Les scènes et superpixels insuffisamment valides seront soit exclus, soit marqués comme non classables selon un seuil défini dans la configuration. La décision et les nombres d’éléments exclus seront enregistrés.

### 5.2 Segmentation SLIC

La segmentation sera créée une fois à partir d’une image ou composition représentative de la saison, puis les mêmes identifiants de superpixels seront utilisés pour extraire les caractéristiques à toutes les dates. Une segmentation différente à chaque date n’est pas prévue dans la version minimale, car elle rendrait les séries par superpixel difficiles à comparer.

L’image utilisée pour SLIC pourra inclure B2, B3, B4 et B8. Les canaux seront normalisés séparément pour la segmentation afin qu’un canal ne domine pas uniquement par son échelle numérique. Les pixels masqués ne devront pas participer à la segmentation. Les paramètres (nombre approximatif de régions, compacité, itérations, canaux, graine si applicable et version logicielle) seront enregistrés.

Au démarrage, tester plusieurs tailles cibles de superpixels et plusieurs valeurs de compacité autour d’ordres de grandeur espacés. Retenir la configuration après inspection visuelle et comparaison avec les limites de référence disponibles. La taille finale dépendra de la résolution, de la taille habituelle des parcelles et de l’emprise ; elle ne sera pas présentée comme une frontière agricole exacte.

### 5.3 Variables par superpixel

Pour chaque date et superpixel, calculer au minimum la **médiane** des réflectances valides des bandes disponibles parmi B2, B3, B4, B8, B11 et B12. L’écart-type et le taux de pixels valides peuvent être conservés comme variables ou indicateurs de qualité.

Calculer :

- **NDVI** = (B8 − B4) / (B8 + B4) ;
- **NDMI B8–B11** = (B8 − B11) / (B8 + B11), indicateur basé sur le proche infrarouge et le SWIR.

Les dénominateurs proches de zéro devront être masqués ou traités explicitement. Comme le nom NDWI désigne plusieurs formules dans la littérature, le code et le rapport utiliseront le nom **NDMI_B8_B11** avec sa formule ; si l’encadrement exige le terme NDWI, la formule retenue sera écrite à côté du nom.

Les caractéristiques temporelles minimales comprennent les valeurs par date ainsi que, lorsque le nombre d’observations le permet, moyenne, minimum, maximum, amplitude et écart-type saisonniers de NDVI/NDMI. Une date de maximum ou des pentes de croissance/décroissance sont des options, uniquement si les dates sont fiables et suffisamment nombreuses. Les dates manquantes ne seront pas remplacées silencieusement.

Chaque colonne de la table doit avoir un nom stable, une définition, une unité, une date ou une période associée et une règle de valeurs manquantes.

### 5.4 Étiquetage des superpixels

La classe d’un superpixel sera déterminée par la classe dominante de ses pixels ou de sa surface de référence. Le calcul ignorera les pixels sans étiquette. La proportion de la classe dominante (pureté) sera conservée dans la table. Un seuil initial configurable de 0,8 peut être étudié ; il sera validé selon la quantité et la qualité des données. Les superpixels trop mélangés seront exclus de l’apprentissage ou marqués ambigus, avec le nombre d’exclusions rapporté.

## 6. Apprentissage et évaluation

### 6.1 Partitionnement

La partition sera réalisée par parcelle, bloc spatial ou autre groupe géographique indépendant. Les superpixels d’une même parcelle ne doivent pas être répartis entre apprentissage et test. Une séparation aléatoire de superpixels voisins ne pourra servir que d’exploration, car elle risque de surestimer la généralisation.

Point de départ recommandé si le nombre de groupes le permet : environ 60 % des groupes pour l’entraînement, 20 % pour la validation et 20 % pour le test. Les proportions seront adaptées et documentées selon le nombre de parcelles, la présence des classes et la taille de la zone. Le jeu de test sera utilisé une seule fois après les choix de variables et d’hyperparamètres.

### 6.2 Random Forest

Utiliser un classifieur Random Forest multiclasse. Le nombre d’arbres, la profondeur maximale, la taille minimale des feuilles, le nombre de variables candidates par division, la pondération des classes et la graine aléatoire seront configurables. Commencer avec une configuration simple et reproductible, puis régler les paramètres sur validation uniquement.

La standardisation Z-score n’est **pas obligatoire** pour la Random Forest seule. Elle ne sera appliquée que si une méthode sensible à l’échelle est ajoutée, par exemple l’ACP, et ses paramètres seront alors ajustés sur l’entraînement uniquement. L’ACP et les projections exploratoires sont facultatives.

### 6.3 Mesures à produire

Rapporter au minimum :

- matrice de confusion, en précisant si les lignes sont les vraies classes ;
- exactitude globale (accuracy) ;
- précision, rappel et F1-score pour chaque classe ;
- F1 macro et effectifs de test par classe ;
- temps d’entraînement et de prédiction, si mesurables ;
- méthode de partitionnement et distribution des classes dans chaque ensemble.

La conclusion ne devra pas s’appuyer uniquement sur l’exactitude globale. Les erreurs entre maïs et prairies/savane ou arboriculture seront décrites si elles sont observées. Les scores obtenus dépendront du jeu de données et ne sont pas garantis par ce cahier des charges.

## 7. Exigences fonctionnelles

| ID | Priorité | Exigence et critère d’acceptation |
|---|---|---|
| F1 | Obligatoire | Le programme lit une configuration indiquant les chemins, dates, bandes, résolution, classes et paramètres. |
| F2 | Obligatoire | Le contrôle d’entrée détecte les bandes/dates manquantes, les incompatibilités spatiales et les valeurs invalides, puis écrit un message exploitable. |
| F3 | Obligatoire | Les données sont alignées sur une grille commune et le masque qualité est appliqué avant les statistiques. |
| F4 | Obligatoire | Une carte SLIC entière, cohérente spatialement, est exportée avec ses paramètres. |
| F5 | Obligatoire | Une ligne de table correspond à un superpixel ; les caractéristiques, l’identifiant, les dates, la classe/pureté et le groupe spatial sont traçables. |
| F6 | Obligatoire | Le modèle est entraîné sans utiliser les groupes du test pour le réglage. Les paramètres et la graine sont sauvegardés. |
| F7 | Obligatoire | Les métriques, la matrice de confusion et les effectifs par classe sont exportés dans des fichiers lisibles. |
| F8 | Obligatoire | Les prédictions sont réinjectées dans une carte raster avec projection, transformée et codes de classe conservés. |
| F9 | Obligatoire | Un journal récapitule les entrées, exclusions, paramètres, versions et principaux fichiers produits. |
| F10 | Souhaitable | Exporter les superpixels et leurs attributs dans un GeoPackage et produire les figures d’analyse d’erreurs. |
| F11 | Option future | Comparer systématiquement plusieurs tailles/compacités SLIC, ajouter ACP ou comparer avec un autre classifieur. |

## 8. Organisation logicielle proposée

```text
projet_slic_rf/
├── README.md
├── pyproject.toml ou requirements.txt
├── configs/
│   └── default.yaml
├── data/
│   ├── raw/          # entrées sources, conservées intactes
│   ├── processed/    # rasters alignés et masques
│   └── reference/    # parcelles/labels
├── outputs/
│   ├── segments/
│   ├── features/
│   ├── models/
│   ├── maps/
│   ├── metrics/
│   └── figures/
├── src/
│   ├── inventory.py
│   ├── preprocessing.py
│   ├── segmentation.py
│   ├── features.py
│   ├── labels.py
│   ├── training.py
│   ├── evaluation.py
│   └── mapping.py
└── docs/
    └── rapport.md
```

Le traitement devra pouvoir être lancé depuis une instruction documentée, par exemple : `python -m src.pipeline --config configs/default.yaml`. La commande exacte sera fixée au début de l’implémentation. Les chemins de données propres à une machine ne doivent pas être codés en dur dans les modules.

## 9. Livrables

1. Code source et fichier de dépendances avec versions fixées au moment du développement.
2. Fichier de configuration exemple et dictionnaire des caractéristiques.
3. Inventaire des données et journal de contrôle qualité.
4. Raster de superpixels, table de caractéristiques et table étiquetée.
5. Modèle Random Forest sérialisé avec paramètres et ordre des colonnes requis.
6. Carte raster de classes, légende et éventuelle couche vectorielle de superpixels.
7. Matrice de confusion, métriques, figures et analyse des erreurs.
8. Rapport de TP expliquant données, méthodes, résultats, limites et reproductibilité.
9. Support de soutenance avec schéma du pipeline et réponses aux questions méthodologiques.

## 10. Phases de réalisation

1. **Cadrage des données** : choisir l’emprise, la saison, la source des images, les labels et vérifier les licences.
2. **Préparation** : aligner les rasters, appliquer les masques et établir le journal qualité.
3. **SLIC** : produire plusieurs essais de segmentation et documenter le choix.
4. **Caractéristiques et étiquettes** : construire la table des superpixels et contrôler la pureté.
5. **Apprentissage** : créer la séparation spatiale, régler la Random Forest sur validation et figer le pipeline.
6. **Évaluation finale** : calculer les mesures sur le test indépendant et analyser les confusions.
7. **Cartographie et défense** : exporter la carte, documenter les limites et préparer l’explication orale.

## 11. Décisions à prendre avant le développement

Ces éléments ne sont pas encore déterminés par les documents fournis et devront être confirmés avant d’écrire le pipeline :

- zone géographique et saison d’étude ;
- source exacte des images Sentinel‑2 et conditions de licence ;
- disponibilité et provenance des labels de maïs et des classes concurrentes ;
- format des données réellement disponibles ;
- nombre de dates sans nuages et couverture des phases de culture ;
- présence d’identifiants de parcelle permettant une séparation spatiale fiable ;
- matériel disponible et taille maximale de l’emprise.

Si des références fiables ou assez de groupes indépendants manquent, le rapport devra le signaler et réduire la portée des conclusions plutôt que présenter une mesure optimiste comme preuve de généralisation.

## 12. Résumé à présenter au jury

« Nous utilisons SLIC pour regrouper des pixels voisins en unités spatiales homogènes. Pour chaque superpixel, nous calculons des statistiques de réflectance et des indices à plusieurs dates afin de représenter la signature spectrale et son évolution. Une Random Forest apprend ensuite à distinguer les classes à partir de superpixels étiquetés. Nous évaluons le modèle sur des parcelles ou blocs spatiaux indépendants, avec une matrice de confusion et des scores par classe. Les superpixels sont des régions de calcul et ne correspondent pas nécessairement aux limites cadastrales. »

## Références techniques à vérifier au démarrage du développement

- [Documentation officielle de SLIC dans scikit-image](https://scikit-image.org/docs/stable/api/skimage.segmentation.html)
- [Documentation officielle du rééchantillonnage dans Rasterio](https://rasterio.readthedocs.io/en/stable/topics/resampling.html)
- [Documentation officielle de RandomForestClassifier dans scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [Documentation officielle des séparations par groupes dans scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data)

Les versions des bibliothèques évoluent : elles seront vérifiées et verrouillées au moment de l’implémentation, et non supposées à partir de ce document.
