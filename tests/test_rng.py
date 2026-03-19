from ims.engine.context import SimulationContext, ensure_context_rng
from ims.engine.rng import create_rng, rand_int_inclusive, rand_uniform_0_1

import pytest


def test_same_seed_produces_same_uniform_sequence() -> None:
    rng_a = create_rng(123)
    rng_b = create_rng(123)

    seq_a = [rand_uniform_0_1(rng_a) for _ in range(3)]
    seq_b = [rand_uniform_0_1(rng_b) for _ in range(3)]

    assert seq_a == seq_b


def test_different_seed_very_likely_changes_sequence() -> None:
    rng_a = create_rng(123)
    rng_b = create_rng(456)

    seq_a = [rand_uniform_0_1(rng_a) for _ in range(3)]
    seq_b = [rand_uniform_0_1(rng_b) for _ in range(3)]

    assert seq_a != seq_b


def test_rand_int_inclusive_respects_bounds() -> None:
    rng = create_rng(123)

    values = [rand_int_inclusive(rng, 2, 4) for _ in range(20)]

    assert all(2 <= value <= 4 for value in values)


def test_rand_int_inclusive_rejects_invalid_interval() -> None:
    rng = create_rng(123)

    with pytest.raises(ValueError, match="low must be less than or equal to high"):
        rand_int_inclusive(rng, 5, 4)


def test_context_can_carry_rng_from_seed() -> None:
    context = SimulationContext(rng_seed=77)

    rng = ensure_context_rng(context)

    assert context.rng is rng
    assert rand_uniform_0_1(rng) == rand_uniform_0_1(create_rng(77))
