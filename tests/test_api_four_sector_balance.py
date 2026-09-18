import importlib

import pytest
from starlette.testclient import TestClient

from ims.accounting.four_sector_balance import four_sector_balance_contract_payload
from ims.api.app import create_app
from tests.test_four_sector_balance import _input
from tests.test_insurer_balance import _input as two_sector_input


@pytest.mark.parametrize("starlette_fallback", [False, True])
def test_four_sector_api_recomputes_and_does_not_write_or_change_two_sector_api(
    monkeypatch, tmp_path, starlette_fallback: bool,
) -> None:
    app_module = importlib.import_module("ims.api.app")
    if starlette_fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    db_path = tmp_path / "unused.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> None:
        raise AssertionError("Vier-Sparten-Bilanz darf keinen Bestandsrunner starten")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/accounting/four-sector-balance"
    contract = client.get("/api/accounting/four-sector-balance-contract").json()
    assert contract == four_sector_balance_contract_payload()
    assert contract["supported_horizons"] == [1, 2, 5, 10, 25, 50, 100]
    response = client.post(endpoint, json=_input())
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["period_count"] == 2
    assert response.headers["etag"] == f'"{body["content_digest"]}"'
    assert response.headers["cache-control"] == "no-store"
    assert db_path.exists() is False
    old = client.post("/api/accounting/insurer-balance", json=two_sector_input())
    assert old.status_code == 200
    assert old.json()["period_count"] == 2
    assert [sector["sector_id"] for sector in old.json()["sectors"]] == ["motor", "property_liability"]
    assert client.get(endpoint).status_code == 405


@pytest.mark.parametrize("starlette_fallback", [False, True])
def test_four_sector_api_rejects_malformed_or_unmatched_input_atomically(
    monkeypatch, tmp_path, starlette_fallback: bool,
) -> None:
    app_module = importlib.import_module("ims.api.app")
    if starlette_fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/accounting/four-sector-balance"
    malformed = client.post(endpoint, content="{", headers={"content-type": "application/json"})
    assert malformed.status_code == 400
    assert malformed.json()["partial_result_returned"] is False
    value = _input()
    value["sectors"]["life"]["periods"].pop()
    invalid = client.post(endpoint, json=value)
    assert invalid.status_code == 422
    assert invalid.json()["valid"] is False
    assert invalid.json()["sectors"] == invalid.json()["total_rows"] == []
    assert invalid.json()["content_digest"] is None
    assert invalid.headers["cache-control"] == "no-store"
