from pathlib import Path

from starlette.testclient import TestClient

from ims.api.app import APP_VERSION, create_app
from ims.api.metadata_import_cli import check_metadata_roundtrip
from ims.api.metadata_repository import build_seeded_metadata_repository
from ims.api.run_control_preflight import preflight_run_control
from ims.api.workbench_cli_overview import build_workbench_cli_overview
from ims.api.workbench_readiness import build_workbench_readiness


def test_workbench_api_metadata_smoke(tmp_path: Path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    health = client.get("/api/health")
    version = client.get("/api/version")
    scenarios = client.get("/api/scenarios")
    runs = client.get("/api/runs")
    source = client.get("/api/metadata/source")
    capabilities = client.get("/api/metadata/capabilities")
    consistency = client.get("/api/metadata/consistency")
    core_validation = client.get("/api/core-validation/overview")
    carryover_probe_contract = client.get("/api/core-validation/carryover-probe-contract")
    adapter_result_contract = client.get("/api/run-control/adapter-result-contract")
    adapter_start_contract = client.get("/api/run-control/adapter-start-contract")
    run_control_queue = client.get("/api/run-control/queue")
    run_control_dry_run = client.post(
        "/api/run-control/dry-run",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "requested_by": "local-smoke",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": False,
        },
    )
    run_control_queue_enqueue = client.post(
        "/api/run-control/queue",
        json={
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "requested_by": "local-smoke",
            "created_at": "2026-05-27T00:00:00Z",
            "execution_enabled": False,
        },
    )
    run_control_queue_after_enqueue = client.get("/api/run-control/queue")
    run_control_queue_action_plan = client.get("/api/run-control/queue/action-plan")
    missing_queue_entry = client.get("/api/run-control/queue/missing-queue-entry")
    missing = client.get("/api/scenarios/missing-scenario")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["frontend_available"] is False
    assert version.status_code == 200
    assert version.json()["version"] == APP_VERSION
    assert scenarios.status_code == 200
    assert runs.status_code == 200
    assert source.status_code == 200
    assert source.json()["storage_kind"] == "sqlite"
    assert source.json()["injected"] is True
    assert capabilities.status_code == 200
    assert source.json()["writes_enabled"] is False
    assert capabilities.json()["writes"]["scenario_metadata"]["enabled"] is False
    assert capabilities.json()["writes"]["run_metadata"]["enabled"] is False
    assert capabilities.json()["simulation_execution"]["enabled"] is False
    assert consistency.status_code == 200
    assert consistency.json()["status"] == "ok"
    assert consistency.json()["runs_with_missing_scenario"] == []
    assert consistency.json()["runs_with_execution_enabled"] == []
    assert consistency.json()["writes_enabled"] is False
    assert consistency.json()["simulation_enabled"] is False
    assert core_validation.status_code == 200
    assert core_validation.json()["mode"] == "ims_core_validation_overview"
    assert core_validation.json()["execution_summary_contract"]["overview_starts_runner"] is False
    assert core_validation.json()["execution_performed"] is False
    assert carryover_probe_contract.status_code == 200
    assert carryover_probe_contract.json()["mode"] == "core_validation_carryover_probe_api_contract"
    assert carryover_probe_contract.json()["precomputed_probe_required"] is True
    assert carryover_probe_contract.json()["api_starts_probe"] is False
    assert carryover_probe_contract.json()["api_accepts_probe_payload"] is False
    assert carryover_probe_contract.json()["execution_performed"] is False
    assert carryover_probe_contract.json()["simulation_performed"] is False
    assert adapter_result_contract.status_code == 200
    assert adapter_result_contract.json()["mode"] == "run_control_adapter_result_api_contract"
    assert adapter_result_contract.json()["api_accepts_result_payload"] is False
    assert adapter_result_contract.json()["api_starts_adapter"] is False
    assert adapter_result_contract.json()["execution_performed"] is False
    assert adapter_result_contract.json()["simulation_performed"] is False
    assert adapter_start_contract.status_code == 200
    assert adapter_start_contract.json()["mode"] == "run_control_adapter_start_contract"
    assert adapter_start_contract.json()["api_accepts_start_payload"] is False
    assert adapter_start_contract.json()["api_starts_adapter"] is False
    assert adapter_start_contract.json()["ui_start_enabled"] is False
    assert adapter_start_contract.json()["queue_worker_enabled"] is False
    assert adapter_start_contract.json()["execution_performed"] is False
    assert adapter_start_contract.json()["simulation_performed"] is False
    assert run_control_queue.status_code == 200
    assert run_control_queue.json()["mode"] == "run_control_queue_overview"
    assert run_control_queue.json()["writes_enabled"] is False
    assert run_control_queue.json()["execution_enabled"] is False
    assert run_control_queue.json()["execution_performed"] is False
    assert run_control_dry_run.status_code == 200
    assert run_control_dry_run.json()["mode"] == "run_control_dry_run"
    assert run_control_dry_run.json()["dry_run_allowed"] is False
    assert run_control_dry_run.json()["writes_performed"] is False
    assert run_control_dry_run.json()["execution_performed"] is False
    assert run_control_queue_enqueue.status_code == 201
    assert run_control_queue_enqueue.json()["mode"] == "run_control_queue_enqueue"
    assert run_control_queue_enqueue.json()["entry"]["execution_performed"] is False
    assert run_control_queue_enqueue.json()["writes_performed"] is True
    assert run_control_queue_enqueue.json()["execution_performed"] is False
    assert run_control_queue_after_enqueue.status_code == 200
    assert run_control_queue_after_enqueue.json()["queue_count"] == 1
    assert run_control_queue_after_enqueue.json()["execution_performed"] is False
    assert run_control_queue_action_plan.status_code == 200
    assert run_control_queue_action_plan.json()["mode"] == "run_control_queue_action_plan"
    assert run_control_queue_action_plan.json()["actions"][0]["next_action"] == "run_preflight"
    assert run_control_queue_action_plan.json()["actions"][0]["execution_performed"] is False
    assert run_control_queue_action_plan.json()["writes_performed"] is False
    assert run_control_queue_action_plan.json()["execution_performed"] is False
    assert missing_queue_entry.status_code == 404
    assert missing_queue_entry.json()["error"]["resource"] == "run_control_queue"

    scenario_id = scenarios.json()["items"][0]["id"]
    run_id = runs.json()["items"][0]["id"]
    assert scenarios.json()["items"][0]["display_name"]
    assert scenarios.json()["items"][0]["domain_scope"]
    assert scenarios.json()["items"][0]["source"]["label"]
    assert scenarios.json()["items"][0]["validation"]["scope"]
    assert scenarios.json()["items"][0]["updated_at"]
    assert runs.json()["items"][0]["display_name"]
    assert runs.json()["items"][0]["scenario_id"]
    assert runs.json()["items"][0]["period_window"]
    assert runs.json()["items"][0]["source"]["label"]
    assert runs.json()["items"][0]["execution_enabled"] is False
    scenario_detail = client.get(f"/api/scenarios/{scenario_id}")
    run_detail = client.get(f"/api/runs/{run_id}")

    assert scenario_detail.status_code == 200
    assert scenario_detail.json()["id"] == scenario_id
    assert run_detail.status_code == 200
    assert run_detail.json()["id"] == run_id
    assert run_detail.json()["execution_enabled"] is False
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "metadata_not_found"


