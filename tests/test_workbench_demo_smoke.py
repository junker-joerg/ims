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
