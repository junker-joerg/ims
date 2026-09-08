from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import re
from typing import Any

from ims.strategies.assignment_snapshot_materialization_validation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION,
    validate_strategy_assignment_snapshot_materialization_input,
)
from ims.strategies.assignment_snapshot_translation import (
    translate_strategy_assignment_draft,
)
from ims.strategies.assignment_vu_snapshot_materialization_validation import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION,
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION,
    VU_DRAW_SOURCE_POLICY_ID,
    VU_FALLBACK_POLICY_ID,
    VU_THRESHOLD_SOURCE_POLICY_ID,
    validate_strategy_assignment_vu_snapshot_materialization_input,
)
from ims.strategies.assignment_vu_snapshot_state_validation import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION,
    validate_strategy_assignment_vu_snapshot_state,
)
from ims.strategies.catalog import StrategyActorType
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_CONTRACT_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)


STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION = (
    "ims.strategy-execution-candidate-input.v1"
)
STRATEGY_EXECUTION_CANDIDATE_VALIDATION_VERSION = (
    "ims.strategy-execution-candidate-validation.v1"
)
STRATEGY_EXECUTION_SCENARIO_PROFILE_REFERENCE_VERSION = (
    "ims.strategy-execution-scenario-profile-reference.v1"
)
STRATEGY_EXECUTION_VN_PROCESS_INPUT_VERSION = (
    "ims.strategy-execution-vn-process-input.v1"
)
STRATEGY_EXECUTION_SCENARIO_PROFILE_SOURCE_POLICY_ID = (
    "server-known-local-scenario-profile-v1"
)
STRATEGY_EXECUTION_VN_PROCESS_DRAW_SOURCE_POLICY_ID = (
    "explicit-vn-process-draws-v1"
)
STRATEGY_EXECUTION_VN_DECISION_SOURCE_POLICY_ID = (
    "server-rematerialized-vn-rule-snapshots-v1"
)
STRATEGY_EXECUTION_VN_INFORMATION_COST_SOURCE_POLICY_ID = (
    "vn-rule-application-v1"
)

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "candidate_schema_version",
        "base_model",
        "scope",
        "assignment_draft",
        "snapshot_context",
        "vu_input_policy",
        "vu_state_provenance",
        "scenario_profile_reference",
        "vn_process_input",
    }
)
_VU_INPUT_POLICY_FIELDS = frozenset(
    {
        "schema_version",
        "threshold_source_policy",
        "draw_source_policy",
        "fallback_policy",
    }
)
_PROFILE_FIELDS = frozenset(
    {
        "schema_version",
        "source_policy",
        "profile_id",
        "period",
        "expected_bav_id",
        "expected_insurer_ids",
        "expected_policyholder_ids",
    }
)
_VN_PROCESS_FIELDS = frozenset(
    {
        "schema_version",
        "draft_id",
        "period",
        "draw_source_policy",
        "decision_source_policy",
        "information_cost_source_policy",
        "damage_settlement_snapshots",
        "settlement_snapshots",
    }
)
_DAMAGE_SNAPSHOT_FIELDS = frozenset(
    {
        "policyholder_id",
        "previous_wealth",
        "previous_wealth_sector",
        "damage_thresholds",
        "change_shock",
        "parameters",
        "draws",
    }
)
_DAMAGE_PARAMETER_FIELDS = frozenset(
    {
        "damage_intercept_normal",
        "damage_factor_normal",
        "damage_intercept_shock",
        "damage_factor_shock",
    }
)
_DAMAGE_DRAW_FIELDS = frozenset({"trigger_draws", "amount_draws"})


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateValidationIssue:
    stage: str
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateValidationReport:
    valid: bool
    request_shape_valid: bool
    vn_context_valid: bool
    vu_input_valid: bool
    vu_state_valid: bool
    scenario_profile_reference_valid: bool
    vn_process_input_valid: bool
    identifiers_consistent: bool
    submitted_schema_version: str | None
    draft_id: str | None
    period: int | None
    expected_vu_entry_count: int
    validated_vu_entry_count: int
    expected_vn_entry_count: int
    validated_vn_entry_count: int
    expected_vn_process_target_count: int
    validated_vn_process_target_count: int
    nested_validation_loader_invocation_count: int
    issues: tuple[StrategyExecutionCandidateValidationIssue, ...]
    schema_version: str = STRATEGY_EXECUTION_CANDIDATE_VALIDATION_VERSION
    mode: str = "strategy_execution_candidate_validation"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "input_schema_version": STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION,
            "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
            "mode": self.mode,
            "status": "ok" if self.valid else "error",
            "valid": self.valid,
            "request_shape_valid": self.request_shape_valid,
            "vn_context_valid": self.vn_context_valid,
            "vu_input_valid": self.vu_input_valid,
            "vu_state_valid": self.vu_state_valid,
            "scenario_profile_reference_valid": (
                self.scenario_profile_reference_valid
            ),
            "vn_process_input_valid": self.vn_process_input_valid,
            "identifiers_consistent": self.identifiers_consistent,
            "submitted_schema_version": self.submitted_schema_version,
            "draft_id": self.draft_id,
            "period": self.period,
            "expected_vu_entry_count": self.expected_vu_entry_count,
            "validated_vu_entry_count": self.validated_vu_entry_count,
            "expected_vn_entry_count": self.expected_vn_entry_count,
            "validated_vn_entry_count": self.validated_vn_entry_count,
            "expected_vn_process_target_count": (
                self.expected_vn_process_target_count
            ),
            "validated_vn_process_target_count": (
                self.validated_vn_process_target_count
            ),
            "nested_validation_loader_invocation_count": (
                self.nested_validation_loader_invocation_count
            ),
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "partial_candidate_returned": False,
            "scenario_profile_resolved": False,
            "source_values_consumed": False,
            "snapshot_loader_invocation_performed": False,
            "snapshots_created": False,
            "server_side_rematerialization_performed": False,
            "digest_calculation_performed": False,
            "candidate_created": False,
            "candidate_persisted": False,
            "run_control_connected": False,
            "runner_invocation_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
        }


