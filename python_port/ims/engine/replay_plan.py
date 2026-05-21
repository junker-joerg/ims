from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path

from ims.engine.replay_runner import ReplayRunResult, run_agrsich_replay_from_mapping


@dataclass(slots=True)
class ReplayPeriodUpdate:
    period: int
    logtime: int | None
    max_periods: int | None
    run_index: int
    rng_seed: int
    insurer_updates: list[dict]
    policyholder_updates: list[dict]


@dataclass(slots=True)
class ReplayPlan:
    metadata: dict
    legacy_window: dict | None
    carry_forward_insurer_state: bool
    base_snapshot: dict
    period_updates: list[ReplayPeriodUpdate]


def _load_plan(data: dict) -> ReplayPlan:
    if not isinstance(data, dict):
        raise ValueError("replay plan must be a JSON object")
    update_items = data.get("period_updates")
    if not isinstance(update_items, list) or not update_items:
        raise ValueError("replay plan must contain a non-empty period_updates list")

    period_updates: list[ReplayPeriodUpdate] = []
    for item in update_items:
        if not isinstance(item, dict):
            raise ValueError("period update must be an object")
        context_data = item.get("context", {})
        if not isinstance(context_data, dict):
            raise ValueError("period update context must be an object")
        period_updates.append(
            ReplayPeriodUpdate(
                period=int(context_data["period"]),
                logtime=(
                    int(context_data["logtime"])
                    if context_data.get("logtime") is not None
                    else None
                ),
                max_periods=(
                    int(context_data["max_periods"])
                    if context_data.get("max_periods") is not None
                    else None
                ),
                run_index=int(context_data.get("run_index", 0)),
                rng_seed=int(context_data.get("rng_seed", 0)),
                insurer_updates=_period_update_list(item, "insurers"),
                policyholder_updates=_period_update_list(item, "policyholders"),
            )
        )

    base_snapshot = data.get("base_snapshot")
    if not isinstance(base_snapshot, dict):
        raise ValueError("replay plan must contain a base_snapshot object")

    legacy_window = data.get("legacy_window")
    if legacy_window is not None and not isinstance(legacy_window, dict):
        raise ValueError("legacy_window must be an object")

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")

    carry_forward_insurer_state = data.get("carry_forward_insurer_state", False)
    if not isinstance(carry_forward_insurer_state, bool):
        raise ValueError("replay plan field carry_forward_insurer_state must be a boolean")

    return ReplayPlan(
        metadata=metadata,
        legacy_window=legacy_window,
        carry_forward_insurer_state=carry_forward_insurer_state,
        base_snapshot=base_snapshot,
        period_updates=period_updates,
    )


def _period_update_list(item: dict, key: str) -> list[dict]:
    value = item.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"replay plan field {key} must be a list")
    return list(value)


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


def build_replay_fixture_from_period_plan(data: dict) -> dict:
    plan = _load_plan(data)
    snapshots: list[dict] = []
    for update in plan.period_updates:
        snapshot = deepcopy(plan.base_snapshot)
        context = snapshot.setdefault("context", {})
        if not isinstance(context, dict):
            raise ValueError("base_snapshot context must be an object")
        context["period"] = update.period
        if update.logtime is not None:
            context["logtime"] = update.logtime
        if update.max_periods is not None:
            context["max_periods"] = update.max_periods
        context["run_index"] = update.run_index
        context["rng_seed"] = update.rng_seed

        _apply_entity_updates(snapshot, "insurers", update.insurer_updates)
        _apply_entity_updates(snapshot, "policyholders", update.policyholder_updates)
        snapshots.append(snapshot)

    replay_fixture: dict = {
        "metadata": dict(plan.metadata),
        "carry_forward_insurer_state": plan.carry_forward_insurer_state,
        "snapshots": snapshots,
    }
    if plan.legacy_window is not None:
        replay_fixture["legacy_window"] = dict(plan.legacy_window)
    return replay_fixture


def run_agrsich_replay_from_period_plan_fixture(path: str | Path, output_dir: str | Path) -> ReplayRunResult:
    plan_path = Path(path).resolve()
    with plan_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    replay_fixture = build_replay_fixture_from_period_plan(data)
    return run_agrsich_replay_from_mapping(
        replay_fixture,
        output_dir,
        fixture_base_path=plan_path.parent,
    )
