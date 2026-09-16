from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from ims.api.strategy_execution_candidate_effect_probe import (
    build_strategy_execution_candidate_scenario_mapping,
    build_strategy_execution_period_effect,
    project_strategy_execution_state,
)
from ims.api.strategy_execution_candidate_store import (
    StrategyExecutionCandidateStoreError,
    StrategyExecutionCandidateStoreRecord,
    get_strategy_execution_candidate,
)
from ims.api.strategy_execution_period_chain_effect_probe import (
    StrategyExecutionPeriodChainEffectProbeRunner,
)
from ims.api.strategy_execution_period_chain_effect_probe_start import (
    StrategyExecutionPeriodChainEffectProbeStartError,
    get_strategy_execution_period_chain_effect_probe_result,
)
from ims.api.strategy_execution_period_chain_five_period_build import (
    FIVE_PERIOD_CHAIN_PERIOD_COUNT,
    FIVE_PERIOD_CHAIN_TRANSITION_COUNT,
    build_strategy_execution_five_period_chain,
)
from ims.engine.explicit_period_runner import (
    ExplicitPeriodRunResult,
    run_loaded_explicit_period,
)
from ims.engine.vn_rule_runner import VNStateCarryover, apply_vn_state_carryover
from ims.engine.vu_rule_runner import (
    VUForeignInfoCarryover,
    apply_vu_foreign_info_carryover,
)
from ims.io.scenario_loader import (
    LoadedScenario,
    ScenarioValidationError,
    load_scenario_from_mapping,
)
from ims.model.agrsich_export import compute_global_period
from ims.strategies.execution_period_chain_bounded_runner_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_PREFIX_PROJECTION_VERSION,
    build_strategy_execution_two_period_prefix_projection,
    calculate_strategy_execution_prefix_digest,
    canonical_strategy_execution_prefix_bytes,
)


STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_CONTRACT_VERSION = (
    "ims.strategy-execution-five-period-effect-probe-contract.v1"
)
STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION = (
    "ims.strategy-execution-five-period-effect-probe-request.v1"
)
STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_VERSION = (
    "ims.strategy-execution-five-period-effect-probe-result.v1"
)

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "period_chain_input",
        "prefix_baseline",
        "explicit_five_period_effect_probe_execution",
    }
)
_BASELINE_FIELDS = frozenset(
    {"chain_id", "expected_content_digest", "expected_result_digest"}
)


class StrategyExecutionFivePeriodEffectProbeError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        runner_invocation_count: int = 0,
        carryover_invocation_count: int = 0,
        candidate_reverified_count: int = 0,
        prefix_baseline_verified: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.runner_invocation_count = runner_invocation_count
        self.carryover_invocation_count = carryover_invocation_count
        self.candidate_reverified_count = candidate_reverified_count
        self.prefix_baseline_verified = prefix_baseline_verified


