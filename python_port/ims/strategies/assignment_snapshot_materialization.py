from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib
from typing import Any

from ims.model.vn_insurance_rules import VNInsuranceRuleSnapshot
from ims.strategies.assignment_snapshot_materialization_contract import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION,
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION,
    STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS,
    VN_SNAPSHOT_MATERIALIZATION_RULES,
    VNSnapshotMaterializationRuleDefinition,
)
from ims.strategies.assignment_snapshot_materialization_validation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION,
    validate_strategy_assignment_snapshot_materialization_input,
)
from ims.strategies.assignment_snapshot_translation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
    StrategyAssignmentSnapshotTranslationEntry,
    translate_strategy_assignment_draft,
)
from ims.strategies.catalog import StrategyActorType


_NESTED_BY_ID = {
    definition.schema_id: definition
    for definition in STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS
}
_RULE_BY_STRATEGY_ID = {
    definition.strategy_id: definition
    for definition in VN_SNAPSHOT_MATERIALIZATION_RULES
}


@dataclass(frozen=True, slots=True)
class StrategyAssignmentSnapshotMaterializationIssue:
    stage: str
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class StrategyAssignmentMaterializedSnapshot:
    strategy_id: str
    snapshot_collection: str
    snapshot_type: str
    snapshot: VNInsuranceRuleSnapshot

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self.snapshot)
        payload["rule_kind"] = self.snapshot.rule_kind.value
        return {
            "strategy_id": self.strategy_id,
            "snapshot_collection": self.snapshot_collection,
            "snapshot_type": self.snapshot_type,
            "snapshot": payload,
        }


@dataclass(frozen=True, slots=True)
class StrategyAssignmentSnapshotMaterializationReport:
    input_valid: bool
    draft_id: str | None
    period: int | None
    expected_snapshot_count: int
    snapshot_loader_invocation_count: int
    nested_loader_invocation_count: int
    snapshots: tuple[StrategyAssignmentMaterializedSnapshot, ...]
    issues: tuple[StrategyAssignmentSnapshotMaterializationIssue, ...]
    schema_version: str = STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION
    mode: str = "strategy_assignment_snapshot_materialization"

    @property
    def materialization_complete(self) -> bool:
        return (
            self.input_valid
            and not self.issues
            and len(self.snapshots) == self.expected_snapshot_count
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "status": "ok" if self.materialization_complete else "error",
            "input_valid": self.input_valid,
            "materialization_complete": self.materialization_complete,
            "draft_id": self.draft_id,
            "period": self.period,
            "expected_snapshot_count": self.expected_snapshot_count,
            "snapshot_count": len(self.snapshots),
            "snapshot_loader_invocation_count": (
                self.snapshot_loader_invocation_count
            ),
            "nested_loader_invocation_count": self.nested_loader_invocation_count,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "snapshots": [entry.to_dict() for entry in self.snapshots],
            "context_values_consumed": self.input_valid,
            "nested_loader_results_retained": self.materialization_complete,
            "snapshot_loader_invocation_performed": (
                self.snapshot_loader_invocation_count > 0
            ),
            "partial_results_returned": False,
            "writes_performed": False,
            "persistence_performed": False,
            "execution_ready": False,
            "execution_performed": False,
            "runner_invoked": False,
            "simulation_performed": False,
            "historical_full_equality_claim": False,
        }


def _materialized_fields(
    definition: VNSnapshotMaterializationRuleDefinition,
    *,
    period: int,
) -> tuple[str, ...]:
    if period == 1:
        return definition.period_one_required_fields
    conditional = tuple(
        field.field_name
        for field in definition.periods_after_one_conditional_fields
    )
    return definition.periods_after_one_required_fields + conditional


def _nested_loader_by_field(
    definition: VNSnapshotMaterializationRuleDefinition,
) -> dict[str, tuple[str, str]]:
    return {
        _NESTED_BY_ID[schema_id].field_name: (
            _NESTED_BY_ID[schema_id].loader_module,
            _NESTED_BY_ID[schema_id].loader_entrypoint,
        )
        for schema_id in definition.nested_value_schema_ids
    }


def _load_context_value(
    field_name: str,
    value: object,
    *,
    nested_loaders: dict[str, tuple[str, str]],
) -> tuple[object, bool]:
    loader_target = nested_loaders.get(field_name)
    if value is None or loader_target is None:
        return value, False
    module_name, loader_name = loader_target
    module = importlib.import_module(module_name)
    return getattr(module, loader_name)(value), True


def _snapshot_payload(
    translation_entry: StrategyAssignmentSnapshotTranslationEntry,
    values: dict[str, object],
    *,
    definition: VNSnapshotMaterializationRuleDefinition,
    period: int,
) -> tuple[dict[str, object], int]:
    payload = translation_entry.snapshot_payload()
    nested_loaders = _nested_loader_by_field(definition)
    nested_loader_count = 0
    for field_name in _materialized_fields(definition, period=period):
        loaded_value, loader_invoked = _load_context_value(
            field_name,
            values[field_name],
            nested_loaders=nested_loaders,
        )
        payload[field_name] = loaded_value
        nested_loader_count += int(loader_invoked)
    return payload, nested_loader_count


