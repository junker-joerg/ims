from dataclasses import dataclass
import json
from pathlib import Path

from ims.io.scenario_loader import LoadedScenario, load_scenario_from_mapping
from ims.engine.vu_rule_runner import (
    VUForeignInfoCarryover,
    VUForeignInfoPeriodRunResult,
    apply_vu_foreign_info_carryover,
    run_loaded_vu_foreign_info_period,
)
from ims.model.agrsich_export import ExportTable, build_agrsich_export_tables, compute_global_period
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.agrsich_writer import write_agrsich_export_tables
from ims.model.legacy_agrsich_reference import (
    LegacyWindowComparison,
    compare_export_file_to_legacy_window,
    parse_legacy_insurer_dat,
)
from ims.model.legacy_agrsich_multi_period import (
    LegacyTableComparison,
    MultiPeriodLegacyComparison,
    build_multi_period_legacy_comparison,
    compare_insurer_export_table_to_legacy,
    compare_policyholder_export_table_to_legacy,
)
from ims.model.legacy_validation_report import (
    LegacyValidationReport,
    build_legacy_validation_report,
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
class ReplaySnapshot:
    index: int
    data: dict
    scenario: LoadedScenario
    global_period: int


@dataclass(slots=True)
class ReplayWindowTarget:
    legacy_path: Path
    export_filename: str
    start_period: int
    end_period: int


@dataclass(slots=True)
class ReplayLegacyTarget:
    legacy_path: Path
    export_filename: str
    subject_type: str
    tolerance: float = 0.05


@dataclass(slots=True)
class ReplayPeriodResult:
    snapshot_index: int
    period: int
    global_period: int
    export_tables: list[ExportTable]
    written_files: list[Path]


@dataclass(slots=True)
class ReplayRunResult:
    processed_periods: list[int]
    processed_local_periods: list[int]
    processed_global_periods: list[int]
    written_files: list[Path]
    period_results: list[ReplayPeriodResult]
    vu_period_results: list[VUForeignInfoPeriodRunResult]
    carryovers: list[VUForeignInfoCarryover]
    legacy_comparison: LegacyWindowComparison | None
    legacy_target_comparison: MultiPeriodLegacyComparison | None
    validation_report: LegacyValidationReport | None
    written_legacy_report_files: list[Path]


def _load_target(data: dict, fixture_base_path: Path) -> ReplayWindowTarget | None:
    target_data = data.get("legacy_window")
    if target_data is None:
        return None
    if not isinstance(target_data, dict):
        raise ValueError("legacy_window must be an object")

    legacy_path = Path(str(target_data["legacy_path"]))
    if not legacy_path.is_absolute():
        legacy_path = fixture_base_path / legacy_path
    return ReplayWindowTarget(
        legacy_path=legacy_path,
        export_filename=str(target_data["export_filename"]),
        start_period=int(target_data["start_period"]),
        end_period=int(target_data["end_period"]),
    )


def _load_legacy_targets(value: object, *, fixture_base_path: Path) -> list[ReplayLegacyTarget]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("replay fixture legacy_targets must be a list")

    targets: list[ReplayLegacyTarget] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("replay fixture legacy target must be an object")
        legacy_path = Path(str(item["legacy_path"]))
        if not legacy_path.is_absolute():
            legacy_path = fixture_base_path / legacy_path
        subject_type = str(item.get("subject_type", "insurer"))
        if subject_type not in ("insurer", "policyholder"):
            raise ValueError(f"unsupported replay legacy target subject_type: {subject_type}")
        targets.append(
            ReplayLegacyTarget(
                legacy_path=legacy_path,
                export_filename=str(item["export_filename"]),
                subject_type=subject_type,
                tolerance=float(item.get("tolerance", 0.05)),
            )
        )
    return targets


def _load_snapshots(data: dict) -> list[ReplaySnapshot]:
    snapshot_items = data.get("snapshots")
    if not isinstance(snapshot_items, list) or not snapshot_items:
        raise ValueError("replay fixture must contain a non-empty snapshots list")

    snapshots: list[ReplaySnapshot] = []
    for index, snapshot_data in enumerate(snapshot_items):
        if not isinstance(snapshot_data, dict):
            raise ValueError("each replay snapshot must be an object")
        scenario = load_scenario_from_mapping(snapshot_data)
        snapshots.append(
            ReplaySnapshot(
                index=index,
                data=snapshot_data,
                scenario=scenario,
                global_period=compute_global_period(scenario.context),
            )
        )
    return snapshots


def _tables_for_snapshot(snapshot: ReplaySnapshot) -> list[ExportTable]:
    scenario = snapshot.scenario
    agrsich_result = collect_extended_agrsich_records(
        scenario.context,
        scenario.bav,
        scenario.insurers,
        scenario.policyholders,
    )
    return build_agrsich_export_tables(scenario.context, agrsich_result)


def _carry_forward_insurer_state_from_fixture_payload(payload: dict) -> bool:
    value = payload.get("carry_forward_insurer_state", False)
    if not isinstance(value, bool):
        raise ValueError("replay fixture field carry_forward_insurer_state must be a boolean")
    return value


def _validate_carryover_replay_period_order(snapshots: list[ReplaySnapshot]) -> None:
    periods = [snapshot.global_period for snapshot in snapshots]
    if len(set(periods)) != len(periods):
        raise ValueError("Agrsich replay carryover rejects duplicate replay periods")
    if periods != sorted(periods):
        raise ValueError("Agrsich replay carryover requires increasing replay periods")


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


def _merge_tables_by_filename(period_results: list[ReplayPeriodResult]) -> dict[str, ExportTable]:
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
    period_results: list[ReplayPeriodResult],
    legacy_targets: list[ReplayLegacyTarget],
) -> MultiPeriodLegacyComparison | None:
    if not legacy_targets:
        return None

    tables_by_filename = _merge_tables_by_filename(period_results)
    table_comparisons: list[LegacyTableComparison] = []
    for target in legacy_targets:
        export_table = tables_by_filename.get(target.export_filename)
        if export_table is None:
            raise ValueError(f"replay legacy target export was not written: {target.export_filename}")
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


