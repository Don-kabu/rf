# Feuille de route — données, entraînement et tests

## Mission

Préparer et évaluer l’expérience scientifique du TP dans la zone pilote de Mbanza‑Ngungu, Kongo Central, puis remettre un résultat lisible à l’application.

**Le périmètre de cette mission s’arrête aux données, au pipeline scientifique, à l’entraînement, à l’évaluation et aux artefacts de résultats.** Le client Vue.js, l’API FastAPI et les fichiers de lancement sont déjà préparés : ne pas les modifier. Le seul fichier de résultat à remettre à l’application est `backend/results/latest_result.json`.

Les cartes ESA sont des références/proxies, pas des relevés de terrain. Les chiffres ne devront donc jamais être présentés comme une précision terrain indépendante.

### En bref pour démarrer

1. Vérifier les données disponibles autour de Mbanza‑Ngungu et faire valider les classes.
2. Préparer les images et les labels, puis régler SLIC et les variables.
3. Entraîner et tester le Random Forest sur des blocs spatiaux séparés.
4. Remettre le rapport de tests et `backend/results/latest_result.json`.

L’interface et l’API sont déjà prêtes à recevoir ce fichier. Il n’y a pas d’application à créer ou à modifier.

## À ne pas faire

- Ne pas modifier `frontend/`, `backend/app/main.py`, `backend/app/schemas.py`, `backend/app/simulator.py` ni les lanceurs.
- Ne pas remplacer les résultats de démonstration par des résultats réels tant que les labels, le test spatial et les métriques ne sont pas contrôlés.
- Ne pas présenter les classes WorldCereal ou WorldCover comme si elles correspondaient automatiquement aux quatre classes du cahier.
- Ne pas mélanger des pixels du même bloc spatial entre apprentissage et test.
- Ne pas verser de grands rasters, clés, identifiants Earth Engine ou données personnelles dans le dépôt.

Si une primitive scientifique manque, ajouter le traitement dans `scripts/` ou `backend/app/pipeline/`, sans toucher à l’application, puis noter son usage et ses limites dans le rapport.

## Étape 1 — vérifier que le jeu d’étude est défendable

1. Lire [`DATASET.md`](DATASET.md) et examiner l’AOI `data/aoi/mbanza_ngungu_10km.geojson`.
2. Exécuter l’audit [`scripts/audit_mbanza_ngungu_gee.js`](../scripts/audit_mbanza_ngungu_gee.js) dans le Code Editor Earth Engine.
3. Noter la date d’audit, les produits, saisons, classes, pixels valides, confiances WorldCereal et observations Sentinel‑2 claires. Tester les seuils de confiance 60, 70 et 80 ; garder les effectifs obtenus pour chacun.
4. Vérifier que les étiquettes et les images couvrent les mêmes pixels et la même période. Si l’AOI est trop nuageuse ou les classes trop rares, réduire l’emprise/période avec justification ou arrêter et signaler le blocage.
5. Faire confirmer la nomenclature par l’encadrement avant l’apprentissage. Pour un TP simplifié, une cible binaire WorldCereal ou WorldCover peut être acceptable si elle est explicitement approuvée. Pour revendiquer les quatre classes du cahier, il faut des labels compatibles pour les quatre classes ; ne pas fabriquer les classes manquantes en renommant des catégories ESA.

**Porte de validation :** pas d’entraînement avant d’avoir documenté la source des labels, leur signification, les classes retenues, le NoData et le seuil de confiance.

## Étape 2 — préparer les entrées

Conserver les originaux dans `data/raw/` (répertoire local, ignoré par Git), les rasters alignés dans `data/processed/`, les scripts d’expérience dans `scripts/` et les tableaux/figures dans `reports/` ou `outputs/`.

Pour chaque couche, consigner source, URL/collection, licence, date/période, bandes, CRS, résolution, unités, NoData et transformation. Ne pas publier les gros fichiers bruts dans le dépôt.

Préparer :

- les images Sentinel‑2 L2A 2021 sur l’AOI, avec bandes et dates retenues ;
- le masque nuages/ombres SCL documenté et un masque NoData explicite ;
- le raster de référence et sa table de correspondance des classes ;
- une grille commune : CRS projeté en mètres, résolution et méthode de rééchantillonnage choisies et consignées ;
- un tableau de contrôle indiquant les pixels/dates valides avant et après masquage.

