from __future__ import annotations

from dataclasses import dataclass
import random

from ims.engine.context import SimulationContext
from ims.engine.vn_rule_runner import run_vn_settlement_period
from ims.engine.vu_rule_runner import run_loaded_vu_foreign_info_period
from ims.io.scenario_loader import LoadedScenario
from ims.model.agrsich_export import ExportTable, build_agrsich_export_tables
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.entities import BAV, Insurer, Policyholder
from ims.model.vdefmd6_population import (
    VDEFMD6_MAX_PERIODS,
    Vdefmd6Population,
    build_vdefmd6_population,
)
from ims.model.vdefmd6_pre_shock_snapshots import (
    Vdefmd6PreShockSnapshotBatch,
    build_vdefmd6_pre_shock_snapshot_batch,
)
from ims.model.vdefmd6_vu_snapshots import (
    Vdefmd6VUSnapshotBatch,
    build_vdefmd6_vu_snapshot_batch,
)
from ims.model.vn_insurance_rules import VNSearchInsuranceHistoryEntry


VDEFMD6_PRE_SHOCK_PERIOD_START = 2
VDEFMD6_PRE_SHOCK_PERIOD_END = 49
VDEFMD6_PRE_SHOCK_EXECUTION_ORDER = (
    "bav_foreign_information",
    "insurer_rules_by_id",
    "policyholder_rules_by_id",
    "aggregate_export",
)
VDEFMD6_PRE_SHOCK_STATE_POLICY_ID = "vdefmd6-modern-pre-shock-state-v1"


@dataclass(frozen=True, slots=True)
class Vdefmd6PreShockPeriodResult:
    period: int
    vu_snapshot_count: int
    vn_insurance_snapshot_count: int
    vn_damage_snapshot_count: int
    vu_rule_application_count: int
    vn_insurance_rule_application_count: int
    vn_damage_settlement_application_count: int
    information_cost: float
    information_cost_policyholder_count: int
    vu_uniform_value_count: int
    vu_normal_value_count: int
    vn_uniform_value_count: int
    vn_normal_value_count: int


@dataclass(frozen=True, slots=True)
class Vdefmd6PreShockRunResult:
    base_seed: int
    execution_order: tuple[str, ...]
    state_policy_id: str
    period_results: tuple[Vdefmd6PreShockPeriodResult, ...]
    vu14_export_table: ExportTable
    total_information_cost: float
    total_information_cost_policyholders: int
    total_vu_rule_applications: int
    total_vn_insurance_rule_applications: int
    total_vn_damage_settlement_applications: int
    total_uniform_value_count: int
    total_normal_value_count: int
    legacy_rows_used_as_generation_input: bool = False
    writes_performed: bool = False
    scheduler_started: bool = False
    simulation_performed: bool = False
    historical_same_slot_order_claimed: bool = False
    historical_rng_equality_claimed: bool = False
    historical_full_equality_claimed: bool = False


