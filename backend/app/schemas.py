from math import isclose
from typing import List

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SimulationRequest(BaseModel):
    area_name: str = Field(default="Zone de démonstration", min_length=1, max_length=120)
    n_segments: int = Field(default=500, ge=10, le=100_000)
    n_dates: int = Field(default=12, ge=1, le=60)
    compactness: float = Field(default=10.0, gt=0, le=1000)


class ClassInfo(BaseModel):
    id: int
    name: str
    color: str


class ClassMetrics(BaseModel):
    class_id: int
    class_name: str
    support: int
    predicted: int
    precision: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)
    f1: float = Field(ge=0, le=1)


class Metrics(BaseModel):
    accuracy: float = Field(ge=0, le=1)
    macro_f1: float = Field(ge=0, le=1)
    samples: int
    correct: int


class FeatureImportance(BaseModel):
    feature: str
    importance: float = Field(ge=0, le=1)


class Configuration(BaseModel):
    # The scientific run may add reproducibility metadata without requiring
    # an application change for every new parameter.
    model_config = ConfigDict(extra="allow")

    area_name: str = Field(min_length=1, max_length=120)
    n_segments: int = Field(ge=1, le=100_000)
    n_dates: int = Field(ge=1, le=60)
    compactness: float = Field(gt=0, le=1000)


class SimulationResult(BaseModel):
    run_id: str
    is_simulation: bool
    data_source: str
    notice: str
    configuration: Configuration
    classes: List[ClassInfo]
    confusion_matrix: List[List[int]]
    metrics: Metrics
    class_metrics: List[ClassMetrics]
    feature_importances: List[FeatureImportance]
    map_grid: List[List[int]]

    @model_validator(mode="after")
    def validate_result_consistency(self) -> "SimulationResult":
        """Reject results whose classes, confusion matrix, and metrics disagree."""
        if self.data_source == "synthetic_demo" and not self.is_simulation:
            raise ValueError("Synthetic demo results must remain marked as simulations.")

        class_ids = [class_info.id for class_info in self.classes]
        if not class_ids:
            raise ValueError("At least one class is required.")
        if any(class_id < 0 for class_id in class_ids):
            raise ValueError("Class identifiers must be non-negative integers.")
        if len(set(class_ids)) != len(class_ids):
            raise ValueError("Class identifiers must be unique.")

        class_count = len(class_ids)
        if len(self.confusion_matrix) != class_count or any(
            len(row) != class_count for row in self.confusion_matrix
        ):
            raise ValueError(
                "The confusion matrix must be square and match the class count."
            )
        if any(value < 0 for row in self.confusion_matrix for value in row):
            raise ValueError("Confusion matrix counts cannot be negative.")

        metric_ids = [item.class_id for item in self.class_metrics]
        if len(metric_ids) != class_count or set(metric_ids) != set(class_ids):
            raise ValueError("Per-class metrics must contain each class exactly once.")

        class_info_by_id = {class_info.id: class_info for class_info in self.classes}
        metrics_by_id = {item.class_id: item for item in self.class_metrics}
        if any(
            metrics_by_id[class_id].class_name != class_info.name
            for class_id, class_info in class_info_by_id.items()
        ):
            raise ValueError("Per-class metric names must match the class legend.")

        total = sum(sum(row) for row in self.confusion_matrix)
        correct = sum(
            self.confusion_matrix[index][index] for index in range(class_count)
        )
        if self.metrics.samples != total or self.metrics.correct != correct:
            raise ValueError("Overall counts must match the confusion matrix.")

        expected_accuracy = correct / total if total else 0.0
        if not isclose(self.metrics.accuracy, expected_accuracy, abs_tol=0.00011):
            raise ValueError("Accuracy must match the confusion matrix.")

        for index, class_id in enumerate(class_ids):
            item = metrics_by_id[class_id]
            support = sum(self.confusion_matrix[index])
            predicted = sum(row[index] for row in self.confusion_matrix)
            true_positive = self.confusion_matrix[index][index]
            precision = true_positive / predicted if predicted else 0.0
            recall = true_positive / support if support else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if precision + recall
                else 0.0
            )
            if item.support != support or item.predicted != predicted:
                raise ValueError("Per-class counts must match the confusion matrix.")
            if not (
                isclose(item.precision, precision, abs_tol=0.00011)
                and isclose(item.recall, recall, abs_tol=0.00011)
                and isclose(item.f1, f1, abs_tol=0.00011)
            ):
                raise ValueError("Per-class scores must match the confusion matrix.")

        expected_macro_f1 = sum(item.f1 for item in self.class_metrics) / class_count
        if not isclose(self.metrics.macro_f1, expected_macro_f1, abs_tol=0.00011):
            raise ValueError("Macro F1 must match the per-class F1 scores.")

        if not self.map_grid:
            raise ValueError("A categorical map preview is required.")
        if len(self.map_grid) > 80:
            raise ValueError("Map preview cannot exceed 80 rows.")
        row_width = len(self.map_grid[0])
        if row_width > 80:
            raise ValueError("Map preview cannot exceed 80 columns.")
        if row_width == 0 or any(len(row) != row_width for row in self.map_grid):
            raise ValueError("Map grid rows must have the same non-zero width.")
        unknown_ids = {
            cell_id
            for row in self.map_grid
            for cell_id in row
            if cell_id not in class_ids
        }
        if unknown_ids:
            raise ValueError("Map grid contains identifiers absent from classes.")

        return self
