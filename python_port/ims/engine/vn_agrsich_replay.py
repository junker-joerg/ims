from dataclasses import dataclass, field
import json
from pathlib import Path

from ims.engine.vn_rule_runner import (
    VNSettlementPeriodRunResult,
    VNStateCarryover,
    apply_vn_state_carryover,
    run_loaded_vn_settlement_period,
)
from ims.io.scenario_loader import load_scenario_from_mapping
from ims.model.agrsich_export import ExportTable, build_agrsich_export_tables, compute_global_period
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.agrsich_writer import write_agrsich_export_tables
from ims.model.legacy_agrsich_multi_period import (
    LegacyTableComparison,
    MultiPeriodLegacyComparison,
    build_multi_period_legacy_comparison,
    compare_insurer_export_table_to_legacy,
    compare_policyholder_export_table_to_legacy,
)
from ims.model.legacy_agrsich_reference import parse_legacy_insurer_dat
from ims.model.legacy_validation_report import (
    LegacyValidationReport,
    build_legacy_validation_report_from_multi_period_comparison,
    write_legacy_validation_deviation_index_csv,
    write_legacy_validation_field_summary_csv,
    write_legacy_validation_group_summary_csv,
    write_legacy_validation_period_summary_csv,
    write_legacy_validation_report_csv,
    write_legacy_validation_report_json,
)
from ims.model.legacy_vn_reference import parse_legacy_policyholder_dat


@dataclass(slots=True)
class VNAgrsichLegacyTarget:
    """Explizites Legacy-Ziel fuer einen geschriebenen VN-Agrsich-Replay-Export."""

    legacy_path: Path
    export_filename: str
    subject_type: str
    tolerance: float = 0.05


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
    processed_local_periods: list[int]
    processed_global_periods: list[int]
    period_results: list[VNAgrsichReplayPeriodResult]
    written_files: list[Path]
    total_settlement_applications: int
    total_damage_settlement_applications: int
    carryovers: list[VNStateCarryover] = field(default_factory=list)
    legacy_comparison: MultiPeriodLegacyComparison | None = None
    legacy_report: LegacyValidationReport | None = None
    written_legacy_report_files: list[Path] = field(default_factory=list)


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


def _load_legacy_targets(value: object, *, fixture_base_path: Path) -> list[VNAgrsichLegacyTarget]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("VN Agrsich replay legacy_targets must be a list")

    targets: list[VNAgrsichLegacyTarget] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("VN Agrsich replay legacy target must be an object")
        legacy_path = Path(str(item["legacy_path"]))
        if not legacy_path.is_absolute():
            legacy_path = fixture_base_path / legacy_path
        subject_type = str(item.get("subject_type", "policyholder"))
        if subject_type not in ("insurer", "policyholder"):
            raise ValueError(f"unsupported VN Agrsich replay legacy target subject_type: {subject_type}")
        targets.append(
            VNAgrsichLegacyTarget(
                legacy_path=legacy_path,
                export_filename=str(item["export_filename"]),
                subject_type=subject_type,
                tolerance=float(item.get("tolerance", 0.05)),
            )
        )
    return targets


def _merge_tables_by_filename(period_results: list[VNAgrsichReplayPeriodResult]) -> dict[str, ExportTable]:
    tables_by_filename: dict[str, ExportTable] = {}
    for period_result in period_results:
        for table in period_result.export_tables:
            existing = tables_by_filename.get(table.spec.filename)
            if existing is None:
                tables_by_filename[table.spec.filename] = ExportTable(
                    spec=table.spec,
                    header=table.header,
                    rows=list(table.rows),
                )
            else:
                existing.rows.extend(table.rows)
    return tables_by_filename


def _compare_legacy_targets(
    period_results: list[VNAgrsichReplayPeriodResult],
    legacy_targets: list[VNAgrsichLegacyTarget],
) -> MultiPeriodLegacyComparison | None:
    if not legacy_targets:
        return None

    tables_by_filename = _merge_tables_by_filename(period_results)
    table_comparisons: list[LegacyTableComparison] = []
    for target in legacy_targets:
        export_table = tables_by_filename.get(target.export_filename)
        if export_table is None:
            raise ValueError(f"VN Agrsich replay legacy target export was not written: {target.export_filename}")
        if target.subject_type == "insurer":
            table_comparisons.append(
                compare_insurer_export_table_to_legacy(
                    export_table,
                    parse_legacy_insurer_dat(target.legacy_path),
                    tolerance=target.tolerance,
                    require_complete_legacy_periods=True,
                )
            )
        else:
            table_comparisons.append(
                compare_policyholder_export_table_to_legacy(
                    export_table,
                    parse_legacy_policyholder_dat(target.legacy_path),
                    tolerance=target.tolerance,
                    require_complete_legacy_periods=True,
                )
            )
    return build_multi_period_legacy_comparison(table_comparisons)


