from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError


RUN_CONTROL_REQUEST_FIELDS = frozenset(
    (
        "schema_version",
        "run_id",
        "scenario_id",
        "metadata_db",
        "requested_by",
        "created_at",
        "execution_enabled",
    )
)
REQUIRED_RUN_CONTROL_REQUEST_FIELDS = frozenset(
    (
        "run_id",
        "scenario_id",
        "requested_by",
        "created_at",
        "execution_enabled",
    )
)


@dataclass(frozen=True)
class WorkbenchRunControlRequest:
    run_id: str
    scenario_id: str
    requested_by: str
    created_at: str
    metadata_db: str | None = None
    schema_version: str = METADATA_SCHEMA_VERSION
    execution_enabled: bool = False

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "requested_by": self.requested_by,
            "created_at": self.created_at,
            "execution_enabled": self.execution_enabled,
        }
        if self.metadata_db is not None:
            payload["metadata_db"] = self.metadata_db
        return payload


@dataclass(frozen=True)
class WorkbenchRunControlRequestValidationResult:
    mode: str
    request: WorkbenchRunControlRequest
    accepted_fields: tuple[str, ...]
    issues: tuple[str, ...] = ()
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "request": self.request.to_dict(),
            "accepted_fields": list(self.accepted_fields),
            "issues": list(self.issues),
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


@dataclass(frozen=True)
class WorkbenchRunControlRequestContract:
    status: str
    mode: str
    schema_version: str
    accepted_fields: tuple[str, ...]
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    forbidden_fields: tuple[str, ...]
    example_request: WorkbenchRunControlRequest
    writes_enabled: bool = False
    execution_enabled: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "schema_version": self.schema_version,
            "accepted_fields": list(self.accepted_fields),
            "required_fields": list(self.required_fields),
            "optional_fields": list(self.optional_fields),
            "forbidden_fields": list(self.forbidden_fields),
            "example_request": self.example_request.to_dict(),
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "execution_performed": self.execution_performed,
        }


def build_run_control_request_contract() -> WorkbenchRunControlRequestContract:
    required_fields = tuple(sorted(REQUIRED_RUN_CONTROL_REQUEST_FIELDS))
    optional_fields = tuple(sorted(RUN_CONTROL_REQUEST_FIELDS - REQUIRED_RUN_CONTROL_REQUEST_FIELDS))
    return WorkbenchRunControlRequestContract(
        status="ok",
        mode="run_control_request_contract",
        schema_version=METADATA_SCHEMA_VERSION,
        accepted_fields=tuple(sorted(RUN_CONTROL_REQUEST_FIELDS)),
        required_fields=required_fields,
        optional_fields=optional_fields,
        forbidden_fields=(
            "execution_enabled=true",
            "unknown_fields",
            "fachlogik_state",
            "simulation_results",
        ),
        example_request=WorkbenchRunControlRequest(
            run_id="baseline-python-tests",
            scenario_id="agrsich-reference-window",
            metadata_db=".ims_workbench/metadata.sqlite",
            requested_by="local-user",
            created_at="2026-05-27T00:00:00Z",
            execution_enabled=False,
        ),
    )


def run_control_request_contract_payload() -> dict[str, object]:
    return build_run_control_request_contract().to_dict()


def validate_run_control_request(path: Path | str) -> WorkbenchRunControlRequestValidationResult:
    return validate_run_control_request_payload(_load_json_payload(path))


def validate_run_control_request_payload(payload: object) -> WorkbenchRunControlRequestValidationResult:
    request = parse_run_control_request_payload(payload)
    return WorkbenchRunControlRequestValidationResult(
        mode="run_control_request_check",
        request=request,
        accepted_fields=tuple(sorted(RUN_CONTROL_REQUEST_FIELDS)),
    )


def parse_run_control_request_payload(payload: object) -> WorkbenchRunControlRequest:
    if not isinstance(payload, dict):
        raise MetadataImportError("run control request payload must be a JSON object")

    unknown_fields = sorted(field for field in payload if field not in RUN_CONTROL_REQUEST_FIELDS)
    if unknown_fields:
        raise MetadataImportError(f"run control request rejected fields: {', '.join(unknown_fields)}")

    missing_fields = sorted(field for field in REQUIRED_RUN_CONTROL_REQUEST_FIELDS if field not in payload)
    if missing_fields:
        raise MetadataImportError(f"run control request missing required fields: {', '.join(missing_fields)}")

    schema_version = _optional_non_empty_string(payload, "schema_version", default=METADATA_SCHEMA_VERSION)
    if schema_version != METADATA_SCHEMA_VERSION:
        raise MetadataImportError(
            f"run control request schema_version must be {METADATA_SCHEMA_VERSION}: {schema_version}"
        )

    execution_enabled = payload["execution_enabled"]
    if not isinstance(execution_enabled, bool):
        raise MetadataImportError("run control request execution_enabled must be a boolean")
    if execution_enabled:
        raise MetadataImportError("run control request execution_enabled=true is forbidden")

    return WorkbenchRunControlRequest(
        schema_version=schema_version,
        run_id=_required_non_empty_string(payload, "run_id"),
        scenario_id=_required_non_empty_string(payload, "scenario_id"),
        metadata_db=_optional_non_empty_string(payload, "metadata_db"),
        requested_by=_required_non_empty_string(payload, "requested_by"),
        created_at=_required_non_empty_string(payload, "created_at"),
        execution_enabled=execution_enabled,
    )


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if len(effective_argv) == 2 and effective_argv[0] == "check":
        try:
            print(
                json.dumps(
                    validate_run_control_request(effective_argv[1]).to_dict(),
                    ensure_ascii=True,
                    sort_keys=True,
                )
            )
        except MetadataImportError as exc:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "mode": "run_control_request_check",
                        "message": str(exc),
                        "issues": [str(exc)],
                        "writes_performed": False,
                        "execution_performed": False,
                    },
                    ensure_ascii=True,
                    sort_keys=True,
                )
            )
            return 2
        return 0
    raise SystemExit("run_control_requests accepts only: check <path>")


def _load_json_payload(path: Path | str) -> object:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetadataImportError(f"run control request JSON is invalid: {exc.msg}") from exc
    except OSError as exc:
        raise MetadataImportError(f"run control request JSON is not readable: {exc}") from exc


def _required_non_empty_string(payload: dict[str, object], field: str) -> str:
    value = payload[field]
    if not isinstance(value, str) or not value.strip():
        raise MetadataImportError(f"run control request {field} must be a non-empty string")
    return value


def _optional_non_empty_string(
    payload: dict[str, object],
    field: str,
    *,
    default: str | None = None,
) -> str | None:
    if field not in payload:
        return default
    value = payload[field]
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise MetadataImportError(f"run control request {field} must be a non-empty string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
