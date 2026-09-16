from copy import deepcopy
from hashlib import sha256
import sqlite3

import pytest

from ims.api.strategy_execution_period_chain_five_period_effect_probe import (
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_VERSION,
    StrategyExecutionFivePeriodEffectProbeError,
    parse_strategy_execution_five_period_effect_probe_request,
    run_strategy_execution_five_period_effect_probe,
    strategy_execution_five_period_effect_probe_contract_payload,
    strategy_execution_five_period_effect_probe_error_payload,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
    persist_two_period_effect_probe_baseline,
)


def _request(
    period_chain_input: dict[str, object],
    baseline: dict[str, str],
) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
        "period_chain_input": deepcopy(period_chain_input),
        "prefix_baseline": dict(baseline),
        "explicit_five_period_effect_probe_execution": True,
    }


def _prepared_request(tmp_path, *, five_period_run_index: int = 2):
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
        run_index=five_period_run_index,
        max_periods=5,
    )
    value = chain_input(
        references,
        run_index=five_period_run_index,
        max_periods=5,
    )
    return db_path, baseline, value


def test_contract_opens_only_ephemeral_five_period_probe() -> None:
    payload = strategy_execution_five_period_effect_probe_contract_payload()

    assert payload["scope"] == (
        "one_ephemeral_chain_five_isolated_periods_four_transitions"
    )
    assert payload["exact_five_period_horizon_required"] is True
    assert payload["stored_two_period_prefix_baseline_required"] is True
    assert payload["all_inputs_validated_before_first_runner"] is True
    assert payload["prefix_mismatch_blocks_periods_three_to_five"] is True
    assert payload["five_period_execution_enabled"] is True
    assert payload["result_persistence_enabled"] is False
    assert payload["ui_start_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR147"


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        (
            {"explicit_five_period_effect_probe_execution": False},
            "effect_probe_execution_release_required",
        ),
        ({"schema_version": "wrong"}, "unsupported_schema_version"),
        ({"output_dir": "output"}, "unknown_request_fields"),
    ],
)
def test_parser_rejects_unreleased_or_ambiguous_requests(
    change: dict[str, object],
    expected_code: str,
) -> None:
    baseline = {
        "chain_id": "strategy-period-chain-" + "1" * 24,
        "expected_content_digest": "sha256:" + "1" * 64,
        "expected_result_digest": "sha256:" + "2" * 64,
    }
    value = _request({"max_periods": 5}, baseline)
    value.update(change)

    with pytest.raises(StrategyExecutionFivePeriodEffectProbeError) as exc_info:
        parse_strategy_execution_five_period_effect_probe_request(value)

    assert exc_info.value.code == expected_code


def test_probe_runs_five_periods_and_proves_exact_two_period_prefix(
    tmp_path,
) -> None:
    db_path, baseline, value = _prepared_request(tmp_path)
    before_digest = sha256(db_path.read_bytes()).hexdigest()
    before_paths = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}
    calls: list[int] = []

    def counting_runner(loaded, *, output_dir=None):
        calls.append(loaded.context.period)
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    result = run_strategy_execution_five_period_effect_probe(
        parse_strategy_execution_five_period_effect_probe_request(
            _request(value, baseline)
        ),
        db_path=db_path,
        runner=counting_runner,
    )

    payload = result.to_dict()
    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_VERSION
    )
    assert payload["status"] == "ok"
    assert calls == [1, 2, 3, 4, 5]
    assert [effect["period"] for effect in payload["period_effects"]] == [
        1,
        2,
        3,
        4,
        5,
    ]
    assert [
        (effect["from_period"], effect["to_period"])
        for effect in payload["transition_effects"]
    ] == [(1, 2), (2, 3), (3, 4), (4, 5)]
    assert payload["runner_invocation_count"] == 5
    assert payload["carryover_invocation_count"] == 8
    assert payload["candidate_reverified_count"] == 5
    assert payload["two_period_prefix_verified"] is True
    assert payload["prefix_proof"]["semantic_equal"] is True
    assert payload["prefix_proof"]["canonical_json_byte_equal"] is True
    assert payload["prefix_proof"]["baseline_projection_digest"] == (
        payload["prefix_proof"]["five_period_projection_digest"]
    )
    assert payload["prefix_proof"]["tolerance_applied"] is False
    assert payload["execution_performed"] is True
    assert payload["writes_performed"] is False
    assert payload["result_persisted"] is False
    assert payload["output_files_written"] is False
    assert payload["simulation_performed"] is False
    assert sha256(db_path.read_bytes()).hexdigest() == before_digest
    assert {path.relative_to(tmp_path) for path in tmp_path.rglob("*")} == before_paths


