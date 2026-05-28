from pathlib import Path

from starlette.testclient import TestClient

from ims.api.app import APP_VERSION, create_app
from ims.api.metadata_repository import build_seeded_metadata_repository


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


def test_workbench_frontend_source_exposes_import_preview_without_upload():
    source = (Path(__file__).resolve().parent.parent / "frontend" / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "Importvorschau" in source
    assert "Betriebsdiagnose" in source
    assert "Metadaten-Konsistenz" in source
    assert "Auswahlzusammenfassung" in source
    assert "Szenario-Uebersicht" in source
    assert "Run-Uebersicht" in source
    assert "Szenariofilter" in source
    assert "Runfilter" in source
    assert "/api/metadata/consistency" in source
    assert "Import aktuell nur ueber Python-Adapter" in source
    assert "Preview lokal per CLI ohne Schreiben" in source
    assert "Snapshot lokal per CLI ohne Browser-Export" in source
    assert "Startplan lokal per CLI nur beschreibend" in source
    assert "CLI-Uebersicht lokal per CLI ohne Seiteneffekte" in source
    assert "Schreibvertrag lokal per CLI nur beschreibend" in source
    assert "Schreibvertragspruefung lokal per CLI ohne Import" in source
    assert "Run-Control-Vertrag lokal per CLI ohne Ausfuehrung" in source
    assert "Run-Control-Preflight lokal per CLI ohne Ausfuehrung" in source
    assert "Export lokal per CLI nur mit explizitem Zielpfad" in source
    assert "Roundtrip lokal per CLI ohne Schreiben" in source
    assert "Dry-Run lokal per CLI ohne Import" in source
    assert "Importbericht lokal per CLI nach explizitem Schreiben" in source
    assert "Browser schreibt keine Metadaten" in source
    assert "Metadatenquelle" in source
    assert "lokal per CLI" in source
    assert "scenario-overview-row" in source
    assert "run-overview-row" in source
    assert "filteredRuns.map" in source
    assert "Auswahl durch Filter aktuell nicht in den Listen sichtbar" in source
    assert 'type="file"' not in source
