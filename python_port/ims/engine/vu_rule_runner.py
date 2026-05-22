from dataclasses import dataclass
import json
from pathlib import Path

from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
from ims.io.scenario_loader import LoadedScenario, load_scenario, load_scenario_from_mapping
from ims.model.agrsich_export import compute_global_period
from ims.model.bav_service import BAVForeignInfoResult, compute_extended_foreign_info
from ims.model.entities import BAV, Insurer, Policyholder
from ims.model.vu_rules import (
    VUExpectedClaimRuleApplication,
    VUFreeLinearRuleApplication,
    VUForeignInfoRuleApplication,
    VUMarketShareMarkupRuleApplication,
    VUNetSwitcherMarkupRuleApplication,
    VURandomNormalRuleApplication,
    VURandomUniformRuleApplication,
    VUReserveMarkupRuleApplication,
    apply_vu_expected_claim_rule_snapshots,
    apply_vu_free_linear_rule_snapshots,
    apply_vu_foreign_info_rule_snapshots,
    apply_vu_market_share_markup_rule_snapshots,
    apply_vu_net_switcher_markup_rule_snapshots,
    apply_vu_random_normal_rule_snapshots,
    apply_vu_random_uniform_rule_snapshots,
    apply_vu_reserve_markup_rule_snapshots,
)


@dataclass(slots=True)
class VUForeignInfoPeriodRunResult:
    """Ergebnis eines kleinen deterministischen VU-Frmdinf-Periodenschritts."""

    context_period: int
    context_global_period: int
    context_logtime: int
    bav: BAV
    insurers: list[Insurer]
    policyholders: list[Policyholder]
    foreign_info: BAVForeignInfoResult
    rule_applications: list[VUForeignInfoRuleApplication]
    random_uniform_applications: list[VURandomUniformRuleApplication]
    random_normal_applications: list[VURandomNormalRuleApplication]
    reserve_markup_applications: list[VUReserveMarkupRuleApplication]
    net_switcher_markup_applications: list[VUNetSwitcherMarkupRuleApplication]
    expected_claim_applications: list[VUExpectedClaimRuleApplication]
    market_share_markup_applications: list[VUMarketShareMarkupRuleApplication]
    free_linear_applications: list[VUFreeLinearRuleApplication]
    aggregate_snapshot: AggregateSnapshot


@dataclass(slots=True)
class VUForeignInfoCarryover:
    """Diagnose der kontrollierten Fortschreibung von VU-Aktuellwerten."""

    from_period: int
    to_period: int
    from_global_period: int
    to_global_period: int
    insurer_ids: list[int]


@dataclass(slots=True)
class VUForeignInfoMultiPeriodRunResult:
    """Ergebnis eines kleinen deterministischen Mehrperiodenlaufs."""

    period_results: list[VUForeignInfoPeriodRunResult]
    processed_periods: list[int]
    processed_local_periods: list[int]
    processed_global_periods: list[int]
    total_rule_applications: int
    carryovers: list[VUForeignInfoCarryover]


def run_loaded_vu_foreign_info_period(loaded: LoadedScenario) -> VUForeignInfoPeriodRunResult:
    """
    Fuehrt einen kleinen fachlichen Periodenschritt fuer explizite VU-Frmdinf-Snapshots aus.

    Dieser Pfad berechnet zuerst die bereits portierten BAV-Fremdinformationen aus
    Vorperiodenwerten und wendet danach nur explizit geladene VU-Regelparameter-
    Snapshots an. Er ist kein Scheduler und keine vollstaendige historische Simulation.
    """

    _validate_disjoint_vu_rule_snapshot_targets(loaded)
    foreign_info = compute_extended_foreign_info(
        loaded.context,
        loaded.bav,
        loaded.insurers,
        loaded.policyholders,
    )
    rule_applications = apply_vu_foreign_info_rule_snapshots(
        loaded.insurers,
        loaded.bav,
        loaded.vu_foreign_info_rule_snapshots,
        period=loaded.context.period,
    )
    random_uniform_applications = apply_vu_random_uniform_rule_snapshots(
        loaded.insurers,
        loaded.vu_random_uniform_rule_snapshots,
        period=loaded.context.period,
    )
    random_normal_applications = apply_vu_random_normal_rule_snapshots(
        loaded.insurers,
        loaded.vu_random_normal_rule_snapshots,
        period=loaded.context.period,
    )
    reserve_markup_applications = apply_vu_reserve_markup_rule_snapshots(
        loaded.insurers,
        loaded.vu_reserve_markup_rule_snapshots,
        period=loaded.context.period,
    )
    net_switcher_markup_applications = apply_vu_net_switcher_markup_rule_snapshots(
        loaded.insurers,
        loaded.vu_net_switcher_markup_rule_snapshots,
        period=loaded.context.period,
    )
    expected_claim_applications = apply_vu_expected_claim_rule_snapshots(
        loaded.insurers,
        loaded.vu_expected_claim_rule_snapshots,
        period=loaded.context.period,
    )
    market_share_markup_applications = apply_vu_market_share_markup_rule_snapshots(
        loaded.insurers,
        loaded.vu_market_share_markup_rule_snapshots,
        period=loaded.context.period,
    )
    free_linear_applications = apply_vu_free_linear_rule_snapshots(
        loaded.insurers,
        loaded.vu_free_linear_rule_snapshots,
        period=loaded.context.period,
    )
    aggregate_snapshot = collect_basic_aggregates(
        context=loaded.context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
    )
    return VUForeignInfoPeriodRunResult(
        context_period=loaded.context.period,
        context_global_period=compute_global_period(loaded.context),
        context_logtime=loaded.context.logtime,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        foreign_info=foreign_info,
        rule_applications=rule_applications,
        random_uniform_applications=random_uniform_applications,
        random_normal_applications=random_normal_applications,
        reserve_markup_applications=reserve_markup_applications,
        net_switcher_markup_applications=net_switcher_markup_applications,
        expected_claim_applications=expected_claim_applications,
        market_share_markup_applications=market_share_markup_applications,
        free_linear_applications=free_linear_applications,
        aggregate_snapshot=aggregate_snapshot,
    )


