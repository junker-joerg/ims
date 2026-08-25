from __future__ import annotations

from dataclasses import dataclass

from ims.model.vdefmd6_population import (
    VDEFMD6_MAX_PERIODS,
    build_vdefmd6_population,
)


VDEFMD6_RULE_LOGICAL_TIME = 1
VDEFMD6_EXPORT_LOGICAL_TIME = 10
VDEFMD6_MAX_RUNS = 100
MODERN_SEED_POLICY_ID = "ims-modern-explicit-run-v1"


@dataclass(frozen=True, slots=True)
class ModernSeedPolicy:
    base_seed: int
    max_runs: int = VDEFMD6_MAX_RUNS
    policy_id: str = MODERN_SEED_POLICY_ID
    historical_seed_known: bool = False

    def __post_init__(self) -> None:
        if type(self.base_seed) is not int or self.base_seed < 0:
            raise ValueError("base_seed must be a non-negative integer")
        if (
            type(self.max_runs) is not int
            or not 1 <= self.max_runs <= VDEFMD6_MAX_RUNS
        ):
            raise ValueError(f"max_runs must be between 1 and {VDEFMD6_MAX_RUNS}")

    def seed_for_run(self, run_number: int) -> int:
        if type(run_number) is not int or not 1 <= run_number <= self.max_runs:
            raise ValueError(f"run_number must be between 1 and {self.max_runs}")
        return self.base_seed + run_number - 1


@dataclass(frozen=True, slots=True)
class Vdefmd6ActionInvocation:
    subject_type: str
    subject_id: int
    action: str
    rule_id: int | None
    rule_class: int | None
    activation_period: int


@dataclass(frozen=True, slots=True)
class Vdefmd6ActionSlot:
    period: int
    logical_time: int
    invocations: tuple[Vdefmd6ActionInvocation, ...]


@dataclass(frozen=True, slots=True)
class Vdefmd6ActionSeedPlan:
    slots: tuple[Vdefmd6ActionSlot, ...]
    run_seeds: tuple[int, ...]
    seed_policy: ModernSeedPolicy
    same_slot_serialization: tuple[str, ...] = ("central", "insurer", "policyholder")
    historical_same_slot_order_claimed: bool = False
    scheduler_started: bool = False
    rng_draws_performed: bool = False
    simulation_performed: bool = False


def build_vdefmd6_action_seed_plan(
    *,
    base_seed: int,
    run_count: int = VDEFMD6_MAX_RUNS,
) -> Vdefmd6ActionSeedPlan:
    seed_policy = ModernSeedPolicy(base_seed=base_seed, max_runs=run_count)
    population = build_vdefmd6_population()
    slots: list[Vdefmd6ActionSlot] = []

    for period in range(1, VDEFMD6_MAX_PERIODS + 1):
        rule_invocations = [
            Vdefmd6ActionInvocation(
                subject_type="central",
                subject_id=1,
                action="foreign_information",
                rule_id=None,
                rule_class=None,
                activation_period=1,
            )
        ]
        rule_invocations.extend(
            Vdefmd6ActionInvocation(
                subject_type="insurer",
                subject_id=item.entity_id,
                action="insurer_rule",
                rule_id=item.action.rule_id,
                rule_class=item.rule_class,
                activation_period=item.activation.activation_period,
            )
            for item in population.insurer_definitions
            if item.activation.activation_period <= period
        )
        rule_invocations.extend(
            Vdefmd6ActionInvocation(
                subject_type="policyholder",
                subject_id=item.entity_id,
                action="policyholder_rule",
                rule_id=item.action.rule_id,
                rule_class=item.rule_class,
                activation_period=item.activation.activation_period,
            )
            for item in population.policyholder_definitions
            if item.activation.activation_period <= period
        )
        slots.append(
            Vdefmd6ActionSlot(
                period=period,
                logical_time=VDEFMD6_RULE_LOGICAL_TIME,
                invocations=tuple(rule_invocations),
            )
        )
        slots.append(
            Vdefmd6ActionSlot(
                period=period,
                logical_time=VDEFMD6_EXPORT_LOGICAL_TIME,
                invocations=(
                    Vdefmd6ActionInvocation(
                        subject_type="central",
                        subject_id=1,
                        action="aggregate_export",
                        rule_id=None,
                        rule_class=None,
                        activation_period=1,
                    ),
                ),
            )
        )

    return Vdefmd6ActionSeedPlan(
        slots=tuple(slots),
        run_seeds=tuple(
            seed_policy.seed_for_run(run) for run in range(1, run_count + 1)
        ),
        seed_policy=seed_policy,
    )
