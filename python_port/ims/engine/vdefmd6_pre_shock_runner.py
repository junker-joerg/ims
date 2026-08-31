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
    build_vdefmd6_population_for_horizon,
)
from ims.model.vdefmd6_pre_shock_snapshots import (
    Vdefmd6PreShockSnapshotBatch,
    build_vdefmd6_pre_shock_snapshot_batch,
    build_vdefmd6_shock_snapshot_batch,
)
from ims.model.vdefmd6_vu_snapshots import (
    Vdefmd6VUSnapshotBatch,
    build_vdefmd6_shock_vu_snapshot_batch,
    build_vdefmd6_vu_snapshot_batch,
)
from ims.model.vn_insurance_rules import VNSearchInsuranceHistoryEntry


VDEFMD6_PRE_SHOCK_PERIOD_START = 2
VDEFMD6_PRE_SHOCK_PERIOD_END = 49
VDEFMD6_SHOCK_PERIOD_START = 50
VDEFMD6_SHOCK_PERIOD_END = VDEFMD6_MAX_PERIODS
VDEFMD6_PRE_SHOCK_EXECUTION_ORDER = (
    "bav_foreign_information",
    "insurer_rules_by_id",
    "policyholder_rules_by_id",
    "aggregate_export",
)
VDEFMD6_PRE_SHOCK_STATE_POLICY_ID = "vdefmd6-modern-pre-shock-state-v1"
VDEFMD6_100_PERIOD_EXECUTION_ORDER = (
    "activate_subjects",
    *VDEFMD6_PRE_SHOCK_EXECUTION_ORDER,
)
VDEFMD6_100_PERIOD_STATE_POLICY_ID = "vdefmd6-modern-100-period-state-v1"
VDEFMD6_300_PERIOD_END = 300
VDEFMD6_300_PERIOD_EXECUTION_ORDER = VDEFMD6_100_PERIOD_EXECUTION_ORDER
VDEFMD6_300_PERIOD_STATE_POLICY_ID = "vdefmd6-modern-300-period-state-v1"
VDEFMD6_500_PERIOD_END = 500
VDEFMD6_500_PERIOD_EXECUTION_ORDER = VDEFMD6_300_PERIOD_EXECUTION_ORDER
VDEFMD6_500_PERIOD_STATE_POLICY_ID = "vdefmd6-modern-500-period-state-v1"
VDEFMD6_VU_AGGREGATE_FILENAMES = (
    "imsvusk1.dat",
    "imsvuvk1.dat",
    "imsvuvk2.dat",
    "imsvuvk3.dat",
)
VDEFMD6_VN_RULE_GROUP_1_FILENAMES = (
    "imsvnr01.dat",
    "imsvnr02.dat",
    "imsvnr03.dat",
)
VDEFMD6_VN_RULE_GROUP_2_FILENAMES = (
    "imsvnr04.dat",
    "imsvnr05.dat",
    "imsvnr06.dat",
)
VDEFMD6_VN_AGGREGATE_FILENAMES = (
    "imsvnsk1.dat",
    "imsvnvk1.dat",
    "imsvnvk2.dat",
    "imsvnvk3.dat",
)
_VDEFMD6_VU_EXPORT_FILENAMES = ("imsvu014.dat", *VDEFMD6_VU_AGGREGATE_FILENAMES)


@dataclass(frozen=True, slots=True)
class Vdefmd6PreShockPeriodResult:
    period: int
    change_shock: bool
    active_policyholder_count: int
    activated_policyholder_ids: tuple[int, ...]
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
    max_periods: int
    execution_order: tuple[str, ...]
    state_policy_id: str
    period_results: tuple[Vdefmd6PreShockPeriodResult, ...]
    vu14_export_table: ExportTable
    vu_aggregate_export_tables: tuple[ExportTable, ...]
    vn_rule_group_1_export_tables: tuple[ExportTable, ...]
    vn_rule_group_2_export_tables: tuple[ExportTable, ...]
    vn_aggregate_export_tables: tuple[ExportTable, ...]
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

    _validate_base_seed(base_seed)
    return _run_vdefmd6_periods(
        base_seed=base_seed,
        period_end=VDEFMD6_PRE_SHOCK_PERIOD_END,
        execution_order=VDEFMD6_PRE_SHOCK_EXECUTION_ORDER,
        state_policy_id=VDEFMD6_PRE_SHOCK_STATE_POLICY_ID,
    )


