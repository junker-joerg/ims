from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
import math
from typing import Any

from ims.strategies.assignment_draft import STRATEGY_ASSIGNMENT_DRAFT_VERSION
from ims.strategies.assignment_snapshot_translation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
    STRATEGY_SNAPSHOT_TARGETS,
    translate_strategy_assignment_draft,
)
from ims.strategies.catalog import StrategyActorType


STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VERSION = (
    "ims.strategy-assignment-snapshot-context.v1"
)
STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION = (
    "ims.strategy-assignment-snapshot-context-validation.v1"
)

_REQUEST_FIELDS = frozenset({"draft", "context"})
_DOCUMENT_FIELDS = frozenset(
    {
        "schema_version",
        "translation_schema_version",
        "base_model",
        "scope",
        "draft_id",
        "period",
        "entries",
    }
)
_ENTRY_FIELDS = frozenset({"actor_type", "target_id", "strategy_id", "values"})


class StrategySnapshotContextSource(StrEnum):
    DRAW = "draw"
    PERIOD_FINANCE = "period_finance"
    SHOCK = "shock"
    STRATEGY_STATE = "strategy_state"
    MARKET_STATE = "market_state"
    PREVIOUS_PERIOD = "previous_period"


@dataclass(frozen=True, slots=True)
class StrategySnapshotContextFieldDefinition:
    field_name: str
    source: StrategySnapshotContextSource
    value_shape: str
    fixed_length: int | None = None
    nullable: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _field(
    field_name: str,
    source: StrategySnapshotContextSource,
    value_shape: str,
    *,
    fixed_length: int | None = None,
    nullable: bool = False,
) -> StrategySnapshotContextFieldDefinition:
    return StrategySnapshotContextFieldDefinition(
        field_name=field_name,
        source=source,
        value_shape=value_shape,
        fixed_length=fixed_length,
        nullable=nullable,
    )


STRATEGY_SNAPSHOT_CONTEXT_FIELDS = (
    _field(
        "random_draws",
        StrategySnapshotContextSource.DRAW,
        "number_array",
        fixed_length=4,
        nullable=True,
    ),
    _field(
        "normal_draws",
        StrategySnapshotContextSource.DRAW,
        "number_array",
        fixed_length=4,
        nullable=True,
    ),
    _field("draws", StrategySnapshotContextSource.DRAW, "object", nullable=True),
    _field("interest_rate", StrategySnapshotContextSource.PERIOD_FINANCE, "finite_number"),
    _field(
        "information_cost_per_sample",
        StrategySnapshotContextSource.PERIOD_FINANCE,
        "finite_number",
    ),
    _field(
        "information_cost_per_insurer",
        StrategySnapshotContextSource.PERIOD_FINANCE,
        "finite_number",
    ),
    _field("change_shock", StrategySnapshotContextSource.SHOCK, "boolean"),
    _field(
        "reserve_thresholds",
        StrategySnapshotContextSource.STRATEGY_STATE,
        "number_array",
        fixed_length=2,
    ),
    _field(
        "net_switcher_thresholds",
        StrategySnapshotContextSource.STRATEGY_STATE,
        "number_array",
        fixed_length=2,
    ),
    _field(
        "market_share_thresholds",
        StrategySnapshotContextSource.STRATEGY_STATE,
        "number_array",
        fixed_length=2,
    ),
    _field(
        "active_insurer_ids",
        StrategySnapshotContextSource.MARKET_STATE,
        "positive_integer_array",
        nullable=True,
    ),
    _field(
        "active_policyholder_count",
        StrategySnapshotContextSource.MARKET_STATE,
        "integer",
        nullable=True,
    ),
    _field(
        "damage_probabilities",
        StrategySnapshotContextSource.MARKET_STATE,
        "number_array",
        fixed_length=2,
        nullable=True,
    ),
    _field("insurer_inputs", StrategySnapshotContextSource.MARKET_STATE, "array", nullable=True),
    _field(
        "market_damage_indicator",
        StrategySnapshotContextSource.MARKET_STATE,
        "finite_number",
        nullable=True,
    ),
    _field(
        "previous_policyholders_sector",
        StrategySnapshotContextSource.PREVIOUS_PERIOD,
        "number_array",
        fixed_length=2,
        nullable=True,
    ),
    _field(
        "initial_decisions",
        StrategySnapshotContextSource.PREVIOUS_PERIOD,
        "array",
        nullable=True,
    ),
    _field("history", StrategySnapshotContextSource.PREVIOUS_PERIOD, "array", nullable=True),
)

