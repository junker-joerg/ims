from hashlib import sha256
import importlib
import sqlite3

import pytest

from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
)
from ims.api.strategy_execution_period_chain_effect_probe import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_VERSION,
    StrategyExecutionPeriodChainEffectProbeError,
    parse_strategy_execution_period_chain_effect_probe_request,
    run_strategy_execution_period_chain_effect_probe,
    strategy_execution_period_chain_effect_probe_contract_payload,
    strategy_execution_period_chain_effect_probe_error_payload,
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


def _persisted_chain(
    db_path,
    profile_root,
    *,
    max_periods: int = 2,
    carry_forward_vu_state: bool = True,
    carry_forward_vn_state: bool = True,
) -> tuple[str, str]:
    references = persist_chain_candidates(
        db_path,
        profile_root,
        max_periods=max_periods,
    )
    value = chain_input(references, max_periods=max_periods)
    for transition in value["transitions"]:
        transition["carry_forward_vu_state"] = carry_forward_vu_state
        transition["carry_forward_vn_state"] = carry_forward_vn_state
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


def _release(chain_id: str, digest: str) -> dict[str, object]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
        ),
        "chain_id": chain_id,
        "expected_content_digest": digest,
        "idempotency_key": "pr139-two-period-probe-001",
        "explicit_run_control_release": True,
        "released_by": "test-reviewer",
        "released_at": "2026-09-11T13:05:00Z",
        "release_reason": "Kontrollierte Zwei-Perioden-Wirkungsprobe",
    }


def _request(chain_id: str, digest: str) -> dict[str, object]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION
        ),
        "release": _release(chain_id, digest),
        "explicit_two_period_effect_probe_execution": True,
    }