def run_vdefmd6_pre_shock_periods(*, base_seed: int) -> Vdefmd6PreShockRunResult:
    """Run the explicit modern Vdefmd6 state path for periods 2 through 49."""

    if type(base_seed) is not int or base_seed < 0:
        raise ValueError("Vdefmd6 pre-shock base_seed must be a non-negative integer")

    population = build_vdefmd6_population()
    bav = BAV(entity_id=1, name="BAV")
    rng = random.Random(base_seed)
    search_history = _initial_search_history(population)
    vu14_tables = [_vu14_export_table(population, bav, period=1)]
    period_results: list[Vdefmd6PreShockPeriodResult] = []

    for period in range(VDEFMD6_PRE_SHOCK_PERIOD_START, VDEFMD6_PRE_SHOCK_PERIOD_END + 1):
        vu_batch = build_vdefmd6_vu_snapshot_batch(
            population,
            period=period,
            rng=rng,
        )
        _shift_current_state_to_previous(population)
        context = SimulationContext(
            period=period,
            max_periods=VDEFMD6_MAX_PERIODS,
            rng_seed=base_seed,
        )
        vu_result = run_loaded_vu_foreign_info_period(
            _loaded_vu_period(context, bav, population, vu_batch)
        )

        _reset_insurer_period_accumulators(population.insurers)
        vn_batch = build_vdefmd6_pre_shock_snapshot_batch(
            population,
            period=period,
            rng=rng,
            search_history_by_policyholder=search_history,
        )
        vn_result = run_vn_settlement_period(
            context,
            population.insurers,
            population.policyholders,
            insurance_rule_snapshots=list(vn_batch.insurance_snapshots),
            damage_settlement_snapshots=list(vn_batch.damage_snapshots),
        )
        _append_search_history(search_history, population.policyholders, period=period)

        settlement_results = [
            application.settlement_result
            for application in vn_result.damage_settlement_applications
        ]
        information_costs = [result.information_cost for result in settlement_results]
        period_results.append(
            Vdefmd6PreShockPeriodResult(
                period=period,
                vu_snapshot_count=vu_batch.snapshot_count,
                vn_insurance_snapshot_count=len(vn_batch.insurance_snapshots),
                vn_damage_snapshot_count=len(vn_batch.damage_snapshots),
                vu_rule_application_count=_vu_rule_application_count(vu_result),
                vn_insurance_rule_application_count=len(
                    vn_result.insurance_rule_applications
                ),
                vn_damage_settlement_application_count=len(
                    vn_result.damage_settlement_applications
                ),
                information_cost=sum(information_costs),
                information_cost_policyholder_count=sum(
                    value > 0.0 for value in information_costs
                ),
                vu_uniform_value_count=vu_batch.uniform_value_count,
                vu_normal_value_count=vu_batch.normal_value_count,
                vn_uniform_value_count=vn_batch.draw_summary.uniform_values,
                vn_normal_value_count=vn_batch.draw_summary.normal_values,
            )
        )
        vu14_tables.append(_vu14_export_table(population, bav, period=period))

    vu14_export_table = ExportTable(
        spec=vu14_tables[0].spec,
        header=vu14_tables[0].header,
        rows=[table.rows[0] for table in vu14_tables],
    )
    return Vdefmd6PreShockRunResult(
        base_seed=base_seed,
        execution_order=VDEFMD6_PRE_SHOCK_EXECUTION_ORDER,
        state_policy_id=VDEFMD6_PRE_SHOCK_STATE_POLICY_ID,
        period_results=tuple(period_results),
        vu14_export_table=vu14_export_table,
        total_information_cost=sum(item.information_cost for item in period_results),
        total_information_cost_policyholders=sum(
            item.information_cost_policyholder_count for item in period_results
        ),
        total_vu_rule_applications=sum(
            item.vu_rule_application_count for item in period_results
        ),
        total_vn_insurance_rule_applications=sum(
            item.vn_insurance_rule_application_count for item in period_results
        ),
        total_vn_damage_settlement_applications=sum(
            item.vn_damage_settlement_application_count for item in period_results
        ),
        total_uniform_value_count=sum(
            item.vu_uniform_value_count + item.vn_uniform_value_count
            for item in period_results
        ),
        total_normal_value_count=sum(
            item.vu_normal_value_count + item.vn_normal_value_count
            for item in period_results
        ),
    )


def _loaded_vu_period(
    context: SimulationContext,
    bav: BAV,
    population: Vdefmd6Population,
    batch: Vdefmd6VUSnapshotBatch,
) -> LoadedScenario:
    return LoadedScenario(
        context=context,
        bav=bav,
        insurers=population.insurers,
        policyholders=population.policyholders,
        vu_foreign_info_rule_snapshots=list(batch.foreign_info_snapshots),
        vu_random_uniform_rule_snapshots=list(batch.random_uniform_snapshots),
        vu_random_normal_rule_snapshots=list(batch.random_normal_snapshots),
        vu_reserve_markup_rule_snapshots=list(batch.reserve_markup_snapshots),
        vu_net_switcher_markup_rule_snapshots=list(
            batch.net_switcher_markup_snapshots
        ),
        vu_expected_claim_rule_snapshots=list(batch.expected_claim_snapshots),
        vu_market_share_markup_rule_snapshots=list(
            batch.market_share_markup_snapshots
        ),
    )


