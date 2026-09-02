from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib
import math
from typing import Any

from ims.model.vdefmd6_population import (
    VDEFMD6_INSURER_COUNT,
    VDEFMD6_POLICYHOLDER_COUNT,
)
from ims.strategies.assignment_contract import (
    STRATEGY_ASSIGNMENT_CONTRACT_VERSION,
    STRATEGY_PARAMETER_SCHEMAS,
    StrategyParameterSchemaDefinition,
)
from ims.strategies.catalog import (
    STRATEGY_CATALOG_VERSION,
    STRATEGY_DEFINITIONS,
    StrategyActorType,
    StrategyDefinition,
)


STRATEGY_ASSIGNMENT_DRAFT_VERSION = "ims.strategy-assignment-draft.v1"
STRATEGY_ASSIGNMENT_DRAFT_VALIDATION_VERSION = (
    "ims.strategy-assignment-draft-validation.v1"
)

_DOCUMENT_FIELDS = frozenset(
    {
        "schema_version",
        "catalog_schema_version",
        "assignment_contract_schema_version",
        "base_model",
        "scope",
        "draft_id",
        "label",
        "assignments",
    }
)
_ASSIGNMENT_FIELDS = frozenset(
    {
        "actor_type",
        "target_id",
        "strategy_id",
        "activation_period",
        "active_through_run",
        "logical_time",
        "parameter_schema",
        "parameter_values",
    }
)
_TARGET_LIMITS = {
    StrategyActorType.INSURER: VDEFMD6_INSURER_COUNT,
    StrategyActorType.POLICYHOLDER: VDEFMD6_POLICYHOLDER_COUNT,
}
_STRATEGIES_BY_ID = {strategy.strategy_id: strategy for strategy in STRATEGY_DEFINITIONS}
_SCHEMAS_BY_ID = {schema.schema_id: schema for schema in STRATEGY_PARAMETER_SCHEMAS}


@dataclass(frozen=True, slots=True)
class StrategyAssignmentDraftIssue:
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class StrategyAssignmentDraftEntry:
    actor_type: StrategyActorType
    target_id: int
    strategy_id: str
    activation_period: int
    active_through_run: int
    logical_time: int
    parameter_schema: str | None
    parameter_values: dict[str, tuple[int | float, int | float]] | None

    def to_dict(self) -> dict[str, object]:
        return {
            "actor_type": self.actor_type,
            "target_id": self.target_id,
            "strategy_id": self.strategy_id,
            "activation_period": self.activation_period,
            "active_through_run": self.active_through_run,
            "logical_time": self.logical_time,
            "parameter_schema": self.parameter_schema,
            "parameter_values": (
                None
                if self.parameter_values is None
                else {key: list(values) for key, values in self.parameter_values.items()}
            ),
        }


@dataclass(frozen=True, slots=True)
class StrategyAssignmentDraft:
    draft_id: str
    label: str
    assignments: tuple[StrategyAssignmentDraftEntry, ...]
    schema_version: str = STRATEGY_ASSIGNMENT_DRAFT_VERSION
    catalog_schema_version: str = STRATEGY_CATALOG_VERSION
    assignment_contract_schema_version: str = STRATEGY_ASSIGNMENT_CONTRACT_VERSION
    base_model: str = "Vdefmd6"
    scope: str = "partial_actor_assignments"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "catalog_schema_version": self.catalog_schema_version,
            "assignment_contract_schema_version": self.assignment_contract_schema_version,
            "base_model": self.base_model,
            "scope": self.scope,
            "draft_id": self.draft_id,
            "label": self.label,
            "assignments": [assignment.to_dict() for assignment in self.assignments],
        }


@dataclass(frozen=True, slots=True)
class StrategyAssignmentDraftValidationReport:
    valid: bool
    submitted_schema_version: str | None
    assignment_count: int
    validated_assignment_count: int
    issues: tuple[StrategyAssignmentDraftIssue, ...]
    schema_version: str = STRATEGY_ASSIGNMENT_DRAFT_VALIDATION_VERSION
    mode: str = "strategy_assignment_draft_validation"
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
            "submitted_schema_version": self.submitted_schema_version,
            "assignment_count": self.assignment_count,
            "validated_assignment_count": self.validated_assignment_count,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "writes_performed": self.writes_performed,
            "snapshots_created": self.snapshots_created,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "historical_full_equality_claim": self.historical_full_equality_claim,
        }


def _add_issue(
    issues: list[StrategyAssignmentDraftIssue],
    path: str,
    code: str,
    message: str,
) -> None:
    issues.append(StrategyAssignmentDraftIssue(path=path, code=code, message=message))


