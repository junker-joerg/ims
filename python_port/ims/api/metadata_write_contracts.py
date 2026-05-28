from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Sequence

from ims.api.metadata import METADATA_GENERATED_AT, METADATA_SCHEMA_VERSION, metadata_capabilities


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


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if effective_argv:
        raise SystemExit("metadata_write_contracts does not accept arguments")
    print(json.dumps(build_metadata_write_contract().to_dict(), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
