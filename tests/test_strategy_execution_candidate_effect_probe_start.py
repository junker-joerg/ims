from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
from threading import Event

import pytest

from ims.api.strategy_execution_candidate_effect_probe import (
    STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION,
    parse_strategy_execution_candidate_effect_probe_request,
)
from ims.api.strategy_execution_candidate_effect_probe_start import (
    StrategyExecutionCandidateEffectProbeStartError,
    get_strategy_execution_candidate_effect_probe_history,
    get_strategy_execution_candidate_effect_probe_result,
    start_strategy_execution_candidate_effect_probe,
    strategy_execution_candidate_effect_probe_start_contract_payload,
)
from ims.api.strategy_execution_candidate_run_control import (
    STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
)
from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
    get_strategy_execution_candidate,
    persist_strategy_execution_candidate,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period
from ims.strategies import (
    build_default_strategy_execution_scenario_profiles,
    build_strategy_execution_candidate,
    strategy_execution_scenario_profile_root,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_execution_candidate_input_v1.json"
)


def _persist_candidate(db_path: Path) -> tuple[str, str]:
    candidate_input = json.loads(FIXTURE.read_text(encoding="utf-8"))
    profiles = build_default_strategy_execution_scenario_profiles()
    profile_root = strategy_execution_scenario_profile_root()
    build = build_strategy_execution_candidate(
        candidate_input,
        profiles=profiles,
        trusted_profile_root=profile_root,
    )
    assert build.candidate is not None
    candidate_id = build.candidate.candidate_id
    digest = build.candidate.content_digest
    persist_strategy_execution_candidate(
        {
            "schema_version": STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
            "candidate_input": candidate_input,
            "expected_candidate_id": candidate_id,
            "expected_content_digest": digest,
            "stored_at": "2026-09-09T09:00:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=db_path,
        profiles=profiles,
        trusted_profile_root=profile_root,
    )
    return candidate_id, digest


def _request(
    candidate_id: str,
    digest: str,
    *,
    idempotency_key: str = "pr131-effect-probe-start-001",
    release_reason: str = "Kontrollierter Workbench-Start",
):
    return parse_strategy_execution_candidate_effect_probe_request(
        {
            "schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION
            ),
            "release": {
                "schema_version": (
                    STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION
                ),
                "candidate_id": candidate_id,
                "expected_content_digest": digest,
                "idempotency_key": idempotency_key,
                "explicit_run_control_release": True,
                "released_by": "test-reviewer",
                "released_at": "2026-09-09T08:00:00Z",
                "release_reason": release_reason,
            },
            "explicit_effect_probe_execution": True,
        }
    )