def _required_positive_int(
    mapping: dict[str, object],
    key: str,
    path: str,
    issues: list[StrategyAssignmentDraftIssue],
) -> int | None:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        _add_issue(
            issues,
            f"{path}.{key}",
            "positive_integer_required",
            f"{key} muss eine positive Ganzzahl sein",
        )
        return None
    return value


def _required_nonempty_string(
    mapping: dict[str, object],
    key: str,
    path: str,
    issues: list[StrategyAssignmentDraftIssue],
) -> str | None:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        _add_issue(
            issues,
            f"{path}.{key}",
            "nonempty_string_required",
            f"{key} muss eine nichtleere Zeichenkette sein",
        )
        return None
    return value


def _check_exact_value(
    mapping: dict[str, object],
    key: str,
    expected: object,
    issues: list[StrategyAssignmentDraftIssue],
) -> None:
    if mapping.get(key) != expected:
        _add_issue(
            issues,
            f"$.{key}",
            "contract_value_mismatch",
            f"{key} muss {expected!r} sein",
        )


def _validate_parameter_values(
    values: object,
    schema: StrategyParameterSchemaDefinition,
    path: str,
    issues: list[StrategyAssignmentDraftIssue],
) -> dict[str, tuple[int | float, int | float]] | None:
    if not isinstance(values, dict):
        _add_issue(
            issues,
            path,
            "parameter_values_object_required",
            "parameter_values muss fuer diese Strategie ein Objekt sein",
        )
        return None

    expected_fields = {field.field_name for field in schema.fields}
    actual_fields = set(values)
    for field_name in sorted(expected_fields - actual_fields):
        _add_issue(
            issues,
            f"{path}.{field_name}",
            "parameter_field_missing",
            f"Pflichtfeld des Parameterschemas fehlt: {field_name}",
        )
    for field_name in sorted(actual_fields - expected_fields):
        _add_issue(
            issues,
            f"{path}.{field_name}",
            "parameter_field_unknown",
            f"Unbekanntes Feld fuer {schema.schema_id}: {field_name}",
        )

    normalized: dict[str, tuple[int | float, int | float]] = {}
    for field in schema.fields:
        value = values.get(field.field_name)
        field_path = f"{path}.{field.field_name}"
        if field.field_name not in values:
            continue
        if not isinstance(value, list) or len(value) != 2:
            _add_issue(
                issues,
                field_path,
                "legacy_two_position_vector_required",
                "Parameterfeld muss genau zwei historische Sektorwerte enthalten",
            )
            continue

        field_values: list[int | float] = []
        for index, item in enumerate(value):
            item_path = f"{field_path}[{index}]"
            if field.python_type == "list[int]":
                if not isinstance(item, int) or isinstance(item, bool):
                    _add_issue(
                        issues,
                        item_path,
                        "integer_required",
                        "Stichprobengroesse muss eine Ganzzahl sein",
                    )
                    continue
                if item < 0:
                    _add_issue(
                        issues,
                        item_path,
                        "existing_parameter_bound_failed",
                        "Stichprobengroesse darf nach vorhandenem Loader nicht negativ sein",
                    )
                    continue
            elif not isinstance(item, (int, float)) or isinstance(item, bool):
                _add_issue(
                    issues,
                    item_path,
                    "number_required",
                    "Parameterwert muss numerisch sein",
                )
                continue
            if isinstance(item, float) and not math.isfinite(item):
                _add_issue(
                    issues,
                    item_path,
                    "finite_number_required",
                    "Parameterwert muss endlich sein",
                )
                continue
            field_values.append(item)
        if len(field_values) == 2:
            normalized[field.field_name] = (field_values[0], field_values[1])

    if set(normalized) != expected_fields or actual_fields != expected_fields:
        return None

    module = importlib.import_module(schema.module)
    loader = getattr(module, schema.loader_entrypoint)
    try:
        loader({key: list(value) for key, value in normalized.items()})
    except (TypeError, ValueError, OverflowError) as exc:
        _add_issue(
            issues,
            path,
            "existing_parameter_loader_rejected",
            f"Vorhandener Parameterloader lehnt die Werte ab: {exc}",
        )
        return None
    return normalized


