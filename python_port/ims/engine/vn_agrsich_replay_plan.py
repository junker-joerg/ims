from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path

from ims.engine.vn_agrsich_replay import (
    VNAgrsichLegacyTarget,
    VNAgrsichReplayRunResult,
    run_vn_agrsich_replay_from_mappings,
)


@dataclass(slots=True)
class VNAgrsichReplayPeriodUpdate:
    period: int
    logtime: int | None
    max_periods: int | None
    run_index: int
    rng_seed: int
    insurer_updates: list[dict]
    policyholder_updates: list[dict]
    vn_settlement_snapshots: list[dict] | None
    vn_damage_settlement_snapshots: list[dict] | None


@dataclass(slots=True)
class VNAgrsichReplayPlan:
    metadata: dict
    legacy_targets: list[dict]
    legacy_report_name: str | None
    carry_forward_vn_state: bool
    base_snapshot: dict
    period_updates: list[VNAgrsichReplayPeriodUpdate]


def _optional_snapshot_list(item: dict, key: str) -> list[dict] | None:
    if key not in item:
        return None
    value = item[key]
    if not isinstance(value, list):
        raise ValueError(f"VN Agrsich replay plan field {key} must be a list")
    return list(value)


def _period_update_list(item: dict, key: str) -> list[dict]:
    value = item.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"VN Agrsich replay plan field {key} must be a list")
    return list(value)


def _load_plan(data: dict) -> VNAgrsichReplayPlan:
    if not isinstance(data, dict):
        raise ValueError("VN Agrsich replay plan must be a JSON object")
    update_items = data.get("period_updates")
    if not isinstance(update_items, list) or not update_items:
        raise ValueError("VN Agrsich replay plan must contain a non-empty period_updates list")

    period_updates: list[VNAgrsichReplayPeriodUpdate] = []
    for item in update_items:
        if not isinstance(item, dict):
            raise ValueError("VN Agrsich replay period update must be an object")
        context_data = item.get("context", {})
        if not isinstance(context_data, dict):
            raise ValueError("VN Agrsich replay period update context must be an object")
        period_updates.append(
            VNAgrsichReplayPeriodUpdate(
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
                vn_settlement_snapshots=_optional_snapshot_list(item, "vn_settlement_snapshots"),
                vn_damage_settlement_snapshots=_optional_snapshot_list(
                    item,
                    "vn_damage_settlement_snapshots",
                ),
            )
        )

    base_snapshot = data.get("base_snapshot")
    if not isinstance(base_snapshot, dict):
        raise ValueError("VN Agrsich replay plan must contain a base_snapshot object")

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("VN Agrsich replay plan metadata must be an object")

    legacy_targets = data.get("legacy_targets", [])
    if not isinstance(legacy_targets, list):
        raise ValueError("VN Agrsich replay plan field legacy_targets must be a list")

    legacy_report_name_value = data.get("legacy_report_name")
    legacy_report_name = str(legacy_report_name_value) if legacy_report_name_value is not None else None

    carry_forward_vn_state = data.get("carry_forward_vn_state", False)
    if not isinstance(carry_forward_vn_state, bool):
        raise ValueError("VN Agrsich replay plan field carry_forward_vn_state must be a boolean")

    return VNAgrsichReplayPlan(
        metadata=metadata,
        legacy_targets=list(legacy_targets),
        legacy_report_name=legacy_report_name,
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


def build_vn_agrsich_replay_fixture_from_period_plan(data: dict) -> dict:
    plan = _load_plan(data)
    periods: list[dict] = []
    for update in plan.period_updates:
        snapshot = deepcopy(plan.base_snapshot)
        context = snapshot.setdefault("context", {})
        if not isinstance(context, dict):
            raise ValueError("VN Agrsich replay base_snapshot context must be an object")
        context["period"] = update.period
        if update.logtime is not None:
            context["logtime"] = update.logtime
        if update.max_periods is not None:
            context["max_periods"] = update.max_periods
        context["run_index"] = update.run_index
        context["rng_seed"] = update.rng_seed

        _apply_entity_updates(snapshot, "insurers", update.insurer_updates)
        _apply_entity_updates(snapshot, "policyholders", update.policyholder_updates)
        if update.vn_settlement_snapshots is not None:
            snapshot["vn_settlement_snapshots"] = deepcopy(update.vn_settlement_snapshots)
        if update.vn_damage_settlement_snapshots is not None:
            snapshot["vn_damage_settlement_snapshots"] = deepcopy(update.vn_damage_settlement_snapshots)
        periods.append(snapshot)

    fixture = {
        "metadata": dict(plan.metadata),
        "carry_forward_vn_state": plan.carry_forward_vn_state,
        "periods": periods,
    }
    if plan.legacy_targets:
        fixture["legacy_targets"] = deepcopy(plan.legacy_targets)
    if plan.legacy_report_name is not None:
        fixture["legacy_report_name"] = plan.legacy_report_name
    return fixture


def _load_legacy_targets_from_plan_fixture(
    fixture: dict,
    *,
    plan_base_path: Path,
) -> list[VNAgrsichLegacyTarget]:
    targets: list[VNAgrsichLegacyTarget] = []
    for item in fixture.get("legacy_targets", []):
        if not isinstance(item, dict):
            raise ValueError("VN Agrsich replay plan legacy target must be an object")
        legacy_path = Path(str(item["legacy_path"]))
        if not legacy_path.is_absolute():
            legacy_path = plan_base_path / legacy_path
        subject_type = str(item.get("subject_type", "policyholder"))
        if subject_type not in ("insurer", "policyholder"):
            raise ValueError(f"unsupported VN Agrsich replay plan legacy target subject_type: {subject_type}")
        targets.append(
            VNAgrsichLegacyTarget(
                legacy_path=legacy_path,
                export_filename=str(item["export_filename"]),
                subject_type=subject_type,
                tolerance=float(item.get("tolerance", 0.05)),
            )
        )
    return targets


def run_vn_agrsich_replay_from_period_plan_fixture(
    path: str | Path,
    output_dir: str | Path,
) -> VNAgrsichReplayRunResult:
    plan_path = Path(path).resolve()
    with plan_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    replay_fixture = build_vn_agrsich_replay_fixture_from_period_plan(data)
    return run_vn_agrsich_replay_from_mappings(
        replay_fixture["periods"],
        output_dir,
        carry_forward_vn_state=bool(replay_fixture["carry_forward_vn_state"]),
        legacy_targets=_load_legacy_targets_from_plan_fixture(
            replay_fixture,
            plan_base_path=plan_path.parent,
        ),
        legacy_report_name=(
            str(replay_fixture["legacy_report_name"])
            if replay_fixture.get("legacy_report_name") is not None
            else None
        ),
    )
