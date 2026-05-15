from dataclasses import dataclass
import json
from pathlib import Path

from ims.io.scenario_loader import LoadedScenario, load_scenario_from_mapping
from ims.model.agrsich_export import ExportTable, build_agrsich_export_tables, compute_global_period
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.agrsich_writer import write_agrsich_export_tables
from ims.model.legacy_agrsich_reference import (
    LegacyWindowComparison,
    compare_export_file_to_legacy_window,
    parse_legacy_insurer_dat,
)
from ims.model.legacy_validation_report import (
    LegacyValidationReport,
    build_legacy_validation_report,
)


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
class ReplayPeriodResult:
    snapshot_index: int
    period: int
    global_period: int
    written_files: list[Path]


@dataclass(slots=True)
class ReplayRunResult:
    processed_periods: list[int]
    written_files: list[Path]
    period_results: list[ReplayPeriodResult]
    legacy_comparison: LegacyWindowComparison | None
    validation_report: LegacyValidationReport | None


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


def run_agrsich_replay_from_mapping(
    data: dict,
    output_dir: str | Path,
    *,
    fixture_base_path: str | Path = ".",
) -> ReplayRunResult:
    if not isinstance(data, dict):
        raise ValueError("replay fixture must be a JSON object")

    snapshots = _load_snapshots(data)
    target = _load_target(data, Path(fixture_base_path).resolve())

    output_path = Path(output_dir)
    all_written_files: list[Path] = []
    period_results: list[ReplayPeriodResult] = []
    for snapshot in snapshots:
        tables = _tables_for_snapshot(snapshot)
        written_files = write_agrsich_export_tables(output_path, tables, append=True)
        all_written_files.extend(written_files)
        period_results.append(
            ReplayPeriodResult(
                snapshot_index=snapshot.index,
                period=snapshot.scenario.context.period,
                global_period=snapshot.global_period,
                written_files=written_files,
            )
        )

    legacy_comparison = None
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

    return ReplayRunResult(
        processed_periods=[snapshot.global_period for snapshot in snapshots],
        written_files=_deduplicate_paths(all_written_files),
        period_results=period_results,
        legacy_comparison=legacy_comparison,
        validation_report=validation_report,
    )


def run_agrsich_replay_from_fixture(path: str | Path, output_dir: str | Path) -> ReplayRunResult:
    fixture_path = Path(path).resolve()
    with fixture_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    return run_agrsich_replay_from_mapping(
        data,
        output_dir,
        fixture_base_path=fixture_path.parent,
    )