def _validate_assignment(
    value: object,
    index: int,
    seen_targets: set[tuple[StrategyActorType, int]],
    issues: list[StrategyAssignmentDraftIssue],
) -> StrategyAssignmentDraftEntry | None:
    path = f"$.assignments[{index}]"
    issue_start = len(issues)
    if not isinstance(value, dict):
        _add_issue(
            issues,
            path,
            "assignment_object_required",
            "Zuordnung muss ein Objekt sein",
        )
        return None

    missing_fields = _ASSIGNMENT_FIELDS - set(value)
    unknown_fields = set(value) - _ASSIGNMENT_FIELDS
    for field_name in sorted(missing_fields):
        _add_issue(
            issues,
            f"{path}.{field_name}",
            "assignment_field_missing",
            f"Pflichtfeld der Zuordnung fehlt: {field_name}",
        )
    for field_name in sorted(unknown_fields):
        _add_issue(
            issues,
            f"{path}.{field_name}",
            "assignment_field_unknown",
            f"Unbekanntes Zuordnungsfeld: {field_name}",
        )

    actor_type: StrategyActorType | None = None
    raw_actor_type = value.get("actor_type")
    try:
        actor_type = StrategyActorType(raw_actor_type)
    except (TypeError, ValueError):
        _add_issue(
            issues,
            f"{path}.actor_type",
            "actor_type_unknown",
            "actor_type muss insurer oder policyholder sein",
        )

    target_id = _required_positive_int(value, "target_id", path, issues)
    if actor_type is not None and target_id is not None:
        target_limit = _TARGET_LIMITS[actor_type]
        if target_id > target_limit:
            _add_issue(
                issues,
                f"{path}.target_id",
                "target_out_of_vdefmd6_range",
                f"Ziel-ID liegt ausserhalb der Vdefmd6-Grenze 1-{target_limit}",
            )
        target_key = (actor_type, target_id)
        if target_key in seen_targets:
            _add_issue(
                issues,
                f"{path}.target_id",
                "duplicate_actor_assignment",
                "Akteur ist in diesem Entwurf bereits zugeordnet",
            )
        seen_targets.add(target_key)

    strategy_id = _required_nonempty_string(value, "strategy_id", path, issues)
    strategy: StrategyDefinition | None = None
    if strategy_id is not None:
        strategy = _STRATEGIES_BY_ID.get(strategy_id)
        if strategy is None:
            _add_issue(
                issues,
                f"{path}.strategy_id",
                "strategy_unknown",
                f"Unbekannte Katalogstrategie: {strategy_id}",
            )
        elif actor_type is not None and strategy.actor_type is not actor_type:
            _add_issue(
                issues,
                f"{path}.strategy_id",
                "strategy_actor_mismatch",
                "Strategie ist fuer den angegebenen Akteurstyp nicht zulaessig",
            )

    activation_period = _required_positive_int(value, "activation_period", path, issues)
    active_through_run = _required_positive_int(value, "active_through_run", path, issues)
    logical_time = _required_positive_int(value, "logical_time", path, issues)
    if (
        activation_period is not None
        and active_through_run is not None
        and activation_period > active_through_run
    ):
        _add_issue(
            issues,
            f"{path}.active_through_run",
            "activation_window_invalid",
            "active_through_run darf nicht vor activation_period liegen",
        )

    parameter_schema: str | None = None
    parameter_values: dict[str, tuple[int | float, int | float]] | None = None
    if strategy is not None:
        expected_schema = strategy.parameter_schema
        raw_schema = value.get("parameter_schema")
        raw_values = value.get("parameter_values")
        if raw_schema != expected_schema:
            _add_issue(
                issues,
                f"{path}.parameter_schema",
                "parameter_schema_mismatch",
                f"parameter_schema muss fuer {strategy.strategy_id} {expected_schema!r} sein",
            )
        else:
            parameter_schema = expected_schema
        if expected_schema is None:
            if raw_values is not None:
                _add_issue(
                    issues,
                    f"{path}.parameter_values",
                    "parameter_values_not_supported",
                    "Diese Strategie besitzt keinen Strategieparameterblock",
                )
        else:
            schema = _SCHEMAS_BY_ID[expected_schema]
            parameter_values = _validate_parameter_values(
                raw_values,
                schema,
                f"{path}.parameter_values",
                issues,
            )

    if len(issues) != issue_start:
        return None
    assert actor_type is not None
    assert target_id is not None
    assert strategy_id is not None
    assert activation_period is not None
    assert active_through_run is not None
    assert logical_time is not None
    return StrategyAssignmentDraftEntry(
        actor_type=actor_type,
        target_id=target_id,
        strategy_id=strategy_id,
        activation_period=activation_period,
        active_through_run=active_through_run,
        logical_time=logical_time,
        parameter_schema=parameter_schema,
        parameter_values=parameter_values,
    )


