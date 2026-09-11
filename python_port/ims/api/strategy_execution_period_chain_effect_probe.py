from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

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
from ims.api.strategy_execution_period_chain_resolution import (
    resolve_strategy_execution_period_chain_input,
)
from ims.api.strategy_execution_period_chain_run_control import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION,
    StrategyExecutionPeriodChainRunControlRequest,
    StrategyExecutionPeriodChainRunControlResult,
    check_strategy_execution_period_chain_run_control_release,
    parse_strategy_execution_period_chain_run_control_request,
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
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)
from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)
from ims.strategies.execution_period_chain_validation import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
)


STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_CONTRACT_VERSION = (
    "ims.strategy-execution-period-chain-effect-probe-contract.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION = (
    "ims.strategy-execution-period-chain-effect-probe-request.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_VERSION = (
    "ims.strategy-execution-period-chain-effect-probe-result.v1"
)

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "release",
        "explicit_two_period_effect_probe_execution",
    }
)


class StrategyExecutionPeriodChainEffectProbeError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        runner_invocation_count: int = 0,
        carryover_invocation_count: int = 0,
        candidate_reverified_count: int = 0,
        release_check: StrategyExecutionPeriodChainRunControlResult | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.runner_invocation_count = runner_invocation_count
        self.carryover_invocation_count = carryover_invocation_count
        self.candidate_reverified_count = candidate_reverified_count
        self.release_check = release_check


class StrategyExecutionPeriodChainEffectProbeRunner(Protocol):
    def __call__(
        self,
        loaded: LoadedScenario,
        *,
        output_dir: str | Path | None = None,
    ) -> ExplicitPeriodRunResult:
        ...


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainEffectProbeRequest:
    release: StrategyExecutionPeriodChainRunControlRequest
    explicit_two_period_effect_probe_execution: bool
    schema_version: str = STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "release": self.release.to_dict(),
            "explicit_two_period_effect_probe_execution": (
                self.explicit_two_period_effect_probe_execution
            ),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainEffectProbeResult:
    request: StrategyExecutionPeriodChainEffectProbeRequest
    release_check: StrategyExecutionPeriodChainRunControlResult
    period_effects: tuple[dict[str, object], ...]
    transition_effect: dict[str, object] | None
    candidate_reverified_count: int

    @property
    def execution_performed(self) -> bool:
        return len(self.period_effects) == 2 and self.transition_effect is not None

    def to_dict(self) -> dict[str, object]:
        transition = deepcopy(self.transition_effect)
        carryover_count = _transition_carryover_count(transition)
        return {
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_VERSION
            ),
            "request_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION
            ),
            "release_request_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
            ),
            "mode": "strategy_execution_period_chain_effect_probe",
            "status": "ok" if self.execution_performed else "blocked",
            "request": self.request.to_dict(),
            "release_check": self.release_check.to_dict(),
            "issue_count": len(self.release_check.issues),
            "issues": [dict(issue) for issue in self.release_check.issues],
            "period_effects": [deepcopy(effect) for effect in self.period_effects],
            "transition_effect": transition,
            "period_chain_release_checked": True,
            "two_period_horizon_verified": self.execution_performed,
            "candidate_re_resolution_performed": (
                self.candidate_reverified_count > 0
            ),
            "candidate_reverified_count": self.candidate_reverified_count,
            "candidate_copies_isolated": self.execution_performed,
            "source_candidates_mutated": False,
            "stored_transition_flags_applied_exactly": self.execution_performed,
            "effect_probe_execution_released": (
                self.request.explicit_two_period_effect_probe_execution
            ),
            "period_count": len(self.period_effects),
            "runner_invocation_count": len(self.period_effects),
            "runner_invocation_performed": bool(self.period_effects),
            "carryover_invocation_count": carryover_count,
            "carryover_invocation_performed": carryover_count > 0,
            "queue_entry_created": False,
            "preflight_performed": False,
            "result_persisted": False,
            "idempotency_persisted": False,
            "writes_performed": False,
            "execution_performed": self.execution_performed,
            "output_files_written": False,
            "legacy_comparison_performed": False,
            "partial_result_returned": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR140",
        }


