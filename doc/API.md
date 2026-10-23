# Contrat API V0

Base locale par défaut : `http://127.0.0.1:8000`  
Documentation interactive : `/docs`  
Préfixe : `/api/v1`

## GET `/api/v1/health`

Réponse 200 :

```json
{"status":"ok","service":"agrislic-api","version":"0.1.0"}
```

## GET `/api/v1/demo`

Retourne le scénario de démonstration. La réponse indique `is_simulation: true` et `data_source: "synthetic_demo"`.

## GET `/api/v1/results/latest`

Charge `backend/results/latest_result.json` et valide sa cohérence avant de le renvoyer. Le client Vue appelle cette route avec le bouton **Charger le dernier résultat réel**. Le fichier n’existe pas avant que le travail scientifique le fournisse ; dans ce cas la route répond `404` avec une explication lisible.

Le résultat doit indiquer `is_simulation: false`, une source dans `data_source`, une configuration avec `area_name`, `n_segments`, `n_dates` et `compactness`, ainsi que les classes, la matrice, les métriques, les importances et un aperçu cartographique. La configuration accepte des métadonnées supplémentaires pour conserver les paramètres d’expérience. L’aperçu est limité à 80 × 80 cellules et doit utiliser uniquement les identifiants déclarés dans `classes`. Les rasters complets ne sont pas intégrés à la réponse JSON.

Le format complet et un exemple de validation (avec chiffres fictifs explicitement signalés) figurent dans [`FEUILLE_ROUTE_DONNEES_ENTRAINEMENT_TESTS.md`](FEUILLE_ROUTE_DONNEES_ENTRAINEMENT_TESTS.md).

## POST `/api/v1/simulations`

Lance une simulation pédagogique déterministe. Ce endpoint ne lance pas de Random Forest et n’ingère pas de raster réel.

Requête :

```json
{
  "area_name": "Zone de démonstration",
  "n_segments": 500,
  "n_dates": 12,
  "compactness": 10.0
}
```

Contraintes : `area_name` non vide (maximum 120 caractères), `n_segments` entre 10 et 100000, `n_dates` entre 1 et 60, `compactness` strictement positive et au plus 1000.

Réponse abrégée (les classes, métriques par classe, importances et grille complètes sont présentes dans la réponse réelle) :

```json
{
  "run_id": "demo-static-v1",
  "is_simulation": true,
  "data_source": "synthetic_demo",
  "notice": "Résultats synthétiques pour démonstration ; aucune image Sentinel-2 n'a été traitée et aucun modèle n'a été entraîné.",
  "configuration": {
    "area_name": "Zone de démonstration",
    "n_segments": 500,
    "n_dates": 12,
    "compactness": 10.0
  },
  "confusion_matrix": [[45, 6, 4, 1], [5, 33, 4, 1], [6, 5, 37, 2], [1, 1, 2, 48]],
  "metrics": {
    "accuracy": 0.8109,
    "macro_f1": 0.8081,
    "samples": 201,
    "correct": 163
  }
}
```

Les scores sont calculés depuis la matrice. Les valeurs `0.8109` et `0.8081` sont arrondies et décrivent uniquement la matrice synthétique.

## Cohérence des résultats

Le schéma de réponse vérifie que la matrice est carrée et suit l’ordre des classes, que les identifiants de classe sont uniques, que les effectifs et métriques par classe correspondent aux lignes/colonnes, et que l’accuracy, le F1 macro et les comptes globaux peuvent être recalculés depuis la matrice. La grille cartographique ne peut référencer que des identifiants déclarés. Ces règles protègent aussi les futures réponses du pipeline réel contre des résultats internes incohérents.

## Erreurs

- `422` : paramètres hors limites ou JSON mal formé ; FastAPI décrit les champs invalides.
- `404` sur `/api/v1/results/latest` : aucun artefact réel n’a encore été fourni.
- `422` sur `/api/v1/results/latest` : artefact invalide, incohérent ou marqué comme simulation.
- `500` : erreur interne inattendue ; aucun traceback n’est transmis au client.
- indisponibilité réseau : le client affiche un message et propose de relancer.

## Limites

La route de résultat lit un fichier local préparé par le workflow scientifique ; elle ne télécharge pas de données, ne lance pas l’entraînement et ne sert pas de gestionnaire de tâches. Le protocole et les métadonnées scientifiques doivent permettre de retrouver sources, paramètres, versions, partitions et artefacts géographiques.
