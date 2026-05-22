from dataclasses import dataclass, field
import json
from pathlib import Path

from ims.engine.context import SimulationContext
from ims.model.entities import BAV, Insurer, Policyholder
from ims.model.vn_rules import (
    VNDamageSettlementSnapshot,
    VNSettlementSnapshot,
    load_vn_insurance_decisions_from_mapping,
    load_vn_damage_settlement_snapshots_from_mapping,
    load_vn_settlement_snapshots_from_mapping,
)
from ims.model.vn_insurance_rules import (
    VNInsuranceRuleKind,
    VNInsuranceRuleSnapshot,
    load_vn_insurance_rule_snapshots_from_mapping,
    load_vn_preference_insurer_inputs_from_mapping,
    load_vn_sample_search_insurer_inputs_from_mapping,
    load_vn_search_insurance_history_from_mapping,
)
from ims.model.vu_rules import (
    VUForeignInfoRuleSnapshot,
    VUExpectedClaimRuleSnapshot,
    VUFreeLinearRuleSnapshot,
    VUNetSwitcherMarkupRuleSnapshot,
    VURandomNormalRuleSnapshot,
    VURandomUniformRuleSnapshot,
    VUReserveMarkupRuleSnapshot,
    VUMarketShareMarkupRuleSnapshot,
    load_vu_expected_claim_rule_snapshots_from_mapping,
    load_vu_free_linear_rule_snapshots_from_mapping,
    load_vu_foreign_info_rule_snapshots_from_mapping,
    load_vu_market_share_markup_rule_snapshots_from_mapping,
    load_vu_net_switcher_markup_rule_snapshots_from_mapping,
    load_vu_random_normal_rule_snapshots_from_mapping,
    load_vu_random_uniform_rule_snapshots_from_mapping,
    load_vu_reserve_markup_rule_snapshots_from_mapping,
)


@dataclass(slots=True)
class LoadedScenario:
    """Minimales Ergebnis eines geladenen Szenarios."""

    context: SimulationContext
    bav: BAV
    insurers: list[Insurer]
    policyholders: list[Policyholder]
    vu_foreign_info_rule_snapshots: list[VUForeignInfoRuleSnapshot] = field(default_factory=list)
    vu_random_uniform_rule_snapshots: list[VURandomUniformRuleSnapshot] = field(default_factory=list)
    vu_random_normal_rule_snapshots: list[VURandomNormalRuleSnapshot] = field(default_factory=list)
    vu_reserve_markup_rule_snapshots: list[VUReserveMarkupRuleSnapshot] = field(default_factory=list)
    vu_net_switcher_markup_rule_snapshots: list[VUNetSwitcherMarkupRuleSnapshot] = field(default_factory=list)
    vu_expected_claim_rule_snapshots: list[VUExpectedClaimRuleSnapshot] = field(default_factory=list)
    vu_market_share_markup_rule_snapshots: list[VUMarketShareMarkupRuleSnapshot] = field(default_factory=list)
    vu_free_linear_rule_snapshots: list[VUFreeLinearRuleSnapshot] = field(default_factory=list)
    vn_insurance_rule_snapshots: list[VNInsuranceRuleSnapshot] = field(default_factory=list)
    vn_damage_settlement_snapshots: list[VNDamageSettlementSnapshot] = field(default_factory=list)
    vn_settlement_snapshots: list[VNSettlementSnapshot] = field(default_factory=list)


class ScenarioValidationError(ValueError):
    """Signalisiert ein grob ungueltiges Szenarioformat."""


def _int_list(value: object, *, default: list[int]) -> list[int]:
    if not isinstance(value, list):
        return list(default)
    return [int(item) for item in value]


def _float_list(value: object, *, default: list[float]) -> list[float]:
    if not isinstance(value, list):
        return list(default)
    return [float(item) for item in value]


