import importlib
import json
from pathlib import Path
import sqlite3

import pytest

from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_STORE_VERSION,
    StrategyExecutionCandidateStoreError,
    get_strategy_execution_candidate,
    persist_strategy_execution_candidate,
    strategy_execution_candidate_store_contract_payload,
)
from ims.strategies import (
    build_default_strategy_execution_scenario_profiles,
    build_strategy_execution_candidate,
    strategy_execution_scenario_profile_root,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT_FIXTURE = (
    ROOT / "tests" / "fixtures" / "strategy_execution_candidate_input_v1.json"
)


def _candidate_input() -> dict[str, object]:
    return json.loads(INPUT_FIXTURE.read_text(encoding="utf-8"))


def _store_request(*, stored_at: str = "2026-09-08T12:00:00+02:00") -> dict[str, object]:
    candidate_input = _candidate_input()
    build = build_strategy_execution_candidate(
        candidate_input,
        profiles=build_default_strategy_execution_scenario_profiles(),
        trusted_profile_root=strategy_execution_scenario_profile_root(),
    )
    assert build.candidate is not None
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
        "candidate_input": candidate_input,
        "expected_candidate_id": build.candidate.candidate_id,
        "expected_content_digest": build.candidate.content_digest,
        "stored_at": stored_at,
        "explicit_storage_release": True,
    }


def _persist(value: object, db_path: Path):
    return persist_strategy_execution_candidate(
        value,
        db_path=db_path,
        profiles=build_default_strategy_execution_scenario_profiles(),
        trusted_profile_root=strategy_execution_scenario_profile_root(),
    )


def test_persists_and_reads_verified_immutable_candidate(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request()

    persisted = _persist(request, db_path)
    read = get_strategy_execution_candidate(
        request["expected_candidate_id"],
        db_path=db_path,
    )

    payload = persisted.to_dict()
    assert payload["schema_version"] == STRATEGY_EXECUTION_CANDIDATE_STORE_VERSION
    assert payload["candidate_persisted"] is True
    assert payload["new_record_created"] is True
    assert payload["replayed"] is False
    assert payload["writes_performed"] is True
    assert payload["pre_storage_digest_verified"] is True
    assert payload["post_storage_digest_verified"] is True
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert read.record == persisted.record
    assert read.to_dict()["writes_performed"] is False
    assert read.to_dict()["post_storage_digest_verified"] is True
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT candidate_id, content_digest FROM strategy_execution_candidates"
        ).fetchone()
    assert row == (
        request["expected_candidate_id"],
        request["expected_content_digest"],
    )


def test_exact_replay_is_idempotent_and_keeps_original_timestamp(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    first_request = _store_request(stored_at="2026-09-08T12:00:00+02:00")
    replay_request = {
        **first_request,
        "stored_at": "2026-09-08T12:05:00+02:00",
    }

    first = _persist(first_request, db_path)
    replay = _persist(replay_request, db_path)

    assert first.new_record_created is True
    assert replay.new_record_created is False
    assert replay.replayed is True
    assert replay.to_dict()["writes_performed"] is False
    assert replay.record.stored_at == "2026-09-08T12:00:00+02:00"
    with sqlite3.connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM strategy_execution_candidates"
        ).fetchone()[0]
    assert count == 1


def test_requires_explicit_release_before_creating_database(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request()
    request["explicit_storage_release"] = False

    with pytest.raises(StrategyExecutionCandidateStoreError) as exc_info:
        _persist(request, db_path)

    assert exc_info.value.code == "storage_release_required"
    assert not db_path.exists()


def test_rejects_expected_digest_mismatch_before_creating_database(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request()
    request["expected_content_digest"] = "sha256:" + "0" * 64
    request["expected_candidate_id"] = "strategy-candidate-" + "0" * 24

    with pytest.raises(StrategyExecutionCandidateStoreError) as exc_info:
        _persist(request, db_path)

    assert exc_info.value.code == "candidate_id_mismatch"
    assert not db_path.exists()


def test_failed_rebuild_is_atomic_and_creates_no_database(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request()
    request["candidate_input"]["scenario_profile_reference"][
        "profile_id"
    ] = "unknown-profile"

    with pytest.raises(StrategyExecutionCandidateStoreError) as exc_info:
        _persist(request, db_path)

    assert exc_info.value.code == "candidate_rebuild_failed"
    assert not db_path.exists()


def test_existing_modified_record_is_rejected_without_repair(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request()
    _persist(request, db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE strategy_execution_candidates SET draft_id = ?",
            ("modified-draft",),
        )

    with pytest.raises(StrategyExecutionCandidateStoreError) as exc_info:
        _persist(request, db_path)

    assert exc_info.value.code == "stored_candidate_metadata_mismatch"
    with sqlite3.connect(db_path) as connection:
        draft_id = connection.execute(
            "SELECT draft_id FROM strategy_execution_candidates"
        ).fetchone()[0]
    assert draft_id == "modified-draft"


def test_read_detects_candidate_payload_corruption(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    request = _store_request()
    persisted = _persist(request, db_path)
    damaged = persisted.record.candidate
    damaged["identity"]["draft_id"] = "damaged-draft"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE strategy_execution_candidates SET candidate_payload_json = ?",
            (json.dumps(damaged, sort_keys=True),),
        )

    with pytest.raises(StrategyExecutionCandidateStoreError) as exc_info:
        get_strategy_execution_candidate(
            request["expected_candidate_id"],
            db_path=db_path,
        )

    assert exc_info.value.code == "candidate_digest_verification_failed"


def test_store_does_not_invoke_runner(monkeypatch, tmp_path) -> None:
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"runner invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)

    result = _persist(_store_request(), tmp_path / "metadata.sqlite")

    assert result.to_dict()["run_control_connected"] is False
    assert result.to_dict()["runner_invocation_performed"] is False
    assert result.to_dict()["execution_performed"] is False
    assert result.to_dict()["simulation_performed"] is False


def test_store_contract_opens_only_explicit_immutable_persistence() -> None:
    payload = strategy_execution_candidate_store_contract_payload()

    assert payload["schema_version"] == STRATEGY_EXECUTION_CANDIDATE_STORE_VERSION
    assert payload["explicit_storage_release_required"] is True
    assert payload["server_side_candidate_rebuild_required"] is True
    assert payload["pre_storage_digest_check_enabled"] is True
    assert payload["post_storage_digest_check_enabled"] is True
    assert payload["immutable_insert_only_enabled"] is True
    assert payload["idempotent_exact_replay_enabled"] is True
    assert payload["candidate_update_enabled"] is False
    assert payload["browser_candidate_payloads_accepted"] is False
    assert payload["candidate_persistence_enabled"] is True
    assert payload["run_control_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["simulation_performed"] is False
