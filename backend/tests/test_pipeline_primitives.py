import pytest

np = pytest.importorskip("numpy")

from app.pipeline.features import extract_superpixel_features, spectral_indices
from app.pipeline.labels import assign_majority_labels
from app.pipeline.segmentation import normalize_slic_channels


BANDS = ["B2", "B3", "B4", "B8", "B11"]


def test_spectral_indices_return_nan_for_zero_denominators():
    reflectance = np.array(
        [[[0.1, 0.1, 0.0, 0.0, 0.0], [0.1, 0.1, 0.2, 0.6, 0.2]]],
        dtype=np.float32,
    )

    indices = spectral_indices(reflectance, BANDS)

    assert np.isnan(indices["NDVI"][0, 0])
    assert np.isnan(indices["NDMI_B8_B11"][0, 0])
    assert indices["NDVI"][0, 1] == pytest.approx(0.5)
    assert indices["NDMI_B8_B11"][0, 1] == pytest.approx(0.5)


def test_feature_extraction_returns_one_row_per_segment_and_valid_date_count():
    reflectance = np.array(
        [
            [[[0.1, 0.2, 0.2, 0.8, 0.4], [0.2, 0.3, 0.4, 0.6, 0.2]]],
            [[[0.1, 0.2, 0.25, 0.75, 0.4], [0.2, 0.3, 0.35, 0.65, 0.25]]],
        ],
        dtype=np.float32,
    )
    segments = np.array([[1, 1]], dtype=np.int32)

    segment_ids, features, feature_names = extract_superpixel_features(
        reflectance, segments, BANDS
    )

    assert segment_ids.tolist() == [1]
    assert features.shape == (1, len(feature_names))
    assert np.isfinite(features).all()
    assert feature_names[-1] == "valid_date_count"
    assert features[0, -1] == 2
    assert "NDVI_temporal_median" in feature_names
    assert "NDMI_B8_B11_temporal_median" in feature_names


def test_channel_normalization_uses_valid_pixel_ranges():
    image = np.array(
        [[[0.0, 100.0], [5.0, 200.0]], [[10.0, 300.0], [1000.0, 9000.0]]],
        dtype=np.float32,
    )

    normalized = normalize_slic_channels(
        image, lower_percentile=0, upper_percentile=100
    )

    assert normalized.shape == image.shape
    assert normalized.min() == pytest.approx(0.0)
    assert normalized.max() == pytest.approx(1.0)
    assert np.all((normalized >= 0.0) & (normalized <= 1.0))


def test_majority_labels_keep_class_zero_and_reject_mixed_segments():
    segments = np.array([[1, 1, 2, 2]], dtype=np.int32)
    reference = np.array([[0, 0, 1, 2]], dtype=np.int16)

    assignments = assign_majority_labels(
        segments, reference, minimum_purity=0.75
    )

    assert assignments.segment_ids.tolist() == [1]
    assert assignments.class_ids.tolist() == [0]
    assert assignments.purity.tolist() == pytest.approx([1.0])
    assert assignments.rejected_segment_ids.tolist() == [2]
    assert assignments.unlabeled_segment_ids.tolist() == []


def test_slic_uses_zero_for_masked_pixels():
    pytest.importorskip("skimage")
    from app.pipeline.segmentation import SLICConfig, segment_composite

    image = np.zeros((24, 24, 3), dtype=np.float32)
    image[:, 12:, 0] = 1.0
    mask = np.ones((24, 24), dtype=bool)
    mask[:, :3] = False

    labels = segment_composite(
        image, SLICConfig(n_segments=8, compactness=5), valid_mask=mask
    )

    assert labels.shape == mask.shape
    assert np.all(labels[:, :3] == 0)
    assert np.all(labels[:, 3:] > 0)


def test_spatial_split_never_shares_a_group_between_partitions():
    pytest.importorskip("sklearn")
    from app.pipeline.spatial_split import split_by_spatial_groups

    groups = np.repeat(np.arange(6), 2)
    train, test = split_by_spatial_groups(len(groups), groups, test_fraction=0.33)

    assert np.intersect1d(groups[train], groups[test]).size == 0


def test_random_forest_returns_test_metrics_with_declared_class_order():
    pytest.importorskip("sklearn")
    from app.pipeline.classifier import evaluate_random_forest, train_random_forest

    features = np.array([[0.0], [0.1], [0.9], [1.0]], dtype=np.float32)
    labels = np.array([0, 0, 1, 1], dtype=np.int64)
    catalog = [{"id": 0, "name": "Classe 0"}, {"id": 1, "name": "Classe 1"}]
    model = train_random_forest(features, labels, n_estimators=10, random_seed=42)

    result = evaluate_random_forest(model, features, labels, catalog, ["B8_median"])

    assert len(result["confusion_matrix"]) == 2
    assert result["metrics"]["samples"] == len(labels)
    assert result["feature_importances"][0]["feature"] == "B8_median"
