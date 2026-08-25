from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import random
from typing import Sequence

from ims.model.vdefmd6_population import build_vdefmd6_population
from ims.model.vdefmd6_pre_shock_snapshots import (
    VDEFMD6_PRE_SHOCK_DRAW_POLICY_ID,
    build_vdefmd6_pre_shock_snapshot_batch,
)


CONTRACT_VERSION = "pr78-v1"
DEFAULT_CONTRACT_PATH = Path(
    "tests/fixtures/vdefmd6_pre_shock_snapshot_contract.json"
)
CONTRACT_PERIOD = 2
CONTRACT_SEED = 780001

_DRAW_ORDER = (
    "policyholder_id_ascending",
    "damage_threshold_sector_1",
    "damage_threshold_sector_2",
    "damage_sector_1_trigger",
    "damage_sector_1_amount",
    "damage_sector_2_trigger",
    "damage_sector_2_amount",
    "rule_specific_insurance_draws",
)
_BLOCKER_CODES = (
    "all_insurer_period_rule_snapshots_missing",
    "information_cost_wealth_application_open",
    "multi_period_state_projection_missing",
    "historical_rng_and_same_slot_order_open",
)
_BOUNDARIES = {
    "legacy_rows_used_as_generation_input": False,
    "snapshot_materialization_performed": True,
    "rng_draws_performed": True,
    "runner_started": False,
    "simulation_performed": False,
    "historical_rng_equality_claimed": False,
    "historical_full_equality_claimed": False,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6PreShockSnapshotIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True, slots=True)
class Vdefmd6PreShockSnapshotReport:
    repo_root: str
    contract_path: str
    summary: dict[str, object]
    source_anchor_count: int
    issues: tuple[Vdefmd6PreShockSnapshotIssue, ...]
    mode: str = "vdefmd6_pre_shock_snapshot_materialization"

    @property
    def snapshot_materialization_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": (
                "snapshot_materialization_ready"
                if self.snapshot_materialization_ready
                else "error"
            ),
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "summary": dict(self.summary),
            "source_anchor_count": self.source_anchor_count,
            "draw_policy_id": VDEFMD6_PRE_SHOCK_DRAW_POLICY_ID,
            "draw_order": list(_DRAW_ORDER),
            "blocker_codes": list(_BLOCKER_CODES),
            "snapshot_materialization_ready": self.snapshot_materialization_ready,
            "independent_periods_2_49_ready": False,
            "full_state_projection_ready": False,
            "generation_ready": False,
            **_BOUNDARIES,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_pre_shock_snapshot_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
) -> Vdefmd6PreShockSnapshotReport:
    root = Path(repo_root).expanduser().resolve()
    path = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    issues: list[Vdefmd6PreShockSnapshotIssue] = []
    contract = _load_contract(path, issues)
    summary = _build_summary()
    anchor_count = _validate_contract(root, path, contract, summary, issues)
    return Vdefmd6PreShockSnapshotReport(
        repo_root=str(root),
        contract_path=str(path),
        summary=summary,
        source_anchor_count=anchor_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_pre_shock_snapshot_report",
        description="Prueft die PR-78-Vorschock-Snapshotmaterialisierung.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_pre_shock_snapshot_report(
        args.repo_root,
        contract_path=args.contract,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.snapshot_materialization_ready else 1


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _issue(
    issues: list[Vdefmd6PreShockSnapshotIssue],
    code: str,
    message: str,
    path: Path | None = None,
) -> None:
    issues.append(
        Vdefmd6PreShockSnapshotIssue(
            code=code,
            message=message,
            path=str(path) if path is not None else None,
        )
    )


def _load_contract(
    path: Path,
    issues: list[Vdefmd6PreShockSnapshotIssue],
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


def _build_summary() -> dict[str, object]:
    batch = build_vdefmd6_pre_shock_snapshot_batch(
        build_vdefmd6_population(),
        period=CONTRACT_PERIOD,
        rng=random.Random(CONTRACT_SEED),
    )
    rule_counts = Counter(item.rule_kind.value for item in batch.insurance_snapshots)
    return {
        "contract_period": batch.period,
        "contract_seed": CONTRACT_SEED,
        "active_insurer_count": len(batch.active_insurer_ids),
        "insurance_snapshot_count": len(batch.insurance_snapshots),
        "damage_snapshot_count": len(batch.damage_snapshots),
        "policyholder_id_start": batch.insurance_snapshots[0].policyholder_id,
        "policyholder_id_end": batch.insurance_snapshots[-1].policyholder_id,
        "rule_counts": dict(sorted(rule_counts.items())),
        "uniform_value_count": batch.draw_summary.uniform_values,
        "normal_value_count": batch.draw_summary.normal_values,
        "damage_threshold_uniform_value_count": (
            batch.draw_summary.damage_threshold_uniform_values
        ),
        "insurance_uniform_value_count": batch.draw_summary.insurance_uniform_values,
    }


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    summary: dict[str, object],
    issues: list[Vdefmd6PreShockSnapshotIssue],
) -> int:
    expected = {
        "schema_version": CONTRACT_VERSION,
        "model_id": "Vdefmd6",
        "scope": "single_pre_shock_period_snapshot_materialization",
        "expected": summary,
        "draw_policy_id": VDEFMD6_PRE_SHOCK_DRAW_POLICY_ID,
        "draw_order": list(_DRAW_ORDER),
        "blocker_codes": list(_BLOCKER_CODES),
        "boundaries": _BOUNDARIES,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            _issue(issues, f"{key}_mismatch", f"contract field differs: {key}", path)
    return _validate_source_anchors(root, contract, issues)


def _validate_source_anchors(
    root: Path,
    contract: dict[str, object],
    issues: list[Vdefmd6PreShockSnapshotIssue],
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
