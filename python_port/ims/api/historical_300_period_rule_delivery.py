from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Sequence

from ims.api.historical_horizon_contract import (
    HistoricalHorizonContractResult,
    HistoricalHorizonExportContract,
    HistoricalPrefixValidationResult,
    LayeredExportTableSnapshot,
    build_historical_horizon_contract,
    validate_historical_horizon_prefixes,
)
from ims.api.production_release_corpus_report import (
    ProductionReleaseCorpusReport,
    build_production_release_corpus_report,
)
from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_100_PERIOD_STATE_POLICY_ID,
    VDEFMD6_300_PERIOD_STATE_POLICY_ID,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
    run_vdefmd6_300_periods,
)
from ims.model.agrsich_export import POLICYHOLDER_HEADER, ExportTable
from ims.model.legacy_agrsich_multi_period import (
    LegacyTableComparison,
    build_multi_period_legacy_comparison,
    compare_policyholder_export_table_to_legacy,
)
from ims.model.legacy_export_identity import build_legacy_export_identity
from ims.model.legacy_validation_report import (
    LegacyValidationReport,
    build_legacy_validation_report_from_multi_period_comparison,
)
from ims.model.legacy_validation_run import (
    LegacyValidationTarget,
    load_legacy_validation_targets_from_fixture,
)
from ims.model.legacy_vn_reference import parse_legacy_policyholder_dat


CONTRACT_VERSION = "pr95-v1"
CONTROLLED_BASE_SEED = 20260001
CALCULATION_ORIGIN = "vdefmd6_controlled_100_300_rule_delivery_pr95"
RULE_FILENAMES = ("imsvnr01.dat", "imsvnr02.dat")
CUMULATIVE_FILENAMES = (
    "imsvu014.dat",
    "imsvnsk1.dat",
    *RULE_FILENAMES,
)
EXPECTED_REFERENCE_PATHS = {
    "imsvnr01.dat": Path("tests/references/legacy_agrsich/IMSVNR01.DAT"),
    "imsvnr02.dat": Path("tests/references/legacy_agrsich/IMSVNR02.DAT"),
}
REFERENCE_SHA256 = {
    "imsvnr01.dat": (
        "79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9"
    ),
    "imsvnr02.dat": (
        "695ca328675b1eb46bcb6e15c0e8c41ce78a48c98ac5216c7644423ced5a4eec"
    ),
}
EXPECTED_COMPARISON = {
    "imsvnr01.dat": {
        "period_count": 300,
        "matched_rows": 0,
        "mismatched_rows": 300,
        "field_count": 3900,
        "exact_field_match_count": 931,
        "tolerated_numeric_difference_count": 0,
        "blocking_numeric_difference_count": 2967,
        "open_field_question_count": 2,
    },
    "imsvnr02.dat": {
        "period_count": 300,
        "matched_rows": 0,
        "mismatched_rows": 300,
        "field_count": 3900,
        "exact_field_match_count": 608,
        "tolerated_numeric_difference_count": 79,
        "blocking_numeric_difference_count": 2628,
        "open_field_question_count": 585,
    },
}


@dataclass(frozen=True)
class Historical300RuleDeliveryIssue:
    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class Historical300RuleDeliveryTarget:
    filename: str
    reference_path: str
    reference_sha256: str
    level: str
    selector_value: int
    layer_ids: tuple[str, ...]
    allowed_claims: tuple[str, ...]
    period_count: int
    matched_rows: int
    mismatched_rows: int
    field_count: int
    exact_field_match_count: int
    tolerated_numeric_difference_count: int
    blocking_numeric_difference_count: int
    open_field_question_count: int
    fields_with_differences: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "reference_path": self.reference_path,
            "reference_sha256": self.reference_sha256,
            "subject_type": "policyholder",
            "level": self.level,
            "selector_kind": "rule",
            "selector_value": self.selector_value,
            "layer_ids": list(self.layer_ids),
            "allowed_claims": list(self.allowed_claims),
            "period_start": 1,
            "period_end": 300,
            "period_count": self.period_count,
            "matched_rows": self.matched_rows,
            "mismatched_rows": self.mismatched_rows,
            "field_count": self.field_count,
            "exact_field_match_count": self.exact_field_match_count,
            "tolerated_numeric_difference_count": (
                self.tolerated_numeric_difference_count
            ),
            "blocking_numeric_difference_count": (
                self.blocking_numeric_difference_count
            ),
            "open_field_question_count": self.open_field_question_count,
            "fields_with_differences": list(self.fields_with_differences),
        }