def _validation_issues(value: object) -> tuple[
    bool,
    str | None,
    int | None,
    int,
    list[StrategyAssignmentSnapshotMaterializationIssue],
]:
    validation = validate_strategy_assignment_snapshot_materialization_input(value)
    issues = [
        StrategyAssignmentSnapshotMaterializationIssue(
            stage=f"input_validation.{issue.stage}",
            path=issue.path,
            code=issue.code,
            message=issue.message,
        )
        for issue in validation.issues
    ]
    return (
        validation.valid,
        validation.draft_id,
        validation.period,
        validation.expected_vn_entry_count,
        issues,
    )


def materialize_strategy_assignment_snapshots(
    value: object,
) -> StrategyAssignmentSnapshotMaterializationReport:
    """Materialisiert gueltige VN-Kontexte ohne I/O oder Regelausfuehrung."""

    input_valid, draft_id, period, expected_count, issues = _validation_issues(
        value
    )
    if not input_valid:
        return StrategyAssignmentSnapshotMaterializationReport(
            input_valid=False,
            draft_id=draft_id,
            period=period,
            expected_snapshot_count=expected_count,
            snapshot_loader_invocation_count=0,
            nested_loader_invocation_count=0,
            snapshots=(),
            issues=tuple(issues),
        )

    assert isinstance(value, dict)
    context = value["context"]
    assert isinstance(context, dict)
    assert isinstance(period, int)
    raw_entries = context["entries"]
    assert isinstance(raw_entries, list)
    context_entries = {
        (entry["actor_type"], entry["target_id"]): (index, entry)
        for index, entry in enumerate(raw_entries)
    }
    translation = translate_strategy_assignment_draft(value["draft"])
    vn_entries = tuple(
        entry
        for entry in translation.entries
        if entry.assignment.actor_type is StrategyActorType.POLICYHOLDER
    )

    materialized: list[StrategyAssignmentMaterializedSnapshot] = []
    snapshot_loader_count = 0
    nested_loader_count = 0
    for entry in vn_entries:
        assignment = entry.assignment
        index, context_entry = context_entries[
            (assignment.actor_type.value, assignment.target_id)
        ]
        values = context_entry["values"]
        assert isinstance(values, dict)
        path = f"$.context.entries[{index}].values"
        definition = _RULE_BY_STRATEGY_ID[assignment.strategy_id]
        try:
            payload, entry_nested_count = _snapshot_payload(
                entry,
                values,
                definition=definition,
                period=period,
            )
            nested_loader_count += entry_nested_count
        except (AttributeError, TypeError, ValueError, OverflowError) as exc:
            issues.append(
                StrategyAssignmentSnapshotMaterializationIssue(
                    stage="nested_loader",
                    path=path,
                    code="nested_loader_rejected",
                    message=str(exc),
                )
            )
            continue

        module = importlib.import_module(entry.target.snapshot_module)
        snapshot_loader = getattr(module, entry.target.snapshot_loader)
        snapshot_loader_count += 1
        try:
            snapshot = snapshot_loader(payload)
        except (AttributeError, TypeError, ValueError, OverflowError) as exc:
            issues.append(
                StrategyAssignmentSnapshotMaterializationIssue(
                    stage="snapshot_loader",
                    path=f"$.context.entries[{index}]",
                    code="snapshot_loader_rejected",
                    message=str(exc),
                )
            )
            continue
        if not isinstance(snapshot, VNInsuranceRuleSnapshot):
            issues.append(
                StrategyAssignmentSnapshotMaterializationIssue(
                    stage="snapshot_loader",
                    path=f"$.context.entries[{index}]",
                    code="snapshot_type_mismatch",
                    message=(
                        f"{entry.target.snapshot_loader} lieferte nicht "
                        f"{entry.target.snapshot_type}"
                    ),
                )
            )
            continue
        materialized.append(
            StrategyAssignmentMaterializedSnapshot(
                strategy_id=assignment.strategy_id,
                snapshot_collection=entry.target.snapshot_collection,
                snapshot_type=entry.target.snapshot_type,
                snapshot=snapshot,
            )
        )

    published = () if issues else tuple(materialized)
    return StrategyAssignmentSnapshotMaterializationReport(
        input_valid=True,
        draft_id=draft_id,
        period=period,
        expected_snapshot_count=expected_count,
        snapshot_loader_invocation_count=snapshot_loader_count,
        nested_loader_invocation_count=nested_loader_count,
        snapshots=published,
        issues=tuple(issues),
    )


def strategy_assignment_snapshot_materialization_operation_contract_payload(
) -> dict[str, Any]:
    return {
        "schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION,
        "materialization_contract_schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION
        ),
        "validation_schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
        ),
        "translation_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
        "mode": "strategy_assignment_snapshot_materialization_contract",
        "scope": "validated_vn_single_period_context_to_typed_snapshots",
        "materialization_endpoint": (
            "/api/strategies/assignment-snapshot-materialization"
        ),
        "validation_required": True,
        "validated_rule_count": len(VN_SNAPSHOT_MATERIALIZATION_RULES),
        "snapshot_collection": "vn_insurance_rule_snapshots",
        "snapshot_loader_invocation_enabled": True,
        "snapshots_published_only_after_complete_success": True,
        "partial_results_allowed": False,
        "persistence_enabled": False,
        "execution_enabled": False,
        "runner_enabled": False,
        "simulation_performed": False,
        "historical_full_equality_claim": False,
    }
