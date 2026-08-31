from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.historical_horizon_contract import (
    HistoricalHorizonContractResult,
    HistoricalHorizonExportContract,
    build_historical_horizon_contract,
)
from ims.api.production_release_corpus_report import (
    ProductionReleaseCorpusReport,
    build_production_release_corpus_report,
)
from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_100_PERIOD_STATE_POLICY_ID,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
)
from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportTable,
)
from ims.model.legacy_export_identity import build_legacy_export_identity


CONTRACT_VERSION = "pr93-v1"
CONTROLLED_BASE_SEED = 20260001
CALCULATION_ORIGIN = "vdefmd6_controlled_100_period_core_exports_pr93"
DELIVERY_FILENAMES = ("imsvu014.dat", "imsvnsk1.dat")


@dataclass(frozen=True)
class Historical100PeriodDeliveryIssue:
    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class Historical100PeriodDeliveryTarget:
    filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str | None
    raw_selector_value: int | str | None
    period_start: int
    period_end: int
    period_count: int
    layer_ids: tuple[str, ...]
    allowed_claims: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "subject_type": self.subject_type,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "raw_selector_value": self.raw_selector_value,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "period_count": self.period_count,
            "layer_ids": list(self.layer_ids),
            "allowed_claims": list(self.allowed_claims),
        }


@dataclass(frozen=True)
class Historical100PeriodCorpusDeliveryResult:
    status: str
    root: str
    targets: tuple[Historical100PeriodDeliveryTarget, ...]
    production_report: ProductionReleaseCorpusReport
    controlled_execution_performed: bool
    issues: tuple[Historical100PeriodDeliveryIssue, ...]
    mode: str = "historical_100_period_corpus_delivery"

    def to_dict(self) -> dict[str, object]:
        production = self.production_report.to_dict()
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "root": self.root,
            "calculation_origin": CALCULATION_ORIGIN,
            "source_contracts": ["pr86-v1", "pr91-v1", "pr92-v1"],
            "state_policy_id": VDEFMD6_100_PERIOD_STATE_POLICY_ID,
            "controlled_base_seed": CONTROLLED_BASE_SEED,
            "delivered_export_count": len(self.targets),
            "delivered_period_count": sum(
                target.period_count for target in self.targets
            ),
            "required_export_count": production[
                "required_calculated_export_count"
            ],
            "missing_export_count": production[
                "missing_calculated_export_count"
            ],
            "missing_period_count": production[
                "missing_calculated_period_count"
            ],
            "targets": [target.to_dict() for target in self.targets],
            "production_corpus_status": production["status"],
            "production_release_decision": production["release_decision"],
            "production_calculated_comparison_status": production[
                "calculated_comparison_status"
            ],
            "production_calculated_comparison_performed": production[
                "calculated_comparison_performed"
            ],
            "issues": [issue.to_dict() for issue in self.issues],
            "legacy_rows_used_as_generation_input": False,
            "controlled_execution_performed": self.controlled_execution_performed,
            "writes_performed": False,
            "scheduler_started": False,
            "simulation_performed": False,
            "full_300_500_window_comparison_performed": False,
            "historical_run_identity_claimed": False,
            "historical_full_equality_claimed": False,
            "production_release_approved": False,
        }