@dataclass(frozen=True, slots=True)
class StrategyExecutionPrefixBaselineReference:
    chain_id: str
    expected_content_digest: str
    expected_result_digest: str

    def to_dict(self) -> dict[str, str]:
        return {
            "chain_id": self.chain_id,
            "expected_content_digest": self.expected_content_digest,
            "expected_result_digest": self.expected_result_digest,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionFivePeriodEffectProbeRequest:
    period_chain_input: dict[str, object]
    prefix_baseline: StrategyExecutionPrefixBaselineReference
    explicit_five_period_effect_probe_execution: bool
    schema_version: str = STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "period_chain_input": deepcopy(self.period_chain_input),
            "prefix_baseline": self.prefix_baseline.to_dict(),
            "explicit_five_period_effect_probe_execution": (
                self.explicit_five_period_effect_probe_execution
            ),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionFivePeriodEffectProbeResult:
    request: StrategyExecutionFivePeriodEffectProbeRequest
    period_chain: dict[str, object]
    period_effects: tuple[dict[str, object], ...]
    transition_effects: tuple[dict[str, object], ...]
    prefix_proof: dict[str, object]
    candidate_reverified_count: int

    @property
    def execution_performed(self) -> bool:
        return (
            len(self.period_effects) == FIVE_PERIOD_CHAIN_PERIOD_COUNT
            and len(self.transition_effects) == FIVE_PERIOD_CHAIN_TRANSITION_COUNT
            and self.prefix_proof.get("prefix_equal") is True
        )

    def to_dict(self) -> dict[str, object]:
        carryover_count = sum(
            int(effect.get("vu_carryover_executed") is True)
            + int(effect.get("vn_carryover_executed") is True)
            for effect in self.transition_effects
        )
        identity = self.period_chain.get("identity")
        return {
            "schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_VERSION,
            "request_schema_version": (
                STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION
            ),
            "prefix_projection_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_PREFIX_PROJECTION_VERSION
            ),
            "mode": "strategy_execution_five_period_effect_probe",
            "status": "ok" if self.execution_performed else "blocked",
            "request": self.request.to_dict(),
            "period_chain_identity": deepcopy(identity),
            "period_effects": [deepcopy(effect) for effect in self.period_effects],
            "transition_effects": [
                deepcopy(effect) for effect in self.transition_effects
            ],
            "prefix_proof": deepcopy(self.prefix_proof),
            "issue_count": 0,
            "issues": [],
            "five_period_chain_built_and_validated": True,
            "prefix_baseline_verified": True,
            "two_period_prefix_verified": self.prefix_proof.get("prefix_equal") is True,
            "candidate_re_resolution_performed": True,
            "candidate_reverified_count": self.candidate_reverified_count,
            "candidate_copies_isolated": self.execution_performed,
            "source_candidates_mutated": False,
            "canonical_transition_flags_applied_exactly": self.execution_performed,
            "effect_probe_execution_released": (
                self.request.explicit_five_period_effect_probe_execution
            ),
            "period_count": len(self.period_effects),
            "runner_invocation_count": len(self.period_effects),
            "runner_invocation_performed": bool(self.period_effects),
            "transition_count": len(self.transition_effects),
            "carryover_invocation_count": carryover_count,
            "carryover_invocation_performed": carryover_count > 0,
            "partial_result_returned": False,
            "queue_entry_created": False,
            "result_persisted": False,
            "idempotency_persisted": False,
            "writes_performed": False,
            "execution_performed": self.execution_performed,
            "output_files_written": False,
            "legacy_comparison_performed": False,
            "simulation_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR147",
        }


@dataclass(frozen=True, slots=True)
class _PreparedFivePeriodProbe:
    loaded_scenarios: tuple[LoadedScenario, ...]
    source_candidates: tuple[dict[str, object], ...]
    transitions: tuple[dict[str, object], ...]
    candidate_reverified_count: int


def parse_strategy_execution_five_period_effect_probe_request(
    value: object,
) -> StrategyExecutionFivePeriodEffectProbeRequest:
    if not isinstance(value, dict):
        raise StrategyExecutionFivePeriodEffectProbeError(
            "request_object_required",
            "Fuenf-Perioden-Wirkungsprobe verlangt ein JSON-Objekt",
        )
    _require_exact_fields(value, _REQUEST_FIELDS, "request")
    if value["schema_version"] != (
        STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION
    ):
        raise StrategyExecutionFivePeriodEffectProbeError(
            "unsupported_schema_version",
            "Fuenf-Perioden-Wirkungsprobe erwartet schema_version "
            f"{STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION}",
        )
    if value["explicit_five_period_effect_probe_execution"] is not True:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "effect_probe_execution_release_required",
            "Fuenf-Perioden-Wirkungsprobe muss explizit freigegeben sein",
        )
    period_chain_input = value["period_chain_input"]
    if not isinstance(period_chain_input, dict):
        raise StrategyExecutionFivePeriodEffectProbeError(
            "period_chain_input_object_required",
            "Fuenf-Perioden-Wirkungsprobe verlangt einen Ketteneingang",
        )
    baseline = value["prefix_baseline"]
    if not isinstance(baseline, dict):
        raise StrategyExecutionFivePeriodEffectProbeError(
            "prefix_baseline_object_required",
            "Prefixnachweis verlangt eine gespeicherte Zwei-Perioden-Referenz",
        )
    _require_exact_fields(baseline, _BASELINE_FIELDS, "prefix_baseline")
    chain_id = _required_text(baseline, "chain_id")
    expected_content_digest = _required_digest(
        baseline,
        "expected_content_digest",
    )
    expected_result_digest = _required_digest(
        baseline,
        "expected_result_digest",
    )
    return StrategyExecutionFivePeriodEffectProbeRequest(
        period_chain_input=deepcopy(period_chain_input),
        prefix_baseline=StrategyExecutionPrefixBaselineReference(
            chain_id=chain_id,
            expected_content_digest=expected_content_digest,
            expected_result_digest=expected_result_digest,
        ),
        explicit_five_period_effect_probe_execution=True,
    )


