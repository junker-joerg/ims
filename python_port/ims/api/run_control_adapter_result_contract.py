from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from ims.api.controlled_execution_adapter import ControlledExecutionAdapterResult
from ims.api.controlled_execution_adapter_contract import (
    EXPLICIT_MULTI_PERIOD_EXECUTION_SUMMARY_FIELDS,
)
from ims.api.metadata import METADATA_SCHEMA_VERSION


CONTROLLED_EXECUTION_ADAPTER_RESULT_FIELDS: tuple[str, ...] = tuple(
    ControlledExecutionAdapterResult.__dataclass_fields__
)


@dataclass(frozen=True)
class RunControlAdapterResultIssue:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class RunControlAdapterResultContract:
    status: str
    mode: str
    schema_version: str
    expected_result_mode: str
    expected_summary_mode: str
    source_result_mode: str
    required_result_fields: tuple[str, ...]
    required_summary_fields: tuple[str, ...]
    forbidden_fields: tuple[str, ...]
    forbidden_boundaries: tuple[str, ...]
    precomputed_result_required: bool = True
    adapter_start_allowed: bool = False
    api_accepts_upload: bool = False
    http_enabled: bool = False
    ui_enabled: bool = False
    queue_worker_enabled: bool = False
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
            "expected_result_mode": self.expected_result_mode,
            "expected_summary_mode": self.expected_summary_mode,
            "source_result_mode": self.source_result_mode,
            "required_result_fields": list(self.required_result_fields),
            "required_summary_fields": list(self.required_summary_fields),
            "forbidden_fields": list(self.forbidden_fields),
            "forbidden_boundaries": list(self.forbidden_boundaries),
            "precomputed_result_required": self.precomputed_result_required,
            "adapter_start_allowed": self.adapter_start_allowed,
            "api_accepts_upload": self.api_accepts_upload,
            "http_enabled": self.http_enabled,
            "ui_enabled": self.ui_enabled,
            "queue_worker_enabled": self.queue_worker_enabled,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
        }


@dataclass(frozen=True)
class RunControlAdapterResultValidationResult:
    status: str
    mode: str
    contract: RunControlAdapterResultContract
    result_accepted: bool
    issues: tuple[RunControlAdapterResultIssue, ...]
    writes_performed: bool = False
    execution_performed: bool = False
    adapter_started: bool = False
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "contract": self.contract.to_dict(),
            "result_accepted": self.result_accepted,
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "adapter_started": self.adapter_started,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
        }