def run_vdefmd6_100_periods(*, base_seed: int) -> Vdefmd6PreShockRunResult:
    """Run the controlled modern Vdefmd6 state path through period 100."""

    _validate_base_seed(base_seed)
    return _run_vdefmd6_periods(
        base_seed=base_seed,
        period_end=VDEFMD6_SHOCK_PERIOD_END,
        execution_order=VDEFMD6_100_PERIOD_EXECUTION_ORDER,
        state_policy_id=VDEFMD6_100_PERIOD_STATE_POLICY_ID,
    )


def run_vdefmd6_300_periods(*, base_seed: int) -> Vdefmd6PreShockRunResult:
    """Continue the controlled modern Vdefmd6 state path through period 300."""

    _validate_base_seed(base_seed)
    return _run_vdefmd6_periods(
        base_seed=base_seed,
        period_end=VDEFMD6_300_PERIOD_END,
        execution_order=VDEFMD6_300_PERIOD_EXECUTION_ORDER,
        state_policy_id=VDEFMD6_300_PERIOD_STATE_POLICY_ID,
        max_periods=VDEFMD6_300_PERIOD_END,
    )


def run_vdefmd6_500_periods(*, base_seed: int) -> Vdefmd6PreShockRunResult:
    """Continue the controlled modern Vdefmd6 state path through period 500."""

    _validate_base_seed(base_seed)
    return _run_vdefmd6_periods(
        base_seed=base_seed,
        period_end=VDEFMD6_500_PERIOD_END,
        execution_order=VDEFMD6_500_PERIOD_EXECUTION_ORDER,
        state_policy_id=VDEFMD6_500_PERIOD_STATE_POLICY_ID,
        max_periods=VDEFMD6_500_PERIOD_END,
    )


def _validate_base_seed(base_seed: int) -> None:
    if type(base_seed) is not int or base_seed < 0:
        raise ValueError("Vdefmd6 base_seed must be a non-negative integer")