def _write_legacy_report_files(
    report: LegacyValidationReport,
    output_dir: Path,
    report_name: str,
) -> list[Path]:
    return [
        write_legacy_validation_report_json(report, output_dir / f"{report_name}.json"),
        write_legacy_validation_report_csv(report, output_dir / f"{report_name}.csv"),
        write_legacy_validation_field_summary_csv(report, output_dir / f"{report_name}_fields.csv"),
        write_legacy_validation_group_summary_csv(report, output_dir / f"{report_name}_groups.csv"),
        write_legacy_validation_period_summary_csv(report, output_dir / f"{report_name}_periods.csv"),
        write_legacy_validation_deviation_index_csv(report, output_dir / f"{report_name}_deviations.csv"),
    ]


def _carry_forward_vn_state_from_fixture_payload(payload: object) -> bool:
    if not isinstance(payload, dict) or "carry_forward_vn_state" not in payload:
        return False
    value = payload["carry_forward_vn_state"]
    if not isinstance(value, bool):
        raise ValueError("VN Agrsich replay fixture field carry_forward_vn_state must be a boolean")
    return value


def run_vn_agrsich_replay_from_mappings(
    period_scenarios: list[dict],
    output_dir: str | Path,
    *,
    legacy_targets: list[VNAgrsichLegacyTarget] | None = None,
    legacy_report_name: str | None = None,
    carry_forward_vn_state: bool = False,
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
    processed_global_periods = _validate_strictly_increasing_periods(
        [compute_global_period(loaded.context) for loaded in loaded_scenarios]
    )

    output_path = Path(output_dir)
    period_results: list[VNAgrsichReplayPeriodResult] = []
    carryovers: list[VNStateCarryover] = []
    all_written_files: list[Path] = []
    for loaded in loaded_scenarios:
        if carry_forward_vn_state and period_results:
            carryover = apply_vn_state_carryover(period_results[-1].settlement_result, loaded)
            if carryover is not None:
                carryovers.append(carryover)
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

    legacy_comparison = _compare_legacy_targets(period_results, legacy_targets or [])
    legacy_report = (
        build_legacy_validation_report_from_multi_period_comparison(legacy_comparison)
        if legacy_comparison is not None
        else None
    )
    written_legacy_report_files = (
        _write_legacy_report_files(legacy_report, output_path, legacy_report_name)
        if legacy_report is not None and legacy_report_name is not None
        else []
    )

    return VNAgrsichReplayRunResult(
        processed_periods=processed_global_periods,
        processed_local_periods=[loaded.context.period for loaded in loaded_scenarios],
        processed_global_periods=processed_global_periods,
        period_results=period_results,
        written_files=_deduplicate_paths(all_written_files),
        total_settlement_applications=sum(
            result.settlement_result.total_settlement_applications for result in period_results
        ),
        total_damage_settlement_applications=sum(
            result.settlement_result.total_damage_settlement_applications for result in period_results
        ),
        carryovers=carryovers,
        legacy_comparison=legacy_comparison,
        legacy_report=legacy_report,
        written_legacy_report_files=written_legacy_report_files,
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

    fixture_path = Path(path).resolve()
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    legacy_targets = (
        _load_legacy_targets(payload.get("legacy_targets"), fixture_base_path=fixture_path.parent)
        if isinstance(payload, dict)
        else []
    )
    fixture_carry_forward_vn_state = _carry_forward_vn_state_from_fixture_payload(payload)
    return run_vn_agrsich_replay_from_mappings(
        _period_scenarios_from_fixture_payload(payload),
        output_dir,
        legacy_targets=legacy_targets,
        carry_forward_vn_state=fixture_carry_forward_vn_state,
        legacy_report_name=(
            str(payload["legacy_report_name"])
            if isinstance(payload, dict) and payload.get("legacy_report_name") is not None
            else None
        ),
    )
