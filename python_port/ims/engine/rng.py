import random


def create_rng(seed: int | None) -> random.Random:
    """Create a deterministic RNG instance from an optional seed."""

    return random.Random(seed)


def rand_uniform_0_1(rng: random.Random) -> float:
    """Return a uniform random float in the half-open interval [0.0, 1.0)."""

    return rng.random()


def rand_int_inclusive(rng: random.Random, low: int, high: int) -> int:
    """Return a random integer N such that low <= N <= high."""

    if low > high:
        raise ValueError("low must be less than or equal to high")
    return rng.randint(low, high)