def test_workbench_static_frontend_smoke(tmp_path: Path):
    dist_dir = tmp_path / "dist"
    assets_dir = dist_dir / "assets"
    assets_dir.mkdir(parents=True)
    (dist_dir / "index.html").write_text(
        '<!doctype html><title>IMS Workbench</title><script type="module" src="/assets/app.js"></script>',
        encoding="utf-8",
    )
    (assets_dir / "app.js").write_text("window.__IMS_WORKBENCH_SMOKE__ = true;", encoding="utf-8")
    app = create_app(frontend_dist=dist_dir)
    client = TestClient(app)

    root = client.get("/")
    asset = client.get("/assets/app.js")
    health = client.get("/api/health")

    assert root.status_code == 200
    assert "IMS Workbench" in root.text
    assert asset.status_code == 200
    assert "__IMS_WORKBENCH_SMOKE__" in asset.text
    assert health.json()["frontend_available"] is True


def test_workbench_v1_readiness_smoke_keeps_local_boundaries(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    frontend_dist = tmp_path / "dist"
    frontend_dist.mkdir()
    (frontend_dist / "index.html").write_text("<!doctype html><title>IMS Workbench</title>", encoding="utf-8")

    readiness = build_workbench_readiness(
        frontend_dist=frontend_dist,
        run_id="baseline-python-tests",
    ).to_dict()
    overview = build_workbench_cli_overview().to_dict()
    roundtrip = check_metadata_roundtrip().to_dict()
    preflight = preflight_run_control("baseline-python-tests").to_dict()

    assert readiness["status"] == "ok"
    assert readiness["backend_ready"] is True
    assert readiness["frontend_ready"] is True
    assert readiness["metadata_ready"] is True
    assert readiness["cli_ready"] is True
    assert readiness["run_control_ready"] is True
    assert readiness["run_control_queue_ready"] is True
    assert readiness["writes_enabled"] is False
    assert readiness["execution_enabled"] is False
    assert [check["name"] for check in readiness["checks"]] == [
        "backend",
        "frontend",
        "metadata",
        "cli",
        "run_control",
        "run_control_queue",
    ]

    assert overview["boundaries"]["writes_enabled"] is False
    assert overview["boundaries"]["execution_enabled"] is False
    assert overview["boundaries"]["starts_server"] is False
    assert overview["boundaries"]["creates_sqlite_file"] is False
    assert overview["boundaries"]["write_commands"] == [
        "metadata_import_cli export",
        "workbench_bundle_build",
        "run_control_queue init",
        "run_control_queue enqueue",
        "metadata_import_cli import --db",
        "workbench_portable_staging",
    ]
    assert all(command["starts_server"] is False for command in overview["commands"])
    assert all(command["starts_simulation"] is False for command in overview["commands"])

    assert roundtrip["import_valid"] is True
    assert roundtrip["write_contract_valid"] is True
    assert roundtrip["writes_performed"] is False
    assert roundtrip["execution_performed"] is False
    assert preflight["run_found"] is True
    assert preflight["scenario_found"] is True
    assert preflight["execution_allowed"] is False
    assert preflight["writes_performed"] is False
    assert preflight["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_workbench_frontend_source_exposes_import_preview_without_upload():
    source = (Path(__file__).resolve().parent.parent / "frontend" / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "Importvorschau" in source
    assert "Betriebsdiagnose" in source
    assert "Metadaten-Konsistenz" in source
    assert "Auswahlzusammenfassung" in source
    assert "Szenario-Uebersicht" in source
    assert "Run-Uebersicht" in source
    assert "Run-Control-Uebersicht" in source
    assert "Run-Control-Queue-Detail" in source
    assert "Run-Control-Dry-Run-Vertrag" in source
    assert "Run-Control-Ausfuehrungsflow" in source
    assert "Run-Control-Kernblick-Bruecke" in source
    assert "Adapter-Resultat-Vertrag" in source
    assert 'data-testid="run-control-demo-dry-run-button"' in source
    assert 'data-testid="run-control-demo-queue-button"' in source
    assert 'data-testid="run-control-demo-action-plan"' in source
    assert 'data-testid="run-control-execution-flow"' in source
    assert 'data-testid="run-control-core-bridge"' in source
    assert 'data-testid="carryover-probe-contract"' in source
    assert 'data-testid="adapter-result-contract"' in source
    assert "Szenariofilter" in source
    assert "Runfilter" in source
    assert "/api/metadata/consistency" in source
    assert "/api/core-validation/overview" in source
    assert "/api/core-validation/carryover-probe-contract" in source
    assert "/api/run-control/adapter-result-contract" in source
    assert "/api/run-control/adapter-start-contract" in source
    assert "/api/run-control/queue" in source
    assert "/api/run-control/queue/action-plan" in source
    assert "/api/run-control/queue/${encodeURIComponent(selectedQueueId)}" in source
    assert "/api/run-control/dry-run-contract" in source
    assert "/api/run-control/dry-run" in source
    assert "/api/run-control/core-diagnostics-bridge" in source
    assert "Dry-Run pruefen" in source
    assert "Queue vormerken" in source
    assert "Preflight -> explizite Freigabe -> Ausfuehren" in source
    assert "inspect_persisted_result" in source
    assert "Import aktuell nur ueber Python-Adapter" in source
    assert "Preview lokal per CLI ohne Schreiben" in source
    assert "Snapshot lokal per CLI ohne Browser-Export" in source
    assert "Startplan lokal per CLI nur beschreibend" in source
    assert "CLI-Uebersicht lokal per CLI ohne Seiteneffekte" in source
    assert "Schreibvertrag lokal per CLI nur beschreibend" in source
    assert "Schreibvertragspruefung lokal per CLI ohne Import" in source
    assert "Run-Control-Vertrag lokal per CLI ohne Ausfuehrung" in source
    assert "Run-Control-Preflight lokal per CLI ohne Ausfuehrung" in source
    assert "Run-Control-Dry-Run per API pruefend ohne Ausfuehrung" in source
    assert "Export lokal per CLI nur mit explizitem Zielpfad" in source
    assert "Roundtrip lokal per CLI ohne Schreiben" in source
    assert "Dry-Run lokal per CLI ohne Import" in source
    assert "Importbericht lokal per CLI nach explizitem Schreiben" in source
    assert "Readiness lokal per CLI ohne Serverstart" in source
    assert "v1-Readiness als lokaler Abschluss-Smoke" in source
    assert "Browser schreibt keine Metadaten" in source
    assert "Metadatenquelle" in source
    assert "lokal per CLI" in source
    assert "scenario-overview-row" in source
    assert "run-overview-row" in source
    assert "filteredRuns.map" in source
    assert "Auswahl durch Filter aktuell nicht in den Listen sichtbar" in source
    assert 'type="file"' not in source
