from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ims.api.strategy_execution_candidate_run_control import (
    STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
    StrategyExecutionCandidateRunControlRequest,
    StrategyExecutionCandidateRunControlResult,
    check_strategy_execution_candidate_run_control_release,
    parse_strategy_execution_candidate_run_control_request,
)
from ims.engine.explicit_period_runner import (
    ExplicitPeriodRunResult,
    run_loaded_explicit_period,
)
from ims.io.scenario_loader import (
    LoadedScenario,
    ScenarioValidationError,
    load_scenario_from_mapping,
)
from ims.model.entities import Insurer, Policyholder
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)


STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_CONTRACT_VERSION = (
    "ims.strategy-execution-candidate-effect-probe-contract.v1"
)
STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION = (
    "ims.strategy-execution-candidate-effect-probe-request.v1"
)
STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_VERSION = (
    "ims.strategy-execution-candidate-effect-probe-result.v1"
)

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "release",
        "explicit_effect_probe_execution",
    }
)
_CANDIDATE_COLLECTION_SECTIONS = (
    "vu_rule_snapshots",
    "vn_rule_snapshots",
    "vn_process_snapshots",
)


class StrategyExecutionCandidateEffectProbeError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        runner_invocation_performed: bool = False,
        release_check: StrategyExecutionCandidateRunControlResult | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.runner_invocation_performed = runner_invocation_performed
        self.release_check = release_check


class StrategyExecutionCandidateEffectProbeRunner(Protocol):
    def __call__(
        self,
        loaded: LoadedScenario,
        *,
        output_dir: str | Path | None = None,
    ) -> ExplicitPeriodRunResult:
        ...


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateEffectProbeRequest:
    release: StrategyExecutionCandidateRunControlRequest
    explicit_effect_probe_execution: bool
    schema_version: str = STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "release": self.release.to_dict(),
            "explicit_effect_probe_execution": self.explicit_effect_probe_execution,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateEffectProbeResult:
    request: StrategyExecutionCandidateEffectProbeRequest
    release_check: StrategyExecutionCandidateRunControlResult
    effect: dict[str, object] | None

    @property
    def execution_performed(self) -> bool:
        return self.effect is not None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_VERSION,
            "request_schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION
            ),
            "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
            "mode": "strategy_execution_candidate_effect_probe",
            "status": "ok" if self.execution_performed else "blocked",
            "request": self.request.to_dict(),
            "release_check": self.release_check.to_dict(),
            "issue_count": len(self.release_check.issues),
            "issues": [dict(issue) for issue in self.release_check.issues],
            "effect": deepcopy(self.effect),
            "candidate_resolved": self.release_check.candidate is not None,
            "candidate_digest_reverified": (
                self.release_check.release_ready
                and self.release_check.record is not None
            ),
            "run_control_release_checked": True,
            "effect_probe_execution_released": (
                self.request.explicit_effect_probe_execution
            ),
            "candidate_copy_isolated": self.execution_performed,
            "source_candidate_mutated": False,
            "period_count": 1 if self.execution_performed else 0,
            "queue_entry_created": False,
            "preflight_performed": False,
            "adapter_started": False,
            "runner_invocation_count": 1 if self.execution_performed else 0,
            "runner_invocation_performed": self.execution_performed,
            "result_persisted": False,
            "idempotency_persisted": False,
            "writes_performed": False,
            "execution_performed": self.execution_performed,
            "carryover_performed": False,
            "output_files_written": False,
            "legacy_comparison_performed": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR140",
        }


def parse_strategy_execution_candidate_effect_probe_request(
    value: object,
) -> StrategyExecutionCandidateEffectProbeRequest:
    if not isinstance(value, dict):
        raise StrategyExecutionCandidateEffectProbeError(
            "request_object_required",
            "Einperioden-Wirkungsprobe verlangt ein JSON-Objekt",
        )
    actual_fields = frozenset(value)
    missing_fields = sorted(_REQUEST_FIELDS - actual_fields)
    unknown_fields = sorted(actual_fields - _REQUEST_FIELDS)
    if missing_fields:
        raise StrategyExecutionCandidateEffectProbeError(
            "missing_request_fields",
            "Einperioden-Wirkungsprobe vermisst Pflichtfelder: "
            + ", ".join(missing_fields),
        )
    if unknown_fields:
        raise StrategyExecutionCandidateEffectProbeError(
            "unknown_request_fields",
            "Einperioden-Wirkungsprobe enthaelt unbekannte Felder: "
            + ", ".join(unknown_fields),
        )
    if value["schema_version"] != (
        STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION
    ):
        raise StrategyExecutionCandidateEffectProbeError(
            "unsupported_schema_version",
            "Einperioden-Wirkungsprobe erwartet schema_version "
            f"{STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION}",
        )
    if value["explicit_effect_probe_execution"] is not True:
        raise StrategyExecutionCandidateEffectProbeError(
            "effect_probe_execution_release_required",
            "Einperioden-Wirkungsprobe muss explizit zur Ausfuehrung freigegeben sein",
        )
    try:
        release = parse_strategy_execution_candidate_run_control_request(
            value["release"]
        )
    except ValueError as exc:
        code = getattr(exc, "code", "release_request_invalid")
        raise StrategyExecutionCandidateEffectProbeError(code, str(exc)) from exc
    return StrategyExecutionCandidateEffectProbeRequest(
        release=release,
        explicit_effect_probe_execution=True,
    )


