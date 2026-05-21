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
    damage_settlement_applications: list[VNDamageSettlementApplication] = field(default_factory=list)
    settlement_applications: list[VNSettlementApplication] = field(default_factory=list)

    @property
    def total_settlement_applications(self) -> int:
        return len(self.damage_settlement_applications) + len(self.settlement_applications)

    @property
    def total_damage_settlement_applications(self) -> int:
        return len(self.damage_settlement_applications)


@dataclass(slots=True)
class VNSettlementMultiPeriodRunResult:
    """Ergebnis eines kleinen deterministischen VN-Mehrperiodenlaufs."""

    period_results: list[VNSettlementPeriodRunResult]
    processed_periods: list[int]
    total_settlement_applications: int
    total_damage_settlement_applications: int


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


def run_vn_settlement_multi_period_from_mappings(
    period_scenarios: list[dict],
) -> VNSettlementMultiPeriodRunResult:
    """Fuehrt mehrere explizite VN-Periodenszenarien deterministisch aus."""

    if not isinstance(period_scenarios, list):
        raise ValueError("VN settlement multi-period run requires a list of period scenarios")

    loaded_scenarios = [load_scenario_from_mapping(period_scenario) for period_scenario in period_scenarios]
    processed_periods = _validate_strictly_increasing_periods(
        [loaded.context.period for loaded in loaded_scenarios]
    )
    period_results = [run_loaded_vn_settlement_period(loaded) for loaded in loaded_scenarios]
    return VNSettlementMultiPeriodRunResult(
        period_results=period_results,
        processed_periods=processed_periods,
        total_settlement_applications=sum(result.total_settlement_applications for result in period_results),
        total_damage_settlement_applications=sum(
            result.total_damage_settlement_applications for result in period_results
        ),
    )


def _period_scenarios_from_fixture_payload(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        period_scenarios = payload.get("periods")
        if isinstance(period_scenarios, list):
            return period_scenarios
    raise ValueError("VN settlement multi-period fixture requires a list or object field: periods")


def run_vn_settlement_multi_period_from_fixture(path: str | Path) -> VNSettlementMultiPeriodRunResult:
    """Laedt ein Mehrperioden-Fixture und fuehrt den expliziten VN-Lauf aus."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return run_vn_settlement_multi_period_from_mappings(_period_scenarios_from_fixture_payload(payload))
