from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib
from typing import Any

from ims.strategies.assignment_snapshot_context import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION,
    STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VERSION,
)
from ims.strategies.assignment_snapshot_translation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
    STRATEGY_SNAPSHOT_TARGETS,
)
from ims.strategies.catalog import StrategyActorType


STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION = (
    "ims.strategy-assignment-snapshot-materialization-contract.v1"
)
STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION = (
    "ims.strategy-assignment-snapshot-materialization.v1"
)

_VN_NESTED_FIELDS = frozenset(
    {"draws", "initial_decisions", "insurer_inputs", "history"}
)


@dataclass(frozen=True, slots=True)
class StrategySnapshotNestedValueDefinition:
    """Loadergebundene Form eines verschachtelten VN-Kontextwerts."""

    schema_id: str
    field_name: str
    value_shape: str
    loader_module: str
    loader_entrypoint: str
    loaded_type: str
    required_item_fields: tuple[str, ...] = ()
    optional_item_fields: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StrategySnapshotConditionalField:
    field_name: str
    condition: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class VNSnapshotMaterializationRuleDefinition:
    """Periodenabhaengige Eingabegrenze einer vorhandenen VN-Regel."""

    strategy_id: str
    rule_kind: str
    source_path: str
    source_symbol: str
    period_one_required_fields: tuple[str, ...]
    periods_after_one_required_fields: tuple[str, ...]
    periods_after_one_conditional_fields: tuple[
        StrategySnapshotConditionalField, ...
    ]
    nested_value_schema_ids: tuple[str, ...]
    runtime_constraints: tuple[str, ...] = ()

    def to_dict(self, *, open_fields: tuple[str, ...]) -> dict[str, object]:
        period_one_used = set(self.period_one_required_fields)
        later_used = set(self.periods_after_one_required_fields) | {
            item.field_name for item in self.periods_after_one_conditional_fields
        }
        return {
            **asdict(self),
            "period_one_not_consumed_fields": tuple(
                field_name
                for field_name in open_fields
                if field_name not in period_one_used
            ),
            "periods_after_one_not_consumed_fields": tuple(
                field_name for field_name in open_fields if field_name not in later_used
            ),
        }


def _nested_value(
    schema_id: str,
    field_name: str,
    value_shape: str,
    loader_module: str,
    loader_entrypoint: str,
    loaded_type: str,
    *,
    required_item_fields: tuple[str, ...] = (),
    optional_item_fields: tuple[str, ...] = (),
    constraints: tuple[str, ...] = (),
) -> StrategySnapshotNestedValueDefinition:
    return StrategySnapshotNestedValueDefinition(
        schema_id=schema_id,
        field_name=field_name,
        value_shape=value_shape,
        loader_module=loader_module,
        loader_entrypoint=loader_entrypoint,
        loaded_type=loaded_type,
        required_item_fields=required_item_fields,
        optional_item_fields=optional_item_fields,
        constraints=constraints,
    )


_VN_RULE_MODULE = "ims.model.vn_insurance_rules"
_VN_DECISION_MODULE = "ims.model.vn_rules"


STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS = (
    _nested_value(
        "vn.initial-decisions.v1",
        "initial_decisions",
        "array_of_two_sector_objects",
        _VN_DECISION_MODULE,
        "load_vn_insurance_decisions_from_mapping",
        "list[VNInsuranceDecision]",
        required_item_fields=("sector_index", "insured"),
        optional_item_fields=("insurer_id", "premium"),
        constraints=(
            "exactly_one_entry_for_sector_index_0_and_1",
            "insured_requires_positive_insurer_id",
            "uninsured_forbids_insurer_id",
            "premium_is_optional_and_non_negative",
        ),
    ),
    _nested_value(
        "vn.compulsory-draws.v1",
        "draws",
        "object_with_two_sector_draws",
        _VN_RULE_MODULE,
        "vn_compulsory_insurance_rule_draws_from_mapping",
        "VNCompulsoryInsuranceRuleDraws",
        required_item_fields=("insurer_choice_draws",),
        constraints=("exactly_two_values", "values_in_half_open_unit_interval"),
    ),
    _nested_value(
        "vn.random-draws.v1",
        "draws",
        "object_with_two_draw_vectors",
        _VN_RULE_MODULE,
        "vn_random_insurance_rule_draws_from_mapping",
        "VNRandomInsuranceRuleDraws",
        required_item_fields=("status_draws", "insurer_choice_draws"),
        constraints=(
            "exactly_two_values_per_vector",
            "values_in_half_open_unit_interval",
        ),
    ),
    _nested_value(
        "vn.preference-draws.v1",
        "draws",
        "object_with_two_sector_fallback_draws",
        _VN_RULE_MODULE,
        "vn_preference_insurance_rule_draws_from_mapping",
        "VNPreferenceInsuranceRuleDraws",
        required_item_fields=("fallback_insurer_choice_draws",),
        constraints=("exactly_two_values", "values_in_half_open_unit_interval"),
    ),
    _nested_value(
        "vn.preference-insurer-inputs.v1",
        "insurer_inputs",
        "array_of_insurer_advertising_objects",
        _VN_RULE_MODULE,
        "load_vn_preference_insurer_inputs_from_mapping",
        "list[VNPreferenceInsurerInput]",
        required_item_fields=("insurer_id", "advertising_current_sector"),
        constraints=(
            "non_empty_for_periods_after_one",
            "unique_positive_insurer_ids",
            "exactly_two_non_negative_advertising_values",
        ),
    ),
    _nested_value(
        "vn.search-draws.v1",
        "draws",
        "object_with_two_sector_fallback_draws",
        _VN_RULE_MODULE,
        "vn_search_insurance_rule_draws_from_mapping",
        "VNSearchInsuranceRuleDraws",
        required_item_fields=("fallback_insurer_choice_draws",),
        constraints=("exactly_two_values", "values_in_half_open_unit_interval"),
    ),
    _nested_value(
        "vn.search-history.v1",
        "history",
        "array_of_period_sector_objects",
        _VN_RULE_MODULE,
        "load_vn_search_insurance_history_from_mapping",
        "list[VNSearchInsuranceHistoryEntry]",
        required_item_fields=("period", "sector_index", "insured", "premium"),
        optional_item_fields=("insurer_id",),
        constraints=(
            "period_at_least_one_and_before_current_period",
            "sector_index_0_or_1",
            "unique_period_sector_pairs",
            "insured_requires_positive_insurer_id",
            "uninsured_forbids_insurer_id",
            "premium_non_negative",
        ),
    ),
    _nested_value(
        "vn.sample-search-draws.v1",
        "draws",
        "object_with_two_sector_draw_lists",
        _VN_RULE_MODULE,
        "vn_sample_search_insurance_rule_draws_from_mapping",
        "VNSampleSearchInsuranceRuleDraws",
        required_item_fields=("insurer_choice_draws_by_sector",),
        constraints=(
            "exactly_two_sector_lists",
            "values_in_half_open_unit_interval",
            "each_list_covers_selected_period_sample_size",
        ),
    ),
    _nested_value(
        "vn.premium-insurer-inputs.v1",
        "insurer_inputs",
        "array_of_insurer_premium_objects",
        _VN_RULE_MODULE,
        "load_vn_sample_search_insurer_inputs_from_mapping",
        "list[VNSampleSearchInsurerInput]",
        required_item_fields=("insurer_id", "premiums_current_sector"),
        constraints=(
            "non_empty_for_periods_after_one",
            "unique_positive_insurer_ids",
            "exactly_two_non_negative_premium_values",
        ),
    ),
)


def _conditional(field_name: str, condition: str) -> StrategySnapshotConditionalField:
    return StrategySnapshotConditionalField(
        field_name=field_name,
        condition=condition,
    )


