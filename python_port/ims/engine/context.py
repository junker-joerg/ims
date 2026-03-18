from dataclasses import dataclass


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
