import importlib

import pytest
from starlette.testclient import TestClient

from ims.accounting.solvency_model_balance import solvency_model_balance_contract_payload
from ims.api.app import create_app
from tests.test_solvency_model_balance import _input


@pytest.mark.parametrize("starlette_fallback", [False, True])
def test_model_bridge_api_recalculates_without_runner_or_write(
    monkeypatch, tmp_path, starlette_fallback: bool,
) -> None:
    app_module = importlib.import_module("ims.api.app")
    if starlette_fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    db_path = tmp_path / "unused.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> None:
        raise AssertionError("Modell-Solvenzbilanz darf keinen Runner starten")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/accounting/solvency-model-balance"
    contract_endpoint = endpoint + "-contract"
    assert client.get(contract_endpoint).json() == solvency_model_balance_contract_payload()
    response = client.post(endpoint, json=_input())
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["total_row"]["model_own_funds_proxy"] == "319.0000"
    assert response.headers["etag"] == f'"{body["content_digest"]}"'
    assert response.headers["cache-control"] == "no-store"
    assert db_path.exists() is False
    assert client.get(endpoint).status_code == 405
    for method in ("POST", "PUT", "DELETE"):
        assert client.request(method, contract_endpoint, json={}).status_code == 405


@pytest.mark.parametrize("starlette_fallback", [False, True])
def test_model_bridge_api_rejects_bad_input_without_partial_rows(
    monkeypatch, tmp_path, starlette_fallback: bool,
) -> None:
    app_module = importlib.import_module("ims.api.app")
    if starlette_fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/accounting/solvency-model-balance"
    malformed = client.post(endpoint, content="{", headers={"content-type": "application/json"})
    assert malformed.status_code == 400
    assert malformed.json()["partial_result_returned"] is False
    value = _input()
    value["adjustments"][0]["asset_delta"] = "-99999"
    invalid = client.post(endpoint, json=value)
    assert invalid.status_code == 422
    assert invalid.json()["valid"] is False
    assert invalid.json()["sector_rows"] == []
    assert invalid.json()["total_row"] is None
    assert invalid.json()["content_digest"] is None
    assert invalid.headers["cache-control"] == "no-store"
