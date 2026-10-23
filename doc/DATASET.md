# Données pilotes — Kongo Central

## Décision de cadrage

- **Province :** Kongo Central, RDC.
- **Emprise pilote retenue :** carré d’environ 10 × 10 km centré sur Mbanza‑Ngungu, défini dans [`data/aoi/mbanza_ngungu_10km.geojson`](../data/aoi/mbanza_ngungu_10km.geojson). Ce carré peut couvrir des espaces périurbains et ruraux ; sa part cultivée doit être contrôlée sur les rasters avant l’apprentissage.
- **Période :** 2021 pour commencer, afin de faire correspondre les images Sentinel‑2 et les produits cartographiques ESA disponibles.
- **Images :** Sentinel‑2 L2A harmonisé, collection `COPERNICUS/S2_SR_HARMONIZED` dans Earth Engine.
- **Labels à vérifier en premier :** ESA WorldCereal 2021, collection `ESA/WorldCereal/2021/MODELS/v100`.
- **Solution de repli :** ESA WorldCover 2021, produit mondial 10 m `ESA/WorldCover/v200`, classe 40 « cropland ».

Le centre de l’emprise utilise les coordonnées de Mbanza‑Ngungu publiées par le [GEOnet Names Server de la NGA](https://geonames.nga.mil/geon-ags/rest/services/RESEARCH/GIS_OUTPUT/MapServer/0/2589215/htmlPopup?f=html) : longitude 14.858382° E, latitude 5.258369° S. Le carré est une enveloppe d’étude reproductible, pas une limite administrative ou cadastrale. Le choix de la localité est motivé par l’activité agricole documentée dans le territoire et par des programmes agricoles qui y ciblent notamment manioc, maïs et arachide ([ACP](https://acp.cd/province/kongo-central-presentation-dun-plan-de-la-production-agricole-a-matadi/)).

## Jeu principal à vérifier : ESA WorldCereal 2021

La première vérification spatiale est faite à partir du GeoJSON officiel des zones agro-écologiques fourni dans le [dépôt ESA WorldCereal sur Zenodo](https://zenodo.org/records/7875105) : le point de référence et les quatre coins du carré pilote sont dans l’**AEZ 4010**. La fiche de cette AEZ définit la saison `tc-maize-main` (jours de l’année 43 à 214) et la saison `tc-annual` (291 à 290, à cheval sur deux années). Le [catalogue Earth Engine WorldCereal](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCereal_2021_MODELS_v100) confirme les produits par AEZ, saison, classe et bande de confiance.

Cela confirme la couverture **de l’emprise par l’AEZ et du calendrier saisonnier** ; il reste à extraire les pixels de classification/confiance et vérifier qu’ils sont valides et assez nombreux dans le carré. L’ordre de travail est donc : vérifier le produit `temporarycrops` annuel, puis le produit `maize` de saison principale. Le deuxième permet une expérience maïs si suffisamment de pixels et de confiance sont présents. Les produits 2021 sont également consultables dans le [visualiseur WorldCereal](https://vdm.esa-worldcereal.org/) et téléchargeables par zone.

### Procédure reproductible d’audit

Le script prêt à lancer est [`scripts/audit_mbanza_ngungu_gee.js`](../scripts/audit_mbanza_ngungu_gee.js). Il interroge directement les collections publiques Earth Engine : il n’est pas nécessaire de télécharger toute la carte mondiale.

1. Se connecter avec un compte autorisé à [Google Earth Engine Code Editor](https://code.earthengine.google.com/). Si l’accès n’est pas encore activé, suivre l’inscription proposée par Earth Engine.
2. Ouvrir le script local, copier son contenu dans l’éditeur, puis cliquer sur **Run**.
3. Dans la console, relever le nombre d’images WorldCereal, les classes trouvées (`0` et `100`), le nombre de pixels valides, la part de chaque classe, la moyenne et les percentiles de confiance.
4. Comparer la confiance avec plusieurs seuils (60, 70 et 80). Le seuil initial de 70 dans le script est seulement un repère de diagnostic, pas une règle officielle ESA. Choisir le seuil avant l’apprentissage et documenter l’effet sur le nombre de pixels conservés.
5. Pour Sentinel‑2, relever le nombre de scènes intersectant l’emprise et le pourcentage de pixels ayant au moins une puis au moins trois observations claires après le masque SCL. Afficher les couches de composition RGB et de nombre d’observations pour repérer visuellement les trous.
6. Vérifier séparément la fenêtre annuelle (17 octobre 2020–17 octobre 2021) et la saison maïs principale (12 février–2 août 2021). Le script calcule les deux audits Sentinel‑2 ; pour examiner les étiquettes maïs, remplacer en haut `tc-annual`/`temporarycrops` par `tc-maize-main`/`maize`.

Une emprise ne passe à l’entraînement que si les étiquettes ont une couverture exploitable, que les deux classes disposent d’assez de pixels après filtrage de confiance et que les observations claires couvrent les zones où se trouvent ces étiquettes. Le nombre de scènes sur la fiche d’une image ne suffit pas : ce sont les mesures de pixels dans l’AOI qui comptent. Les résultats chiffrés doivent être copiés dans le rapport avec la date de l’audit, les filtres et le seuil choisi.

Le masque utilise la bande SCL (classification des scènes) de Sentinel‑2. Elle est fournie à 20 m dans le catalogue, alors que B2/B3/B4/B8 sont à 10 m ; les mesures de couverture servent à décider si la zone et la période sont utilisables. La résolution commune et le rééchantillonnage des bandes devront être fixés explicitement dans le pipeline de production.

La cible de départ est **culture temporaire / hors culture temporaire**. Pour le produit saisonnier maïs, l’expérience complémentaire est **maïs / non-maïs dans la zone masquée comme cultures temporaires** ; les pixels hors du masque agricole ne doivent pas être assimilés à des non-maïs. Les produits sont binaires et accompagnés d’une confiance de 0 à 100. Les pixels manquants ou de confiance insuffisante sont écartés selon un seuil fixé avant l’entraînement. Les saisons étant définies par AEZ, les résultats d’autres zones ne doivent pas être supposés comparables.

Page officielle et possibilités de téléchargement par zone : [ESA WorldCereal — Global Maps](https://esa-worldcereal.org/en/products/global-maps). Le produit peut également être interrogé dans Earth Engine sans télécharger le monde entier.

## Compatibilité avec les quatre classes du sujet

Le cahier fourni avec le sujet cite **maïs, arboriculture, prairies/savane et sols nus/surfaces bâties**. Les cartes ESA retenues sont faciles à consulter pour le TP, mais elles ne donnent pas directement ces quatre classes avec cette nomenclature :

| Classe demandée | Ce que les cartes candidates peuvent fournir | Limite à présenter |
|---|---|---|
| Maïs | Le produit WorldCereal `maize` peut servir de proxy saisonnier après audit. | Il est binaire et ne fournit pas les quatre classes ensemble. |
| Arboriculture | WorldCover `tree cover` peut repérer une couverture arborée. | « Couverture arborée » n’identifie pas spécifiquement les vergers ou l’arboriculture. |
| Prairies / savane | WorldCover `grassland` est un proxy possible. | La catégorie est générale et peut comprendre des pâturages et d’autres couverts herbacés. |
| Sols nus / bâti | WorldCover distingue `bare / sparse vegetation` et `built-up`. | Il faut décider si les deux sont regroupés dans une classe ou évalués séparément. |

WorldCereal fournit une classification binaire par produit (valeurs 0/100) avec confiance ; il ne faut donc pas interpréter son produit annuel `temporarycrops` comme une vérité à quatre classes. WorldCover 2021 fournit onze classes générales, dont tree cover (10), grassland (30), cropland (40), built-up (50) et bare/sparse vegetation (60) ; la classe cropland ne distingue pas le maïs des autres cultures. Voir les [catalogues officiels WorldCereal](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCereal_2021_MODELS_v100) et [WorldCover](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200).

**Décision de TP :** l’interface de démonstration garde les quatre classes du cahier et des résultats explicitement synthétiques. Pour le traitement réel, l’audit des pixels vérifiera la quantité et la qualité des données, mais pas la justesse de leur nomenclature. Il faudra ensuite soit obtenir des étiquettes locales compatibles avec les quatre classes, soit convenir avec l’encadrement d’une nomenclature simplifiée correspondant aux cartes disponibles. La carte de référence choisie devra être nommée comme un proxy, pas comme une vérité terrain.

## Images : Sentinel‑2

Utiliser les images Sentinel‑2 L2A harmonisées de 2021, filtrées sur l’emprise et la période, puis masquer nuages et ombres. Les bandes envisagées sont B2, B3, B4, B8, B11 et B12 ; les bandes SWIR B11/B12 sont à 20 m, ce qui implique une grille de travail commune à définir. La collection Earth Engine `COPERNICUS/S2_SR_HARMONIZED` est décrite dans le [catalogue officiel Sentinel‑2](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED).

Prévoir une composition temporelle ou plusieurs dates de la saison étudiée. Ne pas sélectionner une scène seulement parce qu’elle est sans nuage sur la fiche produit : vérifier les pixels valides dans l’emprise.

## Repli : ESA WorldCover 2021

Si WorldCereal ne fournit pas de produit utile pour la zone ou la saison, utiliser WorldCover 2021 à 10 m. Définir la classe 40 comme `cultivé` et les autres classes valides retenues comme `autre couverture`, en excluant NoData. Cette option ne distingue pas le maïs du manioc, du riz ou des autres cultures. Voir [ESA WorldCover — accès aux données](https://esa-worldcover.org/en/data-access) et son [entrée Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200).

## Limites à dire pendant la soutenance

1. Les produits WorldCereal et WorldCover sont des cartes produites à partir d’observations satellitaires, pas des relevés terrain propres à chaque parcelle. Une évaluation contre ces produits mesure l’accord avec la carte de référence, pas une exactitude indépendante au sol.
2. WorldCereal 2021 définit une saison maïs dans l’AEZ 4010 ; les pixels de classification et de confiance doivent encore être extraits et contrôlés dans l’emprise. Ce produit n’est pas une nomenclature exhaustive des cultures du Kongo Central.
3. WorldCover permet seulement une cible de couverture agricole générale (`cultivé` / `autre couverture`).
4. SLIC produit des superpixels d’analyse qui ne coïncident pas nécessairement avec les vraies limites de parcelles.
5. Pour revendiquer une précision de classification agricole, il faudra des observations de terrain géoréférencées, datées et indépendantes, ou des polygones agricoles locaux validés.

## Vérifications avant de lancer le vrai pipeline

- [x] Définir et conserver le carré pilote d’environ 10 × 10 km ; le centre et les quatre coins sont couverts par l’AEZ 4010.
- [ ] Lancer `scripts/audit_mbanza_ngungu_gee.js` dans Earth Engine et enregistrer les résultats de l’audit.
- [ ] Vérifier avec l’encadrement si le TP exige exactement les quatre classes du cahier ou accepte une nomenclature adaptée aux labels disponibles.
- [ ] Extraire le produit WorldCereal `temporarycrops` sur cette emprise ; calculer les pixels valides, la part des deux classes et la confiance.
- [ ] Extraire le produit WorldCereal `maize` de la saison principale (AEZ 4010, DOY 43–214), puis vérifier les pixels valides et la confiance.
- [ ] Inspecter les images Sentinel‑2 2021, le taux de nuages et les pixels valides après masque.
- [ ] Choisir une résolution commune ; conserver les bandes natives ou documenter le rééchantillonnage.
- [ ] Fixer les classes, le seuil de confiance/pureté, la nomenclature et la stratégie de blocs spatiaux.
- [ ] Télécharger uniquement les sous-zones et couches nécessaires et enregistrer sources, licences, dates et paramètres.
