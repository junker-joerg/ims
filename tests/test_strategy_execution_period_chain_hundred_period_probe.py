from copy import deepcopy
from dataclasses import replace

import pytest

from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
)
from ims.api.strategy_execution_period_chain_extended_probe import (
    EXTENDED_PROBE_REQUEST_VERSION,
    EXTENDED_PROBE_REQUEST_VERSION_V1,
    EXTENDED_PROBE_RESULT_VERSION,
    EXTENDED_PROBE_RESULT_VERSION_V1,
    ExtendedProbeError,
    parse_extended_probe_request,
    run_extended_probe,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period
from tests.period_chain_test_support import chain_input, persist_chain_candidates
from tests.test_strategy_execution_period_chain_extended_probe import (
    _input,
    _release,
    _slow_runner,
)


def _late_failing_runner(loaded, *, output_dir=None):
    if loaded.context.period == 99:
        raise RuntimeError("period 99 failed")
    return run_loaded_explicit_period(loaded, output_dir=output_dir)


def test_hundred_period_run_is_reproducible_complete_and_source_immutable(tmp_path):
    db_path, payload = _input(tmp_path, 100)
    before = db_path.read_bytes()
    request = parse_extended_probe_request(payload)

    first = run_extended_probe(request, db_path=db_path)
    second = run_extended_probe(request, db_path=db_path)

    assert first["schema_version"] == EXTENDED_PROBE_RESULT_VERSION
    assert first["status"] == "ok"
    assert first["period_count"] == 100
    assert [effect["period"] for effect in first["period_effects"]] == list(
        range(1, 101)
    )
    assert [
        (effect["from_period"], effect["to_period"])
        for effect in first["transition_effects"]
    ] == [(period, period + 1) for period in range(1, 100)]
    assert first["runner_invocation_count"] == 100
    assert first["carryover_invocation_count"] == 198
    assert first["candidate_reverified_count"] == 100
    assert first["prefix_equal"] is True
    assert first["prefix_proof"]["semantic_equal"] is True
    assert first["prefix_proof"]["canonical_json_byte_equal"] is True
    assert first["effect_digest"] == second["effect_digest"]
    assert first["period_effects"] == second["period_effects"]
    assert first["transition_effects"] == second["transition_effects"]
    assert 0 < first["wall_elapsed_seconds"] < 1800
    assert 0 < first["peak_worker_rss_bytes"] < 1024 * 1024 * 1024
    assert first["chain_payload_bytes"] < 64 * 1024 * 1024
    assert first["result_payload_bytes"] < 64 * 1024 * 1024
    assert first["result_persisted"] is False
    assert first["partial_result_returned"] is False
    assert db_path.read_bytes() == before


def test_v1_remains_bounded_and_v2_requires_explicit_release(tmp_path):
    db_path, payload = _input(tmp_path, 100)
    legacy = deepcopy(payload)
    legacy["schema_version"] = EXTENDED_PROBE_REQUEST_VERSION_V1
    with pytest.raises(ExtendedProbeError) as caught:
        parse_extended_probe_request(legacy)
    assert caught.value.code == "horizon_not_released"
    valid_v2 = parse_extended_probe_request(payload)
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(
            replace(valid_v2, schema_version=EXTENDED_PROBE_REQUEST_VERSION_V1),
            db_path=db_path,
        )
    assert caught.value.code == "horizon_not_released"

    payload["explicit_extended_effect_probe_execution"] = False
    with pytest.raises(ExtendedProbeError) as caught:
        parse_extended_probe_request(payload)
    assert caught.value.code == "explicit_release_required"
    payload["explicit_extended_effect_probe_execution"] = True
    payload["release"]["explicit_run_control_release"] = False
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(parse_extended_probe_request(payload), db_path=db_path)
    assert caught.value.code == "release_invalid"


def test_late_error_is_atomic_and_blocks_period_100(tmp_path):
    db_path, payload = _input(tmp_path, 100)
    before = db_path.read_bytes()
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(
            parse_extended_probe_request(payload),
            db_path=db_path,
            worker_runner=_late_failing_runner,
        )
    assert caught.value.code == "worker_failed"
    assert "period 99 failed" in str(caught.value)
    assert db_path.read_bytes() == before


def test_hundred_period_prefix_mismatch_blocks_period_six(tmp_path):
    db_path, payload = _input(tmp_path, 100)
    root = tmp_path / "different-run"
    root.mkdir()
    references = persist_chain_candidates(db_path, root, run_index=1, max_periods=100)
    value = chain_input(references, run_index=1, max_periods=100)
    chain = build_strategy_execution_period_chain(value, db_path=db_path).chain
    assert chain is not None
    payload["period_chain_input"] = value
    payload["release"] = _release(chain, "hundred-prefix-mismatch-001")
    before = db_path.read_bytes()

    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(parse_extended_probe_request(payload), db_path=db_path)

    assert caught.value.code == "prefix_mismatch"
    assert "vor Periode 6" in str(caught.value)
    assert db_path.read_bytes() == before


def test_hundred_period_memory_abort_returns_no_partial_result(tmp_path, monkeypatch):
    import ims.api.strategy_execution_period_chain_extended_probe as module

    db_path, payload = _input(tmp_path, 100)
    before = db_path.read_bytes()
    monkeypatch.setattr(module, "_MAX_WORKER_RSS", 1)
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(
            parse_extended_probe_request(payload),
            db_path=db_path,
            worker_runner=_slow_runner,
        )
    assert caught.value.code == "rss_budget_exceeded"
    assert db_path.read_bytes() == before


def test_v1_request_and_result_remain_compatible_for_existing_horizon(tmp_path):
    db_path, payload = _input(tmp_path, 10)
    payload["schema_version"] = EXTENDED_PROBE_REQUEST_VERSION_V1
    result = run_extended_probe(parse_extended_probe_request(payload), db_path=db_path)
    assert result["schema_version"] == EXTENDED_PROBE_RESULT_VERSION_V1
    assert result["period_count"] == 10
    assert EXTENDED_PROBE_REQUEST_VERSION != EXTENDED_PROBE_REQUEST_VERSION_V1
