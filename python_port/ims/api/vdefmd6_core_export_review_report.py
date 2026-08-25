from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from ims.api.vdefmd6_pre_shock_run_report import (
    Vdefmd6PreShockRunIssue,
    validate_vdefmd6_run_source_anchors,
)
from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_100_PERIOD_EXECUTION_ORDER,
    VDEFMD6_100_PERIOD_STATE_POLICY_ID,
    VDEFMD6_VN_AGGREGATE_FILENAMES,
    VDEFMD6_VN_RULE_GROUP_1_FILENAMES,
    VDEFMD6_VN_RULE_GROUP_2_FILENAMES,
    VDEFMD6_VU_AGGREGATE_FILENAMES,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
)
from ims.model.agrsich_export import ExportTable
from ims.model.legacy_calculated_deviation_report import (
    CalculatedLegacyDeviationReport,
    build_calculated_legacy_deviation_report,
)


CONTRACT_VERSION = "pr86-v1"
CONTRACT_BASE_SEED = 20260001
DEFAULT_CONTRACT_PATH = Path(
    "tests/fixtures/vdefmd6_core_export_run_contract.json"
)
DEFAULT_WINDOW_BUNDLE_PATH = Path(
    "tests/fixtures/vdefmd6_core_export_window_bundle.json"
)
CORE_EXPORT_FILENAMES = (
    "imsvu014.dat",
    *VDEFMD6_VU_AGGREGATE_FILENAMES,
    *VDEFMD6_VN_RULE_GROUP_1_FILENAMES,
    *VDEFMD6_VN_RULE_GROUP_2_FILENAMES,
    *VDEFMD6_VN_AGGREGATE_FILENAMES,
)
_BLOCKER_CODES = (
    "full_required_period_windows_missing",
    "historical_reference_run_identity_open",
    "historical_reference_family_coherence_open",
    "historical_same_slot_execution_order_open",
    "historical_rng_draw_order_open",
    "market_insurance_degree_derivation_open",
    "historical_vu_class_accumulator_semantics_open",
    "historical_vn_rule_accumulator_semantics_open",
    "historical_vn_class_accumulator_semantics_open",
    "historical_vn_aggregate_initialization_semantics_open",
    "policyholder_ev_field_semantics_open",
)
_BOUNDARIES = {
    "legacy_rows_used_as_generation_input": False,
    "comparison_started_after_generation": True,
    "controlled_execution_performed": True,
    "writes_performed": False,
    "scheduler_started": False,
    "simulation_performed": False,
    "automatic_historical_rule_selection_performed": False,
    "controlled_100_period_window_complete": True,
    "full_legacy_corpus_window_complete": False,
    "historical_reference_run_identity_claimed": False,
    "historical_reference_family_coherence_claimed": False,
    "historical_same_slot_order_claimed": False,
    "historical_rng_equality_claimed": False,
    "historical_vu_class_accumulator_compatibility_applied": False,
    "historical_vn_rule_accumulator_compatibility_applied": False,
    "historical_vn_class_accumulator_compatibility_applied": False,
    "historical_vn_aggregate_initialization_compatibility_applied": False,
    "historical_full_equality_claimed": False,
    "production_release_approved": False,
}
_STRUCTURAL_FIELDS = frozenset({"header", "global_period"})
_REVIEW_RECOMMENDATION = "keep_blocked"


