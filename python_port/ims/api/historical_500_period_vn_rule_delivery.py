from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

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
from ims.model.agrsich_export import INSURER_HEADER, POLICYHOLDER_HEADER, ExportTable
from ims.model.legacy_agrsich_multi_period import (
    LegacyTableComparison,
    compare_insurer_export_table_to_legacy,
    compare_policyholder_export_table_to_legacy,
)
from ims.model.legacy_agrsich_reference import parse_legacy_insurer_dat
from ims.model.legacy_export_identity import build_legacy_export_identity
from ims.model.legacy_validation_run import (
    LegacyValidationTarget,
    load_legacy_validation_targets_from_fixture,
)
from ims.model.legacy_vn_reference import parse_legacy_policyholder_dat


CONTRACT_VERSION = "pr99-v1"
CONTROLLED_BASE_SEED = 20260001
HISTORICAL_RUN_COUNT = 5
CALCULATION_ORIGIN = "vdefmd6_controlled_5x100_vn_rule_diagnostics_pr99"
RULE_FILENAMES = (
    "imsvnr03.dat",
    "imsvnr04.dat",
    "imsvnr05.dat",
    "imsvnr06.dat",
)
CUMULATIVE_ROW_COUNTS = {
    "imsvu014.dat": 100,
    "imsvnsk1.dat": 100,
    "imsvnr01.dat": 300,
    "imsvnr02.dat": 300,
    "imsvusk1.dat": 500,
    **{filename: 500 for filename in RULE_FILENAMES},
}
EXPECTED_REFERENCE_PATHS = {
    filename: Path("tests/references/legacy_agrsich") / filename.upper()
    for filename in RULE_FILENAMES
}
REFERENCE_SHA256 = {
    "imsvnr03.dat": (
        "8491bec0736fbf4fb95c9b7649338d0142207265024ec5c5e9c3e649bd49ffd4"
    ),
    "imsvnr04.dat": (
        "16bdf0b4329ec414990aaaec2ece0d48a8001b43d4a6bb8210625cfb56f3fce4"
    ),
    "imsvnr05.dat": (
        "80a83f47de5451cb9b660025ca3c0e511aa268602b0ced2301f82b4467549dfa"
    ),
    "imsvnr06.dat": (
        "1d18b3ce471f4b19f525956650b414e1fcfb8b93854eaaf60c8316b18b1eced0"
    ),
}
EXPECTED_COMPARISON = {
    "imsvnr03.dat": {
        "period_count": 500,
        "matched_rows": 0,
        "mismatched_rows": 500,
        "field_count": 6500,
        "exact_field_match_count": 1434,
        "tolerated_numeric_difference_count": 447,
        "blocking_numeric_difference_count": 4239,
        "open_field_question_count": 380,
    },
    "imsvnr04.dat": {
        "period_count": 500,
        "matched_rows": 0,
        "mismatched_rows": 500,
        "field_count": 6500,
        "exact_field_match_count": 1028,
        "tolerated_numeric_difference_count": 316,
        "blocking_numeric_difference_count": 4552,
        "open_field_question_count": 604,
    },
    "imsvnr05.dat": {
        "period_count": 500,
        "matched_rows": 0,
        "mismatched_rows": 500,
        "field_count": 6500,
        "exact_field_match_count": 1038,
        "tolerated_numeric_difference_count": 19,
        "blocking_numeric_difference_count": 5433,
        "open_field_question_count": 10,
    },
    "imsvnr06.dat": {
        "period_count": 500,
        "matched_rows": 0,
        "mismatched_rows": 500,
        "field_count": 6500,
        "exact_field_match_count": 2178,
        "tolerated_numeric_difference_count": 27,
        "blocking_numeric_difference_count": 4285,
        "open_field_question_count": 10,
    },
}