_FIELD_BY_NAME = {
    definition.field_name: definition
    for definition in STRATEGY_SNAPSHOT_CONTEXT_FIELDS
}
_VALUE_SHAPES = {
    "array",
    "boolean",
    "finite_number",
    "integer",
    "number_array",
    "object",
    "positive_integer_array",
}


@dataclass(frozen=True, slots=True)
class StrategySnapshotContextIssue:
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class StrategySnapshotContextValidationReport:
    valid: bool
    draft_valid: bool
    translation_complete: bool
    submitted_schema_version: str | None
    draft_id: str | None
    period: int | None
    expected_entry_count: int
    validated_entry_count: int
    expected_value_count: int
    validated_value_count: int
    resolved_value_count: int
    explicitly_open_value_count: int
    issues: tuple[StrategySnapshotContextIssue, ...]
    schema_version: str = STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION
    mode: str = "strategy_assignment_snapshot_context_validation"
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
            "draft_valid": self.draft_valid,
            "translation_complete": self.translation_complete,
            "submitted_schema_version": self.submitted_schema_version,
            "draft_id": self.draft_id,
            "period": self.period,
            "expected_entry_count": self.expected_entry_count,
            "validated_entry_count": self.validated_entry_count,
            "expected_value_count": self.expected_value_count,
            "validated_value_count": self.validated_value_count,
            "resolved_value_count": self.resolved_value_count,
            "explicitly_open_value_count": self.explicitly_open_value_count,
            "all_context_values_supplied": (
                self.valid
                and self.resolved_value_count == self.expected_value_count
                and self.explicitly_open_value_count == 0
            ),
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "defaults_applied": False,
            "context_values_consumed": False,
            "snapshot_loader_invocation_performed": False,
            "snapshot_materialization_ready": False,
            "writes_performed": self.writes_performed,
            "snapshots_created": self.snapshots_created,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "historical_full_equality_claim": self.historical_full_equality_claim,
        }


