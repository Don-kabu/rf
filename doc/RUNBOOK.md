# Lancement local et décisions à venir

## Démarrage Windows en double-clic

À la racine du projet, lancer `LANCER_TP_AGRISLIC.cmd`. Il prépare les dépendances manquantes, ouvre l’API et le client dans deux fenêtres, puis ouvre le navigateur. Consulter [LANCEMENT_RAPIDE.md](LANCEMENT_RAPIDE.md) pour les prérequis et les erreurs courantes. La version actuelle affiche des résultats synthétiques.

## Prérequis

- Python 3.10 ou plus récent pour l’API ;
- Node.js compatible avec la version de Vite définie dans `frontend/package.json` ;
- accès réseau la première fois pour récupérer les dépendances Python/Node.

## Démarrer le serveur FastAPI (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

L’API est sur `http://127.0.0.1:8000`; sa documentation interactive est sur `http://127.0.0.1:8000/docs`.

## Démarrer le client Vue.js (dans un second terminal)

```powershell
cd frontend
npm install
npm run dev
```

Vite affiche l’adresse locale, normalement `http://localhost:5173`.

## Lancer les tests API

Dans un terminal activant l’environnement Python du backend :

```powershell
cd backend
pytest -q
```

## Construire le client

```powershell
cd frontend
npm run build
```

## Afficher le résultat scientifique après entraînement

1. Suivre la [feuille de route données/entraînement/tests](FEUILLE_ROUTE_DONNEES_ENTRAINEMENT_TESTS.md) : elle borne le travail scientifique et le format de résultat attendu.
2. Après audit des labels, préparation des images, entraînement et test, enregistrer le résumé dans `backend/results/latest_result.json`.
3. Relancer l’API si nécessaire, ouvrir le client, puis cliquer sur **Charger le dernier résultat réel**. L’application valide les classes, les comptes et les métriques et signale un fichier manquant ou incohérent.
4. Le bouton **Revenir à la démonstration** recharge le jeu synthétique. Ne présenter les mesures que selon la source indiquée dans le résultat et les limites des labels.

Les primitives array-based de `backend/app/pipeline/` peuvent être préparées avant ces étapes, mais elles attendent des tableaux déjà harmonisés. Le prototype ne lit pas encore les GeoTIFF. Pour installer les dépendances optionnelles de ces modules dans l’environnement backend :

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements-pipeline.txt
```

Cette installation n’est pas nécessaire pour le lanceur de démonstration Vue/FastAPI.

Le client Vue et l’API FastAPI restent des supports de démonstration. Il n’est pas nécessaire d’ajouter une authentification, un déploiement public, une base de données ou un système de traitements en arrière-plan pour défendre ce TP.

## Limites actuelles

La démo ne téléverse pas de fichiers, ne traite pas de GeoTIFF, ne persiste pas les runs et ne fournit pas de résultats terrain. Ces éléments restent des travaux V1/V2 listés dans le backlog.

## Configurer l’adresse de l’API (facultatif)

Le client utilise `http://127.0.0.1:8000` par défaut. Pour la remplacer, copier `frontend/.env.example` vers `frontend/.env.local`, modifier `VITE_API_BASE_URL`, puis redémarrer Vite.

