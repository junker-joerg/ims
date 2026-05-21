from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path

from ims.engine.explicit_period_runner import (
    ExplicitMultiPeriodRunResult,
    run_explicit_multi_period_from_mappings,
)


_SNAPSHOT_KEYS = (
    "vu_foreign_info_rule_snapshots",
    "vu_random_uniform_rule_snapshots",
    "vu_random_normal_rule_snapshots",
    "vu_reserve_markup_rule_snapshots",
    "vu_net_switcher_markup_rule_snapshots",
    "vu_expected_claim_rule_snapshots",
    "vu_market_share_markup_rule_snapshots",
    "vu_free_linear_rule_snapshots",
    "vn_damage_settlement_snapshots",
    "vn_settlement_snapshots",
)


@dataclass(slots=True)
class ExplicitPeriodPlanUpdate:
    period: int
    run_index: int
    rng_seed: int
    insurer_updates: list[dict]
    policyholder_updates: list[dict]
    snapshot_updates: dict[str, list[dict]]


@dataclass(slots=True)
class ExplicitPeriodPlan:
    metadata: dict
    carry_forward_vu_state: bool
    carry_forward_vn_state: bool
    base_snapshot: dict
    period_updates: list[ExplicitPeriodPlanUpdate]


def _optional_snapshot_updates(item: dict) -> dict[str, list[dict]]:
    updates: dict[str, list[dict]] = {}
    for key in _SNAPSHOT_KEYS:
        if key not in item:
            continue
        value = item[key]
        if not isinstance(value, list):
            raise ValueError(f"explicit VU/VN period plan field {key} must be a list")
        updates[key] = list(value)
    return updates


def _load_plan(data: dict) -> ExplicitPeriodPlan:
    if not isinstance(data, dict):
        raise ValueError("explicit VU/VN period plan must be a JSON object")
    update_items = data.get("period_updates")
    if not isinstance(update_items, list) or not update_items:
        raise ValueError("explicit VU/VN period plan must contain a non-empty period_updates list")

    period_updates: list[ExplicitPeriodPlanUpdate] = []
    for item in update_items:
        if not isinstance(item, dict):
            raise ValueError("explicit VU/VN period update must be an object")
        context_data = item.get("context", {})
        if not isinstance(context_data, dict):
            raise ValueError("explicit VU/VN period update context must be an object")
        period_updates.append(
            ExplicitPeriodPlanUpdate(
                period=int(context_data["period"]),
                run_index=int(context_data.get("run_index", 0)),
                rng_seed=int(context_data.get("rng_seed", 0)),
                insurer_updates=list(item.get("insurers", [])),
                policyholder_updates=list(item.get("policyholders", [])),
                snapshot_updates=_optional_snapshot_updates(item),
            )
        )

    base_snapshot = data.get("base_snapshot")
    if not isinstance(base_snapshot, dict):
        raise ValueError("explicit VU/VN period plan must contain a base_snapshot object")

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("explicit VU/VN period plan metadata must be an object")

    carry_forward_vu_state = data.get("carry_forward_vu_state", False)
    if not isinstance(carry_forward_vu_state, bool):
        raise ValueError("explicit VU/VN period plan field carry_forward_vu_state must be a boolean")

    carry_forward_vn_state = data.get("carry_forward_vn_state", False)
    if not isinstance(carry_forward_vn_state, bool):
        raise ValueError("explicit VU/VN period plan field carry_forward_vn_state must be a boolean")

    return ExplicitPeriodPlan(
        metadata=metadata,
        carry_forward_vu_state=carry_forward_vu_state,
        carry_forward_vn_state=carry_forward_vn_state,
        base_snapshot=base_snapshot,
        period_updates=period_updates,
    )


def _apply_entity_updates(snapshot: dict, entity_key: str, updates: list[dict]) -> None:
    entities = snapshot.get(entity_key)
    if not isinstance(entities, list):
        raise ValueError(f"{entity_key} must be a list")

    entities_by_id = {int(entity["entity_id"]): entity for entity in entities}
    for update in updates:
        if not isinstance(update, dict):
            raise ValueError(f"{entity_key} update must be an object")
        entity_id = int(update["entity_id"])
        if entity_id not in entities_by_id:
            raise ValueError(f"unknown {entity_key} entity_id: {entity_id}")
        entities_by_id[entity_id].update(update)


def build_explicit_period_fixture_from_plan(data: dict) -> dict:
    plan = _load_plan(data)
    periods: list[dict] = []
    for update in plan.period_updates:
        snapshot = deepcopy(plan.base_snapshot)
        context = snapshot.setdefault("context", {})
        if not isinstance(context, dict):
            raise ValueError("explicit VU/VN base_snapshot context must be an object")
        context["period"] = update.period
        context["run_index"] = update.run_index
        context["rng_seed"] = update.rng_seed

        _apply_entity_updates(snapshot, "insurers", update.insurer_updates)
        _apply_entity_updates(snapshot, "policyholders", update.policyholder_updates)
        for key, value in update.snapshot_updates.items():
            snapshot[key] = deepcopy(value)
        periods.append(snapshot)

    return {
        "metadata": dict(plan.metadata),
        "carry_forward_vu_state": plan.carry_forward_vu_state,
        "carry_forward_vn_state": plan.carry_forward_vn_state,
        "periods": periods,
    }


def run_explicit_multi_period_from_plan_fixture(
    path: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> ExplicitMultiPeriodRunResult:
    plan_path = Path(path).resolve()
    with plan_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    fixture = build_explicit_period_fixture_from_plan(data)
    return run_explicit_multi_period_from_mappings(
        fixture["periods"],
        output_dir=output_dir,
        carry_forward_vu_state=bool(fixture["carry_forward_vu_state"]),
        carry_forward_vn_state=bool(fixture["carry_forward_vn_state"]),
    )