@dataclass(frozen=True, slots=True)
class _PreparedTwoPeriodProbe:
    loaded_scenarios: tuple[LoadedScenario, LoadedScenario]
    source_candidates: tuple[dict[str, object], dict[str, object]]
    carry_forward_vu_state: bool
    carry_forward_vn_state: bool
    candidate_reverified_count: int


def parse_strategy_execution_period_chain_effect_probe_request(
    value: object,
) -> StrategyExecutionPeriodChainEffectProbeRequest:
    if not isinstance(value, dict):
        raise StrategyExecutionPeriodChainEffectProbeError(
            "request_object_required",
            "Zwei-Perioden-Wirkungsprobe verlangt ein JSON-Objekt",
        )
    actual_fields = frozenset(value)
    missing_fields = sorted(_REQUEST_FIELDS - actual_fields)
    unknown_fields = sorted(actual_fields - _REQUEST_FIELDS)
    if missing_fields:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "missing_request_fields",
            "Zwei-Perioden-Wirkungsprobe vermisst Pflichtfelder: "
            + ", ".join(missing_fields),
        )
    if unknown_fields:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "unknown_request_fields",
            "Zwei-Perioden-Wirkungsprobe enthaelt unbekannte Felder: "
            + ", ".join(unknown_fields),
        )
    if value["schema_version"] != (
        STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION
    ):
        raise StrategyExecutionPeriodChainEffectProbeError(
            "unsupported_schema_version",
            "Zwei-Perioden-Wirkungsprobe erwartet schema_version "
            f"{STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION}",
        )
    if value["explicit_two_period_effect_probe_execution"] is not True:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "effect_probe_execution_release_required",
            "Zwei-Perioden-Wirkungsprobe muss explizit freigegeben sein",
        )
    try:
        release = parse_strategy_execution_period_chain_run_control_request(
            value["release"]
        )
    except ValueError as exc:
        code = getattr(exc, "code", "release_request_invalid")
        raise StrategyExecutionPeriodChainEffectProbeError(code, str(exc)) from exc
    return StrategyExecutionPeriodChainEffectProbeRequest(
        release=release,
        explicit_two_period_effect_probe_execution=True,
    )


