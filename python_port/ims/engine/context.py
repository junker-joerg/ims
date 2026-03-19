from dataclasses import dataclass
import random

from ims.engine.rng import create_rng


@dataclass(slots=True)
class SimulationContext:
    """
    Minimaler Simulationskontext.

    Dieser Platzhalter enthält bewusst noch keine Fachlogik.
    Spätere PRs ergänzen Registries, RNG-Objekte sowie weitere Laufparameter.
    """

    period: int = 0
    logtime: int = 0
    max_periods: int = 0
    run_index: int = 0
    rng_seed: int = 0
    rng: random.Random | None = None


def ensure_context_rng(context: SimulationContext) -> random.Random:
    """Create and attach a deterministic RNG if the context has none yet."""

    if context.rng is None:
        context.rng = create_rng(context.rng_seed)
    return context.rng
"""Placeholder module for future runtime context code.

No simulation or business initialization logic is implemented yet.
"""
