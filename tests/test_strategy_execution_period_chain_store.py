import importlib
import json
import sqlite3

from fastapi.testclient import TestClient
import pytest

from ims.api.app import create_app
from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
    strategy_execution_period_chain_id_from_digest,
)
from ims.api.strategy_execution_period_chain_store import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION,
    StrategyExecutionPeriodChainStoreError,
    get_strategy_execution_period_chain,
    persist_strategy_execution_period_chain,
    strategy_execution_period_chain_store_contract_payload,
)
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
)


def _store_request(
    db_path,
    profile_root,
    *,
    stored_at: str = "2026-09-11T12:00:00+02:00",
) -> dict[str, object]:
    references = persist_chain_candidates(db_path, profile_root)
    period_chain_input = chain_input(references)
    build = build_strategy_execution_period_chain(
        period_chain_input,
        db_path=db_path,
    )
    assert build.chain is not None, build.issues
    return {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
        "period_chain_input": period_chain_input,
        "expected_chain_id": build.chain.chain_id,
        "expected_content_digest": build.chain.content_digest,
        "stored_at": stored_at,
        "explicit_storage_release": True,
    }


def _chain_table_exists(db_path) -> bool:
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' "
            "AND name = 'strategy_execution_period_chains'"
        ).fetchone()
    return row is not None


def test_persists_and_reads_verified_immutable_period_chain(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)

    persisted = persist_strategy_execution_period_chain(request, db_path=db_path)
    read = get_strategy_execution_period_chain(
        str(request["expected_chain_id"]),
        db_path=db_path,
    )

    payload = persisted.to_dict()
    assert payload["schema_version"] == STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION
    assert payload["period_chain_persisted"] is True
    assert payload["storage_release_confirmed"] is True
    assert payload["chain_rebuilt"] is True
    assert payload["pre_storage_digest_verified"] is True
    assert payload["post_storage_digest_verified"] is True
    assert payload["new_record_created"] is True
    assert payload["replayed"] is False
    assert payload["writes_performed"] is True
    assert payload["carryover_invocation_performed"] is False
    assert payload["runner_invocation_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert read.record == persisted.record
    assert read.to_dict()["chain_rebuilt"] is False
    assert read.to_dict()["writes_performed"] is False
    assert read.to_dict()["post_storage_digest_verified"] is True
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT chain_id, content_digest FROM strategy_execution_period_chains"
        ).fetchone()
    assert row == (
        request["expected_chain_id"],
        request["expected_content_digest"],
    )


def test_exact_replay_is_idempotent_and_keeps_original_timestamp(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    first_request = _store_request(
        db_path,
        tmp_path,
        stored_at="2026-09-11T12:00:00+02:00",
    )
    replay_request = {
        **first_request,
        "stored_at": "2026-09-11T12:05:00+02:00",
    }

    first = persist_strategy_execution_period_chain(first_request, db_path=db_path)
    replay = persist_strategy_execution_period_chain(replay_request, db_path=db_path)

    assert first.new_record_created is True
    assert replay.new_record_created is False
    assert replay.replayed is True
    assert replay.to_dict()["writes_performed"] is False
    assert replay.record.stored_at == "2026-09-11T12:00:00+02:00"
    with sqlite3.connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM strategy_execution_period_chains"
        ).fetchone()[0]
    assert count == 1


