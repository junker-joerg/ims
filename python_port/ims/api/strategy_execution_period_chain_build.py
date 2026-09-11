from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from ims.api.strategy_execution_period_chain_resolution import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_VERSION,
    StrategyExecutionPeriodChainResolutionReport,
    resolve_strategy_execution_period_chain_input,
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
)


STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_CONTRACT_VERSION = (
    "ims.strategy-execution-period-chain-build-contract.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION = (
    "ims.strategy-execution-period-chain-build.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_DIGEST_ALGORITHM = "sha256"
STRATEGY_EXECUTION_PERIOD_CHAIN_ID_PREFIX = "strategy-period-chain-"


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainBuildIssue:
    stage: str
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChain:
    chain_id: str
    content_digest: str
    sections: dict[str, object]
    schema_version: str = STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION
    mode: str = "strategy_execution_period_chain"
    base_model: str = "Vdefmd6"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "base_model": self.base_model,
            "identity": {
                "chain_id": self.chain_id,
                "content_digest": self.content_digest,
                "schema_version": self.schema_version,
            },
            **deepcopy(self.sections),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainBuildReport:
    input_validated: bool
    candidate_resolution_ready: bool
    expected_candidate_count: int
    resolved_candidate_count: int
    chain: StrategyExecutionPeriodChain | None
    issues: tuple[StrategyExecutionPeriodChainBuildIssue, ...]
    schema_version: str = STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION
    mode: str = "strategy_execution_period_chain_build"

    @property
    def build_complete(self) -> bool:
        return (
            self.input_validated
            and self.candidate_resolution_ready
            and self.chain is not None
            and not self.issues
        )

    def to_dict(self) -> dict[str, object]:
        chain_created = self.chain is not None and self.build_complete
        return {
            "schema_version": self.schema_version,
            "input_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
            "period_chain_contract_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION
            ),
            "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
            "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
            "resolution_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_VERSION
            ),
            "mode": self.mode,
            "status": "ready" if self.build_complete else "blocked",
            "build_complete": self.build_complete,
            "input_validated": self.input_validated,
            "candidate_resolution_ready": self.candidate_resolution_ready,
            "expected_candidate_count": self.expected_candidate_count,
            "resolved_candidate_count": self.resolved_candidate_count,
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
            "period_chain_digest_calculated": chain_created,
            "period_chain_persisted": False,
            "source_values_consumed": chain_created,
            "carryover_invocation_performed": False,
            "runner_invocation_performed": False,
            "writes_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR139",
        }


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def calculate_strategy_execution_period_chain_content_digest(
    *,
    sections: Mapping[str, object],
    period_chain_schema_version: str = STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
    base_model: str = "Vdefmd6",
) -> str:
    """Berechnet den Kettendigest ohne die daraus abgeleitete Identitaet."""

    basis = {
        "period_chain_schema_version": period_chain_schema_version,
        "base_model": base_model,
        **deepcopy(dict(sections)),
    }
    return f"sha256:{sha256(_canonical_bytes(basis)).hexdigest()}"


def strategy_execution_period_chain_id_from_digest(content_digest: str) -> str:
    prefix = "sha256:"
    digest_hex = content_digest.removeprefix(prefix)
    if (
        not content_digest.startswith(prefix)
        or len(digest_hex) != 64
        or digest_hex.lower() != digest_hex
    ):
        raise ValueError("period chain content digest must be a lowercase sha256 digest")
    try:
        int(digest_hex, 16)
    except ValueError as exc:
        raise ValueError(
            "period chain content digest must be a lowercase sha256 digest"
        ) from exc
    return f"{STRATEGY_EXECUTION_PERIOD_CHAIN_ID_PREFIX}{digest_hex[:24]}"


def strategy_execution_period_chain_build_provenance_payload(
    candidate_count: int,
) -> dict[str, object]:
    return {
        "chain_build_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION,
        "candidate_resolution_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_VERSION
        ),
        "candidate_store_source": "configured_workbench_sqlite_read_only",
        "candidate_count": candidate_count,
        "candidate_digest_reverification_complete": True,
        "candidate_context_cross_check_complete": True,
        "actor_identity_cross_check_complete": True,
    }


def strategy_execution_period_chain_execution_boundaries_payload() -> dict[
    str, object
]:
    return {
        "validation_enabled": True,
        "persistence_enabled": False,
        "runner_enabled": False,
        "ui_start_enabled": False,
        "carryover_execution_enabled": False,
        "multi_period_execution_enabled": False,
        "output_files_enabled": False,
        "simulation_performed": False,
    }


