import json
from pathlib import Path

from fastapi.testclient import TestClient

from ims.api.app import create_app


FIXTURES = Path(__file__).parent / "fixtures"


def _request() -> dict[str, object]:
    draft = json.loads(
        (FIXTURES / "strategy_assignment_draft_v1.json").read_text(
            encoding="utf-8"
        )
    )
    context = json.loads(
        (FIXTURES / "strategy_assignment_snapshot_context_v1.json").read_text(
            encoding="utf-8"
        )
    )
    insurer_context = next(
        entry for entry in context["entries"] if entry["actor_type"] == "insurer"
    )
    return {
        "input": {
            "schema_version": (
                "ims.strategy-assignment-vu-snapshot-materialization-input.v1"
            ),
            "threshold_source_policy": "insurer-aspiration-profile-v1",
            "draw_source_policy": "explicit-context-draws-v1",
            "fallback_policy": "reject-loader-and-runner-fallbacks-v1",
            "draft": draft,
            "context": context,
        },
        "state": {
            "schema_version": "ims.strategy-assignment-vu-snapshot-state.v1",
            "input_schema_version": (
                "ims.strategy-assignment-vu-snapshot-materialization-input.v1"
            ),
            "base_model": "Vdefmd6",
            "scope": "vu_snapshot_materialization_provenance_state",
            "draft_id": draft["draft_id"],
            "period": context["period"],
            "period_state": {
                "interest_rate": insurer_context["values"]["interest_rate"],
                "change_shock": insurer_context["values"]["change_shock"],
                "active_policyholder_count": 200,
            },
            "entries": [
                {
                    "insurer_id": insurer_context["target_id"],
                    "strategy_id": insurer_context["strategy_id"],
                    "values": {},
                }
            ],
        },
    }


def test_vu_state_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-vu-snapshot-state-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-assignment-vu-snapshot-state-validation.v1"
    )
    assert payload["validated_strategy_count"] == 10
    assert payload["provenance_definition_count"] == 7
    assert payload["contract_issue_count"] == 0
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["execution_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_vu_state_validation_endpoint_accepts_matching_state(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/assignment-vu-snapshot-state-validation",
        json=_request(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["valid"] is True
    assert payload["input_valid"] is True
    assert payload["state_shape_valid"] is True
    assert payload["matched_provenance_check_count"] == 2
    assert payload["draw_values_cross_checked_against_draw_plan"] is False
    assert payload["snapshot_loader_invocation_performed"] is False
    assert payload["snapshots_created"] is False
    assert payload["simulation_performed"] is False


def test_vu_state_validation_endpoint_rejects_mismatch_and_invalid_json(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-vu-snapshot-state-validation"
    request = _request()
    request["state"]["period_state"]["interest_rate"] = 0.03

    response = client.post(endpoint, json=request)
    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["issues"][0]["code"] == "period_state_mismatch"
    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