def build_historical_100_period_corpus_delivery(
    root: Path | str = ".",
    *,
    export_tables: Sequence[ExportTable] | None = None,
) -> Historical100PeriodCorpusDeliveryResult:
    resolved_root = Path(root).expanduser().resolve()
    issues: list[Historical100PeriodDeliveryIssue] = []
    horizon_contract = build_historical_horizon_contract(resolved_root)
    _validate_horizon_contract(horizon_contract, issues)

    controlled_execution = export_tables is None
    tables = (
        _run_and_collect_tables(issues)
        if export_tables is None
        else tuple(export_tables)
    )
    targets = _validate_delivery_tables(
        horizon_contract,
        tables,
        issues,
    )
    production_report = build_production_release_corpus_report(
        resolved_root,
        calculated_export_tables=tables,
        calculation_origin=CALCULATION_ORIGIN,
    )
    _validate_production_delivery(production_report, targets, issues)
    return Historical100PeriodCorpusDeliveryResult(
        status="ready" if not issues else "error",
        root=str(resolved_root),
        targets=targets,
        production_report=production_report,
        controlled_execution_performed=controlled_execution,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_100_period_corpus_delivery",
        description=(
            "Bindet zwei kontrolliert erzeugte 100-Perioden-Tabellen an den "
            "weiterhin gesperrten Produktionskorpusbericht."
        ),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    result = build_historical_100_period_corpus_delivery(args.root)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.status == "ready" else 1


def _validate_horizon_contract(
    contract: HistoricalHorizonContractResult,
    issues: list[Historical100PeriodDeliveryIssue],
) -> None:
    if contract.status != "ready":
        _issue(
            issues,
            "horizon_contract_not_ready",
            contract.fixture_path,
            "PR92 horizon contract must be ready",
        )
        return
    entries = {
        entry.filename: entry
        for entry in contract.entries
        if entry.required_horizon == 100
    }
    if tuple(sorted(entries)) != tuple(sorted(DELIVERY_FILENAMES)):
        _issue(
            issues,
            "horizon_target_set_mismatch",
            contract.fixture_path,
            "100-period horizon targets differ from the PR93 delivery set",
        )


def _run_and_collect_tables(
    issues: list[Historical100PeriodDeliveryIssue],
) -> tuple[ExportTable, ...]:
    try:
        result = run_vdefmd6_100_periods(base_seed=CONTROLLED_BASE_SEED)
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "controlled_run_failed", "Vdefmd6", str(error))
        return ()
    _validate_run_boundaries(result, issues)
    policyholder_table = next(
        (
            table
            for table in result.vn_aggregate_export_tables
            if table.spec.filename == "imsvnsk1.dat"
        ),
        None,
    )
    if policyholder_table is None:
        _issue(
            issues,
            "controlled_run_target_missing",
            "imsvnsk1.dat",
            "controlled 100-period result has no VN-SK1 table",
        )
        return (result.vu14_export_table,)
    return (result.vu14_export_table, policyholder_table)


def _validate_run_boundaries(
    result: Vdefmd6PreShockRunResult,
    issues: list[Historical100PeriodDeliveryIssue],
) -> None:
    if result.base_seed != CONTROLLED_BASE_SEED:
        _issue(issues, "controlled_seed_mismatch", "Vdefmd6", "base seed differs")
    if result.state_policy_id != VDEFMD6_100_PERIOD_STATE_POLICY_ID:
        _issue(
            issues,
            "state_policy_mismatch",
            "Vdefmd6",
            "controlled state policy differs",
        )
    periods = tuple(item.period for item in result.period_results)
    if periods != tuple(range(2, 101)):
        _issue(
            issues,
            "controlled_period_boundary_mismatch",
            "Vdefmd6",
            "controlled transitions must cover periods 2 through 100",
        )
    if result.legacy_rows_used_as_generation_input:
        _issue(
            issues,
            "legacy_rows_used_as_generation_input",
            "Vdefmd6",
            "legacy rows must not generate calculated exports",
        )
    if result.writes_performed or result.scheduler_started or result.simulation_performed:
        _issue(
            issues,
            "controlled_run_boundary_violation",
            "Vdefmd6",
            "controlled delivery must not write, schedule or simulate",
        )


def _validate_delivery_tables(
    contract: HistoricalHorizonContractResult,
    tables: Sequence[ExportTable],
    issues: list[Historical100PeriodDeliveryIssue],
) -> tuple[Historical100PeriodDeliveryTarget, ...]:
    entries = {entry.filename: entry for entry in contract.entries}
    tables_by_filename: dict[str, list[ExportTable]] = {}
    for table in tables:
        tables_by_filename.setdefault(table.spec.filename.lower(), []).append(table)
    unexpected = sorted(set(tables_by_filename) - set(DELIVERY_FILENAMES))
    for filename in unexpected:
        _issue(
            issues,
            "delivery_target_unexpected",
            filename,
            "table is outside the PR93 100-period delivery set",
        )

    targets: list[Historical100PeriodDeliveryTarget] = []
    for filename in DELIVERY_FILENAMES:
        matches = tables_by_filename.get(filename, [])
        if not matches:
            _issue(
                issues,
                "delivery_target_missing",
                filename,
                "required 100-period delivery table is missing",
            )
            continue
        if len(matches) != 1:
            _issue(
                issues,
                "delivery_target_duplicate",
                filename,
                "100-period delivery table must be unique",
            )
            continue
        entry = entries.get(filename)
        if entry is None:
            _issue(
                issues,
                "delivery_contract_entry_missing",
                filename,
                "PR92 horizon entry is missing",
            )
            continue
        target = _validate_table(entry, matches[0], issues)
        if target is not None:
            targets.append(target)
    return tuple(targets)


