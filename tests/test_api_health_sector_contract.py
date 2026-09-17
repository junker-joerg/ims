import importlib

import pytest
from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.model.health_sector_contract import (
    HEALTH_SECTOR_CONTRACT_V1_VERSION,
    health_sector_contract_payload,
)


@pytest.mark.parametrize("starlette_fallback", [False, True])
def test_health_contract_is_get_only_without_storage_or_runner(
    monkeypatch, tmp_path, starlette_fallback: bool
) -> None:
    app_module = importlib.import_module("ims.api.app")
    if starlette_fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    db_path = tmp_path / "unused.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> None:
        raise AssertionError("Der Kranken-Vertrag darf keinen Runner starten")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/model/health-sector-contract"

    response = client.get(endpoint)
    assert response.status_code == 200
    assert response.json() == health_sector_contract_payload()
    assert client.get(endpoint + "/v1").json() == health_sector_contract_payload(
        HEALTH_SECTOR_CONTRACT_V1_VERSION
    )
    assert db_path.exists() is False
    for path in (endpoint, endpoint + "/v1"):
        for method in ("POST", "PUT", "DELETE"):
            assert client.request(method, path, json={}).status_code == 405
    assert db_path.exists() is False
