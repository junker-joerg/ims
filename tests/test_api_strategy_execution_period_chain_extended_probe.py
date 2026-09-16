import importlib

from fastapi.testclient import TestClient
import pytest

from ims.api.app import create_app
from tests.test_strategy_execution_period_chain_extended_probe import _input


ENDPOINT = "/api/run-control/strategy-period-chain-extended-effect-probe"


@pytest.mark.parametrize("fallback", [False, True])
def test_extended_probe_requires_explicit_store_and_release(
    monkeypatch, tmp_path, fallback
):
    app_module = importlib.import_module("ims.api.app")
    if fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    monkeypatch.delenv("IMS_METADATA_DB", raising=False)
    client = TestClient(create_app(frontend_dist=tmp_path))
    assert (
        client.post(ENDPOINT, json={}).json()["code"]
        == "explicit_sqlite_store_required"
    )
    assert client.get(ENDPOINT).status_code == 405

    monkeypatch.setenv("IMS_METADATA_DB", str(tmp_path / "metadata.sqlite"))
    client = TestClient(create_app(frontend_dist=tmp_path))
    response = client.post(ENDPOINT, json={})
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request_fields"


@pytest.mark.parametrize("fallback", [False, True])
def test_extended_probe_endpoint_runs_only_explicit_ten_period_request(
    monkeypatch, tmp_path, fallback
):
    db_path, payload = _input(tmp_path, 10)
    before = db_path.read_bytes()
    app_module = importlib.import_module("ims.api.app")
    if fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["period_count"] == 10
    assert response.json()["prefix_proof"]["semantic_equal"] is True
    assert db_path.read_bytes() == before


def test_hundred_period_probe_is_released_via_api(monkeypatch, tmp_path):
    db_path, payload = _input(tmp_path, 100)
    before = db_path.read_bytes()
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["period_count"] == 100
    assert result["prefix_proof"]["canonical_json_byte_equal"] is True
    assert result["result_persisted"] is False
    assert db_path.read_bytes() == before
