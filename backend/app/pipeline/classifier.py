from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ..metrics import calculate_classification_metrics


def train_random_forest(
    features: NDArray[np.floating],
    labels: NDArray[np.integer],
    n_estimators: int = 300,
    max_features: str | int | float = "sqrt",
    class_weight: str | None = "balanced",
    random_seed: int = 42,
) -> Any:
    """Fit the proposed RF baseline on an already filtered training partition."""
    x = np.asarray(features, dtype=np.float32)
    y = np.asarray(labels)
    if x.ndim != 2 or y.ndim != 1 or x.shape[0] != y.size:
        raise ValueError("features must be 2D and align row-for-row with labels.")
    if x.shape[0] < 2 or x.shape[1] == 0 or np.unique(y).size < 2:
        raise ValueError("At least two samples and two classes are required.")
    if not np.all(np.isfinite(x)):
        raise ValueError("Non-finite feature rows must be filtered before training.")
    if n_estimators < 1:
        raise ValueError("n_estimators must be at least 1.")

    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_features=max_features,
        class_weight=class_weight,
        random_state=random_seed,
        n_jobs=1,
    )
    return model.fit(x, y)


def evaluate_random_forest(
    model: Any,
    features: NDArray[np.floating],
    reference_labels: NDArray[np.integer],
    classes: Sequence[Mapping[str, Any]],
    feature_names: Sequence[str],
) -> dict[str, Any]:
    """Evaluate once on held-out samples and return the shared result components."""
    x = np.asarray(features, dtype=np.float32)
    y_true = np.asarray(reference_labels)
    class_ids = [int(item["id"]) for item in classes]
    if x.ndim != 2 or y_true.ndim != 1 or x.shape[0] != y_true.size:
        raise ValueError("Test features and reference labels must align.")
    if x.shape[0] == 0 or not np.all(np.isfinite(x)):
        raise ValueError("Test features must be non-empty and finite.")
    if len(class_ids) < 2 or len(set(class_ids)) != len(class_ids):
        raise ValueError("At least two uniquely identified classes are required.")
    if len(feature_names) != x.shape[1]:
        raise ValueError("feature_names must match the feature matrix columns.")
    if not set(np.unique(y_true).tolist()).issubset(class_ids):
        raise ValueError("Test labels contain a class absent from the class catalog.")

    from sklearn.metrics import confusion_matrix

    predicted_labels = model.predict(x)
    observed_classes = set(np.unique(y_true).tolist()) | set(
        np.unique(predicted_labels).tolist()
    )
    if not observed_classes.issubset(class_ids):
        raise ValueError("Observed labels contain a class absent from the class catalog.")
    matrix = confusion_matrix(y_true, predicted_labels, labels=class_ids).tolist()
    metrics, class_metrics = calculate_classification_metrics(matrix, classes)
    importances = getattr(model, "feature_importances_", None)
    feature_importances = (
        [
            {"feature": name, "importance": float(value)}
            for name, value in zip(feature_names, importances, strict=True)
        ]
        if importances is not None
        else []
    )
    return {
        "confusion_matrix": matrix,
        "metrics": metrics,
        "class_metrics": class_metrics,
        "feature_importances": feature_importances,
        "predicted_labels": predicted_labels,
    }
