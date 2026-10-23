# Tests et simulation de résultats

## 1. Limite de la simulation V0

La simulation utilise une matrice de confusion fixée dans le code pour valider le flux API → client et l’affichage. Elle ne lit aucune image, n’exécute ni SLIC ni Random Forest, et ses chiffres ne doivent pas apparaître comme des performances expérimentales dans le rapport scientifique.

Le serveur doit retourner `is_simulation: true`, `data_source: synthetic_demo` et un message visible. La carte et l’importance des variables sont des illustrations, pas une géographie ou une explication apprise par le modèle.

## 2. Exemple numérique contrôlé

Ordre des classes illustratives V0 : Maïs, Arboriculture, Prairies/savane, Sols nus/bâti. Ces noms servent uniquement à rendre la simulation lisible et ne fixent pas la nomenclature du pipeline réel ; celle-ci dépendra des produits WorldCereal/WorldCover disponibles pour le Kongo Central. Lignes = vraie classe synthétique ; colonnes = classe prédite synthétique.

| Vrai  Prédit | Maïs | Arboriculture | Prairies/savane | Sols nus/bâti | Support |
|---|---:|---:|---:|---:|---:|
| Maïs | 45 | 6 | 4 | 1 | 56 |
| Arboriculture | 5 | 33 | 4 | 1 | 43 |
| Prairies/savane | 6 | 5 | 37 | 2 | 50 |
| Sols nus/bâti | 1 | 1 | 2 | 48 | 52 |
| Total | 57 prédits | 45 prédits | 47 prédits | 52 prédits | 201 |

La diagonale contient 163 classifications correctes sur 201, soit une accuracy d’environ **81,09 %**. La F1 macro est d’environ **80,81 %**. Ces chiffres décrivent uniquement cette matrice synthétique.

## 3. Tests du backend

- endpoint de santé : statut 200 et service attendu ;
- endpoint demo : marqueur synthétique présent ;
- simulation : même réponse pour la même requête ;
- cohérence : taille de matrice égale au nombre de classes, somme égale à `samples`, métriques recalculables ;
- validation : valeurs invalides rejetées avec statut 422 ;
- cas réseau côté client : message d’erreur visible si l’API n’est pas joignable.

Commande prévue depuis `backend/` : `pytest -q`.

## 4. Vérification du futur modèle réel

Les tests array-based de `backend/tests/test_pipeline_primitives.py` utilisent uniquement de petits tableaux synthétiques : ils vérifient les indices, la normalisation, l’agrégation, la majorité/pureté et, si les dépendances optionnelles sont installées, SLIC, le split par groupes et le classifieur. Ces fixtures vérifient la logique du code ; elles ne valident pas l’emprise ni les choix du modèle sur Kongo Central.

Les tests de simulation et les petits tests array-based ne valident pas toute la chaîne géospatiale. Après ajout de la lecture de raster et du raccordement, prévoir en plus :

- contrôles de dimensions/CRS/transformée et masques ;
- calcul vérifié de NDVI/NDMI et traitement des dénominateurs nuls ;
- couverture complète des identifiants SLIC valides dans la table ;
- contrôle des labels/pureté et exclusion de segments invalides ;
- assertion qu’aucun identifiant de groupe ne se retrouve dans plusieurs partitions ;
- recalcul indépendant des métriques depuis les prédictions du test ;
- vérification de projection, transformée, NoData et codes de classes à l’export raster.

Les exemples de test de pipeline devront être petits, synthétiques et séparés du jeu de données scientifique.

## Fixture de résultat

Le JSON complet [simulation_result_demo.json](../backend/examples/simulation_result_demo.json) est un exemple exporté par le simulateur et comporte le marqueur `is_simulation: true`. Il sert à vérifier l’affichage et la structure de réponse.