def run_strategy_execution_period_chain_effect_probe(
    request: StrategyExecutionPeriodChainEffectProbeRequest,
    *,
    db_path: Path | str,
    runner: StrategyExecutionPeriodChainEffectProbeRunner | None = None,
) -> StrategyExecutionPeriodChainEffectProbeResult:
    release_check = check_strategy_execution_period_chain_run_control_release(
        request.release,
        db_path=db_path,
    )
    if not release_check.release_ready:
        return StrategyExecutionPeriodChainEffectProbeResult(
            request=request,
            release_check=release_check,
            period_effects=(),
            transition_effect=None,
            candidate_reverified_count=0,
        )
    record = release_check.record
    if record is None:  # pragma: no cover - protected by release_ready.
        raise StrategyExecutionPeriodChainEffectProbeError(
            "released_period_chain_record_missing",
            "Freigegebene Periodenkette hat keinen Speicherdatensatz",
            release_check=release_check,
        )

    prepared = _prepare_two_period_probe(
        record.period_chain,
        expected_run_index=record.run_index,
        db_path=db_path,
        release_check=release_check,
    )
    loaded_first, loaded_second = prepared.loaded_scenarios
    effective_runner = runner or run_loaded_explicit_period
    period_effects: list[dict[str, object]] = []
    runner_count = 0
    carryover_count = 0

    first_before = project_strategy_execution_state(loaded_first)
    first_result = _run_period(
        effective_runner,
        loaded_first,
        expected_period=1,
        runner_invocation_count=runner_count,
        carryover_invocation_count=carryover_count,
        candidate_reverified_count=prepared.candidate_reverified_count,
        release_check=release_check,
    )
    runner_count += 1
    first_after = project_strategy_execution_state(loaded_first)
    period_effects.append(
        build_strategy_execution_period_effect(
            first_result,
            state_before=first_before,
            state_after=first_after,
        )
    )

    transition_before = project_strategy_execution_state(loaded_second)
    vu_carryover: VUForeignInfoCarryover | None = None
    vn_carryover: VNStateCarryover | None = None
    try:
        if prepared.carry_forward_vu_state:
            vu_carryover = apply_vu_foreign_info_carryover(
                first_result.vu_result,
                loaded_second,
            )
            carryover_count += 1
        if prepared.carry_forward_vn_state:
            vn_carryover = apply_vn_state_carryover(
                first_result.vn_result,
                loaded_second,
            )
            carryover_count += 1
    except Exception as exc:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "effect_probe_carryover_failed",
            f"Zwei-Perioden-Carryover ist fehlgeschlagen: {exc}",
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=prepared.candidate_reverified_count,
            release_check=release_check,
        ) from exc
    _validate_requested_carryovers(
        vu_requested=prepared.carry_forward_vu_state,
        vn_requested=prepared.carry_forward_vn_state,
        vu_carryover=vu_carryover,
        vn_carryover=vn_carryover,
        runner_invocation_count=runner_count,
        carryover_invocation_count=carryover_count,
        candidate_reverified_count=prepared.candidate_reverified_count,
        release_check=release_check,
    )
    transition_after = project_strategy_execution_state(loaded_second)
    transition_effect = _transition_effect_payload(
        first_result,
        loaded_second,
        vu_requested=prepared.carry_forward_vu_state,
        vn_requested=prepared.carry_forward_vn_state,
        vu_carryover=vu_carryover,
        vn_carryover=vn_carryover,
        state_before=transition_before,
        state_after=transition_after,
    )

    second_before = project_strategy_execution_state(loaded_second)
    second_result = _run_period(
        effective_runner,
        loaded_second,
        expected_period=2,
        runner_invocation_count=runner_count,
        carryover_invocation_count=carryover_count,
        candidate_reverified_count=prepared.candidate_reverified_count,
        release_check=release_check,
    )
    runner_count += 1
    second_after = project_strategy_execution_state(loaded_second)
    period_effects.append(
        build_strategy_execution_period_effect(
            second_result,
            state_before=second_before,
            state_after=second_after,
        )
    )

    try:
        fresh_candidates = _fresh_candidate_payloads(
            record.period_chain,
            db_path=db_path,
        )
    except StrategyExecutionCandidateStoreError as exc:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "source_candidate_reverification_failed",
            f"Gespeicherte Kandidaten konnten nach der Probe nicht erneut "
            f"geprueft werden: {exc}",
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=prepared.candidate_reverified_count,
            release_check=release_check,
        ) from exc
    if fresh_candidates != prepared.source_candidates:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "source_candidate_mutated",
            "Zwei-Perioden-Wirkungsprobe hat einen gespeicherten Kandidaten veraendert",
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=prepared.candidate_reverified_count,
            release_check=release_check,
        )

    return StrategyExecutionPeriodChainEffectProbeResult(
        request=request,
        release_check=release_check,
        period_effects=tuple(period_effects),
        transition_effect=transition_effect,
        candidate_reverified_count=prepared.candidate_reverified_count,
    )