def _issue(
    issues: list[StrategyExecutionCandidateValidationIssue],
    *,
    stage: str,
    path: str,
    code: str,
    message: str,
) -> None:
    issues.append(
        StrategyExecutionCandidateValidationIssue(
            stage=stage,
            path=path,
            code=code,
            message=message,
        )
    )


def _exact_object(
    value: object,
    expected_fields: frozenset[str],
    *,
    path: str,
    noun: str,
    issues: list[StrategyExecutionCandidateValidationIssue],
) -> dict[str, object] | None:
    if not isinstance(value, dict):
        _issue(
            issues,
            stage="input_contract",
            path=path,
            code="object_required",
            message=f"{noun} muss ein Objekt sein",
        )
        return None
    for field_name in sorted(expected_fields - set(value)):
        _issue(
            issues,
            stage="input_contract",
            path=f"{path}.{field_name}",
            code="field_missing",
            message=f"Pflichtfeld fehlt in {noun}: {field_name}",
        )
    for field_name in sorted(set(value) - expected_fields):
        _issue(
            issues,
            stage="input_contract",
            path=f"{path}.{field_name}",
            code="field_unknown",
            message=f"Unbekanntes Feld in {noun}: {field_name}",
        )
    return value


def _require_exact_value(
    value: dict[str, object],
    field_name: str,
    expected: object,
    *,
    path: str,
    issues: list[StrategyExecutionCandidateValidationIssue],
) -> None:
    if value.get(field_name) != expected:
        _issue(
            issues,
            stage="input_contract",
            path=f"{path}.{field_name}",
            code="contract_value_mismatch",
            message=f"{field_name} muss {expected!r} sein",
        )


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _two_finite_numbers(
    value: object,
    *,
    path: str,
    issues: list[StrategyExecutionCandidateValidationIssue],
) -> bool:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(not _is_finite_number(item) for item in value)
    ):
        _issue(
            issues,
            stage="vn_process_input",
            path=path,
            code="two_finite_values_required",
            message="VN-Prozesswert benoetigt genau zwei endliche Zahlen",
        )
        return False
    return True


def _positive_unique_ids(
    value: object,
    *,
    path: str,
    issues: list[StrategyExecutionCandidateValidationIssue],
) -> tuple[int, ...] | None:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, int) or isinstance(item, bool) or item <= 0 for item in value)
        or len(set(value)) != len(value)
    ):
        _issue(
            issues,
            stage="scenario_profile_reference",
            path=path,
            code="positive_unique_ids_required",
            message="Erwartete Profil-IDs muessen positive eindeutige Ganzzahlen sein",
        )
        return None
    return tuple(value)