def run_strategy_execution_five_period_effect_probe(
    request: StrategyExecutionFivePeriodEffectProbeRequest,
    *,
    db_path: Path | str,
    runner: StrategyExecutionPeriodChainEffectProbeRunner | None = None,
) -> StrategyExecutionFivePeriodEffectProbeResult:
    build = build_strategy_execution_five_period_chain(
        request.period_chain_input,
        db_path=db_path,
    )
    if not build.build_complete or build.chain is None:
        issue = build.issues[0] if build.issues else None
        raise StrategyExecutionFivePeriodEffectProbeError(
            issue.code if issue is not None else "five_period_chain_not_ready",
            (
                issue.message
                if issue is not None
                else "Fuenf-Perioden-Kette konnte nicht vollstaendig gebaut werden"
            ),
            candidate_reverified_count=build.resolved_candidate_count,
        )

    baseline_payload = _load_verified_prefix_baseline(
        request.prefix_baseline,
        db_path=db_path,
    )
    prepared = _prepare_five_period_probe(
        build.chain.to_dict(),
        db_path=db_path,
    )
    effective_runner = runner or run_loaded_explicit_period
    period_effects: list[dict[str, object]] = []
    transition_effects: list[dict[str, object]] = []
    runner_count = 0
    carryover_count = 0
    prefix_proof: dict[str, object] | None = None

    for index, loaded in enumerate(prepared.loaded_scenarios):
        period = index + 1
        state_before = project_strategy_execution_state(loaded)
        result = _run_period(
            effective_runner,
            loaded,
            expected_period=period,
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=prepared.candidate_reverified_count,
        )
        runner_count += 1
        state_after = project_strategy_execution_state(loaded)
        period_effects.append(
            build_strategy_execution_period_effect(
                result,
                state_before=state_before,
                state_after=state_after,
            )
        )

        if period == 2:
            prefix_proof = _build_prefix_proof(
                baseline_payload,
                request.prefix_baseline,
                period_effects=period_effects,
                transition_effects=transition_effects,
            )
            if prefix_proof["prefix_equal"] is not True:
                raise StrategyExecutionFivePeriodEffectProbeError(
                    "five_period_prefix_mismatch",
                    "Fuenf-Perioden-Wirkung weicht im Prefix 1 bis 2 von der "
                    "gespeicherten Referenz ab",
                    runner_invocation_count=runner_count,
                    carryover_invocation_count=carryover_count,
                    candidate_reverified_count=prepared.candidate_reverified_count,
                    prefix_baseline_verified=True,
                )

        if index >= FIVE_PERIOD_CHAIN_TRANSITION_COUNT:
            continue
        transition = prepared.transitions[index]
        next_loaded = prepared.loaded_scenarios[index + 1]
        transition_before = project_strategy_execution_state(next_loaded)
        vu_carryover: VUForeignInfoCarryover | None = None
        vn_carryover: VNStateCarryover | None = None
        try:
            if transition["carry_forward_vu_state"]:
                vu_carryover = apply_vu_foreign_info_carryover(
                    result.vu_result,
                    next_loaded,
                )
                carryover_count += 1
            if transition["carry_forward_vn_state"]:
                vn_carryover = apply_vn_state_carryover(
                    result.vn_result,
                    next_loaded,
                )
                carryover_count += 1
        except Exception as exc:
            raise StrategyExecutionFivePeriodEffectProbeError(
                "effect_probe_carryover_failed",
                f"Fuenf-Perioden-Carryover {period}->{period + 1} ist "
                f"fehlgeschlagen: {exc}",
                runner_invocation_count=runner_count,
                carryover_invocation_count=carryover_count,
                candidate_reverified_count=prepared.candidate_reverified_count,
                prefix_baseline_verified=True,
            ) from exc
        _validate_carryovers(
            transition,
            vu_carryover=vu_carryover,
            vn_carryover=vn_carryover,
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=prepared.candidate_reverified_count,
        )
        transition_after = project_strategy_execution_state(next_loaded)
        transition_effects.append(
            _transition_effect_payload(
                result,
                next_loaded,
                transition=transition,
                vu_carryover=vu_carryover,
                vn_carryover=vn_carryover,
                state_before=transition_before,
                state_after=transition_after,
            )
        )

    if prefix_proof is None:  # pragma: no cover - protected by exact horizon.
        raise StrategyExecutionFivePeriodEffectProbeError(
            "five_period_prefix_not_checked",
            "Prefix 1 bis 2 wurde nicht geprueft",
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=prepared.candidate_reverified_count,
            prefix_baseline_verified=True,
        )
    _verify_source_candidates_unchanged(
        build.chain.to_dict(),
        prepared.source_candidates,
        db_path=db_path,
        runner_invocation_count=runner_count,
        carryover_invocation_count=carryover_count,
        candidate_reverified_count=prepared.candidate_reverified_count,
    )
    return StrategyExecutionFivePeriodEffectProbeResult(
        request=request,
        period_chain=build.chain.to_dict(),
        period_effects=tuple(period_effects),
        transition_effects=tuple(transition_effects),
        prefix_proof=prefix_proof,
        candidate_reverified_count=prepared.candidate_reverified_count,
    )


