from __future__ import annotations

from dataclasses import dataclass
import json
import sys
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION


@dataclass(frozen=True)
class RunControlAdapterStartContract:
    status: str
    mode: str
    schema_version: str
    endpoint: str
    release_check_endpoint: str
    planned_start_endpoint: str
    source_adapter_module: str
    release_validation_module: str
    expected_adapter_mode: str
    expected_summary_mode: str
    required_request_fields: tuple[str, ...]
    optional_request_fields: tuple[str, ...]
    required_preconditions: tuple[str, ...]
    forbidden_request_fields: tuple[str, ...]
    forbidden_boundaries: tuple[str, ...]
    contract_only: bool = False
    http_enabled: bool = True
    api_accepts_start_payload: bool = True
    api_validates_start_payload: bool = True
    api_accepts_release_payload: bool = True
    api_validates_release_payload: bool = True
    api_starts_adapter: bool = True
    ui_start_enabled: bool = True
    queue_worker_enabled: bool = False
    writes_enabled: bool = True
    execution_enabled: bool = True
    writes_performed: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False
    historical_full_equality_claimed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "schema_version": self.schema_version,
            "endpoint": self.endpoint,
            "release_check_endpoint": self.release_check_endpoint,
            "planned_start_endpoint": self.planned_start_endpoint,
            "source_adapter_module": self.source_adapter_module,
            "release_validation_module": self.release_validation_module,
            "expected_adapter_mode": self.expected_adapter_mode,
            "expected_summary_mode": self.expected_summary_mode,
            "required_request_fields": list(self.required_request_fields),
            "optional_request_fields": list(self.optional_request_fields),
            "required_preconditions": list(self.required_preconditions),
            "forbidden_request_fields": list(self.forbidden_request_fields),
            "forbidden_boundaries": list(self.forbidden_boundaries),
            "contract_only": self.contract_only,
            "http_enabled": self.http_enabled,
            "api_accepts_start_payload": self.api_accepts_start_payload,
            "api_validates_start_payload": self.api_validates_start_payload,
            "api_accepts_release_payload": self.api_accepts_release_payload,
            "api_validates_release_payload": self.api_validates_release_payload,
            "api_starts_adapter": self.api_starts_adapter,
            "ui_start_enabled": self.ui_start_enabled,
            "queue_worker_enabled": self.queue_worker_enabled,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
        }


def build_run_control_adapter_start_contract() -> RunControlAdapterStartContract:
    return RunControlAdapterStartContract(
        status="ok",
        mode="run_control_adapter_start_contract",
        schema_version=METADATA_SCHEMA_VERSION,
        endpoint="/api/run-control/adapter-start-contract",
        release_check_endpoint="/api/run-control/adapter-release-check",
        planned_start_endpoint="/api/run-control/adapter-start",
        source_adapter_module="ims.api.controlled_execution_adapter",
        release_validation_module="ims.api.run_control_execution_release",
        expected_adapter_mode="explicit_multi_period_fixture_adapter",
        expected_summary_mode="explicit_multi_period_execution_summary",
        required_request_fields=(
            "queue_id",
            "run_id",
            "scenario_id",
            "release_profile_id",
            "idempotency_key",
            "explicit_execution_release",
            "expected_adapter_mode",
            "released_by",
            "released_at",
            "release_reason",
        ),
        optional_request_fields=(
            "requested_by",
            "created_at",
            "carry_forward_vu_state",
            "carry_forward_vn_state",
        ),
        required_preconditions=(
            "queue_entry_exists",
            "queue_entry_matches_known_run",
            "queue_status_validated_or_explicitly_released",
            "preflight_passed_or_blockers_explicitly_resolved",
            "explicit_execution_release_true",
            "release_audit_fields_present",
            "release_profile_known_locally",
            "fixture_path_from_known_local_metadata",
            "result_storage_path_controlled_by_run_control",
        ),
        forbidden_request_fields=(
            "browser_upload",
            "fixture_path",
            "free_fixture_path",
            "output_dir",
            "free_output_path",
            "execution_enabled_true_from_queue_metadata",
            "historical_rule_auto_selection",
            "legacy_full_equality_expectation",
        ),
        forbidden_boundaries=(
            "adapter_start_from_contract",
            "runner_start_from_contract",
            "simulation_execution",
            "scheduler_start",
            "queue_worker",
            "browser_file_picker",
            "metadata_write",
            "fachlogik_mutation",
            "historical_full_equality_claim",
        ),
    )


def run_control_adapter_start_contract_payload() -> dict[str, object]:
    return build_run_control_adapter_start_contract().to_dict()


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if effective_argv:
        raise SystemExit("run_control_adapter_start_contract does not accept arguments")
    print(json.dumps(run_control_adapter_start_contract_payload(), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