def _remap_existing_path(path: str, *, source: str) -> str:
    mappings = {
        "vn": (("$.draft", "$.assignment_draft"), ("$.context", "$.snapshot_context")),
        "vu": (
            ("$.draft", "$.assignment_draft"),
            ("$.context", "$.snapshot_context"),
            ("$.schema_version", "$.vu_input_policy.schema_version"),
            ("$.threshold_source_policy", "$.vu_input_policy.threshold_source_policy"),
            ("$.draw_source_policy", "$.vu_input_policy.draw_source_policy"),
            ("$.fallback_policy", "$.vu_input_policy.fallback_policy"),
        ),
        "vu_state": (
            ("$.input.context", "$.snapshot_context"),
            ("$.input.draft", "$.assignment_draft"),
            ("$.input.schema_version", "$.vu_input_policy.schema_version"),
            ("$.input.threshold_source_policy", "$.vu_input_policy.threshold_source_policy"),
            ("$.input.draw_source_policy", "$.vu_input_policy.draw_source_policy"),
            ("$.input.fallback_policy", "$.vu_input_policy.fallback_policy"),
            ("$.state", "$.vu_state_provenance"),
        ),
    }
    for old_prefix, new_prefix in mappings[source]:
        if path == old_prefix or path.startswith(f"{old_prefix}.") or path.startswith(
            f"{old_prefix}["
        ):
            return f"{new_prefix}{path[len(old_prefix):]}"
    return path


def _append_existing_issues(
    target: list[StrategyExecutionCandidateValidationIssue],
    source_issues: tuple[object, ...],
    *,
    stage: str,
    source: str,
) -> None:
    for item in source_issues:
        target.append(
            StrategyExecutionCandidateValidationIssue(
                stage=stage,
                path=_remap_existing_path(str(getattr(item, "path")), source=source),
                code=str(getattr(item, "code")),
                message=str(getattr(item, "message")),
            )
        )


def _validate_damage_snapshot(
    value: object,
    *,
    index: int,
    issues: list[StrategyExecutionCandidateValidationIssue],
) -> tuple[int | None, bool | None]:
    path = f"$.vn_process_input.damage_settlement_snapshots[{index}]"
    issue_start = len(issues)
    snapshot = _exact_object(
        value,
        _DAMAGE_SNAPSHOT_FIELDS,
        path=path,
        noun="VN-Schaden-/Abrechnungseintrag",
        issues=issues,
    )
    if snapshot is None:
        return None, None

    policyholder_id = snapshot.get("policyholder_id")
    if (
        not isinstance(policyholder_id, int)
        or isinstance(policyholder_id, bool)
        or policyholder_id <= 0
    ):
        _issue(
            issues,
            stage="vn_process_input",
            path=f"{path}.policyholder_id",
            code="positive_policyholder_id_required",
            message="policyholder_id muss eine positive Ganzzahl sein",
        )
        policyholder_id = None
    for field_name in ("previous_wealth",):
        if not _is_finite_number(snapshot.get(field_name)):
            _issue(
                issues,
                stage="vn_process_input",
                path=f"{path}.{field_name}",
                code="finite_number_required",
                message=f"{field_name} muss eine endliche Zahl sein",
            )
    _two_finite_numbers(
        snapshot.get("previous_wealth_sector"),
        path=f"{path}.previous_wealth_sector",
        issues=issues,
    )
    _two_finite_numbers(
        snapshot.get("damage_thresholds"),
        path=f"{path}.damage_thresholds",
        issues=issues,
    )
    change_shock = snapshot.get("change_shock")
    if not isinstance(change_shock, bool):
        _issue(
            issues,
            stage="vn_process_input",
            path=f"{path}.change_shock",
            code="boolean_required",
            message="change_shock muss ein boolescher Wert sein",
        )
        change_shock = None

    parameters = _exact_object(
        snapshot.get("parameters"),
        _DAMAGE_PARAMETER_FIELDS,
        path=f"{path}.parameters",
        noun="VN-Schadenparameter",
        issues=issues,
    )
    if parameters is not None:
        for field_name in sorted(_DAMAGE_PARAMETER_FIELDS):
            _two_finite_numbers(
                parameters.get(field_name),
                path=f"{path}.parameters.{field_name}",
                issues=issues,
            )
    draws = _exact_object(
        snapshot.get("draws"),
        _DAMAGE_DRAW_FIELDS,
        path=f"{path}.draws",
        noun="explizite VN-Schadenziehungen",
        issues=issues,
    )
    if draws is not None:
        for field_name in sorted(_DAMAGE_DRAW_FIELDS):
            _two_finite_numbers(
                draws.get(field_name),
                path=f"{path}.draws.{field_name}",
                issues=issues,
            )
    return policyholder_id, change_shock if len(issues) == issue_start else None


