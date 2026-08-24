from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ims.model.agrsich_export import ExportTable
from ims.model.legacy_agrsich_multi_period import (
    LegacyTableComparison,
    MultiPeriodLegacyComparison,
    build_multi_period_legacy_comparison,
    compare_insurer_export_table_to_legacy,
    compare_policyholder_export_table_to_legacy,
)
from ims.model.legacy_agrsich_reference import LegacyInsurerTable, parse_legacy_insurer_dat
from ims.model.legacy_validation_report import (
    LegacyValidationReport,
    build_legacy_validation_report_from_multi_period_comparison,
)
from ims.model.legacy_validation_run import (
    LegacyValidationTarget,
    load_legacy_validation_targets_from_fixture,
)
from ims.model.legacy_vn_reference import LegacyPolicyholderTable, parse_legacy_policyholder_dat


ExportIdentity = tuple[str, str, str, str, int | str | None]


@dataclass(slots=True)
class RequiredCalculatedExport:
    filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str | None
    periods: list[int]
    target_count: int
    legacy_paths: list[Path]

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "subject_type": self.subject_type,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "periods": list(self.periods),
            "period_count": len(self.periods),
            "target_count": self.target_count,
            "legacy_paths": [str(path) for path in self.legacy_paths],
        }


@dataclass(slots=True)
class CalculatedLegacyComparisonPlan:
    mode: str
    fixture_path: Path
    target_count: int
    target_period_count: int
    required_export_count: int
    required_exports: list[RequiredCalculatedExport]
    comparison_performed: bool = False
    writes_performed: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "fixture_path": str(self.fixture_path),
            "target_count": self.target_count,
            "target_period_count": self.target_period_count,
            "required_export_count": self.required_export_count,
            "required_exports": [item.to_dict() for item in self.required_exports],
            "comparison_performed": self.comparison_performed,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
        }


@dataclass(slots=True)
class CalculatedLegacyComparisonResult:
    mode: str
    fixture_path: Path
    calculation_origin: str
    target_count: int
    target_period_count: int
    required_export_count: int
    supplied_export_count: int
    matches: bool
    comparison: MultiPeriodLegacyComparison
    report: LegacyValidationReport
    comparison_performed: bool = True
    calculated_export_tables_supplied: bool = True
    calculation_origin_verified: bool = False
    legacy_fixture_rows_used_as_export: bool = False
    writes_performed: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "fixture_path": str(self.fixture_path),
            "calculation_origin": self.calculation_origin,
            "target_count": self.target_count,
            "target_period_count": self.target_period_count,
            "required_export_count": self.required_export_count,
            "supplied_export_count": self.supplied_export_count,
            "matches": self.matches,
            "comparison_performed": self.comparison_performed,
            "calculated_export_tables_supplied": self.calculated_export_tables_supplied,
            "calculation_origin_verified": self.calculation_origin_verified,
            "legacy_fixture_rows_used_as_export": self.legacy_fixture_rows_used_as_export,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
        }


def _target_identity(target: LegacyValidationTarget) -> ExportIdentity:
    return (
        target.export_filename,
        target.subject_type,
        target.level,
        target.selector_kind,
        target.selector_value,
    )


def _table_identity(table: ExportTable) -> ExportIdentity:
    return (
        table.spec.filename,
        table.spec.subject_type,
        table.spec.level,
        table.spec.selector_kind,
        table.spec.selector_value,
    )


def _identity_label(identity: ExportIdentity) -> str:
    filename, subject_type, level, selector_kind, selector_value = identity
    return f"{filename} ({subject_type}/{level}/{selector_kind}={selector_value})"


def _required_exports(targets: list[LegacyValidationTarget]) -> list[RequiredCalculatedExport]:
    grouped: dict[ExportIdentity, RequiredCalculatedExport] = {}
    period_owners: dict[ExportIdentity, set[int]] = {}
    for target in targets:
        identity = _target_identity(target)
        existing = grouped.get(identity)
        if existing is None:
            existing = RequiredCalculatedExport(
                filename=target.export_filename,
                subject_type=target.subject_type,
                level=target.level,
                selector_kind=target.selector_kind,
                selector_value=target.selector_value,
                periods=[],
                target_count=0,
                legacy_paths=[],
            )
            grouped[identity] = existing
            period_owners[identity] = set()

        overlap = period_owners[identity].intersection(target.periods)
        if overlap:
            raise ValueError(
                "calculated legacy comparison targets contain overlapping periods for "
                f"{_identity_label(identity)}: {sorted(overlap)}"
            )
        period_owners[identity].update(target.periods)
        existing.periods.extend(target.periods)
        existing.target_count += 1
        existing.legacy_paths.append(target.legacy_path.resolve())

    for item in grouped.values():
        item.periods.sort()
    return sorted(
        grouped.values(),
        key=lambda item: (
            item.filename,
            item.subject_type,
            item.level,
            item.selector_kind,
            str(item.selector_value),
        ),
    )


