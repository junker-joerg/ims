from dataclasses import dataclass, field
import json
from pathlib import Path

from ims.engine.context import SimulationContext
from ims.io.scenario_loader import LoadedScenario, load_scenario, load_scenario_from_mapping
from ims.model.entities import Insurer, Policyholder
from ims.model.vn_rules import (
    VNDamageSettlementApplication,
    VNDamageSettlementSnapshot,
    VNSettlementApplication,
    VNSettlementSnapshot,
    apply_vn_damage_settlement_snapshots,
    apply_vn_settlement_snapshots,
)


@dataclass(slots=True)
class VNSettlementPeriodRunResult:
    """Kleines Ergebnis eines expliziten VN-Periodenschritts."""

    period: int
    insurers: list[Insurer] = field(default_factory=list)
    policyholders: list[Policyholder] = field(default_factory=list)
    damage_settlement_applications: list[VNDamageSettlementApplication] = field(default_factory=list)
    settlement_applications: list[VNSettlementApplication] = field(default_factory=list)

    @property
    def total_settlement_applications(self) -> int:
        return len(self.damage_settlement_applications) + len(self.settlement_applications)

    @property
    def total_damage_settlement_applications(self) -> int:
        return len(self.damage_settlement_applications)


@dataclass(slots=True)
class VNStateCarryover:
    """Diagnose der kontrollierten Fortschreibung von VN-/VU-Aktuellwerten."""

    from_period: int
    to_period: int
    insurer_ids: list[int]
    policyholder_ids: list[int]


@dataclass(slots=True)
class VNSettlementMultiPeriodRunResult:
    """Ergebnis eines kleinen deterministischen VN-Mehrperiodenlaufs."""

    period_results: list[VNSettlementPeriodRunResult]
    processed_periods: list[int]
    total_settlement_applications: int
    total_damage_settlement_applications: int
    carryovers: list[VNStateCarryover] = field(default_factory=list)


def _validate_disjoint_vn_snapshot_targets(
    *,
    damage_settlement_snapshots: list[VNDamageSettlementSnapshot],
    settlement_snapshots: list[VNSettlementSnapshot],
) -> None:
    damage_targets = [snapshot.policyholder_id for snapshot in damage_settlement_snapshots]
    settlement_targets = [snapshot.policyholder_id for snapshot in settlement_snapshots]
    duplicate_damage_targets = sorted(
        policyholder_id
        for policyholder_id in set(damage_targets)
        if damage_targets.count(policyholder_id) > 1
    )
    duplicate_settlement_targets = sorted(
        policyholder_id
        for policyholder_id in set(settlement_targets)
        if settlement_targets.count(policyholder_id) > 1
    )
    conflicts = sorted(set(damage_targets) & set(settlement_targets))
    if duplicate_damage_targets:
        values = ", ".join(str(policyholder_id) for policyholder_id in duplicate_damage_targets)
        raise ValueError(f"duplicate VN damage settlement snapshot targets per period: {values}")
    if duplicate_settlement_targets:
        values = ", ".join(str(policyholder_id) for policyholder_id in duplicate_settlement_targets)
        raise ValueError(f"duplicate VN settlement snapshot targets per period: {values}")
    if conflicts:
        values = ", ".join(str(policyholder_id) for policyholder_id in conflicts)
        raise ValueError(f"VN snapshot sets must target disjoint policyholders per period: {values}")


def run_vn_settlement_period(
    context: SimulationContext,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
    *,
    damage_settlement_snapshots: list[VNDamageSettlementSnapshot] | None = None,
    settlement_snapshots: list[VNSettlementSnapshot] | None = None,
) -> VNSettlementPeriodRunResult:
    """
    Wendet explizite VN-Schaden- und Settlement-Snapshots fuer eine Periode an.

    Dieser Runner ist bewusst kein historischer PlanVN-Scheduler. Er stellt nur den
    portierten deterministischen Schaden- und Abrechnungskern als kleinen
    Periodenschritt bereit.
    """

    damage_settlement_snapshots = damage_settlement_snapshots or []
    settlement_snapshots = settlement_snapshots or []
    _validate_disjoint_vn_snapshot_targets(
        damage_settlement_snapshots=damage_settlement_snapshots,
        settlement_snapshots=settlement_snapshots,
    )
    damage_settlement_applications = apply_vn_damage_settlement_snapshots(
        policyholders,
        insurers,
        damage_settlement_snapshots,
    )
    applications = apply_vn_settlement_snapshots(
        policyholders,
        insurers,
        settlement_snapshots,
    )
    return VNSettlementPeriodRunResult(
        period=context.period,
        insurers=insurers,
        policyholders=policyholders,
        damage_settlement_applications=damage_settlement_applications,
        settlement_applications=applications,
    )


