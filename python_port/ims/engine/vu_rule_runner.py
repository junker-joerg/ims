from dataclasses import dataclass
import json
from pathlib import Path

from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
from ims.io.scenario_loader import LoadedScenario, load_scenario, load_scenario_from_mapping
from ims.model.bav_service import BAVForeignInfoResult, compute_extended_foreign_info
from ims.model.entities import BAV, Insurer, Policyholder
from ims.model.vu_rules import VUForeignInfoRuleApplication, apply_vu_foreign_info_rule_snapshots


@dataclass(slots=True)
class VUForeignInfoPeriodRunResult:
    """Ergebnis eines kleinen deterministischen VU-Frmdinf-Periodenschritts."""

    context_period: int
    context_logtime: int
    bav: BAV
    insurers: list[Insurer]
    policyholders: list[Policyholder]
    foreign_info: BAVForeignInfoResult
    rule_applications: list[VUForeignInfoRuleApplication]
    aggregate_snapshot: AggregateSnapshot


@dataclass(slots=True)
class VUForeignInfoMultiPeriodRunResult:
    """Ergebnis eines kleinen deterministischen Mehrperiodenlaufs."""

    period_results: list[VUForeignInfoPeriodRunResult]
    processed_periods: list[int]
    total_rule_applications: int


def run_loaded_vu_foreign_info_period(loaded: LoadedScenario) -> VUForeignInfoPeriodRunResult:
    """
    Fuehrt einen kleinen fachlichen Periodenschritt fuer explizite VU-Frmdinf-Snapshots aus.

    Dieser Pfad berechnet zuerst die bereits portierten BAV-Fremdinformationen aus
    Vorperiodenwerten und wendet danach nur explizit geladene VU-Regelparameter-
    Snapshots an. Er ist kein Scheduler und keine vollstaendige historische Simulation.
    """

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
    aggregate_snapshot = collect_basic_aggregates(
        context=loaded.context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
    )
    return VUForeignInfoPeriodRunResult(
        context_period=loaded.context.period,
        context_logtime=loaded.context.logtime,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        foreign_info=foreign_info,
        rule_applications=rule_applications,
        aggregate_snapshot=aggregate_snapshot,
    )


def run_vu_foreign_info_period_from_mapping(data: dict) -> VUForeignInfoPeriodRunResult:
    """Laedt ein In-Memory-Szenario und fuehrt den kleinen VU-Frmdinf-Periodenschritt aus."""

    return run_loaded_vu_foreign_info_period(load_scenario_from_mapping(data))


def run_vu_foreign_info_period_from_fixture(path: str | Path) -> VUForeignInfoPeriodRunResult:
    """Laedt ein Szenariofile und fuehrt den kleinen VU-Frmdinf-Periodenschritt aus."""

    return run_loaded_vu_foreign_info_period(load_scenario(path))


def _validate_strictly_increasing_periods(period_results: list[VUForeignInfoPeriodRunResult]) -> list[int]:
    processed_periods = [result.context_period for result in period_results]
    if not processed_periods:
        raise ValueError("VU foreign-info multi-period run requires at least one period scenario")
    if len(set(processed_periods)) != len(processed_periods):
        raise ValueError("VU foreign-info multi-period run rejects duplicate periods")
    if processed_periods != sorted(processed_periods):
        raise ValueError("VU foreign-info multi-period run requires increasing periods")
    return processed_periods


def run_vu_foreign_info_multi_period_from_mappings(
    period_scenarios: list[dict],
) -> VUForeignInfoMultiPeriodRunResult:
    """Fuehrt mehrere explizite VU-Frmdinf-Periodenszenarien deterministisch aus."""

    if not isinstance(period_scenarios, list):
        raise ValueError("VU foreign-info multi-period run requires a list of period scenarios")
    period_results = [
        run_vu_foreign_info_period_from_mapping(period_scenario)
        for period_scenario in period_scenarios
    ]
    processed_periods = _validate_strictly_increasing_periods(period_results)
    return VUForeignInfoMultiPeriodRunResult(
        period_results=period_results,
        processed_periods=processed_periods,
        total_rule_applications=sum(len(result.rule_applications) for result in period_results),
    )


def _period_scenarios_from_fixture_payload(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        period_scenarios = payload.get("periods")
        if isinstance(period_scenarios, list):
            return period_scenarios
    raise ValueError("VU foreign-info multi-period fixture requires a list or object field: periods")


def run_vu_foreign_info_multi_period_from_fixture(path: str | Path) -> VUForeignInfoMultiPeriodRunResult:
    """Laedt ein Mehrperioden-Fixture und fuehrt den kleinen VU-Frmdinf-Lauf aus."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return run_vu_foreign_info_multi_period_from_mappings(
        _period_scenarios_from_fixture_payload(payload)
    )