def strategy_execution_five_period_effect_probe_contract_payload() -> dict[
    str, object
]:
    boundary_flags = {
        "explicit_five_period_effect_probe_execution_required": True,
        "exact_five_period_horizon_required": True,
        "stored_two_period_prefix_baseline_required": True,
        "stored_two_period_result_digest_reverification_required": True,
        "all_inputs_validated_before_first_runner": True,
        "isolated_candidate_copies_required": True,
        "canonical_transition_flags_authoritative": True,
        "two_period_prefix_canonical_byte_equality_required": True,
        "prefix_mismatch_blocks_periods_three_to_five": True,
        "atomic_partial_result_suppression_enabled": True,
        "five_period_execution_enabled": True,
        "result_persistence_enabled": False,
        "idempotency_persistence_enabled": False,
        "ui_start_enabled": False,
        "queue_write_enabled": False,
        "output_files_enabled": False,
        "legacy_comparison_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_CONTRACT_VERSION,
        "request_schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
        "result_schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_VERSION,
        "prefix_projection_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_PREFIX_PROJECTION_VERSION
        ),
        "mode": "strategy_execution_five_period_effect_probe_contract",
        "scope": "one_ephemeral_chain_five_isolated_periods_four_transitions",
        "contract_endpoint": (
            "/api/run-control/strategy-period-chain-five-period-effect-probe-contract"
        ),
        "execution_endpoint": (
            "/api/run-control/strategy-period-chain-five-period-effect-probe"
        ),
        "request_fields": sorted(_REQUEST_FIELDS),
        "prefix_baseline_fields": sorted(_BASELINE_FIELDS),
        "execution_order": [
            "build_and_validate_complete_five_period_chain",
            "load_and_verify_stored_two_period_result",
            "load_and_cross_check_five_isolated_candidate_copies",
            "run_period_1_and_apply_transition_1_to_2",
            "run_period_2_and_compare_canonical_prefix",
            "run_periods_3_to_5_only_after_exact_prefix_match",
            "reverify_source_candidates_unchanged",
            "return_ephemeral_complete_result_only",
        ],
        "next_gate": "PR147",
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }


def strategy_execution_five_period_effect_probe_error_payload(
    code: str,
    message: str,
    *,
    runner_invocation_count: int = 0,
    carryover_invocation_count: int = 0,
    candidate_reverified_count: int = 0,
    prefix_baseline_verified: bool = False,
) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_VERSION,
        "request_schema_version": STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
        "mode": "strategy_execution_five_period_effect_probe",
        "status": "error",
        "issue_count": 1,
        "issues": [{"code": code, "message": message}],
        "period_chain_identity": None,
        "period_effects": [],
        "transition_effects": [],
        "prefix_proof": None,
        "five_period_chain_built_and_validated": False,
        "prefix_baseline_verified": prefix_baseline_verified,
        "two_period_prefix_verified": False,
        "candidate_re_resolution_performed": candidate_reverified_count > 0,
        "candidate_reverified_count": candidate_reverified_count,
        "candidate_copies_isolated": False,
        "source_candidates_mutated": False,
        "canonical_transition_flags_applied_exactly": False,
        "effect_probe_execution_released": False,
        "period_count": 0,
        "runner_invocation_count": runner_invocation_count,
        "runner_invocation_performed": runner_invocation_count > 0,
        "transition_count": 0,
        "carryover_invocation_count": carryover_invocation_count,
        "carryover_invocation_performed": carryover_invocation_count > 0,
        "partial_result_returned": False,
        "queue_entry_created": False,
        "result_persisted": False,
        "idempotency_persisted": False,
        "writes_performed": False,
        "execution_performed": False,
        "output_files_written": False,
        "legacy_comparison_performed": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR147",
    }


