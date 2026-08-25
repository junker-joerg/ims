from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from ims.model.vdefmd6_action_seed import (
    MODERN_SEED_POLICY_ID,
    Vdefmd6ActionSlot,
    Vdefmd6ActionSeedPlan,
    build_vdefmd6_action_seed_plan,
)


CONTRACT_VERSION = "pr75-v1"
DEFAULT_CONTRACT_PATH = Path("tests/fixtures/vdefmd6_action_seed_contract.json")
REPORT_BASE_SEED = 20260001
_BOUNDARIES = {
    "scheduler_started": False,
    "rng_draws_performed": False,
    "simulation_performed": False,
    "historical_rng_equality_claimed": False,
    "historical_full_equality_claimed": False,
}
_SAME_SLOT = {
    "serialization": ["central", "insurer", "policyholder"],
    "serialization_is_execution_order": False,
    "historical_order_claimed": False,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6ActionSeedIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True, slots=True)
class Vdefmd6ActionSeedReport:
    repo_root: str
    contract_path: str
    summary: dict[str, object]
    seed_policy: dict[str, object]
    source_anchor_count: int
    issues: tuple[Vdefmd6ActionSeedIssue, ...]
    mode: str = "vdefmd6_action_seed"

    @property
    def action_seed_plan_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "action_seed_plan_built" if self.action_seed_plan_ready else "error",
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "source_anchor_count": self.source_anchor_count,
            "summary": dict(self.summary),
            "seed_policy": dict(self.seed_policy),
            "action_seed_plan_ready": self.action_seed_plan_ready,
            "modern_seed_policy_ready": self.action_seed_plan_ready,
            "historical_seed_known": False,
            "same_slot_serialization_is_execution_order": False,
            "historical_same_slot_order_claimed": False,
            "writes_performed": False,
            "execution_performed": False,
            "scheduler_started": False,
            "rng_draws_performed": False,
            "simulation_performed": False,
            "historical_rng_equality_claimed": False,
            "historical_full_equality_claimed": False,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_action_seed_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
) -> Vdefmd6ActionSeedReport:
    root = Path(repo_root).expanduser().resolve()
    path = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    issues: list[Vdefmd6ActionSeedIssue] = []
    contract = _load_contract(path, issues)
    plan = build_vdefmd6_action_seed_plan(base_seed=REPORT_BASE_SEED)
    summary = _plan_summary(plan)
    seed_policy = _seed_policy_summary(plan)
    anchor_count = _validate_contract(root, path, contract, summary, seed_policy, issues)
    return Vdefmd6ActionSeedReport(
        repo_root=str(root),
        contract_path=str(path),
        summary=summary,
        seed_policy=seed_policy,
        source_anchor_count=anchor_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_action_seed_report",
        description="Prueft den read-only Vdefmd6-Aktions- und Seed-Vertrag.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_action_seed_report(args.repo_root, contract_path=args.contract)
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.action_seed_plan_ready else 1


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _issue(
    issues: list[Vdefmd6ActionSeedIssue],
    code: str,
    message: str,
    path: Path | None = None,
) -> None:
    issues.append(
        Vdefmd6ActionSeedIssue(
            code=code,
            message=message,
            path=str(path) if path is not None else None,
        )
    )


def _load_contract(
    path: Path,
    issues: list[Vdefmd6ActionSeedIssue],
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


def _slot(
    plan: Vdefmd6ActionSeedPlan,
    period: int,
    logical_time: int,
) -> Vdefmd6ActionSlot:
    return next(
        item
        for item in plan.slots
        if item.period == period and item.logical_time == logical_time
    )


def _plan_summary(plan: Vdefmd6ActionSeedPlan) -> dict[str, object]:
    return {
        "period_start": min(item.period for item in plan.slots),
        "period_end": max(item.period for item in plan.slots),
        "slot_count": len(plan.slots),
        "invocation_count": sum(len(item.invocations) for item in plan.slots),
        "period_1_rule_invocation_count": len(_slot(plan, 1, 1).invocations),
        "period_49_rule_invocation_count": len(_slot(plan, 49, 1).invocations),
        "period_50_rule_invocation_count": len(_slot(plan, 50, 1).invocations),
        "period_100_rule_invocation_count": len(_slot(plan, 100, 1).invocations),
        "export_invocation_count": sum(
            len(item.invocations) for item in plan.slots if item.logical_time == 10
        ),
    }


def _seed_policy_summary(plan: Vdefmd6ActionSeedPlan) -> dict[str, object]:
    policy = plan.seed_policy
    return {
        "policy_id": policy.policy_id,
        "base_seed_required": True,
        "derivation": "base_seed + run_number - 1",
        "max_runs": policy.max_runs,
        "historical_seed_known": policy.historical_seed_known,
        "example_base_seed": policy.base_seed,
        "example_run_seeds": {
            "1": policy.seed_for_run(1),
            "2": policy.seed_for_run(2),
            "100": policy.seed_for_run(100),
        },
    }


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    summary: dict[str, object],
    seed_policy: dict[str, object],
    issues: list[Vdefmd6ActionSeedIssue],
) -> int:
    if contract.get("schema_version") != CONTRACT_VERSION:
        _issue(issues, "contract_version_mismatch", f"expected {CONTRACT_VERSION}", path)
    if contract.get("model_id") != "Vdefmd6":
        _issue(issues, "model_id_mismatch", "expected Vdefmd6", path)
    if contract.get("expected") != summary:
        _issue(issues, "action_summary_mismatch", "expected action summary differs", path)
    if (
        contract.get("seed_policy") != seed_policy
        or seed_policy["policy_id"] != MODERN_SEED_POLICY_ID
    ):
        _issue(issues, "seed_policy_mismatch", "modern seed policy differs", path)
    if contract.get("same_slot") != _SAME_SLOT:
        _issue(issues, "same_slot_boundary_mismatch", "same-slot boundary differs", path)
    if contract.get("boundaries") != _BOUNDARIES:
        _issue(issues, "execution_boundary_mismatch", "read-only boundaries differ", path)
    return _validate_source_anchors(root, contract, issues)


def _validate_source_anchors(
    root: Path,
    contract: dict[str, object],
    issues: list[Vdefmd6ActionSeedIssue],
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
