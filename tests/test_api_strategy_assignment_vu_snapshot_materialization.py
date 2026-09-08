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


def test_vu_materialization_contract_advertises_atomic_operation(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.get(
        "/api/strategies/assignment-vu-snapshot-materialization-contract"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["operation"]["schema_version"] == (
        "ims.strategy-assignment-vu-snapshot-materialization.v1"
    )
    assert payload["operation"]["state_provenance_validation_required"] is True
    assert payload["operation"]["snapshot_loader_invocation_enabled"] is True
    assert payload["operation"]["partial_results_allowed"] is False
    assert payload["operation"]["execution_enabled"] is False


def test_vu_materialization_endpoint_returns_snapshot_without_execution(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/strategies/assignment-vu-snapshot-materialization",
        json=_request(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["input_valid"] is True
    assert payload["materialization_complete"] is True
    assert payload["snapshot_count"] == 1
    assert payload["snapshot_loader_invocation_count"] == 1
    assert payload["snapshots"][0]["snapshot_type"] == (
        "VURandomUniformRuleSnapshot"
    )
    assert payload["partial_results_returned"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_ready"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_vu_materialization_endpoint_rejects_invalid_input_and_json(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-vu-snapshot-materialization"
    request = _request()
    request["state"]["period_state"]["interest_rate"] = 0.03

    response = client.post(endpoint, json=request)
    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["input_valid"] is False
    assert payload["snapshot_count"] == 0
    assert payload["snapshot_loader_invocation_count"] == 0
    assert payload["issues"][0]["code"] == "period_state_mismatch"
    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
