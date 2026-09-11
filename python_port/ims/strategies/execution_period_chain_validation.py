from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

from ims.strategies.execution_candidate_build import (
    strategy_execution_candidate_id_from_digest,
)
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)
from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)


STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION = (
    "ims.strategy-execution-period-chain-input.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_VALIDATION_VERSION = (
    "ims.strategy-execution-period-chain-validation.v1"
)

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "period_chain_schema_version",
        "candidate_schema_version",
        "base_model",
        "scope",
        "run_index",
        "max_periods",
        "period_candidates",
        "transitions",
    }
)
_CANDIDATE_REFERENCE_FIELDS = frozenset(
    {"candidate_id", "content_digest", "period"}
)
_TRANSITION_FIELDS = frozenset(
    {
        "from_period",
        "to_period",
        "carry_forward_vu_state",
        "carry_forward_vn_state",
    }
)
_DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
_CANDIDATE_ID_PATTERN = re.compile(r"strategy-candidate-[0-9a-f]{24}\Z")


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainValidationIssue:
    stage: str
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainValidationReport:
    valid: bool
    request_shape_valid: bool
    horizon_valid: bool
    candidate_references_valid: bool
    transitions_valid: bool
    identifiers_consistent: bool
    submitted_schema_version: str | None
    run_index: int | None
    max_periods: int | None
    first_period: int | None
    last_period: int | None
    expected_candidate_count: int
    validated_candidate_count: int
    expected_transition_count: int
    validated_transition_count: int
    vu_carryover_transition_count: int
    vn_carryover_transition_count: int
    issues: tuple[StrategyExecutionPeriodChainValidationIssue, ...]
    schema_version: str = STRATEGY_EXECUTION_PERIOD_CHAIN_VALIDATION_VERSION
    mode: str = "strategy_execution_period_chain_validation"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "input_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
            "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
            "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
            "mode": self.mode,
            "status": "ok" if self.valid else "error",
            "valid": self.valid,
            "request_shape_valid": self.request_shape_valid,
            "horizon_valid": self.horizon_valid,
            "candidate_references_valid": self.candidate_references_valid,
            "transitions_valid": self.transitions_valid,
            "identifiers_consistent": self.identifiers_consistent,
            "submitted_schema_version": self.submitted_schema_version,
            "run_index": self.run_index,
            "max_periods": self.max_periods,
            "first_period": self.first_period,
            "last_period": self.last_period,
            "expected_candidate_count": self.expected_candidate_count,
            "validated_candidate_count": self.validated_candidate_count,
            "expected_transition_count": self.expected_transition_count,
            "validated_transition_count": self.validated_transition_count,
            "vu_carryover_transition_count": self.vu_carryover_transition_count,
            "vn_carryover_transition_count": self.vn_carryover_transition_count,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "partial_chain_returned": False,
            "candidate_reference_digest_identity_checked": True,
            "candidate_storage_resolved": False,
            "candidate_content_digest_reverified": False,
            "candidate_context_cross_checked": False,
            "period_chain_created": False,
            "period_chain_persisted": False,
            "source_values_consumed": False,
            "carryover_invocation_performed": False,
            "runner_invocation_performed": False,
            "writes_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR140",
        }


def _issue(
    issues: list[StrategyExecutionPeriodChainValidationIssue],
    *,
    stage: str,
    path: str,
    code: str,
    message: str,
) -> None:
    issues.append(
        StrategyExecutionPeriodChainValidationIssue(
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
    issues: list[StrategyExecutionPeriodChainValidationIssue],
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
    issues: list[StrategyExecutionPeriodChainValidationIssue],
) -> None:
    if value.get(field_name) != expected:
        _issue(
            issues,
            stage="input_contract",
            path=f"{path}.{field_name}",
            code="contract_value_mismatch",
            message=f"{field_name} muss {expected!r} sein",
        )


def _integer(
    value: object,
    *,
    minimum: int,
    maximum: int | None,
    path: str,
    noun: str,
    issues: list[StrategyExecutionPeriodChainValidationIssue],
) -> int | None:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < minimum
        or (maximum is not None and value > maximum)
    ):
        limit = (
            f" zwischen {minimum} und {maximum}"
            if maximum is not None
            else f" groesser oder gleich {minimum}"
        )
        _issue(
            issues,
            stage="horizon",
            path=path,
            code="integer_range_required",
            message=f"{noun} muss eine Ganzzahl{limit} sein",
        )
        return None
    return value