@dataclass(frozen=True)
class Historical500AggregateDeliveryProfile:
    contract_version: str
    calculation_origin: str
    mode: str
    source_contracts: tuple[str, ...]
    target_label: str
    summary_path: str
    filenames: tuple[str, ...]
    subject_type: str
    level: str
    selector_kind: str
    expected_header: str
    expected_row_width: int
    layer_ids: tuple[str, ...]
    allowed_claims: tuple[str, ...]
    expected_reference_paths: Mapping[str, Path]
    reference_sha256: Mapping[str, str]
    expected_comparison: Mapping[str, Mapping[str, int]]
    cumulative_row_counts: Mapping[str, int]


Historical500PolicyholderDeliveryProfile = Historical500AggregateDeliveryProfile


VN_RULE_PROFILE = Historical500AggregateDeliveryProfile(
    contract_version=CONTRACT_VERSION,
    calculation_origin=CALCULATION_ORIGIN,
    mode="historical_500_row_vn_rule_repeat_diagnostics",
    source_contracts=("pr91-v1", "pr98-v1", "pr99-v1"),
    target_label="PR99 VN rule",
    summary_path="IMSVNR03-06",
    filenames=RULE_FILENAMES,
    subject_type="policyholder",
    level="II",
    selector_kind="rule",
    expected_header=POLICYHOLDER_HEADER,
    expected_row_width=12,
    layer_ids=("wvemod1_archive",),
    allowed_claims=("archive_content_match_only",),
    expected_reference_paths=EXPECTED_REFERENCE_PATHS,
    reference_sha256=REFERENCE_SHA256,
    expected_comparison=EXPECTED_COMPARISON,
    cumulative_row_counts=CUMULATIVE_ROW_COUNTS,
)


@dataclass(frozen=True)
class Historical500VNRuleDeliveryIssue:
    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class Historical500VNRuleDeliveryTarget:
    filename: str
    reference_path: str
    reference_sha256: str
    subject_type: str
    level: str
    selector_kind: str
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
            "subject_type": self.subject_type,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "layer_ids": list(self.layer_ids),
            "allowed_claims": list(self.allowed_claims),
            "result_row_start": 1,
            "result_row_end": self.period_count,
            "result_row_count": self.period_count,
            "run_start": 1,
            "run_end": HISTORICAL_RUN_COUNT,
            "local_period_start": 1,
            "local_period_end": HISTORICAL_PERIODS_PER_RUN,
            "numbering_semantics": (
                "cumulative_result_rows_across_100_period_runs"
            ),
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
class Historical500VNRuleDeliveryResult:
    root: str
    targets: tuple[Historical500VNRuleDeliveryTarget, ...]
    production_report: ProductionReleaseCorpusReport
    run_seeds: tuple[int, ...]
    controlled_execution_performed: bool
    issues: tuple[Historical500VNRuleDeliveryIssue, ...]
    profile: Historical500AggregateDeliveryProfile

    @property
    def status(self) -> str:
        return "ready" if not self.issues else "error"

    def to_dict(self) -> dict[str, object]:
        production = self.production_report.to_dict()
        compared_rows = sum(target.period_count for target in self.targets)
        matched_rows = sum(target.matched_rows for target in self.targets)
        return {
            "status": self.status,
            "mode": self.profile.mode,
            "contract_version": self.profile.contract_version,
            "root": self.root,
            "calculation_origin": self.profile.calculation_origin,
            "source_contracts": list(self.profile.source_contracts),
            "controlled_base_seed": CONTROLLED_BASE_SEED,
            "controlled_run_seeds": list(self.run_seeds),
            "historical_run_count": HISTORICAL_RUN_COUNT,
            "historical_periods_per_run": HISTORICAL_PERIODS_PER_RUN,
            "historical_result_row_count": 500,
            "repeat_corpus_policy_id": REPEAT_CORPUS_POLICY_ID,
            "current_delivery_export_count": len(self.targets),
            "current_delivery_period_count": compared_rows,
            "cumulative_delivered_export_count": production[
                "supplied_calculated_export_count"
            ],
            "cumulative_delivered_period_count": production[
                "supplied_calculated_period_count"
            ],
            "required_export_count": production[
                "required_calculated_export_count"
            ],
            "missing_export_count": production["missing_calculated_export_count"],
            "missing_period_count": production["missing_calculated_period_count"],
            "targets": [target.to_dict() for target in self.targets],
            "prefix_validation_status": "not_applicable_repeated_runs",
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
            "historical_parameterization_match_claimed": False,
            "historical_rng_reproduction_required": False,
            "historical_rng_equality_claimed": False,
            "historical_full_equality_claimed": False,
            "production_release_approved": False,
        }


