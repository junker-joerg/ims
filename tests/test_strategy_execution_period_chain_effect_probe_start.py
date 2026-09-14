from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import sqlite3
from threading import Event

import pytest

from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
)
from ims.api.strategy_execution_period_chain_effect_probe import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION,
    parse_strategy_execution_period_chain_effect_probe_request,
)
from ims.api.strategy_execution_period_chain_effect_probe_start import (
    StrategyExecutionPeriodChainEffectProbeStartError,
    get_strategy_execution_period_chain_effect_probe_history,
    get_strategy_execution_period_chain_effect_probe_result,
    start_strategy_execution_period_chain_effect_probe,
    strategy_execution_period_chain_effect_probe_start_contract_payload,
)
from ims.api.strategy_execution_period_chain_run_control import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION,
)
from ims.api.strategy_execution_period_chain_store import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
    get_strategy_execution_period_chain,
    persist_strategy_execution_period_chain,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
)


def _persist_chain(
    db_path: Path,
    profile_root: Path,
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
    result = persist_strategy_execution_period_chain(
        {
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION
            ),
            "period_chain_input": value,
            "expected_chain_id": build.chain.chain_id,
            "expected_content_digest": build.chain.content_digest,
            "stored_at": "2026-09-14T09:00:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=db_path,
    )
    return result.record.chain_id, result.record.content_digest


def _request(
    chain_id: str,
    digest: str,
    *,
    idempotency_key: str = "pr140-two-period-start-001",
    release_reason: str = "Kontrollierter Zwei-Perioden-Start",
):
    return parse_strategy_execution_period_chain_effect_probe_request(
        {
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
                "released_by": "test-reviewer",
                "released_at": "2026-09-14T07:05:00Z",
                "release_reason": release_reason,
            },
            "explicit_two_period_effect_probe_execution": True,
        }
    )