@dataclass(frozen=True, slots=True)
class Vdefmd6CoreExportReviewReport:
    repo_root: str
    contract_path: str
    window_bundle_path: str
    summary: dict[str, object]
    target_summaries: tuple[dict[str, object], ...]
    source_anchor_count: int
    issues: tuple[Vdefmd6PreShockRunIssue, ...]
    mode: str = "vdefmd6_core_export_review"

    @property
    def review_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "review_ready" if self.review_ready else "error",
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "window_bundle_path": self.window_bundle_path,
            "controlled_export_count": len(self.target_summaries),
            "summary": dict(self.summary),
            "target_summaries": [dict(item) for item in self.target_summaries],
            "source_anchor_count": self.source_anchor_count,
            "execution_order": list(VDEFMD6_100_PERIOD_EXECUTION_ORDER),
            "state_policy_id": VDEFMD6_100_PERIOD_STATE_POLICY_ID,
            "blocker_codes": list(_BLOCKER_CODES),
            "review_recommendation": _REVIEW_RECOMMENDATION,
            "human_release_review_required": True,
            "planned_minimum_series_complete": self.review_ready,
            "joint_deviation_comparison_ready": self.review_ready,
            **_BOUNDARIES,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_core_export_review_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
    window_bundle_path: Path | str | None = None,
) -> Vdefmd6CoreExportReviewReport:
    root = Path(repo_root).expanduser().resolve()
    contract_file = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    window_bundle_file = _resolve(
        root,
        window_bundle_path,
        DEFAULT_WINDOW_BUNDLE_PATH,
    )
    issues: list[Vdefmd6PreShockRunIssue] = []
    contract = _load_contract(contract_file, issues)
    result = _run(issues)
    tables = _collect_export_tables(result, issues)
    deviation = _build_deviation(window_bundle_file, tables, issues)
    target_summaries = _target_summaries(deviation)
    summary = _summary(deviation, target_summaries)
    anchor_count = _validate_contract(
        root,
        contract_file,
        contract,
        window_bundle_file,
        summary,
        target_summaries,
        issues,
    )
    return Vdefmd6CoreExportReviewReport(
        repo_root=str(root),
        contract_path=str(contract_file),
        window_bundle_path=str(window_bundle_file),
        summary=summary,
        target_summaries=target_summaries,
        source_anchor_count=anchor_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_core_export_review_report",
        description="Prueft den gemeinsamen PR-86-Bericht fuer 15 Kernexporte.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--window-bundle", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_core_export_review_report(
        args.repo_root,
        contract_path=args.contract,
        window_bundle_path=args.window_bundle,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.review_ready else 1


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _issue(
    issues: list[Vdefmd6PreShockRunIssue],
    code: str,
    message: str,
    path: Path | None = None,
) -> None:
    issues.append(
        Vdefmd6PreShockRunIssue(
            code=code,
            message=message,
            path=str(path) if path is not None else None,
        )
    )


def _load_contract(
    path: Path,
    issues: list[Vdefmd6PreShockRunIssue],
) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _issue(issues, "contract_unreadable", str(exc), path)
        return {}
    if not isinstance(payload, dict):
        _issue(issues, "contract_shape_invalid", "contract must be an object", path)
        return {}
    return payload


def _run(
    issues: list[Vdefmd6PreShockRunIssue],
) -> Vdefmd6PreShockRunResult | None:
    try:
        return run_vdefmd6_100_periods(base_seed=CONTRACT_BASE_SEED)
    except (TypeError, ValueError, StopIteration) as exc:
        _issue(issues, "controlled_run_failed", str(exc))
        return None


def _collect_export_tables(
    result: Vdefmd6PreShockRunResult | None,
    issues: list[Vdefmd6PreShockRunIssue],
) -> tuple[ExportTable, ...]:
    if result is None:
        return ()
    tables = (
        result.vu14_export_table,
        *result.vu_aggregate_export_tables,
        *result.vn_rule_group_1_export_tables,
        *result.vn_rule_group_2_export_tables,
        *result.vn_aggregate_export_tables,
    )
    filenames = tuple(table.spec.filename for table in tables)
    if filenames != CORE_EXPORT_FILENAMES:
        _issue(
            issues,
            "core_export_target_set_mismatch",
            f"unexpected core export targets: {list(filenames)}",
        )
        return ()
    return tables


def _build_deviation(
    window_bundle_path: Path,
    tables: tuple[ExportTable, ...],
    issues: list[Vdefmd6PreShockRunIssue],
) -> CalculatedLegacyDeviationReport | None:
    if not tables:
        return None
    try:
        deviation = build_calculated_legacy_deviation_report(
            window_bundle_path,
            list(tables),
            calculation_origin="vdefmd6_controlled_100_period_core_exports",
        )
    except (OSError, TypeError, ValueError) as exc:
        _issue(issues, "joint_deviation_failed", str(exc), window_bundle_path)
        return None
    if not deviation.comparison_performed:
        codes = sorted({item.code for item in deviation.input_issues})
        _issue(
            issues,
            "joint_deviation_blocked",
            f"joint deviation input blocked: {codes}",
            window_bundle_path,
        )
    return deviation


def _row_period(row_comparison: object) -> int | None:
    for field in row_comparison.field_comparisons:
        if field.name != "global_period":
            continue
        for value in (field.actual, field.expected):
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
    return None


def _target_summaries(
    deviation: CalculatedLegacyDeviationReport | None,
) -> tuple[dict[str, object], ...]:
    if deviation is None or deviation.comparison_result is None:
        return ()
    by_filename = {
        item.filename: item
        for item in deviation.comparison_result.comparison.table_comparisons
    }
    summaries: list[dict[str, object]] = []
    for filename in CORE_EXPORT_FILENAMES:
        table = by_filename[filename]
        fields = [
            field
            for row in table.row_comparisons
            for field in row.field_comparisons
        ]
        structural = [field for field in fields if field.name in _STRUCTURAL_FIELDS]
        fach = [field for field in fields if field.name not in _STRUCTURAL_FIELDS]
        full_rows = [
            period
            for row in table.row_comparisons
            if row.matches and (period := _row_period(row)) is not None
        ]
        summaries.append(
            {
                "export_filename": filename,
                "subject_type": table.subject_type,
                "level": table.level,
                "selector_kind": table.selector_kind,
                "selector_value": table.selector_value,
                "compared_row_count": len(table.row_comparisons),
                "compared_field_count": len(fields),
                "matched_field_count": sum(field.matches for field in fields),
                "structural_field_count": len(structural),
                "matched_structural_field_count": sum(
                    field.matches for field in structural
                ),
                "fach_field_count": len(fach),
                "matched_fach_field_count": sum(field.matches for field in fach),
                "full_row_match_periods": full_rows,
            }
        )
    return tuple(summaries)


def _summary(
    deviation: CalculatedLegacyDeviationReport | None,
    target_summaries: tuple[dict[str, object], ...],
) -> dict[str, object]:
    compared_rows = sum(int(item["compared_row_count"]) for item in target_summaries)
    full_rows = sum(len(item["full_row_match_periods"]) for item in target_summaries)
    compared_fields = sum(
        int(item["compared_field_count"]) for item in target_summaries
    )
    matched_fields = sum(
        int(item["matched_field_count"]) for item in target_summaries
    )
    structural_fields = sum(
        int(item["structural_field_count"]) for item in target_summaries
    )
    matched_structural = sum(
        int(item["matched_structural_field_count"]) for item in target_summaries
    )
    fach_fields = sum(int(item["fach_field_count"]) for item in target_summaries)
    matched_fach = sum(
        int(item["matched_fach_field_count"]) for item in target_summaries
    )
    return {
        "controlled_period_start": 1,
        "controlled_period_end": 100,
        "controlled_export_count": len(target_summaries),
        "compared_row_count": compared_rows,
        "full_row_match_count": full_rows,
        "mismatched_row_count": compared_rows - full_rows,
        "compared_field_count": compared_fields,
        "matched_field_count": matched_fields,
        "structural_field_count": structural_fields,
        "matched_structural_field_count": matched_structural,
        "fach_field_count": fach_fields,
        "matched_fach_field_count": matched_fach,
        "deviation_status": deviation.status if deviation is not None else "not_available",
        "exact_field_match_count": (
            deviation.exact_field_match_count if deviation is not None else 0
        ),
        "tolerated_numeric_difference_count": (
            len(deviation.tolerated_numeric_differences) if deviation is not None else 0
        ),
        "blocking_numeric_difference_count": (
            len(deviation.blocking_numeric_differences) if deviation is not None else 0
        ),
        "open_field_question_count": (
            len(deviation.open_field_questions) if deviation is not None else 0
        ),
    }


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    window_bundle_path: Path,
    summary: dict[str, object],
    target_summaries: tuple[dict[str, object], ...],
    issues: list[Vdefmd6PreShockRunIssue],
) -> int:
    expected = {
        "schema_version": CONTRACT_VERSION,
        "model_id": "Vdefmd6",
        "scope": "joint_core_exports_periods_1_100_release_review",
        "window_bundle": window_bundle_path.name,
        "expected_target_filenames": list(CORE_EXPORT_FILENAMES),
        "expected_summary": summary,
        "expected_targets": list(target_summaries),
        "execution_order": list(VDEFMD6_100_PERIOD_EXECUTION_ORDER),
        "state_policy_id": VDEFMD6_100_PERIOD_STATE_POLICY_ID,
        "blocker_codes": list(_BLOCKER_CODES),
        "review_recommendation": _REVIEW_RECOMMENDATION,
        "boundaries": _BOUNDARIES,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            _issue(issues, f"{key}_mismatch", f"contract field differs: {key}", path)
    return validate_vdefmd6_run_source_anchors(root, contract, issues)


if __name__ == "__main__":
    raise SystemExit(main())
