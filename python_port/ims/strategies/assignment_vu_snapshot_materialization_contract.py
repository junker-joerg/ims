from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib
from typing import Any

from ims.strategies.assignment_snapshot_translation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
    STRATEGY_SNAPSHOT_TARGETS,
)
from ims.strategies.catalog import (
    STRATEGY_CATALOG_VERSION,
    STRATEGY_DEFINITIONS,
    StrategyActorType,
)


STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION = (
    "ims.strategy-assignment-vu-snapshot-materialization-contract.v1"
)


@dataclass(frozen=True, slots=True)
class VUSnapshotRuntimeFieldDefinition:
    """Bestandsaufnahme eines noch offenen Felds im VU-Snapshot."""

    field_name: str
    strategy_ids: tuple[str, ...]
    value_shape: str
    source_candidate: str
    consumed_when: str
    loader_fallback: str
    runner_fallback: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class VUExternalStateDependencyDefinition:
    """Laufzeitwert, den der Regelkern ausserhalb seines Snapshots liest."""

    dependency_id: str
    strategy_ids: tuple[str, ...]
    value_shape: str
    consumed_when: str
    python_source: str
    historical_source: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class VUSnapshotMaterializationTargetDefinition:
    """Read-only Grenze eines vorhandenen VU-Snapshotziels."""

    strategy_id: str
    historical_action: str
    source_path: str
    source_symbol: str
    included_in_vdefmd6: bool
    snapshot_module: str
    snapshot_type: str
    snapshot_loader: str
    snapshot_collection: str
    rule_kind: str | None
    open_snapshot_fields: tuple[str, ...]
    carryover_period_condition: str
    rule_period_condition: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_ALL_VU_STRATEGY_IDS = tuple(f"vu.vrvu{index:02d}" for index in range(1, 11))
_FOREIGN_INFO_STRATEGY_IDS = ("vu.vrvu07", "vu.vrvu08", "vu.vrvu09")


VU_SNAPSHOT_RUNTIME_FIELDS = (
    VUSnapshotRuntimeFieldDefinition(
        "interest_rate",
        _ALL_VU_STRATEGY_IDS,
        "number",
        "single_period_finance_context",
        "all_periods_for_reserve_accrual",
        "0.0",
    ),
    VUSnapshotRuntimeFieldDefinition(
        "change_shock",
        _ALL_VU_STRATEGY_IDS,
        "boolean",
        "single_period_shock_context",
        "period_greater_than_one_except_vrvu04_period_at_least_three",
        "false",
    ),
    VUSnapshotRuntimeFieldDefinition(
        "random_draws",
        ("vu.vrvu01",),
        "array_of_four_numbers",
        "explicit_uniform_draw_context",
        "all_periods_in_current_python_core",
        "None",
        "context_rng_uniform_draw_provider",
    ),
    VUSnapshotRuntimeFieldDefinition(
        "normal_draws",
        ("vu.vrvu02",),
        "array_of_four_numbers",
        "explicit_normal_draw_context",
        "all_periods_in_current_python_core",
        "None",
        "context_rng_normal_draw_provider",
    ),
    VUSnapshotRuntimeFieldDefinition(
        "reserve_thresholds",
        ("vu.vrvu03",),
        "array_of_two_numbers",
        "strategy_runtime_thresholds",
        "period_greater_than_one_without_change_shock",
        "two_zero_values",
    ),
    VUSnapshotRuntimeFieldDefinition(
        "net_switcher_thresholds",
        ("vu.vrvu04",),
        "array_of_two_numbers",
        "strategy_runtime_thresholds",
        "period_at_least_three",
        "two_zero_values",
    ),
    VUSnapshotRuntimeFieldDefinition(
        "previous_policyholders_sector",
        ("vu.vrvu04",),
        "array_of_two_numbers",
        "insurer_previous_period_state_or_explicit_override",
        "all_periods_for_net_switcher_diagnostic",
        "None",
        "insurer.policyholders_prev_sector",
    ),
    VUSnapshotRuntimeFieldDefinition(
        "market_share_thresholds",
        ("vu.vrvu05",),
        "array_of_two_numbers",
        "strategy_runtime_thresholds",
        "period_greater_than_one",
        "two_zero_values",
    ),
    VUSnapshotRuntimeFieldDefinition(
        "active_policyholder_count",
        ("vu.vrvu05",),
        "non_negative_integer",
        "bav_activity_state_or_explicit_override",
        "all_periods_for_market_share_diagnostic",
        "None",
        "bav.service_state.activity_state.active_policyholder_count_current",
    ),
)


