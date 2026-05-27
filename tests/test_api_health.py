from starlette.testclient import TestClient

from ims.api.app import APP_VERSION, create_app


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
    scenarios = response.json()
    assert scenarios[0]["id"] == "agrsich-reference-window"
    assert scenarios[0]["source"] == "tests/fixtures"
    assert "Vollgleichheitsbehauptung" in scenarios[0]["notes"]


def test_run_metadata_endpoint_has_no_execution_control(tmp_path):
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/runs")

    assert response.status_code == 200
    runs = response.json()
    assert runs[0]["id"] == "baseline-python-tests"
    assert runs[1]["period_window"] == "keine Simulation"