def test_start_contract_opens_only_persisted_single_period_path() -> None:
    payload = strategy_execution_candidate_effect_probe_start_contract_payload()

    assert payload["request_source"] == "pr130_effect_probe_request_unchanged"
    assert payload["ui_start_enabled"] is True
    assert payload["atomic_idempotency_claim_enabled"] is True
    assert payload["idempotency_persistence_enabled"] is True
    assert payload["immutable_result_persistence_enabled"] is True
    assert payload["attempt_history_enabled"] is True
    assert payload["single_period_only"] is True
    assert payload["automatic_retry_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["carryover_enabled"] is False
    assert payload["output_files_enabled"] is False
    assert payload["multi_period_execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR134"


def test_readers_report_empty_without_creating_evidence_tables(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)

    result = get_strategy_execution_candidate_effect_probe_result(
        candidate_id,
        db_path=db_path,
    ).to_dict()
    history = get_strategy_execution_candidate_effect_probe_history(
        candidate_id,
        db_path=db_path,
    ).to_dict()

    assert result["content_digest"] == digest
    assert result["result_available"] is False
    assert result["record"] is None
    assert history["attempt_count"] == 0
    assert history["attempts"] == []
    assert history["result_available"] is False
    assert history["writes_performed"] is False
    with sqlite3.connect(db_path) as connection:
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert "strategy_execution_candidate_effect_probe_attempts" not in names
    assert "strategy_execution_candidate_effect_probe_results" not in names


def test_start_persists_result_and_replays_without_second_runner(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    candidate_before = deepcopy(
        get_strategy_execution_candidate(candidate_id, db_path=db_path).record.to_dict()
    )
    calls = 0

    def counting_runner(loaded, *, output_dir=None):
        nonlocal calls
        calls += 1
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    request = _request(candidate_id, digest)
    first = start_strategy_execution_candidate_effect_probe(
        request,
        db_path=db_path,
        runner=counting_runner,
        timestamp_factory=lambda: "2026-09-09T08:00:01Z",
    )
    replay = start_strategy_execution_candidate_effect_probe(
        request,
        db_path=db_path,
        runner=counting_runner,
        timestamp_factory=lambda: "2026-09-09T08:00:02Z",
    )

    assert first.replayed is False
    assert replay.replayed is True
    assert first.record == replay.record
    assert calls == 1
    first_payload = first.to_dict()
    replay_payload = replay.to_dict()
    assert first_payload["runner_invocation_count"] == 1
    assert replay_payload["runner_invocation_count"] == 0
    assert first_payload["result_persisted"] is True
    assert first_payload["idempotency_persisted"] is True
    assert first_payload["simulation_performed"] is False
    assert first.record.result_digest.startswith("sha256:")
    assert first.record.result_payload["effect"]["period"] == 2
    assert first.record.result_payload["effect"]["applications"]["vu_total"] == 1
    assert get_strategy_execution_candidate(
        candidate_id,
        db_path=db_path,
    ).record.to_dict() == candidate_before

    history = get_strategy_execution_candidate_effect_probe_history(
        candidate_id,
        db_path=db_path,
    ).to_dict()
    assert history["attempt_count"] == 1
    assert history["latest_attempt"]["status"] == "result_persisted"
    assert history["latest_attempt"]["runner_invocation_performed"] is True
    assert history["latest_attempt"]["result_persisted"] is True
    assert history["result_available"] is True


def test_same_idempotency_key_rejects_changed_release_payload(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    request = _request(candidate_id, digest)
    start_strategy_execution_candidate_effect_probe(request, db_path=db_path)

    changed = _request(
        candidate_id,
        digest,
        release_reason="Geaenderte Freigabe",
    )
    with pytest.raises(StrategyExecutionCandidateEffectProbeStartError) as exc_info:
        start_strategy_execution_candidate_effect_probe(changed, db_path=db_path)

    assert exc_info.value.code == "idempotency_payload_conflict"
    assert exc_info.value.release_check is not None
    assert exc_info.value.release_check.release_ready is True
    assert exc_info.value.runner_invocation_performed is False


def test_second_idempotency_key_cannot_duplicate_persisted_candidate_result(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    start_strategy_execution_candidate_effect_probe(
        _request(candidate_id, digest),
        db_path=db_path,
    )

    with pytest.raises(StrategyExecutionCandidateEffectProbeStartError) as exc_info:
        start_strategy_execution_candidate_effect_probe(
            _request(
                candidate_id,
                digest,
                idempotency_key="pr131-effect-probe-start-002",
            ),
            db_path=db_path,
        )

    assert exc_info.value.code == "candidate_result_already_persisted"


def test_concurrent_duplicate_is_blocked_by_atomic_claim(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    request = _request(candidate_id, digest)
    entered = Event()
    finish = Event()
    calls = 0

    def blocking_runner(loaded, *, output_dir=None):
        nonlocal calls
        calls += 1
        entered.set()
        assert finish.wait(timeout=5)
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            start_strategy_execution_candidate_effect_probe,
            request,
            db_path=db_path,
            runner=blocking_runner,
        )
        assert entered.wait(timeout=5)
        with pytest.raises(
            StrategyExecutionCandidateEffectProbeStartError,
        ) as exc_info:
            start_strategy_execution_candidate_effect_probe(
                request,
                db_path=db_path,
                runner=blocking_runner,
            )
        finish.set()
        result = future.result(timeout=5)

    assert exc_info.value.code == "idempotency_attempt_not_replayable"
    assert result.replayed is False
    assert calls == 1


def test_failed_runner_is_recorded_and_new_manual_release_can_retry(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)

    def failing_runner(loaded, *, output_dir=None):
        assert output_dir is None
        raise RuntimeError("synthetic PR131 runner failure")

    with pytest.raises(StrategyExecutionCandidateEffectProbeStartError) as exc_info:
        start_strategy_execution_candidate_effect_probe(
            _request(candidate_id, digest),
            db_path=db_path,
            runner=failing_runner,
        )

    assert exc_info.value.code == "effect_probe_runner_failed"
    assert exc_info.value.runner_invocation_performed is True
    assert exc_info.value.writes_performed is True
    failed_history = get_strategy_execution_candidate_effect_probe_history(
        candidate_id,
        db_path=db_path,
    ).to_dict()
    assert failed_history["attempt_count"] == 1
    assert failed_history["latest_attempt"]["status"] == "failed"
    assert failed_history["latest_attempt"]["failure_code"] == (
        "effect_probe_runner_failed"
    )
    assert failed_history["result_available"] is False

    retry = start_strategy_execution_candidate_effect_probe(
        _request(
            candidate_id,
            digest,
            idempotency_key="pr131-effect-probe-start-retry-001",
        ),
        db_path=db_path,
    )
    assert retry.replayed is False
    final_history = get_strategy_execution_candidate_effect_probe_history(
        candidate_id,
        db_path=db_path,
    ).to_dict()
    assert final_history["attempt_count"] == 2
    assert {attempt["status"] for attempt in final_history["attempts"]} == {
        "failed",
        "result_persisted",
    }


def test_result_reader_rejects_tampered_persisted_payload(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    start_strategy_execution_candidate_effect_probe(
        _request(candidate_id, digest),
        db_path=db_path,
    )
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            UPDATE strategy_execution_candidate_effect_probe_results
            SET result_payload_json = '{"status":"changed"}'
            WHERE candidate_id = ?
            """,
            (candidate_id,),
        )

    with pytest.raises(StrategyExecutionCandidateEffectProbeStartError) as exc_info:
        get_strategy_execution_candidate_effect_probe_result(
            candidate_id,
            db_path=db_path,
        )

    assert exc_info.value.code == "effect_probe_result_digest_mismatch"
