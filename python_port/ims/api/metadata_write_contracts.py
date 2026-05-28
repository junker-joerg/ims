from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata import METADATA_GENERATED_AT, METADATA_SCHEMA_VERSION, metadata_capabilities
from ims.api.metadata_import import MetadataImportError, load_metadata_import, validate_metadata_bundle
from ims.api.metadata_repository import build_seeded_metadata_repository


TOP_LEVEL_IMPORT_FIELDS = frozenset(("schema_version", "scenarios", "runs"))
SOURCE_FIELDS = frozenset(("kind", "label", "path"))
VALIDATION_FIELDS = frozenset(("status", "scope", "claim"))


@dataclass(frozen=True)
class WorkbenchMetadataWriteArea:
    name: str
    prepared: bool
    http_enabled: bool
    ui_enabled: bool
    cli_adapter_allowed: bool
    allowed_fields: tuple[str, ...]
    forbidden_fields: tuple[str, ...]
    boundary: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "prepared": self.prepared,
            "http_enabled": self.http_enabled,
            "ui_enabled": self.ui_enabled,
            "cli_adapter_allowed": self.cli_adapter_allowed,
            "allowed_fields": list(self.allowed_fields),
            "forbidden_fields": list(self.forbidden_fields),
            "boundary": self.boundary,
        }


@dataclass(frozen=True)
class WorkbenchMetadataWriteContract:
    schema_version: str
    generated_at: str
    mode: str
    metadata_areas: tuple[WorkbenchMetadataWriteArea, ...]
    forbidden_boundaries: tuple[str, ...]
    allowed_local_write_paths: tuple[str, ...]
    http_write_paths_enabled: bool
    ui_write_paths_enabled: bool
    simulation_execution_enabled: bool
    sqlite_migration_performed: bool
    writes_performed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "mode": self.mode,
            "metadata_areas": [area.to_dict() for area in self.metadata_areas],
            "forbidden_boundaries": list(self.forbidden_boundaries),
            "allowed_local_write_paths": list(self.allowed_local_write_paths),
            "http_write_paths_enabled": self.http_write_paths_enabled,
            "ui_write_paths_enabled": self.ui_write_paths_enabled,
            "simulation_execution_enabled": self.simulation_execution_enabled,
            "sqlite_migration_performed": self.sqlite_migration_performed,
            "writes_performed": self.writes_performed,
        }


@dataclass(frozen=True)
class MetadataWriteContractValidationResult:
    mode: str
    scenario_count: int
    run_count: int
    scenario_ids: tuple[str, ...]
    run_ids: tuple[str, ...]
    accepted_fields: dict[str, tuple[str, ...]]
    rejected_fields: tuple[str, ...]
    issues: tuple[str, ...]
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "scenario_count": self.scenario_count,
            "run_count": self.run_count,
            "scenario_ids": list(self.scenario_ids),
            "run_ids": list(self.run_ids),
            "accepted_fields": {name: list(fields) for name, fields in self.accepted_fields.items()},
            "rejected_fields": list(self.rejected_fields),
            "issues": list(self.issues),
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def build_metadata_write_contract() -> WorkbenchMetadataWriteContract:
    capabilities = metadata_capabilities()
    return WorkbenchMetadataWriteContract(
        schema_version=METADATA_SCHEMA_VERSION,
        generated_at=METADATA_GENERATED_AT,
        mode="metadata_write_contract",
        metadata_areas=(
            WorkbenchMetadataWriteArea(
                name="scenario_metadata",
                prepared=True,
                http_enabled=False,
                ui_enabled=False,
                cli_adapter_allowed=True,
                allowed_fields=(
                    "id",
                    "display_name",
                    "status",
                    "domain_scope",
                    "source",
                    "validation",
                    "updated_at",
                    "notes",
                ),
                forbidden_fields=("simulation_state", "fachlogik_state", "historical_full_equality_claim"),
                boundary="repository-upsert-via-explicit-local-adapter",
            ),
            WorkbenchMetadataWriteArea(
                name="run_metadata",
                prepared=True,
                http_enabled=False,
                ui_enabled=False,
                cli_adapter_allowed=True,
                allowed_fields=(
                    "id",
                    "display_name",
                    "scenario_id",
                    "status",
                    "source",
                    "validation",
                    "period_window",
                    "execution_enabled",
                    "updated_at",
                ),
                forbidden_fields=("execution_enabled=true", "simulation_result", "fachlogik_state"),
                boundary="repository-upsert-via-explicit-local-adapter",
            ),
        ),
        forbidden_boundaries=(
            "execution_enabled=true",
            "simulation_execution",
            "fachlogik_data",
            "http_write_endpoint",
            "ui_write_workflow",
            "historical_full_equality_claim",
        ),
        allowed_local_write_paths=("metadata_import_cli import --db",),
        http_write_paths_enabled=bool(
            capabilities["writes"]["scenario_metadata"]["enabled"] or capabilities["writes"]["run_metadata"]["enabled"]
        ),
        ui_write_paths_enabled=False,
        simulation_execution_enabled=bool(capabilities["simulation_execution"]["enabled"]),
        sqlite_migration_performed=False,
        writes_performed=False,
    )