def _load_verified_prefix_baseline(
    reference: StrategyExecutionPrefixBaselineReference,
    *,
    db_path: Path | str,
) -> dict[str, object]:
    try:
        result = get_strategy_execution_period_chain_effect_probe_result(
            reference.chain_id,
            db_path=db_path,
        )
    except StrategyExecutionPeriodChainEffectProbeStartError as exc:
        raise StrategyExecutionFivePeriodEffectProbeError(
            exc.code,
            f"Zwei-Perioden-Prefixreferenz konnte nicht geprueft werden: {exc}",
        ) from exc
    record = result.record
    if record is None:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "prefix_baseline_result_missing",
            "Gespeichertes Zwei-Perioden-Ergebnis fuer den Prefix fehlt",
        )
    if record.content_digest != reference.expected_content_digest:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "prefix_baseline_content_digest_mismatch",
            "Kettendigest der Zwei-Perioden-Prefixreferenz weicht ab",
        )
    if record.result_digest != reference.expected_result_digest:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "prefix_baseline_result_digest_mismatch",
            "Ergebnisdigest der Zwei-Perioden-Prefixreferenz weicht ab",
        )
    return deepcopy(record.result_payload)


def _prepare_five_period_probe(
    period_chain: dict[str, object],
    *,
    db_path: Path | str,
) -> _PreparedFivePeriodProbe:
    horizon = period_chain.get("horizon")
    references = period_chain.get("period_candidates")
    transitions = period_chain.get("transitions")
    if (
        not isinstance(horizon, dict)
        or horizon.get("first_period") != 1
        or horizon.get("last_period") != 5
        or horizon.get("period_count") != 5
        or horizon.get("max_periods") != 5
        or not isinstance(references, list)
        or len(references) != 5
        or not isinstance(transitions, list)
        or len(transitions) != 4
    ):
        raise StrategyExecutionFivePeriodEffectProbeError(
            "exact_five_period_horizon_required",
            "Wirkungsprobe akzeptiert genau die Perioden 1 bis 5",
        )
    records = _resolve_candidate_records(references, db_path=db_path)
    source_candidates = tuple(deepcopy(record.candidate) for record in records)
    loaded_scenarios: list[LoadedScenario] = []
    try:
        for record in records:
            loaded_scenarios.append(
                load_scenario_from_mapping(
                    build_strategy_execution_candidate_scenario_mapping(
                        deepcopy(record.candidate)
                    )
                )
            )
    except (ScenarioValidationError, TypeError, ValueError, OverflowError) as exc:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "candidate_copy_load_failed",
            f"Isolierte Kandidatenkopien konnten nicht geladen werden: {exc}",
            candidate_reverified_count=len(records),
            prefix_baseline_verified=True,
        ) from exc
    _validate_loaded_scenarios(
        loaded_scenarios,
        expected_run_index=horizon.get("run_index"),
    )
    canonical_transitions: list[dict[str, object]] = []
    for period, transition in enumerate(transitions, start=1):
        if (
            not isinstance(transition, dict)
            or transition.get("from_period") != period
            or transition.get("to_period") != period + 1
            or not isinstance(transition.get("carry_forward_vu_state"), bool)
            or not isinstance(transition.get("carry_forward_vn_state"), bool)
        ):
            raise StrategyExecutionFivePeriodEffectProbeError(
                "five_period_transition_invalid",
                f"Uebergang {period}->{period + 1} ist nicht kanonisch",
                candidate_reverified_count=len(records),
                prefix_baseline_verified=True,
            )
        canonical_transitions.append(deepcopy(transition))
    return _PreparedFivePeriodProbe(
        loaded_scenarios=tuple(loaded_scenarios),
        source_candidates=source_candidates,
        transitions=tuple(canonical_transitions),
        candidate_reverified_count=len(records),
    )