def build_run_control_adapter_result_contract() -> RunControlAdapterResultContract:
    return RunControlAdapterResultContract(
        status="ok",
        mode="run_control_adapter_result_contract",
        schema_version=METADATA_SCHEMA_VERSION,
        expected_result_mode="controlled_execution_adapter",
        expected_summary_mode="explicit_multi_period_execution_summary",
        source_result_mode="controlled_execution_adapter",
        required_result_fields=CONTROLLED_EXECUTION_ADAPTER_RESULT_FIELDS,
        required_summary_fields=EXPLICIT_MULTI_PERIOD_EXECUTION_SUMMARY_FIELDS,
        forbidden_fields=(
            "request_body",
            "browser_upload",
            "output_dir",
            "free_output_path",
            "queue_execution_request",
            "execution_enabled_true_from_queue_metadata",
            "start_button",
            "historical_full_equality_expectation",
        ),
        forbidden_boundaries=(
            "adapter_start_from_run_control",
            "runner_start_from_run_control",
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


def run_control_adapter_result_contract_payload() -> dict[str, object]:
    return build_run_control_adapter_result_contract().to_dict()


def validate_run_control_adapter_result_payload(
    payload: Mapping[str, object],
) -> RunControlAdapterResultValidationResult:
    contract = build_run_control_adapter_result_contract()
    issues: list[RunControlAdapterResultIssue] = []

    payload_keys = set(payload)
    required_keys = set(contract.required_result_fields)
    for field in sorted(required_keys - payload_keys):
        issues.append(RunControlAdapterResultIssue("missing_result_field", field))
    for field in sorted(payload_keys - required_keys):
        issues.append(RunControlAdapterResultIssue("unknown_result_field", field))
    for field in contract.forbidden_fields:
        if field in payload:
            issues.append(RunControlAdapterResultIssue("forbidden_result_field", field))

    if payload.get("mode") != contract.expected_result_mode:
        issues.append(
            RunControlAdapterResultIssue(
                "unexpected_result_mode",
                f"expected {contract.expected_result_mode}",
            )
        )
    if payload.get("http_enabled") is not False:
        issues.append(RunControlAdapterResultIssue("http_enabled", "must be false"))
    if payload.get("ui_enabled") is not False:
        issues.append(RunControlAdapterResultIssue("ui_enabled", "must be false"))
    if payload.get("queue_worker_enabled") is not False:
        issues.append(RunControlAdapterResultIssue("queue_worker_enabled", "must be false"))
    if payload.get("writes_enabled") is not False:
        issues.append(RunControlAdapterResultIssue("writes_enabled", "must be false"))
    if payload.get("writes_performed") is not False:
        issues.append(RunControlAdapterResultIssue("writes_performed", "must be false"))
    if payload.get("simulation_performed") is not False:
        issues.append(RunControlAdapterResultIssue("simulation_performed", "must be false"))
    if payload.get("automatic_historical_rule_selection_performed") is not False:
        issues.append(
            RunControlAdapterResultIssue(
                "automatic_historical_rule_selection_performed",
                "must be false",
            )
        )
    if payload.get("historical_full_equality_claimed") is not False:
        issues.append(
            RunControlAdapterResultIssue("historical_full_equality_claimed", "must be false")
        )

    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        issues.append(RunControlAdapterResultIssue("summary_missing", "summary must be an object"))
    else:
        _validate_summary(summary, contract, issues)

    result_accepted = not issues
    return RunControlAdapterResultValidationResult(
        status="ok" if result_accepted else "error",
        mode="run_control_adapter_result_validation",
        contract=contract,
        result_accepted=result_accepted,
        issues=tuple(issues),
    )


def validate_run_control_adapter_result_file(path: str | Path) -> RunControlAdapterResultValidationResult:
    with Path(path).resolve().open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        contract = build_run_control_adapter_result_contract()
        return RunControlAdapterResultValidationResult(
            status="error",
            mode="run_control_adapter_result_validation",
            contract=contract,
            result_accepted=False,
            issues=(
                RunControlAdapterResultIssue(
                    "result_payload_type",
                    "adapter result payload must be a JSON object",
                ),
            ),
        )
    return validate_run_control_adapter_result_payload(payload)


def _validate_summary(
    summary: Mapping[str, object],
    contract: RunControlAdapterResultContract,
    issues: list[RunControlAdapterResultIssue],
) -> None:
    summary_keys = set(summary)
    required_keys = set(contract.required_summary_fields)
    for field in sorted(required_keys - summary_keys):
        issues.append(RunControlAdapterResultIssue("missing_summary_field", field))
    for field in sorted(summary_keys - required_keys):
        issues.append(RunControlAdapterResultIssue("unknown_summary_field", field))
    if summary.get("mode") != contract.expected_summary_mode:
        issues.append(
            RunControlAdapterResultIssue(
                "unexpected_summary_mode",
                f"expected {contract.expected_summary_mode}",
            )
        )
    if summary.get("writes_performed") is not False:
        issues.append(RunControlAdapterResultIssue("summary_writes_performed", "must be false"))
    if summary.get("simulation_performed") is not False:
        issues.append(RunControlAdapterResultIssue("summary_simulation_performed", "must be false"))
    if summary.get("automatic_historical_rule_selection_performed") is not False:
        issues.append(
            RunControlAdapterResultIssue(
                "summary_automatic_historical_rule_selection_performed",
                "must be false",
            )
        )


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if not effective_argv:
        print(json.dumps(run_control_adapter_result_contract_payload(), ensure_ascii=True, sort_keys=True))
        return 0

    parser = _build_parser()
    args = parser.parse_args(effective_argv)
    result = validate_run_control_adapter_result_file(args.path)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.result_accepted else 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prueft ein vorab erzeugtes Adapter-Resultat fuer Run-Control read-only."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("path", help="Pfad zu einem controlled_execution_adapter-JSON.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
