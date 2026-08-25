from __future__ import annotations

from dataclasses import dataclass

from ims.engine.context import SimulationContext
from ims.model.agrsich_export import ExportTable, build_agrsich_export_tables
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.entities import BAV
from ims.model.vdefmd6_population import build_vdefmd6_population
from ims.model.vu_rules import (
    VUExpectedClaimRuleParameters,
    apply_vu_expected_claim_rule_to_insurer,
)


VU14_ENTITY_ID = 14
VU14_PRE_SHOCK_PERIOD_START = 1
VU14_PRE_SHOCK_PERIOD_END = 49
VU14_MAX_PERIODS = 100


@dataclass(frozen=True, slots=True)
class VU14ProjectionPeriod:
    period: int
    export_table: ExportTable
    expected_claim_values: tuple[float, float]


@dataclass(frozen=True, slots=True)
class VU14PreShockProjection:
    periods: tuple[VU14ProjectionPeriod, ...]
    legacy_rows_used_as_input: bool = False
    policyholder_claim_inputs_bound: bool = False
    settlement_state_inputs_bound: bool = False
    rng_draws_performed: bool = False
    scheduler_started: bool = False
    simulation_performed: bool = False


def build_vu14_pre_shock_projection(
    parameters: VUExpectedClaimRuleParameters,
    *,
    interest_rate: float,
) -> VU14PreShockProjection:
    population = build_vdefmd6_population()
    insurer = next(
        item for item in population.insurers if item.entity_id == VU14_ENTITY_ID
    )
    projected_periods: list[VU14ProjectionPeriod] = []

    for period in range(
        VU14_PRE_SHOCK_PERIOD_START,
        VU14_PRE_SHOCK_PERIOD_END + 1,
    ):
        result = apply_vu_expected_claim_rule_to_insurer(
            insurer,
            parameters,
            period=period,
            interest_rate=interest_rate,
            change_shock=False,
        )
        context = SimulationContext(period=period, max_periods=VU14_MAX_PERIODS)
        records = collect_extended_agrsich_records(
            context,
            BAV(entity_id=1),
            [insurer],
            [],
        )
        export_table = next(
            table
            for table in build_agrsich_export_tables(context, records)
            if table.spec.filename == "imsvu014.dat"
        )
        projected_periods.append(
            VU14ProjectionPeriod(
                period=period,
                export_table=export_table,
                expected_claim_values=(
                    result.expected_claim_values[0],
                    result.expected_claim_values[1],
                ),
            )
        )

    return VU14PreShockProjection(periods=tuple(projected_periods))
