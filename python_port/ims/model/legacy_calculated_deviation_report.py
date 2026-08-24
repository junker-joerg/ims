from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ims.model.agrsich_export import ExportTable
from ims.model.legacy_calculated_comparison import (
    CalculatedLegacyComparisonPlan,
    CalculatedLegacyComparisonResult,
    RequiredCalculatedExport,
    build_calculated_legacy_comparison_plan,
    compare_calculated_export_tables_to_legacy_fixture,
)


ExportIdentity = tuple[str, str, str, str, int | str | None]


@dataclass(slots=True)
class CalculatedDeviationInputIssue:
    code: str
    message: str
    export_identity: str | None = None
    periods: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "export_identity": self.export_identity,
            "periods": list(self.periods),
        }


@dataclass(slots=True)
class CalculatedFieldDifference:
    classification: str
    filename: str
    global_period: int | None
    field_name: str
    actual: str | float | int
    expected: str | float | int
    abs_delta: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification,
            "filename": self.filename,
            "global_period": self.global_period,
            "field_name": self.field_name,
            "actual": self.actual,
            "expected": self.expected,
            "abs_delta": self.abs_delta,
        }


@dataclass(slots=True)
class CalculatedLegacyDeviationReport:
    mode: str
    status: str
    fixture_path: Path
    calculation_origin: str
    target_count: int
    target_period_count: int
    required_export_count: int
    supplied_export_count: int
    input_issues: list[CalculatedDeviationInputIssue]
    comparison_result: CalculatedLegacyComparisonResult | None = None
    exact_field_match_count: int = 0
    tolerated_numeric_differences: list[CalculatedFieldDifference] = field(default_factory=list)
    blocking_numeric_differences: list[CalculatedFieldDifference] = field(default_factory=list)
    open_field_questions: list[CalculatedFieldDifference] = field(default_factory=list)
    comparison_performed: bool = False
    writes_performed: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False
    historical_equivalence_claimed: bool = False

    @property
    def matches(self) -> bool | None:
        if self.comparison_result is None:
            return None
        return self.comparison_result.matches

    @property
    def compared_row_count(self) -> int:
        if self.comparison_result is None:
            return 0
        return self.comparison_result.report.total_rows

    @property
    def matched_row_count(self) -> int:
        if self.comparison_result is None:
            return 0
        return self.comparison_result.report.matched_rows

    @property
    def mismatched_row_count(self) -> int:
        if self.comparison_result is None:
            return 0
        return self.comparison_result.report.mismatched_rows

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "status": self.status,
            "fixture_path": str(self.fixture_path),
            "calculation_origin": self.calculation_origin,
            "target_count": self.target_count,
            "target_period_count": self.target_period_count,
            "required_export_count": self.required_export_count,
            "supplied_export_count": self.supplied_export_count,
            "input_issue_count": len(self.input_issues),
            "input_issues": [issue.to_dict() for issue in self.input_issues],
            "matches": self.matches,
            "compared_row_count": self.compared_row_count,
            "matched_row_count": self.matched_row_count,
            "mismatched_row_count": self.mismatched_row_count,
            "exact_field_match_count": self.exact_field_match_count,
            "tolerated_numeric_difference_count": len(self.tolerated_numeric_differences),
            "blocking_numeric_difference_count": len(self.blocking_numeric_differences),
            "open_field_question_count": len(self.open_field_questions),
            "tolerated_numeric_differences": [
                difference.to_dict() for difference in self.tolerated_numeric_differences
            ],
            "blocking_numeric_differences": [
                difference.to_dict() for difference in self.blocking_numeric_differences
            ],
            "open_field_questions": [
                difference.to_dict() for difference in self.open_field_questions
            ],
            "comparison_performed": self.comparison_performed,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "historical_equivalence_claimed": self.historical_equivalence_claimed,
        }


