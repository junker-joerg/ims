import importlib
import json
import sqlite3

from starlette.testclient import TestClient

from ims.api.app import APP_VERSION, create_app
from ims.api.metadata_repository import build_seeded_metadata_repository
from ims.api.run_control_queue import enqueue_run_control_request, initialize_run_control_queue


def test_health_endpoint_reports_backend_ready(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ims-workbench-api",
        "version": APP_VERSION,
        "frontend_available": False,
    }


def test_version_endpoint_reports_workbench_version(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/version")

    assert response.status_code == 200
    assert response.json()["name"] == "IMS Workbench"
    assert response.json()["version"] == APP_VERSION


def test_root_serves_built_frontend_when_available(tmp_path):
    index_file = tmp_path / "index.html"
    index_file.write_text("<!doctype html><title>IMS Workbench</title>", encoding="utf-8")
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "IMS Workbench" in response.text


def test_scenario_metadata_endpoint_is_adapter_only(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/scenarios")

    assert response.status_code == 200
    payload = response.json()
    scenarios = payload["items"]
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["generated_at"] == "2026-05-27T00:00:00Z"
    assert scenarios[0]["id"] == "agrsich-reference-window"
    assert scenarios[0]["display_name"] == "Agrsich Referenzfenster"
    assert scenarios[0]["source"]["path"] == "tests/fixtures"
    assert "Vollgleichheit" in scenarios[0]["validation"]["claim"]


def test_scenario_metadata_detail_endpoint_reads_by_id(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/scenarios/agrsich-reference-window")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "agrsich-reference-window"
    assert payload["display_name"] == "Agrsich Referenzfenster"
    assert payload["validation"]["status"] == "validated"


def test_fastapi_app_starts_with_detail_route_annotations(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/scenarios/agrsich-reference-window")

    assert response.status_code == 200
    assert response.json()["id"] == "agrsich-reference-window"


def test_scenario_metadata_detail_endpoint_returns_stable_404(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/scenarios/missing-scenario")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "metadata_not_found",
            "resource": "scenario",
            "id": "missing-scenario",
            "message": "scenario metadata not found",
        }
    }


def test_run_metadata_endpoint_has_no_execution_control(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/runs")

    assert response.status_code == 200
    payload = response.json()
    runs = payload["items"]
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert runs[0]["id"] == "baseline-python-tests"
    assert runs[0]["execution_enabled"] is False
    assert runs[1]["period_window"] == "keine Simulation"
    assert runs[1]["execution_enabled"] is False


def test_run_metadata_detail_endpoint_reads_by_id(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/runs/baseline-python-tests")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "baseline-python-tests"
    assert payload["scenario_id"] == "agrsich-reference-window"
    assert payload["execution_enabled"] is False


def test_run_metadata_detail_endpoint_returns_stable_404(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/runs/missing-run")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "metadata_not_found",
            "resource": "run",
            "id": "missing-run",
            "message": "run metadata not found",
        }
    }


def test_api_can_read_metadata_from_sqlite_repository(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/scenarios")

    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == "agrsich-reference-window"


def test_metadata_capabilities_keep_write_paths_disabled(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/metadata/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["writes"]["scenario_metadata"]["enabled"] is False
    assert payload["writes"]["run_metadata"]["enabled"] is False
    assert payload["simulation_execution"]["enabled"] is False


def test_metadata_consistency_endpoint_keeps_readonly_boundaries_visible(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/metadata/consistency")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["scenario_count"] == 2
    assert payload["run_count"] == 2
    assert payload["runs_with_known_scenario"] == 2
    assert payload["runs_with_missing_scenario"] == []
    assert payload["runs_with_execution_enabled"] == []
    assert payload["writes_enabled"] is False
    assert payload["simulation_enabled"] is False


def test_run_control_queue_overview_reports_in_memory_boundary(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/run-control/queue")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_queue_overview"
    assert payload["queue_count"] == 0
    assert payload["entries"] == []
    assert payload["issues"][0]["code"] == "run_control_queue_not_configured"
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["execution_performed"] is False


def test_run_control_queue_action_plan_reports_in_memory_boundary(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/run-control/queue/action-plan")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "warning"
    assert payload["mode"] == "run_control_queue_action_plan"
    assert payload["queue_count"] == 0
    assert payload["actions"] == []
    assert payload["issues"][0]["code"] == "run_control_queue_action_plan_unavailable"
    assert "explicit SQLite metadata source" in payload["issues"][0]["message"]
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_core_diagnostics_bridge_reports_in_memory_boundary(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/run-control/core-diagnostics-bridge")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "warning"
    assert payload["mode"] == "run_control_core_diagnostics_bridge"
    assert payload["queue_action_plan_mode"] == "run_control_queue_action_plan"
    assert payload["core_validation_mode"] == "ims_core_validation_overview"
    assert payload["queue_count"] == 0
    assert payload["action_count"] == 0
    assert payload["period_plan_count"] == 2
    assert payload["period_count"] == 8
    assert payload["legacy_reference_count"] == 19
    assert payload["execution_summary_available"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["issues"][0]["code"] == "run_control_queue_action_plan_unavailable"
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_queue_enqueue_requires_explicit_sqlite_source(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.post(
        "/api/run-control/queue",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "requested_by": "local-test",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": False,
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["mode"] == "run_control_queue_enqueue"
    assert "explicit SQLite metadata source" in payload["message"]
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_queue_enqueue_endpoint_writes_only_queue_metadata(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.post(
        "/api/run-control/queue",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "requested_by": "local-test",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": False,
        },
    )
    overview = client.get("/api/run-control/queue")
    detail = client.get("/api/run-control/queue/baseline-python-tests")

    assert response.status_code == 201
    payload = response.json()
    assert payload["mode"] == "run_control_queue_enqueue"
    assert payload["entry"]["queue_id"] == "baseline-python-tests"
    assert payload["entry"]["request"]["scenario_id"] == "agrsich-reference-window"
    assert payload["entry"]["execution_enabled"] is False
    assert payload["entry"]["execution_performed"] is False
    assert payload["dry_run"]["status"] == "ok"
    assert payload["writes_performed"] is True
    assert payload["execution_enabled"] is False
    assert payload["execution_performed"] is False
    assert overview.status_code == 200
    assert overview.json()["queue_count"] == 1
    assert overview.json()["entries"][0]["queue_id"] == "baseline-python-tests"
    assert overview.json()["writes_enabled"] is False
    assert overview.json()["execution_performed"] is False
    assert detail.status_code == 200
    assert detail.json()["entry"]["queue_id"] == "baseline-python-tests"
    assert detail.json()["execution_performed"] is False


def test_run_control_queue_action_plan_endpoint_reads_enqueued_queue(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)
    client.post(
        "/api/run-control/queue",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "requested_by": "local-test",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": False,
        },
    )

    response = client.get("/api/run-control/queue/action-plan")
    filtered = client.get("/api/run-control/queue/action-plan?queue_id=baseline-python-tests")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_queue_action_plan"
    assert payload["queue_count"] == 1
    assert payload["actions"][0]["queue_id"] == "baseline-python-tests"
    assert payload["actions"][0]["next_action"] == "run_preflight"
    assert payload["actions"][0]["execution_allowed"] is False
    assert payload["actions"][0]["writes_performed"] is False
    assert payload["actions"][0]["execution_performed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert filtered.status_code == 200
    assert filtered.json()["queue_id"] == "baseline-python-tests"
    assert filtered.json()["actions"][0]["next_action_label"] == "Lokalen Preflight ausfuehren"


def test_run_control_core_diagnostics_bridge_endpoint_reads_enqueued_queue(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)
    client.post(
        "/api/run-control/queue",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "requested_by": "local-test",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": False,
        },
    )

    response = client.get("/api/run-control/core-diagnostics-bridge")
    filtered = client.get("/api/run-control/core-diagnostics-bridge?queue_id=baseline-python-tests")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "warning"
    assert payload["mode"] == "run_control_core_diagnostics_bridge"
    assert payload["queue_count"] == 1
    assert payload["action_count"] == 1
    assert payload["period_plan_count"] == 2
    assert payload["legacy_reference_count"] == 19
    assert payload["actions"][0]["queue_id"] == "baseline-python-tests"
    assert payload["actions"][0]["queue_next_action"] == "run_preflight"
    assert payload["actions"][0]["bridge_next_action"] == "resolve_core_validation_blockers"
    assert "core_validation_await_historical_reference" in payload["actions"][0]["blocked_by"]
    assert payload["actions"][0]["execution_allowed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert filtered.status_code == 200
    assert filtered.json()["action_count"] == 1
    assert filtered.json()["actions"][0]["queue_id"] == "baseline-python-tests"


def test_run_control_queue_enqueue_endpoint_rejects_execution_enabled(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.post(
        "/api/run-control/queue",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "requested_by": "local-test",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": True,
        },
    )
    overview = client.get("/api/run-control/queue")

    assert response.status_code == 400
    payload = response.json()
    assert payload["mode"] == "run_control_queue_enqueue"
    assert "execution_enabled=true is forbidden" in payload["message"]
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert overview.json()["queue_count"] == 0


def test_run_control_queue_enqueue_endpoint_rejects_failed_dry_run(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.post(
        "/api/run-control/queue",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "metadata-only-local",
            "requested_by": "local-test",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": False,
        },
    )
    overview = client.get("/api/run-control/queue")

    assert response.status_code == 400
    payload = response.json()
    assert payload["mode"] == "run_control_queue_enqueue"
    assert payload["message"] == "run control queue enqueue requires a passing dry-run"
    assert "scenario_id does not match" in payload["issues"][0]
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert overview.json()["queue_count"] == 0


def test_run_control_request_contract_endpoint_is_readonly(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/run-control/request-contract")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_request_contract"
    assert payload["example_request"]["execution_enabled"] is False
    assert "run_id" in payload["required_fields"]
    assert "metadata_db" in payload["optional_fields"]
    assert "execution_enabled=true" in payload["forbidden_fields"]
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_dry_run_contract_endpoint_is_disabled_and_readonly(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/run-control/dry-run-contract")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_dry_run_contract"
    assert "request_body" in payload["expected_inputs"]
    assert "run_id" in payload["expected_inputs"]
    assert "run_control_request_contract_visible" in payload["required_preconditions"]
    assert "run_control_dry_run_endpoint_visible" in payload["required_preconditions"]
    assert "http_post" not in payload["forbidden_boundaries"]
    assert payload["http_enabled"] is True
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_dry_run_endpoint_validates_request_without_execution(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.post(
        "/api/run-control/dry-run",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "requested_by": "local-test",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_dry_run"
    assert payload["request_accepted"] is True
    assert payload["preflight_passed"] is True
    assert payload["scenario_matches_request"] is True
    assert payload["dry_run_allowed"] is False
    assert payload["preflight"]["mode"] == "run_control_preflight"
    assert payload["preflight"]["execution_allowed"] is False
    assert payload["issues"] == []
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_dry_run_endpoint_rejects_execution_enabled(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.post(
        "/api/run-control/dry-run",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "requested_by": "local-test",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": True,
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["mode"] == "run_control_dry_run"
    assert "execution_enabled=true is forbidden" in payload["message"]
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_dry_run_endpoint_reports_scenario_mismatch_without_execution(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.post(
        "/api/run-control/dry-run",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "metadata-only-local",
            "requested_by": "local-test",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["request_accepted"] is True
    assert payload["preflight_passed"] is True
    assert payload["scenario_matches_request"] is False
    assert payload["dry_run_allowed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_core_validation_overview_endpoint_is_readonly_contract(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/core-validation/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "ims_core_validation_overview"
    assert payload["plan_count"] == 2
    assert payload["legacy_reference_count"] == 19
    assert payload["execution_summary_available"] is False
    assert payload["execution_summary_contract"]["mode"] == "explicit_multi_period_execution_summary_contract"
    assert payload["execution_summary_contract"]["overview_starts_runner"] is False
    assert payload["execution_summary_contract"]["overview_accepts_summary_input"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_preflight_endpoint_reads_selected_run(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/run-control/preflight/baseline-python-tests")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_preflight"
    assert payload["run_id"] == "baseline-python-tests"
    assert payload["scenario_id"] == "agrsich-reference-window"
    assert payload["run_found"] is True
    assert payload["scenario_found"] is True
    assert payload["execution_enabled"] is False
    assert payload["execution_allowed"] is False
    assert payload["issues"] == []
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_run_control_preflight_endpoint_reports_missing_run_without_execution(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/run-control/preflight/missing-run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["mode"] == "run_control_preflight"
    assert payload["run_id"] == "missing-run"
    assert payload["run_found"] is False
    assert payload["scenario_found"] is False
    assert payload["execution_allowed"] is False
    assert payload["issues"] == ["run metadata not found: missing-run"]
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_run_control_queue_overview_reads_injected_sqlite_queue(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
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
    repository = build_seeded_metadata_repository(db_path)
    initialize_run_control_queue(db_path)
    enqueue_run_control_request(request_path, db_path=db_path)
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/run-control/queue")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["queue_count"] == 1
    assert payload["entries"][0]["queue_id"] == "baseline-python-tests"
    assert payload["entries"][0]["request"]["scenario_id"] == "agrsich-reference-window"
    assert payload["entries"][0]["execution_enabled"] is False
    assert payload["entries"][0]["execution_performed"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False


def test_run_control_queue_overview_reports_malformed_queue_schema(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute("CREATE TABLE run_control_queue (queue_id TEXT PRIMARY KEY)")
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/run-control/queue")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "warning"
    assert payload["queue_count"] == 0
    assert payload["entries"] == []
    assert payload["issues"][0]["code"] == "run_control_queue_unreadable"
    assert payload["issues"][0]["severity"] == "warning"
    assert "no such column" in payload["issues"][0]["message"]
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["execution_performed"] is False


def test_run_control_queue_detail_reads_injected_sqlite_queue_entry(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
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
    repository = build_seeded_metadata_repository(db_path)
    initialize_run_control_queue(db_path)
    enqueue_run_control_request(request_path, db_path=db_path)
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/run-control/queue/baseline-python-tests")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "run_control_queue_detail"
    assert payload["entry"]["queue_id"] == "baseline-python-tests"
    assert payload["entry"]["request"]["requested_by"] == "local-test"
    assert payload["entry"]["request"]["execution_enabled"] is False
    assert payload["entry"]["execution_performed"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["execution_performed"] is False


def test_run_control_queue_detail_returns_stable_404(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/run-control/queue/missing-queue-entry")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "metadata_not_found",
            "resource": "run_control_queue",
            "id": "missing-queue-entry",
            "message": "run_control_queue metadata not found",
        }
    }


def test_metadata_source_reports_in_memory_default(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/metadata/source")

    assert response.status_code == 200
    assert response.json() == {
        "schema_version": "ims.workbench.metadata.v1",
        "storage_kind": "memory",
        "configured": False,
        "injected": False,
        "writes_enabled": False,
        "execution_enabled": False,
    }


def test_metadata_source_reports_explicit_sqlite_path(tmp_path, monkeypatch):
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))

    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)
    response = client.get("/api/metadata/source")

    assert response.status_code == 200
    assert response.json() == {
        "schema_version": "ims.workbench.metadata.v1",
        "storage_kind": "sqlite",
        "configured": True,
        "injected": False,
        "path": str(db_path.resolve()),
        "writes_enabled": False,
        "execution_enabled": False,
    }
    assert db_path.exists() is False


def test_metadata_source_reports_injected_sqlite_repository(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/metadata/source")

    assert response.status_code == 200
    assert response.json() == {
        "schema_version": "ims.workbench.metadata.v1",
        "storage_kind": "sqlite",
        "configured": True,
        "injected": True,
        "path": str(db_path.resolve()),
        "writes_enabled": False,
        "execution_enabled": False,
    }


def test_importing_default_app_does_not_create_metadata_db(tmp_path, monkeypatch):
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))

    import ims.api.app as app_module

    importlib.reload(app_module)

    assert db_path.exists() is False
    monkeypatch.delenv("IMS_METADATA_DB")
    importlib.reload(app_module)