def build_historical_500_period_vn_rule_delivery(
    root: Path | str = ".",
    *,
    repeat_corpus: Vdefmd6RepeatCorpusResult | None = None,
    repeat_rule_tables: Sequence[ExportTable] | None = None,
) -> Historical500VNRuleDeliveryResult:
    return build_historical_500_period_aggregate_delivery(
        root,
        profile=VN_RULE_PROFILE,
        repeat_corpus=repeat_corpus,
        repeat_tables=repeat_rule_tables,
    )


def build_historical_500_period_aggregate_delivery(
    root: Path | str,
    *,
    profile: Historical500AggregateDeliveryProfile,
    repeat_corpus: Vdefmd6RepeatCorpusResult | None = None,
    repeat_tables: Sequence[ExportTable] | None = None,
) -> Historical500VNRuleDeliveryResult:
    resolved_root = Path(root).expanduser().resolve()
    issues: list[Historical500VNRuleDeliveryIssue] = []
    horizon_contract = build_historical_horizon_contract(resolved_root)
    entries = _validate_horizon_contract(horizon_contract, issues, profile)

    controlled_execution = repeat_corpus is None
    corpus = repeat_corpus or _run_controlled_repetitions(issues)
    _validate_repeat_corpus(corpus, issues)
    repeated_tables = tuple(
        repeat_tables
        if repeat_tables is not None
        else _select_aggregate_tables(corpus, profile)
    )
    valid_tables = _validate_aggregate_tables(
        repeated_tables,
        entries,
        issues,
        profile,
    )
    targets = _compare_historical_targets(
        resolved_root,
        horizon_contract,
        valid_tables,
        entries,
        issues,
        profile,
    )
    cumulative_tables = _collect_cumulative_tables(
        corpus,
        valid_tables,
        issues,
        profile,
    )
    production_report = build_production_release_corpus_report(
        resolved_root,
        calculated_export_tables=cumulative_tables,
        calculation_origin=profile.calculation_origin,
    )
    _validate_production_delivery(production_report, issues, profile)
    return Historical500VNRuleDeliveryResult(
        root=str(resolved_root),
        targets=targets,
        production_report=production_report,
        run_seeds=corpus.run_seeds if corpus is not None else (),
        controlled_execution_performed=controlled_execution,
        issues=tuple(issues),
        profile=profile,
    )


def build_historical_500_period_policyholder_delivery(
    root: Path | str,
    *,
    profile: Historical500AggregateDeliveryProfile,
    repeat_corpus: Vdefmd6RepeatCorpusResult | None = None,
    repeat_tables: Sequence[ExportTable] | None = None,
) -> Historical500VNRuleDeliveryResult:
    return build_historical_500_period_aggregate_delivery(
        root,
        profile=profile,
        repeat_corpus=repeat_corpus,
        repeat_tables=repeat_tables,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_500_period_vn_rule_delivery",
        description=(
            "Vergleicht vier WVEMOD1-VN-Regeltabellen mit je fuenf getrennten "
            "100-Perioden-Laeufen und haelt die Produktionsfreigabe gesperrt."
        ),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    result = build_historical_500_period_vn_rule_delivery(args.root)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.status == "ready" else 1


def _run_controlled_repetitions(
    issues: list[Historical500VNRuleDeliveryIssue],
) -> Vdefmd6RepeatCorpusResult | None:
    try:
        return run_vdefmd6_100_period_repetitions(
            base_seed=CONTROLLED_BASE_SEED,
            run_count=HISTORICAL_RUN_COUNT,
        )
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "controlled_repeat_corpus_failed", "Vdefmd6@5x100", str(error))
        return None


