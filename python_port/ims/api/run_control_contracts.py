from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION


@dataclass(frozen=True)
class WorkbenchRunControlContract:
    schema_version: str
    mode: str
    allowed_future_inputs: tuple[str, ...]
    forbidden_boundaries: tuple[str, ...]
    execution_enabled: bool = False
    http_enabled: bool = False
    ui_enabled: bool = False
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "schema_version": self.schema_version,
            "execution_enabled": self.execution_enabled,
            "http_enabled": self.http_enabled,
            "ui_enabled": self.ui_enabled,
            "allowed_future_inputs": list(self.allowed_future_inputs),
            "forbidden_boundaries": list(self.forbidden_boundaries),
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def build_run_control_contract() -> WorkbenchRunControlContract:
    return WorkbenchRunControlContract(
        schema_version=METADATA_SCHEMA_VERSION,
        mode="run_control_contract",
        allowed_future_inputs=(
            "run_id",
            "scenario_id",
            "metadata_db",
            "requested_by",
            "created_at",
        ),
        forbidden_boundaries=(
            "simulation_execution",
            "fachlogik_mutation",
            "historical_full_equality_claim",
            "browser_upload",
            "http_write_endpoint",
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if effective_argv:
        raise SystemExit("run_control_contracts does not accept arguments")
    print(json.dumps(build_run_control_contract().to_dict(), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
