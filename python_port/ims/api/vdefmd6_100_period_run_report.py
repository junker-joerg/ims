from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from ims.api.vdefmd6_pre_shock_run_report import (
    Vdefmd6PreShockRunIssue,
    build_vdefmd6_run_summary,
    validate_vdefmd6_run_source_anchors,
)
from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_100_PERIOD_EXECUTION_ORDER,
    VDEFMD6_100_PERIOD_STATE_POLICY_ID,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
)


CONTRACT_VERSION = "pr81-v1"
CONTRACT_BASE_SEED = 20260001
DEFAULT_CONTRACT_PATH = Path(
    "tests/fixtures/vdefmd6_100_period_run_contract.json"
)
DEFAULT_REFERENCE_PATH = Path("tests/references/legacy_agrsich/VU14L1.DAT")
_BLOCKER_CODES = (
    "historical_same_slot_execution_order_open",
    "historical_rng_draw_order_open",
    "market_insurance_degree_derivation_open",
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
    "production_release_approved": False,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6100PeriodRunReport:
    repo_root: str
    contract_path: str
    reference_path: str
    summary: dict[str, object]
    shock_boundary: dict[str, object]
    source_anchor_count: int
    issues: tuple[Vdefmd6PreShockRunIssue, ...]
    mode: str = "vdefmd6_controlled_100_period_run"

    @property
    def run_path_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": (
                "100_period_path_classified" if self.run_path_ready else "error"
            ),
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "reference_path": self.reference_path,
            "summary": dict(self.summary),
            "shock_boundary": dict(self.shock_boundary),
            "source_anchor_count": self.source_anchor_count,
            "execution_order": list(VDEFMD6_100_PERIOD_EXECUTION_ORDER),
            "state_policy_id": VDEFMD6_100_PERIOD_STATE_POLICY_ID,
            "blocker_codes": list(_BLOCKER_CODES),
            "shock_boundary_ready": self.run_path_ready,
            "late_policyholder_activation_ready": self.run_path_ready,
            "generation_ready": self.run_path_ready,
            "historical_comparison_classified": self.run_path_ready,
            **_BOUNDARIES,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_100_period_run_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
    reference_path: Path | str | None = None,
) -> Vdefmd6100PeriodRunReport:
    root = Path(repo_root).expanduser().resolve()
    contract_file = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    reference_file = _resolve(root, reference_path, DEFAULT_REFERENCE_PATH)
    issues: list[Vdefmd6PreShockRunIssue] = []
    contract = _load_contract(contract_file, issues)
    result = _run(issues)
    summary = build_vdefmd6_run_summary(result, reference_file, issues)
    shock_boundary = _shock_boundary(result)
    anchor_count = _validate_contract(
        root,
        contract_file,
        contract,
        summary,
        shock_boundary,
        issues,
    )
    return Vdefmd6100PeriodRunReport(
        repo_root=str(root),
        contract_path=str(contract_file),
        reference_path=str(reference_file),
        summary=summary,
        shock_boundary=shock_boundary,
        source_anchor_count=anchor_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_100_period_run_report",
        description="Prueft den kontrollierten PR-81-Lauf bis Periode 100.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--reference", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_100_period_run_report(
        args.repo_root,
        contract_path=args.contract,
        reference_path=args.reference,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.run_path_ready else 1


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


def _shock_boundary(
    result: Vdefmd6PreShockRunResult | None,
) -> dict[str, object]:
    if result is None:
        return {
            "shock_period": 50,
            "shock_period_count": 0,
            "activated_policyholder_count": 0,
            "activated_policyholder_ids": [],
            "active_policyholder_count": 0,
        }
    period_50 = next(item for item in result.period_results if item.period == 50)
    return {
        "shock_period": 50,
        "shock_period_count": sum(item.change_shock for item in result.period_results),
        "activated_policyholder_count": len(period_50.activated_policyholder_ids),
        "activated_policyholder_ids": list(period_50.activated_policyholder_ids),
        "active_policyholder_count": period_50.active_policyholder_count,
    }


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    summary: dict[str, object],
    shock_boundary: dict[str, object],
    issues: list[Vdefmd6PreShockRunIssue],
) -> int:
    expected = {
        "schema_version": CONTRACT_VERSION,
        "model_id": "Vdefmd6",
        "scope": "controlled_periods_1_100_with_shock",
        "expected": summary,
        "shock_boundary": shock_boundary,
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