Le protocole de départ est dans [`PROTOCOLE_PIPELINE.md`](PROTOCOLE_PIPELINE.md), et les champs à remplir dans [`backend/examples/pipeline_config_template.json`](../backend/examples/pipeline_config_template.json). Les paramètres `null` ne sont pas des valeurs utilisables : les compléter après l’audit.

Formes attendues par les primitives déjà présentes : pile d’images `dates × hauteur × largeur × bandes`, segmentation `hauteur × largeur`, labels de référence `hauteur × largeur`, masque temporel `dates × hauteur × largeur`.

## Étape 3 — segmenter et attribuer les labels

1. Former une image multispectrale représentative et appliquer SLIC sur les pixels valides.
2. Essayer plusieurs nombres de segments et compacités raisonnables ; exporter une figure RGB avec contours SLIC et choisir après inspection visuelle. Les 500 segments/compacité 10 de la démo ne sont pas des paramètres scientifiques.
3. Extraire pour chaque superpixel les statistiques spectrales et temporelles retenues (au minimum médianes des bandes, NDVI et NDMI B8–B11 si les bandes sont présentes).
4. Affecter la classe de référence majoritaire dans chaque superpixel. Exclure NoData et les pixels sous le seuil de confiance retenu. Calculer la pureté du superpixel, essayer au moins 0,60 / 0,70 / 0,80, puis documenter le nombre et la proportion de segments conservés.
5. Contrôler visuellement une sélection de superpixels et la table variables/labels. Vérifier notamment qu’un code de classe `0` n’a pas été confondu avec NoData ; le code NoData doit être explicitement listé.

## Étape 4 — séparer spatialement, entraîner, évaluer

1. Créer des blocs géographiques projetés en mètres ; chaque bloc va entièrement dans une seule partition.
2. Viser environ 80 % des blocs pour apprentissage et 20 % pour test, avec graine 42 comme point de départ. Ajuster la taille des blocs à l’emprise et à l’échelle spatiale des superpixels.
3. Vérifier l’absence de blocs communs entre apprentissage et test, la présence des classes évaluables dans le test, et les effectifs de chaque classe. Ne pas régler les paramètres sur les résultats du test.
4. Entraîner un Random Forest de référence : 300 arbres, `max_features="sqrt"`, `class_weight="balanced"`, graine 42. Toute variante doit être consignée et comparée sur validation dans les seuls blocs d’apprentissage.
5. Calculer les prédictions uniquement sur les blocs de test : matrice de confusion (lignes = référence, colonnes = prédiction), accuracy, précision/rappel/F1 par classe et F1 macro. Rapporter les supports et les effectifs exclus.
6. Produire l’importance des variables du modèle. Elle décrit l’usage des variables par le modèle, pas une relation causale.
7. Générer un petit aperçu catégoriel pour l’interface et, si possible, conserver la carte catégorielle complète GeoTIFF dans `data/processed/`.

Les primitives array-based sont déjà dans `backend/app/pipeline/`; elles ne sont pas encore un lecteur GeoTIFF ni une orchestration complète. Le travail scientifique doit les relier aux rasters, ou utiliser des scripts reproductibles dédiés, sans modifier le client ou l’API.

## Étape 5 — tests et contrôles avant remise

- Refaire l’exécution depuis la configuration et les données documentées ; vérifier qu’une seconde exécution avec la même graine donne les mêmes partitions et le même résultat, dans les limites de la reproductibilité des bibliothèques.
- Vérifier les dimensions et valeurs finies des variables, l’absence de fuite spatiale, la cohérence classes/labels, la matrice de confusion et les métriques recalculées depuis cette matrice.
- Vérifier que le fichier JSON ci-dessous est accepté par le schéma de l’API : classes uniques, matrice carrée, métriques par classe concordantes, grille avec identifiants déclarés, `is_simulation: false`.
- Vérifier dans le client le chargement du résultat réel et le retour à la simulation. L’API démarre avec le lanceur habituel ; le bouton **Charger le dernier résultat réel** lit le fichier attendu.
- Garder dans le rapport les scripts/commandes exécutés, versions de bibliothèques, dates, choix de paramètres, partitions, métriques et limites des labels. Une erreur d’installation ou un label incompatible doit être signalé clairement, pas contourné en inventant un chiffre.

