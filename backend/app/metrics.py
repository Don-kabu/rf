from collections.abc import Mapping, Sequence
from typing import Any


def calculate_classification_metrics(
    confusion_matrix: Sequence[Sequence[int]],
    classes: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Calculate overall and per-class scores using rows=true, columns=predicted."""
    class_count = len(classes)
    if class_count == 0 or len(confusion_matrix) != class_count:
        raise ValueError("The confusion matrix must have one row per class.")
    if any(len(row) != class_count for row in confusion_matrix):
        raise ValueError("The confusion matrix must be square.")
    if any(value < 0 for row in confusion_matrix for value in row):
        raise ValueError("Confusion matrix counts cannot be negative.")

    total = sum(sum(row) for row in confusion_matrix)
    correct = sum(confusion_matrix[index][index] for index in range(class_count))
    class_metrics: list[dict[str, Any]] = []

    for index, class_info in enumerate(classes):
        true_positive = confusion_matrix[index][index]
        support = sum(confusion_matrix[index])
        predicted = sum(confusion_matrix[row][index] for row in range(class_count))
        precision = true_positive / predicted if predicted else 0.0
        recall = true_positive / support if support else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        class_metrics.append(
            {
                "class_id": class_info["id"],
                "class_name": class_info["name"],
                "support": support,
                "predicted": predicted,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }
        )

    metrics = {
        "accuracy": round(correct / total if total else 0.0, 4),
        "macro_f1": round(
            sum(item["f1"] for item in class_metrics) / class_count, 4
        ),
        "samples": total,
        "correct": correct,
    }
    return metrics, class_metrics
