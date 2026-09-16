import importlib

from fastapi.testclient import TestClient

from ims.api.app import create_app
from tests.period_chain_test_support import chain_input, persist_chain_candidates


CONTRACT_ENDPOINT = (
    "/api/strategies/execution-period-chain-five-period-build-contract"
)
BUILD_ENDPOINT = "/api/strategies/execution-period-chain-five-period-build"


def test_five_period_build_api_uses_configured_store_and_enforces_methods(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = persist_chain_candidates(db_path, tmp_path, max_periods=5)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))

    contract = client.get(CONTRACT_ENDPOINT)
    response = client.post(
        BUILD_ENDPOINT,
        json=chain_input(references, max_periods=5),
    )

    assert contract.status_code == 200
    assert contract.json()["required_period_count"] == 5
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["five_period_horizon_validated"] is True
    assert payload["resolved_candidate_count"] == 5
    assert payload["period_chain"]["horizon"]["last_period"] == 5
    assert payload["period_chain_persisted"] is False
    assert payload["execution_performed"] is False
    assert client.post(CONTRACT_ENDPOINT, json={}).status_code == 405
    assert client.get(BUILD_ENDPOINT).status_code == 405
    assert client.put(BUILD_ENDPOINT, json={}).status_code == 405
    assert client.delete(BUILD_ENDPOINT).status_code == 405


def test_five_period_build_api_reports_closed_error_paths(
    monkeypatch,
    tmp_path,
) -> None:
    memory_client = TestClient(create_app(frontend_dist=tmp_path))

    unavailable = memory_client.post(BUILD_ENDPOINT, json={})

    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )
    assert unavailable.json()["period_chain"] is None

    db_path = tmp_path / "metadata.sqlite"
    persist_chain_candidates(db_path, tmp_path, max_periods=5)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    sqlite_client = TestClient(create_app(frontend_dist=tmp_path))

    invalid_json = sqlite_client.post(
        BUILD_ENDPOINT,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert invalid_json.json()["period_chain"] is None
    assert invalid_json.json()["runner_invocation_performed"] is False
    assert invalid_json.json()["next_gate"] == "PR147"


def test_starlette_fallback_exposes_same_five_period_build(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = persist_chain_candidates(db_path, tmp_path, max_periods=5)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    app_module = importlib.import_module("ims.api.app")
    monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))

    contract = client.get(CONTRACT_ENDPOINT)
    response = client.post(
        BUILD_ENDPOINT,
        json=chain_input(references, max_periods=5),
    )

    assert contract.status_code == 200
    assert contract.json()["required_period_count"] == 5
    assert response.status_code == 200
    assert response.json()["build_complete"] is True
    assert response.json()["period_chain"]["horizon"]["period_count"] == 5
