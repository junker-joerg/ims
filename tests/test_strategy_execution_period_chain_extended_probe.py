from copy import deepcopy
from pathlib import Path
import sqlite3
from time import sleep

import pytest

from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
)
from ims.api.strategy_execution_period_chain_extended_probe import (
    EXTENDED_PROBE_REQUEST_VERSION,
    ExtendedProbeError,
    parse_extended_probe_request,
    run_extended_probe,
)
from ims.api.strategy_execution_period_chain_five_period_build import (
    build_strategy_execution_five_period_chain,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe import (
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe_start import (
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION,
    parse_strategy_execution_five_period_effect_probe_start_request,
    start_strategy_execution_five_period_effect_probe,
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


def _slow_runner(loaded, *, output_dir=None):
    sleep(2)
    return run_loaded_explicit_period(loaded, output_dir=output_dir)


def _failing_runner(loaded, *, output_dir=None):
    if loaded.context.period == 3:
        raise RuntimeError("third period fails")
    return run_loaded_explicit_period(loaded, output_dir=output_dir)


def _five_baseline(tmp_path: Path, db_path: Path):
    two = persist_two_period_effect_probe_baseline(
        db_path, tmp_path / "two", run_index=0
    )
    root = tmp_path / "five"
    root.mkdir()
    refs = persist_chain_candidates(db_path, root, run_index=0, max_periods=5)
    value = chain_input(refs, run_index=0, max_periods=5)
    chain = build_strategy_execution_five_period_chain(value, db_path=db_path).chain
    assert chain is not None
    request = parse_strategy_execution_five_period_effect_probe_start_request(
        {
            "schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION,
            "effect_probe_request": {
                "schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
                "period_chain_input": value,
                "prefix_baseline": two,
                "explicit_five_period_effect_probe_execution": True,
            },
            "release": _release(chain, "five-001"),
            "explicit_five_period_effect_probe_start": True,
        }
    )
    stored = start_strategy_execution_five_period_effect_probe(request, db_path=db_path)
    return {
        "chain_id": stored.record.chain_id,
        "expected_content_digest": stored.record.content_digest,
        "expected_result_digest": stored.record.result_digest,
    }


def _release(chain, key):
    return {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION,
        "chain_id": chain.chain_id,
        "expected_content_digest": chain.content_digest,
        "idempotency_key": key,
        "explicit_run_control_release": True,
        "released_by": "test-reviewer",
        "released_at": "2026-09-16T08:00:00Z",
        "release_reason": "Kontrollierte Folgeprobe",
    }


def _input(tmp_path, count):
    db_path = tmp_path / "metadata.sqlite"
    baseline = _five_baseline(tmp_path, db_path)
    root = tmp_path / "extended"
    root.mkdir()
    refs = persist_chain_candidates(db_path, root, run_index=0, max_periods=count)
    value = chain_input(refs, run_index=0, max_periods=count)
    chain = build_strategy_execution_period_chain(value, db_path=db_path).chain
    assert chain is not None
    payload = {
        "schema_version": EXTENDED_PROBE_REQUEST_VERSION,
        "period_chain_input": value,
        "five_period_baseline": baseline,
        "release": _release(chain, f"extended-{count}"),
        "explicit_extended_effect_probe_execution": True,
    }
    return db_path, payload


@pytest.mark.parametrize("count", [10, 25, 50])
def test_extended_horizons_are_deterministic_and_leave_db_unchanged(tmp_path, count):
    db_path, payload = _input(tmp_path, count)
    before = db_path.read_bytes()
    request = parse_extended_probe_request(payload)
    first = run_extended_probe(request, db_path=db_path)
    second = run_extended_probe(request, db_path=db_path)
    assert first["period_count"] == count
    assert first["runner_invocation_count"] == count
    assert first["carryover_invocation_count"] == 2 * (count - 1)
    assert first["prefix_equal"] is True
    assert first["prefix_proof"]["canonical_json_byte_equal"] is True
    assert first["effect_digest"] == second["effect_digest"]
    assert first["period_effects"] == second["period_effects"]
    assert first["transition_effects"] == second["transition_effects"]
    assert first["peak_worker_rss_bytes"] > 0
    assert first["peak_worker_rss_bytes"] < 1024 * 1024 * 1024
    assert first["chain_payload_bytes"] < 64 * 1024 * 1024
    assert first["result_payload_bytes"] < 64 * 1024 * 1024
    assert first["wall_elapsed_seconds"] < {10: 180, 25: 450, 50: 900}[count]
    assert first["wall_elapsed_seconds"] > 0
    assert db_path.read_bytes() == before


def test_unreleased_100_and_wrong_prefix_are_blocked(tmp_path):
    db_path, payload = _input(tmp_path, 10)
    payload["period_chain_input"]["max_periods"] = 100
    with pytest.raises(ExtendedProbeError, match="10, 25 und 50"):
        parse_extended_probe_request(payload)
    payload["period_chain_input"]["max_periods"] = 10
    payload["five_period_baseline"]["expected_result_digest"] = "sha256:" + "0" * 64
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(parse_extended_probe_request(payload), db_path=db_path)
    assert caught.value.code == "baseline_mismatch"


def test_release_mismatch_and_cancellation_do_not_write_partial_results(tmp_path):
    db_path, payload = _input(tmp_path, 10)
    before = db_path.read_bytes()
    broken = deepcopy(payload)
    broken["release"]["expected_content_digest"] = "sha256:" + "0" * 64
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(parse_extended_probe_request(broken), db_path=db_path)
    assert caught.value.code == "release_mismatch"
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(
            parse_extended_probe_request(payload),
            db_path=db_path,
            worker_runner=_slow_runner,
            cancel_requested=lambda: True,
        )
    assert caught.value.code == "cancelled"
    assert db_path.read_bytes() == before
    with sqlite3.connect(db_path) as connection:
        assert not any(
            "extended_probe" in row[0]
            for row in connection.execute("SELECT name FROM sqlite_master")
        )


def test_prefix_mismatch_stops_before_sixth_period(tmp_path):
    db_path, payload = _input(tmp_path, 10)
    root = tmp_path / "different-run"
    root.mkdir()
    references = persist_chain_candidates(db_path, root, run_index=1, max_periods=10)
    value = chain_input(references, run_index=1, max_periods=10)
    chain = build_strategy_execution_period_chain(value, db_path=db_path).chain
    assert chain is not None
    payload["period_chain_input"] = value
    payload["release"] = _release(chain, "different-run-001")
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(parse_extended_probe_request(payload), db_path=db_path)
    assert caught.value.code == "prefix_mismatch"
    assert "vor Periode 6" in str(caught.value)


def test_first_runner_error_and_hard_resource_limits_fail_closed(tmp_path, monkeypatch):
    import ims.api.strategy_execution_period_chain_extended_probe as module

    db_path, payload = _input(tmp_path, 10)
    request = parse_extended_probe_request(payload)
    before = db_path.read_bytes()
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(request, db_path=db_path, worker_runner=_failing_runner)
    assert caught.value.code == "worker_failed"
    assert "third period fails" in str(caught.value)

    monkeypatch.setattr(module, "_MAX_WORKER_RSS", 1)
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(request, db_path=db_path, worker_runner=_slow_runner)
    assert caught.value.code == "rss_budget_exceeded"
    monkeypatch.setattr(module, "_MAX_WORKER_RSS", 1024 * 1024 * 1024)
    monkeypatch.setattr(module, "_PERIOD_SECONDS", 0.1)
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(request, db_path=db_path, worker_runner=_slow_runner)
    assert caught.value.code == "period_budget_exceeded"
    assert db_path.read_bytes() == before


def test_missing_rss_measurement_and_excess_chain_payload_block_release(
    tmp_path, monkeypatch
):
    import ims.api.strategy_execution_period_chain_extended_probe as module

    db_path, payload = _input(tmp_path, 10)
    request = parse_extended_probe_request(payload)
    monkeypatch.setattr(module, "_MAX_PAYLOAD", 1)
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(request, db_path=db_path)
    assert caught.value.code == "chain_budget_exceeded"

    monkeypatch.setattr(module, "_MAX_PAYLOAD", 64 * 1024 * 1024)
    monkeypatch.setattr(module, "_peak_worker_rss", lambda pid: None)
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(request, db_path=db_path, worker_runner=_slow_runner)
    assert caught.value.code == "rss_measurement_unavailable"


def test_runtime_limits_match_versioned_contract():
    import ims.api.strategy_execution_period_chain_extended_probe as module
    from ims.strategies.execution_period_chain_horizon_contract import (
        strategy_execution_period_chain_horizon_contract_payload,
    )

    horizons = strategy_execution_period_chain_horizon_contract_payload()["horizons"]
    for horizon in horizons[:3]:
        assert horizon["execution_enabled"] is True
        assert (
            horizon["max_peak_worker_rss_mib"] * module._MIB == module._MAX_WORKER_RSS
        )
        assert (
            horizon["max_canonical_chain_payload_mib"] * module._MIB
            == module._MAX_PAYLOAD
        )
        assert (
            horizon["max_serialized_result_payload_mib"] * module._MIB
            == module._MAX_PAYLOAD
        )
        assert (
            horizon["min_free_storage_before_start_mib"] * module._MIB
            == module._MIN_DISK
        )
        assert horizon["max_period_seconds"] == module._PERIOD_SECONDS
    assert horizons[3]["execution_enabled"] is False


def test_complete_response_payload_is_measured_before_return(tmp_path, monkeypatch):
    import ims.api.strategy_execution_period_chain_extended_probe as module

    db_path, payload = _input(tmp_path, 10)
    request = parse_extended_probe_request(payload)
    result = run_extended_probe(request, db_path=db_path)
    complete_bytes = len(module._canonical(result))
    worker_bytes = result["result_payload_bytes"]
    assert complete_bytes > worker_bytes
    monkeypatch.setattr(module, "_MAX_PAYLOAD", (complete_bytes + worker_bytes) // 2)
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(request, db_path=db_path)
    assert caught.value.code == "result_budget_exceeded"


def test_noncanonical_input_stops_before_worker(tmp_path):
    db_path, payload = _input(tmp_path, 10)
    payload["period_chain_input"]["invalid_number"] = float("nan")
    with pytest.raises(ExtendedProbeError) as caught:
        run_extended_probe(parse_extended_probe_request(payload), db_path=db_path)
    assert caught.value.code == "chain_input_not_canonical"
