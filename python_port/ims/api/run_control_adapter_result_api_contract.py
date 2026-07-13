from __future__ import annotations

from dataclasses import dataclass
import json
import sys
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.run_control_adapter_result_contract import (
    build_run_control_adapter_result_contract,
)


@dataclass(frozen=True)
class RunControlAdapterResultApiContract:
    status: str
    mode: str
    schema_version: str
    endpoint: str
    expected_result_mode: str
    expected_validation_mode: str
    expected_contract_mode: str
    source_contract_module: str
    expected_inputs: tuple[str, ...]
    required_preconditions: tuple[str, ...]
    accepted_result_fields: tuple[str, ...]
    accepted_summary_fields: tuple[str, ...]
    forbidden_fields: tuple[str, ...]
    forbidden_boundaries: tuple[str, ...]
    precomputed_result_required: bool = True
    api_accepts_result_payload: bool = False
    api_validates_result_payload: bool = False
    api_starts_adapter: bool = False
    http_enabled: bool = True
    ui_enabled: bool = False
    queue_worker_enabled: bool = False
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
            "expected_result_mode": self.expected_result_mode,
            "expected_validation_mode": self.expected_validation_mode,
            "expected_contract_mode": self.expected_contract_mode,
            "source_contract_module": self.source_contract_module,
            "expected_inputs": list(self.expected_inputs),
            "required_preconditions": list(self.required_preconditions),
            "accepted_result_fields": list(self.accepted_result_fields),
            "accepted_summary_fields": list(self.accepted_summary_fields),
            "forbidden_fields": list(self.forbidden_fields),
            "forbidden_boundaries": list(self.forbidden_boundaries),
            "precomputed_result_required": self.precomputed_result_required,
            "api_accepts_result_payload": self.api_accepts_result_payload,
            "api_validates_result_payload": self.api_validates_result_payload,
            "api_starts_adapter": self.api_starts_adapter,
            "http_enabled": self.http_enabled,
            "ui_enabled": self.ui_enabled,
            "queue_worker_enabled": self.queue_worker_enabled,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
        }


def build_run_control_adapter_result_api_contract() -> RunControlAdapterResultApiContract:
    result_contract = build_run_control_adapter_result_contract()
    return RunControlAdapterResultApiContract(
        status="ok",
        mode="run_control_adapter_result_api_contract",
        schema_version=METADATA_SCHEMA_VERSION,
        endpoint="/api/run-control/adapter-result-contract",
        expected_result_mode=result_contract.expected_result_mode,
        expected_validation_mode="run_control_adapter_result_validation",
        expected_contract_mode=result_contract.mode,
        source_contract_module="ims.api.run_control_adapter_result_contract",
        expected_inputs=(
            "precomputed_controlled_execution_adapter_json",
            "local_run_control_adapter_result_contract_check",
        ),
        required_preconditions=(
            "adapter_result_payload_precomputed_outside_api",
            "adapter_result_contract_visible",
            "execution_enabled_false",
            "writes_enabled_false",
        ),
        accepted_result_fields=tuple(result_contract.required_result_fields),
        accepted_summary_fields=tuple(result_contract.required_summary_fields),
        forbidden_fields=tuple(result_contract.forbidden_fields),
        forbidden_boundaries=(
            *result_contract.forbidden_boundaries,
            "http_payload_validation",
            "browser_file_picker",
            "ui_result_upload",
        ),
    )


def run_control_adapter_result_api_contract_payload() -> dict[str, object]:
    return build_run_control_adapter_result_api_contract().to_dict()


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if effective_argv:
        raise SystemExit("run_control_adapter_result_api_contract does not accept arguments")
    print(json.dumps(run_control_adapter_result_api_contract_payload(), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
