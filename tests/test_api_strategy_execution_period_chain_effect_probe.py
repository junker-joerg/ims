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
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
)


def _persisted_identity(
    db_path,
    profile_root,
    *,
    max_periods: int = 2,
) -> tuple[str, str]:
    references = persist_chain_candidates(
        db_path,
        profile_root,
        max_periods=max_periods,
    )
    value = chain_input(references, max_periods=max_periods)
    build = build_strategy_execution_period_chain(value, db_path=db_path)
    assert build.chain is not None, build.issues
    persisted = persist_strategy_execution_period_chain(
        {
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION
            ),
            "period_chain_input": value,
            "expected_chain_id": build.chain.chain_id,
            "expected_content_digest": build.chain.content_digest,
            "stored_at": "2026-09-11T15:00:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=db_path,
    )
    return persisted.record.chain_id, persisted.record.content_digest


def _request(chain_id: str, digest: str) -> dict[str, object]:
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
            "idempotency_key": "api-pr139-two-period-probe-001",
            "explicit_run_control_release": True,
            "released_by": "api-test-reviewer",
            "released_at": "2026-09-11T13:05:00Z",
            "release_reason": "API-Zwei-Perioden-Wirkungsprobe",
        },
        "explicit_two_period_effect_probe_execution": True,
    }


def test_period_chain_effect_probe_contract_enforces_methods(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-period-chain-effect-probe-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["exact_two_period_horizon_required"] is True
    assert payload["candidate_re_resolution_required"] is True
    assert payload["result_persistence_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR140"
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_period_chain_effect_probe_executes_ephemerally(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-period-chain-effect-probe"
    before = db_path.read_bytes()

    response = client.post(endpoint, json=_request(chain_id, digest))

    assert response.status_code == 200
    assert db_path.read_bytes() == before
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["period_count"] == 2
    assert payload["runner_invocation_count"] == 2
    assert payload["candidate_reverified_count"] == 2
    assert payload["transition_effect"]["from_period"] == 1
    assert payload["transition_effect"]["to_period"] == 2
    assert payload["result_persisted"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is True
    assert payload["simulation_performed"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_period_chain_effect_probe_rejects_bad_and_long_requests(
    monkeypatch,
    tmp_path,
) -> None:
    endpoint = "/api/run-control/strategy-period-chain-effect-probe"
    memory_client = TestClient(create_app(frontend_dist=tmp_path))
    unavailable = memory_client.post(endpoint, json={})
    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )

    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(
        db_path,
        tmp_path,
        max_periods=3,
    )
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )
    unreleased = _request(chain_id, digest)
    unreleased["explicit_two_period_effect_probe_execution"] = False

    rejected_release = client.post(endpoint, json=unreleased)
    rejected_horizon = client.post(endpoint, json=_request(chain_id, digest))

    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert rejected_release.status_code == 400
    assert rejected_release.json()["issues"][0]["code"] == (
        "effect_probe_execution_release_required"
    )
    assert rejected_horizon.status_code == 409
    assert rejected_horizon.json()["issues"][0]["code"] == (
        "exact_two_period_horizon_required"
    )
    assert rejected_horizon.json()["runner_invocation_count"] == 0
    assert rejected_horizon.json()["partial_result_returned"] is False


def test_period_chain_effect_probe_reports_second_runner_failure(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))

    def failing_runner(loaded, *, output_dir=None):
        if loaded.context.period == 2:
            raise RuntimeError("synthetic API runner failure")
        from ims.engine.explicit_period_runner import run_loaded_explicit_period

        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            period_chain_effect_probe_runner=failing_runner,
        )
    )

    response = client.post(
        "/api/run-control/strategy-period-chain-effect-probe",
        json=_request(chain_id, digest),
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["issues"][0]["code"] == "effect_probe_runner_failed"
    assert payload["runner_invocation_count"] == 2
    assert payload["period_effects"] == []
    assert payload["partial_result_returned"] is False
    assert payload["execution_performed"] is False
    assert payload["writes_performed"] is False


def test_starlette_fallback_exposes_same_two_period_probe(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    app_module = importlib.import_module("ims.api.app")
    monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))

    contract = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-contract"
    )
    executed = client.post(
        "/api/run-control/strategy-period-chain-effect-probe",
        json=_request(chain_id, digest),
    )

    assert contract.status_code == 200
    assert contract.json()["next_gate"] == "PR140"
    assert executed.status_code == 200
    assert executed.json()["period_count"] == 2
    assert executed.json()["writes_performed"] is False
    assert executed.json()["simulation_performed"] is False
