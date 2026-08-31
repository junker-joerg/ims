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
    HistoricalHorizonReferenceSlice,
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
from ims.model.agrsich_export import INSURER_HEADER, ExportTable
from ims.model.legacy_agrsich_multi_period import (
    LegacyTableComparison,
    compare_insurer_export_table_to_legacy,
)
from ims.model.legacy_agrsich_reference import parse_legacy_insurer_dat
from ims.model.legacy_export_identity import build_legacy_export_identity
from ims.model.legacy_validation_run import (
    LegacyValidationTarget,
    load_legacy_validation_targets_from_fixture,
)


CONTRACT_VERSION = "pr98-v1"
CONTROLLED_BASE_SEED = 20260001
HISTORICAL_RUN_COUNT = 5
CALCULATION_ORIGIN = "vdefmd6_controlled_5x100_vusk1_repeat_diagnostics_pr98"
EXPORT_FILENAME = "imsvusk1.dat"
REFERENCE_FILENAMES = (
    "VUSK1L5.DAT",
    "VUSK1L4.DAT",
    "VUSK1L3.DAT",
    "VUSK1L2.DAT",
    "VUSK1L1.DAT",
)
CUMULATIVE_FILENAMES = (
    "imsvu014.dat",
    "imsvnsk1.dat",
    "imsvnr01.dat",
    "imsvnr02.dat",
    EXPORT_FILENAME,
)
EXPECTED_REFERENCE_PATHS = {
    filename: Path("tests/references/legacy_agrsich") / filename
    for filename in REFERENCE_FILENAMES
}
REFERENCE_SHA256 = {
    "VUSK1L5.DAT": (
        "0d7f02f992d418baef0c259f8e6cab59bde452e34cd794aed1876dc52da6feec"
    ),
    "VUSK1L4.DAT": (
        "dbb38cf052a7bf1260f716e65642269062ddefb0ffc2348bfe9c9023c5ab27e4"
    ),
    "VUSK1L3.DAT": (
        "92a2b12f0e5715201b7af28572c5a2a912bc634d49a9038e2790000298c4d25e"
    ),
    "VUSK1L2.DAT": (
        "d77fab22e32c73ecaff95fc46ef43e9efb7548af6f882d9905983ddb28bbb38d"
    ),
    "VUSK1L1.DAT": (
        "aa9fd4e13073231fc0b8286fe36ca63ee475f35365652161c675c3d592c10568"
    ),
}
EXPECTED_COMPARISON = {
    "VUSK1L5.DAT": {
        "period_start": 1,
        "period_end": 100,
        "matched_rows": 1,
        "mismatched_rows": 99,
        "field_count": 1400,
        "exact_field_match_count": 215,
        "tolerated_numeric_difference_count": 17,
        "blocking_numeric_difference_count": 1168,
        "open_field_question_count": 0,
    },
    "VUSK1L4.DAT": {
        "period_start": 101,
        "period_end": 200,
        "matched_rows": 0,
        "mismatched_rows": 100,
        "field_count": 1400,
        "exact_field_match_count": 200,
        "tolerated_numeric_difference_count": 0,
        "blocking_numeric_difference_count": 1200,
        "open_field_question_count": 0,
    },
    "VUSK1L3.DAT": {
        "period_start": 201,
        "period_end": 300,
        "matched_rows": 1,
        "mismatched_rows": 99,
        "field_count": 1400,
        "exact_field_match_count": 213,
        "tolerated_numeric_difference_count": 15,
        "blocking_numeric_difference_count": 1172,
        "open_field_question_count": 0,
    },
    "VUSK1L2.DAT": {
        "period_start": 301,
        "period_end": 400,
        "matched_rows": 1,
        "mismatched_rows": 99,
        "field_count": 1400,
        "exact_field_match_count": 212,
        "tolerated_numeric_difference_count": 21,
        "blocking_numeric_difference_count": 1167,
        "open_field_question_count": 0,
    },
    "VUSK1L1.DAT": {
        "period_start": 401,
        "period_end": 500,
        "matched_rows": 1,
        "mismatched_rows": 99,
        "field_count": 1400,
        "exact_field_match_count": 212,
        "tolerated_numeric_difference_count": 11,
        "blocking_numeric_difference_count": 1177,
        "open_field_question_count": 0,
    },
}


