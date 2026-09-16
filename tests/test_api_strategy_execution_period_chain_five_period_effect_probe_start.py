from copy import deepcopy
import importlib

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_period_chain_five_period_build import (
    build_strategy_execution_five_period_chain,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe import (
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe_start import (
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION,
)
from ims.api.strategy_execution_period_chain_run_control import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
    persist_two_period_effect_probe_baseline,
)


CONTRACT_ENDPOINT = (
    "/api/run-control/strategy-period-chain-five-period-effect-probe-start-contract"
)
START_ENDPOINT = (
    "/api/run-control/strategy-period-chain-five-period-effect-probe-start"
)
RESULT_PREFIX = (
    "/api/run-control/strategy-period-chain-five-period-effect-probe-result/"
)
HISTORY_PREFIX = (
    "/api/run-control/strategy-period-chain-five-period-effect-probe-history/"
)


def _prepared_request(tmp_path):
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
    value = chain_input(references, run_index=2, max_periods=5)
    build = build_strategy_execution_five_period_chain(value, db_path=db_path)
    assert build.chain is not None, build.issues
    return db_path, build.chain.chain_id, {
        "schema_version": (
            STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION
        ),
        "effect_probe_request": {
            "schema_version": (
                STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION
            ),
            "period_chain_input": value,
            "prefix_baseline": baseline,
            "explicit_five_period_effect_probe_execution": True,
        },
        "release": {
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
            ),
            "chain_id": build.chain.chain_id,
            "expected_content_digest": build.chain.content_digest,
            "idempotency_key": "api-pr145-five-period-start-001",
            "explicit_run_control_release": True,
            "released_by": "workbench-test",
            "released_at": "2026-09-14T09:30:00Z",
            "release_reason": "Kontrollierter Fuenf-Perioden-Start",
        },
        "explicit_five_period_effect_probe_start": True,
    }


def test_contract_and_read_routes_enforce_methods(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    contract = client.get(CONTRACT_ENDPOINT)

    assert contract.status_code == 200
    payload = contract.json()
    assert payload["server_start_enabled"] is True
    assert payload["ui_start_enabled"] is True
    assert payload["immutable_period_chain_snapshot_persistence_enabled"] is True
    assert payload["immutable_result_persistence_enabled"] is True
    assert payload["exact_five_period_horizon_required"] is True
    assert payload["next_gate"] == "PR147"
    assert client.post(CONTRACT_ENDPOINT, json={}).status_code == 405
    assert client.get(START_ENDPOINT).status_code == 405
    for endpoint in (RESULT_PREFIX + "unknown", HISTORY_PREFIX + "unknown"):
        assert client.post(endpoint, json={}).status_code == 405
        assert client.put(endpoint, json={}).status_code == 405
        assert client.delete(endpoint).status_code == 405


def test_start_replay_result_and_history_use_configured_store(
    monkeypatch,
    tmp_path,
) -> None:
    db_path, chain_id, request = _prepared_request(tmp_path)
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

    first = client.post(START_ENDPOINT, json=request)
    replay = client.post(START_ENDPOINT, json=request)
    result = client.get(RESULT_PREFIX + chain_id)
    history = client.get(HISTORY_PREFIX + chain_id)

    assert first.status_code == 201
    assert replay.status_code == 200
    assert first.json()["replayed"] is False
    assert replay.json()["replayed"] is True
    assert replay.json()["runner_invocation_count"] == 0
    assert replay.json()["writes_performed"] is False
    assert calls == [1, 2, 3, 4, 5]
    assert result.status_code == 200
    assert result.json()["result_available"] is True
    assert [
        item["period"]
        for item in result.json()["record"]["result_payload"]["period_effects"]
    ] == [1, 2, 3, 4, 5]
    assert result.json()["record"]["period_chain_payload"]["identity"][
        "chain_id"
    ] == chain_id
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 1
    assert history.json()["latest_attempt"]["status"] == "result_persisted"
    assert history.json()["latest_attempt"]["runner_invocation_count"] == 5
    assert history.json()["latest_attempt"]["prefix_baseline_verified"] is True
    assert history.json()["simulation_performed"] is False


def test_start_requires_sqlite_and_explicit_release(monkeypatch, tmp_path) -> None:
    memory_client = TestClient(create_app(frontend_dist=tmp_path))
    missing_store = memory_client.post(START_ENDPOINT, json={})
    assert missing_store.status_code == 400
    assert missing_store.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )

    db_path, chain_id, request = _prepared_request(tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    rejected_request = deepcopy(request)
    rejected_request["explicit_five_period_effect_probe_start"] = False
    rejected = client.post(START_ENDPOINT, json=rejected_request)

    assert rejected.status_code == 400
    assert rejected.json()["issues"][0]["code"] == (
        "five_period_effect_probe_start_release_required"
    )
    history = client.get(HISTORY_PREFIX + chain_id)
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 0


def test_fourth_runner_failure_is_audited_without_result(
    monkeypatch,
    tmp_path,
) -> None:
    db_path, chain_id, request = _prepared_request(tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))

    def failing_runner(loaded, *, output_dir=None):
        if loaded.context.period == 4:
            raise RuntimeError("synthetic API PR145 failure")
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            period_chain_effect_probe_runner=failing_runner,
        )
    )

    response = client.post(START_ENDPOINT, json=request)
    history = client.get(HISTORY_PREFIX + chain_id)

    assert response.status_code == 409
    assert response.json()["issues"][0]["code"] == "effect_probe_runner_failed"
    assert response.json()["runner_invocation_count"] == 4
    assert response.json()["period_chain_digest_reverified"] is True
    assert response.json()["attempt_persisted"] is True
    assert response.json()["partial_result_returned"] is False
    assert response.json()["result_persisted"] is False
    assert history.json()["latest_attempt"]["status"] == "failed"
    assert history.json()["result_available"] is False


def test_starlette_fallback_exposes_same_persistent_paths(
    monkeypatch,
    tmp_path,
) -> None:
    db_path, chain_id, request = _prepared_request(tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    app_module = importlib.import_module("ims.api.app")
    monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))

    contract = client.get(CONTRACT_ENDPOINT)
    started = client.post(START_ENDPOINT, json=request)
    result = client.get(RESULT_PREFIX + chain_id)
    history = client.get(HISTORY_PREFIX + chain_id)

    assert contract.status_code == 200
    assert contract.json()["next_gate"] == "PR147"
    assert started.status_code == 201
    assert started.json()["runner_invocation_count"] == 5
    assert result.status_code == 200
    assert result.json()["result_available"] is True
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 1
