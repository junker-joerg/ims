from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import random
from typing import Sequence

from ims.model.vdefmd6_population import build_vdefmd6_population
from ims.model.vdefmd6_vu_snapshots import (
    VDEFMD6_VU_DRAW_POLICY_ID,
    build_vdefmd6_vu_snapshot_batch,
)


CONTRACT_VERSION = "pr79-v1"
DEFAULT_CONTRACT_PATH = Path("tests/fixtures/vdefmd6_vu_snapshot_contract.json")
CONTRACT_PERIOD = 2
CONTRACT_SEED = 790001

_DRAW_ORDER = (
    "insurer_id_ascending",
    "rule_1_four_uniform_values",
    "rule_2_four_normal_values",
    "rules_3_to_9_no_rng_values",
)
_BLOCKER_CODES = (
    "information_cost_settlement_application_missing",
    "combined_vu_vn_period_application_missing",
    "historical_same_slot_rng_order_open",
)
_BOUNDARIES = {
    "legacy_rows_used_as_generation_input": False,
    "snapshot_materialization_performed": True,
    "bav_service_executed": False,
    "rng_draws_performed": True,
    "runner_started": False,
    "simulation_performed": False,
    "historical_rng_equality_claimed": False,
    "historical_full_equality_claimed": False,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6VUSnapshotIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True, slots=True)
class Vdefmd6VUSnapshotReport:
    repo_root: str
    contract_path: str
    summary: dict[str, object]
    source_anchor_count: int
    issues: tuple[Vdefmd6VUSnapshotIssue, ...]
    mode: str = "vdefmd6_vu_snapshot_materialization"

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
            "draw_policy_id": VDEFMD6_VU_DRAW_POLICY_ID,
            "draw_order": list(_DRAW_ORDER),
            "blocker_codes": list(_BLOCKER_CODES),
            "snapshot_materialization_ready": self.snapshot_materialization_ready,
            "bav_previous_period_inputs_ready": self.snapshot_materialization_ready,
            "information_cost_origin_evidenced": self.snapshot_materialization_ready,
            "information_cost_application_ready": False,
            "independent_periods_2_49_ready": False,
            "full_state_projection_ready": False,
            "generation_ready": False,
            **_BOUNDARIES,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_vu_snapshot_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
) -> Vdefmd6VUSnapshotReport:
    root = Path(repo_root).expanduser().resolve()
    path = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    issues: list[Vdefmd6VUSnapshotIssue] = []
    contract = _load_contract(path, issues)
    summary = _build_summary()
    anchor_count = _validate_contract(root, path, contract, summary, issues)
    return Vdefmd6VUSnapshotReport(
        repo_root=str(root),
        contract_path=str(path),
        summary=summary,
        source_anchor_count=anchor_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_vu_snapshot_report",
        description="Prueft die PR-79-VU-Snapshotmaterialisierung.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_vu_snapshot_report(
        args.repo_root,
        contract_path=args.contract,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.snapshot_materialization_ready else 1


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _issue(
    issues: list[Vdefmd6VUSnapshotIssue],
    code: str,
    message: str,
    path: Path | None = None,
) -> None:
    issues.append(
        Vdefmd6VUSnapshotIssue(
            code=code,
            message=message,
            path=str(path) if path is not None else None,
        )
    )


def _load_contract(
    path: Path,
    issues: list[Vdefmd6VUSnapshotIssue],
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
    batch = build_vdefmd6_vu_snapshot_batch(
        build_vdefmd6_population(),
        period=CONTRACT_PERIOD,
        rng=random.Random(CONTRACT_SEED),
    )
    foreign_counts = {
        kind: sum(item.rule_kind.value == kind for item in batch.foreign_info_snapshots)
        for kind in ("dumping", "average", "attack")
    }
    boundary = batch.information_cost_boundary
    return {
        "contract_period": batch.period,
        "contract_seed": CONTRACT_SEED,
        "snapshot_count": batch.snapshot_count,
        "snapshot_family_counts": {
            "random_uniform": len(batch.random_uniform_snapshots),
            "random_normal": len(batch.random_normal_snapshots),
            "reserve_markup": len(batch.reserve_markup_snapshots),
            "net_switcher_markup": len(batch.net_switcher_markup_snapshots),
            "market_share_markup": len(batch.market_share_markup_snapshots),
            "expected_claim": len(batch.expected_claim_snapshots),
            "foreign_info": len(batch.foreign_info_snapshots),
        },
        "foreign_info_kind_counts": foreign_counts,
        "active_insurer_input_count": len(
            batch.bav_previous_period_inputs.active_insurer_ids_t_minus_1
        ),
        "active_policyholder_input_count": len(
            batch.bav_previous_period_inputs.active_policyholder_ids_t_minus_1
        ),
        "uniform_value_count": batch.uniform_value_count,
        "normal_value_count": batch.normal_value_count,
        "interest_rate": batch.bav_previous_period_inputs.interest_rate,
        "information_cost_per_lookup": (
            batch.bav_previous_period_inputs.information_cost_per_lookup
        ),
        "historical_information_cost_rules": list(boundary.historical_rules),
        "historical_wealth_subtraction_evidenced": (
            boundary.historical_wealth_subtraction_evidenced
        ),
        "python_settlement_snapshot_accepts_cost": (
            boundary.python_settlement_snapshot_accepts_cost
        ),
    }


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    summary: dict[str, object],
    issues: list[Vdefmd6VUSnapshotIssue],
) -> int:
    expected = {
        "schema_version": CONTRACT_VERSION,
        "model_id": "Vdefmd6",
        "scope": "single_pre_shock_period_vu_snapshot_materialization",
        "expected": summary,
        "draw_policy_id": VDEFMD6_VU_DRAW_POLICY_ID,
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
    issues: list[Vdefmd6VUSnapshotIssue],
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
