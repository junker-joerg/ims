import importlib
from io import BytesIO

import pytest
from openpyxl import load_workbook
from starlette.testclient import TestClient

from ims.accounting.insurer_balance import insurer_balance_workbench_contract_payload
from ims.api.app import create_app
from tests.test_insurer_balance import _input


@pytest.mark.parametrize("starlette_fallback", [False, True])
def test_insurer_balance_api_and_xlsx_share_verified_digest_without_side_effects(
    monkeypatch, tmp_path, starlette_fallback: bool
) -> None:
    app_module = importlib.import_module("ims.api.app")
    if starlette_fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    db_path = tmp_path / "unused.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> None:
        raise AssertionError("Die Modellbilanz darf keinen Runner starten")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)
    client = TestClient(create_app(frontend_dist=tmp_path))
    contract_endpoint = "/api/accounting/insurer-balance-contract"
    balance_endpoint = "/api/accounting/insurer-balance"
    workbook_endpoint = "/api/accounting/insurer-balance.xlsx"

    assert client.get(contract_endpoint).json() == insurer_balance_workbench_contract_payload()
    response = client.post(balance_endpoint, json=_input())
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    digest = body["content_digest"]
    assert response.headers["etag"] == f'"{digest}"'
    assert response.headers["cache-control"] == "no-store"
    assert db_path.exists() is False

    missing_match = client.post(workbook_endpoint, json=_input())
    assert missing_match.status_code == 428
    assert missing_match.json()["code"] == "if_match_required"
    changed = _input()
    changed["sectors"][0]["periods"][0]["premium_income"] = "21"
    mismatch = client.post(workbook_endpoint, json=changed, headers={"If-Match": f'"{digest}"'})
    assert mismatch.status_code == 409
    assert mismatch.json()["code"] == "balance_digest_mismatch"

    download = client.post(workbook_endpoint, json=_input(), headers={"If-Match": f'"{digest}"'})
    assert download.status_code == 200
    assert download.headers["etag"] == f'"{digest}"'
    assert download.headers["cache-control"] == "no-store"
    assert "spreadsheetml.sheet" in download.headers["content-type"]
    assert 'filename="ims-modellbilanz-vu-1.xlsx"' in download.headers["content-disposition"]
    workbook = load_workbook(BytesIO(download.content), read_only=True)
    try:
        assert workbook["Gesamt"]["M2"].value == body["total_rows"][0]["closing_cash"]
        assert workbook["Gesamt"]["M2"].data_type == "s"
    finally:
        workbook.close()
    assert db_path.exists() is False
    assert client.post(contract_endpoint, json={}).status_code == 405
    assert client.get(balance_endpoint).status_code == 405
    assert client.get(workbook_endpoint).status_code == 405


@pytest.mark.parametrize("starlette_fallback", [False, True])
def test_insurer_balance_api_errors_return_no_partial_result(
    monkeypatch, tmp_path, starlette_fallback: bool
) -> None:
    app_module = importlib.import_module("ims.api.app")
    if starlette_fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))
    balance_endpoint = "/api/accounting/insurer-balance"
    workbook_endpoint = "/api/accounting/insurer-balance.xlsx"

    malformed = client.post(balance_endpoint, content="{", headers={"content-type": "application/json"})
    assert malformed.status_code == 400
    assert malformed.json()["partial_result_returned"] is False
    invalid = _input()
    invalid["sectors"][1]["periods"][1]["claims_paid"] = "999"
    for endpoint in (balance_endpoint, workbook_endpoint):
        response = client.post(endpoint, json=invalid)
        assert response.status_code == 422
        assert response.json()["valid"] is False
        assert response.json()["sectors"] == []
        assert response.json()["total_rows"] == []
        assert response.json()["content_digest"] is None
