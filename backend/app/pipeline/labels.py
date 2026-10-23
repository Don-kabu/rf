from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class LabelAssignments:
    segment_ids: NDArray[np.int64]
    class_ids: NDArray[np.int64]
    purity: NDArray[np.float32]
    valid_pixel_counts: NDArray[np.int64]
    rejected_segment_ids: NDArray[np.int64]
    unlabeled_segment_ids: NDArray[np.int64]


def assign_majority_labels(
    segment_labels: NDArray[np.integer],
    reference_labels: NDArray[np.integer],
    valid_mask: NDArray[np.bool_] | None = None,
    ignored_values: Sequence[int] = (),
    minimum_purity: float = 0.7,
) -> LabelAssignments:
    """Assign each segment its majority reference class and report its purity.

    Segment id 0 is reserved for pixels outside the segmentation. Reference
    values are categorical; pass source-specific NoData codes in ignored_values.
    Tied majorities resolve to the smallest class identifier deterministically.
    """
    segments = np.asarray(segment_labels)
    reference = np.asarray(reference_labels)
    if segments.ndim != 2 or reference.shape != segments.shape:
        raise ValueError("Segment and reference labels must be matching 2D arrays.")
    if not np.issubdtype(segments.dtype, np.integer):
        raise ValueError("segment_labels must contain integer identifiers.")
    if not np.issubdtype(reference.dtype, np.integer):
        raise ValueError("reference_labels must contain integer class identifiers.")
    if not 0 <= minimum_purity <= 1:
        raise ValueError("minimum_purity must be between 0 and 1.")

    if valid_mask is None:
        valid = np.ones(segments.shape, dtype=bool)
    else:
        valid = np.asarray(valid_mask, dtype=bool).copy()
        if valid.shape != segments.shape:
            raise ValueError("valid_mask must match the segmentation shape.")
    if ignored_values:
        valid &= ~np.isin(reference, np.asarray(ignored_values))
    valid &= segments > 0

    segment_ids = np.unique(segments[segments > 0]).astype(np.int64)
    accepted_segments: list[int] = []
    class_ids: list[int] = []
    purities: list[float] = []
    valid_counts: list[int] = []
    rejected_segments: list[int] = []
    unlabeled_segments: list[int] = []

    for segment_id in segment_ids:
        pixel_values = reference[(segments == segment_id) & valid]
        if pixel_values.size == 0:
            unlabeled_segments.append(int(segment_id))
            continue
        classes, counts = np.unique(pixel_values, return_counts=True)
        majority_index = int(np.argmax(counts))
        purity = float(counts[majority_index] / counts.sum())
        if purity < minimum_purity:
            rejected_segments.append(int(segment_id))
            continue
        accepted_segments.append(int(segment_id))
        class_ids.append(int(classes[majority_index]))
        purities.append(purity)
        valid_counts.append(int(counts.sum()))

    return LabelAssignments(
        segment_ids=np.asarray(accepted_segments, dtype=np.int64),
        class_ids=np.asarray(class_ids, dtype=np.int64),
        purity=np.asarray(purities, dtype=np.float32),
        valid_pixel_counts=np.asarray(valid_counts, dtype=np.int64),
        rejected_segment_ids=np.asarray(rejected_segments, dtype=np.int64),
        unlabeled_segment_ids=np.asarray(unlabeled_segments, dtype=np.int64),
    )
