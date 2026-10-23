import json

from fastapi.testclient import TestClient

from app import main
from app.main import app
from app.schemas import SimulationRequest
from app.simulator import build_demo_result

client = TestClient(app)


def test_health_endpoint_returns_service_status():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "agrislic-api",
        "version": "0.1.0",
    }


def test_demo_endpoint_is_explicitly_synthetic():
    response = client.get("/api/v1/demo")

    assert response.status_code == 200
    result = response.json()
    assert result["is_simulation"] is True
    assert result["data_source"] == "synthetic_demo"
    assert "aucun modèle n'a été entraîné" in result["notice"]


def test_simulation_metrics_match_confusion_matrix():
    response = client.post(
        "/api/v1/simulations",
        json={
            "area_name": "Zone test",
            "n_segments": 250,
            "n_dates": 8,
            "compactness": 5,
        },
    )

    assert response.status_code == 200
    result = response.json()
    matrix = result["confusion_matrix"]
    total = sum(sum(row) for row in matrix)
    correct = sum(matrix[index][index] for index in range(len(matrix)))

    assert result["configuration"]["area_name"] == "Zone test"
    assert result["metrics"]["samples"] == total
    assert result["metrics"]["correct"] == correct
    assert result["metrics"]["accuracy"] == round(correct / total, 4)
    assert len(result["class_metrics"]) == len(result["classes"])

    for index, metrics in enumerate(result["class_metrics"]):
        true_positive = matrix[index][index]
        support = sum(matrix[index])
        predicted = sum(row[index] for row in matrix)
        assert metrics["support"] == support
        assert metrics["predicted"] == predicted
        assert metrics["precision"] == round(true_positive / predicted, 4)
        assert metrics["recall"] == round(true_positive / support, 4)
        assert metrics["f1"] == round(
            2 * true_positive / (support + predicted), 4
        )

    macro_f1 = sum(item["f1"] for item in result["class_metrics"]) / len(matrix)
    assert result["metrics"]["macro_f1"] == round(macro_f1, 4)
    assert len(result["map_grid"]) > 0


def test_invalid_parameters_are_rejected():
    response = client.post(
        "/api/v1/simulations",
        json={"n_segments": 1},
    )

    assert response.status_code == 422


def test_latest_result_explains_when_artifact_is_missing(tmp_path, monkeypatch):
    missing_file = tmp_path / "latest_result.json"
    monkeypatch.setattr(main, "LATEST_RESULT_PATH", missing_file)

    response = client.get("/api/v1/results/latest")

    assert response.status_code == 404
    assert "Aucun résultat réel" in response.json()["detail"]


def test_latest_result_loads_valid_real_artifact(tmp_path, monkeypatch):
    result_file = tmp_path / "latest_result.json"
    monkeypatch.setattr(main, "LATEST_RESULT_PATH", result_file)
    result = build_demo_result(SimulationRequest())
    result["is_simulation"] = False
    result["data_source"] = "test_reference_fixture"
    result["notice"] = "Fixture de test de l'API, pas un résultat scientifique."
    result["configuration"]["reference_source"] = "fixture"
    result_file.write_text(json.dumps(result), encoding="utf-8")

    response = client.get("/api/v1/results/latest")

    assert response.status_code == 200
    assert response.json()["is_simulation"] is False
    assert response.json()["data_source"] == "test_reference_fixture"
    assert response.json()["configuration"]["reference_source"] == "fixture"


def test_latest_result_rejects_a_simulation_artifact(tmp_path, monkeypatch):
    result_file = tmp_path / "latest_result.json"
    monkeypatch.setattr(main, "LATEST_RESULT_PATH", result_file)
    result_file.write_text(
        json.dumps(build_demo_result(SimulationRequest())),
        encoding="utf-8",
    )

    response = client.get("/api/v1/results/latest")

    assert response.status_code == 422
    assert "is_simulation" in response.json()["detail"]
