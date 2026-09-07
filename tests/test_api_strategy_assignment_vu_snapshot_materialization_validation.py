import json
from pathlib import Path

from fastapi.testclient import TestClient

from ims.api.app import create_app


FIXTURES = Path(__file__).parent / "fixtures"


def _request() -> dict[str, object]:
    return {
        "schema_version": (
            "ims.strategy-assignment-vu-snapshot-materialization-input.v1"
        ),
        "threshold_source_policy": "insurer-aspiration-profile-v1",
        "draw_source_policy": "explicit-context-draws-v1",
        "fallback_policy": "reject-loader-and-runner-fallbacks-v1",
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


def test_vu_materialization_validation_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = (
        "/api/strategies/assignment-vu-snapshot-materialization-validation-contract"
    )

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-assignment-vu-snapshot-materialization-validation.v1"
    )
    assert payload["validated_strategy_count"] == 10
    assert payload["fallback_policy"]["allowed_fallbacks"] == []
    assert payload["snapshot_loader_invocation_enabled"] is False
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["execution_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_vu_materialization_validation_endpoint_accepts_explicit_context(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/assignment-vu-snapshot-materialization-validation",
        json=_request(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["valid"] is True
    assert payload["validated_vu_entry_count"] == 1
    assert payload["threshold_values_cross_checked_against_actor_state"] is False
    assert payload["snapshot_loader_invocation_performed"] is False
    assert payload["snapshots_created"] is False
    assert payload["simulation_performed"] is False


def test_vu_materialization_validation_endpoint_rejects_fallback_and_invalid_json(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-vu-snapshot-materialization-validation"
    request = _request()
    request["context"]["entries"][0]["values"]["random_draws"] = None

    response = client.post(endpoint, json=request)
    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["issues"][0]["code"] == "fallback_not_allowed"
    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