def strategy_execution_period_chain_effect_probe_contract_payload() -> dict[
    str, object
]:
    boundary_flags = {
        "explicit_run_control_release_required": True,
        "explicit_two_period_effect_probe_execution_required": True,
        "stored_period_chain_required": True,
        "period_chain_digest_reverification_required": True,
        "exact_two_period_horizon_required": True,
        "candidate_re_resolution_required": True,
        "candidate_digest_reverification_required": True,
        "all_inputs_validated_before_first_runner": True,
        "isolated_candidate_copies_required": True,
        "stored_transition_flags_authoritative": True,
        "atomic_partial_result_suppression_enabled": True,
        "effect_probe_execution_enabled": True,
        "ui_start_enabled": False,
        "queue_write_enabled": False,
        "idempotency_persistence_enabled": False,
        "result_persistence_enabled": False,
        "output_files_enabled": False,
        "legacy_comparison_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_CONTRACT_VERSION
        ),
        "request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION
        ),
        "result_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_VERSION
        ),
        "release_request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
        ),
        "mode": "strategy_execution_period_chain_effect_probe_contract",
        "scope": "one_released_chain_two_isolated_periods_one_transition",
        "contract_endpoint": (
            "/api/run-control/strategy-period-chain-effect-probe-contract"
        ),
        "execution_endpoint": (
            "/api/run-control/strategy-period-chain-effect-probe"
        ),
        "request_fields": sorted(_REQUEST_FIELDS),
        "forbidden_request_fields": [
            "period_chain",
            "period_chain_input",
            "candidate",
            "candidate_payload",
            "db_path",
            "fixture_path",
            "output_dir",
            "carry_forward_vu_state",
            "carry_forward_vn_state",
            "legacy_targets",
        ],
        "execution_order": [
            "reverify_stored_period_chain_release",
            "require_exact_two_period_horizon_and_transition",
            "reresolve_both_candidates_and_reverify_digests",
            "load_and_cross_check_both_isolated_candidate_copies",
            "run_period_1",
            "apply_exact_stored_vu_and_vn_carryover_flags",
            "run_period_2",
            "return_ephemeral_complete_result_only",
        ],
        "next_gate": "PR140",
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }


def strategy_execution_period_chain_effect_probe_error_payload(
    code: str,
    message: str,
    *,
    runner_invocation_count: int = 0,
    carryover_invocation_count: int = 0,
    candidate_reverified_count: int = 0,
    release_check: StrategyExecutionPeriodChainRunControlResult | None = None,
) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_VERSION,
        "request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION
        ),
        "mode": "strategy_execution_period_chain_effect_probe",
        "status": "error",
        "release_check": (
            release_check.to_dict() if release_check is not None else None
        ),
        "issue_count": 1,
        "issues": [{"code": code, "message": message}],
        "period_effects": [],
        "transition_effect": None,
        "period_chain_release_checked": release_check is not None,
        "two_period_horizon_verified": False,
        "candidate_re_resolution_performed": candidate_reverified_count > 0,
        "candidate_reverified_count": candidate_reverified_count,
        "candidate_copies_isolated": False,
        "source_candidates_mutated": False,
        "stored_transition_flags_applied_exactly": False,
        "effect_probe_execution_released": release_check is not None,
        "period_count": 0,
        "runner_invocation_count": runner_invocation_count,
        "runner_invocation_performed": runner_invocation_count > 0,
        "carryover_invocation_count": carryover_invocation_count,
        "carryover_invocation_performed": carryover_invocation_count > 0,
        "partial_result_returned": False,
        "queue_entry_created": False,
        "preflight_performed": False,
        "adapter_started": False,
        "result_persisted": False,
        "idempotency_persisted": False,
        "writes_performed": False,
        "execution_performed": False,
        "output_files_written": False,
        "legacy_comparison_performed": False,
        "simulation_performed": False,
        "automatic_historical_rule_selection_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR140",
    }