@dataclass(frozen=True)
class Historical300RuleDeliveryResult:
    root: str
    targets: tuple[Historical300RuleDeliveryTarget, ...]
    prefix_validation: HistoricalPrefixValidationResult | None
    historical_report: LegacyValidationReport | None
    production_report: ProductionReleaseCorpusReport
    controlled_execution_performed: bool
    issues: tuple[Historical300RuleDeliveryIssue, ...]
    mode: str = "historical_300_period_rule_delivery"

    @property
    def status(self) -> str:
        return "ready" if not self.issues else "error"

    def to_dict(self) -> dict[str, object]:
        production = self.production_report.to_dict()
        prefix = (
            self.prefix_validation.to_dict()
            if self.prefix_validation is not None
            else {}
        )
        historical = self.historical_report
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "root": self.root,
            "calculation_origin": CALCULATION_ORIGIN,
            "source_contracts": ["pr91-v1", "pr92-v1", "pr93-v1", "pr94-v1"],
            "controlled_base_seed": CONTROLLED_BASE_SEED,
            "current_delivery_export_count": len(self.targets),
            "current_delivery_period_count": sum(
                target.period_count for target in self.targets
            ),
            "cumulative_delivered_export_count": production[
                "supplied_calculated_export_count"
            ],
            "cumulative_delivered_period_count": production[
                "supplied_calculated_period_count"
            ],
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
            "prefix_validation_status": prefix.get("status", "not_available"),
            "prefix_comparison_count": prefix.get("comparison_count", 0),
            "prefix_compared_row_count": prefix.get("compared_row_count", 0),
            "historical_comparison_status": (
                "documented_differences"
                if historical is not None and not historical.matches
                else "matches"
                if historical is not None
                else "not_available"
            ),
            "historical_comparison_performed": historical is not None,
            "historical_comparison_matches": (
                historical.matches if historical is not None else None
            ),
            "historical_compared_row_count": (
                historical.total_rows if historical is not None else 0
            ),
            "historical_matched_row_count": (
                historical.matched_rows if historical is not None else 0
            ),
            "historical_mismatched_row_count": (
                historical.mismatched_rows if historical is not None else 0
            ),
            "production_corpus_status": production["status"],
            "production_release_decision": production["release_decision"],
            "production_calculated_comparison_performed": production[
                "calculated_comparison_performed"
            ],
            "controlled_execution_performed": self.controlled_execution_performed,
            "issues": [issue.to_dict() for issue in self.issues],
            "legacy_rows_used_as_generation_input": False,
            "writes_performed": False,
            "scheduler_started": False,
            "simulation_performed": False,
            "historical_run_identity_claimed": False,
            "historical_rng_equality_claimed": False,
            "historical_full_equality_claimed": False,
            "production_release_approved": False,
        }