def run_strategy_execution_candidate_effect_probe(
    request: StrategyExecutionCandidateEffectProbeRequest,
    *,
    db_path: Path | str,
    runner: StrategyExecutionCandidateEffectProbeRunner | None = None,
) -> StrategyExecutionCandidateEffectProbeResult:
    release_check = check_strategy_execution_candidate_run_control_release(
        request.release,
        db_path=db_path,
    )
    if not release_check.release_ready:
        return StrategyExecutionCandidateEffectProbeResult(
            request=request,
            release_check=release_check,
            effect=None,
        )
    record = release_check.record
    if record is None:  # pragma: no cover - protected by release_ready
        raise StrategyExecutionCandidateEffectProbeError(
            "released_candidate_record_missing",
            "Freigegebener Kandidat hat keinen aufgeloesten Speicherdatensatz",
            release_check=release_check,
        )

    source_before = deepcopy(record.candidate)
    candidate_copy = deepcopy(record.candidate)
    try:
        loaded = load_scenario_from_mapping(
            _candidate_scenario_mapping(candidate_copy)
        )
    except (ScenarioValidationError, TypeError, ValueError, OverflowError) as exc:
        raise StrategyExecutionCandidateEffectProbeError(
            "candidate_copy_load_failed",
            f"Isolierte Kandidatenkopie konnte nicht geladen werden: {exc}",
            release_check=release_check,
        ) from exc
    if loaded.context.period != record.period:
        raise StrategyExecutionCandidateEffectProbeError(
            "candidate_period_mismatch",
            "Isolierte Kandidatenkopie weicht von der gespeicherten Periode ab",
            release_check=release_check,
        )

    state_before = _state_projection(loaded)
    effective_runner = runner or run_loaded_explicit_period
    try:
        period_result = effective_runner(loaded, output_dir=None)
    except Exception as exc:
        raise StrategyExecutionCandidateEffectProbeError(
            "effect_probe_runner_failed",
            f"Einperioden-Wirkungsprobe ist fehlgeschlagen: {exc}",
            runner_invocation_performed=True,
            release_check=release_check,
        ) from exc
    _validate_period_result(
        period_result,
        expected_period=record.period,
        release_check=release_check,
    )
    if record.candidate != source_before:
        raise StrategyExecutionCandidateEffectProbeError(
            "source_candidate_mutated",
            "Einperioden-Wirkungsprobe hat den gespeicherten Kandidaten veraendert",
            runner_invocation_performed=True,
            release_check=release_check,
        )
    state_after = _state_projection(loaded)
    effect = _effect_payload(
        period_result,
        state_before=state_before,
        state_after=state_after,
    )
    return StrategyExecutionCandidateEffectProbeResult(
        request=request,
        release_check=release_check,
        effect=effect,
    )


def strategy_execution_candidate_effect_probe_contract_payload() -> dict[str, object]:
    boundary_flags = {
        "explicit_run_control_release_required": True,
        "explicit_effect_probe_execution_required": True,
        "stored_candidate_required": True,
        "candidate_digest_reverification_required": True,
        "isolated_candidate_copy_required": True,
        "single_period_only": True,
        "effect_probe_execution_enabled": True,
        "ui_start_enabled": False,
        "queue_write_enabled": False,
        "preflight_enabled": False,
        "adapter_start_enabled": False,
        "idempotency_persistence_enabled": False,
        "automatic_replay_protection_enabled": False,
        "result_persistence_enabled": False,
        "carryover_enabled": False,
        "output_files_enabled": False,
        "legacy_comparison_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_CONTRACT_VERSION
        ),
        "request_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION
        ),
        "result_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_VERSION
        ),
        "release_request_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION
        ),
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_candidate_effect_probe_contract_read_only",
        "scope": "one_released_candidate_one_isolated_period_effect_probe",
        "contract_endpoint": (
            "/api/run-control/strategy-candidate-effect-probe-contract"
        ),
        "execution_endpoint": (
            "/api/run-control/strategy-candidate-effect-probe"
        ),
        "persistent_start_contract_endpoint": (
            "/api/run-control/strategy-candidate-effect-probe-start-contract"
        ),
        "persistent_start_endpoint": (
            "/api/run-control/strategy-candidate-effect-probe-start"
        ),
        "request_fields": sorted(_REQUEST_FIELDS),
        "forbidden_request_fields": [
            "candidate",
            "candidate_input",
            "db_path",
            "fixture_path",
            "output_dir",
            "carry_forward_vu_state",
            "carry_forward_vn_state",
            "legacy_targets",
        ],
        "effect_sections": [
            "period",
            "applications",
            "state_before",
            "state_after",
            "changed_insurer_ids",
            "changed_policyholder_ids",
            "in_memory_export",
        ],
        "next_gate": "PR140",
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }


def strategy_execution_candidate_effect_probe_error_payload(
    code: str,
    message: str,
    *,
    runner_invocation_performed: bool = False,
    release_check: StrategyExecutionCandidateRunControlResult | None = None,
) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_VERSION,
        "request_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION
        ),
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_candidate_effect_probe",
        "status": "error",
        "release_check": (
            release_check.to_dict() if release_check is not None else None
        ),
        "issue_count": 1,
        "issues": [{"code": code, "message": message}],
        "effect": None,
        "candidate_resolved": (
            release_check is not None and release_check.candidate is not None
        ),
        "candidate_digest_reverified": (
            release_check is not None and release_check.release_ready
        ),
        "run_control_release_checked": release_check is not None,
        "effect_probe_execution_released": release_check is not None,
        "candidate_copy_isolated": False,
        "source_candidate_mutated": False,
        "period_count": 0,
        "queue_entry_created": False,
        "preflight_performed": False,
        "adapter_started": False,
        "runner_invocation_count": int(runner_invocation_performed),
        "runner_invocation_performed": runner_invocation_performed,
        "result_persisted": False,
        "idempotency_persisted": False,
        "writes_performed": False,
        "execution_performed": False,
        "carryover_performed": False,
        "output_files_written": False,
        "legacy_comparison_performed": False,
        "simulation_performed": False,
        "automatic_historical_rule_selection_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR140",
    }


def _candidate_scenario_mapping(candidate: dict[str, object]) -> dict[str, object]:
    ground = _mapping(candidate, "market_ground_state")
    mapping = {
        "context": deepcopy(ground.get("simulation_context")),
        "bav": deepcopy(ground.get("bav")),
        "insurers": deepcopy(ground.get("insurers")),
        "policyholders": deepcopy(ground.get("policyholders")),
    }
    for section_name in _CANDIDATE_COLLECTION_SECTIONS:
        section = _mapping(candidate, section_name)
        collections = _mapping(section, "collections")
        for collection_name, values in collections.items():
            mapping[collection_name] = _collection_for_loader(
                collection_name,
                values,
            )
    return mapping


def build_strategy_execution_candidate_scenario_mapping(
    candidate: dict[str, object],
) -> dict[str, object]:
    """Stellt den bereits verwendeten Loader-Eingang fuer isolierte Proben bereit."""

    return _candidate_scenario_mapping(candidate)


def _collection_for_loader(
    collection_name: str,
    values: object,
) -> object:
    copied = deepcopy(values)
    if (
        collection_name != "vn_damage_settlement_snapshots"
        or not isinstance(copied, list)
    ):
        return copied
    for entry in copied:
        if isinstance(entry, dict) and entry.get("insurance_decisions") is None:
            entry.pop("insurance_decisions", None)
    return copied


def _mapping(value: dict[str, object], field_name: str) -> dict[str, object]:
    field = value.get(field_name)
    if not isinstance(field, dict):
        raise StrategyExecutionCandidateEffectProbeError(
            "candidate_section_invalid",
            f"Gespeicherter Kandidat vermisst Objektabschnitt {field_name}",
        )
    return field


def _state_projection(loaded: LoadedScenario) -> dict[str, object]:
    return {
        "insurers": [
            _insurer_projection(insurer)
            for insurer in sorted(loaded.insurers, key=lambda item: item.entity_id)
        ],
        "policyholders": [
            _policyholder_projection(policyholder)
            for policyholder in sorted(
                loaded.policyholders,
                key=lambda item: item.entity_id,
            )
        ],
    }


def project_strategy_execution_state(
    loaded: LoadedScenario,
) -> dict[str, object]:
    """Projiziert den fuer Wirkungsproben sichtbaren VU-/VN-Zustand."""

    return _state_projection(loaded)


def _insurer_projection(insurer: Insurer) -> dict[str, object]:
    return {
        "insurer_id": insurer.entity_id,
        "active": insurer.active,
        "premiums_current": insurer.premiums_current,
        "premiums_current_sector": list(insurer.premiums_current_sector),
        "advertising_current": insurer.advertising_current,
        "advertising_current_sector": list(insurer.advertising_current_sector),
        "reserves_current": list(insurer.reserves_current),
        "policyholders_current": insurer.policyholders_current,
        "policyholders_current_sector": list(insurer.policyholders_current_sector),
        "claims_count_current": list(insurer.claims_count_current),
        "claims_sum_current": list(insurer.claims_sum_current),
    }


