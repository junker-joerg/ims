from dataclasses import dataclass
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