def run_agrsich_replay_from_mapping(
    data: dict,
    output_dir: str | Path,
    *,
    fixture_base_path: str | Path = ".",
    carry_forward_insurer_state: bool = False,
    legacy_targets: list[ReplayLegacyTarget] | None = None,
    legacy_report_name: str | None = None,
) -> ReplayRunResult:
    if not isinstance(data, dict):
        raise ValueError("replay fixture must be a JSON object")

    snapshots = _load_snapshots(data)
    base_path = Path(fixture_base_path).resolve()
    target = _load_target(data, base_path)
    fixture_legacy_targets = _load_legacy_targets(data.get("legacy_targets"), fixture_base_path=base_path)
    fixture_carry_forward_insurer_state = _carry_forward_insurer_state_from_fixture_payload(data)
    should_carry_forward_insurer_state = carry_forward_insurer_state or fixture_carry_forward_insurer_state
    if should_carry_forward_insurer_state:
        _validate_carryover_replay_period_order(snapshots)

    output_path = Path(output_dir)
    all_written_files: list[Path] = []
    period_results: list[ReplayPeriodResult] = []
    vu_period_results: list[VUForeignInfoPeriodRunResult] = []
    carryovers: list[VUForeignInfoCarryover] = []
    for snapshot in snapshots:
        if should_carry_forward_insurer_state and vu_period_results:
            carryover = apply_vu_foreign_info_carryover(vu_period_results[-1], snapshot.scenario)
            if carryover is not None:
                carryovers.append(carryover)
        vu_period_result = run_loaded_vu_foreign_info_period(snapshot.scenario)
        vu_period_results.append(vu_period_result)
        tables = _tables_for_snapshot(snapshot)
        written_files = write_agrsich_export_tables(output_path, tables, append=True)
        all_written_files.extend(written_files)
        period_results.append(
            ReplayPeriodResult(
                snapshot_index=snapshot.index,
                period=snapshot.scenario.context.period,
                global_period=snapshot.global_period,
                export_tables=tables,
                written_files=written_files,
            )
        )

    legacy_comparison = None
    legacy_target_comparison = _compare_legacy_targets(
        period_results,
        list(legacy_targets or []) + fixture_legacy_targets,
    )
    validation_report = None
    if target is not None:
        legacy_table = parse_legacy_insurer_dat(target.legacy_path)
        legacy_comparison = compare_export_file_to_legacy_window(
            output_path / target.export_filename,
            legacy_table,
            target.start_period,
            target.end_period,
        )
        validation_report = build_legacy_validation_report([legacy_comparison])
    if legacy_target_comparison is not None:
        validation_report = build_legacy_validation_report_from_multi_period_comparison(legacy_target_comparison)
    written_legacy_report_files = (
        _write_legacy_report_files(validation_report, output_path, legacy_report_name)
        if validation_report is not None and legacy_report_name is not None
        else []
    )

    return ReplayRunResult(
        processed_periods=[snapshot.global_period for snapshot in snapshots],
        processed_local_periods=[snapshot.scenario.context.period for snapshot in snapshots],
        processed_global_periods=[snapshot.global_period for snapshot in snapshots],
        written_files=_deduplicate_paths(all_written_files),
        period_results=period_results,
        vu_period_results=vu_period_results,
        carryovers=carryovers,
        legacy_comparison=legacy_comparison,
        legacy_target_comparison=legacy_target_comparison,
        validation_report=validation_report,
        written_legacy_report_files=written_legacy_report_files,
    )


def run_agrsich_replay_from_fixture(
    path: str | Path,
    output_dir: str | Path,
    *,
    carry_forward_insurer_state: bool = False,
) -> ReplayRunResult:
    fixture_path = Path(path).resolve()
    with fixture_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    return run_agrsich_replay_from_mapping(
        data,
        output_dir,
        fixture_base_path=fixture_path.parent,
        carry_forward_insurer_state=carry_forward_insurer_state,
        legacy_report_name=(
            str(data["legacy_report_name"])
            if isinstance(data, dict) and data.get("legacy_report_name") is not None
            else None
        ),
    )
