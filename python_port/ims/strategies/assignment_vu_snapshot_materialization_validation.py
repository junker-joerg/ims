from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from ims.strategies.assignment_snapshot_context import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION,
    validate_strategy_assignment_snapshot_context,
)
from ims.strategies.assignment_snapshot_translation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
    translate_strategy_assignment_draft,
)
from ims.strategies.assignment_vu_snapshot_materialization_contract import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION,
    VU_SNAPSHOT_MATERIALIZATION_TARGETS,
    strategy_vu_snapshot_materialization_contract_issues,
)
from ims.strategies.catalog import StrategyActorType


STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION = (
    "ims.strategy-assignment-vu-snapshot-materialization-input.v1"
)
STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION = (
    "ims.strategy-assignment-vu-snapshot-materialization-validation.v1"
)
VU_THRESHOLD_SOURCE_POLICY_ID = "insurer-aspiration-profile-v1"
VU_DRAW_SOURCE_POLICY_ID = "explicit-context-draws-v1"
VU_FALLBACK_POLICY_ID = "reject-loader-and-runner-fallbacks-v1"

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "threshold_source_policy",
        "draw_source_policy",
        "fallback_policy",
        "draft",
        "context",
    }
)
_TARGETS_BY_ID = {
    target.strategy_id: target for target in VU_SNAPSHOT_MATERIALIZATION_TARGETS
}


@dataclass(frozen=True, slots=True)
class VUSnapshotMaterializationValidationIssue:
    stage: str
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class VUSnapshotMaterializationValidationReport:
    valid: bool
    policy_valid: bool
    base_context_valid: bool
    submitted_schema_version: str | None
    draft_id: str | None
    period: int | None
    expected_vu_entry_count: int
    validated_vu_entry_count: int
    expected_value_count: int
    validated_value_count: int
    rejected_fallback_count: int
    issues: tuple[VUSnapshotMaterializationValidationIssue, ...]
    schema_version: str = (
        STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
    )
    mode: str = "strategy_assignment_vu_snapshot_materialization_validation"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "status": "ok" if self.valid else "error",
            "valid": self.valid,
            "policy_valid": self.policy_valid,
            "base_context_valid": self.base_context_valid,
            "submitted_schema_version": self.submitted_schema_version,
            "draft_id": self.draft_id,
            "period": self.period,
            "expected_vu_entry_count": self.expected_vu_entry_count,
            "validated_vu_entry_count": self.validated_vu_entry_count,
            "expected_value_count": self.expected_value_count,
            "validated_value_count": self.validated_value_count,
            "rejected_fallback_count": self.rejected_fallback_count,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "threshold_values_cross_checked_against_actor_state": False,
            "context_values_inspected": self.base_context_valid,
            "context_values_consumed": False,
            "snapshot_loader_invocation_performed": False,
            "snapshot_materialization_ready": False,
            "writes_performed": False,
            "snapshots_created": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
        }


def _add_issue(
    issues: list[VUSnapshotMaterializationValidationIssue],
    *,
    stage: str,
    path: str,
    code: str,
    message: str,
) -> None:
    issues.append(
        VUSnapshotMaterializationValidationIssue(
            stage=stage,
            path=path,
            code=code,
            message=message,
        )
    )


def _report(
    *,
    valid: bool,
    policy_valid: bool,
    base_context_valid: bool,
    submitted_schema_version: str | None,
    draft_id: str | None,
    period: int | None,
    expected_vu_entry_count: int,
    validated_vu_entry_count: int,
    expected_value_count: int,
    validated_value_count: int,
    rejected_fallback_count: int,
    issues: list[VUSnapshotMaterializationValidationIssue],
) -> VUSnapshotMaterializationValidationReport:
    return VUSnapshotMaterializationValidationReport(
        valid=valid,
        policy_valid=policy_valid,
        base_context_valid=base_context_valid,
        submitted_schema_version=submitted_schema_version,
        draft_id=draft_id,
        period=period,
        expected_vu_entry_count=expected_vu_entry_count,
        validated_vu_entry_count=validated_vu_entry_count,
        expected_value_count=expected_value_count,
        validated_value_count=validated_value_count,
        rejected_fallback_count=rejected_fallback_count,
        issues=tuple(issues),
    )