def _two_float_vector(value: object, *, fallback: float) -> list[float]:
    if isinstance(value, list):
        values = [float(entry) for entry in value[:2]]
        if len(values) == 1:
            return [values[0], values[0]]
        if len(values) >= 2:
            return values
        return [fallback, fallback]
    if value is not None:
        scalar = float(value)
        return [scalar, scalar]
    return [fallback, fallback]


def _insurer_reserves_vector(item: dict[str, object]) -> list[float]:
    current_value = item.get("reserves_current")
    if isinstance(current_value, list):
        values = [float(entry) for entry in current_value[:2]]
        if len(values) == 1:
            return [values[0], values[0]]
        if len(values) >= 2:
            return values
        return [0.0, 0.0]
    if current_value is not None:
        value = float(current_value)
        return [value, value]

    previous_value = item.get("reserves_prev", 0.0)
    value = float(previous_value)
    return [value, value]


def _policyholder_chosen_insurer_vector(item: dict[str, object]) -> list[int | None]:
    current_value = item.get("chosen_insurer_sector_current")
    if isinstance(current_value, list):
        values = [int(entry) if entry is not None else None for entry in current_value[:2]]
        if len(values) == 1:
            return [values[0], values[0]]
        if len(values) >= 2:
            return values
        return [None, None]

    scalar_value = item.get("chosen_insurer_current", item.get("insurer_id"))
    if scalar_value is None:
        return [None, None]
    value = int(scalar_value)
    return [value, value]


def _validate_entity_items(items: list[object], *, label: str) -> None:
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ScenarioValidationError(f"{label} entries must be objects: index {index}")
        if "entity_id" not in item:
            raise ScenarioValidationError(f"{label} entries require field: entity_id at index {index}")


def _validate_unique_entity_ids(items: list[object], *, label: str) -> None:
    seen: set[int] = set()
    duplicates: set[int] = set()
    for item in items:
        if not isinstance(item, dict) or "entity_id" not in item:
            continue
        entity_id = int(item["entity_id"])
        if entity_id in seen:
            duplicates.add(entity_id)
        else:
            seen.add(entity_id)
    if duplicates:
        values = ", ".join(str(entity_id) for entity_id in sorted(duplicates))
        raise ScenarioValidationError(f"duplicate {label} entity_id values: {values}")


def _validate_policyholder_insurer_references(
    insurer_items: list[object],
    policyholder_items: list[object],
) -> None:
    insurer_ids = {
        int(item["entity_id"])
        for item in insurer_items
        if isinstance(item, dict) and "entity_id" in item
    }
    unknown_insurer_ids: set[int] = set()
    for item in policyholder_items:
        if not isinstance(item, dict) or item.get("insurer_id") is None:
            continue
        insurer_id = int(item["insurer_id"])
        if insurer_id not in insurer_ids:
            unknown_insurer_ids.add(insurer_id)
    if unknown_insurer_ids:
        values = ", ".join(str(insurer_id) for insurer_id in sorted(unknown_insurer_ids))
        raise ScenarioValidationError(f"policyholder insurer_id references unknown insurers: {values}")


def _validate_vn_settlement_snapshot_references(
    insurer_items: list[object],
    policyholder_items: list[object],
    snapshots: list[VNSettlementSnapshot],
) -> None:
    insurer_ids = {
        int(item["entity_id"])
        for item in insurer_items
        if isinstance(item, dict) and "entity_id" in item
    }
    policyholder_ids = {
        int(item["entity_id"])
        for item in policyholder_items
        if isinstance(item, dict) and "entity_id" in item
    }
    unknown_policyholder_ids: set[int] = set()
    unknown_insurer_ids: set[int] = set()
    duplicate_policyholder_ids: set[int] = set()
    seen_policyholder_ids: set[int] = set()
    for snapshot in snapshots:
        if snapshot.policyholder_id in seen_policyholder_ids:
            duplicate_policyholder_ids.add(snapshot.policyholder_id)
        else:
            seen_policyholder_ids.add(snapshot.policyholder_id)
        if snapshot.policyholder_id not in policyholder_ids:
            unknown_policyholder_ids.add(snapshot.policyholder_id)
        for decision in snapshot.decisions:
            if decision.insurer_id is not None and decision.insurer_id not in insurer_ids:
                unknown_insurer_ids.add(decision.insurer_id)
    if duplicate_policyholder_ids:
        values = ", ".join(str(policyholder_id) for policyholder_id in sorted(duplicate_policyholder_ids))
        raise ScenarioValidationError(f"duplicate VN settlement snapshot policyholder_id values: {values}")
    if unknown_policyholder_ids:
        values = ", ".join(str(policyholder_id) for policyholder_id in sorted(unknown_policyholder_ids))
        raise ScenarioValidationError(f"VN settlement snapshots reference unknown policyholders: {values}")
    if unknown_insurer_ids:
        values = ", ".join(str(insurer_id) for insurer_id in sorted(unknown_insurer_ids))
        raise ScenarioValidationError(f"VN settlement snapshots reference unknown insurers: {values}")


