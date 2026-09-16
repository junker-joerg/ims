from copy import deepcopy
import importlib

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_period_chain_five_period_effect_probe import (
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
    persist_two_period_effect_probe_baseline,
)


CONTRACT_ENDPOINT = (
    "/api/run-control/strategy-period-chain-five-period-effect-probe-contract"
)
EXECUTION_ENDPOINT = (
    "/api/run-control/strategy-period-chain-five-period-effect-probe"
)


def _request(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    baseline = persist_two_period_effect_probe_baseline(
        db_path,
        tmp_path / "baseline",
        run_index=5,
    )
    five_root = tmp_path / "five"
    five_root.mkdir()
    references = persist_chain_candidates(
        db_path,
        five_root,
        run_index=2,
        max_periods=5,
    )
    return db_path, {
        "schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
        "period_chain_input": chain_input(
            references,
            run_index=2,
            max_periods=5,
        ),
        "prefix_baseline": deepcopy(baseline),
        "explicit_five_period_effect_probe_execution": True,
    }


def test_five_period_effect_probe_api_executes_without_persistence(
    monkeypatch,
    tmp_path,
) -> None:
    db_path, request = _request(tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    calls: list[int] = []

    def counting_runner(loaded, *, output_dir=None):
        calls.append(loaded.context.period)
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            period_chain_effect_probe_runner=counting_runner,
        )
    )

    contract = client.get(CONTRACT_ENDPOINT)
    response = client.post(EXECUTION_ENDPOINT, json=request)

    assert contract.status_code == 200
    assert contract.json()["five_period_execution_enabled"] is True
    assert contract.json()["next_gate"] == "PR147"
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["period_count"] == 5
    assert payload["transition_count"] == 4
    assert payload["two_period_prefix_verified"] is True
    assert payload["result_persisted"] is False
    assert payload["writes_performed"] is False
    assert payload["simulation_performed"] is False
    assert calls == [1, 2, 3, 4, 5]
    assert client.post(CONTRACT_ENDPOINT, json={}).status_code == 405
    assert client.get(EXECUTION_ENDPOINT).status_code == 405
    assert client.put(EXECUTION_ENDPOINT, json={}).status_code == 405
    assert client.delete(EXECUTION_ENDPOINT).status_code == 405


def test_five_period_effect_probe_api_reports_closed_error_paths(
    monkeypatch,
    tmp_path,
) -> None:
    memory_client = TestClient(create_app(frontend_dist=tmp_path))

    unavailable = memory_client.post(EXECUTION_ENDPOINT, json={})

    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )
    assert unavailable.json()["runner_invocation_count"] == 0

    db_path, _ = _request(tmp_path / "sqlite")
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    sqlite_client = TestClient(create_app(frontend_dist=tmp_path))

    invalid_json = sqlite_client.post(
        EXECUTION_ENDPOINT,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert invalid_json.json()["period_effects"] == []
    assert invalid_json.json()["partial_result_returned"] is False


def test_starlette_fallback_exposes_same_five_period_effect_probe(
    monkeypatch,
    tmp_path,
) -> None:
    db_path, request = _request(tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    app_module = importlib.import_module("ims.api.app")
    monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))

    contract = client.get(CONTRACT_ENDPOINT)
    response = client.post(EXECUTION_ENDPOINT, json=request)

    assert contract.status_code == 200
    assert contract.json()["exact_five_period_horizon_required"] is True
    assert response.status_code == 200
    assert response.json()["period_count"] == 5
    assert response.json()["two_period_prefix_verified"] is True
