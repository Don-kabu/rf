import json
from json import JSONDecodeError
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .schemas import SimulationRequest, SimulationResult
from .simulator import build_demo_result

LATEST_RESULT_PATH = Path(__file__).resolve().parents[1] / "results" / "latest_result.json"

app = FastAPI(
    title="AgriSLIC API",
    description=(
        "API de démonstration du projet SLIC + Random Forest. "
        "Les résultats réels peuvent être chargés depuis le fichier "
        "backend/results/latest_result.json."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/v1/health", tags=["service"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "agrislic-api", "version": "0.1.0"}


@app.get("/api/v1/demo", response_model=SimulationResult, tags=["demonstration"])
def get_demo() -> dict:
    return build_demo_result(SimulationRequest())


@app.get(
    "/api/v1/results/latest",
    response_model=SimulationResult,
    tags=["results"],
)
def get_latest_result() -> SimulationResult:
    """Load the latest result artifact produced by the data/training workflow."""
    result_path = LATEST_RESULT_PATH
    if not result_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=(
                "Aucun résultat réel n'est encore disponible. Après les tests, "
                "place le fichier latest_result.json dans backend/results/."
            ),
        )

    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        result = SimulationResult.model_validate(payload)
    except (JSONDecodeError, UnicodeDecodeError, ValidationError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "Le fichier backend/results/latest_result.json est invalide. "
                "Vérifie le format décrit dans doc/FEUILLE_ROUTE_DONNEES_ENTRAINEMENT_TESTS.md."
            ),
        ) from exc

    if result.is_simulation:
        raise HTTPException(
            status_code=422,
            detail="Le résultat chargé doit être réel (is_simulation doit valoir false).",
        )
    return result


@app.post(
    "/api/v1/simulations",
    response_model=SimulationResult,
    tags=["demonstration"],
)
def create_simulation(configuration: SimulationRequest) -> dict:
    """Return a deterministic synthetic result to exercise the Vue client."""
    return build_demo_result(configuration)
