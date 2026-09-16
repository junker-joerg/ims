import importlib

import pytest
from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.model.sector_taxonomy import sector_taxonomy_payload


@pytest.mark.parametrize("starlette_fallback", [False, True])
def test_sector_taxonomy_endpoint_is_read_only_without_execution(
    monkeypatch, tmp_path, starlette_fallback: bool
) -> None:
    app_module = importlib.import_module("ims.api.app")
    if starlette_fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    db_path = tmp_path / "unused.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> None:
        raise AssertionError("Die Taxonomie darf keinen Runner starten")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/model/sector-taxonomy"

    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.json() == sector_taxonomy_payload()
    assert db_path.exists() is False
    for method in ("POST", "PUT", "DELETE"):
        assert client.request(method, endpoint, json={}).status_code == 405
    assert db_path.exists() is False
