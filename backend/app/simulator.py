from typing import Any

from .metrics import calculate_classification_metrics
from .schemas import SimulationRequest


CLASSES: list[dict[str, Any]] = [
    {"id": 1, "name": "Maïs", "color": "#d79b28"},
    {"id": 2, "name": "Arboriculture", "color": "#427c58"},
    {"id": 3, "name": "Prairies / savane", "color": "#9dbb63"},
    {"id": 4, "name": "Sols nus / bâti", "color": "#b96f4d"},
]

# Matrice pédagogique, pas issue d'un apprentissage sur des images satellitaires.
CONFUSION_MATRIX: list[list[int]] = [
    [45, 6, 4, 1],
    [5, 33, 4, 1],
    [6, 5, 37, 2],
    [1, 1, 2, 48],
]

FEATURE_IMPORTANCES: list[dict[str, Any]] = [
    {"feature": "ndvi_amplitude", "importance": 0.21},
    {"feature": "ndmi_mean", "importance": 0.18},
    {"feature": "B8_median", "importance": 0.16},
    {"feature": "B4_median", "importance": 0.14},
    {"feature": "B11_median", "importance": 0.12},
    {"feature": "ndvi_max", "importance": 0.10},
    {"feature": "valid_date_count", "importance": 0.09},
]


def _build_demo_map(rows: int = 14, columns: int = 22) -> list[list[int]]:
    """Return a stable, illustrative categorical grid with no geographic meaning."""
    grid: list[list[int]] = []
    for row in range(rows):
        line: list[int] = []
        for column in range(columns):
            if column < 9 and row < 9:
                class_id = 1
            elif column >= 15 and row < 7:
                class_id = 2
            elif column < 14 and row >= 9:
                class_id = 3
            else:
                class_id = 4

            # Add a few deterministic edge cells so the example is not a rectangle.
            if (row * 7 + column * 11) % 19 == 0:
                class_id = (class_id % len(CLASSES)) + 1
            line.append(class_id)
        grid.append(line)
    return grid


def build_demo_result(configuration: SimulationRequest) -> dict[str, Any]:
    metrics, class_metrics = calculate_classification_metrics(
        CONFUSION_MATRIX, CLASSES
    )
    return {
        "run_id": "demo-static-v1",
        "is_simulation": True,
        "data_source": "synthetic_demo",
        "notice": (
            "Résultats synthétiques pour démonstration ; aucune image Sentinel-2 "
            "n'a été traitée et aucun modèle n'a été entraîné."
        ),
        "configuration": configuration.model_dump(),
        "classes": CLASSES,
        "confusion_matrix": CONFUSION_MATRIX,
        "metrics": metrics,
        "class_metrics": class_metrics,
        "feature_importances": FEATURE_IMPORTANCES,
        "map_grid": _build_demo_map(),
    }
