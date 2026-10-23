# Documentation du projet

**AgriSLIC — classification agricole SLIC + Random Forest**

Ce dossier est la source de référence pour la première version du projet. Il couvre le cahier des charges, l’architecture Vue.js/FastAPI, le backlog, le contrat API et la simulation de démonstration.

## Documents

- [Spécification fonctionnelle et critères d’acceptation](SPECIFICATION.md)
- [Architecture et décisions techniques](ARCHITECTURE.md)
- [Backlog priorisé](BACKLOG.md)
- [Choix et vérifications des données pour le Kongo Central](DATASET.md)
- [Feuille de route pour les données, les labels, l'entraînement et les tests](FEUILLE_ROUTE_DONNEES_ENTRAINEMENT_TESTS.md)
- [Protocole provisoire du pipeline scientifique](PROTOCOLE_PIPELINE.md)
- [Contrat de l’API FastAPI](API.md)
- [Tests et simulation de résultats](TESTS_SIMULATION.md)
- [Guide de soutenance](DEFENSE.md)
- [Lancement rapide Windows en double-clic](LANCEMENT_RAPIDE.md)
- [Lancement local et prochaines décisions](RUNBOOK.md)

## État actuel

Le dépôt contient un prototype local avec une interface Vue.js, une API FastAPI et un jeu de résultats **synthétiques** pour démontrer l’affichage. L’application sait aussi charger un résultat réel conforme au contrat depuis `backend/results/latest_result.json`, mais aucun raster Sentinel‑2 réel, label terrain ni entraînement réel n’est inclus à ce stade. Les mesures affichées par défaut ne sont donc pas des résultats scientifiques.

Le [protocole provisoire](PROTOCOLE_PIPELINE.md) et le [modèle de configuration](../backend/examples/pipeline_config_template.json) cadrent les traitements. Les primitives array-based sont écrites, mais elles ne chargent pas encore de rasters et n’ont pas été exécutées sur l’emprise de Mbanza‑Ngungu. Les paramètres liés à la résolution, aux labels et à la taille des superpixels restent à confirmer.

La zone pilote documentaire est fixée autour de Mbanza‑Ngungu, Kongo Central. Son emprise GeoJSON est dans `data/aoi/mbanza_ngungu_10km.geojson` ; l’identification de l’AEZ WorldCereal 4010 et les vérifications de pixels à terminer sont décrites dans [DATASET.md](DATASET.md). Ce document précise aussi l’écart entre les quatre classes du cahier et les catégories proxy des cartes ESA. La feuille de route ci-dessus délimite le travail scientifique à remettre sans modifier l’application.

## Documents sources

Le cadrage reprend le sujet « Classification de parcelles agricoles par superpixels SLIC — Variante B » et les deux documents théoriques remis au début du travail. Les décisions pratiques prises pour le prototype sont détaillées dans `SPECIFICATION.md` et `ARCHITECTURE.md`.
