from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from ims.api.vu14_source_binding import (
    DEFAULT_SOURCE_BINDING_PATH,
    build_vu14_source_binding_report,
)
from ims.model.legacy_agrsich_reference import (
    compare_export_record_to_legacy_row,
    parse_legacy_insurer_dat,
)
from ims.model.vu14_pre_shock_projection import (
    VU14PreShockProjection,
    build_vu14_pre_shock_projection,
)
from ims.model.vu_rules import vu_expected_claim_rule_parameters_from_mapping


CONTRACT_VERSION = "pr76-v1"
DEFAULT_CONTRACT_PATH = Path("tests/fixtures/vu14_pre_shock_projection_contract.json")
_TARGET = {
    "model_id": "Vdefmd6",
    "subject_type": "insurer",
    "level": "I",
    "selector_kind": "entity",
    "selector_value": 14,
    "rule_id": 6,
    "period_start": 1,
    "period_end": 49,
    "followup_period_start": 2,
    "followup_period_end": 49,
}
_RULE_OUTPUT_FIELDS = ("Pr1", "Wa1", "Pr2", "Wa2")
_BLOCKER_CODES = (
    "policyholder_claim_origin_missing",
    "settlement_state_origin_missing",
    "historical_rng_draw_order_missing",
)
_BOUNDARIES = {
    "legacy_rows_used_as_generation_input": False,
    "comparison_started_after_generation": True,
    "downstream_incidental_matches_are_evidence": False,
    "scheduler_started": False,
    "rng_draws_performed": False,
    "simulation_performed": False,
    "historical_full_equality_claimed": False,
}


