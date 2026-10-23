# Résultat réel consommé par l’application

Après l’entraînement et l’évaluation, déposer le résumé ici sous le nom exact :

```text
backend/results/latest_result.json
```

L’API `GET /api/v1/results/latest` valide le JSON puis le client Vue peut l’afficher avec le bouton **Charger le dernier résultat réel**. Le schéma complet et un exemple cohérent sont dans [`doc/FEUILLE_ROUTE_DONNEES_ENTRAINEMENT_TESTS.md`](../../doc/FEUILLE_ROUTE_DONNEES_ENTRAINEMENT_TESTS.md).

À respecter :

- `is_simulation` doit être `false` et `data_source` doit identifier la source réelle/proxy utilisée ;
- `configuration` doit contenir `area_name`, `n_segments`, `n_dates` et `compactness` ; les métadonnées scientifiques peuvent s’y ajouter ;
- l’ordre de `classes` définit l’ordre des lignes (référence) et colonnes (prédiction) de `confusion_matrix` ;
- métriques globales et par classe doivent être recalculables depuis la matrice ;
- `map_grid` est un aperçu catégoriel de maximum 80 × 80 cellules, sans coordonnées ; chaque valeur doit référencer un identifiant dans `classes` ;
- les importances de variables sont comprises entre 0 et 1.

Ne pas déposer les rasters sources ou une carte lourde dans ce JSON. Conserver les données volumineuses sous `data/raw/` ou `data/processed/`, conformément aux règles de partage et aux licences des sources.
