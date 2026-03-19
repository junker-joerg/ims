import pytest

from ims.engine.context import SimulationContext, ensure_context_rng
from ims.engine.simulation import DispatchedEventResult, dispatch_event, run_scheduled_bav_update
from ims.engine.scheduler import Event
from ims.model.entities import BAV, Insurer, Policyholder


def test_dispatch_event_executes_bav_update() -> None:
    context = SimulationContext(period=2, logtime=4)
    bav = BAV(entity_id=100, name="Basis-BAV")
    event = Event(2, 4, 0, "bav", 100, "bav_update")

    result = dispatch_event(
        event,
        context=context,
        bav=bav,
        insurers=[Insurer(entity_id=200, name="Aktive VU", active=True)],
        policyholders=[Policyholder(entity_id=300, name="Aktiver VN", active=True, insurer_id=200)],
    )

    assert isinstance(result, DispatchedEventResult)
    assert result.bav_update.period == 2
    assert result.bav_update.active_insurer_count == 1
    assert result.aggregate_snapshot.assigned_policyholders == 1


def test_dispatch_event_rejects_unknown_action() -> None:
    with pytest.raises(ValueError, match="unsupported event action"):
        dispatch_event(
            Event(0, 0, 0, "bav", 100, "unknown"),
            context=SimulationContext(),
            bav=BAV(entity_id=100, name="Basis-BAV"),
            insurers=[],
            policyholders=[],
        )


def test_run_scheduled_bav_update_executes_single_planned_event() -> None:
    result = run_scheduled_bav_update("tests/fixtures/minimal_scenario.json")

    assert result.event.action == "bav_update"
    assert result.context.period == 0
    assert result.bav_update.active_policyholder_count == 1
    assert result.aggregate_snapshot.assigned_policyholders == 1


def test_run_scheduled_bav_update_rng_samples_are_deterministic() -> None:
    first = run_scheduled_bav_update(
        "tests/fixtures/minimal_scenario.json",
        initialize_rng=True,
        use_rng_sample=True,
    )
    second = run_scheduled_bav_update(
        "tests/fixtures/minimal_scenario.json",
        initialize_rng=True,
        use_rng_sample=True,
    )

    assert first.bav_update.sample_token == 0.052363598850944326
    assert second.bav_update.sample_token == first.bav_update.sample_token


def test_run_scheduled_bav_update_raises_when_sampling_without_rng() -> None:
    with pytest.raises(ValueError, match="context.rng is required"):
        run_scheduled_bav_update(
            "tests/fixtures/minimal_scenario.json",
            initialize_rng=False,
            use_rng_sample=True,
        )
