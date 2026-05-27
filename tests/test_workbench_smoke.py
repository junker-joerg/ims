from pathlib import Path

from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.api.metadata_repository import build_seeded_metadata_repository


def test_workbench_api_metadata_smoke(tmp_path: Path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    health = client.get("/api/health")
    scenarios = client.get("/api/scenarios")
    runs = client.get("/api/runs")
    missing = client.get("/api/scenarios/missing-scenario")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert scenarios.status_code == 200
    assert runs.status_code == 200

    scenario_id = scenarios.json()["items"][0]["id"]
    run_id = runs.json()["items"][0]["id"]
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