def _validate_profile_reference(
    profile: dict[str, object],
    *,
    period: int | None,
    insurer_ids: set[int],
    policyholder_ids: set[int],
    issues: list[StrategyExecutionCandidateValidationIssue],
) -> bool:
    issue_start = len(issues)
    _require_exact_value(
        profile,
        "schema_version",
        STRATEGY_EXECUTION_SCENARIO_PROFILE_REFERENCE_VERSION,
        path="$.scenario_profile_reference",
        issues=issues,
    )
    _require_exact_value(
        profile,
        "source_policy",
        STRATEGY_EXECUTION_SCENARIO_PROFILE_SOURCE_POLICY_ID,
        path="$.scenario_profile_reference",
        issues=issues,
    )
    profile_id = profile.get("profile_id")
    if (
        not isinstance(profile_id, str)
        or re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", profile_id) is None
    ):
        _issue(
            issues,
            stage="scenario_profile_reference",
            path="$.scenario_profile_reference.profile_id",
            code="profile_id_required",
            message="profile_id muss ein stabiler Bezeichner ohne Pfadsyntax sein",
        )
    profile_period = profile.get("period")
    if (
        not isinstance(profile_period, int)
        or isinstance(profile_period, bool)
        or profile_period <= 0
    ):
        _issue(
            issues,
            stage="scenario_profile_reference",
            path="$.scenario_profile_reference.period",
            code="positive_period_required",
            message="Profilperiode muss eine positive Ganzzahl sein",
        )
    elif period is not None and profile_period != period:
        _issue(
            issues,
            stage="cross_document",
            path="$.scenario_profile_reference.period",
            code="period_mismatch",
            message="Profilperiode stimmt nicht mit dem Snapshotkontext ueberein",
        )
    bav_id = profile.get("expected_bav_id")
    if not isinstance(bav_id, int) or isinstance(bav_id, bool) or bav_id <= 0:
        _issue(
            issues,
            stage="scenario_profile_reference",
            path="$.scenario_profile_reference.expected_bav_id",
            code="positive_bav_id_required",
            message="expected_bav_id muss eine positive Ganzzahl sein",
        )
    expected_insurers = _positive_unique_ids(
        profile.get("expected_insurer_ids"),
        path="$.scenario_profile_reference.expected_insurer_ids",
        issues=issues,
    )
    expected_policyholders = _positive_unique_ids(
        profile.get("expected_policyholder_ids"),
        path="$.scenario_profile_reference.expected_policyholder_ids",
        issues=issues,
    )
    if expected_insurers is not None and set(expected_insurers) != insurer_ids:
        _issue(
            issues,
            stage="cross_document",
            path="$.scenario_profile_reference.expected_insurer_ids",
            code="insurer_population_mismatch",
            message="Erwartete Profil-VU entsprechen nicht exakt den VU-Zielen im Entwurf",
        )
    if (
        expected_policyholders is not None
        and set(expected_policyholders) != policyholder_ids
    ):
        _issue(
            issues,
            stage="cross_document",
            path="$.scenario_profile_reference.expected_policyholder_ids",
            code="policyholder_population_mismatch",
            message="Erwartete Profil-VN entsprechen nicht exakt den VN-Zielen im Entwurf",
        )
    return len(issues) == issue_start


