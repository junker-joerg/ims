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


def test_materialization_contract_advertises_atomic_operation(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.get(
        "/api/strategies/assignment-snapshot-materialization-contract"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["materialization_schema_version"] == (
        "ims.strategy-assignment-snapshot-materialization.v1"
    )
    assert payload["snapshot_loader_invocation_enabled"] is True
    assert payload["snapshot_materialization_enabled"] is True
    assert payload["partial_results_allowed"] is False
    assert payload["operation"]["validation_required"] is True
    assert payload["operation"]["execution_enabled"] is False


def test_materialization_endpoint_returns_six_snapshots_without_execution(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/assignment-snapshot-materialization",
        json=_request(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["input_valid"] is True
    assert payload["materialization_complete"] is True
    assert payload["snapshot_count"] == 6
    assert payload["snapshot_loader_invocation_count"] == 6
    assert payload["partial_results_returned"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_ready"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_materialization_endpoint_rejects_invalid_input_atomically(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    request = _request()
    invalid = deepcopy(request)
    invalid["context"]["entries"][0]["values"]["active_insurer_ids"] = []

    response = client.post(
        "/api/strategies/assignment-snapshot-materialization",
        json=invalid,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["input_valid"] is False
    assert payload["snapshot_count"] == 0
    assert payload["snapshot_loader_invocation_count"] == 0
    assert payload["issues"][0]["code"] == "active_insurer_ids_empty"


def test_materialization_endpoint_rejects_invalid_json_and_methods(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-snapshot-materialization"

    response = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["issues"][0]["code"] == "invalid_json"
    assert payload["snapshot_count"] == 0
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
