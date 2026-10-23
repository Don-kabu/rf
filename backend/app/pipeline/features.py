from collections.abc import Sequence
import warnings

import numpy as np
from numpy.typing import NDArray


DEFAULT_TEMPORAL_STATISTICS = ("median", "p10", "p90", "p90_minus_p10")
SUPPORTED_TEMPORAL_STATISTICS = frozenset(DEFAULT_TEMPORAL_STATISTICS)


def _safe_normalized_difference(
    first: NDArray[np.floating],
    second: NDArray[np.floating],
    epsilon: float,
) -> NDArray[np.float32]:
    denominator = first + second
    result = np.full(denominator.shape, np.nan, dtype=np.float32)
    valid = (
        np.isfinite(first)
        & np.isfinite(second)
        & np.isfinite(denominator)
        & (np.abs(denominator) > epsilon)
    )
    np.divide(first - second, denominator, out=result, where=valid)
    return result


def spectral_indices(
    reflectance: NDArray[np.floating],
    band_names: Sequence[str],
    epsilon: float = 1e-8,
) -> dict[str, NDArray[np.float32]]:
    """Compute NDVI and NDMI (B8-B11) from a (..., bands) reflectance array."""
    values = np.asarray(reflectance, dtype=np.float32)
    names = list(band_names)
    if values.ndim < 2 or values.shape[-1] != len(names):
        raise ValueError("The final array dimension must match band_names.")
    if len(set(names)) != len(names):
        raise ValueError("band_names cannot contain duplicates.")
    if epsilon <= 0:
        raise ValueError("epsilon must be positive.")

    indices: dict[str, NDArray[np.float32]] = {}
    band_index = {name: index for index, name in enumerate(names)}
    if "B8" in band_index and "B4" in band_index:
        indices["NDVI"] = _safe_normalized_difference(
            values[..., band_index["B8"]], values[..., band_index["B4"]], epsilon
        )
    if "B8" in band_index and "B11" in band_index:
        indices["NDMI_B8_B11"] = _safe_normalized_difference(
            values[..., band_index["B8"]], values[..., band_index["B11"]], epsilon
        )
    return indices


def extract_superpixel_features(
    reflectance: NDArray[np.floating],
    segment_labels: NDArray[np.integer],
    band_names: Sequence[str],
    valid_mask: NDArray[np.bool_] | None = None,
    temporal_statistics: Sequence[str] = DEFAULT_TEMPORAL_STATISTICS,
) -> tuple[NDArray[np.int64], NDArray[np.float32], list[str]]:
    """Summarize multi-date reflectance as one feature row per SLIC segment.

    ``reflectance`` must have shape dates×height×width×bands. A pixel is treated
    as valid only when all bands are finite and the optional date mask is true.
    Temporal summaries are calculated from per-date spatial medians.
    """
    values = np.asarray(reflectance, dtype=np.float32)
    segments = np.asarray(segment_labels)
    names = list(band_names)
    statistics = tuple(temporal_statistics)

    if values.ndim != 4:
        raise ValueError("reflectance must have shape dates×height×width×bands.")
    date_count, height, width, band_count = values.shape
    if date_count == 0 or height == 0 or width == 0:
        raise ValueError("reflectance dimensions cannot be empty.")
    if band_count != len(names) or len(set(names)) != len(names):
        raise ValueError("band_names must uniquely identify every input band.")
    if segments.shape != (height, width):
        raise ValueError("segment_labels must match the image height and width.")
    unsupported = set(statistics) - SUPPORTED_TEMPORAL_STATISTICS
    if unsupported:
        raise ValueError(f"Unsupported temporal statistics: {sorted(unsupported)}")
    if not statistics:
        raise ValueError("At least one temporal statistic is required.")
    if not np.issubdtype(segments.dtype, np.integer):
        raise ValueError("segment_labels must contain integer identifiers.")

    if valid_mask is None:
        mask = np.ones((date_count, height, width), dtype=bool)
    else:
        mask = np.asarray(valid_mask, dtype=bool)
        if mask.shape == (height, width):
            mask = np.broadcast_to(mask, (date_count, height, width))
        elif mask.shape != (date_count, height, width):
            raise ValueError("valid_mask must have shape H×W or dates×H×W.")
    mask = mask & np.all(np.isfinite(values), axis=-1)

    segment_ids = np.unique(segments[segments > 0]).astype(np.int64)
    if segment_ids.size == 0:
        raise ValueError("No positive segment identifiers were found.")

    band_index = {name: index for index, name in enumerate(names)}
    feature_sources: list[tuple[str, str, int | None, int | None]] = [
        (name, "band", band_index[name], None) for name in names
    ]
    if "B8" in band_index and "B4" in band_index:
        feature_sources.append(("NDVI", "index", band_index["B8"], band_index["B4"]))
    if "B8" in band_index and "B11" in band_index:
        feature_sources.append(
            ("NDMI_B8_B11", "index", band_index["B8"], band_index["B11"])
        )

    feature_names = [
        f"{source_name}_temporal_{statistic}"
        for source_name, _, _, _ in feature_sources
        for statistic in statistics
    ] + ["valid_date_count"]
    feature_matrix = np.full(
        (len(segment_ids), len(feature_names)), np.nan, dtype=np.float32
    )

    flat_segments = segments.reshape(-1)
    positive_pixel_indices = np.flatnonzero(flat_segments > 0)
    order = np.argsort(flat_segments[positive_pixel_indices], kind="stable")
    sorted_pixel_indices = positive_pixel_indices[order]
    sorted_segment_ids = flat_segments[sorted_pixel_indices]
    boundaries = np.searchsorted(sorted_segment_ids, segment_ids, side="left")
    ends = np.searchsorted(sorted_segment_ids, segment_ids, side="right")

    values_flat = values.reshape(date_count, height * width, band_count)
    mask_flat = mask.reshape(date_count, height * width)
    for row_index, (start, end) in enumerate(zip(boundaries, ends, strict=True)):
        pixel_indices = sorted_pixel_indices[start:end]
        if pixel_indices.size == 0:
            continue
        per_segment_valid = mask_flat[:, pixel_indices]
        feature_index = 0

        for _, source_type, first_band, second_band in feature_sources:
            first = values_flat[:, pixel_indices, first_band]
            if source_type == "band":
                date_values = first
            else:
                second = values_flat[:, pixel_indices, second_band]
                denominator = first + second
                date_values = np.full(denominator.shape, np.nan, dtype=np.float32)
                safe = np.abs(denominator) > 1e-8
                np.divide(first - second, denominator, out=date_values, where=safe)

            masked_values = np.where(per_segment_valid, date_values, np.nan)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                per_date_median = np.nanmedian(masked_values, axis=1)
                median = np.nanmedian(per_date_median)
                p10, p90 = np.nanpercentile(per_date_median, [10, 90])

            statistic_values = {
                "median": median,
                "p10": p10,
                "p90": p90,
                "p90_minus_p10": p90 - p10,
            }
            for statistic in statistics:
                feature_matrix[row_index, feature_index] = statistic_values[statistic]
                feature_index += 1

        feature_matrix[row_index, feature_index] = np.count_nonzero(
            np.any(per_segment_valid, axis=1)
        )

    return segment_ids, feature_matrix, feature_names