@dataclass(frozen=True, slots=True)
class VU14PreShockProjectionIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True, slots=True)
class VU14PreShockProjectionReport:
    repo_root: str
    contract_path: str
    binding_path: str
    summary: dict[str, object]
    source_anchor_count: int
    source_binding: dict[str, object]
    projection_performed: bool
    issues: tuple[VU14PreShockProjectionIssue, ...]
    mode: str = "vu14_pre_shock_projection"

    @property
    def rule_projection_ready(self) -> bool:
        return self.projection_performed and not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "projection_classified" if self.rule_projection_ready else "error",
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "binding_path": self.binding_path,
            "target": dict(_TARGET),
            "summary": dict(self.summary),
            "source_anchor_count": self.source_anchor_count,
            "source_binding": dict(self.source_binding),
            "blocker_codes": list(_BLOCKER_CODES),
            "rule_projection_ready": self.rule_projection_ready,
            "independent_periods_2_49_ready": False,
            "full_state_projection_ready": False,
            "generation_ready": False,
            "projection_performed": self.projection_performed,
            "projection_generated_before_legacy_read": True,
            "legacy_rows_used_as_generation_input": False,
            "downstream_incidental_matches_are_evidence": False,
            "writes_performed": False,
            "execution_performed": False,
            "scheduler_started": False,
            "rng_draws_performed": False,
            "simulation_performed": False,
            "historical_full_equality_claimed": False,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vu14_pre_shock_projection_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
    binding_path: Path | str | None = None,
) -> VU14PreShockProjectionReport:
    root = Path(repo_root).expanduser().resolve()
    contract_file = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    binding_file = _resolve(root, binding_path, DEFAULT_SOURCE_BINDING_PATH)
    issues: list[VU14PreShockProjectionIssue] = []
    contract = _load_json_object(contract_file, "contract", issues)
    profile = _load_json_object(binding_file, "binding", issues)

    projection = _build_projection(profile, issues, binding_file)

    binding_report = build_vu14_source_binding_report(root, binding_path=binding_file)
    for binding_issue in binding_report.issues:
        issues.append(
            VU14PreShockProjectionIssue(
                code=f"source_binding_{binding_issue.code}",
                message=binding_issue.message,
                path=binding_issue.path,
            )
        )

    summary = _compare_after_generation(root, profile, projection, issues)
    anchor_count = _validate_contract(
        root,
        contract_file,
        contract,
        summary,
        issues,
    )
    return VU14PreShockProjectionReport(
        repo_root=str(root),
        contract_path=str(contract_file),
        binding_path=str(binding_file),
        summary=summary,
        source_anchor_count=anchor_count,
        source_binding=binding_report.to_dict(),
        projection_performed=projection is not None,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vu14_pre_shock_projection_report",
        description="Prueft die read-only VU14-Regelprojektion fuer Perioden 1-49.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--binding", type=Path)
    args = parser.parse_args(argv)
    report = build_vu14_pre_shock_projection_report(
        args.repo_root,
        contract_path=args.contract,
        binding_path=args.binding,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.rule_projection_ready else 1


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _issue(
    issues: list[VU14PreShockProjectionIssue],
    code: str,
    message: str,
    path: Path | None = None,
) -> None:
    issues.append(
        VU14PreShockProjectionIssue(
            code=code,
            message=message,
            path=str(path) if path is not None else None,
        )
    )


def _load_json_object(
    path: Path,
    label: str,
    issues: list[VU14PreShockProjectionIssue],
) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _issue(issues, f"{label}_unreadable", str(exc), path)
        return {}
    if not isinstance(payload, dict):
        _issue(issues, f"{label}_shape_invalid", f"{label} must be an object", path)
        return {}
    return payload


def _build_projection(
    profile: dict[str, object],
    issues: list[VU14PreShockProjectionIssue],
    path: Path,
) -> VU14PreShockProjection | None:
    vu14 = profile.get("vu14") if isinstance(profile.get("vu14"), dict) else {}
    parameters = vu14.get("parameters") if isinstance(vu14.get("parameters"), dict) else {}
    bav = profile.get("bav") if isinstance(profile.get("bav"), dict) else {}
    try:
        return build_vu14_pre_shock_projection(
            vu_expected_claim_rule_parameters_from_mapping(parameters),
            interest_rate=float(bav["interest_rate"]),
        )
    except (KeyError, TypeError, ValueError, StopIteration) as exc:
        _issue(issues, "projection_failed", str(exc), path)
        return None


def _empty_summary() -> dict[str, object]:
    return {
        "generated_period_count": 0,
        "followup_period_count": 0,
        "compared_row_count": 0,
        "compared_field_count": 0,
        "matched_field_count": 0,
        "full_row_match_periods": [],
        "rule_output_match_periods": [],
        "first_rule_output_divergence_period": None,
        "field_match_counts": {},
    }


def _compare_after_generation(
    root: Path,
    profile: dict[str, object],
    projection: VU14PreShockProjection | None,
    issues: list[VU14PreShockProjectionIssue],
) -> dict[str, object]:
    if projection is None:
        return _empty_summary()
    reference = profile.get("reference") if isinstance(profile.get("reference"), dict) else {}
    reference_path = (root / str(reference.get("path", ""))).resolve()
    try:
        legacy_rows = {
            row.global_period: row
            for row in parse_legacy_insurer_dat(reference_path).rows
            if 1 <= row.global_period <= 49
        }
        comparisons = [
            (
                item.period,
                compare_export_record_to_legacy_row(
                    item.export_table,
                    legacy_rows[item.period],
                ),
            )
            for item in projection.periods
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

    first_divergence = next(
        (
            period
            for period, _comparison in comparisons
            if period not in rule_output_match_periods
        ),
        None,
    )
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
        "generated_period_count": len(projection.periods),
        "followup_period_count": sum(item.period >= 2 for item in projection.periods),
        "compared_row_count": len(comparisons),
        "compared_field_count": compared_field_count,
        "matched_field_count": matched_field_count,
        "full_row_match_periods": full_row_match_periods,
        "rule_output_match_periods": rule_output_match_periods,
        "first_rule_output_divergence_period": first_divergence,
        "field_match_counts": {
            name: field_match_counts[name] for name in ordered_names
        },
    }


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    summary: dict[str, object],
    issues: list[VU14PreShockProjectionIssue],
) -> int:
    if contract.get("schema_version") != CONTRACT_VERSION:
        _issue(issues, "contract_version_mismatch", CONTRACT_VERSION, path)
    if contract.get("target") != _TARGET:
        _issue(issues, "target_mismatch", "expected VU14 / periods 1-49", path)
    if contract.get("expected") != summary:
        _issue(issues, "projection_summary_mismatch", "expected summary differs", path)
    if tuple(contract.get("blocker_codes", ())) != _BLOCKER_CODES:
        _issue(issues, "blocker_boundary_mismatch", "blocker codes differ", path)
    if contract.get("boundaries") != _BOUNDARIES:
        _issue(issues, "execution_boundary_mismatch", "read-only boundaries differ", path)
    return _validate_source_anchors(root, contract, issues)


def _validate_source_anchors(
    root: Path,
    contract: dict[str, object],
    issues: list[VU14PreShockProjectionIssue],
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
