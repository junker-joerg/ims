from __future__ import annotations

import argparse
from collections import Counter
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
    VDEFMD6_VU_AGGREGATE_FILENAMES,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
)
from ims.model.agrsich_export import ExportTable
from ims.model.legacy_agrsich_reference import (
    INSURER_FIELD_NAMES,
    compare_export_record_to_legacy_row,
    parse_legacy_insurer_dat,
)


CONTRACT_VERSION = "pr82-v1"
CONTRACT_BASE_SEED = 20260001
DEFAULT_CONTRACT_PATH = Path(
    "tests/fixtures/vdefmd6_vu_aggregate_run_contract.json"
)
DEFAULT_REFERENCE_PATHS = {
    "imsvusk1.dat": Path("tests/references/legacy_agrsich/VUSK1L5.DAT"),
    "imsvuvk1.dat": Path("tests/references/legacy_agrsich/IMSVUVK1.DAT"),
    "imsvuvk2.dat": Path("tests/references/legacy_agrsich/IMSVUVK2.DAT"),
    "imsvuvk3.dat": Path("tests/references/legacy_agrsich/IMSVUVK3.DAT"),
}
_BLOCKER_CODES = (
    "historical_same_slot_execution_order_open",
    "historical_rng_draw_order_open",
    "market_insurance_degree_derivation_open",
    "historical_vu_class_accumulator_semantics_open",
)
_BOUNDARIES = {
    "legacy_rows_used_as_generation_input": False,
    "comparison_started_after_generation": True,
    "controlled_execution_performed": True,
    "writes_performed": False,
    "scheduler_started": False,
    "simulation_performed": False,
    "historical_same_slot_order_claimed": False,
    "historical_rng_equality_claimed": False,
    "historical_vu_class_accumulator_compatibility_applied": False,
    "historical_full_equality_claimed": False,
    "production_release_approved": False,
}
_ORDERED_FIELD_NAMES = (
    "header",
    "global_period",
    *INSURER_FIELD_NAMES,
)


