import importlib

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.strategies import strategy_execution_period_chain_horizon_contract_payload


ENDPOINT = "/api/run-control/strategy-period-chain-horizon-contract"


def test_horizon_contract_is_get_only_and_does_not_open_storage(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "unused.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> None:
        raise AssertionError("Der read-only Vertrag darf keinen Runner starten")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.get(ENDPOINT)

    assert response.status_code == 200
    assert response.json() == strategy_execution_period_chain_horizon_contract_payload()
    assert db_path.exists() is False
    for method in ("POST", "PUT", "DELETE"):
        assert client.request(method, ENDPOINT, json={}).status_code == 405
    assert db_path.exists() is False


def test_starlette_fallback_exposes_same_get_only_contract(
    monkeypatch,
    tmp_path,
) -> None:
    app_module = importlib.import_module("ims.api.app")
    monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.get(ENDPOINT)

    assert response.status_code == 200
    assert response.json() == strategy_execution_period_chain_horizon_contract_payload()
    assert client.post(ENDPOINT, json={}).status_code == 405
