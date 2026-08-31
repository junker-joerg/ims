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
    VDEFMD6_500_PERIOD_STATE_POLICY_ID,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
    run_vdefmd6_300_periods,
    run_vdefmd6_500_periods,
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


CONTRACT_VERSION = "pr97-v1"
CONTROLLED_BASE_SEED = 20260001
CALCULATION_ORIGIN = "vdefmd6_controlled_100_300_500_vusk1_delivery_pr97"
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
        "exact_field_match_count": 201,
        "tolerated_numeric_difference_count": 2,
        "blocking_numeric_difference_count": 1197,
        "open_field_question_count": 0,
    },
    "VUSK1L3.DAT": {
        "period_start": 201,
        "period_end": 300,
        "matched_rows": 0,
        "mismatched_rows": 100,
        "field_count": 1400,
        "exact_field_match_count": 200,
        "tolerated_numeric_difference_count": 1,
        "blocking_numeric_difference_count": 1199,
        "open_field_question_count": 0,
    },
    "VUSK1L2.DAT": {
        "period_start": 301,
        "period_end": 400,
        "matched_rows": 0,
        "mismatched_rows": 100,
        "field_count": 1400,
        "exact_field_match_count": 202,
        "tolerated_numeric_difference_count": 5,
        "blocking_numeric_difference_count": 1193,
        "open_field_question_count": 0,
    },
    "VUSK1L1.DAT": {
        "period_start": 401,
        "period_end": 500,
        "matched_rows": 0,
        "mismatched_rows": 100,
        "field_count": 1400,
        "exact_field_match_count": 203,
        "tolerated_numeric_difference_count": 4,
        "blocking_numeric_difference_count": 1193,
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
            "period_start": self.period_start,
            "period_end": self.period_end,
            "period_count": self.period_count,
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
    prefix_validation: HistoricalPrefixValidationResult | None
    production_report: ProductionReleaseCorpusReport
    controlled_execution_performed: bool
    issues: tuple[Historical500VUSK1DeliveryIssue, ...]
    mode: str = "historical_500_period_vusk1_delivery"

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
                "pr92-v1",
                "pr93-v1",
                "pr94-v1",
                "pr95-v1",
                "pr96-v1",
            ],
            "controlled_base_seed": CONTROLLED_BASE_SEED,
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
            "prefix_validation_status": prefix.get("status", "not_available"),
            "prefix_snapshot_count": prefix.get("snapshot_count", 0),
            "prefix_comparison_count": prefix.get("comparison_count", 0),
            "prefix_compared_row_count": prefix.get("compared_row_count", 0),
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
            "historical_rng_equality_claimed": False,
            "historical_full_equality_claimed": False,
            "production_release_approved": False,
        }


def build_historical_500_period_vusk1_delivery(
    root: Path | str = ".",
    *,
    baseline_100_result: Vdefmd6PreShockRunResult | None = None,
    baseline_300_result: Vdefmd6PreShockRunResult | None = None,
    extended_result: Vdefmd6PreShockRunResult | None = None,
    baseline_100_tables: Sequence[ExportTable] | None = None,
    baseline_300_tables: Sequence[ExportTable] | None = None,
    extended_tables: Sequence[ExportTable] | None = None,
) -> Historical500VUSK1DeliveryResult:
    resolved_root = Path(root).expanduser().resolve()
    issues: list[Historical500VUSK1DeliveryIssue] = []
    horizon_contract = build_historical_horizon_contract(resolved_root)
    entry = _validate_horizon_contract(horizon_contract, issues)

    controlled_execution = (
        baseline_100_result is None
        or baseline_300_result is None
        or extended_result is None
    )
    baseline_100 = baseline_100_result or _run_controlled(100, issues)
    baseline_300 = baseline_300_result or _run_controlled(300, issues)
    extended = extended_result or _run_controlled(500, issues)
    _validate_run_boundaries(baseline_100, baseline_300, extended, issues)

    table_100 = _validate_calculated_tables(
        "baseline_100",
        tuple(
            baseline_100_tables
            if baseline_100_tables is not None
            else _select_vusk1_tables(baseline_100)
        ),
        100,
        entry,
        issues,
    )
    table_300 = _validate_calculated_tables(
        "baseline_300",
        tuple(
            baseline_300_tables
            if baseline_300_tables is not None
            else _select_vusk1_tables(baseline_300)
        ),
        300,
        entry,
        issues,
    )
    table_500 = _validate_calculated_tables(
        "extended",
        tuple(
            extended_tables
            if extended_tables is not None
            else _select_vusk1_tables(extended)
        ),
        500,
        entry,
        issues,
    )
    prefix_validation = _validate_prefixes(
        horizon_contract,
        entry,
        table_100,
        table_300,
        table_500,
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
        baseline_100,
        baseline_300,
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
        prefix_validation=prefix_validation,
        production_report=production_report,
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
            "PR92 horizon contract must be ready",
        )
    matches = [entry for entry in contract.entries if entry.filename == EXPORT_FILENAME]
    if len(matches) != 1:
        _issue(
            issues,
            "horizon_target_set_mismatch",
            contract.fixture_path,
            "PR97 requires exactly one imsvusk1.dat horizon target",
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
        or entry.prefix_checkpoints != (100, 300)
        or entry.layer_ids != ("wvemod2_archive", "vusk1l4_direct_04410ef")
        or entry.allowed_claims
        != ("archive_content_match_only", "versioned_fixture_regression_only")
        or actual_slices != expected_slices
    ):
        _issue(
            issues,
            "horizon_layer_boundary_mismatch",
            EXPORT_FILENAME,
            "PR97 must preserve five SK1/all windows and the isolated L4 layer",
        )
    return entry