def _validate_vn_process_input(
    process: dict[str, object],
    *,
    draft_id: str | None,
    period: int | None,
    policyholder_ids: set[int],
    context_change_shock: dict[int, bool],
    issues: list[StrategyExecutionCandidateValidationIssue],
) -> tuple[bool, int]:
    issue_start = len(issues)
    exact_values = {
        "schema_version": STRATEGY_EXECUTION_VN_PROCESS_INPUT_VERSION,
        "draw_source_policy": STRATEGY_EXECUTION_VN_PROCESS_DRAW_SOURCE_POLICY_ID,
        "decision_source_policy": STRATEGY_EXECUTION_VN_DECISION_SOURCE_POLICY_ID,
        "information_cost_source_policy": (
            STRATEGY_EXECUTION_VN_INFORMATION_COST_SOURCE_POLICY_ID
        ),
    }
    for field_name, expected in exact_values.items():
        _require_exact_value(
            process,
            field_name,
            expected,
            path="$.vn_process_input",
            issues=issues,
        )
    if draft_id is not None and process.get("draft_id") != draft_id:
        _issue(
            issues,
            stage="cross_document",
            path="$.vn_process_input.draft_id",
            code="draft_id_mismatch",
            message="VN-Prozess-draft_id stimmt nicht mit dem Entwurf ueberein",
        )
    if period is not None and process.get("period") != period:
        _issue(
            issues,
            stage="cross_document",
            path="$.vn_process_input.period",
            code="period_mismatch",
            message="VN-Prozessperiode stimmt nicht mit dem Snapshotkontext ueberein",
        )
    settlement_snapshots = process.get("settlement_snapshots")
    if not isinstance(settlement_snapshots, list):
        _issue(
            issues,
            stage="vn_process_input",
            path="$.vn_process_input.settlement_snapshots",
            code="list_required",
            message="settlement_snapshots muss eine Liste sein",
        )
    elif settlement_snapshots:
        _issue(
            issues,
            stage="vn_process_input",
            path="$.vn_process_input.settlement_snapshots",
            code="settlement_only_not_supported",
            message=(
                "Reine Settlement-Snapshots umgehen die vorbereiteten VN-Entscheidungen "
                "und sind fuer den ersten Kandidatenpfad gesperrt"
            ),
        )
    damage_snapshots = process.get("damage_settlement_snapshots")
    if not isinstance(damage_snapshots, list):
        _issue(
            issues,
            stage="vn_process_input",
            path="$.vn_process_input.damage_settlement_snapshots",
            code="list_required",
            message="damage_settlement_snapshots muss eine Liste sein",
        )
        return False, 0

    validated_targets: set[int] = set()
    seen_targets: set[int] = set()
    for index, snapshot in enumerate(damage_snapshots):
        entry_issue_start = len(issues)
        policyholder_id, change_shock = _validate_damage_snapshot(
            snapshot,
            index=index,
            issues=issues,
        )
        if policyholder_id is not None:
            if policyholder_id in seen_targets:
                _issue(
                    issues,
                    stage="vn_process_input",
                    path=(
                        "$.vn_process_input.damage_settlement_snapshots"
                        f"[{index}].policyholder_id"
                    ),
                    code="duplicate_process_target",
                    message="VN-Prozessziel darf nur einmal vorkommen",
                )
            seen_targets.add(policyholder_id)
            if policyholder_id not in policyholder_ids:
                _issue(
                    issues,
                    stage="cross_document",
                    path=(
                        "$.vn_process_input.damage_settlement_snapshots"
                        f"[{index}].policyholder_id"
                    ),
                    code="unknown_process_target",
                    message="VN-Prozessziel ist nicht im Strategieentwurf enthalten",
                )
            expected_shock = context_change_shock.get(policyholder_id)
            if change_shock is not None and expected_shock is not None and (
                change_shock != expected_shock
            ):
                _issue(
                    issues,
                    stage="cross_document",
                    path=(
                        "$.vn_process_input.damage_settlement_snapshots"
                        f"[{index}].change_shock"
                    ),
                    code="change_shock_mismatch",
                    message="VN-Prozessschock stimmt nicht mit dem VN-Kontext ueberein",
                )
        if policyholder_id is not None and len(issues) == entry_issue_start:
            validated_targets.add(policyholder_id)

    if seen_targets != policyholder_ids:
        _issue(
            issues,
            stage="cross_document",
            path="$.vn_process_input.damage_settlement_snapshots",
            code="vn_process_coverage_mismatch",
            message="VN-Prozesseingaenge muessen alle VN-Ziele exakt abdecken",
        )
    return len(issues) == issue_start, len(validated_targets)