def _validate_request_contract(
    value: object,
    issues: list[VUSnapshotMaterializationValidationIssue],
) -> tuple[dict[str, object] | None, str | None]:
    if not isinstance(value, dict):
        _add_issue(
            issues,
            stage="input_contract",
            path="$",
            code="request_object_required",
            message="VU-Materialisierungspruefung muss ein Objekt sein",
        )
        return None, None

    for field_name in sorted(_REQUEST_FIELDS - set(value)):
        _add_issue(
            issues,
            stage="input_contract",
            path=f"$.{field_name}",
            code="request_field_missing",
            message=f"Pflichtfeld der VU-Anfrage fehlt: {field_name}",
        )
    for field_name in sorted(set(value) - _REQUEST_FIELDS):
        _add_issue(
            issues,
            stage="input_contract",
            path=f"$.{field_name}",
            code="request_field_unknown",
            message=f"Unbekanntes Feld der VU-Anfrage: {field_name}",
        )

    submitted_schema_version = (
        value.get("schema_version")
        if isinstance(value.get("schema_version"), str)
        else None
    )
    exact_values = {
        "schema_version": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION,
        "threshold_source_policy": VU_THRESHOLD_SOURCE_POLICY_ID,
        "draw_source_policy": VU_DRAW_SOURCE_POLICY_ID,
        "fallback_policy": VU_FALLBACK_POLICY_ID,
    }
    for field_name, expected in exact_values.items():
        if value.get(field_name) != expected:
            _add_issue(
                issues,
                stage="input_contract",
                path=f"$.{field_name}",
                code="contract_value_mismatch",
                message=f"{field_name} muss {expected!r} sein",
            )
    return value, submitted_schema_version


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _validate_vu_value(
    field_name: str,
    value: object,
    *,
    path: str,
    issues: list[VUSnapshotMaterializationValidationIssue],
) -> bool:
    if value is None:
        _add_issue(
            issues,
            stage="fallback_policy",
            path=path,
            code="fallback_not_allowed",
            message=f"{field_name} muss explizit vorliegen; Fallback ist nicht zugelassen",
        )
        return False
    if field_name == "random_draws" and (
        not isinstance(value, list)
        or any(not _is_finite_number(item) or not 0.0 <= float(item) < 1.0 for item in value)
    ):
        _add_issue(
            issues,
            stage="draw_policy",
            path=path,
            code="uniform_draw_out_of_range",
            message="Vrvu01-Ziehungen muessen im Intervall [0.0, 1.0) liegen",
        )
        return False
    if field_name == "active_policyholder_count" and (
        not isinstance(value, int) or isinstance(value, bool) or value < 0
    ):
        _add_issue(
            issues,
            stage="state_value",
            path=path,
            code="active_policyholder_count_negative",
            message="active_policyholder_count muss eine nicht negative Ganzzahl sein",
        )
        return False
    if field_name == "previous_policyholders_sector" and (
        not isinstance(value, list)
        or any(not _is_finite_number(item) or float(item) < 0.0 for item in value)
    ):
        _add_issue(
            issues,
            stage="state_value",
            path=path,
            code="previous_policyholders_negative",
            message="Vorperiodenbestaende muessen nicht negative endliche Zahlen sein",
        )
        return False
    return True