def _validate_vn_damage_settlement_snapshot_references(
    insurer_items: list[object],
    policyholder_items: list[object],
    snapshots: list[VNDamageSettlementSnapshot],
) -> None:
    insurer_ids = {
        int(item["entity_id"])
        for item in insurer_items
        if isinstance(item, dict) and "entity_id" in item
    }
    policyholder_ids = {
        int(item["entity_id"])
        for item in policyholder_items
        if isinstance(item, dict) and "entity_id" in item
    }
    unknown_policyholder_ids: set[int] = set()
    unknown_insurer_ids: set[int] = set()
    duplicate_policyholder_ids: set[int] = set()
    seen_policyholder_ids: set[int] = set()
    for snapshot in snapshots:
        if snapshot.policyholder_id in seen_policyholder_ids:
            duplicate_policyholder_ids.add(snapshot.policyholder_id)
        else:
            seen_policyholder_ids.add(snapshot.policyholder_id)
        if snapshot.policyholder_id not in policyholder_ids:
            unknown_policyholder_ids.add(snapshot.policyholder_id)
        for decision in snapshot.insurance_decisions:
            if decision.insurer_id is not None and decision.insurer_id not in insurer_ids:
                unknown_insurer_ids.add(decision.insurer_id)
    if duplicate_policyholder_ids:
        values = ", ".join(str(policyholder_id) for policyholder_id in sorted(duplicate_policyholder_ids))
        raise ScenarioValidationError(f"duplicate VN damage settlement snapshot policyholder_id values: {values}")
    if unknown_policyholder_ids:
        values = ", ".join(str(policyholder_id) for policyholder_id in sorted(unknown_policyholder_ids))
        raise ScenarioValidationError(f"VN damage settlement snapshots reference unknown policyholders: {values}")
    if unknown_insurer_ids:
        values = ", ".join(str(insurer_id) for insurer_id in sorted(unknown_insurer_ids))
        raise ScenarioValidationError(f"VN damage settlement snapshots reference unknown insurers: {values}")