VN_SNAPSHOT_MATERIALIZATION_RULES = (
    VNSnapshotMaterializationRuleDefinition(
        strategy_id="vn.vrvn01",
        rule_kind="compulsory",
        source_path="IMS.E",
        source_symbol="act Vrvn01",
        period_one_required_fields=("initial_decisions",),
        periods_after_one_required_fields=("draws", "active_insurer_ids"),
        periods_after_one_conditional_fields=(),
        nested_value_schema_ids=(
            "vn.initial-decisions.v1",
            "vn.compulsory-draws.v1",
        ),
        runtime_constraints=(
            "active_insurer_ids_non_empty_for_periods_after_one",
        ),
    ),
    VNSnapshotMaterializationRuleDefinition(
        strategy_id="vn.vrvn02",
        rule_kind="random",
        source_path="IMS.E",
        source_symbol="act Vrvn02",
        period_one_required_fields=("initial_decisions",),
        periods_after_one_required_fields=(
            "draws",
            "active_insurer_ids",
            "change_shock",
        ),
        periods_after_one_conditional_fields=(),
        nested_value_schema_ids=("vn.initial-decisions.v1", "vn.random-draws.v1"),
        runtime_constraints=(
            "active_insurer_ids_non_empty_for_periods_after_one",
            "typed_parameters_are_supplied_by_translation",
        ),
    ),
    VNSnapshotMaterializationRuleDefinition(
        strategy_id="vn.vrvn03",
        rule_kind="preference",
        source_path="IMS.E",
        source_symbol="act Vrvn03",
        period_one_required_fields=("initial_decisions",),
        periods_after_one_required_fields=(
            "damage_probabilities",
            "insurer_inputs",
            "change_shock",
        ),
        periods_after_one_conditional_fields=(
            _conditional(
                "draws",
                "required_when_any_sector_has_no_positive_advertising",
            ),
        ),
        nested_value_schema_ids=(
            "vn.initial-decisions.v1",
            "vn.preference-draws.v1",
            "vn.preference-insurer-inputs.v1",
        ),
        runtime_constraints=("typed_parameters_are_supplied_by_translation",),
    ),
    VNSnapshotMaterializationRuleDefinition(
        strategy_id="vn.vrvn04",
        rule_kind="search_history",
        source_path="IMS.E",
        source_symbol="act Vrvn04",
        period_one_required_fields=("initial_decisions",),
        periods_after_one_required_fields=(
            "damage_probabilities",
            "history",
            "active_insurer_ids",
            "change_shock",
        ),
        periods_after_one_conditional_fields=(
            _conditional(
                "draws",
                "required_when_any_sector_has_no_prior_insured_history",
            ),
        ),
        nested_value_schema_ids=(
            "vn.initial-decisions.v1",
            "vn.search-draws.v1",
            "vn.search-history.v1",
        ),
        runtime_constraints=(
            "history_periods_must_be_before_context_period",
            "active_insurer_ids_non_empty_when_fallback_is_required",
            "typed_parameters_are_supplied_by_translation",
        ),
    ),
    VNSnapshotMaterializationRuleDefinition(
        strategy_id="vn.vrvn05",
        rule_kind="sample_search",
        source_path="IMS.E",
        source_symbol="act Vrvn05",
        period_one_required_fields=("initial_decisions",),
        periods_after_one_required_fields=(
            "draws",
            "insurer_inputs",
            "market_damage_indicator",
            "change_shock",
            "information_cost_per_sample",
        ),
        periods_after_one_conditional_fields=(),
        nested_value_schema_ids=(
            "vn.initial-decisions.v1",
            "vn.sample-search-draws.v1",
            "vn.premium-insurer-inputs.v1",
        ),
        runtime_constraints=(
            "selected_sample_sizes_must_be_positive",
            "draw_count_per_sector_must_cover_selected_sample_size",
            "information_cost_per_sample_non_negative",
            "typed_parameters_are_supplied_by_translation",
        ),
    ),
    VNSnapshotMaterializationRuleDefinition(
        strategy_id="vn.vrvn06",
        rule_kind="best_info",
        source_path="IMS.E",
        source_symbol="act Vrvn06",
        period_one_required_fields=("initial_decisions",),
        periods_after_one_required_fields=(
            "insurer_inputs",
            "market_damage_indicator",
            "change_shock",
            "information_cost_per_insurer",
        ),
        periods_after_one_conditional_fields=(),
        nested_value_schema_ids=(
            "vn.initial-decisions.v1",
            "vn.premium-insurer-inputs.v1",
        ),
        runtime_constraints=(
            "draws_are_not_consumed",
            "information_cost_per_insurer_non_negative",
            "typed_parameters_are_supplied_by_translation",
        ),
    ),
)


def _vn_open_fields() -> tuple[str, ...]:
    fields_by_strategy = {
        target.strategy_id: target.unresolved_snapshot_fields
        for target in STRATEGY_SNAPSHOT_TARGETS
        if target.actor_type is StrategyActorType.POLICYHOLDER
    }
    return next(iter(fields_by_strategy.values()), ())