def _boolean(
    value: object,
    *,
    path: str,
    issues: list[StrategyExecutionPeriodChainValidationIssue],
) -> bool | None:
    if not isinstance(value, bool):
        _issue(
            issues,
            stage="transition",
            path=path,
            code="boolean_required",
            message="Carryover-Schalter muss explizit boolesch sein",
        )
        return None
    return value


def _validate_candidate_references(
    value: object,
    *,
    max_periods: int | None,
    issues: list[StrategyExecutionPeriodChainValidationIssue],
) -> tuple[list[int], int, bool]:
    if not isinstance(value, list):
        _issue(
            issues,
            stage="input_contract",
            path="$.period_candidates",
            code="list_required",
            message="period_candidates muss eine Liste sein",
        )
        return [], 0, False

    periods: list[int] = []
    candidate_ids: set[str] = set()
    content_digests: set[str] = set()
    validated_count = 0
    identifiers_consistent = True
    for index, item in enumerate(value):
        path = f"$.period_candidates[{index}]"
        issue_start = len(issues)
        reference = _exact_object(
            item,
            _CANDIDATE_REFERENCE_FIELDS,
            path=path,
            noun="Periodenkandidatenreferenz",
            issues=issues,
        )
        if reference is None:
            identifiers_consistent = False
            continue

        period = _integer(
            reference.get("period"),
            minimum=1,
            maximum=100,
            path=f"{path}.period",
            noun="Kandidatenperiode",
            issues=issues,
        )
        if period is not None:
            periods.append(period)

        candidate_id = reference.get("candidate_id")
        candidate_id_valid = (
            isinstance(candidate_id, str)
            and _CANDIDATE_ID_PATTERN.fullmatch(candidate_id) is not None
        )
        if not candidate_id_valid:
            identifiers_consistent = False
            _issue(
                issues,
                stage="candidate_reference",
                path=f"{path}.candidate_id",
                code="candidate_id_invalid",
                message="Kandidaten-ID entspricht nicht dem gespeicherten Format",
            )

        content_digest = reference.get("content_digest")
        digest_valid = (
            isinstance(content_digest, str)
            and _DIGEST_PATTERN.fullmatch(content_digest) is not None
        )
        if not digest_valid:
            identifiers_consistent = False
            _issue(
                issues,
                stage="candidate_reference",
                path=f"{path}.content_digest",
                code="content_digest_invalid",
                message="Kandidatendigest muss ein kleingeschriebener SHA-256-Digest sein",
            )

        if candidate_id_valid and digest_valid:
            assert isinstance(candidate_id, str)
            assert isinstance(content_digest, str)
            if candidate_id != strategy_execution_candidate_id_from_digest(
                content_digest
            ):
                identifiers_consistent = False
                _issue(
                    issues,
                    stage="candidate_reference",
                    path=path,
                    code="candidate_digest_identity_mismatch",
                    message="Kandidaten-ID passt nicht zum angegebenen Digest",
                )
            if candidate_id in candidate_ids:
                identifiers_consistent = False
                _issue(
                    issues,
                    stage="candidate_reference",
                    path=f"{path}.candidate_id",
                    code="duplicate_candidate_id",
                    message="Kandidaten-ID darf in der Kette nur einmal vorkommen",
                )
            if content_digest in content_digests:
                identifiers_consistent = False
                _issue(
                    issues,
                    stage="candidate_reference",
                    path=f"{path}.content_digest",
                    code="duplicate_content_digest",
                    message="Kandidatendigest darf in der Kette nur einmal vorkommen",
                )
            candidate_ids.add(candidate_id)
            content_digests.add(content_digest)

        if len(issues) == issue_start:
            validated_count += 1

    if max_periods is not None and len(value) != max_periods:
        _issue(
            issues,
            stage="horizon",
            path="$.period_candidates",
            code="candidate_count_mismatch",
            message="Kandidatenanzahl muss dem vollstaendigen max_periods-Horizont entsprechen",
        )
    expected_periods = (
        list(range(1, max_periods + 1)) if max_periods is not None else None
    )
    if expected_periods is not None and periods != expected_periods:
        _issue(
            issues,
            stage="horizon",
            path="$.period_candidates",
            code="period_sequence_mismatch",
            message="Kandidatenperioden muessen lueckenlos und geordnet von 1 bis max_periods reichen",
        )
    return periods, validated_count, identifiers_consistent


