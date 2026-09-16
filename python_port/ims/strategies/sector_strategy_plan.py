"""Validation-only strategy plans for named IMS 2.x non-life sectors."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite

from ims.model.sector_taxonomy import (
    SECTOR_DEFINITIONS,
    SECTOR_TAXONOMY_VERSION,
    SectorModelFamily,
)
from ims.model.vdefmd6_population import (
    VDEFMD6_INSURER_COUNT,
    VDEFMD6_POLICYHOLDER_COUNT,
)
from ims.strategies.assignment_contract import STRATEGY_PARAMETER_SCHEMAS
from ims.strategies.catalog import (
    STRATEGY_CATALOG_VERSION,
    STRATEGY_DEFINITIONS,
    StrategyActorType,
)


SECTOR_STRATEGY_PLAN_VERSION = "ims.sector-strategy-plan.v1"
SECTOR_STRATEGY_PLAN_VALIDATION_VERSION = "ims.sector-strategy-plan-validation.v1"
_PERIOD_LIMIT = 100
_ASSIGNMENT_LIMIT = 1000
_DOCUMENT_FIELDS = frozenset(
    {
        "schema_version", "sector_taxonomy_schema_version", "catalog_schema_version",
        "actor_population", "scope", "historical_mapping_status", "plan_id",
        "label", "assignments",
    }
)
_ASSIGNMENT_FIELDS = frozenset(
    {
        "actor_type", "target_id", "sector_id", "strategy_id", "period_from",
        "period_through", "parameter_schema", "parameter_values",
    }
)
_TARGET_LIMITS = {
    StrategyActorType.INSURER: VDEFMD6_INSURER_COUNT,
    StrategyActorType.POLICYHOLDER: VDEFMD6_POLICYHOLDER_COUNT,
}
_SECTORS_BY_ID = {sector.sector_id: sector for sector in SECTOR_DEFINITIONS}
_STRATEGIES_BY_ID = {strategy.strategy_id: strategy for strategy in STRATEGY_DEFINITIONS}
_SCHEMAS_BY_ID = {schema.schema_id: schema for schema in STRATEGY_PARAMETER_SCHEMAS}


@dataclass(frozen=True, slots=True)
class SectorStrategyPlanIssue:
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class SectorStrategyPlanValidationReport:
    valid: bool
    submitted_schema_version: str | None
    assignment_count: int
    accepted_assignment_count: int
    issues: tuple[SectorStrategyPlanIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SECTOR_STRATEGY_PLAN_VALIDATION_VERSION,
            "mode": "sector_strategy_plan_validation",
            "status": "ok" if self.valid else "error",
            "valid": self.valid,
            "submitted_schema_version": self.submitted_schema_version,
            "assignment_count": self.assignment_count,
            "accepted_assignment_count": self.accepted_assignment_count,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "historical_mapping_status": "unresolved",
            "writes_performed": False,
            "snapshots_created": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_full_equality_claim": False,
        }


def _issue(issues: list[SectorStrategyPlanIssue], path: str, code: str, message: str) -> None:
    issues.append(SectorStrategyPlanIssue(path, code, message))


def _exact_fields(
    value: dict, expected: frozenset[str], path: str, issues: list[SectorStrategyPlanIssue]
) -> None:
    actual = {key for key in value if type(key) is str}
    for key in sorted(expected - actual):
        _issue(issues, f"{path}.{key}", "field_missing", f"Pflichtfeld fehlt: {key}")
    for key in sorted(actual - expected):
        _issue(issues, f"{path}.{key}", "field_unknown", f"Unbekanntes Feld: {key}")
    if len(actual) != len(value):
        _issue(issues, path, "field_name_invalid", "Feldnamen muessen Text sein")


def _exact_value(
    value: dict, key: str, expected: str, issues: list[SectorStrategyPlanIssue]
) -> None:
    if value.get(key) != expected:
        _issue(issues, f"$.{key}", "contract_value_mismatch", f"{key} muss {expected!r} sein")


def _positive_bounded_int(
    value: object, maximum: int, path: str, issues: list[SectorStrategyPlanIssue]
) -> int | None:
    if type(value) is not int or not 1 <= value <= maximum:
        _issue(issues, path, "integer_out_of_range", f"Ganzzahl von 1 bis {maximum} erforderlich")
        return None
    return value


def _parameter_values_valid(
    values: object,
    schema_id: str | None,
    path: str,
    issues: list[SectorStrategyPlanIssue],
) -> bool:
    if schema_id is None:
        if values is not None:
            _issue(issues, path, "parameters_not_supported", "Strategie hat keine Parameter")
            return False
        return True
    if not isinstance(values, dict):
        _issue(issues, path, "parameters_object_required", "Parameterobjekt erforderlich")
        return False

    schema = _SCHEMAS_BY_ID[schema_id]
    expected = frozenset(field.field_name for field in schema.fields)
    _exact_fields(values, expected, path, issues)
    valid = set(values) == expected
    for field in schema.fields:
        if field.field_name not in values:
            continue
        item = values[field.field_name]
        item_path = f"{path}.{field.field_name}"
        if field.python_type == "list[int]":
            if type(item) is not int or item < 0:
                _issue(
                    issues, item_path, "non_negative_integer_required",
                    "Nichtnegative Ganzzahl erforderlich",
                )
                valid = False
        elif type(item) not in (int, float) or (type(item) is float and not isfinite(item)):
            _issue(issues, item_path, "finite_number_required", "Endliche Zahl erforderlich")
            valid = False
    return valid


def _validate_assignment(
    value: object,
    index: int,
    issues: list[SectorStrategyPlanIssue],
) -> tuple[StrategyActorType, int, str, int, int] | None:
    path = f"$.assignments[{index}]"
    start_issues = len(issues)
    if not isinstance(value, dict):
        _issue(issues, path, "assignment_object_required", "Zuordnung muss ein Objekt sein")
        return None
    _exact_fields(value, _ASSIGNMENT_FIELDS, path, issues)

    try:
        actor_type = StrategyActorType(value.get("actor_type"))
    except (TypeError, ValueError):
        actor_type = None
        _issue(issues, f"{path}.actor_type", "actor_type_unknown", "insurer oder policyholder erforderlich")
    target_id = None
    if actor_type is not None:
        target_id = _positive_bounded_int(
            value.get("target_id"), _TARGET_LIMITS[actor_type], f"{path}.target_id", issues
        )

    sector_id = value.get("sector_id")
    sector = _SECTORS_BY_ID.get(sector_id) if type(sector_id) is str else None
    if sector is None:
        _issue(issues, f"{path}.sector_id", "sector_unknown", "Unbekannte Zielsparten-ID")
    elif sector.model_family is not SectorModelFamily.NON_LIFE:
        _issue(
            issues, f"{path}.sector_id", "sector_strategy_not_available",
            "Fuer Leben/Kranken fehlt ein eigener Strategievertrag",
        )

    strategy_id = value.get("strategy_id")
    strategy = _STRATEGIES_BY_ID.get(strategy_id) if type(strategy_id) is str else None
    if strategy is None:
        _issue(issues, f"{path}.strategy_id", "strategy_unknown", "Unbekannte Katalogstrategie")
    elif actor_type is not None and strategy.actor_type is not actor_type:
        _issue(issues, f"{path}.strategy_id", "strategy_actor_mismatch", "Strategie passt nicht zum Akteur")

    period_from = _positive_bounded_int(
        value.get("period_from"), _PERIOD_LIMIT, f"{path}.period_from", issues
    )
    period_through = _positive_bounded_int(
        value.get("period_through"), _PERIOD_LIMIT, f"{path}.period_through", issues
    )
    if period_from is not None and period_through is not None and period_from > period_through:
        _issue(issues, f"{path}.period_through", "period_window_invalid", "Ende liegt vor Beginn")

    if strategy is not None:
        if value.get("parameter_schema") != strategy.parameter_schema:
            _issue(
                issues, f"{path}.parameter_schema", "parameter_schema_mismatch",
                "Parameterschema passt nicht zur Strategie",
            )
        _parameter_values_valid(
            value.get("parameter_values"),
            strategy.parameter_schema,
            f"{path}.parameter_values",
            issues,
        )

    if len(issues) != start_issues:
        return None
    assert actor_type is not None and target_id is not None
    assert type(sector_id) is str and period_from is not None and period_through is not None
    return actor_type, target_id, sector_id, period_from, period_through


def validate_sector_strategy_plan(value: object) -> SectorStrategyPlanValidationReport:
    """Validate a partial plan atomically, without snapshots, storage or execution."""

    issues: list[SectorStrategyPlanIssue] = []
    if not isinstance(value, dict):
        _issue(issues, "$", "plan_object_required", "Strategieplan muss ein Objekt sein")
        return SectorStrategyPlanValidationReport(False, None, 0, 0, tuple(issues))

    submitted_version = value.get("schema_version")
    submitted_version = submitted_version if type(submitted_version) is str else None
    _exact_fields(value, _DOCUMENT_FIELDS, "$", issues)
    for key, expected in (
        ("schema_version", SECTOR_STRATEGY_PLAN_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("catalog_schema_version", STRATEGY_CATALOG_VERSION),
        ("actor_population", "Vdefmd6"),
        ("scope", "planned_non_life_sector_assignments"),
        ("historical_mapping_status", "unresolved"),
    ):
        _exact_value(value, key, expected, issues)
    for key in ("plan_id", "label"):
        item = value.get(key)
        if type(item) is not str or not item.strip():
            _issue(issues, f"$.{key}", "nonempty_string_required", "Nichtleerer Text erforderlich")

    assignments = value.get("assignments")
    assignment_count = len(assignments) if isinstance(assignments, list) else 0
    if not isinstance(assignments, list) or not 1 <= len(assignments) <= _ASSIGNMENT_LIMIT:
        _issue(issues, "$.assignments", "assignment_count_invalid", "1 bis 1000 Zuordnungen erforderlich")
    else:
        windows: dict[tuple[StrategyActorType, int, str], list[tuple[int, int, int]]] = {}
        for index, item in enumerate(assignments):
            parsed = _validate_assignment(item, index, issues)
            if parsed is None:
                continue
            actor_type, target_id, sector_id, period_from, period_through = parsed
            windows.setdefault((actor_type, target_id, sector_id), []).append(
                (period_from, period_through, index)
            )
        for entries in windows.values():
            entries.sort()
            previous_through = 0
            for period_from, period_through, index in entries:
                if period_from <= previous_through:
                    _issue(
                        issues,
                        f"$.assignments[{index}].period_from",
                        "period_window_overlap",
                        "Zeitfenster desselben Akteurs und derselben Sparte ueberlappen",
                    )
                previous_through = max(previous_through, period_through)

    valid = not issues
    return SectorStrategyPlanValidationReport(
        valid, submitted_version, assignment_count,
        assignment_count if valid else 0, tuple(issues),
    )


def sector_strategy_plan_contract_payload() -> dict[str, object]:
    """Describe the validation-only format and its unsupported execution boundary."""

    return {
        "schema_version": SECTOR_STRATEGY_PLAN_VERSION,
        "validation_schema_version": SECTOR_STRATEGY_PLAN_VALIDATION_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "catalog_schema_version": STRATEGY_CATALOG_VERSION,
        "mode": "sector_strategy_plan_contract_read_only",
        "actor_population": "Vdefmd6",
        "scope": "planned_non_life_sector_assignments",
        "historical_mapping_status": "unresolved",
        "validation_endpoint": "/api/strategies/sector-plan-validation",
        "document_fields": sorted(_DOCUMENT_FIELDS),
        "assignment_fields": sorted(_ASSIGNMENT_FIELDS),
        "eligible_sector_ids": [
            sector.sector_id for sector in SECTOR_DEFINITIONS
            if sector.model_family is SectorModelFamily.NON_LIFE
        ],
        "pending_sector_ids": [
            sector.sector_id for sector in SECTOR_DEFINITIONS
            if sector.model_family is not SectorModelFamily.NON_LIFE
        ],
        "target_limits": {actor_type: maximum for actor_type, maximum in _TARGET_LIMITS.items()},
        "period_limit": _PERIOD_LIMIT,
        "parameter_value_shape": "scalar_per_named_sector",
        "strategy_ids_by_actor": {
            actor_type: [
                strategy.strategy_id for strategy in STRATEGY_DEFINITIONS
                if strategy.actor_type is actor_type
            ]
            for actor_type in StrategyActorType
        },
        "partial_assignments_allowed": True,
        "overlapping_windows_allowed": False,
        "unknown_fields_allowed": False,
        "legacy_sector_binding_enabled": False,
        "snapshot_materialization_enabled": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_full_equality_claim": False,
    }


def sector_strategy_plan_invalid_json_payload() -> dict[str, object]:
    return SectorStrategyPlanValidationReport(
        False,
        None,
        0,
        0,
        (SectorStrategyPlanIssue("$", "invalid_json", "Strategieplan ist kein gueltiges JSON"),),
    ).to_dict()
