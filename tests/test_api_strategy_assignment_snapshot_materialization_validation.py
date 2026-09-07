from copy import deepcopy
import json
from pathlib import Path

from fastapi.testclient import TestClient

from ims.api.app import create_app


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_assignment_snapshot_materialization_validation_v1.json"
)


def _request() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_materialization_validation_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = (
        "/api/strategies/assignment-snapshot-materialization-validation-contract"
    )

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-assignment-snapshot-materialization-validation.v1"
    )
    assert payload["validated_rule_count"] == 6
    assert payload["validated_nested_schema_count"] == 9
    assert payload["materialization_contract_issue_count"] == 0
    assert payload["snapshot_loader_invocation_enabled"] is False
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["execution_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_materialization_validation_endpoint_accepts_complete_vn_context(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/assignment-snapshot-materialization-validation",
        json=_request(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["valid"] is True
    assert payload["validated_vn_entry_count"] == 6
    assert payload["materialization_input_valid"] is True
    assert payload["context_values_consumed"] is False
    assert payload["snapshot_loader_invocation_performed"] is False
    assert payload["snapshots_created"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_materialization_validation_endpoint_reports_atomic_semantic_errors(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    request = _request()
    invalid = deepcopy(request)
    invalid["context"]["entries"][4]["values"]["draws"][
        "insurer_choice_draws_by_sector"
    ][0] = [0.1]

    response = client.post(
        "/api/strategies/assignment-snapshot-materialization-validation",
        json=invalid,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert payload["validated_vn_entry_count"] == 5
    assert payload["issues"][0]["code"] == "sample_draw_count_insufficient"
    assert payload["materialization_input_valid"] is False
    assert payload["snapshot_materialization_ready"] is False
    assert payload["snapshots_created"] is False


def test_materialization_validation_endpoint_rejects_invalid_json_and_methods(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-snapshot-materialization-validation"

    response = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["issues"][0]["code"] == "invalid_json"
    assert payload["context_values_consumed"] is False
    assert payload["snapshot_loader_invocation_performed"] is False
    assert payload["snapshots_created"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