def _validate_transitions(
    value: object,
    *,
    max_periods: int | None,
    issues: list[StrategyExecutionPeriodChainValidationIssue],
) -> tuple[int, int, int]:
    if not isinstance(value, list):
        _issue(
            issues,
            stage="input_contract",
            path="$.transitions",
            code="list_required",
            message="transitions muss eine Liste sein",
        )
        return 0, 0, 0

    validated_count = 0
    vu_count = 0
    vn_count = 0
    for index, item in enumerate(value):
        path = f"$.transitions[{index}]"
        issue_start = len(issues)
        transition = _exact_object(
            item,
            _TRANSITION_FIELDS,
            path=path,
            noun="Periodenuebergang",
            issues=issues,
        )
        if transition is None:
            continue

        from_period = _integer(
            transition.get("from_period"),
            minimum=1,
            maximum=99,
            path=f"{path}.from_period",
            noun="Quellperiode",
            issues=issues,
        )
        to_period = _integer(
            transition.get("to_period"),
            minimum=2,
            maximum=100,
            path=f"{path}.to_period",
            noun="Zielperiode",
            issues=issues,
        )
        vu_carryover = _boolean(
            transition.get("carry_forward_vu_state"),
            path=f"{path}.carry_forward_vu_state",
            issues=issues,
        )
        vn_carryover = _boolean(
            transition.get("carry_forward_vn_state"),
            path=f"{path}.carry_forward_vn_state",
            issues=issues,
        )
        if from_period is not None and to_period is not None and (
            to_period != from_period + 1
        ):
            _issue(
                issues,
                stage="transition",
                path=path,
                code="non_adjacent_transition",
                message="Periodenuebergang muss genau von t nach t+1 fuehren",
            )
        expected_from = index + 1
        expected_to = index + 2
        if (
            max_periods is not None
            and index < max_periods - 1
            and (from_period, to_period) != (expected_from, expected_to)
        ):
            _issue(
                issues,
                stage="cross_reference",
                path=path,
                code="transition_sequence_mismatch",
                message="Uebergang stimmt nicht mit seiner Kandidatenposition ueberein",
            )
        if vu_carryover is True:
            vu_count += 1
        if vn_carryover is True:
            vn_count += 1
        if len(issues) == issue_start:
            validated_count += 1

    expected_count = max_periods - 1 if max_periods is not None else None
    if expected_count is not None and len(value) != expected_count:
        _issue(
            issues,
            stage="horizon",
            path="$.transitions",
            code="transition_count_mismatch",
            message="Uebergangsanzahl muss max_periods minus eins entsprechen",
        )
    return validated_count, vu_count, vn_count


def validate_strategy_execution_period_chain_input(
    value: object,
) -> StrategyExecutionPeriodChainValidationReport:
    """Prueft einen vollstaendigen Ketteneingang atomar und ohne Aufloesung."""

    issues: list[StrategyExecutionPeriodChainValidationIssue] = []
    request = _exact_object(
        value,
        _REQUEST_FIELDS,
        path="$",
        noun="Periodenkettendokument",
        issues=issues,
    )
    submitted_schema_version = (
        request.get("schema_version")
        if isinstance(request, dict) and isinstance(request.get("schema_version"), str)
        else None
    )
    if request is None:
        return _report(
            issues=issues,
            submitted_schema_version=submitted_schema_version,
        )

    for field_name, expected in {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "base_model": "Vdefmd6",
        "scope": "contiguous_local_period_chain_input",
    }.items():
        _require_exact_value(
            request,
            field_name,
            expected,
            path="$",
            issues=issues,
        )

    run_index = _integer(
        request.get("run_index"),
        minimum=0,
        maximum=None,
        path="$.run_index",
        noun="run_index",
        issues=issues,
    )
    max_periods = _integer(
        request.get("max_periods"),
        minimum=2,
        maximum=100,
        path="$.max_periods",
        noun="max_periods",
        issues=issues,
    )
    candidate_issue_start = len(issues)
    periods, validated_candidates, identifiers_consistent = (
        _validate_candidate_references(
            request.get("period_candidates"),
            max_periods=max_periods,
            issues=issues,
        )
    )
    candidate_references_valid = (
        len(issues) == candidate_issue_start and identifiers_consistent
    )
    transition_issue_start = len(issues)
    validated_transitions, vu_count, vn_count = _validate_transitions(
        request.get("transitions"),
        max_periods=max_periods,
        issues=issues,
    )
    transitions_valid = len(issues) == transition_issue_start
    request_shape_valid = not any(
        issue.stage == "input_contract" for issue in issues
    )
    horizon_valid = (
        run_index is not None
        and max_periods is not None
        and periods == list(range(1, max_periods + 1))
        and not any(issue.stage == "horizon" for issue in issues)
    )
    valid = (
        not issues
        and request_shape_valid
        and horizon_valid
        and candidate_references_valid
        and transitions_valid
        and identifiers_consistent
    )
    return _report(
        issues=issues,
        submitted_schema_version=submitted_schema_version,
        valid=valid,
        request_shape_valid=request_shape_valid,
        horizon_valid=horizon_valid,
        candidate_references_valid=candidate_references_valid,
        transitions_valid=transitions_valid,
        identifiers_consistent=identifiers_consistent,
        run_index=run_index,
        max_periods=max_periods,
        periods=periods,
        validated_candidate_count=validated_candidates,
        validated_transition_count=validated_transitions,
        vu_carryover_transition_count=vu_count,
        vn_carryover_transition_count=vn_count,
    )


