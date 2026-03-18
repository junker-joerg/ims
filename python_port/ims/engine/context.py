from dataclasses import dataclass


@dataclass(slots=True)
class SimulationContext:
    """
    Minimaler Simulationskontext.

    Dieser Platzhalter enthält bewusst noch keine Fachlogik.
    Spätere PRs ergänzen Registries, RNG, Perioden- und Laufparameter.
    """
    period: int = 0
    logtime: int = 0
    run_index: int = 0