def _run_vdefmd6_periods(
    *,
    base_seed: int,
    period_end: int,
    execution_order: tuple[str, ...],
    state_policy_id: str,
    max_periods: int = VDEFMD6_MAX_PERIODS,
) -> Vdefmd6PreShockRunResult:

    population = (
        build_vdefmd6_population()
        if max_periods == VDEFMD6_MAX_PERIODS
        else build_vdefmd6_population_for_horizon(max_periods=max_periods)
    )
    bav = BAV(entity_id=1, name="BAV")
    rng = random.Random(base_seed)
    search_history = _initial_search_history(population)
    vu_tables_by_filename = {
        filename: [table]
        for filename, table in _vu_export_tables(
            population,
            bav,
            period=1,
        ).items()
    }
    vn_rule_tables_by_filename = {
        filename: [table]
        for filename, table in _vn_rule_group_1_export_tables(
            population,
            bav,
            period=1,
        ).items()
    }
    vn_rule_group_2_tables_by_filename = {
        filename: [table]
        for filename, table in _vn_rule_group_2_export_tables(
            population,
            bav,
            period=1,
        ).items()
    }
    vn_aggregate_tables_by_filename = {
        filename: [table]
        for filename, table in _vn_aggregate_export_tables(
            population,
            bav,
            period=1,
        ).items()
    }
    period_results: list[Vdefmd6PreShockPeriodResult] = []

    for period in range(VDEFMD6_PRE_SHOCK_PERIOD_START, period_end + 1):
        activated_policyholder_ids = _activate_policyholders(
            population,
            period=period,
        )
        change_shock = period >= VDEFMD6_SHOCK_PERIOD_START
        vu_batch = _build_vu_batch(
            population,
            period=period,
            rng=rng,
            change_shock=change_shock,
        )
        _shift_current_state_to_previous(population)
        context = SimulationContext(
            period=period,
            max_periods=population.max_periods,
            rng_seed=base_seed,
        )
        vu_result = run_loaded_vu_foreign_info_period(
            _loaded_vu_period(context, bav, population, vu_batch)
        )

        _reset_insurer_period_accumulators(population.insurers)
        vn_batch = _build_vn_batch(
            population,
            period=period,
            rng=rng,
            search_history_by_policyholder=search_history,
            change_shock=change_shock,
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
                change_shock=change_shock,
                active_policyholder_count=sum(
                    policyholder.active for policyholder in population.policyholders
                ),
                activated_policyholder_ids=activated_policyholder_ids,
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
        for filename, table in _vu_export_tables(
            population,
            bav,
            period=period,
        ).items():
            vu_tables_by_filename[filename].append(table)
        for filename, table in _vn_rule_group_1_export_tables(
            population,
            bav,
            period=period,
        ).items():
            vn_rule_tables_by_filename[filename].append(table)
        for filename, table in _vn_rule_group_2_export_tables(
            population,
            bav,
            period=period,
        ).items():
            vn_rule_group_2_tables_by_filename[filename].append(table)
        for filename, table in _vn_aggregate_export_tables(
            population,
            bav,
            period=period,
        ).items():
            vn_aggregate_tables_by_filename[filename].append(table)

    vu14_export_table = _merge_export_tables(
        vu_tables_by_filename["imsvu014.dat"]
    )
    vu_aggregate_export_tables = tuple(
        _merge_export_tables(vu_tables_by_filename[filename])
        for filename in VDEFMD6_VU_AGGREGATE_FILENAMES
    )
    vn_rule_group_1_export_tables = tuple(
        _merge_export_tables(vn_rule_tables_by_filename[filename])
        for filename in VDEFMD6_VN_RULE_GROUP_1_FILENAMES
    )
    vn_rule_group_2_export_tables = tuple(
        _merge_export_tables(vn_rule_group_2_tables_by_filename[filename])
        for filename in VDEFMD6_VN_RULE_GROUP_2_FILENAMES
    )
    vn_aggregate_export_tables = tuple(
        _merge_export_tables(vn_aggregate_tables_by_filename[filename])
        for filename in VDEFMD6_VN_AGGREGATE_FILENAMES
    )
    return Vdefmd6PreShockRunResult(
        base_seed=base_seed,
        max_periods=population.max_periods,
        execution_order=execution_order,
        state_policy_id=state_policy_id,
        period_results=tuple(period_results),
        vu14_export_table=vu14_export_table,
        vu_aggregate_export_tables=vu_aggregate_export_tables,
        vn_rule_group_1_export_tables=vn_rule_group_1_export_tables,
        vn_rule_group_2_export_tables=vn_rule_group_2_export_tables,
        vn_aggregate_export_tables=vn_aggregate_export_tables,
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


def _build_vu_batch(
    population: Vdefmd6Population,
    *,
    period: int,
    rng: random.Random,
    change_shock: bool,
) -> Vdefmd6VUSnapshotBatch:
    builder = (
        build_vdefmd6_shock_vu_snapshot_batch
        if change_shock
        else build_vdefmd6_vu_snapshot_batch
    )
    return builder(population, period=period, rng=rng)


def _build_vn_batch(
    population: Vdefmd6Population,
    *,
    period: int,
    rng: random.Random,
    search_history_by_policyholder: dict[
        int, list[VNSearchInsuranceHistoryEntry]
    ],
    change_shock: bool,
) -> Vdefmd6PreShockSnapshotBatch:
    builder = (
        build_vdefmd6_shock_snapshot_batch
        if change_shock
        else build_vdefmd6_pre_shock_snapshot_batch
    )
    return builder(
        population,
        period=period,
        rng=rng,
        search_history_by_policyholder=search_history_by_policyholder,
    )


def _activate_policyholders(
    population: Vdefmd6Population,
    *,
    period: int,
) -> tuple[int, ...]:
    policyholders_by_id = {item.entity_id: item for item in population.policyholders}
    activated: list[int] = []
    for definition in population.policyholder_definitions:
        policyholder = policyholders_by_id[definition.entity_id]
        if (
            definition.activation.activation_period <= period
            and not policyholder.active
        ):
            policyholder.active = True
            activated.append(policyholder.entity_id)
    return tuple(activated)


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


def _vu_export_tables(
    population: Vdefmd6Population,
    bav: BAV,
    *,
    period: int,
) -> dict[str, ExportTable]:
    context = SimulationContext(period=period, max_periods=population.max_periods)
    records = collect_extended_agrsich_records(
        context,
        bav,
        population.insurers,
        population.policyholders,
    )
    tables = {
        table.spec.filename: table
        for table in build_agrsich_export_tables(context, records)
        if table.spec.filename in _VDEFMD6_VU_EXPORT_FILENAMES
    }
    missing = set(_VDEFMD6_VU_EXPORT_FILENAMES) - tables.keys()
    if missing:
        raise ValueError(
            "missing Vdefmd6 VU export tables: " + ", ".join(sorted(missing))
        )
    return tables


def _vn_rule_group_1_export_tables(
    population: Vdefmd6Population,
    bav: BAV,
    *,
    period: int,
) -> dict[str, ExportTable]:
    context = SimulationContext(period=period, max_periods=population.max_periods)
    records = collect_extended_agrsich_records(
        context,
        bav,
        population.insurers,
        population.policyholders,
    )
    tables = {
        table.spec.filename: table
        for table in build_agrsich_export_tables(context, records)
        if table.spec.filename in VDEFMD6_VN_RULE_GROUP_1_FILENAMES
    }
    missing = set(VDEFMD6_VN_RULE_GROUP_1_FILENAMES) - tables.keys()
    if missing:
        raise ValueError(
            "missing Vdefmd6 VN rule group 1 export tables: "
            + ", ".join(sorted(missing))
        )
    return tables


def _vn_rule_group_2_export_tables(
    population: Vdefmd6Population,
    bav: BAV,
    *,
    period: int,
) -> dict[str, ExportTable]:
    context = SimulationContext(period=period, max_periods=population.max_periods)
    records = collect_extended_agrsich_records(
        context,
        bav,
        population.insurers,
        population.policyholders,
    )
    tables = {
        table.spec.filename: table
        for table in build_agrsich_export_tables(context, records)
        if table.spec.filename in VDEFMD6_VN_RULE_GROUP_2_FILENAMES
    }
    missing = set(VDEFMD6_VN_RULE_GROUP_2_FILENAMES) - tables.keys()
    if missing:
        raise ValueError(
            "missing Vdefmd6 VN rule group 2 export tables: "
            + ", ".join(sorted(missing))
        )
    return tables


def _vn_aggregate_export_tables(
    population: Vdefmd6Population,
    bav: BAV,
    *,
    period: int,
) -> dict[str, ExportTable]:
    context = SimulationContext(period=period, max_periods=population.max_periods)
    records = collect_extended_agrsich_records(
        context,
        bav,
        population.insurers,
        population.policyholders,
    )
    tables = {
        table.spec.filename: table
        for table in build_agrsich_export_tables(context, records)
        if table.spec.filename in VDEFMD6_VN_AGGREGATE_FILENAMES
    }
    missing = set(VDEFMD6_VN_AGGREGATE_FILENAMES) - tables.keys()
    if missing:
        raise ValueError(
            "missing Vdefmd6 VN aggregate export tables: "
            + ", ".join(sorted(missing))
        )
    return tables


def _merge_export_tables(tables: list[ExportTable]) -> ExportTable:
    first = tables[0]
    return ExportTable(
        spec=first.spec,
        header=first.header,
        rows=[table.rows[0] for table in tables],
    )
