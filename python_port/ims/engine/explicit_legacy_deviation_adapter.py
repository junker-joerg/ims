from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ims.engine.explicit_period_runner import ExplicitMultiPeriodRunResult
from ims.model.agrsich_export import ExportTable
from ims.model.legacy_calculated_comparison import build_calculated_legacy_comparison_plan
from ims.model.legacy_calculated_deviation_report import (
    CalculatedLegacyDeviationReport,
    build_calculated_legacy_deviation_report,
)


ExportIdentity = tuple[str, str, str, str, int | str | None]


@dataclass(slots=True)
class ExplicitLegacyDeviationAdapterResult:
    mode: str
    calculation_origin: str
    calculation_scope: str
    validation_fixture_path: Path
    source_period_count: int
    source_processed_global_periods: list[int]
    source_export_table_count: int
    selected_export_count: int
    ignored_source_export_table_count: int
    ignored_export_identities: list[str]
    deviation_report: CalculatedLegacyDeviationReport
    source_execution_performed: bool = True
    source_writes_performed: bool = False
    source_legacy_comparison_performed: bool = False
    adapter_writes_performed: bool = False
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False
    source_state_origin_verified: bool = False
    independent_historical_state_evolution_verified: bool = False
    historical_equivalence_claimed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "calculation_origin": self.calculation_origin,
            "calculation_scope": self.calculation_scope,
            "validation_fixture_path": str(self.validation_fixture_path),
            "source_period_count": self.source_period_count,
            "source_processed_global_periods": list(self.source_processed_global_periods),
            "source_export_table_count": self.source_export_table_count,
            "selected_export_count": self.selected_export_count,
            "ignored_source_export_table_count": self.ignored_source_export_table_count,
            "ignored_export_identities": list(self.ignored_export_identities),
            "deviation_report": self.deviation_report.to_dict(),
            "source_execution_performed": self.source_execution_performed,
            "source_writes_performed": self.source_writes_performed,
            "source_legacy_comparison_performed": self.source_legacy_comparison_performed,
            "adapter_writes_performed": self.adapter_writes_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
            "source_state_origin_verified": self.source_state_origin_verified,
            "independent_historical_state_evolution_verified": (
                self.independent_historical_state_evolution_verified
            ),
            "historical_equivalence_claimed": self.historical_equivalence_claimed,
        }


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


def _required_identities(validation_fixture_path: str | Path) -> set[ExportIdentity]:
    plan = build_calculated_legacy_comparison_plan(validation_fixture_path)
    return {
        (
            required.filename,
            required.subject_type,
            required.level,
            required.selector_kind,
            required.selector_value,
        )
        for required in plan.required_exports
    }


def _select_and_merge_required_exports(
    result: ExplicitMultiPeriodRunResult,
    required_identities: set[ExportIdentity],
) -> tuple[list[ExportTable], int, list[str]]:
    selected: dict[ExportIdentity, ExportTable] = {}
    ignored_count = 0
    ignored_identities: set[ExportIdentity] = set()
    for period_result in result.period_results:
        for table in period_result.export_tables:
            identity = _table_identity(table)
            if identity not in required_identities:
                ignored_count += 1
                ignored_identities.add(identity)
                continue

            existing = selected.get(identity)
            if existing is None:
                selected[identity] = ExportTable(
                    spec=table.spec,
                    header=table.header,
                    rows=list(table.rows),
                )
                continue
            if existing.header != table.header:
                raise ValueError(
                    "explicit legacy deviation adapter rejects changing export headers for "
                    f"{_identity_label(identity)}"
                )
            existing.rows.extend(table.rows)

    selected_tables = sorted(
        selected.values(),
        key=lambda table: (
            table.spec.filename,
            table.spec.subject_type,
            table.spec.level,
            table.spec.selector_kind,
            str(table.spec.selector_value),
        ),
    )
    return (
        selected_tables,
        ignored_count,
        sorted(_identity_label(identity) for identity in ignored_identities),
    )


def build_explicit_legacy_deviation_report(
    result: ExplicitMultiPeriodRunResult,
    validation_fixture_path: str | Path,
    *,
    tolerance: float = 0.05,
) -> ExplicitLegacyDeviationAdapterResult:
    fixture_path = Path(validation_fixture_path).resolve()
    required_identities = _required_identities(fixture_path)
    selected_tables, ignored_count, ignored_identities = _select_and_merge_required_exports(
        result,
        required_identities,
    )
    calculation_origin = "explicit_multi_period_run_result"
    calculation_scope = "agrsich_aggregation_and_export_from_explicit_state_snapshots"
    deviation_report = build_calculated_legacy_deviation_report(
        fixture_path,
        selected_tables,
        calculation_origin=calculation_origin,
        tolerance=tolerance,
    )
    return ExplicitLegacyDeviationAdapterResult(
        mode="explicit_multi_period_legacy_deviation_adapter",
        calculation_origin=calculation_origin,
        calculation_scope=calculation_scope,
        validation_fixture_path=fixture_path,
        source_period_count=len(result.period_results),
        source_processed_global_periods=list(result.processed_global_periods),
        source_export_table_count=sum(
            len(period_result.export_tables) for period_result in result.period_results
        ),
        selected_export_count=len(selected_tables),
        ignored_source_export_table_count=ignored_count,
        ignored_export_identities=ignored_identities,
        deviation_report=deviation_report,
        source_writes_performed=bool(result.written_files or result.written_legacy_report_files),
        source_legacy_comparison_performed=result.legacy_comparison is not None,
    )