def _snapshot_insurer_ids(snapshots: object) -> list[int]:
    return [int(snapshot.insurer_id) for snapshot in snapshots]


def _validate_disjoint_vu_rule_snapshot_targets(loaded: LoadedScenario) -> None:
    rule_sets = [
        ("vu_foreign_info_rule_snapshots", _snapshot_insurer_ids(loaded.vu_foreign_info_rule_snapshots)),
        ("vu_random_uniform_rule_snapshots", _snapshot_insurer_ids(loaded.vu_random_uniform_rule_snapshots)),
        ("vu_random_normal_rule_snapshots", _snapshot_insurer_ids(loaded.vu_random_normal_rule_snapshots)),
        ("vu_reserve_markup_rule_snapshots", _snapshot_insurer_ids(loaded.vu_reserve_markup_rule_snapshots)),
        ("vu_net_switcher_markup_rule_snapshots", _snapshot_insurer_ids(loaded.vu_net_switcher_markup_rule_snapshots)),
        ("vu_expected_claim_rule_snapshots", _snapshot_insurer_ids(loaded.vu_expected_claim_rule_snapshots)),
        ("vu_market_share_markup_rule_snapshots", _snapshot_insurer_ids(loaded.vu_market_share_markup_rule_snapshots)),
        ("vu_free_linear_rule_snapshots", _snapshot_insurer_ids(loaded.vu_free_linear_rule_snapshots)),
    ]
    seen: dict[int, str] = {}
    duplicates: list[str] = []
    conflicts: list[str] = []
    for rule_set_name, insurer_ids in rule_sets:
        seen_in_rule_set: set[int] = set()
        for insurer_id in sorted(insurer_ids):
            if insurer_id in seen_in_rule_set:
                duplicates.append(f"insurer {insurer_id}: {rule_set_name}")
                continue
            seen_in_rule_set.add(insurer_id)
            previous_rule_set = seen.get(insurer_id)
            if previous_rule_set is not None:
                conflicts.append(f"insurer {insurer_id}: {previous_rule_set} and {rule_set_name}")
            else:
                seen[insurer_id] = rule_set_name
    if duplicates:
        details = "; ".join(duplicates)
        raise ValueError(f"VU rule snapshot sets reject duplicate insurer targets per period: {details}")
    if conflicts:
        details = "; ".join(conflicts)
        raise ValueError(f"VU rule snapshot sets must target disjoint insurers per period: {details}")


def run_vu_foreign_info_period_from_mapping(data: dict) -> VUForeignInfoPeriodRunResult:
    """Laedt ein In-Memory-Szenario und fuehrt den kleinen VU-Frmdinf-Periodenschritt aus."""

    return run_loaded_vu_foreign_info_period(load_scenario_from_mapping(data))


def run_vu_foreign_info_period_from_fixture(path: str | Path) -> VUForeignInfoPeriodRunResult:
    """Laedt ein Szenariofile und fuehrt den kleinen VU-Frmdinf-Periodenschritt aus."""

    return run_loaded_vu_foreign_info_period(load_scenario(path))


def _set_two_sector_state(
    insurer: Insurer,
    *,
    premiums: list[float],
    advertising: list[float],
    reserves: list[float],
    policyholders: list[float],
) -> None:
    insurer.premiums_prev_sector = list(premiums)
    insurer.premiums_prev = float(premiums[0]) if premiums else 0.0
    insurer.premiums_current_sector = list(premiums)
    insurer.premiums_current = float(premiums[0]) if premiums else 0.0
    insurer.advertising_prev_sector = list(advertising)
    insurer.advertising_prev = float(advertising[0]) if advertising else 0.0
    insurer.advertising_current_sector = list(advertising)
    insurer.advertising_current = float(advertising[0]) if advertising else 0.0
    insurer.reserves_prev_sector = list(reserves)
    insurer.reserves_prev = float(reserves[0]) if reserves else 0.0
    insurer.reserves_current = list(reserves)
    insurer.policyholders_current_sector = list(policyholders)
    insurer.policyholders_current = float(policyholders[0]) if policyholders else 0.0


