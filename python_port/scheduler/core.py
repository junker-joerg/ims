"""Minimal scheduler scaffold with deterministic step ordering."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SchedulerStep:
    """A named scheduler step placeholder."""

    name: str


@dataclass(slots=True)
class SchedulerPlan:
    """Ordered collection of scheduler steps.

    This class is deliberately small and only preserves insertion order so
    tests can define the first observable contract for the future port.
    """

    steps: list[SchedulerStep] = field(default_factory=list)

    def add_step(self, step: SchedulerStep) -> None:
        """Append a single step without applying domain-specific logic."""

        self.steps.append(step)

    def extend(self, steps: list[SchedulerStep]) -> None:
        """Append multiple steps while preserving the provided order."""

        self.steps.extend(steps)

    def ordered_names(self) -> list[str]:
        """Return the current step names in execution order."""

        return [step.name for step in self.steps]
