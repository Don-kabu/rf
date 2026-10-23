# AgriSLIC — prototype Vue.js + FastAPI

Projet pédagogique pour le sujet « Classification de parcelles agricoles par superpixels SLIC — Variante B ». Le dépôt contient un tableau de bord Vue.js, une API FastAPI et une simulation synthétique afin de montrer le parcours et tester les métriques.

> **Important :** la démonstration n’utilise pas de données Sentinel‑2 et n’entraîne aucun modèle. Les scores, importances et cartes sont fictifs. Les fonctions de calcul array-based SLIC, variables, labels, séparation spatiale et Random Forest sont dans `backend/app/pipeline/`, mais elles ne chargent pas encore de rasters et n’ont pas été exécutées sur Mbanza‑Ngungu.

Le client comprend aussi un résumé visuel des trois étapes SLIC → caractéristiques → Random Forest, pour accompagner l’explication orale du TP. Il affiche la simulation par défaut et peut charger le dernier résultat réel depuis `backend/results/latest_result.json` via le bouton **Charger le dernier résultat réel**. Ce fichier est le seul point de remise à l’application pour le travail scientifique ; voir le contrat [`doc/API.md`](doc/API.md).

## Documentation

Commencer par [`doc/README.md`](doc/README.md), puis consulter la spécification, l’architecture, le backlog, l’API, les tests et le runbook dans `doc/`. Pour partager le travail restant à un ami sans lui confier l’application, utiliser la [feuille de route données, entraînement et tests](doc/FEUILLE_ROUTE_DONNEES_ENTRAINEMENT_TESTS.md).

Zone pilote retenue : Mbanza‑Ngungu, Kongo Central. Le polygone d’étude d’environ 10 × 10 km est dans [`data/aoi/mbanza_ngungu_10km.geojson`](data/aoi/mbanza_ngungu_10km.geojson) ; voir [`doc/DATASET.md`](doc/DATASET.md) pour les sources et limites des labels.

Le cahier du sujet demande quatre classes. Les produits ESA candidats ne fournissent pas exactement ces quatre étiquettes : l’audit des données devra être suivi d’un choix de labels ou de proxies compatible avec le TP. Le tableau de bord actuel garde les quatre classes uniquement dans une simulation synthétique.

## Lancer localement

Sur Windows, le moyen le plus simple est de double-cliquer sur [`LANCER_TP_AGRISLIC.cmd`](LANCER_TP_AGRISLIC.cmd). Le [guide de lancement rapide](doc/LANCEMENT_RAPIDE.md) décrit les prérequis, les adresses et les problèmes fréquents. Ce lanceur démarre la simulation actuelle ; il ne lance pas encore un vrai entraînement SLIC/Random Forest.

### API

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API : <http://127.0.0.1:8000/api/v1/health>  
Documentation interactive : <http://127.0.0.1:8000/docs>

### Client

Dans un second terminal :

```powershell
cd frontend
npm install
npm run dev
```

Vite affiche l’URL locale, par défaut <http://localhost:5173>.

### Vérifier

```powershell
cd backend
pytest -q
```

Pour tester les fonctions de présentation sans navigateur :

```powershell
cd frontend
npm test
```

Construire le client : `npm run build` depuis `frontend/`.

Résultat synthétique de démonstration : [`backend/examples/simulation_result_demo.json`](backend/examples/simulation_result_demo.json). Il ne s’agit pas d’un résultat scientifique.

