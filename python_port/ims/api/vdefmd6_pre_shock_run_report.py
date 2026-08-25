from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_PRE_SHOCK_EXECUTION_ORDER,
    VDEFMD6_PRE_SHOCK_STATE_POLICY_ID,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_pre_shock_periods,
)
from ims.model.agrsich_export import ExportTable
from ims.model.legacy_agrsich_reference import (
    compare_export_record_to_legacy_row,
    parse_legacy_insurer_dat,
)


CONTRACT_VERSION = "pr80-v1"
CONTRACT_BASE_SEED = 20260001
DEFAULT_CONTRACT_PATH = Path(
    "tests/fixtures/vdefmd6_pre_shock_run_contract.json"
)
DEFAULT_REFERENCE_PATH = Path("tests/references/legacy_agrsich/VU14L1.DAT")
_RULE_OUTPUT_FIELDS = ("Pr1", "Wa1", "Pr2", "Wa2")
_BLOCKER_CODES = (
    "historical_same_slot_execution_order_open",
    "historical_rng_draw_order_open",
    "shock_periods_50_100_missing",
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
    "historical_full_equality_claimed": False,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6PreShockRunIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True, slots=True)
class Vdefmd6PreShockRunReport:
    repo_root: str
    contract_path: str
    reference_path: str
    summary: dict[str, object]
    source_anchor_count: int
    issues: tuple[Vdefmd6PreShockRunIssue, ...]
    mode: str = "vdefmd6_controlled_pre_shock_run"

    @property
    def pre_shock_path_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": (
                "pre_shock_path_classified"
                if self.pre_shock_path_ready
                else "error"
            ),
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "reference_path": self.reference_path,
            "summary": dict(self.summary),
            "source_anchor_count": self.source_anchor_count,
            "execution_order": list(VDEFMD6_PRE_SHOCK_EXECUTION_ORDER),
            "state_policy_id": VDEFMD6_PRE_SHOCK_STATE_POLICY_ID,
            "blocker_codes": list(_BLOCKER_CODES),
            "information_cost_application_ready": self.pre_shock_path_ready,
            "independent_periods_2_49_ready": self.pre_shock_path_ready,
            "full_state_projection_ready": self.pre_shock_path_ready,
            "generation_ready": False,
            **_BOUNDARIES,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_pre_shock_run_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
    reference_path: Path | str | None = None,
) -> Vdefmd6PreShockRunReport:
    root = Path(repo_root).expanduser().resolve()
    contract_file = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    reference_file = _resolve(root, reference_path, DEFAULT_REFERENCE_PATH)
    issues: list[Vdefmd6PreShockRunIssue] = []
    contract = _load_contract(contract_file, issues)
    result = _run(issues)
    summary = build_vdefmd6_run_summary(result, reference_file, issues)
    anchor_count = _validate_contract(
        root,
        contract_file,
        contract,
        summary,
        issues,
    )
    return Vdefmd6PreShockRunReport(
        repo_root=str(root),
        contract_path=str(contract_file),
        reference_path=str(reference_file),
        summary=summary,
        source_anchor_count=anchor_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_pre_shock_run_report",
        description="Prueft den kontrollierten PR-80-Vorschockpfad.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--reference", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_pre_shock_run_report(
        args.repo_root,
        contract_path=args.contract,
        reference_path=args.reference,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.pre_shock_path_ready else 1


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
        return run_vdefmd6_pre_shock_periods(base_seed=CONTRACT_BASE_SEED)
    except (TypeError, ValueError, StopIteration) as exc:
        _issue(issues, "controlled_run_failed", str(exc))
        return None


def _empty_summary() -> dict[str, object]:
    return {
        "base_seed": CONTRACT_BASE_SEED,
        "generated_period_count": 0,
        "followup_period_count": 0,
        "total_information_cost": 0.0,
        "total_information_cost_policyholders": 0,
        "total_vu_rule_applications": 0,
        "total_vn_insurance_rule_applications": 0,
        "total_vn_damage_settlement_applications": 0,
        "total_uniform_value_count": 0,
        "total_normal_value_count": 0,
        "compared_row_count": 0,
        "compared_field_count": 0,
        "matched_field_count": 0,
        "full_row_match_periods": [],
        "rule_output_match_periods": [],
        "first_full_state_divergence_period": None,
        "first_rule_output_divergence_period": None,
        "field_match_counts": {},
    }


def build_vdefmd6_run_summary(
    result: Vdefmd6PreShockRunResult | None,
    reference_path: Path,
    issues: list[Vdefmd6PreShockRunIssue],
) -> dict[str, object]:
    if result is None:
        return _empty_summary()
    try:
        legacy_rows = {
            row.global_period: row
            for row in parse_legacy_insurer_dat(reference_path).rows
        }
        comparisons = [
            (
                int(row.values[0]),
                compare_export_record_to_legacy_row(
                    ExportTable(
                        spec=result.vu14_export_table.spec,
                        header=result.vu14_export_table.header,
                        rows=[row],
                    ),
                    legacy_rows[int(row.values[0])],
                ),
            )
            for row in result.vu14_export_table.rows
        ]
    except (KeyError, OSError, ValueError) as exc:
        _issue(issues, "reference_comparison_failed", str(exc), reference_path)
        return _empty_summary()

    field_match_counts: Counter[str] = Counter()
    full_row_match_periods: list[int] = []
    rule_output_match_periods: list[int] = []
    matched_field_count = 0
    compared_field_count = 0
    for period, comparison in comparisons:
        matches_by_name = {
            field.name: field.matches for field in comparison.field_comparisons
        }
        field_match_counts.update(
            field.name for field in comparison.field_comparisons if field.matches
        )
        matched_field_count += sum(field.matches for field in comparison.field_comparisons)
        compared_field_count += len(comparison.field_comparisons)
        if comparison.matches:
            full_row_match_periods.append(period)
        if all(matches_by_name.get(name) is True for name in _RULE_OUTPUT_FIELDS):
            rule_output_match_periods.append(period)

    ordered_names = (
        "header",
        "global_period",
        "Pr1",
        "Wa1",
        "Rs1",
        "Vn1",
        "Sa1",
        "Sh1",
        "Pr2",
        "Wa2",
        "Rs2",
        "Vn2",
        "Sa2",
        "Sh2",
    )
    return {
        "base_seed": result.base_seed,
        "generated_period_count": len(result.vu14_export_table.rows),
        "followup_period_count": len(result.period_results),
        "total_information_cost": result.total_information_cost,
        "total_information_cost_policyholders": (
            result.total_information_cost_policyholders
        ),
        "total_vu_rule_applications": result.total_vu_rule_applications,
        "total_vn_insurance_rule_applications": (
            result.total_vn_insurance_rule_applications
        ),
        "total_vn_damage_settlement_applications": (
            result.total_vn_damage_settlement_applications
        ),
        "total_uniform_value_count": result.total_uniform_value_count,
        "total_normal_value_count": result.total_normal_value_count,
        "compared_row_count": len(comparisons),
        "compared_field_count": compared_field_count,
        "matched_field_count": matched_field_count,
        "full_row_match_periods": full_row_match_periods,
        "rule_output_match_periods": rule_output_match_periods,
        "first_full_state_divergence_period": next(
            (period for period, _ in comparisons if period not in full_row_match_periods),
            None,
        ),
        "first_rule_output_divergence_period": next(
            (period for period, _ in comparisons if period not in rule_output_match_periods),
            None,
        ),
        "field_match_counts": {
            name: field_match_counts[name] for name in ordered_names
        },
    }


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    summary: dict[str, object],
    issues: list[Vdefmd6PreShockRunIssue],
) -> int:
    expected = {
        "schema_version": CONTRACT_VERSION,
        "model_id": "Vdefmd6",
        "scope": "controlled_pre_shock_periods_2_49",
        "expected": summary,
        "execution_order": list(VDEFMD6_PRE_SHOCK_EXECUTION_ORDER),
        "state_policy_id": VDEFMD6_PRE_SHOCK_STATE_POLICY_ID,
        "blocker_codes": list(_BLOCKER_CODES),
        "boundaries": _BOUNDARIES,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            _issue(issues, f"{key}_mismatch", f"contract field differs: {key}", path)
    return validate_vdefmd6_run_source_anchors(root, contract, issues)


def validate_vdefmd6_run_source_anchors(
    root: Path,
    contract: dict[str, object],
    issues: list[Vdefmd6PreShockRunIssue],
) -> int:
    anchors = contract.get("source_anchors")
    if not isinstance(anchors, list):
        _issue(issues, "source_anchors_missing", "source_anchors must be a list")
        return 0
    texts: dict[Path, str] = {}
    for anchor in anchors:
        if not isinstance(anchor, dict):
            _issue(issues, "source_anchor_invalid", str(anchor))
            continue
        source_path = (root / str(anchor.get("path", ""))).resolve()
        if source_path not in texts:
            try:
                texts[source_path] = source_path.read_text(encoding="latin-1")
            except OSError as exc:
                _issue(issues, "source_unreadable", str(exc), source_path)
                continue
        needle = str(anchor.get("needle", ""))
        if not needle or needle not in texts[source_path]:
            _issue(issues, "source_anchor_missing", needle, source_path)
    return len(anchors)


if __name__ == "__main__":
    raise SystemExit(main())
