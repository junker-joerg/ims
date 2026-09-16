from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import sqlite3
from threading import Event

import pytest

from ims.api.strategy_execution_period_chain_five_period_build import (
    build_strategy_execution_five_period_chain,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe import (
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe_start import (
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION,
    StrategyExecutionFivePeriodEffectProbeStartError,
    get_strategy_execution_five_period_effect_probe_history,
    get_strategy_execution_five_period_effect_probe_result,
    parse_strategy_execution_five_period_effect_probe_start_request,
    start_strategy_execution_five_period_effect_probe,
    strategy_execution_five_period_effect_probe_start_contract_payload,
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


def _prepared_start_request(
    tmp_path: Path,
    *,
    idempotency_key: str = "pr145-five-period-start-001",
    release_reason: str = "Kontrollierter Fuenf-Perioden-Start",
):
    db_path = tmp_path / "metadata.sqlite"
    baseline = persist_two_period_effect_probe_baseline(
        db_path,
        tmp_path / "baseline",
        run_index=5,
    )
    five_root = tmp_path / "five"
    five_root.mkdir(exist_ok=True)
    references = persist_chain_candidates(
        db_path,
        five_root,
        run_index=2,
        max_periods=5,
    )
    value = chain_input(references, run_index=2, max_periods=5)
    build = build_strategy_execution_five_period_chain(value, db_path=db_path)
    assert build.chain is not None, build.issues
    payload = {
        "schema_version": (
            STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION
        ),
        "effect_probe_request": {
            "schema_version": (
                STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION
            ),
            "period_chain_input": deepcopy(value),
            "prefix_baseline": dict(baseline),
            "explicit_five_period_effect_probe_execution": True,
        },
        "release": {
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
            ),
            "chain_id": build.chain.chain_id,
            "expected_content_digest": build.chain.content_digest,
            "idempotency_key": idempotency_key,
            "explicit_run_control_release": True,
            "released_by": "test-reviewer",
            "released_at": "2026-09-14T09:05:00Z",
            "release_reason": release_reason,
        },
        "explicit_five_period_effect_probe_start": True,
    }
    return (
        db_path,
        build.chain.chain_id,
        build.chain.content_digest,
        payload,
    )


def test_start_contract_opens_only_persisted_five_period_path() -> None:
    payload = strategy_execution_five_period_effect_probe_start_contract_payload()

    assert payload["request_source"] == (
        "pr144_effect_probe_request_wrapped_unchanged"
    )
    assert payload["server_start_enabled"] is True
    assert payload["ui_start_enabled"] is True
    assert payload["atomic_idempotency_claim_enabled"] is True
    assert payload["idempotency_persistence_enabled"] is True
    assert payload["immutable_period_chain_snapshot_persistence_enabled"] is True
    assert payload["immutable_result_persistence_enabled"] is True
    assert payload["exact_five_period_horizon_required"] is True
    assert payload["stored_two_period_prefix_baseline_required"] is True
    assert payload["automatic_retry_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["output_files_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR148"


def test_parser_rejects_unreleased_or_ambiguous_start(tmp_path) -> None:
    _, _, _, payload = _prepared_start_request(tmp_path)
    payload["explicit_five_period_effect_probe_start"] = False
    with pytest.raises(StrategyExecutionFivePeriodEffectProbeStartError) as exc_info:
        parse_strategy_execution_five_period_effect_probe_start_request(payload)
    assert exc_info.value.code == "five_period_effect_probe_start_release_required"

    payload["explicit_five_period_effect_probe_start"] = True
    payload["output_dir"] = "output"
    with pytest.raises(StrategyExecutionFivePeriodEffectProbeStartError) as exc_info:
        parse_strategy_execution_five_period_effect_probe_start_request(payload)
    assert exc_info.value.code == "unknown_request_fields"


def test_readers_are_empty_without_creating_evidence_tables(tmp_path) -> None:
    db_path, chain_id, _, _ = _prepared_start_request(tmp_path)

    result = get_strategy_execution_five_period_effect_probe_result(
        chain_id,
        db_path=db_path,
    ).to_dict()
    history = get_strategy_execution_five_period_effect_probe_history(
        chain_id,
        db_path=db_path,
    ).to_dict()

    assert result["result_available"] is False
    assert history["attempt_count"] == 0
    assert history["result_available"] is False
    with sqlite3.connect(db_path) as connection:
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert "strategy_execution_five_period_effect_probe_attempts" not in names
    assert "strategy_execution_five_period_effect_probe_results" not in names


def test_start_persists_complete_evidence_and_replays_without_runner(
    tmp_path,
) -> None:
    db_path, chain_id, digest, payload = _prepared_start_request(tmp_path)
    request = parse_strategy_execution_five_period_effect_probe_start_request(payload)
    calls: list[int] = []

    def counting_runner(loaded, *, output_dir=None):
        calls.append(loaded.context.period)
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    first = start_strategy_execution_five_period_effect_probe(
        request,
        db_path=db_path,
        runner=counting_runner,
        timestamp_factory=lambda: "2026-09-14T09:05:01Z",
    )
    replay = start_strategy_execution_five_period_effect_probe(
        request,
        db_path=db_path,
        runner=counting_runner,
        timestamp_factory=lambda: "2026-09-14T09:05:02Z",
    )

    assert first.replayed is False
    assert replay.replayed is True
    assert first.record == replay.record
    assert calls == [1, 2, 3, 4, 5]
    assert first.record.chain_id == chain_id
    assert first.record.content_digest == digest
    assert first.record.result_digest.startswith("sha256:")
    assert first.record.period_chain_payload["identity"] == {
        "chain_id": chain_id,
        "content_digest": digest,
        "schema_version": "ims.strategy-execution-period-chain.v1",
    }
    assert [
        effect["period"] for effect in first.record.result_payload["period_effects"]
    ] == [1, 2, 3, 4, 5]
    assert first.record.result_payload["two_period_prefix_verified"] is True
    assert first.to_dict()["runner_invocation_count"] == 5
    assert replay.to_dict()["runner_invocation_count"] == 0
    assert replay.to_dict()["writes_performed"] is False
    assert first.to_dict()["immutable_period_chain_snapshot_persisted"] is True
    assert first.to_dict()["simulation_performed"] is False

    read = get_strategy_execution_five_period_effect_probe_result(
        chain_id,
        db_path=db_path,
    ).to_dict()
    history = get_strategy_execution_five_period_effect_probe_history(
        chain_id,
        db_path=db_path,
    ).to_dict()
    assert read["result_available"] is True
    assert read["record"]["result_digest"] == first.record.result_digest
    assert history["attempt_count"] == 1
    assert history["latest_attempt"]["status"] == "result_persisted"
    assert history["latest_attempt"]["runner_invocation_count"] == 5
    assert history["latest_attempt"]["carryover_invocation_count"] == 8
    assert history["latest_attempt"]["candidate_reverified_count"] == 5
    assert history["latest_attempt"]["prefix_baseline_verified"] is True


def test_same_key_rejects_changed_payload_before_runner(tmp_path) -> None:
    db_path, _, _, payload = _prepared_start_request(tmp_path)
    start_strategy_execution_five_period_effect_probe(
        parse_strategy_execution_five_period_effect_probe_start_request(payload),
        db_path=db_path,
    )
    changed = deepcopy(payload)
    changed["release"]["release_reason"] = "Geaenderte Freigabe"

    with pytest.raises(StrategyExecutionFivePeriodEffectProbeStartError) as exc_info:
        start_strategy_execution_five_period_effect_probe(
            parse_strategy_execution_five_period_effect_probe_start_request(changed),
            db_path=db_path,
        )

    assert exc_info.value.code == "idempotency_payload_conflict"
    assert exc_info.value.runner_invocation_count == 0


def test_replay_remains_readable_without_source_candidates_or_prefix(tmp_path) -> None:
    db_path, chain_id, _, payload = _prepared_start_request(tmp_path)
    request = parse_strategy_execution_five_period_effect_probe_start_request(payload)
    first = start_strategy_execution_five_period_effect_probe(
        request,
        db_path=db_path,
    )
    with sqlite3.connect(db_path) as connection:
        connection.execute("DELETE FROM strategy_execution_candidates")
        connection.execute(
            "DELETE FROM strategy_execution_period_chain_effect_probe_results"
        )

    replay = start_strategy_execution_five_period_effect_probe(
        request,
        db_path=db_path,
    )
    read = get_strategy_execution_five_period_effect_probe_result(
        chain_id,
        db_path=db_path,
    )

    assert replay.replayed is True
    assert replay.record == first.record
    assert replay.to_dict()["runner_invocation_count"] == 0
    assert replay.to_dict()["writes_performed"] is False
    assert read.record == first.record


def test_concurrent_duplicate_is_blocked_by_atomic_claim(tmp_path) -> None:
    db_path, _, _, payload = _prepared_start_request(tmp_path)
    request = parse_strategy_execution_five_period_effect_probe_start_request(payload)
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
            start_strategy_execution_five_period_effect_probe,
            request,
            db_path=db_path,
            runner=blocking_runner,
        )
        assert entered.wait(timeout=5)
        with pytest.raises(
            StrategyExecutionFivePeriodEffectProbeStartError
        ) as exc_info:
            start_strategy_execution_five_period_effect_probe(
                request,
                db_path=db_path,
                runner=blocking_runner,
            )
        finish.set()
        result = future.result(timeout=5)

    assert exc_info.value.code == "idempotency_attempt_not_replayable"
    assert result.replayed is False
    assert calls == 5


def test_second_key_cannot_replace_immutable_result(tmp_path) -> None:
    db_path, _, _, payload = _prepared_start_request(tmp_path)
    start_strategy_execution_five_period_effect_probe(
        parse_strategy_execution_five_period_effect_probe_start_request(payload),
        db_path=db_path,
    )
    changed = deepcopy(payload)
    changed["release"]["idempotency_key"] = "pr145-five-period-start-002"

    with pytest.raises(StrategyExecutionFivePeriodEffectProbeStartError) as exc_info:
        start_strategy_execution_five_period_effect_probe(
            parse_strategy_execution_five_period_effect_probe_start_request(changed),
            db_path=db_path,
        )

    assert exc_info.value.code == "five_period_result_already_persisted"


def test_fourth_runner_failure_is_recorded_without_partial_result(tmp_path) -> None:
    db_path, chain_id, _, payload = _prepared_start_request(tmp_path)

    def failing_runner(loaded, *, output_dir=None):
        if loaded.context.period == 4:
            raise RuntimeError("synthetic PR145 fourth runner failure")
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    with pytest.raises(StrategyExecutionFivePeriodEffectProbeStartError) as exc_info:
        start_strategy_execution_five_period_effect_probe(
            parse_strategy_execution_five_period_effect_probe_start_request(payload),
            db_path=db_path,
            runner=failing_runner,
        )

    assert exc_info.value.code == "effect_probe_runner_failed"
    assert exc_info.value.runner_invocation_count == 4
    assert exc_info.value.carryover_invocation_count == 6
    assert exc_info.value.prefix_baseline_verified is True
    assert exc_info.value.period_chain_digest_reverified is True
    history = get_strategy_execution_five_period_effect_probe_history(
        chain_id,
        db_path=db_path,
    ).to_dict()
    assert history["latest_attempt"]["status"] == "failed"
    assert history["latest_attempt"]["runner_invocation_count"] == 4
    assert history["result_available"] is False


@pytest.mark.parametrize(
    ("column", "value", "expected_code"),
    [
        (
            "period_chain_payload_json",
            '{"status":"changed"}',
            "five_period_result_digest_mismatch",
        ),
        (
            "result_payload_json",
            '{"status":"changed"}',
            "five_period_result_digest_mismatch",
        ),
    ],
)
def test_result_reader_rejects_tampered_complete_evidence(
    tmp_path,
    column: str,
    value: str,
    expected_code: str,
) -> None:
    db_path, chain_id, _, payload = _prepared_start_request(tmp_path)
    start_strategy_execution_five_period_effect_probe(
        parse_strategy_execution_five_period_effect_probe_start_request(payload),
        db_path=db_path,
    )
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            f"UPDATE strategy_execution_five_period_effect_probe_results "
            f"SET {column} = ? WHERE chain_id = ?",
            (value, chain_id),
        )

    with pytest.raises(StrategyExecutionFivePeriodEffectProbeStartError) as exc_info:
        get_strategy_execution_five_period_effect_probe_result(
            chain_id,
            db_path=db_path,
        )

    assert exc_info.value.code == expected_code
