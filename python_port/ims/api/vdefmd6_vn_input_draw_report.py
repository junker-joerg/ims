from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from ims.model.vdefmd6_population import build_vdefmd6_population


CONTRACT_VERSION = "pr77-v1"
DEFAULT_CONTRACT_PATH = Path("tests/fixtures/vdefmd6_vn_input_draw_contract.json")

_RULES = (
    {
        "rule_id": 1,
        "rule_kind": "compulsory",
        "rule_class": 1,
        "population_ranges": [
            {"start": 1, "end": 15, "activation_period": 1},
        ],
        "pre_shock_active_count": 15,
        "insurance_inputs": [
            "active_insurer_ids",
            "initial_decisions",
            "draws.insurer_choice_draws",
        ],
        "periods_2_49_decision_draws": "two active-insurer choices with rejection loops",
    },
    {
        "rule_id": 2,
        "rule_kind": "random",
        "rule_class": 1,
        "population_ranges": [
            {"start": 16, "end": 30, "activation_period": 1},
            {"start": 191, "end": 200, "activation_period": 50},
        ],
        "pre_shock_active_count": 15,
        "insurance_inputs": [
            "parameters.insurance_thresholds_normal",
            "active_insurer_ids",
            "initial_decisions",
            "draws.status_draws",
            "draws.insurer_choice_draws",
        ],
        "periods_2_49_decision_draws": "two status draws then two active-insurer choices with rejection loops",
    },
    {
        "rule_id": 3,
        "rule_kind": "preference",
        "rule_class": 2,
        "population_ranges": [
            {"start": 31, "end": 60, "activation_period": 1},
            {"start": 151, "end": 190, "activation_period": 50},
        ],
        "pre_shock_active_count": 30,
        "insurance_inputs": [
            "parameters.insurance_thresholds_normal",
            "damage_probabilities",
            "active_insurer_ids",
            "initial_decisions",
            "insurer_inputs.advertising_current_sector",
            "draws.fallback_insurer_choice_draws",
        ],
        "periods_2_49_decision_draws": "conditional fallback choices when no positive advertising preference exists",
    },
    {
        "rule_id": 4,
        "rule_kind": "search_history",
        "rule_class": 2,
        "population_ranges": [
            {"start": 61, "end": 90, "activation_period": 1},
        ],
        "pre_shock_active_count": 30,
        "insurance_inputs": [
            "parameters.insurance_thresholds_normal",
            "damage_probabilities",
            "active_insurer_ids",
            "initial_decisions",
            "history",
            "draws.fallback_insurer_choice_draws",
        ],
        "periods_2_49_decision_draws": "conditional fallback choices when no insured premium history exists",
    },
    {
        "rule_id": 5,
        "rule_kind": "sample_search",
        "rule_class": 3,
        "population_ranges": [
            {"start": 91, "end": 120, "activation_period": 1},
        ],
        "pre_shock_active_count": 30,
        "insurance_inputs": [
            "parameters.insurance_thresholds_normal",
            "parameters.sample_sizes_normal",
            "market_damage_indicator",
            "active_insurer_ids",
            "initial_decisions",
            "insurer_inputs.premiums_current_sector",
            "draws.insurer_choice_draws_by_sector",
            "information_cost_per_sample",
        ],
        "periods_2_49_decision_draws": "eight active-insurer sample choices per sector in Vdefmd6",
    },
    {
        "rule_id": 6,
        "rule_kind": "best_info",
        "rule_class": 3,
        "population_ranges": [
            {"start": 121, "end": 150, "activation_period": 1},
        ],
        "pre_shock_active_count": 30,
        "insurance_inputs": [
            "parameters.insurance_thresholds_normal",
            "market_damage_indicator",
            "active_insurer_ids",
            "initial_decisions",
            "insurer_inputs.premiums_current_sector",
            "information_cost_per_insurer",
        ],
        "periods_2_49_decision_draws": "none; minimum current premium among active insurers",
    },
)

_COMMON_DAMAGE_INPUTS = (
    "parameters.damage_intercept_normal",
    "parameters.damage_factor_normal",
    "damage_thresholds",
    "draws.trigger_draws",
    "draws.amount_draws",
    "change_shock=false",
)

_COMMON_SETTLEMENT_INPUTS = (
    "insurance_decisions",
    "previous_wealth",
    "previous_wealth_sector",
    "insurer.premiums_current_sector",
    "insurer.reserves_current_sector",
    "insurer.claim_sum_current_sector",
    "insurer.claim_count_current_sector",
    "insurer.policyholders_current_sector",
)

_STAGE_ORDER = (
    {"position": 1, "stage": "damage_realization", "scope": "sector 1 then sector 2"},
    {"position": 2, "stage": "insurance_decision", "scope": "rule-specific"},
    {"position": 3, "stage": "settlement", "scope": "sector 1"},
    {"position": 4, "stage": "settlement", "scope": "sector 2"},
    {"position": 5, "stage": "wealth_update", "scope": "policyholder total"},
)

_DRAW_ORDER = {
    "damage_sector_statement_order": ["sector_1", "sector_2"],
    "within_sector_normal_call_order": "unspecified_by_c_expression",
    "historical_normal_uniform_draws_per_call": 12,
    "modern_python_damage_order": [
        "sector_1_trigger",
        "sector_1_amount",
        "sector_2_trigger",
        "sector_2_amount",
    ],
    "modern_damage_order_is_historical_claim": False,
    "decision_draws_follow_damage_statements": True,
    "historical_subject_same_slot_order_known": False,
    "historical_draw_order_fully_bound": False,
}