def _prepare_two_period_probe(
    period_chain: dict[str, object],
    *,
    expected_run_index: int,
    db_path: Path | str,
    release_check: StrategyExecutionPeriodChainRunControlResult,
) -> _PreparedTwoPeriodProbe:
    horizon = _required_mapping(period_chain, "horizon", release_check)
    references = _required_list(period_chain, "period_candidates", release_check)
    transitions = _required_list(period_chain, "transitions", release_check)
    if (
        horizon.get("first_period") != 1
        or horizon.get("last_period") != 2
        or horizon.get("period_count") != 2
        or horizon.get("max_periods") != 2
        or len(references) != 2
        or len(transitions) != 1
    ):
        raise StrategyExecutionPeriodChainEffectProbeError(
            "exact_two_period_horizon_required",
            "Wirkungsprobe akzeptiert genau die gespeicherten Perioden 1 und 2",
            release_check=release_check,
        )
    transition = transitions[0]
    if not isinstance(transition, dict):
        raise StrategyExecutionPeriodChainEffectProbeError(
            "transition_object_required",
            "Gespeicherter Uebergang muss ein Objekt sein",
            release_check=release_check,
        )
    if transition.get("from_period") != 1 or transition.get("to_period") != 2:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "two_period_transition_required",
            "Wirkungsprobe verlangt genau den Uebergang von Periode 1 nach 2",
            release_check=release_check,
        )
    vu_flag = transition.get("carry_forward_vu_state")
    vn_flag = transition.get("carry_forward_vn_state")
    if not isinstance(vu_flag, bool) or not isinstance(vn_flag, bool):
        raise StrategyExecutionPeriodChainEffectProbeError(
            "explicit_transition_flags_required",
            "Gespeicherter Uebergang verlangt explizite boolesche Carryover-Flags",
            release_check=release_check,
        )

    chain_input = {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "base_model": period_chain.get("base_model"),
        "scope": "contiguous_local_period_chain_input",
        "run_index": expected_run_index,
        "max_periods": 2,
        "period_candidates": deepcopy(references),
        "transitions": deepcopy(transitions),
    }
    resolution = resolve_strategy_execution_period_chain_input(
        chain_input,
        db_path=db_path,
    )
    if not resolution.resolution_ready:
        codes = ", ".join(issue.code for issue in resolution.issues)
        detail = f": {codes}" if codes else ""
        raise StrategyExecutionPeriodChainEffectProbeError(
            "candidate_re_resolution_failed",
            "Beide Kandidaten konnten nicht atomar erneut geprueft werden"
            + detail,
            candidate_reverified_count=(
                resolution.digest_verified_candidate_count
            ),
            release_check=release_check,
        )

    records = _resolve_candidate_records(
        references,
        db_path=db_path,
        release_check=release_check,
    )
    source_candidates = tuple(deepcopy(record.candidate) for record in records)
    loaded_scenarios: list[LoadedScenario] = []
    try:
        for record in records:
            candidate_copy = deepcopy(record.candidate)
            loaded_scenarios.append(
                load_scenario_from_mapping(
                    build_strategy_execution_candidate_scenario_mapping(
                        candidate_copy
                    )
                )
            )
    except (ScenarioValidationError, TypeError, ValueError, OverflowError) as exc:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "candidate_copy_load_failed",
            f"Isolierte Kandidatenkopien konnten nicht geladen werden: {exc}",
            candidate_reverified_count=len(records),
            release_check=release_check,
        ) from exc
    _validate_loaded_scenarios(
        loaded_scenarios,
        expected_run_index=expected_run_index,
        release_check=release_check,
    )
    return _PreparedTwoPeriodProbe(
        loaded_scenarios=(loaded_scenarios[0], loaded_scenarios[1]),
        source_candidates=(source_candidates[0], source_candidates[1]),
        carry_forward_vu_state=vu_flag,
        carry_forward_vn_state=vn_flag,
        candidate_reverified_count=len(records),
    )