def build_historical_300_period_rule_delivery(
    root: Path | str = ".",
    *,
    baseline_result: Vdefmd6PreShockRunResult | None = None,
    extended_result: Vdefmd6PreShockRunResult | None = None,
    baseline_rule_tables: Sequence[ExportTable] | None = None,
    extended_rule_tables: Sequence[ExportTable] | None = None,
) -> Historical300RuleDeliveryResult:
    resolved_root = Path(root).expanduser().resolve()
    issues: list[Historical300RuleDeliveryIssue] = []
    horizon_contract = build_historical_horizon_contract(resolved_root)
    entries = _validate_horizon_contract(horizon_contract, issues)

    controlled_execution = baseline_result is None or extended_result is None
    baseline = baseline_result or _run_controlled(100, issues)
    extended = extended_result or _run_controlled(300, issues)
    _validate_run_boundaries(baseline, extended, issues)

    baseline_tables = tuple(
        baseline_rule_tables
        if baseline_rule_tables is not None
        else _select_rule_tables(baseline)
    )
    extended_tables = tuple(
        extended_rule_tables
        if extended_rule_tables is not None
        else _select_rule_tables(extended)
    )
    valid_baseline = _validate_rule_tables(
        "baseline", baseline_tables, 100, entries, issues
    )
    valid_extended = _validate_rule_tables(
        "extended", extended_tables, 300, entries, issues
    )
    prefix_validation = _validate_prefixes(
        horizon_contract,
        valid_baseline,
        valid_extended,
        entries,
        issues,
    )
    targets, historical_report = _compare_historical_targets(
        resolved_root,
        horizon_contract,
        valid_extended,
        entries,
        issues,
    )

    cumulative_tables = _collect_cumulative_tables(
        baseline,
        valid_extended,
        issues,
    )
    production_report = build_production_release_corpus_report(
        resolved_root,
        calculated_export_tables=cumulative_tables,
        calculation_origin=CALCULATION_ORIGIN,
    )
    _validate_production_delivery(production_report, issues)
    return Historical300RuleDeliveryResult(
        root=str(resolved_root),
        targets=targets,
        prefix_validation=prefix_validation,
        historical_report=historical_report,
        production_report=production_report,
        controlled_execution_performed=controlled_execution,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_300_period_rule_delivery",
        description=(
            "Vergleicht die zwei getrennten ZINS000-Regelfenster vollstaendig "
            "und bindet vier Tabellen kumuliert an den gesperrten Korpusbericht."
        ),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    result = build_historical_300_period_rule_delivery(args.root)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.status == "ready" else 1


def _run_controlled(
    horizon: int,
    issues: list[Historical300RuleDeliveryIssue],
) -> Vdefmd6PreShockRunResult | None:
    try:
        if horizon == 100:
            return run_vdefmd6_100_periods(base_seed=CONTROLLED_BASE_SEED)
        return run_vdefmd6_300_periods(base_seed=CONTROLLED_BASE_SEED)
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "controlled_run_failed", f"Vdefmd6@{horizon}", str(error))
        return None


def _validate_horizon_contract(
    contract: HistoricalHorizonContractResult,
    issues: list[Historical300RuleDeliveryIssue],
) -> dict[str, HistoricalHorizonExportContract]:
    if contract.status != "ready":
        _issue(
            issues,
            "horizon_contract_not_ready",
            contract.fixture_path,
            "PR92 horizon contract must be ready",
        )
    entries = {
        entry.filename: entry
        for entry in contract.entries
        if entry.required_horizon == 300
    }
    if tuple(sorted(entries)) != tuple(sorted(RULE_FILENAMES)):
        _issue(
            issues,
            "horizon_target_set_mismatch",
            contract.fixture_path,
            "300-period horizon targets differ from the PR95 rule set",
        )
    for filename, entry in entries.items():
        if (
            entry.level != "II"
            or entry.selector_kind != "rule"
            or entry.layer_ids != ("zins000_archive",)
            or entry.allowed_claims != ("archive_content_match_only",)
        ):
            _issue(
                issues,
                "horizon_layer_boundary_mismatch",
                filename,
                "PR95 targets must remain isolated ZINS000 rule references",
            )
    return entries


def _validate_run_boundaries(
    baseline: Vdefmd6PreShockRunResult | None,
    extended: Vdefmd6PreShockRunResult | None,
    issues: list[Historical300RuleDeliveryIssue],
) -> None:
    if baseline is None or extended is None:
        return
    expected = (
        ("baseline", baseline, 100, VDEFMD6_100_PERIOD_STATE_POLICY_ID),
        ("extended", extended, 300, VDEFMD6_300_PERIOD_STATE_POLICY_ID),
    )
    for name, result, horizon, policy_id in expected:
        if result.base_seed != CONTROLLED_BASE_SEED:
            _issue(issues, "controlled_seed_mismatch", name, "base seed differs")
        if result.max_periods != horizon:
            _issue(issues, "controlled_horizon_mismatch", name, "horizon differs")
        if result.state_policy_id != policy_id:
            _issue(issues, "state_policy_mismatch", name, "state policy differs")
        if tuple(item.period for item in result.period_results) != tuple(
            range(2, horizon + 1)
        ):
            _issue(
                issues,
                "controlled_period_boundary_mismatch",
                name,
                f"state transitions must cover periods 2 through {horizon}",
            )
        if (
            result.legacy_rows_used_as_generation_input
            or result.writes_performed
            or result.scheduler_started
            or result.simulation_performed
            or result.historical_same_slot_order_claimed
            or result.historical_rng_equality_claimed
            or result.historical_full_equality_claimed
        ):
            _issue(
                issues,
                "controlled_run_boundary_violation",
                name,
                "controlled delivery must not use legacy rows, write, schedule or simulate",
            )
    if baseline.period_results != extended.period_results[:99]:
        _issue(
            issues,
            "state_prefix_mismatch",
            "Vdefmd6@1-100",
            "extended state changed the exact baseline prefix",
        )