def test_start_contract_opens_only_controlled_two_period_path() -> None:
    payload = strategy_execution_period_chain_effect_probe_start_contract_payload()

    assert payload["request_source"] == "pr139_effect_probe_request_unchanged"
    assert payload["ui_start_enabled"] is True
    assert payload["atomic_idempotency_claim_enabled"] is True
    assert payload["idempotency_persistence_enabled"] is True
    assert payload["immutable_result_persistence_enabled"] is True
    assert payload["attempt_history_enabled"] is True
    assert payload["exact_two_period_horizon_required"] is True
    assert payload["stored_transition_flags_authoritative"] is True
    assert payload["automatic_retry_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["output_files_enabled"] is False
    assert payload["general_multi_period_execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR143"


def test_readers_report_empty_without_creating_evidence_tables(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)

    result = get_strategy_execution_period_chain_effect_probe_result(
        chain_id,
        db_path=db_path,
    ).to_dict()
    history = get_strategy_execution_period_chain_effect_probe_history(
        chain_id,
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
    assert "strategy_execution_period_chain_effect_probe_attempts" not in names
    assert "strategy_execution_period_chain_effect_probe_results" not in names


def test_start_persists_result_and_replays_without_more_runner_calls(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)
    chain_before = deepcopy(
        get_strategy_execution_period_chain(chain_id, db_path=db_path).record.to_dict()
    )
    calls = 0

    def counting_runner(loaded, *, output_dir=None):
        nonlocal calls
        calls += 1
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    request = _request(chain_id, digest)
    first = start_strategy_execution_period_chain_effect_probe(
        request,
        db_path=db_path,
        runner=counting_runner,
        timestamp_factory=lambda: "2026-09-14T07:05:01Z",
    )
    replay = start_strategy_execution_period_chain_effect_probe(
        request,
        db_path=db_path,
        runner=counting_runner,
        timestamp_factory=lambda: "2026-09-14T07:05:02Z",
    )

    assert first.replayed is False
    assert replay.replayed is True
    assert first.record == replay.record
    assert calls == 2
    assert first.to_dict()["runner_invocation_count"] == 2
    assert replay.to_dict()["runner_invocation_count"] == 0
    assert replay.to_dict()["writes_performed"] is False
    assert first.to_dict()["result_persisted"] is True
    assert first.to_dict()["simulation_performed"] is False
    assert first.record.result_digest.startswith("sha256:")
    assert [
        effect["period"]
        for effect in first.record.result_payload["period_effects"]
    ] == [1, 2]
    assert first.record.result_payload["transition_effect"]["to_period"] == 2
    assert (
        get_strategy_execution_period_chain(
            chain_id,
            db_path=db_path,
        ).record.to_dict()
        == chain_before
    )

    history = get_strategy_execution_period_chain_effect_probe_history(
        chain_id,
        db_path=db_path,
    ).to_dict()
    assert history["attempt_count"] == 1
    assert history["latest_attempt"]["status"] == "result_persisted"
    assert history["latest_attempt"]["runner_invocation_count"] == 2
    assert history["latest_attempt"]["candidate_reverified_count"] == 2
    assert history["latest_attempt"]["result_persisted"] is True
    assert history["result_available"] is True


def test_same_idempotency_key_rejects_changed_release_payload(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)
    start_strategy_execution_period_chain_effect_probe(
        _request(chain_id, digest),
        db_path=db_path,
    )

    changed = _request(
        chain_id,
        digest,
        release_reason="Geaenderte Kettenfreigabe",
    )
    with pytest.raises(
        StrategyExecutionPeriodChainEffectProbeStartError
    ) as exc_info:
        start_strategy_execution_period_chain_effect_probe(
            changed,
            db_path=db_path,
        )

    assert exc_info.value.code == "idempotency_payload_conflict"
    assert exc_info.value.release_check is not None
    assert exc_info.value.release_check.release_ready is True
    assert exc_info.value.runner_invocation_count == 0


def test_second_key_cannot_duplicate_persisted_chain_result(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)
    start_strategy_execution_period_chain_effect_probe(
        _request(chain_id, digest),
        db_path=db_path,
    )

    with pytest.raises(
        StrategyExecutionPeriodChainEffectProbeStartError
    ) as exc_info:
        start_strategy_execution_period_chain_effect_probe(
            _request(
                chain_id,
                digest,
                idempotency_key="pr140-two-period-start-002",
            ),
            db_path=db_path,
        )

    assert exc_info.value.code == "period_chain_result_already_persisted"


def test_concurrent_duplicate_is_blocked_by_atomic_claim(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)
    request = _request(chain_id, digest)
    entered = Event()
    finish = Event()
    calls = 0

    def blocking_runner(loaded, *, output_dir=None):
        nonlocal calls
        calls += 1
        if calls == 1:
            entered.set()
            assert finish.wait(timeout=5)
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            start_strategy_execution_period_chain_effect_probe,
            request,
            db_path=db_path,
            runner=blocking_runner,
        )
        assert entered.wait(timeout=5)
        with pytest.raises(
            StrategyExecutionPeriodChainEffectProbeStartError
        ) as exc_info:
            start_strategy_execution_period_chain_effect_probe(
                request,
                db_path=db_path,
                runner=blocking_runner,
            )
        finish.set()
        result = future.result(timeout=5)

    assert exc_info.value.code == "idempotency_attempt_not_replayable"
    assert result.replayed is False
    assert calls == 2


def test_second_runner_failure_is_recorded_without_partial_result(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)

    def failing_runner(loaded, *, output_dir=None):
        if loaded.context.period == 2:
            raise RuntimeError("synthetic PR140 second runner failure")
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    with pytest.raises(
        StrategyExecutionPeriodChainEffectProbeStartError
    ) as exc_info:
        start_strategy_execution_period_chain_effect_probe(
            _request(chain_id, digest),
            db_path=db_path,
            runner=failing_runner,
        )

    assert exc_info.value.code == "effect_probe_runner_failed"
    assert exc_info.value.runner_invocation_count == 2
    assert exc_info.value.writes_performed is True
    failed_history = get_strategy_execution_period_chain_effect_probe_history(
        chain_id,
        db_path=db_path,
    ).to_dict()
    assert failed_history["attempt_count"] == 1
    assert failed_history["latest_attempt"]["status"] == "failed"
    assert failed_history["latest_attempt"]["runner_invocation_count"] == 2
    assert failed_history["result_available"] is False

    retry = start_strategy_execution_period_chain_effect_probe(
        _request(
            chain_id,
            digest,
            idempotency_key="pr140-two-period-start-retry-001",
        ),
        db_path=db_path,
    )
    assert retry.replayed is False
    final_history = get_strategy_execution_period_chain_effect_probe_history(
        chain_id,
        db_path=db_path,
    ).to_dict()
    assert final_history["attempt_count"] == 2
    assert {attempt["status"] for attempt in final_history["attempts"]} == {
        "failed",
        "result_persisted",
    }


def test_long_horizon_fails_before_runner_but_records_attempt(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path, max_periods=3)
    calls = 0

    def counting_runner(loaded, *, output_dir=None):
        nonlocal calls
        calls += 1
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    with pytest.raises(
        StrategyExecutionPeriodChainEffectProbeStartError
    ) as exc_info:
        start_strategy_execution_period_chain_effect_probe(
            _request(chain_id, digest),
            db_path=db_path,
            runner=counting_runner,
        )

    assert exc_info.value.code == "exact_two_period_horizon_required"
    assert exc_info.value.runner_invocation_count == 0
    assert calls == 0
    history = get_strategy_execution_period_chain_effect_probe_history(
        chain_id,
        db_path=db_path,
    ).to_dict()
    assert history["latest_attempt"]["status"] == "failed"
    assert history["latest_attempt"]["runner_invocation_count"] == 0


def test_result_reader_rejects_tampered_persisted_payload(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)
    start_strategy_execution_period_chain_effect_probe(
        _request(chain_id, digest),
        db_path=db_path,
    )
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            UPDATE strategy_execution_period_chain_effect_probe_results
            SET result_payload_json = '{"status":"changed"}'
            WHERE chain_id = ?
            """,
            (chain_id,),
        )

    with pytest.raises(
        StrategyExecutionPeriodChainEffectProbeStartError
    ) as exc_info:
        get_strategy_execution_period_chain_effect_probe_result(
            chain_id,
            db_path=db_path,
        )

    assert exc_info.value.code == "effect_probe_result_digest_mismatch"