def _empty_report(
    *,
    issues: list[StrategyExecutionCandidateValidationIssue],
    submitted_schema_version: str | None = None,
) -> StrategyExecutionCandidateValidationReport:
    return StrategyExecutionCandidateValidationReport(
        valid=False,
        request_shape_valid=False,
        vn_context_valid=False,
        vu_input_valid=False,
        vu_state_valid=False,
        scenario_profile_reference_valid=False,
        vn_process_input_valid=False,
        identifiers_consistent=False,
        submitted_schema_version=submitted_schema_version,
        draft_id=None,
        period=None,
        expected_vu_entry_count=0,
        validated_vu_entry_count=0,
        expected_vn_entry_count=0,
        validated_vn_entry_count=0,
        expected_vn_process_target_count=0,
        validated_vn_process_target_count=0,
        nested_validation_loader_invocation_count=0,
        issues=tuple(issues),
    )


def validate_strategy_execution_candidate_input(
    value: object,
) -> StrategyExecutionCandidateValidationReport:
    """Prueft gemeinsame Kandidatenquellen atomar, ohne Kandidatenbau."""

    issues: list[StrategyExecutionCandidateValidationIssue] = []
    request = _exact_object(
        value,
        _REQUEST_FIELDS,
        path="$",
        noun="Kandidateneingang",
        issues=issues,
    )
    submitted_schema_version = (
        request.get("schema_version")
        if isinstance(request, dict) and isinstance(request.get("schema_version"), str)
        else None
    )
    if request is None:
        return _empty_report(
            issues=issues,
            submitted_schema_version=submitted_schema_version,
        )

    exact_request_values = {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "base_model": "Vdefmd6",
        "scope": "single_period_joint_vu_vn_candidate_input",
    }
    for field_name, expected in exact_request_values.items():
        _require_exact_value(
            request,
            field_name,
            expected,
            path="$",
            issues=issues,
        )
    draft = _exact_object(
        request.get("assignment_draft"),
        frozenset(
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
        ),
        path="$.assignment_draft",
        noun="Strategieentwurf",
        issues=issues,
    )
    context = request.get("snapshot_context")
    if not isinstance(context, dict):
        _issue(
            issues,
            stage="input_contract",
            path="$.snapshot_context",
            code="object_required",
            message="Snapshotkontext muss ein Objekt sein",
        )
    vu_policy = _exact_object(
        request.get("vu_input_policy"),
        _VU_INPUT_POLICY_FIELDS,
        path="$.vu_input_policy",
        noun="VU-Eingabepolicy",
        issues=issues,
    )
    vu_state = request.get("vu_state_provenance")
    if not isinstance(vu_state, dict):
        _issue(
            issues,
            stage="input_contract",
            path="$.vu_state_provenance",
            code="object_required",
            message="VU-Zustandsbeleg muss ein Objekt sein",
        )
    profile = _exact_object(
        request.get("scenario_profile_reference"),
        _PROFILE_FIELDS,
        path="$.scenario_profile_reference",
        noun="Szenarioprofil-Referenz",
        issues=issues,
    )
    process = _exact_object(
        request.get("vn_process_input"),
        _VN_PROCESS_FIELDS,
        path="$.vn_process_input",
        noun="VN-Prozesseingang",
        issues=issues,
    )
    if issues or draft is None or vu_policy is None or profile is None or process is None:
        return _empty_report(
            issues=issues,
            submitted_schema_version=submitted_schema_version,
        )
    assert isinstance(context, dict)
    assert isinstance(vu_state, dict)

    for field_name, expected in {
        "schema_version": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION,
        "threshold_source_policy": VU_THRESHOLD_SOURCE_POLICY_ID,
        "draw_source_policy": VU_DRAW_SOURCE_POLICY_ID,
        "fallback_policy": VU_FALLBACK_POLICY_ID,
    }.items():
        _require_exact_value(
            vu_policy,
            field_name,
            expected,
            path="$.vu_input_policy",
            issues=issues,
        )
    if issues:
        return _empty_report(
            issues=issues,
            submitted_schema_version=submitted_schema_version,
        )

    shared_request = {"draft": draft, "context": context}
    vn_report = validate_strategy_assignment_snapshot_materialization_input(
        shared_request
    )
    vu_input = {
        **vu_policy,
        "draft": draft,
        "context": context,
    }
    vu_report = validate_strategy_assignment_vu_snapshot_materialization_input(
        vu_input
    )
    vu_state_report = validate_strategy_assignment_vu_snapshot_state(
        {"input": vu_input, "state": vu_state}
    )
    _append_existing_issues(
        issues,
        vn_report.issues,
        stage="vn_context",
        source="vn",
    )
    _append_existing_issues(
        issues,
        vu_report.issues,
        stage="vu_input",
        source="vu",
    )
    _append_existing_issues(
        issues,
        vu_state_report.issues,
        stage="vu_state",
        source="vu_state",
    )

    translation = translate_strategy_assignment_draft(draft)
    insurer_ids = {
        entry.assignment.target_id
        for entry in translation.entries
        if entry.assignment.actor_type is StrategyActorType.INSURER
    }
    policyholder_ids = {
        entry.assignment.target_id
        for entry in translation.entries
        if entry.assignment.actor_type is StrategyActorType.POLICYHOLDER
    }
    if not insurer_ids:
        _issue(
            issues,
            stage="cross_document",
            path="$.assignment_draft.assignments",
            code="insurer_assignment_required",
            message="Kandidateneingang benoetigt mindestens eine VU-Zuordnung",
        )
    if not policyholder_ids:
        _issue(
            issues,
            stage="cross_document",
            path="$.assignment_draft.assignments",
            code="policyholder_assignment_required",
            message="Kandidateneingang benoetigt mindestens eine VN-Zuordnung",
        )

    draft_id = vn_report.draft_id if vn_report.draft_id == vu_report.draft_id else None
    period = vn_report.period if vn_report.period == vu_report.period else None
    identifiers_consistent = draft_id is not None and period is not None
    if not identifiers_consistent:
        _issue(
            issues,
            stage="cross_document",
            path="$",
            code="shared_identity_mismatch",
            message="VN- und VU-Pruefung muessen denselben Entwurf und dieselbe Periode liefern",
        )

    profile_valid = _validate_profile_reference(
        profile,
        period=period,
        insurer_ids=insurer_ids,
        policyholder_ids=policyholder_ids,
        issues=issues,
    )
    context_change_shock: dict[int, bool] = {}
    shared_change_shock_values: list[bool] = []
    context_entries = context.get("entries")
    if isinstance(context_entries, list):
        for entry in context_entries:
            if (
                isinstance(entry, dict)
                and entry.get("actor_type") == StrategyActorType.POLICYHOLDER.value
                and isinstance(entry.get("target_id"), int)
                and isinstance(entry.get("values"), dict)
                and isinstance(entry["values"].get("change_shock"), bool)
            ):
                context_change_shock[int(entry["target_id"])] = entry["values"][
                    "change_shock"
                ]
                shared_change_shock_values.append(entry["values"]["change_shock"])
            elif (
                isinstance(entry, dict)
                and isinstance(entry.get("values"), dict)
                and isinstance(entry["values"].get("change_shock"), bool)
            ):
                shared_change_shock_values.append(entry["values"]["change_shock"])
    period_state = vu_state.get("period_state")
    if isinstance(period_state, dict) and isinstance(
        period_state.get("change_shock"), bool
    ):
        shared_change_shock_values.append(period_state["change_shock"])
    if len(set(shared_change_shock_values)) > 1:
        _issue(
            issues,
            stage="cross_document",
            path="$.snapshot_context.entries",
            code="shared_change_shock_mismatch",
            message="VU-, VN- und VU-Zustandsbeleg muessen denselben Schockstatus tragen",
        )
    process_valid, validated_process_targets = _validate_vn_process_input(
        process,
        draft_id=draft_id,
        period=period,
        policyholder_ids=policyholder_ids,
        context_change_shock=context_change_shock,
        issues=issues,
    )

    valid = (
        not issues
        and vn_report.valid
        and vu_report.valid
        and vu_state_report.valid
        and profile_valid
        and process_valid
        and identifiers_consistent
    )
    return StrategyExecutionCandidateValidationReport(
        valid=valid,
        request_shape_valid=True,
        vn_context_valid=vn_report.valid,
        vu_input_valid=vu_report.valid,
        vu_state_valid=vu_state_report.valid,
        scenario_profile_reference_valid=profile_valid,
        vn_process_input_valid=process_valid,
        identifiers_consistent=identifiers_consistent,
        submitted_schema_version=submitted_schema_version,
        draft_id=draft_id,
        period=period,
        expected_vu_entry_count=vu_report.expected_vu_entry_count,
        validated_vu_entry_count=vu_report.validated_vu_entry_count,
        expected_vn_entry_count=vn_report.expected_vn_entry_count,
        validated_vn_entry_count=vn_report.validated_vn_entry_count,
        expected_vn_process_target_count=len(policyholder_ids),
        validated_vn_process_target_count=validated_process_targets,
        nested_validation_loader_invocation_count=(
            vn_report.nested_loader_invocation_count
        ),
        issues=tuple(issues),
    )