def validate_metadata_write_contract(path: Path | str) -> MetadataWriteContractValidationResult:
    raw_payload = _load_raw_payload(path)
    contract = build_metadata_write_contract()
    accepted_fields = _accepted_fields_by_area(contract)
    rejected_fields = _rejected_contract_fields(raw_payload, accepted_fields)
    if rejected_fields:
        rejected_list = ", ".join(rejected_fields)
        raise MetadataImportError(f"metadata write contract rejected fields: {rejected_list}")

    bundle = load_metadata_import(path)
    validate_metadata_bundle(bundle, build_seeded_metadata_repository())
    return MetadataWriteContractValidationResult(
        mode="write_contract_check",
        scenario_count=len(bundle.scenarios),
        run_count=len(bundle.runs),
        scenario_ids=tuple(scenario.id for scenario in bundle.scenarios),
        run_ids=tuple(run.id for run in bundle.runs),
        accepted_fields=accepted_fields,
        rejected_fields=(),
        issues=(),
    )


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if not effective_argv:
        print(json.dumps(build_metadata_write_contract().to_dict(), ensure_ascii=True, sort_keys=True))
        return 0
    if len(effective_argv) == 2 and effective_argv[0] == "check":
        try:
            print(
                json.dumps(
                    validate_metadata_write_contract(effective_argv[1]).to_dict(),
                    ensure_ascii=True,
                    sort_keys=True,
                )
            )
        except MetadataImportError as exc:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "mode": "write_contract_check",
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
    raise SystemExit("metadata_write_contracts accepts no arguments except: check <path>")


def _accepted_fields_by_area(contract: WorkbenchMetadataWriteContract) -> dict[str, tuple[str, ...]]:
    return {area.name: area.allowed_fields for area in contract.metadata_areas}


def _load_raw_payload(path: Path | str) -> object:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetadataImportError(f"metadata import JSON is invalid: {exc.msg}") from exc
    except OSError as exc:
        raise MetadataImportError(f"metadata import JSON is not readable: {exc}") from exc


def _rejected_contract_fields(payload: object, accepted_fields: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        return ("payload",)

    rejected: list[str] = []
    rejected.extend(f"{field}" for field in payload if field not in TOP_LEVEL_IMPORT_FIELDS)
    rejected.extend(
        _rejected_item_fields(
            payload.get("scenarios"),
            "scenarios",
            frozenset(accepted_fields["scenario_metadata"]),
        )
    )
    rejected.extend(
        _rejected_item_fields(
            payload.get("runs"),
            "runs",
            frozenset(accepted_fields["run_metadata"]),
        )
    )
    return tuple(rejected)


def _rejected_item_fields(payload: object, label: str, allowed_fields: frozenset[str]) -> tuple[str, ...]:
    if not isinstance(payload, list):
        return ()
    rejected: list[str] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            continue
        rejected.extend(f"{label}[{index}].{field}" for field in item if field not in allowed_fields)
        rejected.extend(_rejected_nested_fields(item.get("source"), f"{label}[{index}].source", SOURCE_FIELDS))
        rejected.extend(
            _rejected_nested_fields(item.get("validation"), f"{label}[{index}].validation", VALIDATION_FIELDS)
        )
    return tuple(rejected)


def _rejected_nested_fields(payload: object, label: str, allowed_fields: frozenset[str]) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        return ()
    return tuple(f"{label}.{field}" for field in payload if field not in allowed_fields)


if __name__ == "__main__":
    raise SystemExit(main())