def _parse_strategy_assignment_draft(
    value: object,
) -> tuple[StrategyAssignmentDraft | None, StrategyAssignmentDraftValidationReport]:
    issues: list[StrategyAssignmentDraftIssue] = []
    if not isinstance(value, dict):
        _add_issue(
            issues,
            "$",
            "draft_object_required",
            "Strategiezuordnungsentwurf muss ein Objekt sein",
        )
        return None, StrategyAssignmentDraftValidationReport(
            valid=False,
            submitted_schema_version=None,
            assignment_count=0,
            validated_assignment_count=0,
            issues=tuple(issues),
        )

    submitted_schema_version = (
        value.get("schema_version") if isinstance(value.get("schema_version"), str) else None
    )
    for field_name in sorted(_DOCUMENT_FIELDS - set(value)):
        _add_issue(
            issues,
            f"$.{field_name}",
            "draft_field_missing",
            f"Pflichtfeld des Entwurfs fehlt: {field_name}",
        )
    for field_name in sorted(set(value) - _DOCUMENT_FIELDS):
        _add_issue(
            issues,
            f"$.{field_name}",
            "draft_field_unknown",
            f"Unbekanntes Entwurfsfeld: {field_name}",
        )

    _check_exact_value(value, "schema_version", STRATEGY_ASSIGNMENT_DRAFT_VERSION, issues)
    _check_exact_value(value, "catalog_schema_version", STRATEGY_CATALOG_VERSION, issues)
    _check_exact_value(
        value,
        "assignment_contract_schema_version",
        STRATEGY_ASSIGNMENT_CONTRACT_VERSION,
        issues,
    )
    _check_exact_value(value, "base_model", "Vdefmd6", issues)
    _check_exact_value(value, "scope", "partial_actor_assignments", issues)
    draft_id = _required_nonempty_string(value, "draft_id", "$", issues)
    label = _required_nonempty_string(value, "label", "$", issues)

    raw_assignments = value.get("assignments")
    assignment_count = len(raw_assignments) if isinstance(raw_assignments, list) else 0
    assignments: list[StrategyAssignmentDraftEntry] = []
    if not isinstance(raw_assignments, list):
        _add_issue(
            issues,
            "$.assignments",
            "assignments_list_required",
            "assignments muss eine Liste sein",
        )
    elif not raw_assignments:
        _add_issue(
            issues,
            "$.assignments",
            "assignment_required",
            "Entwurf muss mindestens eine Zuordnung enthalten",
        )
    else:
        seen_targets: set[tuple[StrategyActorType, int]] = set()
        for index, raw_assignment in enumerate(raw_assignments):
            assignment = _validate_assignment(raw_assignment, index, seen_targets, issues)
            if assignment is not None:
                assignments.append(assignment)

    report = StrategyAssignmentDraftValidationReport(
        valid=not issues,
        submitted_schema_version=submitted_schema_version,
        assignment_count=assignment_count,
        validated_assignment_count=len(assignments),
        issues=tuple(issues),
    )
    if issues:
        return None, report
    assert draft_id is not None
    assert label is not None
    return (
        StrategyAssignmentDraft(
            draft_id=draft_id,
            label=label,
            assignments=tuple(assignments),
        ),
        report,
    )


def validate_strategy_assignment_draft(
    value: object,
) -> StrategyAssignmentDraftValidationReport:
    """Prueft einen Entwurf rein im Speicher, ohne Snapshot oder Ausfuehrung."""

    return _parse_strategy_assignment_draft(value)[1]


def load_strategy_assignment_draft(value: object) -> StrategyAssignmentDraft:
    """Laedt einen gueltigen Entwurf oder meldet alle strukturellen Fehler."""

    draft, report = _parse_strategy_assignment_draft(value)
    if draft is None:
        details = "; ".join(f"{issue.path}: {issue.message}" for issue in report.issues)
        raise ValueError(f"Ungueltiger Strategiezuordnungsentwurf: {details}")
    return draft


def strategy_assignment_draft_contract_payload() -> dict[str, Any]:
    """Beschreibt das versionierte Format und seine geschlossenen Grenzen."""

    return {
        "schema_version": STRATEGY_ASSIGNMENT_DRAFT_VERSION,
        "catalog_schema_version": STRATEGY_CATALOG_VERSION,
        "assignment_contract_schema_version": STRATEGY_ASSIGNMENT_CONTRACT_VERSION,
        "mode": "strategy_assignment_draft_contract_read_only",
        "base_model": "Vdefmd6",
        "scope": "partial_actor_assignments",
        "validation_endpoint": "/api/strategies/assignment-draft-validation",
        "document_fields": tuple(sorted(_DOCUMENT_FIELDS)),
        "assignment_fields": tuple(sorted(_ASSIGNMENT_FIELDS)),
        "target_limits": {
            actor_type: {"minimum": 1, "maximum": maximum}
            for actor_type, maximum in _TARGET_LIMITS.items()
        },
        "parameter_value_shape": {
            "mode": "legacy_two_position_vector",
            "length": 2,
            "position_keys": ("legacy_sector_1", "legacy_sector_2"),
            "named_sectors_available": False,
        },
        "parameterless_strategy_ids": tuple(
            strategy.strategy_id
            for strategy in STRATEGY_DEFINITIONS
            if strategy.parameter_schema is None
        ),
        "unknown_fields_allowed": False,
        "defaults_applied": False,
        "persistence_enabled": False,
        "workbench_editing_enabled": False,
        "snapshot_translation_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_full_equality_claim": False,
    }