def strategy_execution_candidate_validation_contract_payload() -> dict[str, Any]:
    """Beschreibt den PR125-Validator und seine weiterhin geschlossenen Grenzen."""

    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_VALIDATION_VERSION,
        "input_schema_version": STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION,
        "candidate_contract_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_CONTRACT_VERSION
        ),
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "vn_validation_schema_version": (
            STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
        ),
        "vu_state_validation_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION
        ),
        "vu_validation_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
        ),
        "scenario_profile_reference_schema_version": (
            STRATEGY_EXECUTION_SCENARIO_PROFILE_REFERENCE_VERSION
        ),
        "vn_process_input_schema_version": (
            STRATEGY_EXECUTION_VN_PROCESS_INPUT_VERSION
        ),
        "mode": "strategy_execution_candidate_validation_contract",
        "base_model": "Vdefmd6",
        "scope": "atomic_joint_single_period_candidate_input_validation",
        "contract_endpoint": (
            "/api/strategies/execution-candidate-validation-contract"
        ),
        "validation_endpoint": "/api/strategies/execution-candidate-validation",
        "request_fields": tuple(sorted(_REQUEST_FIELDS)),
        "vu_input_policy_fields": tuple(sorted(_VU_INPUT_POLICY_FIELDS)),
        "scenario_profile_reference_fields": tuple(sorted(_PROFILE_FIELDS)),
        "vn_process_input_fields": tuple(sorted(_VN_PROCESS_FIELDS)),
        "vn_damage_snapshot_fields": tuple(sorted(_DAMAGE_SNAPSHOT_FIELDS)),
        "scenario_profile_source_policy": (
            STRATEGY_EXECUTION_SCENARIO_PROFILE_SOURCE_POLICY_ID
        ),
        "vn_process_draw_source_policy": (
            STRATEGY_EXECUTION_VN_PROCESS_DRAW_SOURCE_POLICY_ID
        ),
        "vn_decision_source_policy": (
            STRATEGY_EXECUTION_VN_DECISION_SOURCE_POLICY_ID
        ),
        "vn_information_cost_source_policy": (
            STRATEGY_EXECUTION_VN_INFORMATION_COST_SOURCE_POLICY_ID
        ),
        "validation_order": (
            "validate_exact_candidate_input_shape",
            "validate_vn_context_with_pr115",
            "validate_vu_input_with_pr119",
            "validate_vu_state_with_pr120",
            "cross_check_shared_draft_period_and_expected_population",
            "validate_explicit_vn_damage_process_without_snapshot_loader",
            "accept_only_when_every_source_is_valid",
        ),
        "single_shared_draft_required": True,
        "single_shared_context_required": True,
        "exact_profile_population_reference_required": True,
        "complete_vn_process_target_coverage_required": True,
        "explicit_vn_damage_draws_required": True,
        "settlement_only_snapshots_allowed": False,
        "partial_acceptance_allowed": False,
        "partial_candidate_returned": False,
        "nested_validation_loader_invocation_enabled": True,
        "nested_validation_loader_results_retained": False,
        "snapshot_loader_invocation_enabled": False,
        "scenario_profile_resolution_enabled": False,
        "server_side_rematerialization_enabled": False,
        "digest_calculation_enabled": False,
        "candidate_creation_enabled": False,
        "candidate_persistence_enabled": False,
        "run_control_enabled": False,
        "runner_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
