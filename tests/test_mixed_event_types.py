from pathlib import Path

import pytest

from ims.engine.simulation import dispatch_event, run_mixed_bav_event_sequence
from ims.io.scenario_loader import load_scenario
from ims.model.entities import BAV


def test_bav_update_mutates_bav_and_bav_snapshot_does_not(minimal_scenario_path: Path) -> None:
    loaded = load_scenario(minimal_scenario_path)
    bav = loaded.bav

    update_result = dispatch_event(
        loaded_context_event("bav_update", loaded.bav.entity_id, loaded.context.period, loaded.context.logtime),
        context=loaded.context,
        bav=bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
    )

    assert isinstance(bav, BAV)
    assert bav.last_update_period == loaded.context.period
    assert bav.last_update_logtime == loaded.context.logtime
    assert update_result.bav_update is not None

    before_snapshot_state = (
        bav.last_update_period,
        bav.last_update_logtime,
        bav.last_active_insurer_count,
        bav.last_active_policyholder_count,
        bav.last_sample_token,
    )
    snapshot_result = dispatch_event(
        loaded_context_event(
            "bav_snapshot",
            loaded.bav.entity_id,
            loaded.context.period,
            loaded.context.logtime + 1,
        ),
        context=loaded.context.advanced(period_increment=0, logtime_increment=1),
        bav=bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
    )
    after_snapshot_state = (
        bav.last_update_period,
        bav.last_update_logtime,
        bav.last_active_insurer_count,
        bav.last_active_policyholder_count,
        bav.last_sample_token,
    )

    assert snapshot_result.bav_update is None
    assert before_snapshot_state == after_snapshot_state


def test_mixed_sequence_with_update_first(minimal_scenario_path: Path) -> None:
    result = run_mixed_bav_event_sequence(minimal_scenario_path, update_first=True)

    assert [item.event.action for item in result.dispatched_results] == [
        "bav_update",
        "bav_snapshot",
    ]
    assert result.dispatched_results[0].bav_update is not None
    assert result.dispatched_results[1].bav_update is None
    assert [
        (item.event.period, item.event.logtime) for item in result.dispatched_results
    ] == [(0, 0), (0, 1)]


def test_mixed_sequence_with_update_first_false(minimal_scenario_path: Path) -> None:
    result = run_mixed_bav_event_sequence(minimal_scenario_path, update_first=False)

    assert [item.event.action for item in result.dispatched_results] == [
        "bav_snapshot",
        "bav_update",
    ]
    assert result.dispatched_results[0].bav_update is None
    assert result.dispatched_results[1].bav_update is not None
    assert [
        (item.event.period, item.event.logtime) for item in result.dispatched_results
    ] == [(0, 0), (0, 1)]


def test_bav_snapshot_result_has_no_bav_update(minimal_scenario_path: Path) -> None:
    result = run_mixed_bav_event_sequence(minimal_scenario_path, update_first=True)

    snapshot_result = result.dispatched_results[1]
    assert snapshot_result.event.action == "bav_snapshot"
    assert snapshot_result.bav_update is None
    assert snapshot_result.aggregate_snapshot is not None


def test_mixed_sequence_seeded_rng_is_deterministic_for_update_part(minimal_scenario_path: Path) -> None:
    result_a = run_mixed_bav_event_sequence(
        minimal_scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
        update_first=True,
    )
    result_b = run_mixed_bav_event_sequence(
        minimal_scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
        update_first=True,
    )

    assert result_a.dispatched_results[0].bav_update is not None
    assert result_b.dispatched_results[0].bav_update is not None
    assert (
        result_a.dispatched_results[0].bav_update.sample_token
        == result_b.dispatched_results[0].bav_update.sample_token
    )


def test_mixed_sequence_raises_when_sampling_without_rng(minimal_scenario_path: Path) -> None:
    with pytest.raises(ValueError, match="context.rng is required"):
        run_mixed_bav_event_sequence(
            minimal_scenario_path,
            initialize_rng=False,
            use_rng_sample=True,
            update_first=True,
        )


def test_dispatch_event_rejects_unknown_action(minimal_scenario_path: Path) -> None:
    loaded = load_scenario(minimal_scenario_path)

    with pytest.raises(ValueError, match="unsupported event action: unsupported"):
        dispatch_event(
            loaded_context_event(
                "unsupported",
                loaded.bav.entity_id,
                loaded.context.period,
                loaded.context.logtime,
            ),
            context=loaded.context,
            bav=loaded.bav,
            insurers=loaded.insurers,
            policyholders=loaded.policyholders,
        )


def loaded_context_event(action: str, subject_id: int, period: int, logtime: int):
    from ims.engine.scheduler import Event

    return Event(
        period=period,
        logtime=logtime,
        priority=0,
        subject_type="bav",
        subject_id=subject_id,
        action=action,
        payload={},
    )
