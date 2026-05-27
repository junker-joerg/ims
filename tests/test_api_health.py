import importlib

from starlette.testclient import TestClient

from ims.api.app import APP_VERSION, create_app
from ims.api.metadata_repository import build_seeded_metadata_repository


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


def test_importing_default_app_does_not_create_metadata_db(tmp_path, monkeypatch):
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))

    import ims.api.app as app_module

    importlib.reload(app_module)

    assert db_path.exists() is False
    monkeypatch.delenv("IMS_METADATA_DB")
    importlib.reload(app_module)