def _validate_vn_insurance_rule_snapshot_references(
    insurer_items: list[object],
    policyholder_items: list[object],
    snapshots: list[VNInsuranceRuleSnapshot],
) -> None:
    insurer_ids = {
        int(item["entity_id"])
        for item in insurer_items
        if isinstance(item, dict) and "entity_id" in item
    }
    policyholder_ids = {
        int(item["entity_id"])
        for item in policyholder_items
        if isinstance(item, dict) and "entity_id" in item
    }
    unknown_policyholder_ids: set[int] = set()
    unknown_insurer_ids: set[int] = set()
    duplicate_policyholder_ids: set[int] = set()
    seen_policyholder_ids: set[int] = set()
    for snapshot in snapshots:
        if snapshot.policyholder_id in seen_policyholder_ids:
            duplicate_policyholder_ids.add(snapshot.policyholder_id)
        else:
            seen_policyholder_ids.add(snapshot.policyholder_id)
        if snapshot.policyholder_id not in policyholder_ids:
            unknown_policyholder_ids.add(snapshot.policyholder_id)
        if snapshot.active_insurer_ids is not None:
            unknown_insurer_ids.update(
                insurer_id for insurer_id in snapshot.active_insurer_ids if insurer_id not in insurer_ids
            )
        if snapshot.initial_decisions is not None:
            decisions = load_vn_insurance_decisions_from_mapping(snapshot.initial_decisions)
            unknown_insurer_ids.update(
                decision.insurer_id
                for decision in decisions
                if decision.insurer_id is not None and decision.insurer_id not in insurer_ids
            )
        if snapshot.rule_kind is VNInsuranceRuleKind.PREFERENCE and snapshot.insurer_inputs is not None:
            inputs = load_vn_preference_insurer_inputs_from_mapping(snapshot.insurer_inputs)
            unknown_insurer_ids.update(item.insurer_id for item in inputs if item.insurer_id not in insurer_ids)
        if snapshot.rule_kind in (
            VNInsuranceRuleKind.SAMPLE_SEARCH,
            VNInsuranceRuleKind.BEST_INFO,
        ) and snapshot.insurer_inputs is not None:
            inputs = load_vn_sample_search_insurer_inputs_from_mapping(snapshot.insurer_inputs)
            unknown_insurer_ids.update(item.insurer_id for item in inputs if item.insurer_id not in insurer_ids)
        if snapshot.rule_kind is VNInsuranceRuleKind.SEARCH_HISTORY and snapshot.history is not None:
            history = load_vn_search_insurance_history_from_mapping(snapshot.history)
            unknown_insurer_ids.update(
                entry.insurer_id
                for entry in history
                if entry.insurer_id is not None and entry.insurer_id not in insurer_ids
            )
    if duplicate_policyholder_ids:
        values = ", ".join(str(policyholder_id) for policyholder_id in sorted(duplicate_policyholder_ids))
        raise ScenarioValidationError(f"duplicate VN insurance rule snapshot policyholder_id values: {values}")
    if unknown_policyholder_ids:
        values = ", ".join(str(policyholder_id) for policyholder_id in sorted(unknown_policyholder_ids))
        raise ScenarioValidationError(f"VN insurance rule snapshots reference unknown policyholders: {values}")
    if unknown_insurer_ids:
        values = ", ".join(str(insurer_id) for insurer_id in sorted(unknown_insurer_ids))
        raise ScenarioValidationError(f"VN insurance rule snapshots reference unknown insurers: {values}")


def _validate_disjoint_vn_snapshot_targets(
    damage_settlement_snapshots: list[VNDamageSettlementSnapshot],
    settlement_snapshots: list[VNSettlementSnapshot],
) -> None:
    damage_targets = {snapshot.policyholder_id for snapshot in damage_settlement_snapshots}
    settlement_targets = {snapshot.policyholder_id for snapshot in settlement_snapshots}
    conflicts = sorted(damage_targets & settlement_targets)
    if conflicts:
        values = ", ".join(str(policyholder_id) for policyholder_id in conflicts)
        raise ScenarioValidationError(
            "VN damage settlement snapshots and VN settlement snapshots "
            f"must target disjoint policyholders: {values}"
        )