def _resolve_candidate_records(
    references: list[object],
    *,
    db_path: Path | str,
) -> tuple[StrategyExecutionCandidateStoreRecord, ...]:
    records: list[StrategyExecutionCandidateStoreRecord] = []
    for index, reference in enumerate(references):
        if not isinstance(reference, dict):
            raise StrategyExecutionFivePeriodEffectProbeError(
                "candidate_reference_object_required",
                f"Kandidatenreferenz {index + 1} muss ein Objekt sein",
                candidate_reverified_count=len(records),
                prefix_baseline_verified=True,
            )
        try:
            stored = get_strategy_execution_candidate(
                str(reference.get("candidate_id", "")),
                db_path=db_path,
            )
        except StrategyExecutionCandidateStoreError as exc:
            raise StrategyExecutionFivePeriodEffectProbeError(
                "candidate_re_resolution_failed",
                f"Kandidat {index + 1} konnte nicht erneut geprueft werden: {exc}",
                candidate_reverified_count=len(records),
                prefix_baseline_verified=True,
            ) from exc
        record = stored.record
        if (
            record.candidate_id != reference.get("candidate_id")
            or record.content_digest != reference.get("content_digest")
            or record.period != reference.get("period")
            or not stored.post_storage_digest_verified
        ):
            raise StrategyExecutionFivePeriodEffectProbeError(
                "candidate_reference_changed",
                f"Kandidat {index + 1} weicht von der Kettenreferenz ab",
                candidate_reverified_count=len(records),
                prefix_baseline_verified=True,
            )
        records.append(record)
    return tuple(records)


def _validate_loaded_scenarios(
    loaded_scenarios: list[LoadedScenario],
    *,
    expected_run_index: object,
) -> None:
    if len(loaded_scenarios) != 5:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "exact_five_loaded_candidates_required",
            "Wirkungsprobe verlangt genau fuenf geladene Kandidatenkopien",
            candidate_reverified_count=len(loaded_scenarios),
            prefix_baseline_verified=True,
        )
    if [loaded.context.period for loaded in loaded_scenarios] != [1, 2, 3, 4, 5]:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "loaded_candidate_periods_mismatch",
            "Geladene Kandidatenkopien muessen Perioden 1 bis 5 abbilden",
            candidate_reverified_count=5,
            prefix_baseline_verified=True,
        )
    if any(
        loaded.context.run_index != expected_run_index
        or loaded.context.max_periods != 5
        for loaded in loaded_scenarios
    ):
        raise StrategyExecutionFivePeriodEffectProbeError(
            "loaded_candidate_context_mismatch",
            "Geladene Kandidatenkopien weichen vom Fuenf-Perioden-Kontext ab",
            candidate_reverified_count=5,
            prefix_baseline_verified=True,
        )
    global_periods = [
        compute_global_period(loaded.context) for loaded in loaded_scenarios
    ]
    if global_periods != list(range(global_periods[0], global_periods[0] + 5)):
        raise StrategyExecutionFivePeriodEffectProbeError(
            "loaded_candidate_global_period_mismatch",
            "Geladene Kandidatenkopien bilden keine benachbarten Globalperioden",
            candidate_reverified_count=5,
            prefix_baseline_verified=True,
        )
    identities = [
        (
            loaded.bav.entity_id,
            tuple(sorted(insurer.entity_id for insurer in loaded.insurers)),
            tuple(
                sorted(
                    policyholder.entity_id
                    for policyholder in loaded.policyholders
                )
            ),
        )
        for loaded in loaded_scenarios
    ]
    if len(set(identities)) != 1:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "loaded_candidate_actor_identity_mismatch",
            "Geladene Kandidatenkopien haben unterschiedliche Akteursidentitaeten",
            candidate_reverified_count=5,
            prefix_baseline_verified=True,
        )