VU_EXTERNAL_STATE_DEPENDENCIES = (
    VUExternalStateDependencyDefinition(
        "context.period",
        _ALL_VU_STRATEGY_IDS,
        "positive_integer",
        "all_periods",
        "run_loaded_vu_foreign_info_period: loaded.context.period",
        "IMS.E: gperiod",
    ),
    VUExternalStateDependencyDefinition(
        "insurer.current_premiums_advertising_reserves",
        _ALL_VU_STRATEGY_IDS,
        "three_arrays_of_two_numbers",
        "all_periods_as_carryover_or_rule_base",
        "Insurer current two-sector state",
        "IMS.E: Pr/Wa/Rs at gperiod-1 and period-1 start values",
    ),
    VUExternalStateDependencyDefinition(
        "insurer.current_policyholders",
        ("vu.vrvu04", "vu.vrvu05"),
        "array_of_two_numbers",
        "all_periods_for_net_switcher_or_market_share_diagnostic",
        "Insurer.policyholders_current_sector",
        "IMS.E: Vn at gperiod-1",
    ),
    VUExternalStateDependencyDefinition(
        "insurer.current_claim_counts_and_sums",
        ("vu.vrvu06",),
        "two_arrays_of_two_numbers",
        "all_periods_for_expected_claim_diagnostic",
        "Insurer.claims_count_current and Insurer.claims_sum_current",
        "IMS.E: Sa and Sh at gperiod-1",
    ),
    VUExternalStateDependencyDefinition(
        "bav.foreign_information",
        _FOREIGN_INFO_STRATEGY_IDS,
        "premium_and_advertising_arrays_of_two_numbers",
        "period_greater_than_one",
        "BAV insurer pm/wm, dp/dw or mp/mw selected by rule_kind",
        "IMS.E: BAV Pm/Wm, Dp/Dw or Mp/Mw",
    ),
)


_TRANSLATION_TARGETS_BY_ID = {
    target.strategy_id: target
    for target in STRATEGY_SNAPSHOT_TARGETS
    if target.actor_type is StrategyActorType.INSURER
}
_CATALOG_BY_ID = {
    strategy.strategy_id: strategy
    for strategy in STRATEGY_DEFINITIONS
    if strategy.actor_type is StrategyActorType.INSURER
}


def _vu_target(
    strategy_id: str,
    *,
    carryover_period_condition: str,
    rule_period_condition: str,
) -> VUSnapshotMaterializationTargetDefinition:
    translation = _TRANSLATION_TARGETS_BY_ID[strategy_id]
    catalog = _CATALOG_BY_ID[strategy_id]
    return VUSnapshotMaterializationTargetDefinition(
        strategy_id=strategy_id,
        historical_action=catalog.historical_action,
        source_path=catalog.source_file,
        source_symbol=f"act {catalog.historical_action}",
        included_in_vdefmd6=catalog.included_in_vdefmd6,
        snapshot_module=translation.snapshot_module,
        snapshot_type=translation.snapshot_type,
        snapshot_loader=translation.snapshot_loader,
        snapshot_collection=translation.snapshot_collection,
        rule_kind=translation.rule_kind,
        open_snapshot_fields=translation.unresolved_snapshot_fields,
        carryover_period_condition=carryover_period_condition,
        rule_period_condition=rule_period_condition,
    )


VU_SNAPSHOT_MATERIALIZATION_TARGETS = tuple(
    _vu_target(
        strategy_id,
        carryover_period_condition=(
            "period_less_than_three" if strategy_id == "vu.vrvu04" else "period_at_most_one"
        ),
        rule_period_condition=(
            "period_at_least_three" if strategy_id == "vu.vrvu04" else "period_greater_than_one"
        ),
    )
    for strategy_id in _ALL_VU_STRATEGY_IDS
)