def strategy_snapshot_materialization_contract_issues(
    nested_values: tuple[
        StrategySnapshotNestedValueDefinition, ...
    ] = STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS,
    rules: tuple[
        VNSnapshotMaterializationRuleDefinition, ...
    ] = VN_SNAPSHOT_MATERIALIZATION_RULES,
) -> tuple[str, ...]:
    """Prueft die PR114-Beschreibung gegen vorhandene Ziele und Loader."""

    issues: list[str] = []
    nested_by_id = {definition.schema_id: definition for definition in nested_values}
    if len(nested_by_id) != len(nested_values):
        issues.append("Doppeltes Schema im verschachtelten VN-Kontextvertrag")
    rules_by_id = {definition.strategy_id: definition for definition in rules}
    if len(rules_by_id) != len(rules):
        issues.append("Doppelte VN-Strategie im Materialisierungsvertrag")

    vn_targets = {
        target.strategy_id: target
        for target in STRATEGY_SNAPSHOT_TARGETS
        if target.actor_type is StrategyActorType.POLICYHOLDER
    }
    if set(rules_by_id) != set(vn_targets):
        issues.append("Materialisierungsvertrag deckt die VN-Strategien nicht exakt ab")

    open_fields = _vn_open_fields()
    for target in vn_targets.values():
        if target.unresolved_snapshot_fields != open_fields:
            issues.append("VN-Snapshotziele besitzen unterschiedliche offene Felder")
            break

    for definition in nested_values:
        if definition.field_name not in _VN_NESTED_FIELDS:
            issues.append(f"Unbekanntes verschachteltes Feld: {definition.schema_id}")
        module = importlib.import_module(definition.loader_module)
        if not callable(getattr(module, definition.loader_entrypoint, None)):
            issues.append(f"Verschachtelter Loader fehlt: {definition.schema_id}")

    nested_fields_by_id = {
        schema_id: definition.field_name
        for schema_id, definition in nested_by_id.items()
    }
    for strategy_id, definition in rules_by_id.items():
        target = vn_targets.get(strategy_id)
        if target is None:
            continue
        if target.rule_kind != definition.rule_kind:
            issues.append(f"VN-Regelart weicht ab: {strategy_id}")
        if target.snapshot_loader != "vn_insurance_rule_snapshot_from_mapping":
            issues.append(f"Unerwarteter VN-Snapshotloader: {strategy_id}")
        referenced_schemas = set(definition.nested_value_schema_ids)
        missing_schemas = referenced_schemas - set(nested_by_id)
        if missing_schemas:
            issues.append(f"Verschachteltes Schema fehlt: {strategy_id}")
            continue
        used_fields = set(definition.period_one_required_fields)
        used_fields.update(definition.periods_after_one_required_fields)
        used_fields.update(
            field.field_name
            for field in definition.periods_after_one_conditional_fields
        )
        if not used_fields <= set(open_fields):
            issues.append(f"VN-Regel referenziert unbekannte offene Felder: {strategy_id}")
        expected_nested_fields = used_fields & _VN_NESTED_FIELDS
        documented_nested_fields = {
            nested_fields_by_id[schema_id] for schema_id in referenced_schemas
        }
        if documented_nested_fields != expected_nested_fields:
            issues.append(
                f"Verschachtelte VN-Felder sind nicht exakt dokumentiert: {strategy_id}"
            )
    return tuple(issues)


def strategy_assignment_snapshot_materialization_contract_payload() -> dict[str, Any]:
    """Beschreibt die atomare Materialisierung, ohne sie beim Lesen auszufuehren."""

    open_fields = _vn_open_fields()
    return {
        "schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION
        ),
        "translation_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
        "context_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VERSION,
        "context_validation_schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION
        ),
        "mode": "strategy_assignment_snapshot_materialization_contract_read_only",
        "base_model": "Vdefmd6",
        "scope": "validated_single_period_context_to_existing_snapshot_loaders",
        "contract_endpoint": (
            "/api/strategies/assignment-snapshot-materialization-contract"
        ),
        "materialization_schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION
        ),
        "materialization_endpoint": (
            "/api/strategies/assignment-snapshot-materialization"
        ),
        "materialization_steps": (
            "validate_draft_atomically",
            "translate_draft_to_partial_snapshot_payloads",
            "validate_matching_single_period_context",
            "validate_rule_specific_nested_values",
            "merge_context_values_without_overwriting_translation_fields",
            "invoke_declared_snapshot_loader_once_per_entry",
            "publish_snapshots_only_when_every_entry_succeeds",
        ),
        "merge_policy": {
            "base": "translation_entry.snapshot_payload",
            "overlay": "matching_context_entry.values",
            "translation_fields_may_be_overwritten": False,
            "unknown_fields_allowed": False,
            "defaults_applied_before_loader": False,
            "partial_results_allowed": False,
        },
        "vn_open_snapshot_fields": open_fields,
        "nested_value_definitions": [
            definition.to_dict()
            for definition in STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS
        ],
        "vn_rule_definitions": [
            definition.to_dict(open_fields=open_fields)
            for definition in VN_SNAPSHOT_MATERIALIZATION_RULES
        ],
        "contract_issue_count": len(
            strategy_snapshot_materialization_contract_issues()
        ),
        "nested_contract_definitions_complete": True,
        "existing_nested_loaders_reused": True,
        "context_validator_uses_nested_contract": False,
        "materialization_validation_required": True,
        "nested_values_consumed": True,
        "snapshot_loader_invocation_enabled": True,
        "snapshot_materialization_enabled": True,
        "partial_results_allowed": False,
        "persistence_enabled": False,
        "execution_enabled": False,
        "runner_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
