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
