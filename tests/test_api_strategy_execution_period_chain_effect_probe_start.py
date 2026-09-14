import importlib

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
)
from ims.api.strategy_execution_period_chain_effect_probe import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION,
)
from ims.api.strategy_execution_period_chain_run_control import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION,
)
from ims.api.strategy_execution_period_chain_store import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
    persist_strategy_execution_period_chain,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
)


def _persisted_identity(db_path, profile_root) -> tuple[str, str]:
    references = persist_chain_candidates(db_path, profile_root)
    value = chain_input(references)
    build = build_strategy_execution_period_chain(value, db_path=db_path)
    assert build.chain is not None, build.issues
    stored = persist_strategy_execution_period_chain(
        {
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION
            ),
            "period_chain_input": value,
            "expected_chain_id": build.chain.chain_id,
            "expected_content_digest": build.chain.content_digest,
            "stored_at": "2026-09-14T10:00:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=db_path,
    )
    return stored.record.chain_id, stored.record.content_digest


def _request(
    chain_id: str,
    digest: str,
    *,
    idempotency_key: str = "api-pr140-two-period-start-001",
) -> dict[str, object]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION
        ),
        "release": {
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
            ),
            "chain_id": chain_id,
            "expected_content_digest": digest,
            "idempotency_key": idempotency_key,
            "explicit_run_control_release": True,
            "released_by": "workbench-test",
            "released_at": "2026-09-14T08:30:00Z",
            "release_reason": "Kontrollierter Zwei-Perioden-Start",
        },
        "explicit_two_period_effect_probe_execution": True,
    }


def test_start_contract_and_read_endpoints_enforce_methods(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    contract = (
        "/api/run-control/strategy-period-chain-effect-probe-start-contract"
    )

    response = client.get(contract)
    overview = client.get("/api/strategies/execution-period-chains")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ui_start_enabled"] is True
    assert payload["idempotency_persistence_enabled"] is True
    assert payload["immutable_result_persistence_enabled"] is True
    assert payload["exact_two_period_horizon_required"] is True
    assert payload["result_endpoint_template"].endswith("/{chain_id}")
    assert payload["history_endpoint_template"].endswith("/{chain_id}")
    assert payload["next_gate"] == "PR142"
    assert overview.status_code == 200
    assert overview.json()["storage"]["configured"] is False
    assert overview.json()["period_chain_count"] == 0
    assert client.post(contract, json={}).status_code == 405
    assert client.put(contract, json={}).status_code == 405
    assert client.delete(contract).status_code == 405
    for endpoint in (
        "/api/run-control/strategy-period-chain-effect-probe-result/unknown",
        "/api/run-control/strategy-period-chain-effect-probe-history/unknown",
    ):
        assert client.post(endpoint, json={}).status_code == 405
        assert client.put(endpoint, json={}).status_code == 405
        assert client.delete(endpoint).status_code == 405


def test_overview_and_start_expose_persisted_result_and_history(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    calls = 0

    def counting_runner(loaded, *, output_dir=None):
        nonlocal calls
        calls += 1
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            period_chain_effect_probe_runner=counting_runner,
        )
    )
    start_endpoint = (
        "/api/run-control/strategy-period-chain-effect-probe-start"
    )

    overview = client.get("/api/strategies/execution-period-chains")
    first = client.post(start_endpoint, json=_request(chain_id, digest))
    replay = client.post(start_endpoint, json=_request(chain_id, digest))
    result = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-result/"
        + chain_id
    )
    history = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-history/"
        + chain_id
    )

    assert overview.status_code == 200
    assert overview.json()["period_chain_count"] == 1
    assert overview.json()["period_chains"][0]["digest_verified"] is True
    assert first.status_code == 201
    assert replay.status_code == 200
    assert first.json()["replayed"] is False
    assert replay.json()["replayed"] is True
    assert replay.json()["runner_invocation_count"] == 0
    assert replay.json()["writes_performed"] is False
    assert calls == 2
    assert result.status_code == 200
    assert result.json()["result_available"] is True
    assert [
        effect["period"]
        for effect in result.json()["record"]["result_payload"]["period_effects"]
    ] == [1, 2]
    assert result.json()["writes_performed"] is False
    assert result.json()["execution_performed"] is False
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 1
    assert history.json()["latest_attempt"]["status"] == "result_persisted"
    assert history.json()["latest_attempt"]["runner_invocation_count"] == 2
    assert history.json()["result_available"] is True
    assert history.json()["simulation_performed"] is False
    assert client.get(start_endpoint).status_code == 405
    assert client.put(start_endpoint, json={}).status_code == 405
    assert client.delete(start_endpoint).status_code == 405