def _report(
    *,
    issues: list[StrategyExecutionPeriodChainValidationIssue],
    submitted_schema_version: str | None,
    valid: bool = False,
    request_shape_valid: bool = False,
    horizon_valid: bool = False,
    candidate_references_valid: bool = False,
    transitions_valid: bool = False,
    identifiers_consistent: bool = False,
    run_index: int | None = None,
    max_periods: int | None = None,
    periods: list[int] | None = None,
    validated_candidate_count: int = 0,
    validated_transition_count: int = 0,
    vu_carryover_transition_count: int = 0,
    vn_carryover_transition_count: int = 0,
) -> StrategyExecutionPeriodChainValidationReport:
    actual_periods = periods or []
    expected_candidate_count = max_periods or 0
    expected_transition_count = max_periods - 1 if max_periods is not None else 0
    return StrategyExecutionPeriodChainValidationReport(
        valid=valid,
        request_shape_valid=request_shape_valid,
        horizon_valid=horizon_valid,
        candidate_references_valid=candidate_references_valid,
        transitions_valid=transitions_valid,
        identifiers_consistent=identifiers_consistent,
        submitted_schema_version=submitted_schema_version,
        run_index=run_index,
        max_periods=max_periods,
        first_period=actual_periods[0] if actual_periods else None,
        last_period=actual_periods[-1] if actual_periods else None,
        expected_candidate_count=expected_candidate_count,
        validated_candidate_count=validated_candidate_count,
        expected_transition_count=expected_transition_count,
        validated_transition_count=validated_transition_count,
        vu_carryover_transition_count=vu_carryover_transition_count,
        vn_carryover_transition_count=vn_carryover_transition_count,
        issues=tuple(issues),
    )


def strategy_execution_period_chain_validation_contract_payload() -> dict[str, Any]:
    """Beschreibt den PR134-Validator und seine geschlossenen Laufzeitgrenzen."""

    return {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VALIDATION_VERSION,
        "input_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
        "period_chain_contract_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_period_chain_validation_contract",
        "base_model": "Vdefmd6",
        "scope": "atomic_contiguous_local_period_chain_input_validation",
        "contract_endpoint": (
            "/api/strategies/execution-period-chain-validation-contract"
        ),
        "validation_endpoint": (
            "/api/strategies/execution-period-chain-validation"
        ),
        "request_fields": tuple(sorted(_REQUEST_FIELDS)),
        "candidate_reference_fields": tuple(
            sorted(_CANDIDATE_REFERENCE_FIELDS)
        ),
        "transition_fields": tuple(sorted(_TRANSITION_FIELDS)),
        "validation_order": (
            "validate_exact_chain_input_shape_and_versions",
            "validate_run_index_and_complete_horizon_1_to_max_periods",
            "validate_unique_candidate_id_digest_period_references",
            "validate_candidate_id_matches_digest",
            "validate_exact_adjacent_transition_sequence",
            "accept_only_when_complete_chain_is_valid",
        ),
        "minimum_period_count": 2,
        "maximum_period_count": 100,
        "first_local_period": 1,
        "complete_horizon_required": True,
        "explicit_carryover_flags_required": True,
        "candidate_reference_digest_identity_check_enabled": True,
        "partial_acceptance_allowed": False,
        "partial_chain_returned": False,
        "candidate_storage_resolution_enabled": False,
        "candidate_content_digest_reverification_enabled": False,
        "candidate_context_cross_check_enabled": False,
        "period_chain_creation_enabled": False,
        "period_chain_persistence_enabled": False,
        "carryover_invocation_enabled": False,
        "runner_enabled": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR140",
    }
