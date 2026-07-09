import json
from pathlib import Path

from ims.api.metadata_repository import build_seeded_metadata_repository
from ims.api.run_control_core_diagnostics_bridge import (
    RunControlCoreDiagnosticsBridgeAction,
    RunControlCoreDiagnosticsBridgeIssue,
    RunControlCoreDiagnosticsBridgeResult,
    build_run_control_core_diagnostics_bridge,
)
from ims.api.run_control_queue import enqueue_run_control_request
from ims.api.run_control_queue_action_plan import build_run_control_queue_action_plan
from ims.engine.core_validation_overview import build_core_validation_overview


FIXTURE_DIR = Path("tests/fixtures")
LEGACY_FIXTURE = FIXTURE_DIR / "legacy_validation_bundle.json"
VU14_PLAN = FIXTURE_DIR / "replay_vu14_period_plan.json"
VUSK1_PLAN = FIXTURE_DIR / "replay_vusk1_period_plan.json"


def _write_request(tmp_path: Path) -> Path:
    request_path = tmp_path / "run_control_request.json"
    request_path.write_text(
        json.dumps(
            {
                "run_id": "baseline-python-tests",
                "scenario_id": "agrsich-reference-window",
                "requested_by": "local-test",
                "created_at": "2026-05-27T00:00:00Z",
                "execution_enabled": False,
            }
        ),
        encoding="utf-8",
    )
    return request_path


def _queue_payload(next_action: str = "run_preflight", blocked_by: list[str] | None = None) -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "run_control_queue_action_plan",
        "queue_count": 1,
        "actions": [
            {
                "queue_id": "baseline-python-tests",
                "run_id": "baseline-python-tests",
                "scenario_id": "agrsich-reference-window",
                "queue_status": "planned",
                "next_action": next_action,
                "next_action_label": "Lokalen Preflight ausfuehren",
                "blocked_by": blocked_by or [],
                "execution_allowed": False,
                "writes_performed": False,
                "execution_performed": False,
            }
        ],
        "issues": [],
        "writes_performed": False,
        "execution_performed": False,
    }


def _core_payload(
    *,
    status: str = "ok",
    next_validation_actions: list[str] | None = None,
    execution_summary_available: bool = True,
) -> dict[str, object]:
    return {
        "status": status,
        "mode": "ims_core_validation_overview",
        "plan_count": 2,
        "period_count": 8,
        "global_periods": [1, 2, 3, 4, 101, 102, 103, 104],
        "legacy_reference_count": 19,
        "next_validation_actions": next_validation_actions or [],
        "execution_summary_available": execution_summary_available,
        "execution_summary_next_action": "await_precomputed_execution_summary"
        if not execution_summary_available
        else "summary_available",
        "issues": [],
        "writes_performed": False,
        "execution_performed": False,
    }


def test_bridge_combines_existing_readonly_queue_and_core_payloads(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    enqueue_run_control_request(_write_request(tmp_path), db_path=db_path)
    queue_plan = build_run_control_queue_action_plan(db_path)
    core_overview = build_core_validation_overview(
        legacy_fixture_path=LEGACY_FIXTURE,
        period_plan_paths=[VU14_PLAN, VUSK1_PLAN],
    )

    result = build_run_control_core_diagnostics_bridge(queue_plan, core_overview)
    payload = result.to_dict()

    assert isinstance(result, RunControlCoreDiagnosticsBridgeResult)
    assert payload["status"] == "warning"
    assert payload["mode"] == "run_control_core_diagnostics_bridge"
    assert payload["queue_action_plan_mode"] == "run_control_queue_action_plan"
    assert payload["core_validation_mode"] == "ims_core_validation_overview"
    assert payload["queue_count"] == 1
    assert payload["action_count"] == 1
    assert payload["period_plan_count"] == 2
    assert payload["period_count"] == 8
    assert payload["global_periods"] == [1, 2, 3, 4, 101, 102, 103, 104]
    assert payload["legacy_reference_count"] == 19
    assert payload["execution_summary_available"] is False
    assert payload["execution_summary_next_action"] == "await_precomputed_execution_summary"
    assert payload["actions"][0]["queue_next_action"] == "run_preflight"
    assert payload["actions"][0]["bridge_next_action"] == "resolve_core_validation_blockers"
    assert "core_validation_await_historical_reference" in payload["actions"][0]["blocked_by"]
    assert payload["actions"][0]["execution_allowed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert any(issue["code"] == "core_validation_await_historical_reference" for issue in payload["issues"])
    assert RunControlCoreDiagnosticsBridgeAction is not None
    assert RunControlCoreDiagnosticsBridgeIssue is not None


def test_bridge_waits_for_precomputed_summary_before_release() -> None:
    payload = build_run_control_core_diagnostics_bridge(
        _queue_payload(next_action="await_execution_release"),
        _core_payload(execution_summary_available=False),
    ).to_dict()

    assert payload["status"] == "warning"
    assert payload["actions"][0]["bridge_next_action"] == "await_precomputed_execution_summary"
    assert payload["actions"][0]["blocked_by"] == ["execution_summary_missing"]
    assert payload["actions"][0]["execution_performed"] is False
    assert payload["issues"][0]["code"] == "execution_summary_missing"


def test_bridge_preserves_queue_blockers_without_core_inference() -> None:
    payload = build_run_control_core_diagnostics_bridge(
        _queue_payload(next_action="resolve_blockers", blocked_by=["run_control_preflight_failed"]),
        _core_payload(),
    ).to_dict()

    assert payload["actions"][0]["bridge_next_action"] == "resolve_blockers"
    assert payload["actions"][0]["blocked_by"] == ["run_control_preflight_failed"]
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_bridge_can_pass_through_release_hint_when_core_payload_is_clear() -> None:
    payload = build_run_control_core_diagnostics_bridge(
        _queue_payload(next_action="await_execution_release"),
        _core_payload(execution_summary_available=True),
    ).to_dict()

    assert payload["status"] == "ok"
    assert payload["actions"][0]["bridge_next_action"] == "await_execution_release"
    assert payload["actions"][0]["blocked_by"] == []
    assert payload["actions"][0]["execution_allowed"] is False
