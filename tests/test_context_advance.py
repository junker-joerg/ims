from ims.engine.context import SimulationContext


def test_context_advanced_returns_new_context_with_incremented_logtime() -> None:
    context = SimulationContext(period=2, logtime=5, max_periods=12, run_index=1, rng_seed=123)

    advanced = context.advanced(logtime_increment=1)

    assert advanced is not context
    assert context.period == 2
    assert context.logtime == 5
    assert advanced.period == 2
    assert advanced.logtime == 6
    assert advanced.max_periods == 12
    assert advanced.run_index == 1
    assert advanced.rng_seed == 123


def test_context_advanced_can_start_new_period_and_reset_logtime() -> None:
    context = SimulationContext(period=2, logtime=5)

    advanced = context.advanced(period_increment=1, logtime_increment=0, reset_logtime_to=0)

    assert advanced.period == 3
    assert advanced.logtime == 0
    assert context.period == 2
    assert context.logtime == 5