def _run_controlled(
    horizon: int,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> Vdefmd6PreShockRunResult | None:
    try:
        if horizon == 100:
            return run_vdefmd6_100_periods(base_seed=CONTROLLED_BASE_SEED)
        if horizon == 300:
            return run_vdefmd6_300_periods(base_seed=CONTROLLED_BASE_SEED)
        return run_vdefmd6_500_periods(base_seed=CONTROLLED_BASE_SEED)
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "controlled_run_failed", f"Vdefmd6@{horizon}", str(error))
        return None


def _validate_run_boundaries(
    baseline_100: Vdefmd6PreShockRunResult | None,
    baseline_300: Vdefmd6PreShockRunResult | None,
    extended: Vdefmd6PreShockRunResult | None,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> None:
    if baseline_100 is None or baseline_300 is None or extended is None:
        return
    expected = (
        (
            "baseline_100",
            baseline_100,
            100,
            VDEFMD6_100_PERIOD_STATE_POLICY_ID,
        ),
        (
            "baseline_300",
            baseline_300,
            300,
            VDEFMD6_300_PERIOD_STATE_POLICY_ID,
        ),
        ("extended", extended, 500, VDEFMD6_500_PERIOD_STATE_POLICY_ID),
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
        if _crosses_closed_boundary(result):
            _issue(
                issues,
                "controlled_run_boundary_violation",
                name,
                "controlled delivery crossed an execution or historical boundary",
            )
    if baseline_100.period_results != extended.period_results[:99]:
        _issue(
            issues,
            "state_100_prefix_mismatch",
            "Vdefmd6@1-100",
            "500-period state changed the exact 100-period prefix",
        )
    if baseline_300.period_results != extended.period_results[:299]:
        _issue(
            issues,
            "state_300_prefix_mismatch",
            "Vdefmd6@1-300",
            "500-period state changed the exact 300-period prefix",
        )


def _crosses_closed_boundary(result: Vdefmd6PreShockRunResult) -> bool:
    return bool(
        result.legacy_rows_used_as_generation_input
        or result.writes_performed
        or result.scheduler_started
        or result.simulation_performed
        or result.historical_same_slot_order_claimed
        or result.historical_rng_equality_claimed
        or result.historical_full_equality_claimed
    )


def _select_vusk1_tables(
    result: Vdefmd6PreShockRunResult | None,
) -> tuple[ExportTable, ...]:
    if result is None:
        return ()
    return tuple(
        table
        for table in result.vu_aggregate_export_tables
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
            "calculated SK1/all identity differs from the horizon contract",
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
            f"calculated periods must cover 1 through {horizon}",
        )
        valid = False
    return table if valid else None


def _validate_prefixes(
    contract: HistoricalHorizonContractResult,
    entry: HistoricalHorizonExportContract | None,
    table_100: ExportTable | None,
    table_300: ExportTable | None,
    table_500: ExportTable | None,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> HistoricalPrefixValidationResult | None:
    if entry is None or table_100 is None or table_300 is None or table_500 is None:
        return None
    layer_ids = dict(entry.horizon_layer_ids)
    snapshots = tuple(
        LayeredExportTableSnapshot(horizon, layer_ids[horizon], table)
        for horizon, table in ((100, table_100), (300, table_300), (500, table_500))
    )
    result = validate_historical_horizon_prefixes(contract, snapshots)
    if (
        result.status != "ok"
        or result.snapshot_count != 3
        or result.comparison_count != 3
        or result.compared_row_count != 500
        or result.one_hundred_prefix_comparison_count != 2
    ):
        _issue(
            issues,
            "prefix_validation_failed",
            EXPORT_FILENAME,
            "PR97 requires exact 100- and 300-period prefixes",
        )
    return result


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
            "legacy bundle must contain the five PR97 windows exactly once",
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
        if rows != 500 or matched != 1:
            _issue(
                issues,
                "historical_comparison_summary_mismatch",
                EXPORT_FILENAME,
                "PR97 observation must cover 500 rows with one current full match",
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
            "legacy target identity or 100-period window differs",
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
    baseline_100: Vdefmd6PreShockRunResult | None,
    baseline_300: Vdefmd6PreShockRunResult | None,
    table_500: ExportTable | None,
    issues: list[Historical500VUSK1DeliveryIssue],
) -> tuple[ExportTable, ...]:
    selected: list[ExportTable] = []
    if baseline_100 is not None:
        selected.append(baseline_100.vu14_export_table)
        _append_named_table(
            selected,
            baseline_100.vn_aggregate_export_tables,
            "imsvnsk1.dat",
            issues,
        )
    if baseline_300 is not None:
        for filename in ("imsvnr01.dat", "imsvnr02.dat"):
            _append_named_table(
                selected,
                (
                    *baseline_300.vn_rule_group_1_export_tables,
                    *baseline_300.vn_rule_group_2_export_tables,
                ),
                filename,
                issues,
            )
    if table_500 is not None:
        selected.append(table_500)
    return tuple(selected)


def _append_named_table(
    selected: list[ExportTable],
    tables: Sequence[ExportTable],
    filename: str,
    issues: list[Historical500VUSK1DeliveryIssue],
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
    selected.append(matches[0])


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