def test_requires_explicit_release_before_creating_chain_table(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    request["explicit_storage_release"] = False

    with pytest.raises(StrategyExecutionPeriodChainStoreError) as exc_info:
        persist_strategy_execution_period_chain(request, db_path=db_path)

    assert exc_info.value.code == "storage_release_required"
    assert _chain_table_exists(db_path) is False


def test_rejects_expected_digest_mismatch_before_creating_chain_table(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    wrong_digest = "sha256:" + "0" * 64
    request["expected_content_digest"] = wrong_digest
    request["expected_chain_id"] = strategy_execution_period_chain_id_from_digest(
        wrong_digest
    )

    with pytest.raises(StrategyExecutionPeriodChainStoreError) as exc_info:
        persist_strategy_execution_period_chain(request, db_path=db_path)

    assert exc_info.value.code == "period_chain_id_mismatch"
    assert _chain_table_exists(db_path) is False


def test_failed_server_rebuild_is_atomic_and_creates_no_chain_table(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    second_reference = request["period_chain_input"]["period_candidates"][1]
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "DELETE FROM strategy_execution_candidates WHERE candidate_id = ?",
            (second_reference["candidate_id"],),
        )

    with pytest.raises(StrategyExecutionPeriodChainStoreError) as exc_info:
        persist_strategy_execution_period_chain(request, db_path=db_path)

    assert exc_info.value.code == "period_chain_rebuild_failed"
    assert _chain_table_exists(db_path) is False


def test_rejects_free_database_path_and_browser_chain_payload(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    request["db_path"] = str(tmp_path / "browser-selected.sqlite")
    request["period_chain"] = {"identity": "browser-supplied"}

    with pytest.raises(StrategyExecutionPeriodChainStoreError) as exc_info:
        persist_strategy_execution_period_chain(request, db_path=db_path)

    assert exc_info.value.code == "store_request_fields_unknown"
    assert _chain_table_exists(db_path) is False


def test_failed_post_storage_verification_rolls_back_insert(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    module = importlib.import_module(
        "ims.api.strategy_execution_period_chain_store"
    )

    def reject_stored_row(row):
        raise StrategyExecutionPeriodChainStoreError(
            "forced_post_storage_failure",
            "forced post-storage verification failure",
        )

    monkeypatch.setattr(
        module,
        "_row_to_verified_period_chain_record",
        reject_stored_row,
    )

    with pytest.raises(StrategyExecutionPeriodChainStoreError) as exc_info:
        persist_strategy_execution_period_chain(request, db_path=db_path)

    assert exc_info.value.code == "forced_post_storage_failure"
    with sqlite3.connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM strategy_execution_period_chains"
        ).fetchone()[0]
    assert count == 0


def test_existing_modified_record_is_rejected_without_repair(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    persist_strategy_execution_period_chain(request, db_path=db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE strategy_execution_period_chains SET run_index = ?",
            (99,),
        )

    with pytest.raises(StrategyExecutionPeriodChainStoreError) as exc_info:
        persist_strategy_execution_period_chain(request, db_path=db_path)

    assert exc_info.value.code == "stored_period_chain_metadata_mismatch"
    with sqlite3.connect(db_path) as connection:
        run_index = connection.execute(
            "SELECT run_index FROM strategy_execution_period_chains"
        ).fetchone()[0]
    assert run_index == 99


def test_read_detects_period_chain_payload_corruption(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    persisted = persist_strategy_execution_period_chain(request, db_path=db_path)
    damaged = persisted.record.period_chain
    damaged["transitions"][0]["carry_forward_vu_state"] = False
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE strategy_execution_period_chains SET chain_payload_json = ?",
            (json.dumps(damaged, sort_keys=True),),
        )

    with pytest.raises(StrategyExecutionPeriodChainStoreError) as exc_info:
        get_strategy_execution_period_chain(
            str(request["expected_chain_id"]),
            db_path=db_path,
        )

    assert exc_info.value.code == "period_chain_digest_verification_failed"


def test_read_rejects_payload_outside_execution_boundaries_before_digest(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    persisted = persist_strategy_execution_period_chain(request, db_path=db_path)
    damaged = persisted.record.period_chain
    damaged["execution_boundaries"]["runner_invocation_performed"] = True
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE strategy_execution_period_chains SET chain_payload_json = ?",
            (json.dumps(damaged, sort_keys=True),),
        )

    with pytest.raises(StrategyExecutionPeriodChainStoreError) as exc_info:
        get_strategy_execution_period_chain(
            str(request["expected_chain_id"]),
            db_path=db_path,
        )

    assert exc_info.value.code == "period_chain_execution_boundaries_mismatch"


def test_store_does_not_invoke_carryover_or_runner(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    vu_runner = importlib.import_module("ims.engine.vu_rule_runner")
    vn_runner = importlib.import_module("ims.engine.vn_rule_runner")
    period_runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"execution invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(vu_runner, "apply_vu_foreign_info_carryover", reject_execution)
    monkeypatch.setattr(vn_runner, "apply_vn_state_carryover", reject_execution)
    monkeypatch.setattr(period_runner, "run_loaded_explicit_period", reject_execution)

    result = persist_strategy_execution_period_chain(request, db_path=db_path)

    assert result.to_dict()["period_chain_persisted"] is True
    assert result.to_dict()["carryover_invocation_performed"] is False
    assert result.to_dict()["runner_invocation_performed"] is False
    assert result.to_dict()["execution_performed"] is False
    assert result.to_dict()["simulation_performed"] is False


def test_store_contract_opens_only_explicit_immutable_persistence() -> None:
    payload = strategy_execution_period_chain_store_contract_payload()

    assert payload["schema_version"] == STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION
    assert payload["explicit_storage_release_required"] is True
    assert payload["server_side_period_chain_rebuild_required"] is True
    assert payload["pre_storage_digest_check_enabled"] is True
    assert payload["post_storage_digest_check_enabled"] is True
    assert payload["on_read_digest_check_enabled"] is True
    assert payload["immutable_insert_only_enabled"] is True
    assert payload["idempotent_exact_replay_enabled"] is True
    assert payload["period_chain_update_enabled"] is False
    assert payload["browser_period_chain_payloads_accepted"] is False
    assert payload["period_chain_persistence_enabled"] is True
    assert payload["carryover_invocation_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR139"


def test_store_api_persists_replays_reads_and_enforces_methods(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    contract_endpoint = "/api/strategies/execution-period-chain-store-contract"
    store_endpoint = "/api/strategies/execution-period-chain-store"
    read_endpoint = (
        "/api/strategies/execution-period-chains/"
        f"{request['expected_chain_id']}"
    )

    contract = client.get(contract_endpoint)
    created = client.post(store_endpoint, json=request)
    replayed = client.post(store_endpoint, json=request)
    read = client.get(read_endpoint)

    assert contract.status_code == 200
    assert contract.json()["period_chain_persistence_enabled"] is True
    assert created.status_code == 201
    assert created.json()["new_record_created"] is True
    assert replayed.status_code == 200
    assert replayed.json()["replayed"] is True
    assert read.status_code == 200
    assert read.json()["record"]["chain_id"] == request["expected_chain_id"]
    assert client.post(contract_endpoint, json={}).status_code == 405
    assert client.get(store_endpoint).status_code == 405
    assert client.put(store_endpoint, json={}).status_code == 405
    assert client.delete(store_endpoint).status_code == 405
    assert client.post(read_endpoint, json={}).status_code == 405


def test_store_api_rejects_unconfigured_store_invalid_json_and_missing_chain(
    monkeypatch,
    tmp_path,
) -> None:
    store_endpoint = "/api/strategies/execution-period-chain-store"
    memory_client = TestClient(create_app(frontend_dist=tmp_path))

    unavailable = memory_client.post(store_endpoint, json={})

    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )
    assert unavailable.json()["period_chain_persisted"] is False

    db_path = tmp_path / "metadata.sqlite"
    request = _store_request(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    sqlite_client = TestClient(create_app(frontend_dist=tmp_path))

    invalid_json = sqlite_client.post(
        store_endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )
    created = sqlite_client.post(store_endpoint, json=request)
    missing = sqlite_client.get(
        "/api/strategies/execution-period-chains/missing-chain"
    )

    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert invalid_json.json()["next_gate"] == "PR139"
    assert created.status_code == 201
    assert missing.status_code == 404
    assert missing.json()["issues"][0]["code"] == "period_chain_not_found"
