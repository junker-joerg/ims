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


def test_candidate_validation_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-candidate-validation-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-execution-candidate-validation.v1"
    )
    assert payload["input_schema_version"] == (
        "ims.strategy-execution-candidate-input.v1"
    )
    assert payload["single_shared_draft_required"] is True
    assert payload["complete_vn_process_target_coverage_required"] is True
    assert payload["snapshot_loader_invocation_enabled"] is False
    assert payload["candidate_creation_enabled"] is False
    assert payload["runner_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_candidate_validation_endpoint_accepts_complete_joint_input(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/execution-candidate-validation",
        json=_request(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["valid"] is True
    assert payload["vn_context_valid"] is True
    assert payload["vu_input_valid"] is True
    assert payload["vu_state_valid"] is True
    assert payload["scenario_profile_reference_valid"] is True
    assert payload["vn_process_input_valid"] is True
    assert payload["candidate_created"] is False
    assert payload["execution_performed"] is False


def test_candidate_validation_endpoint_reports_errors_and_rejects_other_methods(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-candidate-validation"
    request = _request()
    invalid = deepcopy(request)
    invalid["vn_process_input"]["period"] = 3

    response = client.post(endpoint, json=invalid)
    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["issues"][0]["code"] == "period_mismatch"
    assert response.json()["candidate_created"] is False
    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert invalid_json.json()["candidate_created"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
