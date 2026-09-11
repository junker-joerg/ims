from copy import deepcopy
import json
from pathlib import Path

from fastapi.testclient import TestClient

from ims.api.app import create_app


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_execution_period_chain_input_v1.json"
)


def _request() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_period_chain_validation_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-period-chain-validation-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-execution-period-chain-validation.v1"
    )
    assert payload["input_schema_version"] == (
        "ims.strategy-execution-period-chain-input.v1"
    )
    assert payload["complete_horizon_required"] is True
    assert payload["candidate_storage_resolution_enabled"] is False
    assert payload["period_chain_creation_enabled"] is False
    assert payload["runner_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_period_chain_validation_endpoint_accepts_complete_input(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/execution-period-chain-validation",
        json=_request(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["valid"] is True
    assert payload["horizon_valid"] is True
    assert payload["candidate_references_valid"] is True
    assert payload["transitions_valid"] is True
    assert payload["candidate_storage_resolved"] is False
    assert payload["period_chain_created"] is False
    assert payload["execution_performed"] is False


def test_period_chain_validation_endpoint_reports_errors_and_rejects_other_methods(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-period-chain-validation"
    invalid = deepcopy(_request())
    invalid["transitions"][0]["to_period"] = 3

    response = client.post(endpoint, json=invalid)
    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["partial_chain_returned"] is False
    assert invalid_json.status_code == 400
    invalid_json_payload = invalid_json.json()
    assert invalid_json_payload["issues"][0]["code"] == "invalid_json"
    assert invalid_json_payload["period_chain_created"] is False
    assert invalid_json_payload["next_gate"] == "PR138"
    assert set(invalid_json_payload) == set(
        client.post(endpoint, json={}).json()
    )
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
