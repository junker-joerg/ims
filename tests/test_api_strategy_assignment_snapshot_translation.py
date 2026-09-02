import json
from pathlib import Path

from starlette.testclient import TestClient

from ims.api.app import create_app


FIXTURE = Path(__file__).parent / "fixtures" / "strategy_assignment_draft_v1.json"


def _fixture_payload() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_assignment_snapshot_translation_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-snapshot-translation-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-assignment-snapshot-translation.v1"
    )
    assert payload["mapping_issue_count"] == 0
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["execution_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_assignment_snapshot_translation_endpoint_returns_partial_payloads_only(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/assignment-snapshot-translation",
        json=_fixture_payload(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["draft_valid"] is True
    assert payload["translation_complete"] is True
    assert payload["translated_assignment_count"] == 3
    assert payload["entries"][0]["snapshot_type"] == (
        "VURandomUniformRuleSnapshot"
    )
    assert payload["entries"][0]["snapshot_payload"]["insurer_id"] == 1
    assert "random_draws" in payload["entries"][0]["unresolved_snapshot_fields"]
    assert payload["defaults_applied"] is False
    assert payload["snapshots_created"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert not list(tmp_path.iterdir())


def test_assignment_snapshot_translation_endpoint_rejects_invalid_draft_atomically(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    payload = _fixture_payload()
    payload["assignments"] = []

    response = client.post(
        "/api/strategies/assignment-snapshot-translation",
        json=payload,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "error"
    assert result["draft_valid"] is False
    assert result["translated_assignment_count"] == 0
    assert result["issues"][0]["code"] == "assignment_required"
    assert result["entries"] == []


def test_assignment_snapshot_translation_rejects_invalid_json_and_other_methods(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-snapshot-translation"

    response = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json()["issues"][0]["code"] == "invalid_json"
    assert response.json()["snapshots_created"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
