from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
import importlib
from typing import Any

from ims.strategies.assignment_contract import (
    STRATEGY_ASSIGNMENT_CONTRACT_VERSION,
    STRATEGY_PARAMETER_SCHEMAS,
)
from ims.strategies.assignment_draft import (
    STRATEGY_ASSIGNMENT_DRAFT_VALIDATION_VERSION,
    STRATEGY_ASSIGNMENT_DRAFT_VERSION,
    StrategyAssignmentDraftEntry,
    StrategyAssignmentDraftIssue,
    load_strategy_assignment_draft,
    validate_strategy_assignment_draft,
)
from ims.strategies.catalog import (
    STRATEGY_CATALOG_VERSION,
    STRATEGY_DEFINITIONS,
    StrategyActorType,
)


STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION = (
    "ims.strategy-assignment-snapshot-translation.v1"
)


@dataclass(frozen=True, slots=True)
class StrategySnapshotTargetDefinition:
    """Explizite Abbildung einer Katalogstrategie auf einen Snapshottyp."""

    strategy_id: str
    actor_type: StrategyActorType
    snapshot_module: str
    snapshot_type: str
    snapshot_loader: str
    snapshot_collection: str
    target_id_field: str
    rule_kind: str | None
    provided_snapshot_fields: tuple[str, ...]
    unresolved_snapshot_fields: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _snapshot_target(
    strategy_id: str,
    actor_type: StrategyActorType,
    snapshot_type: str,
    snapshot_loader: str,
    snapshot_collection: str,
    target_id_field: str,
    *,
    rule_kind: str | None = None,
    snapshot_module: str,
) -> StrategySnapshotTargetDefinition:
    provided_fields = [target_id_field]
    if rule_kind is not None:
        provided_fields.append("rule_kind")
    provided_fields.append("parameters")

    module = importlib.import_module(snapshot_module)
    snapshot_class = getattr(module, snapshot_type)
    unresolved_fields = tuple(
        field.name for field in fields(snapshot_class) if field.name not in provided_fields
    )
    return StrategySnapshotTargetDefinition(
        strategy_id=strategy_id,
        actor_type=actor_type,
        snapshot_module=snapshot_module,
        snapshot_type=snapshot_type,
        snapshot_loader=snapshot_loader,
        snapshot_collection=snapshot_collection,
        target_id_field=target_id_field,
        rule_kind=rule_kind,
        provided_snapshot_fields=tuple(provided_fields),
        unresolved_snapshot_fields=unresolved_fields,
    )


_VU_MODULE = "ims.model.vu_rules"
_VN_MODULE = "ims.model.vn_insurance_rules"
_INSURER = StrategyActorType.INSURER
_POLICYHOLDER = StrategyActorType.POLICYHOLDER


STRATEGY_SNAPSHOT_TARGETS = (
    _snapshot_target(
        "vu.vrvu01",
        _INSURER,
        "VURandomUniformRuleSnapshot",
        "vu_random_uniform_rule_snapshot_from_mapping",
        "vu_random_uniform_rule_snapshots",
        "insurer_id",
        snapshot_module=_VU_MODULE,
    ),
    _snapshot_target(
        "vu.vrvu02",
        _INSURER,
        "VURandomNormalRuleSnapshot",
        "vu_random_normal_rule_snapshot_from_mapping",
        "vu_random_normal_rule_snapshots",
        "insurer_id",
        snapshot_module=_VU_MODULE,
    ),
    _snapshot_target(
        "vu.vrvu03",
        _INSURER,
        "VUReserveMarkupRuleSnapshot",
        "vu_reserve_markup_rule_snapshot_from_mapping",
        "vu_reserve_markup_rule_snapshots",
        "insurer_id",
        snapshot_module=_VU_MODULE,
    ),
    _snapshot_target(
        "vu.vrvu04",
        _INSURER,
        "VUNetSwitcherMarkupRuleSnapshot",
        "vu_net_switcher_markup_rule_snapshot_from_mapping",
        "vu_net_switcher_markup_rule_snapshots",
        "insurer_id",
        snapshot_module=_VU_MODULE,
    ),
    _snapshot_target(
        "vu.vrvu05",
        _INSURER,
        "VUMarketShareMarkupRuleSnapshot",
        "vu_market_share_markup_rule_snapshot_from_mapping",
        "vu_market_share_markup_rule_snapshots",
        "insurer_id",
        snapshot_module=_VU_MODULE,
    ),
    _snapshot_target(
        "vu.vrvu06",
        _INSURER,
        "VUExpectedClaimRuleSnapshot",
        "vu_expected_claim_rule_snapshot_from_mapping",
        "vu_expected_claim_rule_snapshots",
        "insurer_id",
        snapshot_module=_VU_MODULE,
    ),
    _snapshot_target(
        "vu.vrvu07",
        _INSURER,
        "VUForeignInfoRuleSnapshot",
        "vu_foreign_info_rule_snapshot_from_mapping",
        "vu_foreign_info_rule_snapshots",
        "insurer_id",
        rule_kind="dumping",
        snapshot_module=_VU_MODULE,
    ),
    _snapshot_target(
        "vu.vrvu08",
        _INSURER,
        "VUForeignInfoRuleSnapshot",
        "vu_foreign_info_rule_snapshot_from_mapping",
        "vu_foreign_info_rule_snapshots",
        "insurer_id",
        rule_kind="average",
        snapshot_module=_VU_MODULE,
    ),
    _snapshot_target(
        "vu.vrvu09",
        _INSURER,
        "VUForeignInfoRuleSnapshot",
        "vu_foreign_info_rule_snapshot_from_mapping",
        "vu_foreign_info_rule_snapshots",
        "insurer_id",
        rule_kind="attack",
        snapshot_module=_VU_MODULE,
    ),
    _snapshot_target(
        "vu.vrvu10",
        _INSURER,
        "VUFreeLinearRuleSnapshot",
        "vu_free_linear_rule_snapshot_from_mapping",
        "vu_free_linear_rule_snapshots",
        "insurer_id",
        snapshot_module=_VU_MODULE,
    ),
    *(
        _snapshot_target(
            strategy_id,
            _POLICYHOLDER,
            "VNInsuranceRuleSnapshot",
            "vn_insurance_rule_snapshot_from_mapping",
            "vn_insurance_rule_snapshots",
            "policyholder_id",
            rule_kind=rule_kind,
            snapshot_module=_VN_MODULE,
        )
        for strategy_id, rule_kind in (
            ("vn.vrvn01", "compulsory"),
            ("vn.vrvn02", "random"),
            ("vn.vrvn03", "preference"),
            ("vn.vrvn04", "search_history"),
            ("vn.vrvn05", "sample_search"),
            ("vn.vrvn06", "best_info"),
        )
    ),
)

