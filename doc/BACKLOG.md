# Plan de travail du TP

Objectif : terminer un TP reproductible, compréhensible et présentable. Le client Vue/FastAPI est un démonstrateur local ; on ne construit pas une plateforme de production. Les tâches liées aux rasters et à l’entraînement attendent la vérification des données.

## Epic A — socle applicatif

- [x] A1. Créer la structure frontend/backend et les instructions locales.
- [x] A2. Exposer une API FastAPI avec santé, schémas et documentation OpenAPI.
- [x] A3. Créer un client Vue.js connecté à l’API.
- [x] A4. Limiter CORS aux origines locales de développement.
- [x] A5. Garder des avertissements visibles : résultats synthétiques, pas d’images ni de modèle entraîné.
- [x] A6. Ajouter le chargement du dernier résultat réel depuis un JSON validé, sans téléversement ni modification du simulateur.

## Epic B — simulation démonstrative

- [x] B1. Définir une matrice de confusion synthétique pour quatre classes.
- [x] B2. Calculer accuracy, précision, rappel, F1 et F1 macro depuis les comptes.
- [x] B3. Générer une grille de carte illustrative et des importances fictives.
- [x] B4. Afficher un avertissement visible pour empêcher toute confusion avec un entraînement réel.
- [x] B5. Tester les réponses et la cohérence mathématique de l’API.

## Travaux réalisables avant la disponibilité des rasters

- [x] Formaliser les formules NDVI/NDMI, la majorité/pureté, le découpage spatial et les métriques attendues (`doc/PROTOCOLE_PIPELINE.md`).
- [x] Créer un modèle de configuration de départ avec les paramètres dépendants des rasters laissés à renseigner (`backend/examples/pipeline_config_template.json`).
- [x] Extraire le calcul générique des métriques pour le réutiliser sur les prédictions réelles (`backend/app/metrics.py`).
- [x] Écrire les primitives calculatoires array-based SLIC, variables, labels majoritaires, split spatial et Random Forest (`backend/app/pipeline/`). Elles ne sont pas encore raccordées à une lecture de rasters ni exécutées sur le terrain d’étude.
- [x] Ajouter des tests sur petits tableaux synthétiques, avec SLIC/scikit-learn optionnels (`backend/tests/test_pipeline_primitives.py`).
- [x] Valider la cohérence des matrices, effectifs et métriques dans le schéma de réponse FastAPI.
- [x] Faire associer les couleurs de la vue par identifiant de classe plutôt que par position supposée.

## Epic C — données réelles et pipeline

- [~] C1. Zone pilote définie : carré de cadrage d’environ 10 × 10 km autour de Mbanza‑Ngungu, Kongo Central (AEZ 4010) ; polygone conservé dans `data/aoi/`.
- [ ] C2. Lancer l’audit Earth Engine pour relever les pixels valides, les confiances WorldCereal et les observations Sentinel‑2 claires ; le script est dans `scripts/audit_mbanza_ngungu_gee.js`.
- [ ] C3. Résoudre l’écart entre les quatre classes du cahier et les classes proxy disponibles : WorldCereal est binaire par produit ; WorldCover fournit des catégories générales. Confirmer la nomenclature du TP avant l’apprentissage.
- [ ] C4. Préparer les bandes, dates, CRS, NoData et masques pour le petit jeu d’étude.
- [ ] C5. Harmoniser les rasters sur une grille commune.
- [~] C6. Fonction SLIC array-based écrite ; appliquer à l’image réelle, afficher les contours et régler nombre de segments/compacité.
- [~] C7. Extraction array-based écrite ; valider les statistiques par superpixel sur les bandes réelles et vérifier le masque temporel.
- [~] C8. Règle de majorité/pureté codée ; exécuter avec la source de référence retenue et contrôler les segments écartés.
- [~] C9. Attribution des groupes spatiaux et split codés ; choisir la taille des blocs après harmonisation puis vérifier les classes par partition.
- [~] C10. Fonction Random Forest écrite ; entraîner et régler seulement après formation des tables de variables/labels.
- [~] C11. Calcul générique et format d’évaluation écrits ; calculer les scores sur les prédictions du test réel.
- [ ] C12. Reprojeter les prédictions sur la carte, conserver une légende et préparer les figures de soutenance.
- [ ] C13. Déposer le résumé validé dans `backend/results/latest_result.json` ; le client peut l’afficher sans changement de code applicatif.

La [feuille de route données/entraînement/tests](FEUILLE_ROUTE_DONNEES_ENTRAINEMENT_TESTS.md) sert de remise à une personne qui travaille uniquement sur le jeu de données, les labels, les expériences, les tests et les artefacts scientifiques. Elle interdit les modifications du client Vue, de l’API et des lanceurs.

## Hors périmètre du TP

- Déploiement public, authentification et comptes utilisateurs.
- Téléversement générique de grands jeux de données et exécution en arrière-plan.
- Historique persistant, gestion des versions de modèles et automatisation de rapports.
- Promesse de précision terrain sans relevés locaux indépendants.

## Définition de terminé

Le TP est présentable quand la source et la nomenclature sont expliquées, le pipeline SLIC → variables → Random Forest est exécuté sur les données effectivement disponibles, les métriques sont recalculables et les limites des labels proxy sont exposées. Avant l’arrivée des données, la simulation reste marquée comme fictive ; elle ne valide pas le pipeline scientifique.