def test_probe_is_deterministic_without_persistence(tmp_path) -> None:
    db_path, baseline, value = _prepared_request(tmp_path)
    request = parse_strategy_execution_five_period_effect_probe_request(
        _request(value, baseline)
    )

    first = run_strategy_execution_five_period_effect_probe(
        request,
        db_path=db_path,
    )
    second = run_strategy_execution_five_period_effect_probe(
        request,
        db_path=db_path,
    )

    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["idempotency_persisted"] is False
    assert first.to_dict()["result_persisted"] is False


def test_prefix_mismatch_blocks_periods_three_to_five_without_partial_result(
    tmp_path,
) -> None:
    db_path, baseline, value = _prepared_request(
        tmp_path,
        five_period_run_index=3,
    )
    calls: list[int] = []

    def counting_runner(loaded, *, output_dir=None):
        calls.append(loaded.context.period)
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    with pytest.raises(StrategyExecutionFivePeriodEffectProbeError) as exc_info:
        run_strategy_execution_five_period_effect_probe(
            parse_strategy_execution_five_period_effect_probe_request(
                _request(value, baseline)
            ),
            db_path=db_path,
            runner=counting_runner,
        )

    assert exc_info.value.code == "five_period_prefix_mismatch"
    assert exc_info.value.runner_invocation_count == 2
    assert exc_info.value.carryover_invocation_count == 2
    assert calls == [1, 2]
    error = strategy_execution_five_period_effect_probe_error_payload(
        exc_info.value.code,
        str(exc_info.value),
        runner_invocation_count=exc_info.value.runner_invocation_count,
        carryover_invocation_count=exc_info.value.carryover_invocation_count,
        candidate_reverified_count=exc_info.value.candidate_reverified_count,
        prefix_baseline_verified=exc_info.value.prefix_baseline_verified,
    )
    assert error["period_effects"] == []
    assert error["transition_effects"] == []
    assert error["partial_result_returned"] is False
    assert error["prefix_baseline_verified"] is True


def test_missing_prefix_baseline_blocks_before_first_runner(tmp_path) -> None:
    db_path, baseline, value = _prepared_request(tmp_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "DELETE FROM strategy_execution_period_chain_effect_probe_results "
            "WHERE chain_id = ?",
            (baseline["chain_id"],),
        )
    calls = 0

    def reject_runner(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise AssertionError(f"runner invoked with {args!r} {kwargs!r}")

    with pytest.raises(StrategyExecutionFivePeriodEffectProbeError) as exc_info:
        run_strategy_execution_five_period_effect_probe(
            parse_strategy_execution_five_period_effect_probe_request(
                _request(value, baseline)
            ),
            db_path=db_path,
            runner=reject_runner,
        )

    assert exc_info.value.code == "prefix_baseline_result_missing"
    assert exc_info.value.runner_invocation_count == 0
    assert calls == 0


def test_fourth_runner_failure_returns_no_partial_result(tmp_path) -> None:
    db_path, baseline, value = _prepared_request(tmp_path)
    calls: list[int] = []

    def failing_runner(loaded, *, output_dir=None):
        calls.append(loaded.context.period)
        if loaded.context.period == 4:
            raise RuntimeError("synthetic fourth runner failure")
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    with pytest.raises(StrategyExecutionFivePeriodEffectProbeError) as exc_info:
        run_strategy_execution_five_period_effect_probe(
            parse_strategy_execution_five_period_effect_probe_request(
                _request(value, baseline)
            ),
            db_path=db_path,
            runner=failing_runner,
        )

    assert exc_info.value.code == "effect_probe_runner_failed"
    assert exc_info.value.runner_invocation_count == 4
    assert exc_info.value.carryover_invocation_count == 6
    assert calls == [1, 2, 3, 4]
