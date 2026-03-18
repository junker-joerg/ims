"""Generic simulation context primitives for the IMS Python port.

The structures in this module provide technical runtime state only.
They intentionally avoid IMS-specific business rules and domain coupling.
"""

from dataclasses import dataclass, field
import random
from typing import Any


@dataclass(slots=True)
class SimulationContext:
    """Minimal runtime context for future simulation-oriented PRs.

    The fields are intentionally generic so later steps can attach registries,
    stores and RNG handling without forcing IMS domain assumptions here.
    """

    period: int = 0
    logtime: int = 0
    max_periods: int = 0
    run_index: int = 0
    rng_seed: int | None = None
    registries: dict[str, Any] = field(default_factory=dict)
    stores: dict[str, Any] = field(default_factory=dict)


def initialize_run_context(
    *,
    max_periods: int,
    rng_seed: int,
    run_index: int = 0,
) -> SimulationContext:
    """Build a deterministically seeded run context.

    This is the first narrow functional slice: a run can be initialized with a
    fixed seed and receives a dedicated RNG instance in its registries.
    """

    rng = random.Random(rng_seed)
    return SimulationContext(
        period=0,
        logtime=0,
        max_periods=max_periods,
        run_index=run_index,
        rng_seed=rng_seed,
        registries={"rng": rng},
        stores={},
    )
