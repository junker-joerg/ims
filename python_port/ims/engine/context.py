"""Generic simulation context primitives for the IMS Python port.

The structures in this module provide technical runtime state only.
They intentionally avoid IMS-specific business rules and domain coupling.
"""

from dataclasses import dataclass, field
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
