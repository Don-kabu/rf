from dataclasses import dataclass
from math import isfinite

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class SLICConfig:
    n_segments: int
    compactness: float = 10.0
    sigma: float = 0.0
    enforce_connectivity: bool = True
    start_label: int = 1

    def __post_init__(self) -> None:
        if self.n_segments < 2:
            raise ValueError("n_segments must be at least 2.")
        if not isfinite(self.compactness) or self.compactness <= 0:
            raise ValueError("compactness must be positive and finite.")
        if not isfinite(self.sigma) or self.sigma < 0:
            raise ValueError("sigma must be finite and non-negative.")
        if self.start_label != 1:
            raise ValueError("start_label must be 1 because 0 is reserved for masked pixels.")


def normalize_slic_channels(
    image: NDArray[np.floating],
    valid_mask: NDArray[np.bool_] | None = None,
    lower_percentile: float = 2.0,
    upper_percentile: float = 98.0,
) -> NDArray[np.float32]:
    """Scale each spectral channel independently to [0, 1] using valid pixels."""
    composite = np.asarray(image, dtype=np.float32)
    if composite.ndim not in (2, 3):
        raise ValueError("image must have shape H×W or H×W×channels.")
    if not 0 <= lower_percentile < upper_percentile <= 100:
        raise ValueError("Percentiles must satisfy 0 <= lower < upper <= 100.")

    finite_pixels = (
        np.isfinite(composite)
        if composite.ndim == 2
        else np.all(np.isfinite(composite), axis=-1)
    )
    if valid_mask is None:
        mask = finite_pixels
    else:
        mask = np.asarray(valid_mask, dtype=bool)
        if mask.shape != composite.shape[:2]:
            raise ValueError("valid_mask must match the image height and width.")
        mask = mask & finite_pixels
    if not np.any(mask):
        raise ValueError("At least one valid pixel is required for normalization.")

    channel_image = composite[..., None] if composite.ndim == 2 else composite
    scaled = np.zeros(channel_image.shape, dtype=np.float32)
    for channel in range(channel_image.shape[-1]):
        channel_values = channel_image[..., channel]
        lower, upper = np.nanpercentile(
            channel_values[mask], [lower_percentile, upper_percentile]
        )
        if upper > lower:
            scaled[..., channel] = np.clip(
                (channel_values - lower) / (upper - lower), 0.0, 1.0
            )
    scaled[~mask] = 0.0
    return scaled[..., 0] if composite.ndim == 2 else scaled


def segment_composite(
    image: NDArray[np.floating],
    config: SLICConfig,
    valid_mask: NDArray[np.bool_] | None = None,
) -> NDArray[np.int32]:
    """Run SLIC on a normalized 2D image or H×W×channels spectral composite.

    Label 0 is reserved for masked pixels when ``start_label`` is 1.
    The input channels should already be scaled comparably.
    """
    composite = np.asarray(image, dtype=np.float32)
    if composite.ndim not in (2, 3):
        raise ValueError("image must have shape H×W or H×W×channels.")
    if composite.shape[0] == 0 or composite.shape[1] == 0:
        raise ValueError("image dimensions cannot be empty.")

    finite_pixels = (
        np.isfinite(composite)
        if composite.ndim == 2
        else np.all(np.isfinite(composite), axis=-1)
    )
    if valid_mask is None:
        mask = finite_pixels
    else:
        mask = np.asarray(valid_mask, dtype=bool)
        if mask.shape != composite.shape[:2]:
            raise ValueError("valid_mask must match the image height and width.")
        mask = mask & finite_pixels
    if not np.any(mask):
        raise ValueError("At least one valid pixel is required for SLIC.")

    from skimage.segmentation import slic

    clean_image = np.nan_to_num(composite, nan=0.0, posinf=0.0, neginf=0.0)
    return slic(
        clean_image,
        n_segments=config.n_segments,
        compactness=config.compactness,
        sigma=config.sigma,
        enforce_connectivity=config.enforce_connectivity,
        start_label=config.start_label,
        mask=mask,
        convert2lab=False,
        channel_axis=-1 if composite.ndim == 3 else None,
    ).astype(np.int32, copy=False)
