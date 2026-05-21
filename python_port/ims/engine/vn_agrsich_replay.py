from dataclasses import dataclass
import json
from pathlib import Path

from ims.engine.vn_rule_runner import VNSettlementPeriodRunResult, run_loaded_vn_settlement_period
from ims.io.scenario_loader import load_scenario_from_mapping
from ims.model.agrsich_export import ExportTable, build_agrsich_export_tables, compute_global_period
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.agrsich_writer import write_agrsich_export_tables


@dataclass(slots=True)
class VNAgrsichReplayPeriodResult:
    """Diagnose eines expliziten VN-Periodenlaufs mit anschliessendem Agrsich-Export."""

    period: int
    global_period: int
    settlement_result: VNSettlementPeriodRunResult
    export_tables: list[ExportTable]
    written_files: list[Path]


@dataclass(slots=True)
class VNAgrsichReplayRunResult:
    """Ergebnis eines deterministischen VN-Agrsich-Replay-Laufs."""

    processed_periods: list[int]
    period_results: list[VNAgrsichReplayPeriodResult]
    written_files: list[Path]
    total_settlement_applications: int
    total_damage_settlement_applications: int


def _deduplicate_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append(path)
    return result


def _validate_strictly_increasing_periods(processed_periods: list[int]) -> list[int]:
    if not processed_periods:
        raise ValueError("VN Agrsich replay requires at least one period scenario")
    if len(set(processed_periods)) != len(processed_periods):
        raise ValueError("VN Agrsich replay rejects duplicate periods")
    if processed_periods != sorted(processed_periods):
        raise ValueError("VN Agrsich replay requires increasing periods")
    return processed_periods


def run_vn_agrsich_replay_from_mappings(
    period_scenarios: list[dict],
    output_dir: str | Path,
) -> VNAgrsichReplayRunResult:
    """
    Fuehrt explizite VN-Periodenszenarien aus und schreibt danach Agrsich-Exports.

    Dies ist kein historischer PlanVN-Scheduler. Alle Schadenziehungen,
    Versicherungsentscheidungen und Settlement-Snapshots muessen bereits im
    jeweiligen Periodenszenario explizit vorliegen.
    """

    if not isinstance(period_scenarios, list):
        raise ValueError("VN Agrsich replay requires a list of period scenarios")

    loaded_scenarios = [load_scenario_from_mapping(period_scenario) for period_scenario in period_scenarios]
    processed_periods = _validate_strictly_increasing_periods(
        [compute_global_period(loaded.context) for loaded in loaded_scenarios]
    )

    output_path = Path(output_dir)
    period_results: list[VNAgrsichReplayPeriodResult] = []
    all_written_files: list[Path] = []
    for loaded in loaded_scenarios:
        settlement_result = run_loaded_vn_settlement_period(loaded)
        agrsich_result = collect_extended_agrsich_records(
            loaded.context,
            loaded.bav,
            loaded.insurers,
            loaded.policyholders,
        )
        export_tables = build_agrsich_export_tables(loaded.context, agrsich_result)
        written_files = write_agrsich_export_tables(output_path, export_tables, append=True)
        all_written_files.extend(written_files)
        period_results.append(
            VNAgrsichReplayPeriodResult(
                period=loaded.context.period,
                global_period=compute_global_period(loaded.context),
                settlement_result=settlement_result,
                export_tables=export_tables,
                written_files=written_files,
            )
        )

    return VNAgrsichReplayRunResult(
        processed_periods=processed_periods,
        period_results=period_results,
        written_files=_deduplicate_paths(all_written_files),
        total_settlement_applications=sum(
            result.settlement_result.total_settlement_applications for result in period_results
        ),
        total_damage_settlement_applications=sum(
            result.settlement_result.total_damage_settlement_applications for result in period_results
        ),
    )


def _period_scenarios_from_fixture_payload(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        period_scenarios = payload.get("periods")
        if isinstance(period_scenarios, list):
            return period_scenarios
    raise ValueError("VN Agrsich replay fixture requires a list or object field: periods")


def run_vn_agrsich_replay_from_fixture(
    path: str | Path,
    output_dir: str | Path,
) -> VNAgrsichReplayRunResult:
    """Laedt ein Mehrperioden-Fixture und schreibt Agrsich-Exports nach VN-Regelanwendung."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return run_vn_agrsich_replay_from_mappings(_period_scenarios_from_fixture_payload(payload), output_dir)
