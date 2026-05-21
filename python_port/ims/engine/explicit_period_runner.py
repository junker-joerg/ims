from dataclasses import dataclass, field
import json
from pathlib import Path

from ims.engine.vn_rule_runner import (
    VNSettlementPeriodRunResult,
    VNStateCarryover,
    apply_vn_state_carryover,
    run_loaded_vn_settlement_period,
)
from ims.engine.vu_rule_runner import (
    VUForeignInfoCarryover,
    VUForeignInfoPeriodRunResult,
    apply_vu_foreign_info_carryover,
    run_loaded_vu_foreign_info_period,
)
from ims.io.scenario_loader import LoadedScenario, load_scenario_from_mapping
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
class ExplicitLegacyTarget:
    """Explizites Legacy-Ziel fuer einen geschriebenen VU/VN-Agrsich-Export."""

    legacy_path: Path
    export_filename: str
    subject_type: str
    tolerance: float = 0.05


@dataclass(slots=True)
class ExplicitPeriodRunResult:
    """Diagnose eines expliziten VU- plus VN-Periodenschritts."""

    period: int
    global_period: int
    vu_result: VUForeignInfoPeriodRunResult
    vn_result: VNSettlementPeriodRunResult
    export_tables: list[ExportTable] = field(default_factory=list)
    written_files: list[Path] = field(default_factory=list)


@dataclass(slots=True)
class ExplicitPeriodCarryover:
    """Diagnose optionaler Zustandstransfers vor einem expliziten Periodenschritt."""

    from_period: int
    to_period: int
    vu_carryover: VUForeignInfoCarryover | None = None
    vn_carryover: VNStateCarryover | None = None


@dataclass(slots=True)
class ExplicitMultiPeriodRunResult:
    """Ergebnis eines deterministischen expliziten VU/VN-Mehrperiodenlaufs."""

    processed_periods: list[int]
    period_results: list[ExplicitPeriodRunResult]
    written_files: list[Path]
    total_vu_rule_applications: int
    total_vn_settlement_applications: int
    total_vn_damage_settlement_applications: int
    carryovers: list[ExplicitPeriodCarryover] = field(default_factory=list)
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
        raise ValueError("explicit VU/VN multi-period run requires at least one period scenario")
    if len(set(processed_periods)) != len(processed_periods):
        raise ValueError("explicit VU/VN multi-period run rejects duplicate periods")
    if processed_periods != sorted(processed_periods):
        raise ValueError("explicit VU/VN multi-period run requires increasing periods")
    return processed_periods


def _load_legacy_targets(value: object, *, fixture_base_path: Path) -> list[ExplicitLegacyTarget]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("explicit VU/VN fixture legacy_targets must be a list")

    targets: list[ExplicitLegacyTarget] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("explicit VU/VN fixture legacy target must be an object")
        legacy_path = Path(str(item["legacy_path"]))
        if not legacy_path.is_absolute():
            legacy_path = fixture_base_path / legacy_path
        subject_type = str(item.get("subject_type", "policyholder"))
        if subject_type not in ("insurer", "policyholder"):
            raise ValueError(f"unsupported explicit VU/VN legacy target subject_type: {subject_type}")
        targets.append(
            ExplicitLegacyTarget(
                legacy_path=legacy_path,
                export_filename=str(item["export_filename"]),
                subject_type=subject_type,
                tolerance=float(item.get("tolerance", 0.05)),
            )
        )
    return targets


def _merge_tables_by_filename(period_results: list[ExplicitPeriodRunResult]) -> dict[str, ExportTable]:
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
    period_results: list[ExplicitPeriodRunResult],
    legacy_targets: list[ExplicitLegacyTarget],
) -> MultiPeriodLegacyComparison | None:
    if not legacy_targets:
        return None

    tables_by_filename = _merge_tables_by_filename(period_results)
    table_comparisons: list[LegacyTableComparison] = []
    for target in legacy_targets:
        export_table = tables_by_filename.get(target.export_filename)
        if export_table is None:
            raise ValueError(f"explicit VU/VN legacy target export was not written: {target.export_filename}")
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


def _vu_rule_application_count(result: VUForeignInfoPeriodRunResult) -> int:
    return (
        len(result.rule_applications)
        + len(result.random_uniform_applications)
        + len(result.random_normal_applications)
        + len(result.reserve_markup_applications)
        + len(result.net_switcher_markup_applications)
        + len(result.expected_claim_applications)
        + len(result.market_share_markup_applications)
        + len(result.free_linear_applications)
    )


def run_loaded_explicit_period(
    loaded: LoadedScenario,
    *,
    output_dir: str | Path | None = None,
) -> ExplicitPeriodRunResult:
    """
    Fuehrt in einem geladenen Szenario zuerst explizite VU-Regeln und danach VN-Settlement aus.

    Dieser Integrationspfad ist weiterhin kein historischer Scheduler. Alle VU-Regel-
    Snapshots, VN-Schaeden und VN-Entscheidungen muessen bereits explizit geladen sein.
    """

    vu_result = run_loaded_vu_foreign_info_period(loaded)
    vn_result = run_loaded_vn_settlement_period(loaded)
    agrsich_result = collect_extended_agrsich_records(
        loaded.context,
        loaded.bav,
        loaded.insurers,
        loaded.policyholders,
    )
    export_tables = build_agrsich_export_tables(loaded.context, agrsich_result)
    written_files = (
        write_agrsich_export_tables(Path(output_dir), export_tables, append=True)
        if output_dir is not None
        else []
    )
    return ExplicitPeriodRunResult(
        period=loaded.context.period,
        global_period=compute_global_period(loaded.context),
        vu_result=vu_result,
        vn_result=vn_result,
        export_tables=export_tables,
        written_files=written_files,
    )