def build_strategy_execution_period_chain(
    value: object,
    *,
    db_path: Path | str,
) -> StrategyExecutionPeriodChainBuildReport:
    """Baut nach PR135 eine kanonische Kette, ohne sie zu speichern."""

    resolution = resolve_strategy_execution_period_chain_input(
        value,
        db_path=db_path,
    )
    if not resolution.resolution_ready:
        return _blocked_report(resolution)

    assert isinstance(value, dict)
    assert resolution.run_index is not None
    assert resolution.max_periods is not None
    transitions = value["transitions"]
    assert isinstance(transitions, list)

    period_candidates = [
        {
            "candidate_id": candidate.candidate_id,
            "content_digest": candidate.content_digest,
            "period": candidate.period,
        }
        for candidate in sorted(resolution.candidates, key=lambda item: item.period)
    ]
    canonical_transitions = [
        {
            "from_period": int(transition["from_period"]),
            "to_period": int(transition["to_period"]),
            "carry_forward_vu_state": bool(
                transition["carry_forward_vu_state"]
            ),
            "carry_forward_vn_state": bool(
                transition["carry_forward_vn_state"]
            ),
        }
        for transition in transitions
        if isinstance(transition, dict)
    ]
    sections: dict[str, object] = {
        "horizon": {
            "first_period": 1,
            "last_period": resolution.max_periods,
            "period_count": resolution.max_periods,
            "run_index": resolution.run_index,
            "max_periods": resolution.max_periods,
        },
        "period_candidates": period_candidates,
        "transitions": canonical_transitions,
        "provenance": strategy_execution_period_chain_build_provenance_payload(
            len(period_candidates)
        ),
        "execution_boundaries": (
            strategy_execution_period_chain_execution_boundaries_payload()
        ),
    }
    try:
        content_digest = calculate_strategy_execution_period_chain_content_digest(
            sections=sections
        )
        chain_id = strategy_execution_period_chain_id_from_digest(content_digest)
    except (TypeError, ValueError, OverflowError) as exc:
        return StrategyExecutionPeriodChainBuildReport(
            input_validated=True,
            candidate_resolution_ready=True,
            expected_candidate_count=resolution.expected_candidate_count,
            resolved_candidate_count=resolution.resolved_candidate_count,
            chain=None,
            issues=(
                StrategyExecutionPeriodChainBuildIssue(
                    stage="period_chain_digest",
                    path="$",
                    code="period_chain_not_canonicalizable",
                    message=str(exc),
                ),
            ),
        )

    return StrategyExecutionPeriodChainBuildReport(
        input_validated=True,
        candidate_resolution_ready=True,
        expected_candidate_count=resolution.expected_candidate_count,
        resolved_candidate_count=resolution.resolved_candidate_count,
        chain=StrategyExecutionPeriodChain(
            chain_id=chain_id,
            content_digest=content_digest,
            sections=sections,
        ),
        issues=(),
    )


def _blocked_report(
    resolution: StrategyExecutionPeriodChainResolutionReport,
) -> StrategyExecutionPeriodChainBuildReport:
    return StrategyExecutionPeriodChainBuildReport(
        input_validated=resolution.input_validated,
        candidate_resolution_ready=False,
        expected_candidate_count=resolution.expected_candidate_count,
        resolved_candidate_count=resolution.resolved_candidate_count,
        chain=None,
        issues=tuple(
            StrategyExecutionPeriodChainBuildIssue(
                stage=issue.stage,
                path=issue.path,
                code=issue.code,
                message=issue.message,
            )
            for issue in resolution.issues
        ),
    )


def strategy_execution_period_chain_build_contract_payload() -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_CONTRACT_VERSION,
        "build_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION,
        "input_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
        "period_chain_contract_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "resolution_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_VERSION
        ),
        "mode": "strategy_execution_period_chain_build_contract",
        "scope": "resolved_candidates_to_ephemeral_canonical_period_chain",
        "contract_endpoint": (
            "/api/strategies/execution-period-chain-build-contract"
        ),
        "build_endpoint": "/api/strategies/execution-period-chain-build",
        "resolution_endpoint": (
            "/api/strategies/execution-period-chain-resolution"
        ),
        "storage_source": "configured_workbench_sqlite_read_only",
        "forbidden_request_fields": [
            "db_path",
            "metadata_db",
            "candidate",
            "candidate_payload",
            "resolution_report",
            "fixture_path",
            "output_dir",
        ],
        "build_order": [
            "validate_resolve_and_reverify_complete_pr135_input",
            "derive_references_from_server_resolved_candidates",
            "canonicalize_horizon_candidates_transitions_and_boundaries",
            "calculate_complete_chain_content_digest",
            "derive_chain_id_from_complete_digest",
            "return_complete_ephemeral_chain_only",
        ],
        "digest": {
            "algorithm": STRATEGY_EXECUTION_PERIOD_CHAIN_DIGEST_ALGORITHM,
            "prefix": "sha256:",
            "encoding": "ascii",
            "json_sort_keys": True,
            "json_separators": [",", ":"],
            "non_finite_numbers_allowed": False,
            "identity_fields_excluded": ["chain_id", "content_digest"],
            "database_path_excluded": True,
            "candidate_storage_timestamp_excluded": True,
            "full_candidate_payloads_excluded": True,
        },
        "chain_id_prefix": STRATEGY_EXECUTION_PERIOD_CHAIN_ID_PREFIX,
        "partial_chain_allowed": False,
        "candidate_payloads_embedded": False,
        "candidate_resolution_enabled": True,
        "candidate_digest_reverification_enabled": True,
        "period_chain_creation_enabled": True,
        "period_chain_digest_enabled": True,
        "period_chain_persistence_enabled": False,
        "carryover_invocation_enabled": False,
        "runner_enabled": False,
        "ui_start_enabled": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR139",
    }


def strategy_execution_period_chain_build_error_payload(
    code: str,
    message: str,
) -> dict[str, object]:
    report = StrategyExecutionPeriodChainBuildReport(
        input_validated=False,
        candidate_resolution_ready=False,
        expected_candidate_count=0,
        resolved_candidate_count=0,
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