def _run_period(
    runner: StrategyExecutionPeriodChainEffectProbeRunner,
    loaded: LoadedScenario,
    *,
    expected_period: int,
    runner_invocation_count: int,
    carryover_invocation_count: int,
    candidate_reverified_count: int,
) -> ExplicitPeriodRunResult:
    attempted_count = runner_invocation_count + 1
    try:
        result = runner(loaded, output_dir=None)
    except Exception as exc:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "effect_probe_runner_failed",
            f"Fuenf-Perioden-Wirkungsprobe ist in Periode {expected_period} "
            f"fehlgeschlagen: {exc}",
            runner_invocation_count=attempted_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            prefix_baseline_verified=True,
        ) from exc
    if result.period != expected_period:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "runner_period_mismatch",
            f"Runner meldet fuer Periode {expected_period} eine andere Periode",
            runner_invocation_count=attempted_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            prefix_baseline_verified=True,
        )
    if result.written_files:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "effect_probe_wrote_files",
            "Fuenf-Perioden-Wirkungsprobe darf keine Dateien schreiben",
            runner_invocation_count=attempted_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            prefix_baseline_verified=True,
        )
    return result


def _validate_carryovers(
    transition: dict[str, object],
    *,
    vu_carryover: VUForeignInfoCarryover | None,
    vn_carryover: VNStateCarryover | None,
    runner_invocation_count: int,
    carryover_invocation_count: int,
    candidate_reverified_count: int,
) -> None:
    vu_requested = transition["carry_forward_vu_state"] is True
    vn_requested = transition["carry_forward_vn_state"] is True
    from_period = int(transition["from_period"])
    to_period = int(transition["to_period"])
    if vu_requested and vu_carryover is None:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "requested_vu_carryover_missing",
            f"VU-Carryover {from_period}->{to_period} hat keinen Zustand uebertragen",
            runner_invocation_count=runner_invocation_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            prefix_baseline_verified=True,
        )
    if vn_requested and vn_carryover is None:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "requested_vn_carryover_missing",
            f"VN-Carryover {from_period}->{to_period} hat keinen Zustand uebertragen",
            runner_invocation_count=runner_invocation_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            prefix_baseline_verified=True,
        )
    for carryover in (vu_carryover, vn_carryover):
        if carryover is not None and (
            carryover.from_period != from_period
            or carryover.to_period != to_period
        ):
            raise StrategyExecutionFivePeriodEffectProbeError(
                "carryover_period_mismatch",
                f"Carryover meldet nicht den Uebergang {from_period}->{to_period}",
                runner_invocation_count=runner_invocation_count,
                carryover_invocation_count=carryover_invocation_count,
                candidate_reverified_count=candidate_reverified_count,
                prefix_baseline_verified=True,
            )


def _transition_effect_payload(
    previous_result: ExplicitPeriodRunResult,
    next_loaded: LoadedScenario,
    *,
    transition: dict[str, object],
    vu_carryover: VUForeignInfoCarryover | None,
    vn_carryover: VNStateCarryover | None,
    state_before: dict[str, object],
    state_after: dict[str, object],
) -> dict[str, object]:
    return {
        "from_period": transition["from_period"],
        "to_period": transition["to_period"],
        "from_global_period": previous_result.global_period,
        "to_global_period": compute_global_period(next_loaded.context),
        "vu_carryover_requested": transition["carry_forward_vu_state"],
        "vn_carryover_requested": transition["carry_forward_vn_state"],
        "vu_carryover_executed": vu_carryover is not None,
        "vn_carryover_executed": vn_carryover is not None,
        "carried_insurer_ids": sorted(
            set(
                (vu_carryover.insurer_ids if vu_carryover is not None else [])
                + (vn_carryover.insurer_ids if vn_carryover is not None else [])
            )
        ),
        "carried_policyholder_ids": (
            sorted(vn_carryover.policyholder_ids)
            if vn_carryover is not None
            else []
        ),
        "state_before": deepcopy(state_before),
        "state_after": deepcopy(state_after),
        "state_changed": state_before != state_after,
    }