def build_calculated_legacy_comparison_plan(
    fixture_path: str | Path,
) -> CalculatedLegacyComparisonPlan:
    resolved_fixture_path = Path(fixture_path).resolve()
    targets = load_legacy_validation_targets_from_fixture(resolved_fixture_path)
    required_exports = _required_exports(targets)
    return CalculatedLegacyComparisonPlan(
        mode="calculated_legacy_comparison_plan",
        fixture_path=resolved_fixture_path,
        target_count=len(targets),
        target_period_count=sum(len(target.periods) for target in targets),
        required_export_count=len(required_exports),
        required_exports=required_exports,
    )


def _tables_by_identity(export_tables: list[ExportTable]) -> dict[ExportIdentity, ExportTable]:
    tables: dict[ExportIdentity, ExportTable] = {}
    for table in export_tables:
        identity = _table_identity(table)
        if identity in tables:
            raise ValueError(
                "calculated legacy comparison requires unique export tables: "
                f"{_identity_label(identity)}"
            )
        tables[identity] = table
    return tables


def _validate_table_periods(table: ExportTable, expected_periods: list[int]) -> None:
    periods: list[int] = []
    for row in table.rows:
        if not row.values:
            raise ValueError(
                "calculated legacy comparison export row requires a global period: "
                f"{table.spec.filename}"
            )
        periods.append(int(row.values[0]))
    if periods != expected_periods:
        raise ValueError(
            "calculated legacy comparison export periods must match the required "
            f"sorted boundary for {table.spec.filename}: expected {expected_periods[0]}-"
            f"{expected_periods[-1]} ({len(expected_periods)} rows), got {periods}"
        )


def _target_export_table(table: ExportTable, target: LegacyValidationTarget) -> ExportTable:
    target_periods = set(target.periods)
    return ExportTable(
        spec=table.spec,
        header=table.header,
        rows=[row for row in table.rows if int(row.values[0]) in target_periods],
    )


def _target_legacy_insurer_table(target: LegacyValidationTarget) -> LegacyInsurerTable:
    table = parse_legacy_insurer_dat(target.legacy_path)
    target_periods = set(target.periods)
    return LegacyInsurerTable(
        path=table.path,
        header=table.header,
        rows=[row for row in table.rows if row.global_period in target_periods],
    )


def _target_legacy_policyholder_table(target: LegacyValidationTarget) -> LegacyPolicyholderTable:
    table = parse_legacy_policyholder_dat(target.legacy_path)
    target_periods = set(target.periods)
    return LegacyPolicyholderTable(
        path=table.path,
        header=table.header,
        rows=[row for row in table.rows if row.global_period in target_periods],
    )


def _compare_target(
    target: LegacyValidationTarget,
    export_table: ExportTable,
    *,
    tolerance: float,
) -> LegacyTableComparison:
    target_export = _target_export_table(export_table, target)
    if target.subject_type == "insurer":
        return compare_insurer_export_table_to_legacy(
            target_export,
            _target_legacy_insurer_table(target),
            tolerance=tolerance,
            require_complete_legacy_periods=True,
        )
    return compare_policyholder_export_table_to_legacy(
        target_export,
        _target_legacy_policyholder_table(target),
        tolerance=tolerance,
        require_complete_legacy_periods=True,
    )


def compare_calculated_export_tables_to_legacy_fixture(
    fixture_path: str | Path,
    export_tables: list[ExportTable],
    *,
    calculation_origin: str,
    tolerance: float = 0.05,
) -> CalculatedLegacyComparisonResult:
    origin = calculation_origin.strip()
    if not origin:
        raise ValueError("calculated legacy comparison requires a calculation_origin")
    if not export_tables:
        raise ValueError("calculated legacy comparison requires calculated export tables")

    resolved_fixture_path = Path(fixture_path).resolve()
    targets = load_legacy_validation_targets_from_fixture(resolved_fixture_path)
    required_exports = _required_exports(targets)
    required_by_identity = {
        (
            item.filename,
            item.subject_type,
            item.level,
            item.selector_kind,
            item.selector_value,
        ): item
        for item in required_exports
    }
    tables_by_identity = _tables_by_identity(export_tables)

    missing = sorted(
        _identity_label(identity) for identity in required_by_identity.keys() - tables_by_identity.keys()
    )
    unexpected = sorted(
        _identity_label(identity) for identity in tables_by_identity.keys() - required_by_identity.keys()
    )
    if missing or unexpected:
        raise ValueError(
            "calculated legacy comparison export set does not match fixture requirements: "
            f"missing={missing}, unexpected={unexpected}"
        )

    for identity, required in required_by_identity.items():
        _validate_table_periods(tables_by_identity[identity], required.periods)

    table_comparisons = [
        _compare_target(target, tables_by_identity[_target_identity(target)], tolerance=tolerance)
        for target in targets
    ]
    comparison = build_multi_period_legacy_comparison(table_comparisons)
    report = build_legacy_validation_report_from_multi_period_comparison(comparison)
    return CalculatedLegacyComparisonResult(
        mode="calculated_export_tables_to_legacy_fixture",
        fixture_path=resolved_fixture_path,
        calculation_origin=origin,
        target_count=len(targets),
        target_period_count=sum(len(target.periods) for target in targets),
        required_export_count=len(required_exports),
        supplied_export_count=len(export_tables),
        matches=comparison.matches,
        comparison=comparison,
        report=report,
    )