@dataclass(frozen=True)
class Historical500VUSK1DeliveryIssue:
    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class Historical500VUSK1DeliveryTarget:
    reference_filename: str
    reference_path: str
    reference_sha256: str
    period_start: int
    period_end: int
    layer_id: str
    coherence_class: str
    allowed_claim: str
    matched_rows: int
    mismatched_rows: int
    field_count: int
    exact_field_match_count: int
    tolerated_numeric_difference_count: int
    blocking_numeric_difference_count: int
    open_field_question_count: int
    fields_with_differences: tuple[str, ...]

    @property
    def period_count(self) -> int:
        return self.period_end - self.period_start + 1

    @property
    def run_index(self) -> int:
        return (self.period_start - 1) // HISTORICAL_PERIODS_PER_RUN + 1

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": EXPORT_FILENAME,
            "reference_filename": self.reference_filename,
            "reference_path": self.reference_path,
            "reference_sha256": self.reference_sha256,
            "subject_type": "insurer",
            "level": "IV",
            "selector_kind": "all",
            "selector_value": "SK1",
            "result_row_start": self.period_start,
            "result_row_end": self.period_end,
            "result_row_count": self.period_count,
            "run_index": self.run_index,
            "local_period_start": 1,
            "local_period_end": HISTORICAL_PERIODS_PER_RUN,
            "numbering_semantics": "cumulative_result_rows_across_100_period_runs",
            "layer_id": self.layer_id,
            "coherence_class": self.coherence_class,
            "allowed_claim": self.allowed_claim,
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
class Historical500VUSK1DeliveryResult:
    root: str
    targets: tuple[Historical500VUSK1DeliveryTarget, ...]
    production_report: ProductionReleaseCorpusReport
    run_seeds: tuple[int, ...]
    controlled_execution_performed: bool
    issues: tuple[Historical500VUSK1DeliveryIssue, ...]
    mode: str = "historical_500_row_vusk1_repeat_diagnostics"

    @property
    def status(self) -> str:
        return "ready" if not self.issues else "error"

    def to_dict(self) -> dict[str, object]:
        production = self.production_report.to_dict()
        compared_rows = sum(target.period_count for target in self.targets)
        matched_rows = sum(target.matched_rows for target in self.targets)
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "root": self.root,
            "calculation_origin": CALCULATION_ORIGIN,
            "source_contracts": [
                "pr91-v1",
                "pr93-v1",
                "pr98-v1",
            ],
            "controlled_base_seed": CONTROLLED_BASE_SEED,
            "controlled_run_seeds": list(self.run_seeds),
            "historical_run_count": HISTORICAL_RUN_COUNT,
            "historical_periods_per_run": HISTORICAL_PERIODS_PER_RUN,
            "historical_result_row_count": 500,
            "repeat_corpus_policy_id": REPEAT_CORPUS_POLICY_ID,
            "current_delivery_export_count": 1 if self.targets else 0,
            "current_delivery_reference_test_count": len(self.targets),
            "current_delivery_period_count": compared_rows,
            "cumulative_delivered_export_count": production[
                "supplied_calculated_export_count"
            ],
            "cumulative_delivered_period_count": production[
                "supplied_calculated_period_count"
            ],
            "required_export_count": production["required_calculated_export_count"],
            "missing_export_count": production["missing_calculated_export_count"],
            "missing_period_count": production["missing_calculated_period_count"],
            "targets": [target.to_dict() for target in self.targets],
            "prefix_validation_status": "not_applicable_repeated_runs",
            "prefix_snapshot_count": 0,
            "prefix_comparison_count": 0,
            "prefix_compared_row_count": 0,
            "historical_comparison_status": (
                "documented_differences"
                if self.targets and matched_rows != compared_rows
                else "matches"
                if self.targets
                else "not_available"
            ),
            "historical_comparison_performed": bool(self.targets),
            "historical_comparison_matches": (
                matched_rows == compared_rows if self.targets else None
            ),
            "historical_compared_row_count": compared_rows,
            "historical_matched_row_count": matched_rows,
            "historical_mismatched_row_count": compared_rows - matched_rows,
            "historical_compared_field_count": sum(
                target.field_count for target in self.targets
            ),
            "historical_exact_field_match_count": sum(
                target.exact_field_match_count for target in self.targets
            ),
            "historical_tolerated_numeric_difference_count": sum(
                target.tolerated_numeric_difference_count for target in self.targets
            ),
            "historical_blocking_numeric_difference_count": sum(
                target.blocking_numeric_difference_count for target in self.targets
            ),
            "historical_open_field_question_count": sum(
                target.open_field_question_count for target in self.targets
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


def build_historical_500_period_vusk1_delivery(
    root: Path | str = ".",
    *,
    repeat_corpus: Vdefmd6RepeatCorpusResult | None = None,
    repeat_tables: Sequence[ExportTable] | None = None,
) -> Historical500VUSK1DeliveryResult:
    resolved_root = Path(root).expanduser().resolve()
    issues: list[Historical500VUSK1DeliveryIssue] = []
    horizon_contract = build_historical_horizon_contract(resolved_root)
    entry = _validate_horizon_contract(horizon_contract, issues)

    controlled_execution = repeat_corpus is None
    corpus = repeat_corpus or _run_controlled_repetitions(issues)
    _validate_repeat_corpus(corpus, issues)
    table_500 = _validate_calculated_tables(
        "repeat_corpus",
        tuple(
            repeat_tables
            if repeat_tables is not None
            else _select_vusk1_tables(corpus)
        ),
        500,
        entry,
        issues,
    )
    targets = _compare_historical_targets(
        resolved_root,
        horizon_contract,
        entry,
        table_500,
        issues,
    )
    cumulative_tables = _collect_cumulative_tables(
        corpus,
        table_500,
        issues,
    )
    production_report = build_production_release_corpus_report(
        resolved_root,
        calculated_export_tables=cumulative_tables,
        calculation_origin=CALCULATION_ORIGIN,
    )
    _validate_production_delivery(production_report, issues)
    return Historical500VUSK1DeliveryResult(
        root=str(resolved_root),
        targets=targets,
        production_report=production_report,
        run_seeds=corpus.run_seeds if corpus is not None else (),
        controlled_execution_performed=controlled_execution,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_500_period_vusk1_delivery",
        description=(
            "Vergleicht imsvusk1.dat mit fuenf getrennten historischen "
            "SK1/all-Zeitfenstern und haelt die Produktionsfreigabe gesperrt."
        ),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    result = build_historical_500_period_vusk1_delivery(args.root)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.status == "ready" else 1


def _validate_horizon_contract(
    contract: HistoricalHorizonContractResult,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> HistoricalHorizonExportContract | None:
    if contract.status != "ready":
        _issue(
            issues,
            "horizon_contract_not_ready",
            contract.fixture_path,
            "PR98 repeat-corpus contract must be ready",
        )
    matches = [entry for entry in contract.entries if entry.filename == EXPORT_FILENAME]
    if len(matches) != 1:
        _issue(
            issues,
            "horizon_target_set_mismatch",
            contract.fixture_path,
            "PR98 requires exactly one imsvusk1.dat result-row target",
        )
        return None
    entry = matches[0]
    expected_slices = (
        ("VUSK1L5.DAT", 1, 100, "wvemod2_archive", "archive_family_only"),
        (
            "VUSK1L4.DAT",
            101,
            200,
            "vusk1l4_direct_04410ef",
            "contradictory_or_unresolved",
        ),
        ("VUSK1L3.DAT", 201, 300, "wvemod2_archive", "archive_family_only"),
        ("VUSK1L2.DAT", 301, 400, "wvemod2_archive", "archive_family_only"),
        ("VUSK1L1.DAT", 401, 500, "wvemod2_archive", "archive_family_only"),
    )
    actual_slices = tuple(
        (
            item.reference_filename,
            item.period_start,
            item.period_end,
            item.layer_id,
            item.coherence_class,
        )
        for item in entry.reference_slices
    )
    if (
        entry.identity != ("insurer", "IV", "all", "SK1")
        or entry.required_horizon != 500
        or entry.required_period_count != 500
        or entry.required_run_count != HISTORICAL_RUN_COUNT
        or entry.layer_ids != ("wvemod2_archive", "vusk1l4_direct_04410ef")
        or entry.allowed_claims
        != ("archive_content_match_only", "versioned_fixture_regression_only")
        or actual_slices != expected_slices
    ):
        _issue(
            issues,
            "horizon_layer_boundary_mismatch",
            EXPORT_FILENAME,
            "repeat corpus must preserve five SK1/all runs and the isolated L4 layer",
        )
    return entry


def _run_controlled_repetitions(
    issues: list[Historical500VUSK1DeliveryIssue],
) -> Vdefmd6RepeatCorpusResult | None:
    try:
        return run_vdefmd6_100_period_repetitions(
            base_seed=CONTROLLED_BASE_SEED,
            run_count=HISTORICAL_RUN_COUNT,
        )
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "controlled_repeat_corpus_failed", "Vdefmd6@5x100", str(error))
        return None


def _validate_repeat_corpus(
    corpus: Vdefmd6RepeatCorpusResult | None,
    issues: list[Historical500VUSK1DeliveryIssue],
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
        or corpus.result_row_count != 500
        or corpus.run_seeds != expected_seeds
        or corpus.policy_id != REPEAT_CORPUS_POLICY_ID
    ):
        _issue(
            issues,
            "repeat_corpus_boundary_mismatch",
            "Vdefmd6@5x100",
            "controlled corpus must contain five independent 100-period runs",
        )


def _select_vusk1_tables(
    corpus: Vdefmd6RepeatCorpusResult | None,
) -> tuple[ExportTable, ...]:
    if corpus is None:
        return ()
    return tuple(
        table
        for table in corpus.export_tables
        if table.spec.filename.lower() == EXPORT_FILENAME
    )


def _validate_calculated_tables(
    name: str,
    tables: Sequence[ExportTable],
    horizon: int,
    entry: HistoricalHorizonExportContract | None,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> ExportTable | None:
    grouped: dict[str, list[ExportTable]] = {}
    for table in tables:
        grouped.setdefault(table.spec.filename.lower(), []).append(table)
    if set(grouped) != {EXPORT_FILENAME} or len(grouped[EXPORT_FILENAME]) != 1:
        _issue(
            issues,
            f"{name}_target_set_mismatch",
            name,
            "PR97 delivery must contain imsvusk1.dat exactly once",
        )
        return None
    table = grouped[EXPORT_FILENAME][0]
    if entry is None:
        return None
    expected_identity = build_legacy_export_identity(
        EXPORT_FILENAME,
        "insurer",
        "IV",
        "all",
        "SK1",
    )
    actual_identity = build_legacy_export_identity(
        table.spec.filename,
        table.spec.subject_type,
        table.spec.level,
        table.spec.selector_kind,
        table.spec.selector_value,
    )
    valid = True
    if actual_identity != expected_identity:
        _issue(
            issues,
            f"{name}_identity_mismatch",
            EXPORT_FILENAME,
            "calculated SK1/all identity differs from the result-row contract",
        )
        valid = False
    if table.header != INSURER_HEADER:
        _issue(
            issues,
            f"{name}_header_mismatch",
            EXPORT_FILENAME,
            "calculated header differs from the insurer contract",
        )
        valid = False
    if any(len(row.values) != 13 for row in table.rows):
        _issue(
            issues,
            f"{name}_row_width_mismatch",
            EXPORT_FILENAME,
            "calculated insurer rows must contain 13 values",
        )
        valid = False
    if _table_periods(table) != list(range(1, horizon + 1)):
        _issue(
            issues,
            f"{name}_period_boundary_mismatch",
            EXPORT_FILENAME,
            f"calculated result rows must cover 1 through {horizon}",
        )
        valid = False
    return table if valid else None


def _compare_historical_targets(
    root: Path,
    contract: HistoricalHorizonContractResult,
    entry: HistoricalHorizonExportContract | None,
    table: ExportTable | None,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> tuple[Historical500VUSK1DeliveryTarget, ...]:
    if entry is None or table is None:
        return ()
    try:
        fixture_targets = load_legacy_validation_targets_from_fixture(
            contract.fixture_path
        )
    except (OSError, UnicodeError, ValueError) as error:
        _issue(issues, "legacy_bundle_invalid", contract.fixture_path, str(error))
        return ()
    selected = [
        target for target in fixture_targets if target.export_filename == EXPORT_FILENAME
    ]
    by_name = {target.legacy_path.name: target for target in selected}
    if len(selected) != 5 or set(by_name) != set(REFERENCE_FILENAMES):
        _issue(
            issues,
            "legacy_target_set_mismatch",
            contract.fixture_path,
            "legacy bundle must contain the five 100-run result blocks exactly once",
        )
        return ()
    slices = {item.reference_filename: item for item in entry.reference_slices}
    delivery_targets: list[Historical500VUSK1DeliveryTarget] = []
    for reference_filename in REFERENCE_FILENAMES:
        target = by_name[reference_filename]
        reference_slice = slices[reference_filename]
        delivery = _compare_historical_target(
            root,
            table,
            target,
            reference_slice,
            issues,
        )
        if delivery is not None:
            _validate_expected_comparison(delivery, issues)
            delivery_targets.append(delivery)
    if len(delivery_targets) == 5:
        matched = sum(target.matched_rows for target in delivery_targets)
        rows = sum(target.period_count for target in delivery_targets)
        if rows != 500 or matched != 4:
            _issue(
                issues,
                "historical_comparison_summary_mismatch",
                EXPORT_FILENAME,
                "repeat diagnostic must cover 500 rows with four initial-state matches",
            )
    return tuple(delivery_targets)


def _compare_historical_target(
    root: Path,
    table: ExportTable,
    target: LegacyValidationTarget,
    reference_slice: HistoricalHorizonReferenceSlice,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> Historical500VUSK1DeliveryTarget | None:
    filename = target.legacy_path.name
    expected_path = (root / EXPECTED_REFERENCE_PATHS[filename]).resolve()
    if target.legacy_path.resolve() != expected_path:
        _issue(
            issues,
            "legacy_reference_path_mismatch",
            filename,
            "PR97 reference path differs from the versioned contract",
        )
    try:
        digest = hashlib.sha256(target.legacy_path.read_bytes()).hexdigest()
    except OSError as error:
        _issue(issues, "legacy_reference_unreadable", filename, str(error))
        return None
    if digest != REFERENCE_SHA256[filename]:
        _issue(
            issues,
            "legacy_reference_hash_mismatch",
            filename,
            "PR97 reference hash differs from its PR91 layer binding",
        )
    expected_periods = list(
        range(reference_slice.period_start, reference_slice.period_end + 1)
    )
    if (
        target.subject_type != "insurer"
        or target.level != "IV"
        or target.selector_kind != "all"
        or target.selector_value != "SK1"
        or target.periods != expected_periods
    ):
        _issue(
            issues,
            "legacy_reference_contract_mismatch",
            filename,
            "legacy target identity or 100-row run boundary differs",
        )
    sliced_table = ExportTable(
        spec=table.spec,
        header=table.header,
        rows=[
            row
            for row in table.rows
            if reference_slice.period_start
            <= int(row.values[0])
            <= reference_slice.period_end
        ],
    )
    try:
        legacy_table = parse_legacy_insurer_dat(target.legacy_path)
        if [row.global_period for row in legacy_table.rows] != expected_periods:
            raise ValueError("legacy reference periods differ from the declared window")
        comparison = compare_insurer_export_table_to_legacy(
            sliced_table,
            legacy_table,
            require_complete_legacy_periods=True,
        )
    except (OSError, UnicodeError, TypeError, ValueError) as error:
        _issue(issues, "historical_comparison_failed", filename, str(error))
        return None
    counts = _field_counts(comparison)
    matched_rows = sum(row.matches for row in comparison.row_comparisons)
    return Historical500VUSK1DeliveryTarget(
        reference_filename=filename,
        reference_path=str(target.legacy_path.resolve()),
        reference_sha256=digest,
        period_start=reference_slice.period_start,
        period_end=reference_slice.period_end,
        layer_id=reference_slice.layer_id,
        coherence_class=reference_slice.coherence_class,
        allowed_claim=reference_slice.allowed_claim,
        matched_rows=matched_rows,
        mismatched_rows=len(comparison.row_comparisons) - matched_rows,
        fields_with_differences=tuple(
            dict.fromkeys(
                field.name
                for row in comparison.row_comparisons
                for field in row.field_comparisons
                if not field.matches
            )
        ),
        **counts,
    )


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
    target: Historical500VUSK1DeliveryTarget,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> None:
    actual = {
        key: getattr(target, key)
        for key in EXPECTED_COMPARISON[target.reference_filename]
    }
    if actual != EXPECTED_COMPARISON[target.reference_filename]:
        _issue(
            issues,
            "historical_observation_fingerprint_mismatch",
            target.reference_filename,
            "calculated-to-historical field observation changed",
        )


def _collect_cumulative_tables(
    corpus: Vdefmd6RepeatCorpusResult | None,
    table_500: ExportTable | None,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> tuple[ExportTable, ...]:
    selected: list[ExportTable] = []
    if corpus is not None:
        baseline_100 = corpus.runs[0]
        selected.append(baseline_100.vu14_export_table)
        _append_named_table(
            selected,
            baseline_100.vn_aggregate_export_tables,
            "imsvnsk1.dat",
            issues,
        )
        for filename in ("imsvnr01.dat", "imsvnr02.dat"):
            _append_named_table(
                selected,
                corpus.export_tables,
                filename,
                issues,
                row_count=300,
            )
    if table_500 is not None:
        selected.append(table_500)
    return tuple(selected)


def _append_named_table(
    selected: list[ExportTable],
    tables: Sequence[ExportTable],
    filename: str,
    issues: list[Historical500VUSK1DeliveryIssue],
    *,
    row_count: int | None = None,
) -> None:
    matches = [table for table in tables if table.spec.filename.lower() == filename]
    if len(matches) != 1:
        _issue(
            issues,
            "cumulative_delivery_target_missing",
            filename,
            "earlier cumulative delivery target is missing or duplicated",
        )
        return
    table = matches[0]
    selected.append(
        table
        if row_count is None
        else ExportTable(
            spec=table.spec,
            header=table.header,
            rows=list(table.rows[:row_count]),
        )
    )


def _validate_production_delivery(
    report: ProductionReleaseCorpusReport,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> None:
    expected = {
        "supplied_calculated_export_count": 5,
        "supplied_calculated_period_count": 1300,
        "missing_calculated_export_count": 10,
        "missing_calculated_period_count": 5000,
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
            "production report did not accept the five cumulative targets",
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
    issues: list[Historical500VUSK1DeliveryIssue],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(Historical500VUSK1DeliveryIssue(code, path, message))


if __name__ == "__main__":
    raise SystemExit(main())