def _build_prefix_proof(
    baseline_payload: dict[str, object],
    reference: StrategyExecutionPrefixBaselineReference,
    *,
    period_effects: list[dict[str, object]],
    transition_effects: list[dict[str, object]],
) -> dict[str, object]:
    baseline_transition = baseline_payload.get("transition_effect")
    try:
        baseline_projection = build_strategy_execution_two_period_prefix_projection(
            period_effects=baseline_payload.get("period_effects"),
            transition_effects=[baseline_transition],
        )
        current_projection = build_strategy_execution_two_period_prefix_projection(
            period_effects=period_effects,
            transition_effects=transition_effects,
        )
        baseline_bytes = canonical_strategy_execution_prefix_bytes(
            baseline_projection
        )
        current_bytes = canonical_strategy_execution_prefix_bytes(current_projection)
    except (TypeError, ValueError, OverflowError) as exc:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "prefix_projection_invalid",
            f"Prefixprojektion konnte nicht kanonisch gebildet werden: {exc}",
            runner_invocation_count=len(period_effects),
            carryover_invocation_count=sum(
                int(effect.get("vu_carryover_executed") is True)
                + int(effect.get("vn_carryover_executed") is True)
                for effect in transition_effects
            ),
            candidate_reverified_count=5,
            prefix_baseline_verified=True,
        ) from exc
    semantic_equal = baseline_projection == current_projection
    byte_equal = baseline_bytes == current_bytes
    return {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_PREFIX_PROJECTION_VERSION,
        "baseline_chain_id": reference.chain_id,
        "baseline_content_digest": reference.expected_content_digest,
        "baseline_result_digest": reference.expected_result_digest,
        "baseline_projection_digest": calculate_strategy_execution_prefix_digest(
            baseline_projection
        ),
        "five_period_projection_digest": calculate_strategy_execution_prefix_digest(
            current_projection
        ),
        "canonical_json_byte_count": len(current_bytes),
        "semantic_equal": semantic_equal,
        "canonical_json_byte_equal": byte_equal,
        "tolerance_applied": False,
        "prefix_equal": semantic_equal and byte_equal,
    }


def _verify_source_candidates_unchanged(
    period_chain: dict[str, object],
    source_candidates: tuple[dict[str, object], ...],
    *,
    db_path: Path | str,
    runner_invocation_count: int,
    carryover_invocation_count: int,
    candidate_reverified_count: int,
) -> None:
    references = period_chain.get("period_candidates")
    fresh: list[dict[str, object]] = []
    try:
        if isinstance(references, list):
            for reference in references:
                if isinstance(reference, dict):
                    fresh.append(
                        deepcopy(
                            get_strategy_execution_candidate(
                                str(reference.get("candidate_id", "")),
                                db_path=db_path,
                            ).record.candidate
                        )
                    )
    except StrategyExecutionCandidateStoreError as exc:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "source_candidate_reverification_failed",
            f"Kandidaten konnten nach der Probe nicht geprueft werden: {exc}",
            runner_invocation_count=runner_invocation_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            prefix_baseline_verified=True,
        ) from exc
    if tuple(fresh) != source_candidates:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "source_candidate_mutated",
            "Fuenf-Perioden-Wirkungsprobe hat einen Kandidaten veraendert",
            runner_invocation_count=runner_invocation_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            prefix_baseline_verified=True,
        )


def _require_exact_fields(
    value: dict[str, object],
    expected: frozenset[str],
    section: str,
) -> None:
    actual = frozenset(value)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "missing_request_fields",
            f"{section} vermisst Pflichtfelder: " + ", ".join(missing),
        )
    if unknown:
        raise StrategyExecutionFivePeriodEffectProbeError(
            "unknown_request_fields",
            f"{section} enthaelt unbekannte Felder: " + ", ".join(unknown),
        )


def _required_text(value: dict[str, object], field_name: str) -> str:
    field = value[field_name]
    if not isinstance(field, str) or not field.strip():
        raise StrategyExecutionFivePeriodEffectProbeError(
            f"{field_name}_required",
            f"prefix_baseline.{field_name} muss nichtleer sein",
        )
    return field


def _required_digest(value: dict[str, object], field_name: str) -> str:
    field = _required_text(value, field_name)
    digest_hex = field.removeprefix("sha256:")
    if (
        not field.startswith("sha256:")
        or len(digest_hex) != 64
        or digest_hex.lower() != digest_hex
    ):
        raise StrategyExecutionFivePeriodEffectProbeError(
            f"{field_name}_invalid",
            f"prefix_baseline.{field_name} muss ein kleingeschriebener SHA-256-Digest sein",
        )
    try:
        int(digest_hex, 16)
    except ValueError as exc:
        raise StrategyExecutionFivePeriodEffectProbeError(
            f"{field_name}_invalid",
            f"prefix_baseline.{field_name} muss ein kleingeschriebener SHA-256-Digest sein",
        ) from exc
    return field