def apply_vu_foreign_info_carryover(
    previous_result: VUForeignInfoPeriodRunResult,
    loaded: LoadedScenario,
) -> VUForeignInfoCarryover | None:
    """Schreibt berechnete aktuelle VU-Werte kontrolliert in das Folgeszenario."""

    previous_insurers = {insurer.entity_id: insurer for insurer in previous_result.insurers}
    carried_ids: list[int] = []
    for insurer in loaded.insurers:
        previous = previous_insurers.get(insurer.entity_id)
        if previous is None:
            continue
        _set_two_sector_state(
            insurer,
            premiums=previous.premiums_current_sector,
            advertising=previous.advertising_current_sector,
            reserves=previous.reserves_current,
            policyholders=(
                previous.policyholders_current_sector
                if previous.policyholders_current_sector
                else [previous.policyholders_current, previous.policyholders_current]
            ),
        )
        insurer.active_prev = previous.active
        carried_ids.append(insurer.entity_id)

    if not carried_ids:
        return None
    return VUForeignInfoCarryover(
        from_period=previous_result.context_period,
        to_period=loaded.context.period,
        from_global_period=previous_result.context_global_period,
        to_global_period=compute_global_period(loaded.context),
        insurer_ids=carried_ids,
    )


def _validate_strictly_increasing_periods(processed_periods: list[int]) -> list[int]:
    if not processed_periods:
        raise ValueError("VU foreign-info multi-period run requires at least one period scenario")
    if len(set(processed_periods)) != len(processed_periods):
        raise ValueError("VU foreign-info multi-period run rejects duplicate periods")
    if processed_periods != sorted(processed_periods):
        raise ValueError("VU foreign-info multi-period run requires increasing periods")
    return processed_periods


def run_vu_foreign_info_multi_period_from_mappings(
    period_scenarios: list[dict],
    *,
    carry_forward_insurer_state: bool = False,
) -> VUForeignInfoMultiPeriodRunResult:
    """Fuehrt mehrere explizite VU-Frmdinf-Periodenszenarien deterministisch aus."""

    if not isinstance(period_scenarios, list):
        raise ValueError("VU foreign-info multi-period run requires a list of period scenarios")

    loaded_scenarios = [load_scenario_from_mapping(period_scenario) for period_scenario in period_scenarios]
    processed_global_periods = _validate_strictly_increasing_periods(
        [compute_global_period(loaded.context) for loaded in loaded_scenarios]
    )

    period_results: list[VUForeignInfoPeriodRunResult] = []
    carryovers: list[VUForeignInfoCarryover] = []
    for loaded in loaded_scenarios:
        if carry_forward_insurer_state and period_results:
            carryover = apply_vu_foreign_info_carryover(period_results[-1], loaded)
            if carryover is not None:
                carryovers.append(carryover)
        period_results.append(run_loaded_vu_foreign_info_period(loaded))

    return VUForeignInfoMultiPeriodRunResult(
        period_results=period_results,
        processed_periods=[loaded.context.period for loaded in loaded_scenarios],
        processed_local_periods=[loaded.context.period for loaded in loaded_scenarios],
        processed_global_periods=processed_global_periods,
        total_rule_applications=sum(
            len(result.rule_applications)
            + len(result.random_uniform_applications)
            + len(result.random_normal_applications)
            + len(result.reserve_markup_applications)
            + len(result.net_switcher_markup_applications)
            + len(result.expected_claim_applications)
            + len(result.market_share_markup_applications)
            + len(result.free_linear_applications)
            for result in period_results
        ),
        carryovers=carryovers,
    )


def _period_scenarios_from_fixture_payload(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        period_scenarios = payload.get("periods")
        if isinstance(period_scenarios, list):
            return period_scenarios
    raise ValueError("VU foreign-info multi-period fixture requires a list or object field: periods")


def _carry_forward_insurer_state_from_fixture_payload(payload: object) -> bool:
    if not isinstance(payload, dict) or "carry_forward_insurer_state" not in payload:
        return False
    value = payload["carry_forward_insurer_state"]
    if not isinstance(value, bool):
        raise ValueError("VU foreign-info multi-period fixture field carry_forward_insurer_state must be a boolean")
    return value


def run_vu_foreign_info_multi_period_from_fixture(
    path: str | Path,
    *,
    carry_forward_insurer_state: bool = False,
) -> VUForeignInfoMultiPeriodRunResult:
    """Laedt ein Mehrperioden-Fixture und fuehrt den kleinen VU-Frmdinf-Lauf aus."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    fixture_carry_forward_insurer_state = _carry_forward_insurer_state_from_fixture_payload(payload)
    return run_vu_foreign_info_multi_period_from_mappings(
        _period_scenarios_from_fixture_payload(payload),
        carry_forward_insurer_state=carry_forward_insurer_state or fixture_carry_forward_insurer_state,
    )