def validate_strategy_assignment_vu_snapshot_materialization_input(
    value: object,
) -> VUSnapshotMaterializationValidationReport:
    """Prueft VU-Kontextwerte atomar, ohne Snapshotloader aufzurufen."""

    issues: list[VUSnapshotMaterializationValidationIssue] = []
    request, submitted_schema_version = _validate_request_contract(value, issues)
    if request is None or issues:
        return _report(
            valid=False,
            policy_valid=False,
            base_context_valid=False,
            submitted_schema_version=submitted_schema_version,
            draft_id=None,
            period=None,
            expected_vu_entry_count=0,
            validated_vu_entry_count=0,
            expected_value_count=0,
            validated_value_count=0,
            rejected_fallback_count=0,
            issues=issues,
        )

    base_request = {"draft": request["draft"], "context": request["context"]}
    base_report = validate_strategy_assignment_snapshot_context(base_request)
    translation = translate_strategy_assignment_draft(request["draft"])
    vu_entries = tuple(
        entry
        for entry in translation.entries
        if entry.assignment.actor_type is StrategyActorType.INSURER
    )
    expected_value_count = sum(
        len(entry.target.unresolved_snapshot_fields) for entry in vu_entries
    )
    for issue in base_report.issues:
        _add_issue(
            issues,
            stage="base_context",
            path=issue.path,
            code=issue.code,
            message=issue.message,
        )
    if not base_report.valid:
        return _report(
            valid=False,
            policy_valid=True,
            base_context_valid=False,
            submitted_schema_version=submitted_schema_version,
            draft_id=base_report.draft_id,
            period=base_report.period,
            expected_vu_entry_count=len(vu_entries),
            validated_vu_entry_count=0,
            expected_value_count=expected_value_count,
            validated_value_count=0,
            rejected_fallback_count=0,
            issues=issues,
        )

    if not vu_entries:
        _add_issue(
            issues,
            stage="vu_context",
            path="$.draft.assignments",
            code="vu_entry_required",
            message="VU-Materialisierungspruefung benoetigt mindestens einen VU-Eintrag",
        )

    context = request["context"]
    assert isinstance(context, dict)
    raw_entries = context["entries"]
    assert isinstance(raw_entries, list)
    context_entries = {
        (entry["actor_type"], entry["target_id"]): (index, entry)
        for index, entry in enumerate(raw_entries)
    }

    validated_vu_entry_count = 0
    validated_value_count = 0
    rejected_fallback_count = 0
    for translation_entry in vu_entries:
        assignment = translation_entry.assignment
        index, raw_entry = context_entries[
            (assignment.actor_type.value, assignment.target_id)
        ]
        values = raw_entry["values"]
        assert isinstance(values, dict)
        target = _TARGETS_BY_ID[assignment.strategy_id]
        issue_start = len(issues)
        for field_name in target.open_snapshot_fields:
            field_value = values[field_name]
            if field_value is None:
                rejected_fallback_count += 1
            if _validate_vu_value(
                field_name,
                field_value,
                path=f"$.context.entries[{index}].values.{field_name}",
                issues=issues,
            ):
                validated_value_count += 1
        if len(issues) == issue_start:
            validated_vu_entry_count += 1

    valid = not issues and validated_vu_entry_count == len(vu_entries)
    return _report(
        valid=valid,
        policy_valid=True,
        base_context_valid=True,
        submitted_schema_version=submitted_schema_version,
        draft_id=base_report.draft_id,
        period=base_report.period,
        expected_vu_entry_count=len(vu_entries),
        validated_vu_entry_count=validated_vu_entry_count,
        expected_value_count=expected_value_count,
        validated_value_count=validated_value_count,
        rejected_fallback_count=rejected_fallback_count,
        issues=issues,
    )


def strategy_assignment_vu_snapshot_materialization_validation_contract_payload(
) -> dict[str, Any]:
    """Beschreibt die PR119-Eingabepruefung und ihre geschlossenen Grenzen."""

    return {
        "schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
        ),
        "input_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION
        ),
        "inventory_contract_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION
        ),
        "context_validation_schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION
        ),
        "translation_schema_version": STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
        "mode": "strategy_assignment_vu_snapshot_materialization_validation_contract",
        "base_model": "Vdefmd6",
        "scope": "atomic_vu_single_period_input_validation",
        "validation_endpoint": (
            "/api/strategies/assignment-vu-snapshot-materialization-validation"
        ),
        "request_fields": tuple(sorted(_REQUEST_FIELDS)),
        "threshold_source_policy": {
            "policy_id": VU_THRESHOLD_SOURCE_POLICY_ID,
            "reserve_thresholds": "A1/A2[1] -> aspiration profile index 0",
            "net_switcher_thresholds": "A1/A2[2] -> aspiration profile index 1",
            "market_share_thresholds": "A1/A2[3] -> aspiration profile index 2",
            "values_cross_checked_against_actor_state": False,
        },
        "draw_source_policy": {
            "policy_id": VU_DRAW_SOURCE_POLICY_ID,
            "random_draws": "four explicit finite values in [0.0, 1.0)",
            "normal_draws": "four explicit finite values",
            "required_in_every_submitted_period": True,
            "historical_rng_sequence_claimed": False,
        },
        "fallback_policy": {
            "policy_id": VU_FALLBACK_POLICY_ID,
            "allowed_fallbacks": (),
            "loader_defaults_accepted": False,
            "runner_draw_sources_accepted": False,
            "runner_state_sources_accepted": False,
        },
        "validation_order": (
            "validate_vu_input_schema_and_policy_ids",
            "validate_pr112_context_atomically",
            "select_insurer_entries",
            "reject_null_loader_or_runner_fallbacks",
            "validate_draw_and_state_value_semantics",
            "accept_only_when_every_vu_entry_is_valid",
        ),
        "validated_strategy_count": len(VU_SNAPSHOT_MATERIALIZATION_TARGETS),
        "materialization_contract_issue_count": len(
            strategy_vu_snapshot_materialization_contract_issues()
        ),
        "at_least_one_vu_entry_required": True,
        "partial_acceptance_allowed": False,
        "threshold_values_cross_checked_against_actor_state": False,
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
