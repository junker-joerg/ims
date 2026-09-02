import json
from pathlib import Path

from starlette.testclient import TestClient

from ims.api.app import create_app


FIXTURES = Path(__file__).parent / "fixtures"


def _request_payload() -> dict[str, object]:
    return {
        "draft": json.loads(
            (FIXTURES / "strategy_assignment_draft_v1.json").read_text(
                encoding="utf-8"
            )
        ),
        "context": json.loads(
            (FIXTURES / "strategy_assignment_snapshot_context_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    }


def test_assignment_snapshot_context_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-snapshot-context-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "ims.strategy-assignment-snapshot-context.v1"
    assert payload["contract_issue_count"] == 0
    assert payload["validation_endpoint"] == (
        "/api/strategies/assignment-snapshot-context-validation"
    )
    assert len(payload["field_definitions"]) == 18
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["execution_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_assignment_snapshot_context_validation_accepts_without_consuming_values(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/assignment-snapshot-context-validation",
        json=_request_payload(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["valid"] is True
    assert payload["expected_entry_count"] == 3
    assert payload["validated_entry_count"] == 3
    assert payload["expected_value_count"] == 23
    assert payload["resolved_value_count"] == 23
    assert payload["all_context_values_supplied"] is True
    assert payload["context_values_consumed"] is False
    assert payload["snapshots_created"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert not list(tmp_path.iterdir())


def test_assignment_snapshot_context_validation_reports_atomic_errors(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    request = _request_payload()
    del request["context"]["entries"][0]["values"]["interest_rate"]

    response = client.post(
        "/api/strategies/assignment-snapshot-context-validation",
        json=request,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert payload["issues"][0]["code"] == "context_value_missing"
    assert payload["snapshot_materialization_ready"] is False
    assert payload["snapshots_created"] is False


def test_assignment_snapshot_context_validation_rejects_invalid_json_and_methods(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-snapshot-context-validation"

    response = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json()["issues"][0]["code"] == "invalid_json"
    assert response.json()["context_values_consumed"] is False
    assert response.json()["snapshots_created"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
