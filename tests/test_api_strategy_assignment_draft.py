import json
from pathlib import Path

from starlette.testclient import TestClient

from ims.api.app import create_app


FIXTURE = Path(__file__).parent / "fixtures" / "strategy_assignment_draft_v1.json"


def _fixture_payload() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_assignment_draft_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.get("/api/strategies/assignment-draft-contract")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "ims.strategy-assignment-draft.v1"
    assert payload["mode"] == "strategy_assignment_draft_contract_read_only"
    assert payload["validation_endpoint"] == (
        "/api/strategies/assignment-draft-validation"
    )
    assert payload["persistence_enabled"] is False
    assert payload["snapshot_translation_enabled"] is False
    assert payload["execution_enabled"] is False
    assert client.post("/api/strategies/assignment-draft-contract", json={}).status_code == 405
    assert client.put("/api/strategies/assignment-draft-contract", json={}).status_code == 405
    assert client.delete("/api/strategies/assignment-draft-contract").status_code == 405


def test_assignment_draft_validation_endpoint_accepts_without_writing(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/assignment-draft-validation",
        json=_fixture_payload(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "ims.strategy-assignment-draft-validation.v1"
    assert payload["status"] == "ok"
    assert payload["valid"] is True
    assert payload["assignment_count"] == 3
    assert payload["validated_assignment_count"] == 3
    assert payload["issue_count"] == 0
    assert payload["writes_performed"] is False
    assert payload["snapshots_created"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert not list(tmp_path.iterdir())


def test_assignment_draft_validation_endpoint_reports_errors_as_validation_result(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    payload = _fixture_payload()
    payload["assignments"] = []

    response = client.post("/api/strategies/assignment-draft-validation", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "error"
    assert result["valid"] is False
    assert result["issues"] == [
        {
            "path": "$.assignments",
            "code": "assignment_required",
            "message": "Entwurf muss mindestens eine Zuordnung enthalten",
        }
    ]
    assert result["writes_performed"] is False
    assert result["execution_performed"] is False


def test_assignment_draft_validation_endpoint_rejects_invalid_json_and_other_methods(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/assignment-draft-validation",
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json()["issues"][0]["code"] == "invalid_json"
    assert response.json()["writes_performed"] is False
    assert client.get("/api/strategies/assignment-draft-validation").status_code == 405
    assert client.put("/api/strategies/assignment-draft-validation", json={}).status_code == 405
    assert client.delete("/api/strategies/assignment-draft-validation").status_code == 405
