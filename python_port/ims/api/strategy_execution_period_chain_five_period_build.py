from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from ims.api.strategy_execution_period_chain_build import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION,
    StrategyExecutionPeriodChain,
    StrategyExecutionPeriodChainBuildIssue,
    build_strategy_execution_period_chain,
    calculate_strategy_execution_period_chain_content_digest,
    strategy_execution_period_chain_id_from_digest,
)
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)
from ims.strategies.execution_period_chain_bounded_runner_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_BOUNDED_RUNNER_CONTRACT_VERSION,
)
from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)
from ims.strategies.execution_period_chain_validation import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
    StrategyExecutionPeriodChainValidationReport,
    validate_strategy_execution_period_chain_input,
)


STRATEGY_EXECUTION_FIVE_PERIOD_CHAIN_BUILD_CONTRACT_VERSION = (
    "ims.strategy-execution-five-period-chain-build-contract.v1"
)
STRATEGY_EXECUTION_FIVE_PERIOD_CHAIN_BUILD_VERSION = (
    "ims.strategy-execution-five-period-chain-build.v1"
)
FIVE_PERIOD_CHAIN_PERIOD_COUNT = 5
FIVE_PERIOD_CHAIN_TRANSITION_COUNT = 4


@dataclass(frozen=True, slots=True)
class StrategyExecutionFivePeriodChainBuildReport:
    input_validated: bool
    candidate_resolution_ready: bool
    canonical_chain_validated: bool
    resolved_candidate_count: int
    validated_transition_count: int
    chain: StrategyExecutionPeriodChain | None
    issues: tuple[StrategyExecutionPeriodChainBuildIssue, ...]
    schema_version: str = STRATEGY_EXECUTION_FIVE_PERIOD_CHAIN_BUILD_VERSION
    mode: str = "strategy_execution_five_period_chain_build"

    @property
    def build_complete(self) -> bool:
        return (
            self.input_validated
            and self.candidate_resolution_ready
            and self.canonical_chain_validated
            and self.resolved_candidate_count == FIVE_PERIOD_CHAIN_PERIOD_COUNT
            and self.validated_transition_count
            == FIVE_PERIOD_CHAIN_TRANSITION_COUNT
            and self.chain is not None
            and not self.issues
        )

    def to_dict(self) -> dict[str, object]:
        chain_created = self.build_complete and self.chain is not None
        return {
            "schema_version": self.schema_version,
            "input_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
            "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
            "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
            "generic_build_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION
            ),
            "bounded_runner_contract_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_BOUNDED_RUNNER_CONTRACT_VERSION
            ),
            "mode": self.mode,
            "status": "ready" if self.build_complete else "blocked",
            "build_complete": self.build_complete,
            "input_validated": self.input_validated,
            "five_period_horizon_validated": self.input_validated,
            "candidate_resolution_ready": self.candidate_resolution_ready,
            "canonical_chain_validated": self.canonical_chain_validated,
            "expected_candidate_count": FIVE_PERIOD_CHAIN_PERIOD_COUNT,
            "resolved_candidate_count": self.resolved_candidate_count,
            "expected_transition_count": FIVE_PERIOD_CHAIN_TRANSITION_COUNT,
            "validated_transition_count": self.validated_transition_count,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "period_chain": self.chain.to_dict() if chain_created else None,
            "partial_chain_returned": False,
            "candidate_storage_resolved": self.candidate_resolution_ready,
            "candidate_content_digest_reverified": (
                self.candidate_resolution_ready
            ),
            "candidate_context_cross_checked": self.candidate_resolution_ready,
            "actor_identity_cross_checked": self.candidate_resolution_ready,
            "period_chain_created": chain_created,
            "period_chain_digest_recalculated": (
                self.canonical_chain_validated
            ),
            "period_chain_persisted": False,
            "carryover_invocation_performed": False,
            "runner_invocation_performed": False,
            "writes_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR147",
        }