def _policyholder_projection(policyholder: Policyholder) -> dict[str, object]:
    return {
        "policyholder_id": policyholder.entity_id,
        "active": policyholder.active,
        "insured_current": policyholder.insured_current,
        "insured_current_sector": list(policyholder.insured_current_sector),
        "chosen_insurer_current": policyholder.chosen_insurer_current,
        "chosen_insurer_sector_current": list(
            policyholder.chosen_insurer_sector_current
        ),
        "paid_premium_current": list(policyholder.paid_premium_current),
        "self_damage_current": list(policyholder.self_damage_current),
        "claim_sum_current": list(policyholder.claim_sum_current),
        "end_wealth_sector_current": list(
            policyholder.end_wealth_sector_current
        ),
        "end_wealth_current": policyholder.end_wealth_current,
    }


def _validate_period_result(
    result: ExplicitPeriodRunResult,
    *,
    expected_period: int,
    release_check: StrategyExecutionCandidateRunControlResult,
) -> None:
    if result.period != expected_period:
        raise StrategyExecutionCandidateEffectProbeError(
            "runner_period_mismatch",
            "Einperioden-Runner meldet eine unerwartete Periode",
            runner_invocation_performed=True,
            release_check=release_check,
        )
    if result.written_files:
        raise StrategyExecutionCandidateEffectProbeError(
            "effect_probe_wrote_files",
            "Einperioden-Wirkungsprobe darf keine Dateien schreiben",
            runner_invocation_performed=True,
            release_check=release_check,
        )


def _effect_payload(
    result: ExplicitPeriodRunResult,
    *,
    state_before: dict[str, object],
    state_after: dict[str, object],
) -> dict[str, object]:
    vu_counts = {
        "foreign_info": len(result.vu_result.rule_applications),
        "random_uniform": len(result.vu_result.random_uniform_applications),
        "random_normal": len(result.vu_result.random_normal_applications),
        "reserve_markup": len(result.vu_result.reserve_markup_applications),
        "net_switcher_markup": len(
            result.vu_result.net_switcher_markup_applications
        ),
        "expected_claim": len(result.vu_result.expected_claim_applications),
        "market_share_markup": len(
            result.vu_result.market_share_markup_applications
        ),
        "free_linear": len(result.vu_result.free_linear_applications),
    }
    vn_counts = {
        "insurance_rule": len(result.vn_result.insurance_rule_applications),
        "damage_settlement": len(
            result.vn_result.damage_settlement_applications
        ),
        "settlement": len(result.vn_result.settlement_applications),
    }
    return {
        "period": result.period,
        "global_period": result.global_period,
        "applications": {
            "vu": vu_counts,
            "vu_total": sum(vu_counts.values()),
            "vn": vn_counts,
            "vn_total": sum(vn_counts.values()),
        },
        "state_before": deepcopy(state_before),
        "state_after": deepcopy(state_after),
        "state_changed": state_before != state_after,
        "changed_insurer_ids": _changed_ids(
            state_before,
            state_after,
            collection="insurers",
            id_field="insurer_id",
        ),
        "changed_policyholder_ids": _changed_ids(
            state_before,
            state_after,
            collection="policyholders",
            id_field="policyholder_id",
        ),
        "in_memory_export": {
            "table_count": len(result.export_tables),
            "row_count": sum(len(table.rows) for table in result.export_tables),
            "written_file_count": 0,
        },
    }


def build_strategy_execution_period_effect(
    result: ExplicitPeriodRunResult,
    *,
    state_before: dict[str, object],
    state_after: dict[str, object],
) -> dict[str, object]:
    """Baut dieselbe Periodenwirkung fuer Ein- und Zwei-Perioden-Proben."""

    return _effect_payload(
        result,
        state_before=state_before,
        state_after=state_after,
    )


def _changed_ids(
    before: dict[str, object],
    after: dict[str, object],
    *,
    collection: str,
    id_field: str,
) -> list[int]:
    before_items = before.get(collection)
    after_items = after.get(collection)
    if not isinstance(before_items, list) or not isinstance(after_items, list):
        return []
    before_by_id = {
        int(item[id_field]): item
        for item in before_items
        if isinstance(item, dict) and id_field in item
    }
    after_by_id = {
        int(item[id_field]): item
        for item in after_items
        if isinstance(item, dict) and id_field in item
    }
    return sorted(
        item_id
        for item_id in set(before_by_id) | set(after_by_id)
        if before_by_id.get(item_id) != after_by_id.get(item_id)
    )