def run_loaded_vn_settlement_period(loaded: LoadedScenario) -> VNSettlementPeriodRunResult:
    """Fuehrt den expliziten VN-Periodenschritt fuer ein geladenes Szenario aus."""

    return run_vn_settlement_period(
        loaded.context,
        loaded.insurers,
        loaded.policyholders,
        damage_settlement_snapshots=loaded.vn_damage_settlement_snapshots,
        settlement_snapshots=loaded.vn_settlement_snapshots,
    )


def run_vn_settlement_period_from_mapping(data: dict) -> VNSettlementPeriodRunResult:
    """Laedt ein In-Memory-Szenario und fuehrt den expliziten VN-Periodenschritt aus."""

    return run_loaded_vn_settlement_period(load_scenario_from_mapping(data))


def run_vn_settlement_period_from_fixture(path: str | Path) -> VNSettlementPeriodRunResult:
    """Laedt ein Szenariofile und fuehrt den expliziten VN-Periodenschritt aus."""

    return run_loaded_vn_settlement_period(load_scenario(path))


def _validate_strictly_increasing_periods(processed_periods: list[int]) -> list[int]:
    if not processed_periods:
        raise ValueError("VN settlement multi-period run requires at least one period scenario")
    if len(set(processed_periods)) != len(processed_periods):
        raise ValueError("VN settlement multi-period run rejects duplicate periods")
    if processed_periods != sorted(processed_periods):
        raise ValueError("VN settlement multi-period run requires increasing periods")
    return processed_periods


def _two_float_values(values: list[float], fallback: float = 0.0) -> list[float]:
    if len(values) >= 2:
        return [float(values[0]), float(values[1])]
    if len(values) == 1:
        return [float(values[0]), float(values[0])]
    return [float(fallback), float(fallback)]


def _two_int_values(values: list[int], fallback: int = 0) -> list[int]:
    if len(values) >= 2:
        return [int(values[0]), int(values[1])]
    if len(values) == 1:
        return [int(values[0]), int(values[0])]
    return [int(fallback), int(fallback)]


def _carry_insurer_state(previous: Insurer, current: Insurer) -> None:
    premiums = _two_float_values(previous.premiums_current_sector, fallback=previous.premiums_current)
    advertising = _two_float_values(previous.advertising_current_sector, fallback=previous.advertising_current)
    reserves = _two_float_values(previous.reserves_current, fallback=0.0)
    policyholders = _two_float_values(
        previous.policyholders_current_sector,
        fallback=previous.policyholders_current,
    )
    claims_count = _two_int_values(previous.claims_count_current, fallback=0)
    claims_sum = _two_float_values(previous.claims_sum_current, fallback=0.0)

    current.premiums_prev_sector = list(premiums)
    current.premiums_prev = float(premiums[0])
    current.premiums_current_sector = list(premiums)
    current.premiums_current = float(premiums[0])
    current.advertising_prev_sector = list(advertising)
    current.advertising_prev = float(advertising[0])
    current.advertising_current_sector = list(advertising)
    current.advertising_current = float(advertising[0])
    current.reserves_prev_sector = list(reserves)
    current.reserves_prev = float(reserves[0])
    current.reserves_current = list(reserves)
    current.policyholders_current_sector = list(policyholders)
    current.policyholders_current = float(policyholders[0])
    current.claims_count_current = list(claims_count)
    current.claims_sum_current = list(claims_sum)
    current.active_prev = previous.active


