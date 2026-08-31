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
    build_historical_horizon_contract,
)
from ims.api.production_release_corpus_report import (
    ProductionReleaseCorpusReport,
    build_production_release_corpus_report,
)
from ims.engine.vdefmd6_repeat_corpus import (
    HISTORICAL_PERIODS_PER_RUN,
    REPEAT_CORPUS_POLICY_ID,
    Vdefmd6RepeatCorpusResult,
    run_vdefmd6_100_period_repetitions,
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


CONTRACT_VERSION = "pr98-v1"
CONTROLLED_BASE_SEED = 20260001
HISTORICAL_RUN_COUNT = 3
CALCULATION_ORIGIN = "vdefmd6_controlled_3x100_rule_repeat_diagnostics_pr98"
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
        "exact_field_match_count": 946,
        "tolerated_numeric_difference_count": 1,
        "blocking_numeric_difference_count": 2947,
        "open_field_question_count": 6,
    },
    "imsvnr02.dat": {
        "period_count": 300,
        "matched_rows": 0,
        "mismatched_rows": 300,
        "field_count": 3900,
        "exact_field_match_count": 615,
        "tolerated_numeric_difference_count": 127,
        "blocking_numeric_difference_count": 2600,
        "open_field_question_count": 558,
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
            "result_row_start": 1,
            "result_row_end": 300,
            "result_row_count": self.period_count,
            "run_start": 1,
            "run_end": HISTORICAL_RUN_COUNT,
            "local_period_start": 1,
            "local_period_end": HISTORICAL_PERIODS_PER_RUN,
            "numbering_semantics": "cumulative_result_rows_across_100_period_runs",
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
    historical_report: LegacyValidationReport | None
    production_report: ProductionReleaseCorpusReport
    run_seeds: tuple[int, ...]
    controlled_execution_performed: bool
    issues: tuple[Historical300RuleDeliveryIssue, ...]
    mode: str = "historical_300_row_rule_repeat_diagnostics"

    @property
    def status(self) -> str:
        return "ready" if not self.issues else "error"

    def to_dict(self) -> dict[str, object]:
        production = self.production_report.to_dict()
        historical = self.historical_report
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "root": self.root,
            "calculation_origin": CALCULATION_ORIGIN,
            "source_contracts": ["pr91-v1", "pr98-v1"],
            "controlled_base_seed": CONTROLLED_BASE_SEED,
            "controlled_run_seeds": list(self.run_seeds),
            "historical_run_count": HISTORICAL_RUN_COUNT,
            "historical_periods_per_run": HISTORICAL_PERIODS_PER_RUN,
            "historical_result_row_count": 300,
            "repeat_corpus_policy_id": REPEAT_CORPUS_POLICY_ID,
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
            "prefix_validation_status": "not_applicable_repeated_runs",
            "prefix_comparison_count": 0,
            "prefix_compared_row_count": 0,
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
            "historical_single_run_horizon_claimed": False,
            "historical_rng_reproduction_required": False,
            "historical_rng_equality_claimed": False,
            "historical_full_equality_claimed": False,
            "production_release_approved": False,
        }


def build_historical_300_period_rule_delivery(
    root: Path | str = ".",
    *,
    repeat_corpus: Vdefmd6RepeatCorpusResult | None = None,
    repeat_rule_tables: Sequence[ExportTable] | None = None,
) -> Historical300RuleDeliveryResult:
    resolved_root = Path(root).expanduser().resolve()
    issues: list[Historical300RuleDeliveryIssue] = []
    horizon_contract = build_historical_horizon_contract(resolved_root)
    entries = _validate_horizon_contract(horizon_contract, issues)

    controlled_execution = repeat_corpus is None
    corpus = repeat_corpus or _run_controlled_repetitions(issues)
    _validate_repeat_corpus(corpus, issues)
    repeated_tables = tuple(
        repeat_rule_tables
        if repeat_rule_tables is not None
        else _select_rule_tables(corpus)
    )
    valid_repeated = _validate_rule_tables(
        "repeat_corpus",
        repeated_tables,
        300,
        entries,
        issues,
    )
    targets, historical_report = _compare_historical_targets(
        resolved_root,
        horizon_contract,
        valid_repeated,
        entries,
        issues,
    )

    cumulative_tables = _collect_cumulative_tables(
        corpus,
        valid_repeated,
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
        historical_report=historical_report,
        production_report=production_report,
        run_seeds=corpus.run_seeds if corpus is not None else (),
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


def _run_controlled_repetitions(
    issues: list[Historical300RuleDeliveryIssue],
) -> Vdefmd6RepeatCorpusResult | None:
    try:
        return run_vdefmd6_100_period_repetitions(
            base_seed=CONTROLLED_BASE_SEED,
            run_count=HISTORICAL_RUN_COUNT,
        )
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "controlled_repeat_corpus_failed", "Vdefmd6@3x100", str(error))
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
            "PR98 repeat corpus contract must be ready",
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
            "300-row repeat targets differ from the rule diagnostics set",
        )
    for filename, entry in entries.items():
        if (
            entry.level != "II"
            or entry.selector_kind != "rule"
            or entry.required_run_count != HISTORICAL_RUN_COUNT
            or entry.layer_ids != ("zins000_archive",)
            or entry.allowed_claims != ("archive_content_match_only",)
        ):
            _issue(
                issues,
                "horizon_layer_boundary_mismatch",
                filename,
                "repeat targets must remain three-run ZINS000 rule references",
            )
    return entries


def _validate_repeat_corpus(
    corpus: Vdefmd6RepeatCorpusResult | None,
    issues: list[Historical300RuleDeliveryIssue],
) -> None:
    if corpus is None:
        return
    expected_seeds = tuple(
        CONTROLLED_BASE_SEED + index for index in range(HISTORICAL_RUN_COUNT)
    )
    if (
        corpus.base_seed != CONTROLLED_BASE_SEED
        or corpus.run_count != HISTORICAL_RUN_COUNT
        or corpus.periods_per_run != HISTORICAL_PERIODS_PER_RUN
        or corpus.result_row_count != 300
        or corpus.run_seeds != expected_seeds
        or corpus.policy_id != REPEAT_CORPUS_POLICY_ID
    ):
        _issue(
            issues,
            "repeat_corpus_boundary_mismatch",
            "Vdefmd6@3x100",
            "controlled corpus must contain three independent 100-period runs",
        )


def _select_rule_tables(
    corpus: Vdefmd6RepeatCorpusResult | None,
) -> tuple[ExportTable, ...]:
    if corpus is None:
        return ()
    return tuple(
        table
        for table in corpus.export_tables
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
                "calculated rule identity differs from the result-row contract",
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
                f"calculated rule result rows must cover 1 through {horizon}",
            )
            table_valid = False
        if table_valid:
            valid[filename] = table
    return valid


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
                "legacy target identity or 300-result-row boundary differs",
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
    corpus: Vdefmd6RepeatCorpusResult | None,
    extended_rules: dict[str, ExportTable],
    issues: list[Historical300RuleDeliveryIssue],
) -> tuple[ExportTable, ...]:
    if corpus is None:
        return tuple(extended_rules.values())
    baseline = corpus.runs[0]
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