def run_explicit_period_from_mapping(
    data: dict,
    *,
    output_dir: str | Path | None = None,
) -> ExplicitPeriodRunResult:
    """Laedt ein In-Memory-Szenario und fuehrt den expliziten VU/VN-Periodenschritt aus."""

    return run_loaded_explicit_period(load_scenario_from_mapping(data), output_dir=output_dir)


def _period_scenarios_from_fixture_payload(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        period_scenarios = payload.get("periods")
        if isinstance(period_scenarios, list):
            return period_scenarios
    raise ValueError("explicit VU/VN fixture requires a list or object field: periods")


def _boolean_fixture_flag(payload: object, key: str) -> bool:
    if not isinstance(payload, dict) or key not in payload:
        return False
    value = payload[key]
    if not isinstance(value, bool):
        raise ValueError(f"explicit VU/VN fixture field {key} must be a boolean")
    return value


def run_explicit_multi_period_from_mappings(
    period_scenarios: list[dict],
    *,
    output_dir: str | Path | None = None,
    carry_forward_vu_state: bool = False,
    carry_forward_vn_state: bool = False,
    legacy_targets: list[ExplicitLegacyTarget] | None = None,
    legacy_report_name: str | None = None,
) -> ExplicitMultiPeriodRunResult:
    """Fuehrt mehrere explizite VU/VN-Periodenszenarien deterministisch aus."""

    if not isinstance(period_scenarios, list):
        raise ValueError("explicit VU/VN multi-period run requires a list of period scenarios")

    loaded_scenarios = [load_scenario_from_mapping(period_scenario) for period_scenario in period_scenarios]
    processed_periods = _validate_strictly_increasing_periods(
        [compute_global_period(loaded.context) for loaded in loaded_scenarios]
    )
    output_path = Path(output_dir) if output_dir is not None else None

    period_results: list[ExplicitPeriodRunResult] = []
    carryovers: list[ExplicitPeriodCarryover] = []
    written_files: list[Path] = []
    for loaded in loaded_scenarios:
        if period_results and (carry_forward_vu_state or carry_forward_vn_state):
            previous = period_results[-1]
            vu_carryover = (
                apply_vu_foreign_info_carryover(previous.vu_result, loaded)
                if carry_forward_vu_state
                else None
            )
            vn_carryover = (
                apply_vn_state_carryover(previous.vn_result, loaded)
                if carry_forward_vn_state
                else None
            )
            if vu_carryover is not None or vn_carryover is not None:
                carryovers.append(
                    ExplicitPeriodCarryover(
                        from_period=previous.period,
                        to_period=loaded.context.period,
                        vu_carryover=vu_carryover,
                        vn_carryover=vn_carryover,
                    )
                )
        period_result = run_loaded_explicit_period(loaded, output_dir=output_path)
        written_files.extend(period_result.written_files)
        period_results.append(period_result)

    legacy_comparison = _compare_legacy_targets(period_results, legacy_targets or [])
    legacy_report = (
        build_legacy_validation_report_from_multi_period_comparison(legacy_comparison)
        if legacy_comparison is not None
        else None
    )
    written_legacy_report_files = (
        _write_legacy_report_files(legacy_report, output_path, legacy_report_name)
        if legacy_report is not None and legacy_report_name is not None and output_path is not None
        else []
    )

    return ExplicitMultiPeriodRunResult(
        processed_periods=processed_periods,
        period_results=period_results,
        written_files=_deduplicate_paths(written_files),
        total_vu_rule_applications=sum(_vu_rule_application_count(result.vu_result) for result in period_results),
        total_vn_settlement_applications=sum(
            result.vn_result.total_settlement_applications for result in period_results
        ),
        total_vn_damage_settlement_applications=sum(
            result.vn_result.total_damage_settlement_applications for result in period_results
        ),
        carryovers=carryovers,
        legacy_comparison=legacy_comparison,
        legacy_report=legacy_report,
        written_legacy_report_files=written_legacy_report_files,
    )


def run_explicit_multi_period_from_fixture(
    path: str | Path,
    *,
    output_dir: str | Path | None = None,
    carry_forward_vu_state: bool = False,
    carry_forward_vn_state: bool = False,
) -> ExplicitMultiPeriodRunResult:
    """Laedt ein explizites VU/VN-Mehrperioden-Fixture und fuehrt es aus."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    fixture_carry_forward_vu_state = _boolean_fixture_flag(payload, "carry_forward_vu_state")
    fixture_carry_forward_vn_state = _boolean_fixture_flag(payload, "carry_forward_vn_state")
    legacy_targets = (
        _load_legacy_targets(payload.get("legacy_targets"), fixture_base_path=fixture_path.parent)
        if isinstance(payload, dict)
        else []
    )
    return run_explicit_multi_period_from_mappings(
        _period_scenarios_from_fixture_payload(payload),
        output_dir=output_dir,
        carry_forward_vu_state=carry_forward_vu_state or fixture_carry_forward_vu_state,
        carry_forward_vn_state=carry_forward_vn_state or fixture_carry_forward_vn_state,
        legacy_targets=legacy_targets,
        legacy_report_name=(
            str(payload["legacy_report_name"])
            if isinstance(payload, dict) and payload.get("legacy_report_name") is not None
            else None
        ),
    )