def _carry_policyholder_state(previous: Policyholder, current: Policyholder) -> None:
    insured = _two_float_values(previous.insured_current_sector, fallback=previous.insured_current)
    current.insured_prev_sector = list(insured)
    current.insured_prev = float(previous.insured_current)
    current.insured_current_sector = list(insured)
    current.insured_current = float(previous.insured_current)
    current.active_prev = previous.active
    current.insurer_id = (
        previous.chosen_insurer_current
        if previous.chosen_insurer_current is not None
        else previous.insurer_id
    )
    current.chosen_insurer_current = previous.chosen_insurer_current
    current.chosen_insurer_sector_current = list(previous.chosen_insurer_sector_current)
    current.paid_premium_current = _two_float_values(previous.paid_premium_current, fallback=0.0)
    current.self_damage_current = _two_float_values(previous.self_damage_current, fallback=0.0)
    current.claim_sum_current = _two_float_values(previous.claim_sum_current, fallback=0.0)
    current.end_wealth_sector_current = _two_float_values(previous.end_wealth_sector_current, fallback=0.0)
    current.end_wealth_current = float(previous.end_wealth_current)


def _apply_vn_state_carryover(
    previous_result: VNSettlementPeriodRunResult,
    loaded: LoadedScenario,
) -> VNStateCarryover | None:
    previous_insurers = {insurer.entity_id: insurer for insurer in previous_result.insurers}
    previous_policyholders = {
        policyholder.entity_id: policyholder
        for policyholder in previous_result.policyholders
    }
    carried_insurer_ids: list[int] = []
    carried_policyholder_ids: list[int] = []

    for insurer in loaded.insurers:
        previous = previous_insurers.get(insurer.entity_id)
        if previous is None:
            continue
        _carry_insurer_state(previous, insurer)
        carried_insurer_ids.append(insurer.entity_id)

    for policyholder in loaded.policyholders:
        previous = previous_policyholders.get(policyholder.entity_id)
        if previous is None:
            continue
        _carry_policyholder_state(previous, policyholder)
        carried_policyholder_ids.append(policyholder.entity_id)

    if not carried_insurer_ids and not carried_policyholder_ids:
        return None
    return VNStateCarryover(
        from_period=previous_result.period,
        to_period=loaded.context.period,
        insurer_ids=carried_insurer_ids,
        policyholder_ids=carried_policyholder_ids,
    )


def run_vn_settlement_multi_period_from_mappings(
    period_scenarios: list[dict],
    *,
    carry_forward_vn_state: bool = False,
) -> VNSettlementMultiPeriodRunResult:
    """Fuehrt mehrere explizite VN-Periodenszenarien deterministisch aus."""

    if not isinstance(period_scenarios, list):
        raise ValueError("VN settlement multi-period run requires a list of period scenarios")

    loaded_scenarios = [load_scenario_from_mapping(period_scenario) for period_scenario in period_scenarios]
    processed_periods = _validate_strictly_increasing_periods(
        [loaded.context.period for loaded in loaded_scenarios]
    )
    period_results: list[VNSettlementPeriodRunResult] = []
    carryovers: list[VNStateCarryover] = []
    for loaded in loaded_scenarios:
        if carry_forward_vn_state and period_results:
            carryover = _apply_vn_state_carryover(period_results[-1], loaded)
            if carryover is not None:
                carryovers.append(carryover)
        period_results.append(run_loaded_vn_settlement_period(loaded))

    return VNSettlementMultiPeriodRunResult(
        period_results=period_results,
        processed_periods=processed_periods,
        total_settlement_applications=sum(result.total_settlement_applications for result in period_results),
        total_damage_settlement_applications=sum(
            result.total_damage_settlement_applications for result in period_results
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
    raise ValueError("VN settlement multi-period fixture requires a list or object field: periods")


def _carry_forward_vn_state_from_fixture_payload(payload: object) -> bool:
    if not isinstance(payload, dict) or "carry_forward_vn_state" not in payload:
        return False
    value = payload["carry_forward_vn_state"]
    if not isinstance(value, bool):
        raise ValueError("VN settlement multi-period fixture field carry_forward_vn_state must be a boolean")
    return value


def run_vn_settlement_multi_period_from_fixture(
    path: str | Path,
    *,
    carry_forward_vn_state: bool = False,
) -> VNSettlementMultiPeriodRunResult:
    """Laedt ein Mehrperioden-Fixture und fuehrt den expliziten VN-Lauf aus."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return run_vn_settlement_multi_period_from_mappings(
        _period_scenarios_from_fixture_payload(payload),
        carry_forward_vn_state=carry_forward_vn_state or _carry_forward_vn_state_from_fixture_payload(payload),
    )