def _add_issue(
    issues: list[StrategySnapshotContextIssue],
    path: str,
    code: str,
    message: str,
) -> None:
    issues.append(StrategySnapshotContextIssue(path=path, code=code, message=message))


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _is_json_value(value: object) -> bool:
    if value is None or isinstance(value, (str, bool)):
        return True
    if _is_finite_number(value):
        return True
    if isinstance(value, list):
        return all(_is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(
            isinstance(key, str) and _is_json_value(item)
            for key, item in value.items()
        )
    return False


def _value_matches_definition(
    value: object,
    definition: StrategySnapshotContextFieldDefinition,
) -> bool:
    if value is None:
        return definition.nullable
    if definition.value_shape == "boolean":
        return isinstance(value, bool)
    if definition.value_shape == "finite_number":
        return _is_finite_number(value)
    if definition.value_shape == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if definition.value_shape == "object":
        return isinstance(value, dict) and _is_json_value(value)
    if definition.value_shape == "array":
        return isinstance(value, list) and _is_json_value(value)
    if not isinstance(value, list):
        return False
    if definition.fixed_length is not None and len(value) != definition.fixed_length:
        return False
    if definition.value_shape == "positive_integer_array":
        return all(
            isinstance(item, int) and not isinstance(item, bool) and item > 0
            for item in value
        )
    return all(_is_finite_number(item) for item in value)


def strategy_snapshot_context_contract_issues() -> tuple[str, ...]:
    """Prueft die Feldabdeckung gegen alle offenen PR110-Snapshotfelder."""

    issues: list[str] = []
    field_names = [definition.field_name for definition in STRATEGY_SNAPSHOT_CONTEXT_FIELDS]
    if len(set(field_names)) != len(field_names):
        issues.append("Doppeltes Feld im Snapshot-Kontextvertrag")
    expected_fields = set().union(
        *(set(target.unresolved_snapshot_fields) for target in STRATEGY_SNAPSHOT_TARGETS)
    )
    if set(field_names) != expected_fields:
        issues.append("Snapshot-Kontextvertrag deckt offene Snapshotfelder nicht exakt ab")
    if any(
        definition.value_shape not in _VALUE_SHAPES
        for definition in STRATEGY_SNAPSHOT_CONTEXT_FIELDS
    ):
        issues.append("Snapshot-Kontextvertrag enthaelt eine unbekannte Wertform")
    return tuple(issues)


def _context_report(
    *,
    valid: bool,
    draft_valid: bool,
    translation_complete: bool,
    submitted_schema_version: str | None,
    draft_id: str | None,
    period: int | None,
    expected_entry_count: int,
    validated_entry_count: int,
    expected_value_count: int,
    validated_value_count: int,
    resolved_value_count: int,
    explicitly_open_value_count: int,
    issues: list[StrategySnapshotContextIssue],
) -> StrategySnapshotContextValidationReport:
    return StrategySnapshotContextValidationReport(
        valid=valid,
        draft_valid=draft_valid,
        translation_complete=translation_complete,
        submitted_schema_version=submitted_schema_version,
        draft_id=draft_id,
        period=period,
        expected_entry_count=expected_entry_count,
        validated_entry_count=validated_entry_count,
        expected_value_count=expected_value_count,
        validated_value_count=validated_value_count,
        resolved_value_count=resolved_value_count,
        explicitly_open_value_count=explicitly_open_value_count,
        issues=tuple(issues),
    )


def validate_strategy_assignment_snapshot_context(
    value: object,
) -> StrategySnapshotContextValidationReport:
    """Prueft Entwurf und Einperiodenkontext ohne Werte zu verwenden."""

    issues: list[StrategySnapshotContextIssue] = []
    if not isinstance(value, dict):
        _add_issue(
            issues,
            "$",
            "request_object_required",
            "Validierungsanfrage muss ein Objekt sein",
        )
        return _context_report(
            valid=False,
            draft_valid=False,
            translation_complete=False,
            submitted_schema_version=None,
            draft_id=None,
            period=None,
            expected_entry_count=0,
            validated_entry_count=0,
            expected_value_count=0,
            validated_value_count=0,
            resolved_value_count=0,
            explicitly_open_value_count=0,
            issues=issues,
        )

    for field_name in sorted(_REQUEST_FIELDS - set(value)):
        _add_issue(
            issues,
            f"$.{field_name}",
            "request_field_missing",
            f"Pflichtfeld der Anfrage fehlt: {field_name}",
        )
    for field_name in sorted(set(value) - _REQUEST_FIELDS):
        _add_issue(
            issues,
            f"$.{field_name}",
            "request_field_unknown",
            f"Unbekanntes Anfragefeld: {field_name}",
        )

    translation = translate_strategy_assignment_draft(value.get("draft"))
    for issue in translation.issues:
        suffix = issue.path[1:] if issue.path.startswith("$") else f".{issue.path}"
        _add_issue(issues, f"$.draft{suffix}", f"draft_{issue.code}", issue.message)

    expected_entries = {
        (entry.assignment.actor_type, entry.assignment.target_id): entry
        for entry in translation.entries
    }
    expected_value_count = sum(
        len(entry.target.unresolved_snapshot_fields)
        for entry in translation.entries
    )
    context = value.get("context")
    if not isinstance(context, dict):
        _add_issue(
            issues,
            "$.context",
            "context_object_required",
            "Snapshot-Kontext muss ein Objekt sein",
        )
        return _context_report(
            valid=False,
            draft_valid=translation.draft_valid,
            translation_complete=translation.translation_complete,
            submitted_schema_version=None,
            draft_id=translation.draft_id,
            period=None,
            expected_entry_count=len(expected_entries),
            validated_entry_count=0,
            expected_value_count=expected_value_count,
            validated_value_count=0,
            resolved_value_count=0,
            explicitly_open_value_count=0,
            issues=issues,
        )

    submitted_schema_version = (
        context.get("schema_version")
        if isinstance(context.get("schema_version"), str)
        else None
    )
    for field_name in sorted(_DOCUMENT_FIELDS - set(context)):
        _add_issue(
            issues,
            f"$.context.{field_name}",
            "context_field_missing",
            f"Pflichtfeld des Kontexts fehlt: {field_name}",
        )
    for field_name in sorted(set(context) - _DOCUMENT_FIELDS):
        _add_issue(
            issues,
            f"$.context.{field_name}",
            "context_field_unknown",
            f"Unbekanntes Kontextfeld: {field_name}",
        )

    exact_values = {
        "schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VERSION,
        "translation_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
        "base_model": "Vdefmd6",
        "scope": "explicit_single_period_snapshot_context",
    }
    for field_name, expected in exact_values.items():
        if context.get(field_name) != expected:
            _add_issue(
                issues,
                f"$.context.{field_name}",
                "contract_value_mismatch",
                f"{field_name} muss {expected!r} sein",
            )

    draft_id = context.get("draft_id")
    if not isinstance(draft_id, str) or not draft_id.strip():
        _add_issue(
            issues,
            "$.context.draft_id",
            "nonempty_string_required",
            "draft_id muss eine nichtleere Zeichenkette sein",
        )
        draft_id = None
    elif translation.draft_id is not None and draft_id != translation.draft_id:
        _add_issue(
            issues,
            "$.context.draft_id",
            "draft_id_mismatch",
            "Snapshot-Kontext gehoert nicht zum validierten Entwurf",
        )

    period = context.get("period")
    if not isinstance(period, int) or isinstance(period, bool) or period < 1:
        _add_issue(
            issues,
            "$.context.period",
            "positive_integer_required",
            "period muss eine positive Ganzzahl sein",
        )
        period = None

    raw_entries = context.get("entries")
    validated_entry_count = 0
    validated_value_count = 0
    resolved_value_count = 0
    explicitly_open_value_count = 0
    seen_targets: set[tuple[StrategyActorType, int]] = set()
    if not isinstance(raw_entries, list):
        _add_issue(
            issues,
            "$.context.entries",
            "context_entries_list_required",
            "entries muss eine Liste sein",
        )
        raw_entries = []

    for index, raw_entry in enumerate(raw_entries):
        path = f"$.context.entries[{index}]"
        issue_start = len(issues)
        if not isinstance(raw_entry, dict):
            _add_issue(
                issues,
                path,
                "context_entry_object_required",
                "Kontexteintrag muss ein Objekt sein",
            )
            continue
        for field_name in sorted(_ENTRY_FIELDS - set(raw_entry)):
            _add_issue(
                issues,
                f"{path}.{field_name}",
                "context_entry_field_missing",
                f"Pflichtfeld des Kontexteintrags fehlt: {field_name}",
            )
        for field_name in sorted(set(raw_entry) - _ENTRY_FIELDS):
            _add_issue(
                issues,
                f"{path}.{field_name}",
                "context_entry_field_unknown",
                f"Unbekanntes Kontexteintragsfeld: {field_name}",
            )

        actor_type: StrategyActorType | None = None
        try:
            actor_type = StrategyActorType(raw_entry.get("actor_type"))
        except (TypeError, ValueError):
            _add_issue(
                issues,
                f"{path}.actor_type",
                "actor_type_unknown",
                "actor_type muss insurer oder policyholder sein",
            )
        target_id = raw_entry.get("target_id")
        if not isinstance(target_id, int) or isinstance(target_id, bool) or target_id < 1:
            _add_issue(
                issues,
                f"{path}.target_id",
                "positive_integer_required",
                "target_id muss eine positive Ganzzahl sein",
            )
            target_id = None
        strategy_id = raw_entry.get("strategy_id")
        if not isinstance(strategy_id, str) or not strategy_id.strip():
            _add_issue(
                issues,
                f"{path}.strategy_id",
                "nonempty_string_required",
                "strategy_id muss eine nichtleere Zeichenkette sein",
            )
            strategy_id = None

        expected_entry = None
        target_key = None
        if actor_type is not None and target_id is not None:
            target_key = (actor_type, target_id)
            if target_key in seen_targets:
                _add_issue(
                    issues,
                    f"{path}.target_id",
                    "duplicate_context_entry",
                    "Akteur besitzt bereits einen Kontexteintrag",
                )
            seen_targets.add(target_key)
            expected_entry = expected_entries.get(target_key)
            if translation.translation_complete and expected_entry is None:
                _add_issue(
                    issues,
                    f"{path}.target_id",
                    "context_target_not_in_draft",
                    "Akteur ist im validierten Entwurf nicht enthalten",
                )
        if expected_entry is not None and strategy_id != expected_entry.assignment.strategy_id:
            _add_issue(
                issues,
                f"{path}.strategy_id",
                "strategy_id_mismatch",
                "Kontextstrategie stimmt nicht mit dem validierten Entwurf ueberein",
            )

        values = raw_entry.get("values")
        if not isinstance(values, dict):
            _add_issue(
                issues,
                f"{path}.values",
                "context_values_object_required",
                "values muss ein Objekt sein",
            )
        elif expected_entry is not None:
            expected_fields = set(expected_entry.target.unresolved_snapshot_fields)
            for field_name in sorted(expected_fields - set(values)):
                _add_issue(
                    issues,
                    f"{path}.values.{field_name}",
                    "context_value_missing",
                    f"Offenes Snapshotfeld fehlt: {field_name}",
                )
            for field_name in sorted(set(values) - expected_fields):
                _add_issue(
                    issues,
                    f"{path}.values.{field_name}",
                    "context_value_unknown",
                    f"Feld ist fuer diesen Snapshot-Bauplan nicht offen: {field_name}",
                )
            for field_name in sorted(expected_fields & set(values)):
                field_value = values[field_name]
                definition = _FIELD_BY_NAME[field_name]
                if not _value_matches_definition(field_value, definition):
                    _add_issue(
                        issues,
                        f"{path}.values.{field_name}",
                        "context_value_shape_invalid",
                        (
                            f"{field_name} entspricht nicht der Vertragsform "
                            f"{definition.value_shape}"
                        ),
                    )
                    continue
                validated_value_count += 1
                if field_value is None:
                    explicitly_open_value_count += 1
                else:
                    resolved_value_count += 1
        if expected_entry is not None and len(issues) == issue_start:
            validated_entry_count += 1

    if translation.translation_complete:
        for actor_type, target_id in sorted(
            set(expected_entries) - seen_targets,
            key=lambda item: (item[0].value, item[1]),
        ):
            _add_issue(
                issues,
                "$.context.entries",
                "context_entry_missing",
                f"Kontexteintrag fehlt fuer {actor_type.value} {target_id}",
            )

    valid = (
        translation.translation_complete
        and not issues
        and validated_entry_count == len(expected_entries)
        and validated_value_count == expected_value_count
    )
    return _context_report(
        valid=valid,
        draft_valid=translation.draft_valid,
        translation_complete=translation.translation_complete,
        submitted_schema_version=submitted_schema_version,
        draft_id=draft_id,
        period=period,
        expected_entry_count=len(expected_entries),
        validated_entry_count=validated_entry_count,
        expected_value_count=expected_value_count,
        validated_value_count=validated_value_count,
        resolved_value_count=resolved_value_count,
        explicitly_open_value_count=explicitly_open_value_count,
        issues=issues,
    )


def strategy_assignment_snapshot_context_contract_payload() -> dict[str, Any]:
    """Beschreibt den expliziten Einperiodenkontext und geschlossene Grenzen."""

    return {
        "schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VERSION,
        "validation_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION,
        "draft_schema_version": STRATEGY_ASSIGNMENT_DRAFT_VERSION,
        "translation_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
        "mode": "strategy_assignment_snapshot_context_contract_read_only",
        "base_model": "Vdefmd6",
        "scope": "explicit_single_period_snapshot_context",
        "validation_endpoint": "/api/strategies/assignment-snapshot-context-validation",
        "validation_request_fields": tuple(sorted(_REQUEST_FIELDS)),
        "document_fields": tuple(sorted(_DOCUMENT_FIELDS)),
        "entry_fields": tuple(sorted(_ENTRY_FIELDS)),
        "field_definitions": [
            definition.to_dict()
            for definition in STRATEGY_SNAPSHOT_CONTEXT_FIELDS
        ],
        "source_categories": tuple(source.value for source in StrategySnapshotContextSource),
        "contract_issue_count": len(strategy_snapshot_context_contract_issues()),
        "exact_draft_entry_match_required": True,
        "exact_open_field_match_required": True,
        "explicit_null_keeps_value_open": True,
        "rule_specific_nested_semantics_validated": False,
        "unknown_fields_allowed": False,
        "defaults_applied": False,
        "context_values_consumed": False,
        "snapshot_loader_invocation_enabled": False,
        "persistence_enabled": False,
        "snapshot_materialization_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_full_equality_claim": False,
    }
