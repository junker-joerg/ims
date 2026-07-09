from __future__ import annotations

from dataclasses import dataclass
import json
import sys
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.engine.core_validation_overview import build_carryover_probe_contract


@dataclass(frozen=True)
class CoreValidationCarryoverProbeApiContract:
    status: str
    mode: str
    schema_version: str
    endpoint: str
    expected_probe_mode: str
    expected_contract_mode: str
    source_builder: str
    expected_inputs: tuple[str, ...]
    required_preconditions: tuple[str, ...]
    accepted_payload_fields: tuple[str, ...]
    transition_fields: tuple[str, ...]
    carryover_request_fields: tuple[str, ...]
    carried_entity_fields: tuple[str, ...]
    boundary_fields: tuple[str, ...]
    forbidden_boundaries: tuple[str, ...]
    precomputed_probe_required: bool = True
    api_accepts_probe_payload: bool = False
    api_starts_probe: bool = False
    http_enabled: bool = True
    ui_enabled: bool = False
    writes_performed: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "schema_version": self.schema_version,
            "endpoint": self.endpoint,
            "expected_probe_mode": self.expected_probe_mode,
            "expected_contract_mode": self.expected_contract_mode,
            "source_builder": self.source_builder,
            "expected_inputs": list(self.expected_inputs),
            "required_preconditions": list(self.required_preconditions),
            "accepted_payload_fields": list(self.accepted_payload_fields),
            "transition_fields": list(self.transition_fields),
            "carryover_request_fields": list(self.carryover_request_fields),
            "carried_entity_fields": list(self.carried_entity_fields),
            "boundary_fields": list(self.boundary_fields),
            "forbidden_boundaries": list(self.forbidden_boundaries),
            "precomputed_probe_required": self.precomputed_probe_required,
            "api_accepts_probe_payload": self.api_accepts_probe_payload,
            "api_starts_probe": self.api_starts_probe,
            "http_enabled": self.http_enabled,
            "ui_enabled": self.ui_enabled,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
        }


def build_core_validation_carryover_probe_api_contract() -> CoreValidationCarryoverProbeApiContract:
    core_contract = build_carryover_probe_contract()
    return CoreValidationCarryoverProbeApiContract(
        status="ok",
        mode="core_validation_carryover_probe_api_contract",
        schema_version=METADATA_SCHEMA_VERSION,
        endpoint="/api/core-validation/carryover-probe-contract",
        expected_probe_mode=core_contract.probe_mode,
        expected_contract_mode=core_contract.mode,
        source_builder=core_contract.source_builder,
        expected_inputs=("precomputed_explicit_transition_carryover_probe_payload",),
        required_preconditions=(
            "carryover_probe_payload_precomputed_outside_api",
            "core_validation_overview_contract_visible",
            "execution_enabled_false",
            "writes_enabled_false",
        ),
        accepted_payload_fields=tuple(core_contract.required_fields),
        transition_fields=tuple(core_contract.transition_fields),
        carryover_request_fields=tuple(core_contract.carryover_request_fields),
        carried_entity_fields=tuple(core_contract.carried_entity_fields),
        boundary_fields=tuple(core_contract.boundary_fields),
        forbidden_boundaries=(
            "probe_execution_from_api",
            "simulation_execution",
            "runner_start",
            "fachlogik_mutation",
            "metadata_write",
            "http_write_endpoint",
            "browser_upload",
            "browser_download",
            "historical_full_equality_claim",
        ),
    )


def core_validation_carryover_probe_api_contract_payload() -> dict[str, object]:
    return build_core_validation_carryover_probe_api_contract().to_dict()


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if effective_argv:
        raise SystemExit("core_validation_carryover_probe_contract does not accept arguments")
    print(json.dumps(core_validation_carryover_probe_api_contract_payload(), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
