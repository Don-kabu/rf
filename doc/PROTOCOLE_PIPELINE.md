# Protocole provisoire du pipeline scientifique

Ce document fixe les règles méthodologiques qui peuvent être préparées avant le téléchargement et l’inspection des rasters. Il ne prétend pas que le pipeline a été exécuté. Les décisions qui dépendent de la résolution, des pixels disponibles ou de la nomenclature acceptée restent explicitement ouvertes.

La configuration de départ est dans [`backend/examples/pipeline_config_template.json`](../backend/examples/pipeline_config_template.json). Elle sert de fiche à compléter ; l’application ne la lit pas encore. Les primitives de calcul sont dans `backend/app/pipeline/` et prennent des tableaux NumPy déjà alignés. La lecture GeoTIFF, le reprojection/rééchantillonnage et l’orchestration complète restent à raccorder.

## Décisions de méthode proposées

| Étape | Proposition initiale | À confirmer plus tard |
|---|---|---|
| Série d’images | Sentinel‑2 L2A harmonisé, année 2021 | Fenêtres temporelles et dates valides après inspection des nuages et des labels |
| Bandes | B2, B3, B4, B8, B11, B12 | Grille commune et résolution après décision sur les bandes natives à 10 m et 20 m |
| Masque qualité | Exclure NoData, pixels saturés/défectueux, ombres et nuages/cirrus via SCL (classes 0, 1, 3, 8, 9, 10, 11) | Vérifier le masque et la couverture dans l’emprise |
| Composition de référence SLIC | Image multispectrale représentative ; normalisation par bande en clipant les percentiles 2–98 vers [0,1] | Date/composite, bandes d’entrée, nombre de segments et compacité après inspection des contours |
| Variables spectrales | Médiane par bande et indices NDVI et NDMI B8–B11 | Statistiques temporelles retenues selon le nombre de dates valides |
| Attribution de classe | Classe majoritaire des pixels de référence dans le superpixel | Source de labels et nomenclature acceptée par l’encadrement |
| Pureté minimale | 0,70 comme seuil de départ à comparer à 0,60 et 0,80 | Seuil à retenir après mesurer les segments conservés et leur répartition |
| Partition | Séparation spatiale par blocs, cible indicative 80 % apprentissage / 20 % test | Taille des blocs selon l’échelle des superpixels et l’autocorrélation observée |
| Classifieur | Random Forest, 300 arbres, `max_features=sqrt`, `class_weight=balanced`, graine 42 | Réglage éventuel uniquement dans les blocs d’apprentissage/validation |
| Évaluation | Matrice de confusion (lignes = référence, colonnes = prédiction), accuracy, précision/rappel/F1 par classe et F1 macro | Dépend des classes et des groupes qui restent valides après filtrage |

Ces valeurs sont un protocole de départ, pas des résultats ni des paramètres optimaux. En particulier, les 500 superpixels et la compacité 10 de la simulation d’interface ne sont pas des recommandations pour l’emprise réelle.

## Calcul des variables

Pour chaque pixel valide, les indices sont calculés avant l’agrégation par superpixel :

- `NDVI = (B8 - B4) / (B8 + B4)` ;
- `NDMI_B8_B11 = (B8 - B11) / (B8 + B11)`.

Un dénominateur nul ou quasi nul donne une valeur invalide, ignorée dans les statistiques. Les médianes ne doivent utiliser que les pixels non masqués. L’écart-type ou les quantiles peuvent être ajoutés si le nombre de dates et la taille du jeu le permettent. Le nom `NDMI_B8_B11` est conservé pour éviter l’ambiguïté du terme NDWI.

Le module `features.py` accepte une pile `dates × hauteur × largeur × bandes`, un raster de superpixels et un masque facultatif. Il renvoie les identifiants de superpixels, une matrice de variables et les noms de colonnes. Les statistiques temporelles sont calculées sur les médianes spatiales par date. Les lignes avec des valeurs manquantes doivent être filtrées avant le classifieur.

Pour un superpixel `s`, la pureté est :