def test_contract_opens_only_ephemeral_two_period_probe() -> None:
    payload = strategy_execution_period_chain_effect_probe_contract_payload()

    assert payload["scope"] == (
        "one_released_chain_two_isolated_periods_one_transition"
    )
    assert payload["exact_two_period_horizon_required"] is True
    assert payload["candidate_re_resolution_required"] is True
    assert payload["all_inputs_validated_before_first_runner"] is True
    assert payload["isolated_candidate_copies_required"] is True
    assert payload["stored_transition_flags_authoritative"] is True
    assert payload["atomic_partial_result_suppression_enabled"] is True
    assert payload["effect_probe_execution_enabled"] is True
    assert payload["ui_start_enabled"] is False
    assert payload["queue_write_enabled"] is False
    assert payload["idempotency_persistence_enabled"] is False
    assert payload["result_persistence_enabled"] is False
    assert payload["output_files_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR140"


def test_parser_reuses_exact_pr138_release() -> None:
    digest = "sha256:" + "1" * 64
    value = _request("strategy-period-chain-" + "1" * 24, digest)

    parsed = parse_strategy_execution_period_chain_effect_probe_request(value)

    assert parsed.to_dict() == value


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        (
            {"explicit_two_period_effect_probe_execution": False},
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
    digest = "sha256:" + "1" * 64
    value = _request("strategy-period-chain-" + "1" * 24, digest)
    value.update(change)

    with pytest.raises(StrategyExecutionPeriodChainEffectProbeError) as exc_info:
        parse_strategy_execution_period_chain_effect_probe_request(value)

    assert exc_info.value.code == expected_code


def test_probe_runs_two_periods_on_isolated_copies_without_writes(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_chain(db_path, tmp_path)
    before_digest = sha256(db_path.read_bytes()).hexdigest()
    before_paths = {path.name for path in tmp_path.iterdir()}
    request = parse_strategy_execution_period_chain_effect_probe_request(
        _request(chain_id, digest)
    )

    result = run_strategy_execution_period_chain_effect_probe(
        request,
        db_path=db_path,
    )

    payload = result.to_dict()
    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_VERSION
    )
    assert payload["status"] == "ok"
    assert payload["period_chain_release_checked"] is True
    assert payload["two_period_horizon_verified"] is True
    assert payload["candidate_re_resolution_performed"] is True
    assert payload["candidate_reverified_count"] == 2
    assert payload["candidate_copies_isolated"] is True
    assert payload["source_candidates_mutated"] is False
    assert payload["stored_transition_flags_applied_exactly"] is True
    assert payload["period_count"] == 2
    assert payload["runner_invocation_count"] == 2
    assert payload["carryover_invocation_count"] == 2
    assert payload["execution_performed"] is True
    assert payload["writes_performed"] is False
    assert payload["result_persisted"] is False
    assert payload["idempotency_persisted"] is False
    assert payload["output_files_written"] is False
    assert payload["legacy_comparison_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["partial_result_returned"] is False
    assert [effect["period"] for effect in payload["period_effects"]] == [1, 2]
    assert all(
        effect["in_memory_export"]["written_file_count"] == 0
        for effect in payload["period_effects"]
    )
    transition = payload["transition_effect"]
    assert transition["from_period"] == 1
    assert transition["to_period"] == 2
    assert transition["vu_carryover_requested"] is True
    assert transition["vn_carryover_requested"] is True
    assert transition["vu_carryover_executed"] is True
    assert transition["vn_carryover_executed"] is True
    assert transition["carried_insurer_ids"] == [1]
    assert transition["carried_policyholder_ids"] == [1]
    assert sha256(db_path.read_bytes()).hexdigest() == before_digest
    assert {path.name for path in tmp_path.iterdir()} == before_paths


def test_probe_is_deterministic_without_persisting_idempotency(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_chain(db_path, tmp_path)
    request = parse_strategy_execution_period_chain_effect_probe_request(
        _request(chain_id, digest)
    )

    first = run_strategy_execution_period_chain_effect_probe(
        request,
        db_path=db_path,
    )
    second = run_strategy_execution_period_chain_effect_probe(
        request,
        db_path=db_path,
    )

    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["idempotency_persisted"] is False
    assert first.to_dict()["result_persisted"] is False


@pytest.mark.parametrize(
    ("vu_flag", "vn_flag"),
    [(False, False), (True, False), (False, True), (True, True)],
)
def test_probe_applies_exact_stored_transition_flags(
    tmp_path,
    vu_flag: bool,
    vn_flag: bool,
) -> None:
    case_root = tmp_path / f"case-{int(vu_flag)}-{int(vn_flag)}"
    case_root.mkdir()
    db_path = case_root / "metadata.sqlite"
    chain_id, digest = _persisted_chain(
        db_path,
        case_root,
        carry_forward_vu_state=vu_flag,
        carry_forward_vn_state=vn_flag,
    )

    payload = run_strategy_execution_period_chain_effect_probe(
        parse_strategy_execution_period_chain_effect_probe_request(
            _request(chain_id, digest)
        ),
        db_path=db_path,
    ).to_dict()

    transition = payload["transition_effect"]
    assert transition["vu_carryover_requested"] is vu_flag
    assert transition["vn_carryover_requested"] is vn_flag
    assert transition["vu_carryover_executed"] is vu_flag
    assert transition["vn_carryover_executed"] is vn_flag
    assert payload["carryover_invocation_count"] == int(vu_flag) + int(vn_flag)


def test_probe_rejects_longer_chain_before_runner(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_chain(
        db_path,
        tmp_path,
        max_periods=3,
    )
    calls = 0

    def reject_runner(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError(f"runner invoked with {args!r} {kwargs!r}")

    with pytest.raises(StrategyExecutionPeriodChainEffectProbeError) as exc_info:
        run_strategy_execution_period_chain_effect_probe(
            parse_strategy_execution_period_chain_effect_probe_request(
                _request(chain_id, digest)
            ),
            db_path=db_path,
            runner=reject_runner,
        )

    assert exc_info.value.code == "exact_two_period_horizon_required"
    assert exc_info.value.runner_invocation_count == 0
    assert calls == 0


def test_missing_second_candidate_stops_before_first_runner(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_chain(db_path, tmp_path)
    with sqlite3.connect(db_path) as connection:
        second_id = connection.execute(
            "SELECT candidate_id FROM strategy_execution_candidates "
            "WHERE period = 2"
        ).fetchone()[0]
        connection.execute(
            "DELETE FROM strategy_execution_candidates WHERE candidate_id = ?",
            (second_id,),
        )
    runner_count = 0

    def reject_runner(*args: object, **kwargs: object) -> object:
        nonlocal runner_count
        runner_count += 1
        raise AssertionError(f"runner invoked with {args!r} {kwargs!r}")

    with pytest.raises(StrategyExecutionPeriodChainEffectProbeError) as exc_info:
        run_strategy_execution_period_chain_effect_probe(
            parse_strategy_execution_period_chain_effect_probe_request(
                _request(chain_id, digest)
            ),
            db_path=db_path,
            runner=reject_runner,
        )

    assert exc_info.value.code == "candidate_re_resolution_failed"
    assert exc_info.value.candidate_reverified_count == 1
    assert exc_info.value.runner_invocation_count == 0
    assert runner_count == 0


def test_second_candidate_load_failure_stops_before_first_runner(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_chain(db_path, tmp_path)
    module = importlib.import_module(
        "ims.api.strategy_execution_period_chain_effect_probe"
    )
    original_loader = module.load_scenario_from_mapping
    load_count = 0
    runner_count = 0

    def failing_second_load(value):
        nonlocal load_count
        load_count += 1
        if load_count == 2:
            raise ValueError("synthetic second candidate failure")
        return original_loader(value)

    def reject_runner(*args: object, **kwargs: object) -> object:
        nonlocal runner_count
        runner_count += 1
        raise AssertionError(f"runner invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(module, "load_scenario_from_mapping", failing_second_load)

    with pytest.raises(StrategyExecutionPeriodChainEffectProbeError) as exc_info:
        run_strategy_execution_period_chain_effect_probe(
            parse_strategy_execution_period_chain_effect_probe_request(
                _request(chain_id, digest)
            ),
            db_path=db_path,
            runner=reject_runner,
        )

    assert exc_info.value.code == "candidate_copy_load_failed"
    assert exc_info.value.candidate_reverified_count == 2
    assert exc_info.value.runner_invocation_count == 0
    assert load_count == 2
    assert runner_count == 0


def test_second_runner_failure_returns_no_partial_result(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_chain(db_path, tmp_path)
    before_digest = sha256(db_path.read_bytes()).hexdigest()
    calls: list[int] = []

    def failing_second_runner(loaded, *, output_dir=None):
        assert output_dir is None
        calls.append(loaded.context.period)
        if loaded.context.period == 2:
            raise RuntimeError("synthetic second runner failure")
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    with pytest.raises(StrategyExecutionPeriodChainEffectProbeError) as exc_info:
        run_strategy_execution_period_chain_effect_probe(
            parse_strategy_execution_period_chain_effect_probe_request(
                _request(chain_id, digest)
            ),
            db_path=db_path,
            runner=failing_second_runner,
        )

    assert exc_info.value.code == "effect_probe_runner_failed"
    assert exc_info.value.runner_invocation_count == 2
    assert exc_info.value.carryover_invocation_count == 2
    assert calls == [1, 2]
    assert sha256(db_path.read_bytes()).hexdigest() == before_digest
    error = strategy_execution_period_chain_effect_probe_error_payload(
        exc_info.value.code,
        str(exc_info.value),
        runner_invocation_count=exc_info.value.runner_invocation_count,
        carryover_invocation_count=exc_info.value.carryover_invocation_count,
        candidate_reverified_count=exc_info.value.candidate_reverified_count,
        release_check=exc_info.value.release_check,
    )
    assert error["period_effects"] == []
    assert error["transition_effect"] is None
    assert error["partial_result_returned"] is False
    assert error["execution_performed"] is False
    assert error["writes_performed"] is False
    assert error["simulation_performed"] is False
