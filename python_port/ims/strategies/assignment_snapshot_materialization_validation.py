from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib
import math
from typing import Any

from ims.strategies.assignment_snapshot_context import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION,
    validate_strategy_assignment_snapshot_context,
)
from ims.strategies.assignment_snapshot_materialization_contract import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION,
    STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS,
    VN_SNAPSHOT_MATERIALIZATION_RULES,
    VNSnapshotMaterializationRuleDefinition,
    strategy_snapshot_materialization_contract_issues,
)
from ims.strategies.assignment_snapshot_translation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
    translate_strategy_assignment_draft,
)
from ims.strategies.catalog import StrategyActorType


STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION = (
    "ims.strategy-assignment-snapshot-materialization-validation.v1"
)

_NESTED_BY_ID = {
    definition.schema_id: definition
    for definition in STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS
}
_RULE_BY_STRATEGY_ID = {
    definition.strategy_id: definition
    for definition in VN_SNAPSHOT_MATERIALIZATION_RULES
}


@dataclass(frozen=True, slots=True)
class StrategySnapshotMaterializationValidationIssue:
    stage: str
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class StrategySnapshotMaterializationValidationReport:
    valid: bool
    base_context_valid: bool
    draft_id: str | None
    period: int | None
    expected_vn_entry_count: int
    validated_vn_entry_count: int
    validated_nested_value_count: int
    nested_loader_invocation_count: int
    issues: tuple[StrategySnapshotMaterializationValidationIssue, ...]
    schema_version: str = (
        STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
    )
    mode: str = "strategy_assignment_snapshot_materialization_validation"
    writes_performed: bool = False
    snapshots_created: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False
    historical_full_equality_claim: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "status": "ok" if self.valid else "error",
            "valid": self.valid,
            "base_context_valid": self.base_context_valid,
            "draft_id": self.draft_id,
            "period": self.period,
            "expected_vn_entry_count": self.expected_vn_entry_count,
            "validated_vn_entry_count": self.validated_vn_entry_count,
            "validated_nested_value_count": self.validated_nested_value_count,
            "nested_loader_invocation_count": self.nested_loader_invocation_count,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "materialization_input_valid": self.valid,
            "context_values_inspected": self.base_context_valid,
            "context_values_consumed": False,
            "nested_loader_results_retained": False,
            "snapshot_loader_invocation_performed": False,
            "snapshot_materialization_ready": False,
            "writes_performed": self.writes_performed,
            "snapshots_created": self.snapshots_created,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "historical_full_equality_claim": self.historical_full_equality_claim,
        }