def test_read_endpoints_show_empty_evidence_for_unstarted_chain(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, _ = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))

    result = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-result/"
        + chain_id
    )
    history = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-history/"
        + chain_id
    )

    assert result.status_code == 200
    assert result.json()["result_available"] is False
    assert result.json()["record"] is None
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 0
    assert history.json()["attempts"] == []


def test_start_requires_sqlite_and_explicit_probe_release(
    monkeypatch,
    tmp_path,
) -> None:
    endpoint = "/api/run-control/strategy-period-chain-effect-probe-start"
    memory_client = TestClient(create_app(frontend_dist=tmp_path))
    missing_store = memory_client.post(endpoint, json={})

    assert missing_store.status_code == 400
    assert missing_store.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )

    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    sqlite_client = TestClient(create_app(frontend_dist=tmp_path))
    request = _request(chain_id, digest)
    request["explicit_two_period_effect_probe_execution"] = False

    rejected = sqlite_client.post(endpoint, json=request)

    assert rejected.status_code == 400
    assert rejected.json()["issues"][0]["code"] == (
        "effect_probe_execution_release_required"
    )
    history = sqlite_client.get(
        "/api/run-control/strategy-period-chain-effect-probe-history/"
        + chain_id
    ).json()
    assert history["attempt_count"] == 0


def test_second_runner_failure_is_persisted_without_result(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))

    def failing_runner(loaded, *, output_dir=None):
        if loaded.context.period == 2:
            raise RuntimeError("synthetic API second-period failure")
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            period_chain_effect_probe_runner=failing_runner,
        )
    )

    response = client.post(
        "/api/run-control/strategy-period-chain-effect-probe-start",
        json=_request(chain_id, digest),
    )
    history = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-history/"
        + chain_id
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["issues"][0]["code"] == "effect_probe_runner_failed"
    assert payload["attempt_persisted"] is True
    assert payload["runner_invocation_count"] == 2
    assert payload["partial_result_returned"] is False
    assert payload["result_persisted"] is False
    assert payload["simulation_performed"] is False
    assert history.status_code == 200
    assert history.json()["latest_attempt"]["status"] == "failed"
    assert history.json()["latest_attempt"]["runner_invocation_count"] == 2
    assert history.json()["result_available"] is False


def test_start_and_read_endpoints_reject_unknown_chain(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    known_id, _ = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    unknown_id = known_id[:-1] + ("0" if known_id[-1] != "0" else "1")
    unknown_digest = "sha256:" + unknown_id.removeprefix(
        "strategy-period-chain-"
    ) + "0" * 40

    start = client.post(
        "/api/run-control/strategy-period-chain-effect-probe-start",
        json=_request(unknown_id, unknown_digest),
    )
    result = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-result/"
        + unknown_id
    )
    history = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-history/"
        + unknown_id
    )

    assert start.status_code == 404
    assert start.json()["issues"][0]["code"] == "period_chain_not_found"
    assert result.status_code == 404
    assert history.status_code == 404


def test_starlette_fallback_exposes_same_start_and_read_paths(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    app_module = importlib.import_module("ims.api.app")
    monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))

    overview = client.get("/api/strategies/execution-period-chains")
    contract = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-start-contract"
    )
    started = client.post(
        "/api/run-control/strategy-period-chain-effect-probe-start",
        json=_request(chain_id, digest),
    )
    result = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-result/"
        + chain_id
    )

    assert overview.status_code == 200
    assert overview.json()["period_chain_count"] == 1
    assert contract.status_code == 200
    assert contract.json()["next_gate"] == "PR142"
    assert started.status_code == 201
    assert started.json()["runner_invocation_count"] == 2
    assert result.status_code == 200
    assert result.json()["result_available"] is True
