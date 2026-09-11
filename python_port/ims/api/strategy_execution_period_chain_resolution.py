from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from ims.api.strategy_execution_candidate_store import (
    StrategyExecutionCandidateStoreError,
    StrategyExecutionCandidateStoreRecord,
    get_strategy_execution_candidate,
)
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)
from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)
from ims.strategies.execution_period_chain_validation import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_VALIDATION_VERSION,
    validate_strategy_execution_period_chain_input,
)


STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_CONTRACT_VERSION = (
    "ims.strategy-execution-period-chain-resolution-contract.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_VERSION = (
    "ims.strategy-execution-period-chain-resolution.v1"
)


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainResolutionIssue:
    stage: str
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainResolvedCandidate:
    candidate_id: str
    content_digest: str
    period: int
    draft_id: str
    profile_id: str
    profile_content_digest: str
    context_run_index: int
    context_max_periods: int
    bav_id: int
    insurer_ids: tuple[int, ...]
    policyholder_ids: tuple[int, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "content_digest": self.content_digest,
            "period": self.period,
            "draft_id": self.draft_id,
            "profile_id": self.profile_id,
            "profile_content_digest": self.profile_content_digest,
            "context_run_index": self.context_run_index,
            "context_max_periods": self.context_max_periods,
            "bav_id": self.bav_id,
            "insurer_ids": list(self.insurer_ids),
            "policyholder_ids": list(self.policyholder_ids),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainResolutionReport:
    input_validated: bool
    resolution_complete: bool
    digests_reverified: bool
    contexts_consistent: bool
    actor_identities_consistent: bool
    run_index: int | None
    max_periods: int | None
    expected_candidate_count: int
    resolved_candidate_count: int
    digest_verified_candidate_count: int
    context_verified_candidate_count: int
    candidates: tuple[StrategyExecutionPeriodChainResolvedCandidate, ...]
    issues: tuple[StrategyExecutionPeriodChainResolutionIssue, ...]
    schema_version: str = STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_VERSION
    mode: str = "strategy_execution_period_chain_resolution"

    @property
    def resolution_ready(self) -> bool:
        return (
            self.input_validated
            and self.resolution_complete
            and self.digests_reverified
            and self.contexts_consistent
            and self.actor_identities_consistent
            and not self.issues
            and len(self.candidates) == self.expected_candidate_count
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "input_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
            "input_validation_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_VALIDATION_VERSION
            ),
            "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
            "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
            "mode": self.mode,
            "status": "ready" if self.resolution_ready else "blocked",
            "resolution_ready": self.resolution_ready,
            "input_validated": self.input_validated,
            "resolution_complete": self.resolution_complete,
            "digests_reverified": self.digests_reverified,
            "contexts_consistent": self.contexts_consistent,
            "actor_identities_consistent": self.actor_identities_consistent,
            "run_index": self.run_index,
            "max_periods": self.max_periods,
            "expected_candidate_count": self.expected_candidate_count,
            "resolved_candidate_count": self.resolved_candidate_count,
            "digest_verified_candidate_count": (
                self.digest_verified_candidate_count
            ),
            "context_verified_candidate_count": (
                self.context_verified_candidate_count
            ),
            "candidate_count": (
                len(self.candidates) if self.resolution_ready else 0
            ),
            "candidates": (
                [candidate.to_dict() for candidate in self.candidates]
                if self.resolution_ready
                else []
            ),
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "partial_resolution_returned": False,
            "partial_chain_returned": False,
            "candidate_storage_resolved": self.resolution_complete,
            "candidate_content_digest_reverified": self.digests_reverified,
            "candidate_context_cross_checked": self.contexts_consistent,
            "actor_identity_cross_checked": self.actor_identities_consistent,
            "period_chain_created": False,
            "period_chain_digest_calculated": False,
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


def resolve_strategy_execution_period_chain_input(
    value: object,
    *,
    db_path: Path | str,
) -> StrategyExecutionPeriodChainResolutionReport:
    """Loest einen gueltigen PR134-Eingang read-only und atomar auf."""

    input_report = validate_strategy_execution_period_chain_input(value)
    if not input_report.valid:
        return StrategyExecutionPeriodChainResolutionReport(
            input_validated=False,
            resolution_complete=False,
            digests_reverified=False,
            contexts_consistent=False,
            actor_identities_consistent=False,
            run_index=input_report.run_index,
            max_periods=input_report.max_periods,
            expected_candidate_count=input_report.expected_candidate_count,
            resolved_candidate_count=0,
            digest_verified_candidate_count=0,
            context_verified_candidate_count=0,
            candidates=(),
            issues=tuple(
                StrategyExecutionPeriodChainResolutionIssue(
                    stage="input_validation",
                    path=issue.path,
                    code=issue.code,
                    message=issue.message,
                )
                for issue in input_report.issues
            ),
        )

    assert isinstance(value, dict)
    run_index = input_report.run_index
    max_periods = input_report.max_periods
    assert run_index is not None
    assert max_periods is not None
    references = value["period_candidates"]
    assert isinstance(references, list)

    issues: list[StrategyExecutionPeriodChainResolutionIssue] = []
    resolved_count = 0
    digest_verified_count = 0
    context_verified_count = 0
    candidates: list[StrategyExecutionPeriodChainResolvedCandidate] = []
    baseline_actor_identity: tuple[int, tuple[int, ...], tuple[int, ...]] | None = (
        None
    )

    for index, reference_value in enumerate(references):
        assert isinstance(reference_value, dict)
        path = f"$.period_candidates[{index}]"
        candidate_id = str(reference_value["candidate_id"])
        expected_digest = str(reference_value["content_digest"])
        expected_period = int(reference_value["period"])
        try:
            stored = get_strategy_execution_candidate(
                candidate_id,
                db_path=db_path,
            )
        except StrategyExecutionCandidateStoreError as exc:
            _issue(
                issues,
                stage="candidate_resolution",
                path=path,
                code=exc.code,
                message=str(exc),
            )
            continue

        resolved_count += 1
        record = stored.record
        reference_valid = _validate_resolved_reference(
            record,
            candidate_id=candidate_id,
            expected_digest=expected_digest,
            expected_period=expected_period,
            path=path,
            issues=issues,
        )
        if reference_valid and stored.post_storage_digest_verified:
            digest_verified_count += 1

        context = _resolved_candidate_context(
            record,
            expected_period=expected_period,
            expected_run_index=run_index,
            expected_max_periods=max_periods,
            path=path,
            issues=issues,
        )
        if context is None:
            continue
        context_verified_count += 1
        actor_identity = (
            context.bav_id,
            context.insurer_ids,
            context.policyholder_ids,
        )
        if baseline_actor_identity is None:
            baseline_actor_identity = actor_identity
        else:
            _validate_actor_identity(
                actor_identity,
                baseline_actor_identity,
                path=path,
                issues=issues,
            )
        candidates.append(
            StrategyExecutionPeriodChainResolvedCandidate(
                candidate_id=record.candidate_id,
                content_digest=record.content_digest,
                period=record.period,
                draft_id=record.draft_id,
                profile_id=record.profile_id,
                profile_content_digest=record.profile_content_digest,
                context_run_index=context.run_index,
                context_max_periods=context.max_periods,
                bav_id=context.bav_id,
                insurer_ids=context.insurer_ids,
                policyholder_ids=context.policyholder_ids,
            )
        )

    expected_count = len(references)
    resolution_complete = resolved_count == expected_count and not any(
        issue.stage == "candidate_resolution" for issue in issues
    )
    digests_reverified = (
        digest_verified_count == expected_count
        and not any(issue.stage == "candidate_digest" for issue in issues)
    )
    contexts_consistent = (
        context_verified_count == expected_count
        and not any(issue.stage == "candidate_context" for issue in issues)
    )
    actor_identities_consistent = (
        context_verified_count == expected_count
        and not any(issue.stage == "actor_identity" for issue in issues)
    )
    return StrategyExecutionPeriodChainResolutionReport(
        input_validated=True,
        resolution_complete=resolution_complete,
        digests_reverified=digests_reverified,
        contexts_consistent=contexts_consistent,
        actor_identities_consistent=actor_identities_consistent,
        run_index=run_index,
        max_periods=max_periods,
        expected_candidate_count=expected_count,
        resolved_candidate_count=resolved_count,
        digest_verified_candidate_count=digest_verified_count,
        context_verified_candidate_count=context_verified_count,
        candidates=tuple(candidates),
        issues=tuple(issues),
    )


@dataclass(frozen=True, slots=True)
class _ResolvedCandidateContext:
    run_index: int
    max_periods: int
    bav_id: int
    insurer_ids: tuple[int, ...]
    policyholder_ids: tuple[int, ...]


def _validate_resolved_reference(
    record: StrategyExecutionCandidateStoreRecord,
    *,
    candidate_id: str,
    expected_digest: str,
    expected_period: int,
    path: str,
    issues: list[StrategyExecutionPeriodChainResolutionIssue],
) -> bool:
    digest_valid = True
    if record.candidate_id != candidate_id:
        digest_valid = False
        _issue(
            issues,
            stage="candidate_digest",
            path=f"{path}.candidate_id",
            code="resolved_candidate_id_mismatch",
            message="Gespeicherte Kandidaten-ID weicht von der Referenz ab",
        )
    if record.content_digest != expected_digest:
        digest_valid = False
        _issue(
            issues,
            stage="candidate_digest",
            path=f"{path}.content_digest",
            code="resolved_candidate_digest_mismatch",
            message="Neu verifizierter Kandidatendigest weicht von der Referenz ab",
        )
    if record.period != expected_period:
        _issue(
            issues,
            stage="candidate_context",
            path=f"{path}.period",
            code="resolved_candidate_period_mismatch",
            message="Gespeicherte Kandidatenperiode weicht von der Referenz ab",
        )
    return digest_valid


def _resolved_candidate_context(
    record: StrategyExecutionCandidateStoreRecord,
    *,
    expected_period: int,
    expected_run_index: int,
    expected_max_periods: int,
    path: str,
    issues: list[StrategyExecutionPeriodChainResolutionIssue],
) -> _ResolvedCandidateContext | None:
    ground_state = record.candidate.get("market_ground_state")
    if not isinstance(ground_state, dict):
        _issue(
            issues,
            stage="candidate_context",
            path=f"{path}.candidate.market_ground_state",
            code="candidate_ground_state_missing",
            message="Gespeicherter Kandidat hat keinen Marktgrundzustand",
        )
        return None
    context = ground_state.get("simulation_context")
    if not isinstance(context, dict):
        _issue(
            issues,
            stage="candidate_context",
            path=f"{path}.candidate.market_ground_state.simulation_context",
            code="candidate_context_missing",
            message="Gespeicherter Kandidat hat keinen Laufkontext",
        )
        return None

    context_period = _context_integer(
        context.get("period"),
        path=f"{path}.candidate.market_ground_state.simulation_context.period",
        noun="Kontextperiode",
        issues=issues,
    )
    context_run_index = _context_integer(
        context.get("run_index"),
        path=f"{path}.candidate.market_ground_state.simulation_context.run_index",
        noun="Kontextlaufindex",
        issues=issues,
        minimum=0,
    )
    context_max_periods = _context_integer(
        context.get("max_periods"),
        path=f"{path}.candidate.market_ground_state.simulation_context.max_periods",
        noun="Kontexthorizont",
        issues=issues,
    )
    bav_id = _bav_id(ground_state.get("bav"), path=path, issues=issues)
    insurer_ids = _actor_ids(
        ground_state.get("insurers"),
        collection_name="insurers",
        actor_name="VU",
        path=path,
        issues=issues,
    )
    policyholder_ids = _actor_ids(
        ground_state.get("policyholders"),
        collection_name="policyholders",
        actor_name="VN",
        path=path,
        issues=issues,
    )
    if None in {
        context_period,
        context_run_index,
        context_max_periods,
        bav_id,
        insurer_ids,
        policyholder_ids,
    }:
        return None

    assert context_period is not None
    assert context_run_index is not None
    assert context_max_periods is not None
    assert bav_id is not None
    assert insurer_ids is not None
    assert policyholder_ids is not None
    if context_period != expected_period:
        _issue(
            issues,
            stage="candidate_context",
            path=f"{path}.candidate.market_ground_state.simulation_context.period",
            code="candidate_context_period_mismatch",
            message="Kontextperiode weicht von der Kettenperiode ab",
        )
    if context_run_index != expected_run_index:
        _issue(
            issues,
            stage="candidate_context",
            path=f"{path}.candidate.market_ground_state.simulation_context.run_index",
            code="candidate_context_run_index_mismatch",
            message="Kontextlaufindex weicht vom Kettenlaufindex ab",
        )
    if context_max_periods != expected_max_periods:
        _issue(
            issues,
            stage="candidate_context",
            path=f"{path}.candidate.market_ground_state.simulation_context.max_periods",
            code="candidate_context_max_periods_mismatch",
            message="Kontexthorizont weicht vom Kettenhorizont ab",
        )
    return _ResolvedCandidateContext(
        run_index=context_run_index,
        max_periods=context_max_periods,
        bav_id=bav_id,
        insurer_ids=insurer_ids,
        policyholder_ids=policyholder_ids,
    )


def _validate_actor_identity(
    actual: tuple[int, tuple[int, ...], tuple[int, ...]],
    expected: tuple[int, tuple[int, ...], tuple[int, ...]],
    *,
    path: str,
    issues: list[StrategyExecutionPeriodChainResolutionIssue],
) -> None:
    for index, (code, noun) in enumerate(
        (
            ("candidate_bav_identity_mismatch", "BAV-Identitaet"),
            ("candidate_insurer_identity_mismatch", "VU-Identitaeten"),
            ("candidate_policyholder_identity_mismatch", "VN-Identitaeten"),
        )
    ):
        if actual[index] != expected[index]:
            _issue(
                issues,
                stage="actor_identity",
                path=f"{path}.candidate.market_ground_state",
                code=code,
                message=f"{noun} weichen von Periode 1 ab",
            )


def _context_integer(
    value: object,
    *,
    path: str,
    noun: str,
    issues: list[StrategyExecutionPeriodChainResolutionIssue],
    minimum: int = 1,
) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        _issue(
            issues,
            stage="candidate_context",
            path=path,
            code="candidate_context_integer_invalid",
            message=f"{noun} muss eine Ganzzahl groesser oder gleich {minimum} sein",
        )
        return None
    return value


def _bav_id(
    value: object,
    *,
    path: str,
    issues: list[StrategyExecutionPeriodChainResolutionIssue],
) -> int | None:
    if not isinstance(value, dict):
        _issue(
            issues,
            stage="candidate_context",
            path=f"{path}.candidate.market_ground_state.bav",
            code="candidate_bav_missing",
            message="BAV-Grundzustand fehlt",
        )
        return None
    return _context_integer(
        value.get("entity_id"),
        path=f"{path}.candidate.market_ground_state.bav.entity_id",
        noun="BAV-ID",
        issues=issues,
    )


def _actor_ids(
    value: object,
    *,
    collection_name: str,
    actor_name: str,
    path: str,
    issues: list[StrategyExecutionPeriodChainResolutionIssue],
) -> tuple[int, ...] | None:
    collection_path = f"{path}.candidate.market_ground_state.{collection_name}"
    if not isinstance(value, list):
        _issue(
            issues,
            stage="candidate_context",
            path=collection_path,
            code="candidate_actor_collection_invalid",
            message=f"{actor_name}-Grundzustand muss eine Liste sein",
        )
        return None
    actor_ids: list[int] = []
    for index, actor in enumerate(value):
        if not isinstance(actor, dict):
            _issue(
                issues,
                stage="candidate_context",
                path=f"{collection_path}[{index}]",
                code="candidate_actor_invalid",
                message=f"{actor_name}-Grundzustand muss ein Objekt sein",
            )
            return None
        actor_id = _context_integer(
            actor.get("entity_id"),
            path=f"{collection_path}[{index}].entity_id",
            noun=f"{actor_name}-ID",
            issues=issues,
        )
        if actor_id is None:
            return None
        actor_ids.append(actor_id)
    if len(set(actor_ids)) != len(actor_ids):
        _issue(
            issues,
            stage="candidate_context",
            path=collection_path,
            code="candidate_actor_id_duplicate",
            message=f"{actor_name}-IDs muessen eindeutig sein",
        )
        return None
    return tuple(sorted(actor_ids))


def _issue(
    issues: list[StrategyExecutionPeriodChainResolutionIssue],
    *,
    stage: str,
    path: str,
    code: str,
    message: str,
) -> None:
    issues.append(
        StrategyExecutionPeriodChainResolutionIssue(
            stage=stage,
            path=path,
            code=code,
            message=message,
        )
    )


def strategy_execution_period_chain_resolution_contract_payload() -> dict[
    str, object
]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_CONTRACT_VERSION
        ),
        "resolution_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_VERSION
        ),
        "input_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
        "input_validation_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_VALIDATION_VERSION
        ),
        "period_chain_contract_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_period_chain_resolution_contract_read_only",
        "scope": "atomic_server_side_candidate_resolution_and_context_check",
        "contract_endpoint": (
            "/api/strategies/execution-period-chain-resolution-contract"
        ),
        "resolution_endpoint": (
            "/api/strategies/execution-period-chain-resolution"
        ),
        "input_validation_endpoint": (
            "/api/strategies/execution-period-chain-validation"
        ),
        "storage_source": "configured_workbench_sqlite_read_only",
        "forbidden_request_fields": [
            "db_path",
            "metadata_db",
            "candidate",
            "candidate_payload",
            "fixture_path",
            "output_dir",
        ],
        "resolution_order": [
            "validate_complete_pr134_input",
            "resolve_each_candidate_by_candidate_id",
            "recalculate_and_verify_each_stored_candidate_digest",
            "match_reference_id_digest_and_period",
            "match_candidate_period_run_index_and_max_periods",
            "match_bav_insurer_and_policyholder_identities_across_periods",
            "return_summaries_only_when_all_checks_pass",
        ],
        "candidate_context_fields": [
            "identity.period",
            "market_ground_state.simulation_context.period",
            "market_ground_state.simulation_context.run_index",
            "market_ground_state.simulation_context.max_periods",
        ],
        "actor_identity_fields": [
            "market_ground_state.bav.entity_id",
            "market_ground_state.insurers[].entity_id",
            "market_ground_state.policyholders[].entity_id",
        ],
        "profile_identity_must_match_across_periods": False,
        "partial_resolution_allowed": False,
        "candidate_resolution_enabled": True,
        "candidate_digest_reverification_enabled": True,
        "candidate_context_cross_check_enabled": True,
        "actor_identity_cross_check_enabled": True,
        "free_database_paths_accepted": False,
        "period_chain_creation_enabled": False,
        "period_chain_digest_enabled": False,
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


def strategy_execution_period_chain_resolution_error_payload(
    code: str,
    message: str,
) -> dict[str, object]:
    report = StrategyExecutionPeriodChainResolutionReport(
        input_validated=False,
        resolution_complete=False,
        digests_reverified=False,
        contexts_consistent=False,
        actor_identities_consistent=False,
        run_index=None,
        max_periods=None,
        expected_candidate_count=0,
        resolved_candidate_count=0,
        digest_verified_candidate_count=0,
        context_verified_candidate_count=0,
        candidates=(),
        issues=(
            StrategyExecutionPeriodChainResolutionIssue(
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