_RUNNER_BRIDGE = {
    "current_runner_stage_order": [
        "insurance_rule_snapshots",
        "damage_settlement_snapshots",
        "settlement_snapshots",
    ],
    "matches_historical_random_consumption_order": False,
    "required_next_step": "materialize explicit damage and decision draws before runner application",
    "automatic_snapshot_derivation_ready": False,
}

_BLOCKER_CODES = (
    "within_sector_c_normal_order_unspecified",
    "historical_subject_same_slot_order_missing",
    "automatic_vdefmd6_snapshot_derivation_missing",
    "pre_shock_full_state_execution_missing",
)

_BOUNDARIES = {
    "legacy_output_used_as_input": False,
    "writes_performed": False,
    "execution_performed": False,
    "runner_started": False,
    "rng_draws_performed": False,
    "simulation_performed": False,
    "historical_rng_equality_claimed": False,
    "historical_full_equality_claimed": False,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6VNInputDrawIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True, slots=True)
class Vdefmd6VNInputDrawReport:
    repo_root: str
    contract_path: str
    summary: dict[str, object]
    source_anchor_count: int
    issues: tuple[Vdefmd6VNInputDrawIssue, ...]
    mode: str = "vdefmd6_vn_input_draw_mapping"

    @property
    def mapping_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "input_draw_path_mapped" if self.mapping_ready else "error",
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "summary": dict(self.summary),
            "source_anchor_count": self.source_anchor_count,
            "rule_mappings": [dict(item) for item in _RULES],
            "common_damage_inputs": list(_COMMON_DAMAGE_INPUTS),
            "common_settlement_inputs": list(_COMMON_SETTLEMENT_INPUTS),
            "historical_stage_order": [dict(item) for item in _STAGE_ORDER],
            "draw_order": dict(_DRAW_ORDER),
            "runner_bridge": dict(_RUNNER_BRIDGE),
            "blocker_codes": list(_BLOCKER_CODES),
            "mapping_ready": self.mapping_ready,
            "policyholder_claim_path_mapped": self.mapping_ready,
            "settlement_write_path_mapped": self.mapping_ready,
            "policyholder_claim_origin_evidenced_for_generation": False,
            "settlement_state_origin_evidenced_for_generation": False,
            "historical_draw_order_fully_bound": False,
            "independent_periods_2_49_ready": False,
            "generation_ready": False,
            **_BOUNDARIES,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_vn_input_draw_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
) -> Vdefmd6VNInputDrawReport:
    root = Path(repo_root).expanduser().resolve()
    path = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    issues: list[Vdefmd6VNInputDrawIssue] = []
    contract = _load_contract(path, issues)
    summary = _build_summary()
    anchor_count = _validate_contract(root, path, contract, summary, issues)
    return Vdefmd6VNInputDrawReport(
        repo_root=str(root),
        contract_path=str(path),
        summary=summary,
        source_anchor_count=anchor_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_vn_input_draw_report",
        description="Prueft die read-only Vdefmd6-VN-Eingabe- und Draw-Karte.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_vn_input_draw_report(
        args.repo_root,
        contract_path=args.contract,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.mapping_ready else 1


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _issue(
    issues: list[Vdefmd6VNInputDrawIssue],
    code: str,
    message: str,
    path: Path | None = None,
) -> None:
    issues.append(
        Vdefmd6VNInputDrawIssue(
            code=code,
            message=message,
            path=str(path) if path is not None else None,
        )
    )


def _load_contract(
    path: Path,
    issues: list[Vdefmd6VNInputDrawIssue],
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
    population = build_vdefmd6_population()
    pre_shock = [
        item
        for item in population.policyholder_definitions
        if item.activation.activation_period <= 49
    ]
    deferred = [
        item
        for item in population.policyholder_definitions
        if item.activation.activation_period > 49
    ]
    return {
        "period_start": 1,
        "period_end": 49,
        "policyholder_count": len(population.policyholder_definitions),
        "pre_shock_active_policyholder_count": len(pre_shock),
        "deferred_policyholder_count": len(deferred),
        "mapped_rule_count": len(_RULES),
        "pre_shock_rule_counts": {
            str(rule_id): sum(item.action.rule_id == rule_id for item in pre_shock)
            for rule_id in range(1, 7)
        },
        "historical_damage_normal_calls_per_active_policyholder": 4,
        "historical_uniform_draws_per_normal_call": 12,
        "historical_minimum_damage_uniform_draws_per_active_policyholder": 48,
        "historical_minimum_damage_uniform_draws_per_pre_shock_period": len(pre_shock) * 48,
    }


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    summary: dict[str, object],
    issues: list[Vdefmd6VNInputDrawIssue],
) -> int:
    expected = {
        "schema_version": CONTRACT_VERSION,
        "model_id": "Vdefmd6",
        "scope": "pre_shock_periods_1_49",
        "expected": summary,
        "rule_mappings": list(_RULES),
        "common_damage_inputs": list(_COMMON_DAMAGE_INPUTS),
        "common_settlement_inputs": list(_COMMON_SETTLEMENT_INPUTS),
        "historical_stage_order": list(_STAGE_ORDER),
        "draw_order": _DRAW_ORDER,
        "runner_bridge": _RUNNER_BRIDGE,
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
    issues: list[Vdefmd6VNInputDrawIssue],
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
