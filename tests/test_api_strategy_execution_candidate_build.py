from copy import deepcopy
import json
from pathlib import Path

from fastapi.testclient import TestClient

from ims.api.app import create_app


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_execution_candidate_input_v1.json"
)


def _request() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_candidate_build_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-candidate-build-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-execution-candidate-build.v1"
    )
    assert payload["known_profile_ids"] == ["synthetic-joint-single-period-v1"]
    assert payload["scenario_profile_resolution_enabled"] is True
    assert payload["server_side_rematerialization_enabled"] is True
    assert payload["digest_calculation_enabled"] is True
    assert payload["candidate_persistence_enabled"] is False
    assert payload["runner_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_candidate_build_endpoint_returns_ephemeral_candidate(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/execution-candidate-build",
        json=_request(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["build_complete"] is True
    assert payload["scenario_profile_resolved"] is True
    assert payload["server_side_rematerialization_performed"] is True
    assert payload["canonical_loaded_scenario_created"] is True
    assert payload["digest_calculation_performed"] is True
    assert payload["candidate_created"] is True
    assert payload["candidate_persisted"] is False
    assert payload["execution_performed"] is False
    assert payload["candidate"]["identity"]["content_digest"].startswith(
        "sha256:"
    )


def test_candidate_build_endpoint_reports_errors_and_rejects_other_methods(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-candidate-build"
    invalid = deepcopy(_request())
    invalid["scenario_profile_reference"]["profile_id"] = "unknown-profile"

    response = client.post(endpoint, json=invalid)
    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["build_complete"] is False
    assert response.json()["issues"][0]["code"] == "unknown_scenario_profile"
    assert response.json()["candidate"] is None
    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert invalid_json.json()["candidate_created"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