def _select_rule_tables(
    result: Vdefmd6PreShockRunResult | None,
) -> tuple[ExportTable, ...]:
    if result is None:
        return ()
    return tuple(
        table
        for table in (
            *result.vn_rule_group_1_export_tables,
            *result.vn_rule_group_2_export_tables,
        )
        if table.spec.filename.lower() in RULE_FILENAMES
    )


def _validate_rule_tables(
    name: str,
    tables: Sequence[ExportTable],
    horizon: int,
    entries: dict[str, HistoricalHorizonExportContract],
    issues: list[Historical300RuleDeliveryIssue],
) -> dict[str, ExportTable]:
    grouped: dict[str, list[ExportTable]] = {}
    for table in tables:
        grouped.setdefault(table.spec.filename.lower(), []).append(table)
    if set(grouped) != set(RULE_FILENAMES) or any(
        len(items) != 1 for items in grouped.values()
    ):
        _issue(
            issues,
            f"{name}_target_set_mismatch",
            name,
            "rule delivery must contain both PR95 targets exactly once",
        )
    valid: dict[str, ExportTable] = {}
    for filename in RULE_FILENAMES:
        matches = grouped.get(filename, ())
        entry = entries.get(filename)
        if len(matches) != 1 or entry is None:
            continue
        table = matches[0]
        expected_identity = build_legacy_export_identity(
            filename,
            "policyholder",
            "II",
            "rule",
            entry.selector_value,
        )
        actual_identity = build_legacy_export_identity(
            table.spec.filename,
            table.spec.subject_type,
            table.spec.level,
            table.spec.selector_kind,
            table.spec.selector_value,
        )
        periods = _table_periods(table)
        table_valid = True
        if actual_identity != expected_identity:
            _issue(
                issues,
                f"{name}_identity_mismatch",
                filename,
                "calculated rule identity differs from the horizon contract",
            )
            table_valid = False
        if table.header != POLICYHOLDER_HEADER:
            _issue(
                issues,
                f"{name}_header_mismatch",
                filename,
                "calculated rule header differs from the policyholder contract",
            )
            table_valid = False
        if any(len(row.values) != 12 for row in table.rows):
            _issue(
                issues,
                f"{name}_row_width_mismatch",
                filename,
                "calculated rule rows must contain 12 values",
            )
            table_valid = False
        if periods != list(range(1, horizon + 1)):
            _issue(
                issues,
                f"{name}_period_boundary_mismatch",
                filename,
                f"calculated rule periods must cover 1 through {horizon}",
            )
            table_valid = False
        if table_valid:
            valid[filename] = table
    return valid


def _validate_prefixes(
    contract: HistoricalHorizonContractResult,
    baseline: dict[str, ExportTable],
    extended: dict[str, ExportTable],
    entries: dict[str, HistoricalHorizonExportContract],
    issues: list[Historical300RuleDeliveryIssue],
) -> HistoricalPrefixValidationResult | None:
    snapshots: list[LayeredExportTableSnapshot] = []
    for filename in RULE_FILENAMES:
        entry = entries.get(filename)
        if entry is None or filename not in baseline or filename not in extended:
            continue
        layer_ids = dict(entry.horizon_layer_ids)
        if 100 not in layer_ids or 300 not in layer_ids:
            _issue(
                issues,
                "prefix_layer_binding_missing",
                filename,
                "PR95 prefix snapshots require layer bindings at 100 and 300",
            )
            continue
        snapshots.extend(
            (
                LayeredExportTableSnapshot(100, layer_ids[100], baseline[filename]),
                LayeredExportTableSnapshot(300, layer_ids[300], extended[filename]),
            )
        )
    if not snapshots:
        return None
    result = validate_historical_horizon_prefixes(contract, snapshots)
    if (
        result.status != "ok"
        or result.comparison_count != 2
        or result.compared_row_count != 200
    ):
        _issue(
            issues,
            "prefix_validation_failed",
            contract.fixture_path,
            "both 300-period rules must keep their exact 100-period prefix",
        )
    return result


