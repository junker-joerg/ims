"""Reference tests for deterministic run initialization."""

from ims.engine.context import initialize_run_context


def test_initialize_run_context_sets_expected_start_values_and_seeded_rng() -> None:
    context = initialize_run_context(max_periods=3, rng_seed=17, run_index=2)

    assert context.period == 0
    assert context.logtime == 0
    assert context.max_periods == 3
    assert context.run_index == 2
    assert context.rng_seed == 17

    rng = context.registries["rng"]
    values = [round(rng.random(), 6) for _ in range(3)]
    assert values == [0.521984, 0.806691, 0.960495]