```text
pureté(s) = nombre de pixels valides de la classe majoritaire / nombre total de pixels de référence valides dans s
```

Les superpixels sans pixels de référence valides sont exclus. Ceux dont la pureté est sous le seuil choisi sont exclus de l’apprentissage ; leur nombre et leur proportion sont rapportés.

Cette règle est implémentée dans `labels.py`. Les codes de classe d’origine sont conservés, y compris la valeur 0 si elle représente une vraie classe ; les codes NoData doivent être passés explicitement dans `ignored_values`.

## Prévenir la fuite spatiale

Les identifiants de superpixels voisins ne sont pas des groupes indépendants. Le découpage doit donc attribuer des blocs géographiques complets à une partition unique ; aucun bloc ne peut apparaître à la fois en apprentissage et en test. La taille des blocs ne peut pas être arrêtée sérieusement avant de connaître la résolution finale et l’échelle spatiale de l’emprise. Le test reste isolé de tout réglage des paramètres.

`spatial_split.py` contient la création de groupes à partir de coordonnées projetées en mètres ainsi qu’un découpage qui garde chaque groupe dans une seule partition. Le fractionnement vise une part de groupes ; la part exacte de superpixels dépend de la taille des blocs. Il faudra contrôler les classes présentes dans le test après le découpage.

## Segmentation et classifieur

`segmentation.py` expose une normalisation par canal, puis une fonction SLIC qui accepte une image 2D ou une composition `hauteur × largeur × canaux`, un masque de validité et des paramètres explicites. La normalisation candidate utilise les percentiles 2 et 98 calculés sur les pixels valides ; ces bornes devront être contrôlées visuellement. Le label 0 est réservé aux pixels masqués.

`classifier.py` expose le Random Forest de départ (300 arbres, `max_features="sqrt"`, poids de classes équilibrés, graine 42) et le calcul des résultats sur une partition de test. Le module exige des variables finies et n’effectue ni entraînement ni évaluation tant qu’on ne lui fournit pas les tableaux. Les dépendances optionnelles sont dans `backend/requirements-pipeline.txt` ; elles ne sont pas nécessaires au lanceur de la simulation Vue/FastAPI.

## Rapport de résultats attendu

Chaque exécution réelle devra conserver au minimum : source et période des images, produit de référence et version, classes et correspondance, AOI, bandes et résolution, règles de masque, paramètres SLIC, variables, seuil de pureté, groupes de chaque partition, paramètres Random Forest, graine, versions logicielles et effectifs retenus/écartés.

Les métriques sont calculées uniquement sur les groupes de test. Le calcul réutilisable se trouve dans `backend/app/metrics.py` ; il attend une matrice dont les lignes sont les classes de référence et les colonnes les classes prédites. Si les labels sont issus de WorldCereal ou WorldCover, le rapport parlera d’accord avec la carte de référence et précisera qu’il ne s’agit pas d’une validation de terrain indépendante.

## Ce qui peut être fait maintenant

- [x] Décrire les formules spectrales, la règle de majorité/pureté et le découpage spatial.
- [x] Préparer une configuration lisible, avec les champs dépendant des rasters laissés vides.
- [x] Rendre le calcul des métriques générique pour qu’il puisse être réutilisé après l’apprentissage.
- [x] Renforcer le contrat API pour refuser une matrice et des métriques incohérentes.
- [x] Implémenter les primitives array-based SLIC, extraction spectrale, étiquetage majoritaire, découpage spatial et Random Forest ; elles restent à raccorder et à exécuter sur les rasters.
- [ ] Implémenter et exécuter les opérations raster, SLIC, extraction et apprentissage après confirmation des labels et disponibilité des données.

## Références API

- [scikit-image — fonction SLIC](https://scikit-image.org/docs/stable/api/skimage.segmentation.html#skimage.segmentation.slic)
- [scikit-learn — GroupShuffleSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html)
- [scikit-learn — RandomForestClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [NumPy — nanpercentile](https://numpy.org/doc/stable/reference/generated/numpy.nanpercentile.html)