@dataclass(frozen=True, slots=True)
class Vdefmd6VUAggregateRunReport:
    repo_root: str
    contract_path: str
    target_summaries: tuple[dict[str, object], ...]
    source_anchor_count: int
    issues: tuple[Vdefmd6PreShockRunIssue, ...]
    mode: str = "vdefmd6_controlled_vu_aggregate_run"

    @property
    def aggregate_path_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": (
                "vu_aggregate_path_classified"
                if self.aggregate_path_ready
                else "error"
            ),
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "aggregate_target_count": len(self.target_summaries),
            "target_summaries": [dict(item) for item in self.target_summaries],
            "source_anchor_count": self.source_anchor_count,
            "execution_order": list(VDEFMD6_100_PERIOD_EXECUTION_ORDER),
            "state_policy_id": VDEFMD6_100_PERIOD_STATE_POLICY_ID,
            "blocker_codes": list(_BLOCKER_CODES),
            "aggregate_generation_ready": self.aggregate_path_ready,
            "historical_comparison_classified": self.aggregate_path_ready,
            **_BOUNDARIES,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_vu_aggregate_run_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
    reference_paths: dict[str, Path | str] | None = None,
) -> Vdefmd6VUAggregateRunReport:
    root = Path(repo_root).expanduser().resolve()
    contract_file = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    source_references = (
        DEFAULT_REFERENCE_PATHS if reference_paths is None else reference_paths
    )
    resolved_references = {
        filename: _resolve(root, path, Path(path))
        for filename, path in source_references.items()
    }
    issues: list[Vdefmd6PreShockRunIssue] = []
    contract = _load_contract(contract_file, issues)
    result = _run(issues)
    target_summaries = _build_target_summaries(
        result,
        resolved_references,
        issues,
    )
    anchor_count = _validate_contract(
        root,
        contract_file,
        contract,
        target_summaries,
        issues,
    )
    return Vdefmd6VUAggregateRunReport(
        repo_root=str(root),
        contract_path=str(contract_file),
        target_summaries=target_summaries,
        source_anchor_count=anchor_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_vu_aggregate_run_report",
        description="Prueft die vier kontrollierten PR-82-VU-Aggregate.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_vu_aggregate_run_report(
        args.repo_root,
        contract_path=args.contract,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.aggregate_path_ready else 1


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


def _build_target_summaries(
    result: Vdefmd6PreShockRunResult | None,
    reference_paths: dict[str, Path],
    issues: list[Vdefmd6PreShockRunIssue],
) -> tuple[dict[str, object], ...]:
    if result is None:
        return ()
    tables = {table.spec.filename: table for table in result.vu_aggregate_export_tables}
    if set(tables) != set(VDEFMD6_VU_AGGREGATE_FILENAMES):
        _issue(
            issues,
            "aggregate_target_set_mismatch",
            f"unexpected aggregate targets: {sorted(tables)}",
        )
        return ()
    if set(reference_paths) != set(VDEFMD6_VU_AGGREGATE_FILENAMES):
        _issue(
            issues,
            "reference_target_set_mismatch",
            f"unexpected reference targets: {sorted(reference_paths)}",
        )
        return ()
    return tuple(
        _summarize_target(tables[filename], reference_paths[filename], issues)
        for filename in VDEFMD6_VU_AGGREGATE_FILENAMES
    )


def _summarize_target(
    table: ExportTable,
    reference_path: Path,
    issues: list[Vdefmd6PreShockRunIssue],
) -> dict[str, object]:
    empty = _empty_target_summary(table, reference_path)
    try:
        legacy_rows = {
            row.global_period: row
            for row in parse_legacy_insurer_dat(reference_path).rows
            if 1 <= row.global_period <= 100
        }
        if set(legacy_rows) != set(range(1, 101)):
            raise ValueError("legacy comparison window must contain periods 1-100")
        comparisons = [
            (
                int(row.values[0]),
                compare_export_record_to_legacy_row(
                    ExportTable(spec=table.spec, header=table.header, rows=[row]),
                    legacy_rows[int(row.values[0])],
                ),
            )
            for row in table.rows
        ]
    except (KeyError, OSError, ValueError) as exc:
        _issue(issues, "reference_comparison_failed", str(exc), reference_path)
        return empty

    field_match_counts: Counter[str] = Counter()
    full_row_match_periods: list[int] = []
    matched_field_count = 0
    compared_field_count = 0
    for period, comparison in comparisons:
        field_match_counts.update(
            field.name for field in comparison.field_comparisons if field.matches
        )
        matched_field_count += sum(
            field.matches for field in comparison.field_comparisons
        )
        compared_field_count += len(comparison.field_comparisons)
        if comparison.matches:
            full_row_match_periods.append(period)

    return {
        **empty,
        "generated_period_count": len(table.rows),
        "compared_row_count": len(comparisons),
        "compared_field_count": compared_field_count,
        "matched_field_count": matched_field_count,
        "full_row_match_periods": full_row_match_periods,
        "first_full_state_divergence_period": next(
            (
                period
                for period, _ in comparisons
                if period not in full_row_match_periods
            ),
            None,
        ),
        "field_match_counts": {
            name: field_match_counts[name] for name in _ORDERED_FIELD_NAMES
        },
    }


def _empty_target_summary(
    table: ExportTable,
    reference_path: Path,
) -> dict[str, object]:
    return {
        "export_filename": table.spec.filename,
        "reference_filename": reference_path.name,
        "level": table.spec.level,
        "selector_kind": table.spec.selector_kind,
        "selector_value": table.spec.selector_value,
        "generated_period_count": 0,
        "compared_row_count": 0,
        "compared_field_count": 0,
        "matched_field_count": 0,
        "full_row_match_periods": [],
        "first_full_state_divergence_period": None,
        "field_match_counts": {},
    }


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    target_summaries: tuple[dict[str, object], ...],
    issues: list[Vdefmd6PreShockRunIssue],
) -> int:
    expected = {
        "schema_version": CONTRACT_VERSION,
        "model_id": "Vdefmd6",
        "scope": "controlled_vu_aggregates_periods_1_100",
        "expected_targets": list(target_summaries),
        "execution_order": list(VDEFMD6_100_PERIOD_EXECUTION_ORDER),
        "state_policy_id": VDEFMD6_100_PERIOD_STATE_POLICY_ID,
        "blocker_codes": list(_BLOCKER_CODES),
        "boundaries": _BOUNDARIES,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            _issue(issues, f"{key}_mismatch", f"contract field differs: {key}", path)
    return validate_vdefmd6_run_source_anchors(root, contract, issues)


if __name__ == "__main__":
    raise SystemExit(main())
