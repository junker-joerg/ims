from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import importlib
from typing import Any

from ims.strategies.assignment_snapshot_translation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
    translate_strategy_assignment_draft,
)
from ims.strategies.assignment_vu_snapshot_materialization_contract import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION,
    VU_SNAPSHOT_MATERIALIZATION_TARGETS,
)
from ims.strategies.assignment_vu_snapshot_state_validation import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION,
    validate_strategy_assignment_vu_snapshot_state,
)
from ims.strategies.catalog import StrategyActorType


STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VERSION = (
    "ims.strategy-assignment-vu-snapshot-materialization.v1"
)


@dataclass(frozen=True, slots=True)
class VUAssignmentSnapshotMaterializationIssue:
    stage: str
    path: str
    code: str
    message: str


def _json_value(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class VUAssignmentMaterializedSnapshot:
    strategy_id: str
    snapshot_collection: str
    snapshot_type: str
    snapshot: object

    def to_dict(self) -> dict[str, object]:
        return {
            "strategy_id": self.strategy_id,
            "snapshot_collection": self.snapshot_collection,
            "snapshot_type": self.snapshot_type,
            "snapshot": _json_value(asdict(self.snapshot)),
        }


@dataclass(frozen=True, slots=True)
class VUAssignmentSnapshotMaterializationReport:
    input_valid: bool
    draft_id: str | None
    period: int | None
    expected_snapshot_count: int
    snapshot_loader_invocation_count: int
    snapshots: tuple[VUAssignmentMaterializedSnapshot, ...]
    issues: tuple[VUAssignmentSnapshotMaterializationIssue, ...]
    schema_version: str = STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VERSION
    mode: str = "strategy_assignment_vu_snapshot_materialization"

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
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "snapshots": [entry.to_dict() for entry in self.snapshots],
            "state_provenance_validated": self.input_valid,
            "context_values_consumed": self.input_valid,
            "state_values_consumed": False,
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
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
        }


def _input_validation(
    value: object,
) -> tuple[
    bool,
    str | None,
    int | None,
    int,
    list[VUAssignmentSnapshotMaterializationIssue],
]:
    validation = validate_strategy_assignment_vu_snapshot_state(value)
    issues = [
        VUAssignmentSnapshotMaterializationIssue(
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
        validation.expected_state_entry_count,
        issues,
    )


def materialize_strategy_assignment_vu_snapshots(
    value: object,
) -> VUAssignmentSnapshotMaterializationReport:
    """Materialisiert gueltige VU-Kontexte ohne I/O oder Regelausfuehrung."""

    input_valid, draft_id, period, expected_count, issues = _input_validation(
        value
    )
    if not input_valid:
        return VUAssignmentSnapshotMaterializationReport(
            input_valid=False,
            draft_id=draft_id,
            period=period,
            expected_snapshot_count=expected_count,
            snapshot_loader_invocation_count=0,
            snapshots=(),
            issues=tuple(issues),
        )

    assert isinstance(value, dict)
    materialization_input = value["input"]
    assert isinstance(materialization_input, dict)
    context = materialization_input["context"]
    assert isinstance(context, dict)
    raw_entries = context["entries"]
    assert isinstance(raw_entries, list)
    context_entries = {
        (entry["actor_type"], entry["target_id"]): (index, entry)
        for index, entry in enumerate(raw_entries)
    }
    translation = translate_strategy_assignment_draft(
        materialization_input["draft"]
    )
    vu_entries = tuple(
        entry
        for entry in translation.entries
        if entry.assignment.actor_type is StrategyActorType.INSURER
    )

    materialized: list[VUAssignmentMaterializedSnapshot] = []
    snapshot_loader_count = 0
    for entry in vu_entries:
        assignment = entry.assignment
        index, context_entry = context_entries[
            (assignment.actor_type.value, assignment.target_id)
        ]
        values = context_entry["values"]
        assert isinstance(values, dict)
        payload = entry.snapshot_payload()
        for field_name in entry.target.unresolved_snapshot_fields:
            payload[field_name] = values[field_name]

        module = importlib.import_module(entry.target.snapshot_module)
        snapshot_loader = getattr(module, entry.target.snapshot_loader)
        expected_type = getattr(module, entry.target.snapshot_type)
        snapshot_loader_count += 1
        try:
            snapshot = snapshot_loader(payload)
        except (AttributeError, TypeError, ValueError, OverflowError) as exc:
            issues.append(
                VUAssignmentSnapshotMaterializationIssue(
                    stage="snapshot_loader",
                    path=f"$.input.context.entries[{index}]",
                    code="snapshot_loader_rejected",
                    message=str(exc),
                )
            )
            continue
        if not isinstance(snapshot, expected_type):
            issues.append(
                VUAssignmentSnapshotMaterializationIssue(
                    stage="snapshot_loader",
                    path=f"$.input.context.entries[{index}]",
                    code="snapshot_type_mismatch",
                    message=(
                        f"{entry.target.snapshot_loader} lieferte nicht "
                        f"{entry.target.snapshot_type}"
                    ),
                )
            )
            continue
        materialized.append(
            VUAssignmentMaterializedSnapshot(
                strategy_id=assignment.strategy_id,
                snapshot_collection=entry.target.snapshot_collection,
                snapshot_type=entry.target.snapshot_type,
                snapshot=snapshot,
            )
        )

    published = () if issues else tuple(materialized)
    return VUAssignmentSnapshotMaterializationReport(
        input_valid=True,
        draft_id=draft_id,
        period=period,
        expected_snapshot_count=expected_count,
        snapshot_loader_invocation_count=snapshot_loader_count,
        snapshots=published,
        issues=tuple(issues),
    )


def strategy_assignment_vu_snapshot_materialization_operation_contract_payload(
) -> dict[str, Any]:
    """Beschreibt die atomare PR121-Materialisierung ohne Ausfuehrung."""

    return {
        "schema_version": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VERSION,
        "inventory_contract_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION
        ),
        "validation_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION
        ),
        "translation_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
        "mode": "strategy_assignment_vu_snapshot_materialization_contract",
        "scope": "validated_vu_single_period_context_to_typed_snapshots",
        "materialization_endpoint": (
            "/api/strategies/assignment-vu-snapshot-materialization"
        ),
        "validation_required": True,
        "state_provenance_validation_required": True,
        "validated_strategy_count": len(VU_SNAPSHOT_MATERIALIZATION_TARGETS),
        "snapshot_type_count": len(
            {target.snapshot_type for target in VU_SNAPSHOT_MATERIALIZATION_TARGETS}
        ),
        "snapshot_loader_invocation_enabled": True,
        "snapshots_published_only_after_complete_success": True,
        "partial_results_allowed": False,
        "context_values_consumed": True,
        "state_values_consumed": False,
        "persistence_enabled": False,
        "execution_enabled": False,
        "runner_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