def _validate_table(
    entry: HistoricalHorizonExportContract,
    table: ExportTable,
    issues: list[Historical100PeriodDeliveryIssue],
) -> Historical100PeriodDeliveryTarget | None:
    filename = entry.filename
    valid = True
    expected_identity = build_legacy_export_identity(
        entry.filename,
        entry.subject_type,
        entry.level,
        entry.selector_kind,
        entry.selector_value,
    )
    actual_identity = build_legacy_export_identity(
        table.spec.filename.lower(),
        table.spec.subject_type,
        table.spec.level,
        table.spec.selector_kind,
        table.spec.selector_value,
    )
    if actual_identity != expected_identity:
        _issue(
            issues,
            "delivery_identity_mismatch",
            filename,
            "calculated table identity differs from the PR92 contract",
        )
        valid = False
    expected_header = (
        INSURER_HEADER if entry.subject_type == "insurer" else POLICYHOLDER_HEADER
    )
    if table.header != expected_header:
        _issue(
            issues,
            "delivery_header_mismatch",
            filename,
            "calculated table header differs from its subject contract",
        )
        valid = False
    if any(len(row.values) != len(expected_header.split()) for row in table.rows):
        _issue(
            issues,
            "delivery_row_width_mismatch",
            filename,
            "calculated table rows must match the subject header width",
        )
        valid = False
    periods = _table_periods(table)
    if periods != list(range(1, 101)):
        _issue(
            issues,
            "delivery_period_boundary_mismatch",
            filename,
            "calculated table must contain contiguous periods 1 through 100",
        )
        valid = False
    layer_ids = dict(entry.horizon_layer_ids).get(100, ())
    if not layer_ids:
        _issue(
            issues,
            "delivery_layer_binding_missing",
            filename,
            "100-period table has no PR91 reference layer binding",
        )
        valid = False
    if not valid:
        return None
    return Historical100PeriodDeliveryTarget(
        filename=filename,
        subject_type=entry.subject_type,
        level=entry.level,
        selector_kind=entry.selector_kind,
        selector_value=entry.selector_value,
        raw_selector_value=table.spec.selector_value,
        period_start=periods[0],
        period_end=periods[-1],
        period_count=len(periods),
        layer_ids=layer_ids,
        allowed_claims=entry.allowed_claims,
    )


def _table_periods(table: ExportTable) -> list[int]:
    periods: list[int] = []
    for row in table.rows:
        try:
            periods.append(int(row.values[0]))
        except (IndexError, TypeError, ValueError):
            periods.append(-1)
    return periods


def _validate_production_delivery(
    report: ProductionReleaseCorpusReport,
    targets: Sequence[Historical100PeriodDeliveryTarget],
    issues: list[Historical100PeriodDeliveryIssue],
) -> None:
    expected = {
        "supplied_calculated_export_count": 2,
        "supplied_calculated_period_count": 200,
        "missing_calculated_export_count": 13,
        "missing_calculated_period_count": 6100,
    }
    for name, value in expected.items():
        if getattr(report, name) != value:
            _issue(
                issues,
                "production_delivery_count_mismatch",
                name,
                f"expected {value}, got {getattr(report, name)}",
            )
    if tuple(sorted(report.supplied_calculated_exports)) != tuple(
        sorted(DELIVERY_FILENAMES)
    ):
        _issue(
            issues,
            "production_delivery_target_mismatch",
            "production_release_corpus_report",
            "production report did not accept the two PR93 targets",
        )
    if len(targets) != 2:
        return
    if (
        report.status != "blocked"
        or report.release_decision != "blocked_calculated_core_validation"
        or report.calculated_core_validation_complete
    ):
        _issue(
            issues,
            "production_release_boundary_changed",
            "production_release_corpus_report",
            "partial delivery must keep production release blocked",
        )


def _issue(
    issues: list[Historical100PeriodDeliveryIssue],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(Historical100PeriodDeliveryIssue(code, path, message))


if __name__ == "__main__":
    raise SystemExit(main())