def _resolve_candidate_records(
    references: list[object],
    *,
    db_path: Path | str,
    release_check: StrategyExecutionPeriodChainRunControlResult,
) -> tuple[
    StrategyExecutionCandidateStoreRecord,
    StrategyExecutionCandidateStoreRecord,
]:
    records: list[StrategyExecutionCandidateStoreRecord] = []
    for index, reference in enumerate(references):
        if not isinstance(reference, dict):
            raise StrategyExecutionPeriodChainEffectProbeError(
                "candidate_reference_object_required",
                f"Kandidatenreferenz {index} muss ein Objekt sein",
                candidate_reverified_count=len(records),
                release_check=release_check,
            )
        try:
            stored = get_strategy_execution_candidate(
                str(reference.get("candidate_id", "")),
                db_path=db_path,
            )
        except StrategyExecutionCandidateStoreError as exc:
            raise StrategyExecutionPeriodChainEffectProbeError(
                "candidate_re_resolution_failed",
                f"Kandidat {index + 1} konnte nicht erneut geprueft werden: {exc}",
                candidate_reverified_count=len(records),
                release_check=release_check,
            ) from exc
        record = stored.record
        if (
            record.candidate_id != reference.get("candidate_id")
            or record.content_digest != reference.get("content_digest")
            or record.period != reference.get("period")
            or not stored.post_storage_digest_verified
        ):
            raise StrategyExecutionPeriodChainEffectProbeError(
                "candidate_reference_changed",
                f"Kandidat {index + 1} weicht von der gespeicherten Kette ab",
                candidate_reverified_count=len(records),
                release_check=release_check,
            )
        records.append(record)
    if len(records) != 2:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "exact_two_candidates_required",
            "Wirkungsprobe verlangt genau zwei erneut gepruefte Kandidaten",
            candidate_reverified_count=len(records),
            release_check=release_check,
        )
    return records[0], records[1]


def _validate_loaded_scenarios(
    loaded_scenarios: list[LoadedScenario],
    *,
    expected_run_index: int,
    release_check: StrategyExecutionPeriodChainRunControlResult,
) -> None:
    if len(loaded_scenarios) != 2:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "exact_two_loaded_candidates_required",
            "Wirkungsprobe verlangt genau zwei geladene Kandidatenkopien",
            candidate_reverified_count=len(loaded_scenarios),
            release_check=release_check,
        )
    if [loaded.context.period for loaded in loaded_scenarios] != [1, 2]:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "loaded_candidate_periods_mismatch",
            "Geladene Kandidatenkopien muessen die Perioden 1 und 2 abbilden",
            candidate_reverified_count=2,
            release_check=release_check,
        )
    if any(
        loaded.context.run_index != expected_run_index
        or loaded.context.max_periods != 2
        for loaded in loaded_scenarios
    ):
        raise StrategyExecutionPeriodChainEffectProbeError(
            "loaded_candidate_context_mismatch",
            "Geladene Kandidatenkopien weichen vom Kettenkontext ab",
            candidate_reverified_count=2,
            release_check=release_check,
        )
    global_periods = [
        compute_global_period(loaded.context) for loaded in loaded_scenarios
    ]
    if global_periods[1] != global_periods[0] + 1:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "loaded_candidate_global_period_mismatch",
            "Geladene Kandidatenkopien bilden keine benachbarten Globalperioden",
            candidate_reverified_count=2,
            release_check=release_check,
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
    if identities[0] != identities[1]:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "loaded_candidate_actor_identity_mismatch",
            "Geladene Kandidatenkopien haben unterschiedliche Akteursidentitaeten",
            candidate_reverified_count=2,
            release_check=release_check,
        )


def _run_period(
    runner: StrategyExecutionPeriodChainEffectProbeRunner,
    loaded: LoadedScenario,
    *,
    expected_period: int,
    runner_invocation_count: int,
    carryover_invocation_count: int,
    candidate_reverified_count: int,
    release_check: StrategyExecutionPeriodChainRunControlResult,
) -> ExplicitPeriodRunResult:
    attempted_count = runner_invocation_count + 1
    try:
        result = runner(loaded, output_dir=None)
    except Exception as exc:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "effect_probe_runner_failed",
            f"Zwei-Perioden-Wirkungsprobe ist in Periode {expected_period} "
            f"fehlgeschlagen: {exc}",
            runner_invocation_count=attempted_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            release_check=release_check,
        ) from exc
    if result.period != expected_period:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "runner_period_mismatch",
            f"Runner meldet fuer Periode {expected_period} eine andere Periode",
            runner_invocation_count=attempted_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            release_check=release_check,
        )
    if result.written_files:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "effect_probe_wrote_files",
            "Zwei-Perioden-Wirkungsprobe darf keine Dateien schreiben",
            runner_invocation_count=attempted_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            release_check=release_check,
        )
    return result