def strategy_vu_snapshot_materialization_contract_issues(
    targets: tuple[
        VUSnapshotMaterializationTargetDefinition, ...
    ] = VU_SNAPSHOT_MATERIALIZATION_TARGETS,
    runtime_fields: tuple[
        VUSnapshotRuntimeFieldDefinition, ...
    ] = VU_SNAPSHOT_RUNTIME_FIELDS,
    state_dependencies: tuple[
        VUExternalStateDependencyDefinition, ...
    ] = VU_EXTERNAL_STATE_DEPENDENCIES,
) -> tuple[str, ...]:
    """Prueft die PR118-Bestandsaufnahme, ohne Snapshotloader aufzurufen."""

    issues: list[str] = []
    targets_by_id = {target.strategy_id: target for target in targets}
    if len(targets_by_id) != len(targets):
        issues.append("Doppelte VU-Strategie im Materialisierungsbestand")
    if set(targets_by_id) != set(_ALL_VU_STRATEGY_IDS):
        issues.append("Materialisierungsbestand deckt die VU-Strategien nicht exakt ab")

    fields_by_name = {definition.field_name: definition for definition in runtime_fields}
    if len(fields_by_name) != len(runtime_fields):
        issues.append("Doppeltes offenes Feld im VU-Materialisierungsbestand")

    declared_fields_by_strategy = {strategy_id: set() for strategy_id in targets_by_id}
    for definition in runtime_fields:
        if len(set(definition.strategy_ids)) != len(definition.strategy_ids):
            issues.append(f"Doppelte Strategiezuordnung fuer VU-Feld: {definition.field_name}")
        unknown_strategy_ids = set(definition.strategy_ids) - set(targets_by_id)
        if unknown_strategy_ids:
            issues.append(f"VU-Feld referenziert unbekannte Strategie: {definition.field_name}")
        for strategy_id in definition.strategy_ids:
            if strategy_id in declared_fields_by_strategy:
                declared_fields_by_strategy[strategy_id].add(definition.field_name)

    for target in targets:
        translation = _TRANSLATION_TARGETS_BY_ID.get(target.strategy_id)
        catalog = _CATALOG_BY_ID.get(target.strategy_id)
        if translation is None or catalog is None:
            continue
        expected_metadata = (
            translation.snapshot_module,
            translation.snapshot_type,
            translation.snapshot_loader,
            translation.snapshot_collection,
            translation.rule_kind,
            translation.unresolved_snapshot_fields,
        )
        actual_metadata = (
            target.snapshot_module,
            target.snapshot_type,
            target.snapshot_loader,
            target.snapshot_collection,
            target.rule_kind,
            target.open_snapshot_fields,
        )
        if actual_metadata != expected_metadata:
            issues.append(f"VU-Snapshotziel weicht von PR110 ab: {target.strategy_id}")
        if (
            target.historical_action != catalog.historical_action
            or target.source_path != catalog.source_file
            or target.included_in_vdefmd6 != catalog.included_in_vdefmd6
        ):
            issues.append(f"VU-Snapshotziel weicht vom Strategiekatalog ab: {target.strategy_id}")
        module = importlib.import_module(target.snapshot_module)
        if not callable(getattr(module, target.snapshot_loader, None)):
            issues.append(f"VU-Snapshotloader fehlt: {target.strategy_id}")
        if declared_fields_by_strategy[target.strategy_id] != set(target.open_snapshot_fields):
            issues.append(f"Offene VU-Snapshotfelder sind nicht exakt dokumentiert: {target.strategy_id}")

    for dependency in state_dependencies:
        if len(set(dependency.strategy_ids)) != len(dependency.strategy_ids):
            issues.append(f"Doppelte Strategiezuordnung fuer VU-Zustand: {dependency.dependency_id}")
        if set(dependency.strategy_ids) - set(targets_by_id):
            issues.append(f"VU-Zustand referenziert unbekannte Strategie: {dependency.dependency_id}")

    foreign_targets = tuple(targets_by_id.get(strategy_id) for strategy_id in _FOREIGN_INFO_STRATEGY_IDS)
    if None not in foreign_targets:
        foreign_metadata = {
            (target.snapshot_type, target.snapshot_loader, target.snapshot_collection)
            for target in foreign_targets
            if target is not None
        }
        foreign_rule_kinds = tuple(
            target.rule_kind for target in foreign_targets if target is not None
        )
        if len(foreign_metadata) != 1 or foreign_rule_kinds != ("dumping", "average", "attack"):
            issues.append("Vrvu07 bis Vrvu09 teilen den Foreign-Info-Typ nicht konsistent")
    return tuple(issues)


def strategy_assignment_vu_snapshot_materialization_contract_payload() -> dict[str, Any]:
    """Liefert den VU-Bestandsvertrag, ohne Validierung oder Materialisierung."""

    targets = VU_SNAPSHOT_MATERIALIZATION_TARGETS
    return {
        "schema_version": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION,
        "catalog_schema_version": STRATEGY_CATALOG_VERSION,
        "translation_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
        "mode": "strategy_assignment_vu_snapshot_materialization_contract_read_only",
        "base_model": "Vdefmd6",
        "inventory_scope": "all_catalogued_vu_snapshot_targets",
        "contract_endpoint": (
            "/api/strategies/assignment-vu-snapshot-materialization-contract"
        ),
        "strategy_count": len(targets),
        "vdefmd6_strategy_count": sum(target.included_in_vdefmd6 for target in targets),
        "outside_vdefmd6_strategy_count": sum(not target.included_in_vdefmd6 for target in targets),
        "snapshot_type_count": len({target.snapshot_type for target in targets}),
        "snapshot_collection_count": len({target.snapshot_collection for target in targets}),
        "shared_foreign_info_strategy_count": len(_FOREIGN_INFO_STRATEGY_IDS),
        "targets": [target.to_dict() for target in targets],
        "runtime_field_definitions": [
            definition.to_dict() for definition in VU_SNAPSHOT_RUNTIME_FIELDS
        ],
        "external_state_dependencies": [
            definition.to_dict() for definition in VU_EXTERNAL_STATE_DEPENDENCIES
        ],
        "loader_fallbacks_are_inventory_only": True,
        "future_materialization_defaults_defined": False,
        "contract_issue_count": len(strategy_vu_snapshot_materialization_contract_issues()),
        "input_schema_defined": False,
        "input_validation_enabled": False,
        "context_values_consumed": False,
        "snapshot_loader_invocation_enabled": False,
        "snapshot_materialization_enabled": False,
        "persistence_enabled": False,
        "runner_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