def _required_identity(required: RequiredCalculatedExport) -> ExportIdentity:
    return (
        required.filename,
        required.subject_type,
        required.level,
        required.selector_kind,
        required.selector_value,
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


def _audit_table_periods(
    table: ExportTable,
    required: RequiredCalculatedExport,
) -> list[CalculatedDeviationInputIssue]:
    identity = _table_identity(table)
    label = _identity_label(identity)
    issues: list[CalculatedDeviationInputIssue] = []
    periods: list[int] = []
    for row in table.rows:
        if not row.values:
            issues.append(
                CalculatedDeviationInputIssue(
                    code="global_period_missing",
                    message=f"calculated export row has no global period: {label}",
                    export_identity=label,
                )
            )
            continue
        try:
            periods.append(int(row.values[0]))
        except (TypeError, ValueError):
            issues.append(
                CalculatedDeviationInputIssue(
                    code="global_period_invalid",
                    message=f"calculated export row has an invalid global period: {label}",
                    export_identity=label,
                )
            )

    duplicates = sorted(period for period, count in Counter(periods).items() if count > 1)
    if duplicates:
        issues.append(
            CalculatedDeviationInputIssue(
                code="duplicate_periods",
                message=f"calculated export contains duplicate periods: {label}",
                export_identity=label,
                periods=duplicates,
            )
        )
    if periods != sorted(periods):
        issues.append(
            CalculatedDeviationInputIssue(
                code="periods_not_sorted",
                message=f"calculated export periods are not sorted: {label}",
                export_identity=label,
                periods=periods,
            )
        )

    required_periods = set(required.periods)
    actual_periods = set(periods)
    missing = sorted(required_periods - actual_periods)
    unexpected = sorted(actual_periods - required_periods)
    if missing:
        issues.append(
            CalculatedDeviationInputIssue(
                code="required_periods_missing",
                message=f"calculated export is missing required periods: {label}",
                export_identity=label,
                periods=missing,
            )
        )
    if unexpected:
        issues.append(
            CalculatedDeviationInputIssue(
                code="unexpected_periods",
                message=f"calculated export contains unexpected periods: {label}",
                export_identity=label,
                periods=unexpected,
            )
        )
    return issues


def _audit_inputs(
    plan: CalculatedLegacyComparisonPlan,
    export_tables: list[ExportTable],
    calculation_origin: str,
) -> list[CalculatedDeviationInputIssue]:
    issues: list[CalculatedDeviationInputIssue] = []
    if not calculation_origin.strip():
        issues.append(
            CalculatedDeviationInputIssue(
                code="calculation_origin_missing",
                message="calculated deviation report requires a calculation_origin",
            )
        )

    required_by_identity = {
        _required_identity(required): required for required in plan.required_exports
    }
    tables_by_identity: dict[ExportIdentity, list[ExportTable]] = {}
    for table in export_tables:
        tables_by_identity.setdefault(_table_identity(table), []).append(table)

    for identity, required in required_by_identity.items():
        tables = tables_by_identity.get(identity, [])
        label = _identity_label(identity)
        if not tables:
            issues.append(
                CalculatedDeviationInputIssue(
                    code="required_export_missing",
                    message=f"required calculated export is missing: {label}",
                    export_identity=label,
                    periods=list(required.periods),
                )
            )
            continue
        if len(tables) > 1:
            issues.append(
                CalculatedDeviationInputIssue(
                    code="duplicate_export",
                    message=f"calculated export identity is duplicated: {label}",
                    export_identity=label,
                )
            )
            continue
        issues.extend(_audit_table_periods(tables[0], required))

    for identity in tables_by_identity.keys() - required_by_identity.keys():
        label = _identity_label(identity)
        issues.append(
            CalculatedDeviationInputIssue(
                code="unexpected_export",
                message=f"calculated export is not required by the fixture: {label}",
                export_identity=label,
            )
        )
    return issues


def _numeric_delta(actual: object, expected: object) -> float | None:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return None
    if not isinstance(actual, int | float) or not isinstance(expected, int | float):
        return None
    return abs(float(actual) - float(expected))


def _row_global_period(row_comparison: object) -> int | None:
    for field_comparison in row_comparison.field_comparisons:
        if field_comparison.name != "global_period":
            continue
        for value in (field_comparison.actual, field_comparison.expected):
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
    return None


def _classify_fields(
    result: CalculatedLegacyComparisonResult,
) -> tuple[
    int,
    list[CalculatedFieldDifference],
    list[CalculatedFieldDifference],
    list[CalculatedFieldDifference],
]:
    exact_match_count = 0
    tolerated: list[CalculatedFieldDifference] = []
    blocking: list[CalculatedFieldDifference] = []
    open_questions: list[CalculatedFieldDifference] = []
    for table_comparison in result.comparison.table_comparisons:
        for row_comparison in table_comparison.row_comparisons:
            global_period = _row_global_period(row_comparison)
            for field_comparison in row_comparison.field_comparisons:
                delta = _numeric_delta(field_comparison.actual, field_comparison.expected)
                if field_comparison.matches:
                    if delta is None or delta == 0.0:
                        exact_match_count += 1
                        continue
                    tolerated.append(
                        CalculatedFieldDifference(
                            classification="tolerated_numeric_difference",
                            filename=table_comparison.filename,
                            global_period=global_period,
                            field_name=field_comparison.name,
                            actual=field_comparison.actual,
                            expected=field_comparison.expected,
                            abs_delta=delta,
                        )
                    )
                    continue

                difference = CalculatedFieldDifference(
                    classification=(
                        "blocking_numeric_difference" if delta is not None else "open_field_question"
                    ),
                    filename=table_comparison.filename,
                    global_period=global_period,
                    field_name=field_comparison.name,
                    actual=field_comparison.actual,
                    expected=field_comparison.expected,
                    abs_delta=delta,
                )
                if delta is not None:
                    blocking.append(difference)
                else:
                    open_questions.append(difference)
    return exact_match_count, tolerated, blocking, open_questions


def _blocked_report(
    plan: CalculatedLegacyComparisonPlan,
    export_tables: list[ExportTable],
    calculation_origin: str,
    issues: list[CalculatedDeviationInputIssue],
) -> CalculatedLegacyDeviationReport:
    return CalculatedLegacyDeviationReport(
        mode="calculated_legacy_deviation_report",
        status="blocked_input",
        fixture_path=plan.fixture_path,
        calculation_origin=calculation_origin.strip(),
        target_count=plan.target_count,
        target_period_count=plan.target_period_count,
        required_export_count=plan.required_export_count,
        supplied_export_count=len(export_tables),
        input_issues=issues,
    )


def build_calculated_legacy_deviation_report(
    fixture_path: str | Path,
    export_tables: list[ExportTable],
    *,
    calculation_origin: str,
    tolerance: float = 0.05,
) -> CalculatedLegacyDeviationReport:
    plan = build_calculated_legacy_comparison_plan(fixture_path)
    issues = _audit_inputs(plan, export_tables, calculation_origin)
    if issues:
        return _blocked_report(plan, export_tables, calculation_origin, issues)

    try:
        comparison_result = compare_calculated_export_tables_to_legacy_fixture(
            fixture_path,
            export_tables,
            calculation_origin=calculation_origin,
            tolerance=tolerance,
        )
    except ValueError as exc:
        return _blocked_report(
            plan,
            export_tables,
            calculation_origin,
            [
                CalculatedDeviationInputIssue(
                    code="comparison_input_invalid",
                    message=str(exc),
                )
            ],
        )

    exact, tolerated, blocking, open_questions = _classify_fields(comparison_result)
    status = "matches"
    if blocking or open_questions:
        status = "differences"
    elif tolerated:
        status = "matches_with_tolerated_differences"
    return CalculatedLegacyDeviationReport(
        mode="calculated_legacy_deviation_report",
        status=status,
        fixture_path=plan.fixture_path,
        calculation_origin=calculation_origin.strip(),
        target_count=plan.target_count,
        target_period_count=plan.target_period_count,
        required_export_count=plan.required_export_count,
        supplied_export_count=len(export_tables),
        input_issues=[],
        comparison_result=comparison_result,
        exact_field_match_count=exact,
        tolerated_numeric_differences=tolerated,
        blocking_numeric_differences=blocking,
        open_field_questions=open_questions,
        comparison_performed=True,
    )
