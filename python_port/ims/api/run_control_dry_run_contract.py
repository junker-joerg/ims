from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION


@dataclass(frozen=True)
class WorkbenchRunControlDryRunContract:
    status: str
    mode: str
    schema_version: str
    expected_inputs: tuple[str, ...]
    required_preconditions: tuple[str, ...]
    forbidden_boundaries: tuple[str, ...]
    http_enabled: bool = False
    writes_enabled: bool = False
    execution_enabled: bool = False
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "schema_version": self.schema_version,
            "expected_inputs": list(self.expected_inputs),
            "required_preconditions": list(self.required_preconditions),
            "forbidden_boundaries": list(self.forbidden_boundaries),
            "http_enabled": self.http_enabled,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def build_run_control_dry_run_contract() -> WorkbenchRunControlDryRunContract:
    return WorkbenchRunControlDryRunContract(
        status="warning",
        mode="run_control_dry_run_contract",
        schema_version=METADATA_SCHEMA_VERSION,
        expected_inputs=(
            "run_id",
            "scenario_id",
            "metadata_source",
            "request_contract",
            "preflight_status",
        ),
        required_preconditions=(
            "run_control_request_contract_visible",
            "run_control_preflight_visible",
            "execution_enabled_false",
            "writes_enabled_false",
        ),
        forbidden_boundaries=(
            "simulation_execution",
            "fachlogik_mutation",
            "queue_write",
            "metadata_write",
            "http_post",
            "http_put",
            "browser_upload",
            "browser_download",
            "scenario_editor",
            "historical_full_equality_claim",
        ),
    )


def run_control_dry_run_contract_payload() -> dict[str, object]:
    return build_run_control_dry_run_contract().to_dict()


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if effective_argv:
        raise SystemExit("run_control_dry_run_contract does not accept arguments")
    print(json.dumps(run_control_dry_run_contract_payload(), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
