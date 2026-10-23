# Lancement rapide du TP AgriSLIC

## Démarrage en double-clic

À la racine du dossier du projet, double-cliquer sur `LANCER_TP_AGRISLIC.cmd`.

Au premier démarrage, le lanceur crée l’environnement Python local et installe les dépendances FastAPI et Vue.js si elles manquent. Une connexion Internet est alors nécessaire. Il ouvre ensuite deux fenêtres de terminal : une pour l’API FastAPI, une pour le client Vue. Il ouvre également le client dans le navigateur. Après qu’un résultat validé a été remis dans `backend/results/latest_result.json`, le bouton **Charger le dernier résultat réel** permet de l’afficher.

- **Client :** <http://localhost:5173>
- **Documentation de l’API :** <http://127.0.0.1:8000/docs>
- **État de l’API :** <http://127.0.0.1:8000/api/v1/health>

Laisser les deux fenêtres de terminal ouvertes pendant la démonstration. Les fermer arrête les serveurs.

## Prérequis

- Windows 10 ou 11 ;
- Python 3.10 ou plus récent ;
- Node.js 22.12 ou plus récent, avec npm ;
- accès Internet au premier lancement pour installer les dépendances si elles ne sont pas déjà présentes.

Le lanceur vérifie Node.js et crée automatiquement `backend/.venv`. Il n’installe pas Python ni Node.js eux-mêmes.

## Ce que le lancement démarre actuellement

Le client Vue affiche d’abord une **simulation synthétique** : matrice de confusion, métriques et grille illustrative. Si le fichier `backend/results/latest_result.json` a été fourni après le travail scientifique, le bouton **Charger le dernier résultat réel** l’affiche. Le lanceur lui-même ne charge pas les images Sentinel‑2, n’exécute pas SLIC et ne lance pas d’entraînement.

## Problèmes fréquents

- **Python introuvable :** installer Python 3.10+ et relancer le fichier. Avec le lanceur `py`, cocher l’ajout de Python au PATH lors de l’installation.
- **Node/npm introuvable ou trop ancien :** installer Node.js 22.12+ puis rouvrir le lanceur.
- **Échec d’installation des dépendances :** vérifier la connexion Internet, puis relancer ; les installations déjà effectuées seront réutilisées.
- **Le navigateur affiche une erreur de connexion :** vérifier que les deux fenêtres de terminal sont encore ouvertes et que l’API utilise le port 8000.
- **Le port 8000 ou 5173 est déjà occupé :** fermer l’autre application qui l’utilise avant de relancer le TP.

## Lancement manuel

Les commandes séparées et l’utilisation de l’API sont décrites dans [`RUNBOOK.md`](RUNBOOK.md). Le lanceur appelle les scripts `scripts/run_api.cmd` et `scripts/run_vue.cmd`.