def _compare_historical_targets(
    root: Path,
    contract: HistoricalHorizonContractResult,
    tables: dict[str, ExportTable],
    entries: dict[str, HistoricalHorizonExportContract],
    issues: list[Historical300RuleDeliveryIssue],
) -> tuple[tuple[Historical300RuleDeliveryTarget, ...], LegacyValidationReport | None]:
    try:
        fixture_targets = load_legacy_validation_targets_from_fixture(
            contract.fixture_path
        )
    except (OSError, UnicodeError, ValueError) as error:
        _issue(issues, "legacy_bundle_invalid", contract.fixture_path, str(error))
        return (), None
    selected_targets = [
        target
        for target in fixture_targets
        if target.export_filename in RULE_FILENAMES
    ]
    targets = {target.export_filename: target for target in selected_targets}
    if (
        len(selected_targets) != len(RULE_FILENAMES)
        or set(targets) != set(RULE_FILENAMES)
    ):
        _issue(
            issues,
            "legacy_target_set_mismatch",
            contract.fixture_path,
            "legacy bundle must contain both PR95 targets exactly once",
        )
        return (), None

    comparisons: list[LegacyTableComparison] = []
    references: dict[str, tuple[LegacyValidationTarget, str]] = {}
    for filename in RULE_FILENAMES:
        target = targets[filename]
        table = tables.get(filename)
        entry = entries.get(filename)
        expected_path = (root / EXPECTED_REFERENCE_PATHS[filename]).resolve()
        if target.legacy_path.resolve() != expected_path:
            _issue(
                issues,
                "legacy_reference_path_mismatch",
                filename,
                "PR95 reference path differs from the versioned contract",
            )
        try:
            digest = hashlib.sha256(target.legacy_path.read_bytes()).hexdigest()
        except OSError as error:
            _issue(issues, "legacy_reference_unreadable", filename, str(error))
            continue
        if digest != REFERENCE_SHA256[filename]:
            _issue(
                issues,
                "legacy_reference_hash_mismatch",
                filename,
                "PR95 reference hash differs from the archive-bound contract",
            )
        if (
            target.subject_type != "policyholder"
            or target.level != "II"
            or target.selector_kind != "rule"
            or entry is None
            or target.selector_value != entry.selector_value
            or target.periods != list(range(1, 301))
        ):
            _issue(
                issues,
                "legacy_reference_contract_mismatch",
                filename,
                "legacy target identity or 300-period boundary differs",
            )
        if table is None:
            continue
        try:
            legacy_table = parse_legacy_policyholder_dat(target.legacy_path)
            comparison = compare_policyholder_export_table_to_legacy(
                table,
                legacy_table,
                require_complete_legacy_periods=True,
            )
        except (OSError, UnicodeError, TypeError, ValueError) as error:
            _issue(issues, "historical_comparison_failed", filename, str(error))
            continue
        comparisons.append(comparison)
        references[filename] = (target, digest)

    if len(comparisons) != 2:
        return (), None
    report = build_legacy_validation_report_from_multi_period_comparison(
        build_multi_period_legacy_comparison(comparisons)
    )
    summaries = {summary.filename: summary for summary in report.file_summaries}
    comparison_by_filename = {
        comparison.filename: comparison for comparison in comparisons
    }
    delivery_targets: list[Historical300RuleDeliveryTarget] = []
    for filename in RULE_FILENAMES:
        target, digest = references[filename]
        summary = summaries[filename]
        counts = _field_counts(comparison_by_filename[filename])
        delivery_target = Historical300RuleDeliveryTarget(
            filename=filename,
            reference_path=str(target.legacy_path.resolve()),
            reference_sha256=digest,
            level=target.level,
            selector_value=int(target.selector_value),
            layer_ids=entries[filename].layer_ids,
            allowed_claims=entries[filename].allowed_claims,
            period_count=summary.row_count,
            matched_rows=summary.matched_rows,
            mismatched_rows=summary.mismatched_rows,
            fields_with_differences=tuple(summary.fields_with_differences),
            **counts,
        )
        _validate_expected_comparison(delivery_target, issues)
        delivery_targets.append(delivery_target)
    if report.total_rows != 600 or report.matched_rows != 0:
        _issue(
            issues,
            "historical_comparison_summary_mismatch",
            "IMSVNR01/02",
            "PR95 observation must cover 600 currently differing rows",
        )
    return tuple(delivery_targets), report