def _shift_current_state_to_previous(population: Vdefmd6Population) -> None:
    for insurer in population.insurers:
        insurer.premiums_prev_sector = list(insurer.premiums_current_sector)
        insurer.premiums_prev = float(insurer.premiums_current_sector[0])
        insurer.advertising_prev_sector = list(insurer.advertising_current_sector)
        insurer.advertising_prev = float(insurer.advertising_current_sector[0])
        insurer.reserves_prev_sector = list(insurer.reserves_current)
        insurer.reserves_prev = float(insurer.reserves_current[0])
        insurer.policyholders_prev_sector = list(insurer.policyholders_current_sector)
        insurer.policyholders_prev = float(insurer.policyholders_current_sector[0])
        insurer.active_prev = insurer.active

    for policyholder in population.policyholders:
        policyholder.insured_prev_sector = list(policyholder.insured_current_sector)
        policyholder.insured_prev = float(policyholder.insured_current_sector[0])
        policyholder.active_prev = policyholder.active


def _reset_insurer_period_accumulators(insurers: list[Insurer]) -> None:
    for insurer in insurers:
        insurer.policyholders_current_sector = [0.0, 0.0]
        insurer.policyholders_current = 0.0
        insurer.claims_count_current = [0, 0]
        insurer.claims_sum_current = [0.0, 0.0]


def _initial_search_history(
    population: Vdefmd6Population,
) -> dict[int, list[VNSearchInsuranceHistoryEntry]]:
    return {
        definition.entity_id: [
            VNSearchInsuranceHistoryEntry(
                period=1,
                sector_index=sector_index,
                insured=False,
                premium=0.0,
            )
            for sector_index in range(2)
        ]
        for definition in population.policyholder_definitions
        if definition.action.rule_id == 4
    }


def _append_search_history(
    history: dict[int, list[VNSearchInsuranceHistoryEntry]],
    policyholders: list[Policyholder],
    *,
    period: int,
) -> None:
    policyholders_by_id = {item.entity_id: item for item in policyholders}
    for policyholder_id, entries in history.items():
        policyholder = policyholders_by_id[policyholder_id]
        for sector_index in range(2):
            insured = bool(policyholder.insured_current_sector[sector_index])
            entries.append(
                VNSearchInsuranceHistoryEntry(
                    period=period,
                    sector_index=sector_index,
                    insured=insured,
                    insurer_id=(
                        policyholder.chosen_insurer_sector_current[sector_index]
                        if insured
                        else None
                    ),
                    premium=float(policyholder.paid_premium_current[sector_index]),
                )
            )


def _vu_rule_application_count(result: object) -> int:
    return sum(
        len(getattr(result, name))
        for name in (
            "rule_applications",
            "random_uniform_applications",
            "random_normal_applications",
            "reserve_markup_applications",
            "net_switcher_markup_applications",
            "expected_claim_applications",
            "market_share_markup_applications",
            "free_linear_applications",
        )
    )


def _vu14_export_table(
    population: Vdefmd6Population,
    bav: BAV,
    *,
    period: int,
) -> ExportTable:
    context = SimulationContext(period=period, max_periods=VDEFMD6_MAX_PERIODS)
    records = collect_extended_agrsich_records(
        context,
        bav,
        population.insurers,
        population.policyholders,
    )
    return next(
        table
        for table in build_agrsich_export_tables(context, records)
        if table.spec.filename == "imsvu014.dat"
    )