Commandes prévues depuis la racine du dépôt (dans l’environnement backend du projet) :

```powershell
cd backend
python -m pip install -r requirements-lock.txt
python -m pip install -r requirements-pipeline.txt
python -m pytest -q
cd ../frontend
npm install
npm test
npm run build
```

La suite Vue couvre les fonctions de métriques du client ; la suite Python couvre l’API et les primitives de pipeline. Compléter avec les contrôles géospatiaux listés plus haut dès que les scripts raster sont raccordés.

## Livrables à remettre

1. `backend/results/latest_result.json` — résumé final conforme au contrat de l’application.
2. Une note de résultats (Markdown ou PDF) contenant source/licence, nomenclature, paramètres, audit de couverture, contrôles de split, matrice et métriques, limites et commandes reproductibles.
3. Les scripts de traitement et de test nécessaires à la reproduction.
4. Les figures utiles pour la soutenance : composition d’image, contours SLIC, aperçu de classification et matrice de confusion.
5. La carte GeoTIFF complète si elle est produite, conservée séparément du petit JSON d’interface.

## Format exact du fichier remis à l’application

Le fichier doit être enregistré à `backend/results/latest_result.json`. Exemple de **forme** cohérente (valeurs fictives à ne pas citer comme résultat) :

```json
{
  "run_id": "mbanza-ngungu-2021-run-a-remplacer",
  "is_simulation": false,
  "data_source": "ESA_WorldCereal_2021_proxy",
  "notice": "Exemple de format uniquement ; remplacer par la source, la nomenclature et les limites réellement utilisées.",
  "configuration": {
    "area_name": "Mbanza-Ngungu, Kongo Central",
    "n_segments": 800,
    "n_dates": 9,
    "compactness": 10.0,
    "year": 2021,
    "aoi_file": "data/aoi/mbanza_ngungu_10km.geojson",
    "reference_source": "à renseigner",
    "class_mapping": {"1": "classe A", "2": "classe B"},
    "minimum_label_purity": 0.7,
    "spatial_block_size_m": 1000,
    "random_seed": 42,
    "n_estimators": 300,
    "test_partition": "held_out_spatial_blocks"
  },
  "classes": [
    {"id": 1, "name": "classe A", "color": "#427c58"},
    {"id": 2, "name": "classe B", "color": "#d79b28"}
  ],
  "confusion_matrix": [[8, 2], [1, 9]],
  "metrics": {"accuracy": 0.9, "macro_f1": 0.8496, "samples": 20, "correct": 18},
  "class_metrics": [
    {"class_id": 1, "class_name": "classe A", "support": 10, "predicted": 9, "precision": 0.8889, "recall": 0.8, "f1": 0.8421},
    {"class_id": 2, "class_name": "classe B", "support": 10, "predicted": 11, "precision": 0.8182, "recall": 0.9, "f1": 0.8571}
  ],
  "feature_importances": [
    {"feature": "B8_median", "importance": 0.6},
    {"feature": "NDVI_median", "importance": 0.4}
  ],
  "map_grid": [[1, 1, 2], [1, 2, 2], [1, 1, 2]]
}
```

`area_name`, `n_segments`, `n_dates` et `compactness` restent obligatoires pour compatibilité avec l’écran. Les autres champs de `configuration` servent à la traçabilité. `map_grid` est un aperçu à échantillonnage réduit, sans coordonnées géographiques ; il ne remplace pas la carte complète. Les identifiants de la grille doivent être ceux de `classes`. Les nombres de l’exemple sont mathématiquement cohérents mais inventés.

## Conditions de fin

- [ ] Nomenclature validée et limites des labels rédigées.
- [ ] Audit d’images et de labels enregistré ; grille, NoData et masques vérifiés.
- [ ] SLIC et attribution des classes contrôlés visuellement.
- [ ] Partition par blocs sans chevauchement ni fuite ; test indépendant du réglage.
- [ ] Random Forest entraîné et métriques calculées exclusivement sur test.
- [ ] Scripts et résultats reproductibles remis.
- [ ] `backend/results/latest_result.json` chargé dans l’interface sans modifier l’application.
