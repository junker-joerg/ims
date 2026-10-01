import importlib

import pytest
from starlette.testclient import TestClient

from ims.api.app import create_app


@pytest.mark.parametrize("fallback", [False, True])
def test_guided_api_pure_build_atomic_storage_and_late_error(monkeypatch, tmp_path, fallback):
    module = importlib.import_module("ims.api.app")
    if fallback: monkeypatch.setattr(module, "FastAPI", None)
    path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    base = "/api/strategies/guided-period-chain"
    preset = client.post(base + "/workshop-case", json={"seed": 1300, "run_index": 0})
    assert preset.status_code == 200
    source = preset.json()["source_input"]
    built = client.post(base + "/build", json=source)
    assert built.status_code == 200
    assert built.headers["etag"] == '"' + built.json()["content_digest"] + '"'
    assert not path.exists()
    request = {"schema_version": "ims.guided-period-chain-store-request.v1", "source_input": source, "expected_content_digest": built.json()["content_digest"], "stored_at": "2026-10-01T07:00:00Z", "explicit_storage_release": True}
    request["explicit_storage_release"] = False
    assert client.post(base + "/store", json=request).status_code == 422
    assert not path.exists()
    request["explicit_storage_release"] = True
    stored = client.post(base + "/store", json=request)
    assert stored.status_code == 200 and stored.json()["stored"]
    snapshot = path.read_bytes()
    assert client.post(base + "/store", json=request).json()["replayed"]
    source["period_contexts"][-1]["profile"]["context"]["period"] = 99
    invalid = client.post(base + "/store", json=request)
    assert invalid.status_code == 422 and invalid.json()["chains"] == []
    assert invalid.json()["content_digest"] is None
    assert path.read_bytes() == snapshot
    assert client.post(base + "/build", content="{").status_code == 422
    assert client.post(base + "/workshop-case", json={"seed": True, "run_index": 0}).status_code == 422
    assert client.post(base + "/build", content=" " * (16 * 1024 * 1024 + 1)).status_code == 422


def test_unconfigured_api_cannot_persist(monkeypatch, tmp_path):
    monkeypatch.delenv("IMS_METADATA_DB", raising=False)
    client = TestClient(create_app(frontend_dist=tmp_path))
    result = client.post("/api/strategies/guided-period-chain/store", json={})
    assert result.status_code == 422 and result.json()["issues"][0]["code"] == "storage_not_configured"