def _validate_horizon_contract(
    contract: HistoricalHorizonContractResult,
    issues: list[Historical500VNRuleDeliveryIssue],
    profile: Historical500AggregateDeliveryProfile,
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
        if entry.filename in profile.filenames
    }
    if set(entries) != set(profile.filenames):
        _issue(
            issues,
            "horizon_target_set_mismatch",
            contract.fixture_path,
            f"500-row targets differ from the {profile.target_label} set",
        )
    for filename, entry in entries.items():
        if (
            entry.subject_type != profile.subject_type
            or entry.level != profile.level
            or entry.selector_kind != profile.selector_kind
            or entry.required_horizon != 500
            or entry.required_run_count != HISTORICAL_RUN_COUNT
            or entry.layer_ids != profile.layer_ids
            or entry.allowed_claims != profile.allowed_claims
        ):
            _issue(
                issues,
                "horizon_layer_boundary_mismatch",
                filename,
                f"{profile.target_label} targets changed layer or identity",
            )
    return entries


def _validate_repeat_corpus(
    corpus: Vdefmd6RepeatCorpusResult | None,
    issues: list[Historical500VNRuleDeliveryIssue],
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


def _select_aggregate_tables(
    corpus: Vdefmd6RepeatCorpusResult | None,
    profile: Historical500AggregateDeliveryProfile,
) -> tuple[ExportTable, ...]:
    if corpus is None:
        return ()
    return tuple(
        table
        for table in corpus.export_tables
        if table.spec.filename.lower() in profile.filenames
    )


def _validate_aggregate_tables(
    tables: Sequence[ExportTable],
    entries: dict[str, HistoricalHorizonExportContract],
    issues: list[Historical500VNRuleDeliveryIssue],
    profile: Historical500AggregateDeliveryProfile,
) -> dict[str, ExportTable]:
    grouped: dict[str, list[ExportTable]] = {}
    for table in tables:
        grouped.setdefault(table.spec.filename.lower(), []).append(table)
    if set(grouped) != set(profile.filenames) or any(
        len(items) != 1 for items in grouped.values()
    ):
        _issue(
            issues,
            "repeat_corpus_target_set_mismatch",
            "repeat_corpus",
            f"delivery must contain every {profile.target_label} target once",
        )
    valid: dict[str, ExportTable] = {}
    for filename in profile.filenames:
        matches = grouped.get(filename, ())
        entry = entries.get(filename)
        if len(matches) != 1 or entry is None:
            continue
        table = matches[0]
        expected_identity = build_legacy_export_identity(
            filename,
            profile.subject_type,
            profile.level,
            profile.selector_kind,
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
                "repeat_corpus_identity_mismatch",
                filename,
                f"calculated identity differs from the {profile.target_label} contract",
            )
            table_valid = False
        if table.header != profile.expected_header:
            _issue(
                issues,
                "repeat_corpus_header_mismatch",
                filename,
                f"calculated header differs from the {profile.subject_type} contract",
            )
            table_valid = False
        if any(len(row.values) != profile.expected_row_width for row in table.rows):
            _issue(
                issues,
                "repeat_corpus_row_width_mismatch",
                filename,
                (
                    f"calculated {profile.subject_type} rows must contain "
                    f"{profile.expected_row_width} values"
                ),
            )
            table_valid = False
        if periods != list(range(1, 501)):
            _issue(
                issues,
                "repeat_corpus_period_boundary_mismatch",
                filename,
                "calculated result rows must cover 1 through 500",
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
    issues: list[Historical500VNRuleDeliveryIssue],
    profile: Historical500AggregateDeliveryProfile,
) -> tuple[Historical500VNRuleDeliveryTarget, ...]:
    try:
        fixture_targets = load_legacy_validation_targets_from_fixture(
            contract.fixture_path
        )
    except (OSError, UnicodeError, ValueError) as error:
        _issue(issues, "legacy_bundle_invalid", contract.fixture_path, str(error))
        return ()
    selected = [
        target
        for target in fixture_targets
        if target.export_filename in profile.filenames
    ]
    targets = {target.export_filename: target for target in selected}
    if len(selected) != len(profile.filenames) or set(targets) != set(
        profile.filenames
    ):
        _issue(
            issues,
            "legacy_target_set_mismatch",
            contract.fixture_path,
            f"legacy bundle must contain every {profile.target_label} target once",
        )
        return ()

    delivery_targets: list[Historical500VNRuleDeliveryTarget] = []
    for filename in profile.filenames:
        target = targets[filename]
        table = tables.get(filename)
        entry = entries.get(filename)
        expected_path = (
            root / profile.expected_reference_paths[filename]
        ).resolve()
        if target.legacy_path.resolve() != expected_path:
            _issue(
                issues,
                "legacy_reference_path_mismatch",
                filename,
                f"{profile.target_label} path differs from the versioned contract",
            )
        try:
            digest = hashlib.sha256(target.legacy_path.read_bytes()).hexdigest()
        except OSError as error:
            _issue(issues, "legacy_reference_unreadable", filename, str(error))
            continue
        if digest != profile.reference_sha256[filename]:
            _issue(
                issues,
                "legacy_reference_hash_mismatch",
                filename,
                f"{profile.target_label} hash differs from the archive contract",
            )
        if not _legacy_target_matches_contract(target, entry, profile):
            _issue(
                issues,
                "legacy_reference_contract_mismatch",
                filename,
                "legacy target identity or 500-result-row boundary differs",
            )
        if table is None or entry is None:
            continue
        try:
            comparison = _compare_export_table_to_legacy(
                table,
                target.legacy_path,
                profile.subject_type,
            )
        except (OSError, UnicodeError, TypeError, ValueError) as error:
            _issue(issues, "historical_comparison_failed", filename, str(error))
            continue
        delivery_target = _build_delivery_target(
            target,
            entry,
            digest,
            comparison,
            profile,
        )
        _validate_expected_comparison(delivery_target, issues, profile)
        delivery_targets.append(delivery_target)
    expected_matched_rows = sum(
        values["matched_rows"] for values in profile.expected_comparison.values()
    )
    if len(delivery_targets) != len(profile.filenames) or sum(
        target.matched_rows for target in delivery_targets
    ) != expected_matched_rows:
        _issue(
            issues,
            "historical_comparison_summary_mismatch",
            profile.summary_path,
            (
                f"{profile.target_label} observation must cover "
                f"{500 * len(profile.filenames):,} frozen comparison rows"
            ),
        )
    return tuple(delivery_targets)


def _compare_export_table_to_legacy(
    table: ExportTable,
    reference_path: Path,
    subject_type: str,
) -> LegacyTableComparison:
    if subject_type == "insurer":
        return compare_insurer_export_table_to_legacy(
            table,
            parse_legacy_insurer_dat(reference_path),
            require_complete_legacy_periods=True,
        )
    if subject_type == "policyholder":
        return compare_policyholder_export_table_to_legacy(
            table,
            parse_legacy_policyholder_dat(reference_path),
            require_complete_legacy_periods=True,
        )
    raise ValueError(f"unsupported historical subject type: {subject_type}")


def _legacy_target_matches_contract(
    target: LegacyValidationTarget,
    entry: HistoricalHorizonExportContract | None,
    profile: Historical500AggregateDeliveryProfile,
) -> bool:
    return bool(
        entry is not None
        and target.subject_type == profile.subject_type
        and target.level == profile.level
        and target.selector_kind == profile.selector_kind
        and target.selector_value == entry.selector_value
        and target.periods == list(range(1, 501))
    )


def _build_delivery_target(
    target: LegacyValidationTarget,
    entry: HistoricalHorizonExportContract,
    digest: str,
    comparison: LegacyTableComparison,
    profile: Historical500AggregateDeliveryProfile,
) -> Historical500VNRuleDeliveryTarget:
    counts = _field_counts(comparison)
    matched_rows = sum(row.matches for row in comparison.row_comparisons)
    fields_with_differences = tuple(
        sorted(
            {
                field.name
                for row in comparison.row_comparisons
                for field in row.field_comparisons
                if not field.matches
            }
        )
    )
    return Historical500VNRuleDeliveryTarget(
        filename=target.export_filename,
        reference_path=str(target.legacy_path.resolve()),
        reference_sha256=digest,
        subject_type=profile.subject_type,
        level=profile.level,
        selector_kind=profile.selector_kind,
        selector_value=int(target.selector_value),
        layer_ids=entry.layer_ids,
        allowed_claims=entry.allowed_claims,
        period_count=len(comparison.row_comparisons),
        matched_rows=matched_rows,
        mismatched_rows=len(comparison.row_comparisons) - matched_rows,
        fields_with_differences=fields_with_differences,
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
    target: Historical500VNRuleDeliveryTarget,
    issues: list[Historical500VNRuleDeliveryIssue],
    profile: Historical500AggregateDeliveryProfile,
) -> None:
    actual = {
        key: getattr(target, key)
        for key in profile.expected_comparison[target.filename]
    }
    if actual != profile.expected_comparison[target.filename]:
        _issue(
            issues,
            "historical_observation_fingerprint_mismatch",
            target.filename,
            "calculated-to-historical field observation changed",
        )


def _collect_cumulative_tables(
    corpus: Vdefmd6RepeatCorpusResult | None,
    current_tables: dict[str, ExportTable],
    issues: list[Historical500VNRuleDeliveryIssue],
    profile: Historical500AggregateDeliveryProfile,
) -> tuple[ExportTable, ...]:
    if corpus is None:
        return tuple(current_tables.values())
    grouped = {
        filename: [
            table
            for table in corpus.export_tables
            if table.spec.filename.lower() == filename
        ]
        for filename in profile.cumulative_row_counts
    }
    selected: list[ExportTable] = []
    for filename, row_count in profile.cumulative_row_counts.items():
        matches = (
            [current_tables[filename]]
            if filename in current_tables
            else grouped[filename]
        )
        if len(matches) != 1 or len(matches[0].rows) < row_count:
            _issue(
                issues,
                "cumulative_delivery_target_missing",
                filename,
                "cumulative delivery target is missing, duplicated, or too short",
            )
            continue
        table = matches[0]
        selected.append(
            ExportTable(
                spec=table.spec,
                header=table.header,
                rows=list(table.rows[:row_count]),
            )
        )
    return tuple(selected)


def _validate_production_delivery(
    report: ProductionReleaseCorpusReport,
    issues: list[Historical500VNRuleDeliveryIssue],
    profile: Historical500AggregateDeliveryProfile,
) -> None:
    supplied_count = len(profile.cumulative_row_counts)
    supplied_periods = sum(profile.cumulative_row_counts.values())
    expected = {
        "supplied_calculated_export_count": supplied_count,
        "supplied_calculated_period_count": supplied_periods,
        "missing_calculated_export_count": 15 - supplied_count,
        "missing_calculated_period_count": 6300 - supplied_periods,
    }
    for name, value in expected.items():
        if getattr(report, name) != value:
            _issue(
                issues,
                "production_delivery_count_mismatch",
                name,
                f"expected {value}, got {getattr(report, name)}",
            )
    if set(report.supplied_calculated_exports) != set(
        profile.cumulative_row_counts
    ):
        _issue(
            issues,
            "production_delivery_target_mismatch",
            "production_release_corpus_report",
            f"production report did not accept {supplied_count} cumulative targets",
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
    issues: list[Historical500VNRuleDeliveryIssue],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(Historical500VNRuleDeliveryIssue(code, path, message))


if __name__ == "__main__":
    raise SystemExit(main())