def load_scenario_from_mapping(data: dict) -> LoadedScenario:
    if not isinstance(data, dict):
        raise ScenarioValidationError("scenario must be a JSON object")

    try:
        context_data = data["context"]
        bav_data = data["bav"]
        insurer_items = data["insurers"]
        policyholder_items = data["policyholders"]
    except KeyError as exc:
        raise ScenarioValidationError(f"missing top-level field: {exc.args[0]}") from exc

    if not isinstance(context_data, dict):
        raise ScenarioValidationError("context must be an object")
    if not isinstance(bav_data, dict):
        raise ScenarioValidationError("bav must be an object")
    if not isinstance(insurer_items, list) or not isinstance(policyholder_items, list):
        raise ScenarioValidationError("insurers and policyholders must be lists")
    _validate_entity_items(insurer_items, label="insurer")
    _validate_entity_items(policyholder_items, label="policyholder")
    _validate_unique_entity_ids(insurer_items, label="insurer")
    _validate_unique_entity_ids(policyholder_items, label="policyholder")
    _validate_policyholder_insurer_references(insurer_items, policyholder_items)
    vn_damage_settlement_snapshots = load_vn_damage_settlement_snapshots_from_mapping(
        data.get("vn_damage_settlement_snapshots")
    )
    _validate_vn_damage_settlement_snapshot_references(
        insurer_items,
        policyholder_items,
        vn_damage_settlement_snapshots,
    )
    vn_settlement_snapshots = load_vn_settlement_snapshots_from_mapping(data.get("vn_settlement_snapshots"))
    _validate_vn_settlement_snapshot_references(insurer_items, policyholder_items, vn_settlement_snapshots)
    _validate_disjoint_vn_snapshot_targets(vn_damage_settlement_snapshots, vn_settlement_snapshots)
    vn_insurance_rule_snapshots = load_vn_insurance_rule_snapshots_from_mapping(
        data.get("vn_insurance_rule_snapshots")
    )
    _validate_vn_insurance_rule_snapshot_references(
        insurer_items,
        policyholder_items,
        vn_insurance_rule_snapshots,
    )

    context = SimulationContext(
        period=int(context_data.get("period", 0)),
        logtime=int(context_data.get("logtime", 0)),
        max_periods=int(context_data["max_periods"]),
        run_index=int(context_data.get("run_index", 0)),
        rng_seed=int(context_data.get("rng_seed", 0)),
    )
    bav = BAV(
        entity_id=int(bav_data["entity_id"]),
        active=bool(bav_data.get("active", True)),
        name=str(bav_data["name"]),
    )
    insurers = [
        Insurer(
            entity_id=int(item["entity_id"]),
            active=bool(item.get("active", True)),
            name=str(item["name"]),
            premiums_prev=float(item.get("premiums_prev", 0.0)),
            advertising_prev=float(item.get("advertising_prev", 0.0)),
            reserves_prev=float(item.get("reserves_prev", 0.0)),
            premiums_prev_sector=_two_float_vector(
                item.get("premiums_prev_sector"),
                fallback=float(item.get("premiums_prev", 0.0)),
            ),
            advertising_prev_sector=_two_float_vector(
                item.get("advertising_prev_sector"),
                fallback=float(item.get("advertising_prev", 0.0)),
            ),
            reserves_prev_sector=_two_float_vector(
                item.get("reserves_prev_sector"),
                fallback=float(item.get("reserves_prev", 0.0)),
            ),
            policyholders_prev=float(item.get("policyholders_prev", 0.0)),
            policyholders_prev_sector=_two_float_vector(
                item.get("policyholders_prev_sector"),
                fallback=float(item.get("policyholders_prev", 0.0)),
            ),
            active_prev=bool(item.get("active_prev", True)),
            rule_id=int(item["rule_id"]) if item.get("rule_id") is not None else None,
            rule_class=int(item["rule_class"]) if item.get("rule_class") is not None else None,
            premiums_current=float(item.get("premiums_current", item.get("premiums_prev", 0.0))),
            advertising_current=float(item.get("advertising_current", item.get("advertising_prev", 0.0))),
            premiums_current_sector=_two_float_vector(
                item.get("premiums_current_sector"),
                fallback=float(item.get("premiums_current", item.get("premiums_prev", 0.0))),
            ),
            advertising_current_sector=_two_float_vector(
                item.get("advertising_current_sector"),
                fallback=float(item.get("advertising_current", item.get("advertising_prev", 0.0))),
            ),
            reserves_current=_insurer_reserves_vector(item),
            policyholders_current=float(item.get("policyholders_current", 0.0)),
            policyholders_current_sector=_two_float_vector(
                item.get("policyholders_current_sector"),
                fallback=float(item.get("policyholders_current", 0.0)),
            ),
            claims_count_current=_int_list(item.get("claims_count_current"), default=[0, 0]),
            claims_sum_current=_float_list(item.get("claims_sum_current"), default=[0.0, 0.0]),
        )
        for item in insurer_items
    ]
    policyholders = [
        Policyholder(
            entity_id=int(item["entity_id"]),
            active=bool(item.get("active", True)),
            name=str(item["name"]),
            insurer_id=int(item["insurer_id"]) if item.get("insurer_id") is not None else None,
            insured_prev=float(item.get("insured_prev", 0.0)),
            insured_prev_sector=_two_float_vector(
                item.get("insured_prev_sector"),
                fallback=float(item.get("insured_prev", 0.0)),
            ),
            active_prev=bool(item.get("active_prev", True)),
            rule_id=int(item["rule_id"]) if item.get("rule_id") is not None else None,
            rule_class=int(item["rule_class"]) if item.get("rule_class") is not None else None,
            insured_current=float(item.get("insured_current", item.get("insured_prev", 0.0))),
            insured_current_sector=_two_float_vector(
                item.get("insured_current_sector"),
                fallback=float(item.get("insured_current", item.get("insured_prev", 0.0))),
            ),
            chosen_insurer_current=(
                int(item["chosen_insurer_current"])
                if item.get("chosen_insurer_current") is not None
                else (int(item["insurer_id"]) if item.get("insurer_id") is not None else None)
            ),
            chosen_insurer_sector_current=_policyholder_chosen_insurer_vector(item),
            paid_premium_current=_float_list(item.get("paid_premium_current"), default=[0.0, 0.0]),
            self_damage_current=_float_list(item.get("self_damage_current"), default=[0.0, 0.0]),
            claim_sum_current=_float_list(item.get("claim_sum_current"), default=[0.0, 0.0]),
            end_wealth_sector_current=_float_list(item.get("end_wealth_sector_current"), default=[0.0, 0.0]),
            end_wealth_current=float(item.get("end_wealth_current", 0.0)),
        )
        for item in policyholder_items
    ]
    return LoadedScenario(
        context=context,
        bav=bav,
        insurers=insurers,
        policyholders=policyholders,
        vu_foreign_info_rule_snapshots=load_vu_foreign_info_rule_snapshots_from_mapping(
            data.get("vu_foreign_info_rule_snapshots")
        ),
        vu_random_uniform_rule_snapshots=load_vu_random_uniform_rule_snapshots_from_mapping(
            data.get("vu_random_uniform_rule_snapshots")
        ),
        vu_random_normal_rule_snapshots=load_vu_random_normal_rule_snapshots_from_mapping(
            data.get("vu_random_normal_rule_snapshots")
        ),
        vu_reserve_markup_rule_snapshots=load_vu_reserve_markup_rule_snapshots_from_mapping(
            data.get("vu_reserve_markup_rule_snapshots")
        ),
        vu_net_switcher_markup_rule_snapshots=load_vu_net_switcher_markup_rule_snapshots_from_mapping(
            data.get("vu_net_switcher_markup_rule_snapshots")
        ),
        vu_expected_claim_rule_snapshots=load_vu_expected_claim_rule_snapshots_from_mapping(
            data.get("vu_expected_claim_rule_snapshots")
        ),
        vu_market_share_markup_rule_snapshots=load_vu_market_share_markup_rule_snapshots_from_mapping(
            data.get("vu_market_share_markup_rule_snapshots")
        ),
        vu_free_linear_rule_snapshots=load_vu_free_linear_rule_snapshots_from_mapping(
            data.get("vu_free_linear_rule_snapshots")
        ),
        vn_insurance_rule_snapshots=vn_insurance_rule_snapshots,
        vn_damage_settlement_snapshots=vn_damage_settlement_snapshots,
        vn_settlement_snapshots=vn_settlement_snapshots,
    )


def load_scenario(path: str | Path) -> LoadedScenario:
    scenario_path = Path(path)
    with scenario_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    return load_scenario_from_mapping(data)
