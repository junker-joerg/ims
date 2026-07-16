from pathlib import Path

from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.api.metadata_repository import build_seeded_metadata_repository


def test_workbench_demo_smoke_dry_run_queue_and_action_plan_without_execution(tmp_path: Path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)
    request = {
        "run_id": "baseline-python-tests",
        "scenario_id": "agrsich-reference-window",
        "requested_by": "local-demo-smoke",
        "created_at": "2026-05-27T00:00:00Z",
        "execution_enabled": False,
    }

    source = client.get("/api/metadata/source")
    capabilities = client.get("/api/metadata/capabilities")
    dry_run = client.post("/api/run-control/dry-run", json=request)
    queue = client.post("/api/run-control/queue", json=request)
    queue_id = queue.json()["entry"]["queue_id"]
    queue_overview = client.get("/api/run-control/queue")
    action_plan = client.get("/api/run-control/queue/action-plan")
    selected_action_plan = client.get(f"/api/run-control/queue/action-plan?queue_id={queue_id}")
    core_bridge = client.get("/api/run-control/core-diagnostics-bridge")
    selected_core_bridge = client.get(f"/api/run-control/core-diagnostics-bridge?queue_id={queue_id}")
    adapter_start_contract = client.get("/api/run-control/adapter-start-contract")
    execution_result_missing = client.get(f"/api/run-control/execution-result/{queue_id}")
    carryover_probe_contract = client.get("/api/core-validation/carryover-probe-contract")
    adapter_result_contract = client.get("/api/run-control/adapter-result-contract")

    assert source.status_code == 200
    assert source.json()["storage_kind"] == "sqlite"
    assert source.json()["writes_enabled"] is False
    assert capabilities.status_code == 200
    assert capabilities.json()["simulation_execution"]["enabled"] is False

    assert dry_run.status_code == 200
    assert dry_run.json()["mode"] == "run_control_dry_run"
    assert dry_run.json()["writes_performed"] is False
    assert dry_run.json()["execution_performed"] is False

    assert queue.status_code == 201
    assert queue.json()["mode"] == "run_control_queue_enqueue"
    assert queue.json()["entry"]["request"]["run_id"] == "baseline-python-tests"
    assert queue.json()["entry"]["request"]["scenario_id"] == "agrsich-reference-window"
    assert queue.json()["entry"]["execution_enabled"] is False
    assert queue.json()["entry"]["execution_performed"] is False
    assert queue.json()["writes_performed"] is True
    assert queue.json()["execution_performed"] is False

    assert queue_overview.status_code == 200
    assert queue_overview.json()["mode"] == "run_control_queue_overview"
    assert queue_overview.json()["queue_count"] == 1
    assert queue_overview.json()["writes_enabled"] is False
    assert queue_overview.json()["execution_enabled"] is False
    assert queue_overview.json()["execution_performed"] is False

    assert action_plan.status_code == 200
    assert action_plan.json()["mode"] == "run_control_queue_action_plan"
    assert action_plan.json()["queue_count"] == 1
    assert action_plan.json()["actions"][0]["queue_id"] == queue_id
    assert action_plan.json()["actions"][0]["next_action"] == "run_preflight"
    assert action_plan.json()["actions"][0]["execution_allowed"] is False
    assert action_plan.json()["actions"][0]["writes_performed"] is False
    assert action_plan.json()["actions"][0]["execution_performed"] is False
    assert action_plan.json()["writes_performed"] is False
    assert action_plan.json()["execution_performed"] is False

    assert selected_action_plan.status_code == 200
    assert selected_action_plan.json()["queue_count"] == 1
    assert selected_action_plan.json()["actions"][0]["queue_id"] == queue_id
    assert selected_action_plan.json()["actions"][0]["next_action"] == "run_preflight"
    assert selected_action_plan.json()["actions"][0]["execution_allowed"] is False
    assert selected_action_plan.json()["execution_performed"] is False

    assert core_bridge.status_code == 200
    assert core_bridge.json()["mode"] == "run_control_core_diagnostics_bridge"
    assert core_bridge.json()["queue_count"] == 1
    assert core_bridge.json()["action_count"] == 1
    assert core_bridge.json()["actions"][0]["queue_id"] == queue_id
    assert core_bridge.json()["actions"][0]["queue_next_action"] == "run_preflight"
    assert core_bridge.json()["actions"][0]["bridge_next_action"] == "resolve_core_validation_blockers"
    assert core_bridge.json()["actions"][0]["execution_allowed"] is False
    assert core_bridge.json()["actions"][0]["writes_performed"] is False
    assert core_bridge.json()["actions"][0]["execution_performed"] is False
    assert core_bridge.json()["writes_performed"] is False
    assert core_bridge.json()["execution_performed"] is False
    assert core_bridge.json()["execution_summary_next_action"] == "await_precomputed_execution_summary"

    assert selected_core_bridge.status_code == 200
    assert selected_core_bridge.json()["queue_count"] == 1
    assert selected_core_bridge.json()["actions"][0]["queue_id"] == queue_id
    assert selected_core_bridge.json()["actions"][0]["bridge_next_action"] == "resolve_core_validation_blockers"
    assert selected_core_bridge.json()["execution_performed"] is False

    assert adapter_start_contract.status_code == 200
    assert adapter_start_contract.json()["mode"] == "run_control_adapter_start_contract"
    assert adapter_start_contract.json()["planned_start_endpoint"] == "/api/run-control/adapter-start"
    assert adapter_start_contract.json()["api_accepts_start_payload"] is False
    assert adapter_start_contract.json()["api_validates_start_payload"] is False
    assert adapter_start_contract.json()["api_starts_adapter"] is False
    assert adapter_start_contract.json()["ui_start_enabled"] is False
    assert adapter_start_contract.json()["queue_worker_enabled"] is False
    assert adapter_start_contract.json()["execution_performed"] is False
    assert adapter_start_contract.json()["simulation_performed"] is False

    assert execution_result_missing.status_code == 404
    assert execution_result_missing.json()["mode"] == "run_control_execution_result_store_show"
    assert execution_result_missing.json()["status"] == "error"
    assert execution_result_missing.json()["writes_performed"] is False
    assert execution_result_missing.json()["execution_performed"] is False
    assert execution_result_missing.json()["adapter_started"] is False
    assert execution_result_missing.json()["simulation_performed"] is False

    assert carryover_probe_contract.status_code == 200
    assert carryover_probe_contract.json()["mode"] == "core_validation_carryover_probe_api_contract"
    assert carryover_probe_contract.json()["endpoint"] == "/api/core-validation/carryover-probe-contract"
    assert carryover_probe_contract.json()["expected_probe_mode"] == "explicit_transition_carryover_probe"
    assert carryover_probe_contract.json()["precomputed_probe_required"] is True
    assert carryover_probe_contract.json()["api_accepts_probe_payload"] is False
    assert carryover_probe_contract.json()["api_starts_probe"] is False
    assert carryover_probe_contract.json()["ui_enabled"] is False
    assert carryover_probe_contract.json()["writes_performed"] is False
    assert carryover_probe_contract.json()["execution_performed"] is False
    assert carryover_probe_contract.json()["simulation_performed"] is False

    assert adapter_result_contract.status_code == 200
    assert adapter_result_contract.json()["mode"] == "run_control_adapter_result_api_contract"
    assert adapter_result_contract.json()["precomputed_result_required"] is True
    assert adapter_result_contract.json()["api_accepts_result_payload"] is False
    assert adapter_result_contract.json()["api_validates_result_payload"] is False
    assert adapter_result_contract.json()["api_starts_adapter"] is False
    assert adapter_result_contract.json()["execution_performed"] is False
    assert adapter_result_contract.json()["simulation_performed"] is False