def build_strategy_execution_five_period_chain(
    value: object,
    *,
    db_path: Path | str,
) -> StrategyExecutionFivePeriodChainBuildReport:
    """Baut und prueft genau fuenf Perioden, ohne sie auszufuehren."""

    validation = validate_strategy_execution_period_chain_input(value)
    if not validation.valid:
        return _blocked_from_validation(validation)
    if validation.max_periods != FIVE_PERIOD_CHAIN_PERIOD_COUNT:
        return _five_period_horizon_blocked(validation)

    generic = build_strategy_execution_period_chain(value, db_path=db_path)
    if not generic.build_complete or generic.chain is None:
        return StrategyExecutionFivePeriodChainBuildReport(
            input_validated=generic.input_validated,
            candidate_resolution_ready=generic.candidate_resolution_ready,
            canonical_chain_validated=False,
            resolved_candidate_count=generic.resolved_candidate_count,
            validated_transition_count=FIVE_PERIOD_CHAIN_TRANSITION_COUNT,
            chain=None,
            issues=generic.issues,
        )

    canonical_issues = _canonical_five_period_chain_issues(generic.chain)
    if canonical_issues:
        return StrategyExecutionFivePeriodChainBuildReport(
            input_validated=True,
            candidate_resolution_ready=True,
            canonical_chain_validated=False,
            resolved_candidate_count=generic.resolved_candidate_count,
            validated_transition_count=FIVE_PERIOD_CHAIN_TRANSITION_COUNT,
            chain=None,
            issues=canonical_issues,
        )

    return StrategyExecutionFivePeriodChainBuildReport(
        input_validated=True,
        candidate_resolution_ready=True,
        canonical_chain_validated=True,
        resolved_candidate_count=generic.resolved_candidate_count,
        validated_transition_count=FIVE_PERIOD_CHAIN_TRANSITION_COUNT,
        chain=generic.chain,
        issues=(),
    )


def _blocked_from_validation(
    validation: StrategyExecutionPeriodChainValidationReport,
) -> StrategyExecutionFivePeriodChainBuildReport:
    return StrategyExecutionFivePeriodChainBuildReport(
        input_validated=False,
        candidate_resolution_ready=False,
        canonical_chain_validated=False,
        resolved_candidate_count=0,
        validated_transition_count=validation.validated_transition_count,
        chain=None,
        issues=tuple(
            StrategyExecutionPeriodChainBuildIssue(
                stage=issue.stage,
                path=issue.path,
                code=issue.code,
                message=issue.message,
            )
            for issue in validation.issues
        ),
    )


def _five_period_horizon_blocked(
    validation: StrategyExecutionPeriodChainValidationReport,
) -> StrategyExecutionFivePeriodChainBuildReport:
    return StrategyExecutionFivePeriodChainBuildReport(
        input_validated=False,
        candidate_resolution_ready=False,
        canonical_chain_validated=False,
        resolved_candidate_count=0,
        validated_transition_count=validation.validated_transition_count,
        chain=None,
        issues=(
            StrategyExecutionPeriodChainBuildIssue(
                stage="five_period_horizon",
                path="$.max_periods",
                code="exact_five_period_horizon_required",
                message="PR143 akzeptiert genau den Horizont 1 bis 5",
            ),
        ),
    )