class _NestedValueError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _add_issue(
    issues: list[StrategySnapshotMaterializationValidationIssue],
    *,
    stage: str,
    path: str,
    code: str,
    message: str,
) -> None:
    issues.append(
        StrategySnapshotMaterializationValidationIssue(
            stage=stage,
            path=path,
            code=code,
            message=message,
        )
    )


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _object_with_fields(
    value: object,
    *,
    required: set[str],
    optional: set[str] | None = None,
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise _NestedValueError(
            "nested_object_required",
            "Verschachtelter VN-Wert muss ein Objekt sein",
        )
    optional = optional or set()
    missing = required - set(value)
    unknown = set(value) - required - optional
    if missing or unknown:
        details: list[str] = []
        if missing:
            details.append(f"fehlend: {', '.join(sorted(missing))}")
        if unknown:
            details.append(f"unbekannt: {', '.join(sorted(unknown))}")
        raise _NestedValueError(
            "nested_fields_mismatch",
            f"Verschachtelte VN-Felder stimmen nicht exakt ({'; '.join(details)})",
        )
    return value


def _two_numbers(
    value: object,
    *,
    non_negative: bool = False,
    unit_interval: bool = False,
) -> list[float]:
    if not isinstance(value, list) or len(value) != 2:
        raise _NestedValueError(
            "two_sector_values_required",
            "VN-Wert muss genau zwei explizite Sektorwerte enthalten",
        )
    if not all(_is_finite_number(item) for item in value):
        raise _NestedValueError(
            "nested_number_invalid",
            "VN-Sektorwerte muessen endliche Zahlen sein",
        )
    numbers = [float(item) for item in value]
    if non_negative and any(item < 0.0 for item in numbers):
        raise _NestedValueError(
            "nested_number_negative",
            "VN-Sektorwerte muessen nicht negativ sein",
        )
    if unit_interval and any(item < 0.0 or item >= 1.0 for item in numbers):
        raise _NestedValueError(
            "nested_draw_out_of_range",
            "VN-Ziehungen muessen in [0.0, 1.0) liegen",
        )
    return numbers


def _positive_integer(value: object, *, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise _NestedValueError(
            "nested_identifier_invalid",
            f"{field_name} muss eine positive Ganzzahl sein",
        )
    return value


def _validate_initial_decisions(value: object) -> None:
    if not isinstance(value, list) or len(value) != 2:
        raise _NestedValueError(
            "two_sector_decisions_required",
            "initial_decisions muss genau zwei Sektorentscheidungen enthalten",
        )
    sectors: list[int] = []
    for item in value:
        mapping = _object_with_fields(
            item,
            required={"sector_index", "insured"},
            optional={"insurer_id", "premium"},
        )
        sector_index = mapping["sector_index"]
        if (
            not isinstance(sector_index, int)
            or isinstance(sector_index, bool)
            or sector_index not in (0, 1)
        ):
            raise _NestedValueError(
                "sector_index_invalid",
                "sector_index muss 0 oder 1 sein",
            )
        insured = mapping["insured"]
        if not isinstance(insured, bool):
            raise _NestedValueError(
                "insured_boolean_required",
                "insured muss ein boolescher Wert sein",
            )
        insurer_id = mapping.get("insurer_id")
        if insurer_id is not None:
            _positive_integer(insurer_id, field_name="insurer_id")
        if insured and insurer_id is None:
            raise _NestedValueError(
                "insured_decision_requires_insurer",
                "Versicherte Anfangsentscheidung benoetigt insurer_id",
            )
        if not insured and insurer_id is not None:
            raise _NestedValueError(
                "uninsured_decision_forbids_insurer",
                "Unversicherte Anfangsentscheidung darf keinen Versicherer nennen",
            )
        premium = mapping.get("premium")
        if premium is not None and (
            not _is_finite_number(premium) or float(premium) < 0.0
        ):
            raise _NestedValueError(
                "initial_premium_invalid",
                "Anfangspraemie muss eine endliche nicht negative Zahl sein",
            )
        sectors.append(sector_index)
    if sorted(sectors) != [0, 1]:
        raise _NestedValueError(
            "sector_decisions_not_unique",
            "initial_decisions benoetigt je eine Entscheidung fuer Sektor 0 und 1",
        )


def _validate_draw_object(value: object, field_names: tuple[str, ...]) -> None:
    mapping = _object_with_fields(value, required=set(field_names))
    for field_name in field_names:
        _two_numbers(mapping[field_name], unit_interval=True)


def _validate_sample_draws(value: object) -> None:
    mapping = _object_with_fields(
        value,
        required={"insurer_choice_draws_by_sector"},
    )
    sectors = mapping["insurer_choice_draws_by_sector"]
    if not isinstance(sectors, list) or len(sectors) != 2:
        raise _NestedValueError(
            "two_sector_draw_lists_required",
            "Stichprobensuche benoetigt genau zwei Sektor-Ziehungslisten",
        )
    for draws in sectors:
        if not isinstance(draws, list):
            raise _NestedValueError(
                "sector_draw_list_required",
                "Jeder Sektor der Stichprobensuche benoetigt eine Ziehungsliste",
            )
        if not all(_is_finite_number(draw) for draw in draws):
            raise _NestedValueError(
                "nested_number_invalid",
                "Stichprobenziehungen muessen endliche Zahlen sein",
            )
        if any(float(draw) < 0.0 or float(draw) >= 1.0 for draw in draws):
            raise _NestedValueError(
                "nested_draw_out_of_range",
                "Stichprobenziehungen muessen in [0.0, 1.0) liegen",
            )


def _validate_insurer_inputs(
    value: object,
    *,
    vector_field: str,
) -> None:
    if not isinstance(value, list):
        raise _NestedValueError(
            "insurer_input_list_required",
            "VN-Versicherereingaben muessen eine Liste sein",
        )
    if not value:
        raise _NestedValueError(
            "insurer_inputs_empty",
            "VN-Regel benoetigt mindestens einen aktiven Versicherereingang",
        )
    insurer_ids: list[int] = []
    for item in value:
        mapping = _object_with_fields(
            item,
            required={"insurer_id", vector_field},
        )
        insurer_ids.append(
            _positive_integer(mapping["insurer_id"], field_name="insurer_id")
        )
        _two_numbers(mapping[vector_field], non_negative=True)
    if len(set(insurer_ids)) != len(insurer_ids):
        raise _NestedValueError(
            "insurer_ids_not_unique",
            "VN-Versicherereingaben duerfen keine doppelten insurer_id enthalten",
        )


def _validate_search_history(value: object, *, period: int) -> None:
    if not isinstance(value, list):
        raise _NestedValueError(
            "history_list_required",
            "VN-Suchhistorie muss eine Liste sein",
        )
    keys: set[tuple[int, int]] = set()
    for item in value:
        mapping = _object_with_fields(
            item,
            required={"period", "sector_index", "insured", "premium"},
            optional={"insurer_id"},
        )
        item_period = mapping["period"]
        if (
            not isinstance(item_period, int)
            or isinstance(item_period, bool)
            or item_period < 1
        ):
            raise _NestedValueError(
                "history_period_invalid",
                "Historienperiode muss eine positive Ganzzahl sein",
            )
        if item_period >= period:
            raise _NestedValueError(
                "history_period_not_before_context",
                "Historienperiode muss vor der Kontextperiode liegen",
            )
        sector_index = mapping["sector_index"]
        if (
            not isinstance(sector_index, int)
            or isinstance(sector_index, bool)
            or sector_index not in (0, 1)
        ):
            raise _NestedValueError(
                "sector_index_invalid",
                "Historien-Sektor muss 0 oder 1 sein",
            )
        insured = mapping["insured"]
        if not isinstance(insured, bool):
            raise _NestedValueError(
                "insured_boolean_required",
                "Historienfeld insured muss boolesch sein",
            )
        premium = mapping["premium"]
        if not _is_finite_number(premium) or float(premium) < 0.0:
            raise _NestedValueError(
                "history_premium_invalid",
                "Historienpraemie muss eine endliche nicht negative Zahl sein",
            )
        insurer_id = mapping.get("insurer_id")
        if insurer_id is not None:
            _positive_integer(insurer_id, field_name="insurer_id")
        if insured and insurer_id is None:
            raise _NestedValueError(
                "insured_history_requires_insurer",
                "Versicherter Historieneintrag benoetigt insurer_id",
            )
        if not insured and insurer_id is not None:
            raise _NestedValueError(
                "uninsured_history_forbids_insurer",
                "Unversicherter Historieneintrag darf keinen Versicherer nennen",
            )
        key = (item_period, sector_index)
        if key in keys:
            raise _NestedValueError(
                "history_period_sector_not_unique",
                "Suchhistorie darf Periode und Sektor nicht doppelt enthalten",
            )
        keys.add(key)


def _strict_nested_shape(schema_id: str, value: object, *, period: int) -> None:
    if schema_id == "vn.initial-decisions.v1":
        _validate_initial_decisions(value)
    elif schema_id == "vn.compulsory-draws.v1":
        _validate_draw_object(value, ("insurer_choice_draws",))
    elif schema_id == "vn.random-draws.v1":
        _validate_draw_object(value, ("status_draws", "insurer_choice_draws"))
    elif schema_id in {"vn.preference-draws.v1", "vn.search-draws.v1"}:
        _validate_draw_object(value, ("fallback_insurer_choice_draws",))
    elif schema_id == "vn.preference-insurer-inputs.v1":
        _validate_insurer_inputs(value, vector_field="advertising_current_sector")
    elif schema_id == "vn.search-history.v1":
        _validate_search_history(value, period=period)
    elif schema_id == "vn.sample-search-draws.v1":
        _validate_sample_draws(value)
    elif schema_id == "vn.premium-insurer-inputs.v1":
        _validate_insurer_inputs(value, vector_field="premiums_current_sector")
    else:
        raise _NestedValueError(
            "nested_schema_unknown",
            f"Unbekanntes verschachteltes VN-Schema: {schema_id}",
        )


def _validate_nested_value(
    schema_id: str,
    value: object,
    *,
    period: int,
    path: str,
    issues: list[StrategySnapshotMaterializationValidationIssue],
) -> tuple[object | None, bool]:
    definition = _NESTED_BY_ID[schema_id]
    try:
        _strict_nested_shape(schema_id, value, period=period)
    except _NestedValueError as exc:
        _add_issue(
            issues,
            stage="nested_context",
            path=path,
            code=exc.code,
            message=str(exc),
        )
        return None, False

    module = importlib.import_module(definition.loader_module)
    loader = getattr(module, definition.loader_entrypoint)
    try:
        return loader(value), True
    except (TypeError, ValueError, OverflowError) as exc:
        _add_issue(
            issues,
            stage="nested_loader",
            path=path,
            code="nested_loader_rejected",
            message=str(exc),
        )
        return None, True


def _required_fields(
    definition: VNSnapshotMaterializationRuleDefinition,
    *,
    period: int,
) -> tuple[str, ...]:
    if period == 1:
        return definition.period_one_required_fields
    return definition.periods_after_one_required_fields


def _add_required_value_issues(
    definition: VNSnapshotMaterializationRuleDefinition,
    values: dict[str, object],
    *,
    period: int,
    path: str,
    issues: list[StrategySnapshotMaterializationValidationIssue],
) -> None:
    for field_name in _required_fields(definition, period=period):
        if values[field_name] is None:
            _add_issue(
                issues,
                stage="period_condition",
                path=f"{path}.{field_name}",
                code="required_context_value_open",
                message=(
                    f"{field_name} darf fuer {definition.strategy_id} "
                    f"in Periode {period} nicht null sein"
                ),
            )


def _validate_active_insurer_ids(
    values: dict[str, object],
    *,
    require_non_empty: bool,
    path: str,
    issues: list[StrategySnapshotMaterializationValidationIssue],
) -> None:
    active_ids = values["active_insurer_ids"]
    if active_ids is None:
        return
    assert isinstance(active_ids, list)
    if len(set(active_ids)) != len(active_ids):
        _add_issue(
            issues,
            stage="period_condition",
            path=f"{path}.active_insurer_ids",
            code="active_insurer_ids_not_unique",
            message="active_insurer_ids darf keine doppelten VU-IDs enthalten",
        )
    if require_non_empty and not active_ids:
        _add_issue(
            issues,
            stage="period_condition",
            path=f"{path}.active_insurer_ids",
            code="active_insurer_ids_empty",
            message="VN-Regel benoetigt mindestens einen aktiven Versicherer",
        )


def _validate_damage_probabilities(
    values: dict[str, object],
    *,
    path: str,
    issues: list[StrategySnapshotMaterializationValidationIssue],
) -> None:
    probabilities = values["damage_probabilities"]
    if probabilities is not None and any(value < 0.0 for value in probabilities):
        _add_issue(
            issues,
            stage="period_condition",
            path=f"{path}.damage_probabilities",
            code="damage_probability_negative",
            message="Schadenwahrscheinlichkeiten muessen nicht negativ sein",
        )


def _validate_information_cost(
    values: dict[str, object],
    field_name: str,
    *,
    path: str,
    issues: list[StrategySnapshotMaterializationValidationIssue],
) -> None:
    if values[field_name] < 0.0:
        _add_issue(
            issues,
            stage="period_condition",
            path=f"{path}.{field_name}",
            code="information_cost_negative",
            message=f"{field_name} muss nicht negativ sein",
        )


def _fallback_draws_required_for_preference(insurer_inputs: object) -> bool:
    return any(
        sum(item.advertising_current_sector[sector_index] for item in insurer_inputs)
        <= 0.0
        for sector_index in range(2)
    )


def _fallback_draws_required_for_search(history: object) -> bool:
    return any(
        not any(
            item.sector_index == sector_index and item.insured
            for item in history
        )
        for sector_index in range(2)
    )


def _validate_sample_sizes(
    parameters: object,
    values: dict[str, object],
    draws: object | None,
    *,
    path: str,
    issues: list[StrategySnapshotMaterializationValidationIssue],
) -> None:
    if parameters is None:
        _add_issue(
            issues,
            stage="period_condition",
            path=path,
            code="typed_parameters_missing",
            message="Vrvn05 benoetigt den typisierten Parameterblock aus PR110",
        )
        return
    sample_sizes = (
        parameters.sample_sizes_shock
        if values["change_shock"]
        else parameters.sample_sizes_normal
    )
    if any(value <= 0 for value in sample_sizes):
        _add_issue(
            issues,
            stage="period_condition",
            path=path,
            code="sample_size_not_positive",
            message="Wirksame Vrvn05-Stichprobengroessen muessen positiv sein",
        )
    if draws is None:
        return
    for sector_index, sample_size in enumerate(sample_sizes):
        if len(draws.insurer_choice_draws_by_sector[sector_index]) < sample_size:
            _add_issue(
                issues,
                stage="period_condition",
                path=f"{path}.draws.insurer_choice_draws_by_sector",
                code="sample_draw_count_insufficient",
                message=(
                    f"Sektor {sector_index} benoetigt mindestens "
                    f"{sample_size} Stichprobenziehungen"
                ),
            )


def _validate_later_period_conditions(
    definition: VNSnapshotMaterializationRuleDefinition,
    values: dict[str, object],
    loaded_values: dict[str, object],
    parameters: object,
    *,
    path: str,
    issues: list[StrategySnapshotMaterializationValidationIssue],
) -> None:
    strategy_id = definition.strategy_id
    if "damage_probabilities" in definition.periods_after_one_required_fields:
        _validate_damage_probabilities(values, path=path, issues=issues)

    if strategy_id in {"vn.vrvn01", "vn.vrvn02"}:
        _validate_active_insurer_ids(
            values,
            require_non_empty=True,
            path=path,
            issues=issues,
        )
    elif strategy_id == "vn.vrvn03":
        insurer_inputs = loaded_values.get("insurer_inputs")
        if (
            insurer_inputs is not None
            and _fallback_draws_required_for_preference(insurer_inputs)
            and values["draws"] is None
        ):
            _add_issue(
                issues,
                stage="period_condition",
                path=f"{path}.draws",
                code="conditional_context_value_required",
                message="Vrvn03 benoetigt Fallback-Ziehungen ohne positive Werbung",
            )
    elif strategy_id == "vn.vrvn04":
        history = loaded_values.get("history")
        fallback_required = (
            history is not None and _fallback_draws_required_for_search(history)
        )
        _validate_active_insurer_ids(
            values,
            require_non_empty=fallback_required,
            path=path,
            issues=issues,
        )
        if fallback_required and values["draws"] is None:
            _add_issue(
                issues,
                stage="period_condition",
                path=f"{path}.draws",
                code="conditional_context_value_required",
                message="Vrvn04 benoetigt Fallback-Ziehungen ohne versicherte Historie",
            )
    elif strategy_id == "vn.vrvn05":
        _validate_information_cost(
            values,
            "information_cost_per_sample",
            path=path,
            issues=issues,
        )
        _validate_sample_sizes(
            parameters,
            values,
            loaded_values.get("draws"),
            path=path,
            issues=issues,
        )
    elif strategy_id == "vn.vrvn06":
        _validate_information_cost(
            values,
            "information_cost_per_insurer",
            path=path,
            issues=issues,
        )


def _report(
    *,
    valid: bool,
    base_context_valid: bool,
    draft_id: str | None,
    period: int | None,
    expected_vn_entry_count: int,
    validated_vn_entry_count: int,
    validated_nested_value_count: int,
    nested_loader_invocation_count: int,
    issues: list[StrategySnapshotMaterializationValidationIssue],
) -> StrategySnapshotMaterializationValidationReport:
    return StrategySnapshotMaterializationValidationReport(
        valid=valid,
        base_context_valid=base_context_valid,
        draft_id=draft_id,
        period=period,
        expected_vn_entry_count=expected_vn_entry_count,
        validated_vn_entry_count=validated_vn_entry_count,
        validated_nested_value_count=validated_nested_value_count,
        nested_loader_invocation_count=nested_loader_invocation_count,
        issues=tuple(issues),
    )


def validate_strategy_assignment_snapshot_materialization_input(
    value: object,
) -> StrategySnapshotMaterializationValidationReport:
    """Prueft PR112-Kontexte gegen PR114, ohne Snapshots zu erzeugen."""

    base_report = validate_strategy_assignment_snapshot_context(value)
    issues = [
        StrategySnapshotMaterializationValidationIssue(
            stage="base_context",
            path=issue.path,
            code=issue.code,
            message=issue.message,
        )
        for issue in base_report.issues
    ]
    translation = translate_strategy_assignment_draft(
        value.get("draft") if isinstance(value, dict) else None
    )
    vn_entries = tuple(
        entry
        for entry in translation.entries
        if entry.assignment.actor_type is StrategyActorType.POLICYHOLDER
    )
    if not base_report.valid:
        return _report(
            valid=False,
            base_context_valid=False,
            draft_id=base_report.draft_id,
            period=base_report.period,
            expected_vn_entry_count=len(vn_entries),
            validated_vn_entry_count=0,
            validated_nested_value_count=0,
            nested_loader_invocation_count=0,
            issues=issues,
        )

    assert isinstance(value, dict)
    context = value["context"]
    assert isinstance(context, dict)
    period = context["period"]
    assert isinstance(period, int)
    raw_entries = context["entries"]
    assert isinstance(raw_entries, list)
    context_entries = {
        (entry["actor_type"], entry["target_id"]): (index, entry)
        for index, entry in enumerate(raw_entries)
    }

    validated_vn_entry_count = 0
    validated_nested_value_count = 0
    nested_loader_invocation_count = 0
    for translation_entry in vn_entries:
        assignment = translation_entry.assignment
        index, raw_entry = context_entries[
            (assignment.actor_type.value, assignment.target_id)
        ]
        values = raw_entry["values"]
        assert isinstance(values, dict)
        path = f"$.context.entries[{index}].values"
        issue_start = len(issues)
        definition = _RULE_BY_STRATEGY_ID[assignment.strategy_id]
        _add_required_value_issues(
            definition,
            values,
            period=period,
            path=path,
            issues=issues,
        )

        required_fields = set(_required_fields(definition, period=period))
        conditional_fields = (
            {
                item.field_name
                for item in definition.periods_after_one_conditional_fields
            }
            if period > 1
            else set()
        )
        loaded_values: dict[str, object] = {}
        schemas_by_field = {
            _NESTED_BY_ID[schema_id].field_name: schema_id
            for schema_id in definition.nested_value_schema_ids
        }
        for field_name in sorted((required_fields | conditional_fields) & set(schemas_by_field)):
            field_value = values[field_name]
            if field_value is None:
                continue
            loaded_value, loader_invoked = _validate_nested_value(
                schemas_by_field[field_name],
                field_value,
                period=period,
                path=f"{path}.{field_name}",
                issues=issues,
            )
            if loader_invoked:
                nested_loader_invocation_count += 1
            if loaded_value is not None:
                validated_nested_value_count += 1
                loaded_values[field_name] = loaded_value

        if period > 1:
            _validate_later_period_conditions(
                definition,
                values,
                loaded_values,
                translation_entry.parameters,
                path=path,
                issues=issues,
            )
        if len(issues) == issue_start:
            validated_vn_entry_count += 1

    valid = not issues and validated_vn_entry_count == len(vn_entries)
    return _report(
        valid=valid,
        base_context_valid=True,
        draft_id=base_report.draft_id,
        period=period,
        expected_vn_entry_count=len(vn_entries),
        validated_vn_entry_count=validated_vn_entry_count,
        validated_nested_value_count=validated_nested_value_count,
        nested_loader_invocation_count=nested_loader_invocation_count,
        issues=issues,
    )


def strategy_assignment_snapshot_materialization_validation_contract_payload(
) -> dict[str, Any]:
    """Beschreibt die atomare PR115-Pruefung und ihre geschlossenen Grenzen."""

    return {
        "schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
        ),
        "materialization_contract_schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION
        ),
        "context_validation_schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION
        ),
        "translation_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
        "mode": "strategy_assignment_snapshot_materialization_validation_contract",
        "base_model": "Vdefmd6",
        "scope": "atomic_rule_specific_single_period_input_validation",
        "validation_endpoint": (
            "/api/strategies/assignment-snapshot-materialization-validation"
        ),
        "validation_order": (
            "validate_pr112_context_atomically",
            "select_policyholder_entries",
            "check_period_required_values",
            "check_strict_nested_shapes",
            "invoke_existing_nested_loaders_without_retaining_results",
            "check_rule_specific_period_conditions",
            "accept_only_when_every_vn_entry_is_valid",
        ),
        "validated_rule_count": len(VN_SNAPSHOT_MATERIALIZATION_RULES),
        "validated_nested_schema_count": len(
            STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS
        ),
        "materialization_contract_issue_count": len(
            strategy_snapshot_materialization_contract_issues()
        ),
        "period_one_uses_initial_decisions_only": True,
        "strict_two_sector_values_required": True,
        "conditional_fallback_draws_validated": True,
        "history_must_precede_context_period": True,
        "sample_draw_counts_validated": True,
        "partial_acceptance_allowed": False,
        "defaults_applied": False,
        "nested_loader_invocation_enabled": True,
        "nested_loader_results_retained": False,
        "snapshot_loader_invocation_enabled": False,
        "snapshot_materialization_enabled": False,
        "persistence_enabled": False,
        "execution_enabled": False,
        "runner_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
