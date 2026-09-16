from io import BytesIO
import importlib
import json
from zipfile import ZipFile

from fastapi.testclient import TestClient
import pytest

from ims.api.app import create_app
from ims.api.strategy_execution_period_chain_extended_probe import ExtendedProbeError
from tests.test_strategy_execution_period_chain_extended_probe import _input


ENDPOINT = "/api/run-control/strategy-period-chain-extended-result-bundle"


@pytest.mark.parametrize("fallback", [False, True])
def test_explicit_hundred_period_bundle_is_downloadable_and_atomic(
    monkeypatch, tmp_path, fallback
):
    db_path, payload = _input(tmp_path, 100)
    before = db_path.read_bytes()
    app_module = importlib.import_module("ims.api.app")
    if fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 200, response.text[:400]
    assert response.headers["content-type"] == "application/zip"
    assert response.headers["cache-control"] == "no-store"
    with ZipFile(BytesIO(response.content)) as archive:
        assert json.loads(archive.read("manifest.json"))["row_count"] > 100
    assert db_path.read_bytes() == before


@pytest.mark.parametrize("fallback", [False, True])
def test_bundle_rejects_wrong_horizon_and_runtime_failure_before_download(
    monkeypatch, tmp_path, fallback
):
    db_path, payload = _input(tmp_path, 10)
    app_module = importlib.import_module("ims.api.app")
    if fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "bundle_horizon_not_released"
    payload["period_chain_input"]["max_periods"] = 100

    def fail(*args, **kwargs):
        raise ExtendedProbeError("worker_failed", "Abbruch ohne Ergebnis")

    monkeypatch.setattr(app_module, "run_extended_probe", fail)
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 409
    assert response.json()["partial_result_returned"] is False
    assert response.headers["content-type"].startswith("application/json")