_TARGETS_BY_STRATEGY_ID = {
    target.strategy_id: target for target in STRATEGY_SNAPSHOT_TARGETS
}
_SCHEMAS_BY_ID = {schema.schema_id: schema for schema in STRATEGY_PARAMETER_SCHEMAS}


@dataclass(frozen=True, slots=True)
class StrategyAssignmentSnapshotTranslationEntry:
    """Typisierter, noch nicht materialisierter Snapshot-Bauplan."""

    assignment: StrategyAssignmentDraftEntry
    target: StrategySnapshotTargetDefinition
    parameters: object | None

    def snapshot_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            self.target.target_id_field: self.assignment.target_id,
        }
        if self.target.rule_kind is not None:
            payload["rule_kind"] = self.target.rule_kind
        payload["parameters"] = (
            None if self.parameters is None else asdict(self.parameters)
        )
        return payload

    def to_dict(self) -> dict[str, object]:
        return {
            **self.assignment.to_dict(),
            "snapshot_module": self.target.snapshot_module,
            "snapshot_type": self.target.snapshot_type,
            "snapshot_loader": self.target.snapshot_loader,
            "snapshot_collection": self.target.snapshot_collection,
            "snapshot_payload": self.snapshot_payload(),
            "provided_snapshot_fields": self.target.provided_snapshot_fields,
            "unresolved_snapshot_fields": self.target.unresolved_snapshot_fields,
            "snapshot_materialized": False,
            "execution_ready": False,
        }


@dataclass(frozen=True, slots=True)
class StrategyAssignmentSnapshotTranslationReport:
    """Ergebnis der reinen Entwurf-zu-Snapshot-Bauplan-Uebersetzung."""

    draft_valid: bool
    draft_id: str | None
    label: str | None
    assignment_count: int
    entries: tuple[StrategyAssignmentSnapshotTranslationEntry, ...]
    issues: tuple[StrategyAssignmentDraftIssue, ...]
    schema_version: str = STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION
    mode: str = "strategy_assignment_snapshot_translation"
    writes_performed: bool = False
    snapshots_created: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False
    historical_full_equality_claim: bool = False

    @property
    def translation_complete(self) -> bool:
        return self.draft_valid and len(self.entries) == self.assignment_count

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "status": "ok" if self.translation_complete else "error",
            "draft_valid": self.draft_valid,
            "translation_complete": self.translation_complete,
            "draft_id": self.draft_id,
            "label": self.label,
            "assignment_count": self.assignment_count,
            "translated_assignment_count": len(self.entries),
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "entries": [entry.to_dict() for entry in self.entries],
            "defaults_applied": False,
            "snapshot_materialization_ready": False,
            "writes_performed": self.writes_performed,
            "snapshots_created": self.snapshots_created,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "historical_full_equality_claim": self.historical_full_equality_claim,
        }