def _validate_requested_carryovers(
    *,
    vu_requested: bool,
    vn_requested: bool,
    vu_carryover: VUForeignInfoCarryover | None,
    vn_carryover: VNStateCarryover | None,
    runner_invocation_count: int,
    carryover_invocation_count: int,
    candidate_reverified_count: int,
    release_check: StrategyExecutionPeriodChainRunControlResult,
) -> None:
    if vu_requested and vu_carryover is None:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "requested_vu_carryover_missing",
            "Freigegebener VU-Carryover hat keinen Zustand uebertragen",
            runner_invocation_count=runner_invocation_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            release_check=release_check,
        )
    if vn_requested and vn_carryover is None:
        raise StrategyExecutionPeriodChainEffectProbeError(
            "requested_vn_carryover_missing",
            "Freigegebener VN-Carryover hat keinen Zustand uebertragen",
            runner_invocation_count=runner_invocation_count,
            carryover_invocation_count=carryover_invocation_count,
            candidate_reverified_count=candidate_reverified_count,
            release_check=release_check,
        )
    for carryover in (vu_carryover, vn_carryover):
        if carryover is not None and (
            carryover.from_period != 1 or carryover.to_period != 2
        ):
            raise StrategyExecutionPeriodChainEffectProbeError(
                "carryover_period_mismatch",
                "Carryover meldet nicht den Uebergang von Periode 1 nach 2",
                runner_invocation_count=runner_invocation_count,
                carryover_invocation_count=carryover_invocation_count,
                candidate_reverified_count=candidate_reverified_count,
                release_check=release_check,
            )


def _transition_effect_payload(
    first_result: ExplicitPeriodRunResult,
    loaded_second: LoadedScenario,
    *,
    vu_requested: bool,
    vn_requested: bool,
    vu_carryover: VUForeignInfoCarryover | None,
    vn_carryover: VNStateCarryover | None,
    state_before: dict[str, object],
    state_after: dict[str, object],
) -> dict[str, object]:
    return {
        "from_period": 1,
        "to_period": 2,
        "from_global_period": first_result.global_period,
        "to_global_period": compute_global_period(loaded_second.context),
        "vu_carryover_requested": vu_requested,
        "vn_carryover_requested": vn_requested,
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


def _transition_carryover_count(transition: object) -> int:
    if not isinstance(transition, dict):
        return 0
    return int(transition.get("vu_carryover_executed") is True) + int(
        transition.get("vn_carryover_executed") is True
    )


def _fresh_candidate_payloads(
    period_chain: dict[str, object],
    *,
    db_path: Path | str,
) -> tuple[dict[str, object], ...]:
    references = period_chain.get("period_candidates")
    if not isinstance(references, list):
        return ()
    return tuple(
        deepcopy(
            get_strategy_execution_candidate(
                str(reference.get("candidate_id", "")),
                db_path=db_path,
            ).record.candidate
        )
        for reference in references
        if isinstance(reference, dict)
    )


def _required_mapping(
    value: dict[str, object],
    field_name: str,
    release_check: StrategyExecutionPeriodChainRunControlResult,
) -> dict[str, object]:
    field = value.get(field_name)
    if not isinstance(field, dict):
        raise StrategyExecutionPeriodChainEffectProbeError(
            "period_chain_section_invalid",
            f"Gespeicherte Periodenkette vermisst Objektabschnitt {field_name}",
            release_check=release_check,
        )
    return field


def _required_list(
    value: dict[str, object],
    field_name: str,
    release_check: StrategyExecutionPeriodChainRunControlResult,
) -> list[object]:
    field = value.get(field_name)
    if not isinstance(field, list):
        raise StrategyExecutionPeriodChainEffectProbeError(
            "period_chain_section_invalid",
            f"Gespeicherte Periodenkette vermisst Listenabschnitt {field_name}",
            release_check=release_check,
        )
    return field
