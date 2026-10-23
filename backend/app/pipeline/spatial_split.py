import numpy as np
from numpy.typing import NDArray


def spatial_block_groups(
    x_coordinates_m: NDArray[np.floating],
    y_coordinates_m: NDArray[np.floating],
    block_size_m: float,
) -> NDArray[np.int64]:
    """Map projected metre coordinates to deterministic square-block group ids."""
    x = np.asarray(x_coordinates_m, dtype=np.float64)
    y = np.asarray(y_coordinates_m, dtype=np.float64)
    if x.ndim != 1 or y.ndim != 1 or x.shape != y.shape:
        raise ValueError("x and y coordinates must be matching one-dimensional arrays.")
    if x.size == 0 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("Coordinates must be non-empty and finite.")
    if not np.isfinite(block_size_m) or block_size_m <= 0:
        raise ValueError("block_size_m must be positive and finite.")

    block_coordinates = np.column_stack(
        (np.floor(x / block_size_m), np.floor(y / block_size_m))
    ).astype(np.int64)
    _, group_ids = np.unique(block_coordinates, axis=0, return_inverse=True)
    return group_ids.astype(np.int64, copy=False)


def split_by_spatial_groups(
    sample_count: int,
    group_ids: NDArray[np.integer],
    test_fraction: float = 0.2,
    random_seed: int = 42,
) -> tuple[NDArray[np.int64], NDArray[np.int64]]:
    """Return train/test row indices while keeping every group in one split."""
    groups = np.asarray(group_ids)
    if groups.ndim != 1 or groups.size != sample_count:
        raise ValueError("group_ids must contain one group identifier per sample.")
    if sample_count < 2 or np.unique(groups).size < 2:
        raise ValueError("At least two samples and two spatial groups are required.")
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be strictly between 0 and 1.")

    from sklearn.model_selection import GroupShuffleSplit

    splitter = GroupShuffleSplit(
        n_splits=1, test_size=test_fraction, random_state=random_seed
    )
    train_indices, test_indices = next(
        splitter.split(np.arange(sample_count).reshape(-1, 1), groups=groups)
    )
    if np.intersect1d(groups[train_indices], groups[test_indices]).size:
        raise RuntimeError("A spatial group was assigned to both partitions.")
    return train_indices.astype(np.int64), test_indices.astype(np.int64)