def strategy_snapshot_translation_issues(
    targets: tuple[StrategySnapshotTargetDefinition, ...] = STRATEGY_SNAPSHOT_TARGETS,
) -> tuple[str, ...]:
    """Prueft die vollstaendige Bindung an vorhandene Snapshot-Dataclasses."""

    issues: list[str] = []
    targets_by_id = {target.strategy_id: target for target in targets}
    if len(targets_by_id) != len(targets):
        issues.append("Doppelte Strategie im Snapshot-Uebersetzungsvertrag")
    if set(targets_by_id) != {
        strategy.strategy_id for strategy in STRATEGY_DEFINITIONS
    }:
        issues.append("Snapshot-Uebersetzung deckt den Strategiekatalog nicht exakt ab")

    for strategy in STRATEGY_DEFINITIONS:
        target = targets_by_id.get(strategy.strategy_id)
        if target is None:
            continue
        if target.actor_type is not strategy.actor_type:
            issues.append(f"Akteurstyp weicht ab: {strategy.strategy_id}")
        module = importlib.import_module(target.snapshot_module)
        snapshot_class = getattr(module, target.snapshot_type, None)
        if not isinstance(snapshot_class, type) or not is_dataclass(snapshot_class):
            issues.append(f"Snapshottyp ist keine Dataclass: {strategy.strategy_id}")
            continue
        if not callable(getattr(module, target.snapshot_loader, None)):
            issues.append(f"Snapshotloader fehlt: {strategy.strategy_id}")
        field_names = tuple(field.name for field in fields(snapshot_class))
        mapped_fields = target.provided_snapshot_fields + target.unresolved_snapshot_fields
        if len(set(mapped_fields)) != len(mapped_fields) or set(mapped_fields) != set(field_names):
            issues.append(f"Snapshotfelder sind nicht exakt abgedeckt: {strategy.strategy_id}")
    return tuple(issues)


def _load_assignment_parameters(assignment: StrategyAssignmentDraftEntry) -> object | None:
    if assignment.parameter_schema is None:
        return None
    schema = _SCHEMAS_BY_ID[assignment.parameter_schema]
    module = importlib.import_module(schema.module)
    loader = getattr(module, schema.loader_entrypoint)
    assert assignment.parameter_values is not None
    return loader(
        {key: list(values) for key, values in assignment.parameter_values.items()}
    )


def translate_strategy_assignment_draft(
    value: object,
) -> StrategyAssignmentSnapshotTranslationReport:
    """Uebersetzt einen gueltigen Entwurf ohne Defaults, I/O oder Ausfuehrung."""

    validation = validate_strategy_assignment_draft(value)
    if not validation.valid:
        return StrategyAssignmentSnapshotTranslationReport(
            draft_valid=False,
            draft_id=None,
            label=None,
            assignment_count=validation.assignment_count,
            entries=(),
            issues=validation.issues,
        )

    draft = load_strategy_assignment_draft(value)
    entries = tuple(
        StrategyAssignmentSnapshotTranslationEntry(
            assignment=assignment,
            target=_TARGETS_BY_STRATEGY_ID[assignment.strategy_id],
            parameters=_load_assignment_parameters(assignment),
        )
        for assignment in draft.assignments
    )
    return StrategyAssignmentSnapshotTranslationReport(
        draft_valid=True,
        draft_id=draft.draft_id,
        label=draft.label,
        assignment_count=len(draft.assignments),
        entries=entries,
        issues=(),
    )


def strategy_assignment_snapshot_translation_contract_payload() -> dict[str, Any]:
    """Beschreibt Mapping, Ausgabeform und weiterhin geschlossene Grenzen."""

    return {
        "schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
        "draft_schema_version": STRATEGY_ASSIGNMENT_DRAFT_VERSION,
        "draft_validation_schema_version": STRATEGY_ASSIGNMENT_DRAFT_VALIDATION_VERSION,
        "catalog_schema_version": STRATEGY_CATALOG_VERSION,
        "assignment_contract_schema_version": STRATEGY_ASSIGNMENT_CONTRACT_VERSION,
        "mode": "strategy_assignment_snapshot_translation_contract_read_only",
        "scope": "validated_draft_to_existing_snapshot_construction_plan",
        "translation_endpoint": "/api/strategies/assignment-snapshot-translation",
        "strategy_mappings": [target.to_dict() for target in STRATEGY_SNAPSHOT_TARGETS],
        "mapping_issue_count": len(strategy_snapshot_translation_issues()),
        "partial_snapshot_payloads": True,
        "typed_parameter_loading_enabled": True,
        "snapshot_loader_invocation_enabled": False,
        "defaults_applied": False,
        "persistence_enabled": False,
        "snapshot_materialization_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_full_equality_claim": False,
    }