def _field_counts(comparison: LegacyTableComparison) -> dict[str, int]:
    exact = 0
    tolerated = 0
    blocking = 0
    open_questions = 0
    field_count = 0
    for row in comparison.row_comparisons:
        for field in row.field_comparisons:
            field_count += 1
            actual = field.actual
            expected = field.expected
            numeric = (
                isinstance(actual, int | float)
                and not isinstance(actual, bool)
                and isinstance(expected, int | float)
                and not isinstance(expected, bool)
            )
            delta = abs(float(actual) - float(expected)) if numeric else None
            if field.matches:
                if delta is None or delta == 0.0:
                    exact += 1
                else:
                    tolerated += 1
            elif numeric:
                blocking += 1
            else:
                open_questions += 1
    return {
        "field_count": field_count,
        "exact_field_match_count": exact,
        "tolerated_numeric_difference_count": tolerated,
        "blocking_numeric_difference_count": blocking,
        "open_field_question_count": open_questions,
    }


def _validate_expected_comparison(
    target: Historical300RuleDeliveryTarget,
    issues: list[Historical300RuleDeliveryIssue],
) -> None:
    actual = {
        key: getattr(target, key)
        for key in EXPECTED_COMPARISON[target.filename]
    }
    if actual != EXPECTED_COMPARISON[target.filename]:
        _issue(
            issues,
            "historical_observation_fingerprint_mismatch",
            target.filename,
            "calculated-to-historical field observation changed",
        )


def _collect_cumulative_tables(
    baseline: Vdefmd6PreShockRunResult | None,
    extended_rules: dict[str, ExportTable],
    issues: list[Historical300RuleDeliveryIssue],
) -> tuple[ExportTable, ...]:
    if baseline is None:
        return tuple(extended_rules.values())
    policyholder_table = next(
        (
            table
            for table in baseline.vn_aggregate_export_tables
            if table.spec.filename.lower() == "imsvnsk1.dat"
        ),
        None,
    )
    if policyholder_table is None:
        _issue(
            issues,
            "baseline_delivery_target_missing",
            "imsvnsk1.dat",
            "PR93 cumulative baseline table is missing",
        )
        baseline_tables = (baseline.vu14_export_table,)
    else:
        baseline_tables = (baseline.vu14_export_table, policyholder_table)
    return (*baseline_tables, *extended_rules.values())


def _validate_production_delivery(
    report: ProductionReleaseCorpusReport,
    issues: list[Historical300RuleDeliveryIssue],
) -> None:
    expected = {
        "supplied_calculated_export_count": 4,
        "supplied_calculated_period_count": 800,
        "missing_calculated_export_count": 11,
        "missing_calculated_period_count": 5500,
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
        sorted(CUMULATIVE_FILENAMES)
    ):
        _issue(
            issues,
            "production_delivery_target_mismatch",
            "production_release_corpus_report",
            "production report did not accept the four cumulative targets",
        )
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


def _table_periods(table: ExportTable) -> list[int]:
    periods: list[int] = []
    for row in table.rows:
        try:
            periods.append(int(row.values[0]))
        except (IndexError, TypeError, ValueError):
            periods.append(-1)
    return periods


def _issue(
    issues: list[Historical300RuleDeliveryIssue],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(Historical300RuleDeliveryIssue(code, path, message))


if __name__ == "__main__":
    raise SystemExit(main())
