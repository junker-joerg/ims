from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION


EXPLICIT_MULTI_PERIOD_EXECUTION_SUMMARY_FIELDS: tuple[str, ...] = (
    "mode",
    "period_count",
    "processed_local_periods",
    "processed_global_periods",
    "total_vu_rule_applications",
    "total_vn_insurance_rule_applications",
    "total_vn_settlement_applications",
    "total_vn_damage_settlement_applications",
    "carryover_count",
    "vu_carryover_count",
    "vn_carryover_count",
    "written_file_count",
    "legacy_comparison_performed",
    "legacy_comparison_matches",
    "legacy_report_written_file_count",
    "writes_performed",
    "execution_performed",
    "automatic_historical_rule_selection_performed",
    "simulation_performed",
)


@dataclass(frozen=True)
class ControlledExecutionAdapterContract:
    status: str
    mode: str
    schema_version: str
    adapter_mode: str
    expected_summary_mode: str
    source_runner: str
    summary_builder: str
    accepted_fixture_kinds: tuple[str, ...]
    expected_inputs: tuple[str, ...]
    required_preconditions: tuple[str, ...]
    expected_summary_fields: tuple[str, ...]
    forbidden_inputs: tuple[str, ...]
    forbidden_boundaries: tuple[str, ...]
    contract_only: bool = True
    http_enabled: bool = False
    ui_enabled: bool = False
    queue_worker_enabled: bool = False
    runner_start_enabled: bool = False
    writes_enabled: bool = False
    execution_enabled: bool = False
    writes_performed: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "schema_version": self.schema_version,
            "adapter_mode": self.adapter_mode,
            "expected_summary_mode": self.expected_summary_mode,
            "source_runner": self.source_runner,
            "summary_builder": self.summary_builder,
            "accepted_fixture_kinds": list(self.accepted_fixture_kinds),
            "expected_inputs": list(self.expected_inputs),
            "required_preconditions": list(self.required_preconditions),
            "expected_summary_fields": list(self.expected_summary_fields),
            "forbidden_inputs": list(self.forbidden_inputs),
            "forbidden_boundaries": list(self.forbidden_boundaries),
            "contract_only": self.contract_only,
            "http_enabled": self.http_enabled,
            "ui_enabled": self.ui_enabled,
            "queue_worker_enabled": self.queue_worker_enabled,
            "runner_start_enabled": self.runner_start_enabled,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
        }


def build_controlled_execution_adapter_contract() -> ControlledExecutionAdapterContract:
    return ControlledExecutionAdapterContract(
        status="ok",
        mode="controlled_execution_adapter_contract",
        schema_version=METADATA_SCHEMA_VERSION,
        adapter_mode="explicit_multi_period_fixture_adapter",
        expected_summary_mode="explicit_multi_period_execution_summary",
        source_runner="ims.engine.explicit_period_runner.run_explicit_multi_period_from_fixture",
        summary_builder=(
            "ims.engine.explicit_period_runner.build_explicit_multi_period_execution_summary"
        ),
        accepted_fixture_kinds=(
            "explicit_vu_vn_period_plan_fixture",
            "explicit_multi_period_fixture",
        ),
        expected_inputs=(
            "fixture_path",
            "adapter_mode",
            "explicit_execution_release",
            "expected_summary_contract",
            "carry_forward_vu_state",
            "carry_forward_vn_state",
        ),
        required_preconditions=(
            "three_fachliche_regression_tests_green",
            "controlled_execution_adapter_plan_reviewed",
            "execution_release_explicit",
            "execution_enabled_false_in_run_control_metadata",
            "api_ui_queue_start_paths_disabled",
        ),
        expected_summary_fields=EXPLICIT_MULTI_PERIOD_EXECUTION_SUMMARY_FIELDS,
        forbidden_inputs=(
            "browser_upload",
            "api_request_body",
            "queue_execution_request",
            "execution_enabled_true_from_queue_metadata",
            "free_output_path",
            "historical_rule_auto_selection",
            "legacy_full_equality_expectation",
        ),
        forbidden_boundaries=(
            "runner_start_from_contract",
            "simulation_execution",
            "scheduler_start",
            "queue_worker",
            "http_write_endpoint",
            "ui_start_button",
            "metadata_write",
            "fachlogik_mutation",
            "historical_full_equality_claim",
        ),
    )


def controlled_execution_adapter_contract_payload() -> dict[str, object]:
    return build_controlled_execution_adapter_contract().to_dict()


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if effective_argv:
        raise SystemExit("controlled_execution_adapter_contract does not accept arguments")
    print(json.dumps(controlled_execution_adapter_contract_payload(), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