def _canonical_five_period_chain_issues(
    chain: StrategyExecutionPeriodChain,
) -> tuple[StrategyExecutionPeriodChainBuildIssue, ...]:
    issues: list[StrategyExecutionPeriodChainBuildIssue] = []
    sections = chain.sections
    horizon = sections.get("horizon")
    run_index = horizon.get("run_index") if isinstance(horizon, dict) else None
    expected_horizon = {
        "first_period": 1,
        "last_period": FIVE_PERIOD_CHAIN_PERIOD_COUNT,
        "period_count": FIVE_PERIOD_CHAIN_PERIOD_COUNT,
        "run_index": run_index,
        "max_periods": FIVE_PERIOD_CHAIN_PERIOD_COUNT,
    }
    if horizon != expected_horizon:
        _canonical_issue(
            issues,
            path="$.horizon",
            code="five_period_horizon_not_canonical",
            message="Kanonischer Horizont muss vollstaendig von 1 bis 5 reichen",
        )

    candidates = sections.get("period_candidates")
    candidate_periods = (
        [item.get("period") for item in candidates if isinstance(item, dict)]
        if isinstance(candidates, list)
        else []
    )
    if candidate_periods != list(range(1, FIVE_PERIOD_CHAIN_PERIOD_COUNT + 1)):
        _canonical_issue(
            issues,
            path="$.period_candidates",
            code="five_period_candidates_not_canonical",
            message=(
                "Kanonische Kandidaten muessen geordnet die Perioden 1 bis 5 "
                "abbilden"
            ),
        )

    transitions = sections.get("transitions")
    transition_pairs = (
        [
            (item.get("from_period"), item.get("to_period"))
            for item in transitions
            if isinstance(item, dict)
        ]
        if isinstance(transitions, list)
        else []
    )
    if transition_pairs != [(period, period + 1) for period in range(1, 5)]:
        _canonical_issue(
            issues,
            path="$.transitions",
            code="five_period_transitions_not_canonical",
            message="Kanonische Uebergaenge muessen lueckenlos von 1 nach 5 reichen",
        )

    try:
        recalculated_digest = (
            calculate_strategy_execution_period_chain_content_digest(
                sections=sections
            )
        )
        recalculated_id = strategy_execution_period_chain_id_from_digest(
            recalculated_digest
        )
    except (TypeError, ValueError, OverflowError) as exc:
        _canonical_issue(
            issues,
            path="$",
            code="five_period_chain_not_canonicalizable",
            message=str(exc),
        )
    else:
        if recalculated_digest != chain.content_digest:
            _canonical_issue(
                issues,
                path="$.identity.content_digest",
                code="five_period_chain_digest_mismatch",
                message="Neu berechneter Kettendigest weicht vom Ergebnis ab",
            )
        if recalculated_id != chain.chain_id:
            _canonical_issue(
                issues,
                path="$.identity.chain_id",
                code="five_period_chain_id_mismatch",
                message="Ketten-ID passt nicht zum neu berechneten Digest",
            )
    return tuple(issues)


def _canonical_issue(
    issues: list[StrategyExecutionPeriodChainBuildIssue],
    *,
    path: str,
    code: str,
    message: str,
) -> None:
    issues.append(
        StrategyExecutionPeriodChainBuildIssue(
            stage="five_period_canonical_validation",
            path=path,
            code=code,
            message=message,
        )
    )


def strategy_execution_five_period_chain_build_contract_payload() -> dict[
    str, object
]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_FIVE_PERIOD_CHAIN_BUILD_CONTRACT_VERSION
        ),
        "build_schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_CHAIN_BUILD_VERSION,
        "generic_build_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION,
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "bounded_runner_contract_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_BOUNDED_RUNNER_CONTRACT_VERSION
        ),
        "mode": "strategy_execution_five_period_chain_build_contract",
        "scope": "exact_five_period_ephemeral_canonical_chain_build",
        "contract_endpoint": (
            "/api/strategies/execution-period-chain-five-period-build-contract"
        ),
        "build_endpoint": (
            "/api/strategies/execution-period-chain-five-period-build"
        ),
        "required_period_count": FIVE_PERIOD_CHAIN_PERIOD_COUNT,
        "required_transition_count": FIVE_PERIOD_CHAIN_TRANSITION_COUNT,
        "required_periods": [1, 2, 3, 4, 5],
        "required_transition_pairs": [[1, 2], [2, 3], [3, 4], [4, 5]],
        "validation_order": [
            "validate_exact_pr134_input_shape",
            "require_exact_horizon_1_to_5",
            "resolve_all_five_stored_candidates",
            "reverify_all_candidate_digests_contexts_and_actor_identities",
            "build_generic_canonical_chain",
            "recalculate_complete_chain_digest_and_identity",
            "return_complete_ephemeral_chain_or_no_chain",
        ],
        "atomic_validation_enabled": True,
        "five_period_candidate_validation_enabled": True,
        "five_period_chain_build_enabled": True,
        "five_period_chain_digest_enabled": True,
        "partial_chain_allowed": False,
        "period_chain_persistence_enabled": False,
        "carryover_invocation_enabled": False,
        "runner_enabled": False,
        "ui_start_enabled": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR147",
    }


def strategy_execution_five_period_chain_build_error_payload(
    code: str,
    message: str,
) -> dict[str, object]:
    report = StrategyExecutionFivePeriodChainBuildReport(
        input_validated=False,
        candidate_resolution_ready=False,
        canonical_chain_validated=False,
        resolved_candidate_count=0,
        validated_transition_count=0,
        chain=None,
        issues=(
            StrategyExecutionPeriodChainBuildIssue(
                stage="input_contract",
                path="$",
                code=code,
                message=message,
            ),
        ),
    )
    payload = report.to_dict()
    payload["status"] = "error"
    return payload
