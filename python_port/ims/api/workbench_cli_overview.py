from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class WorkbenchCliCommand:
    name: str
    command: str
    purpose: str
    writes_enabled: bool
    requires_explicit_db: bool = False
    starts_server: bool = False
    starts_simulation: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "command": self.command,
            "purpose": self.purpose,
            "writes_enabled": self.writes_enabled,
            "requires_explicit_db": self.requires_explicit_db,
            "starts_server": self.starts_server,
            "starts_simulation": self.starts_simulation,
        }


@dataclass(frozen=True)
class WorkbenchCliOverviewResult:
    status: str
    mode: str
    commands: tuple[WorkbenchCliCommand, ...]
    boundaries: dict[str, object]
    rest_plan: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "commands": [command.to_dict() for command in self.commands],
            "boundaries": self.boundaries,
            "rest_plan": self.rest_plan,
        }


def build_workbench_cli_overview() -> WorkbenchCliOverviewResult:
    commands = (
        WorkbenchCliCommand(
            name="workbench_diagnostics",
            command="python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist",
            purpose="Lokale Startbedingungen pruefen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="workbench_start_plan",
            command="python -m ims.api.workbench_start_plan --config .\\workbench.local.json",
            purpose="Lokalen Start beschreibend zusammenfassen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="metadata_import_cli check",
            command="python -m ims.api.metadata_import_cli check .\\metadata_import.json",
            purpose="Importformat validieren.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="metadata_import_cli preview",
            command="python -m ims.api.metadata_import_cli preview .\\metadata_import.json",
            purpose="Importdatei zusammenfassen und Konsistenzhinweise anzeigen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="metadata_import_cli snapshot",
            command="python -m ims.api.metadata_import_cli snapshot --db .\\.ims_workbench\\metadata.sqlite",
            purpose="Explizite SQLite-Metadaten read-only als Diagnose lesen.",
            writes_enabled=False,
            requires_explicit_db=True,
        ),
        WorkbenchCliCommand(
            name="metadata_import_cli export",
            command="python -m ims.api.metadata_import_cli export --db .\\.ims_workbench\\metadata.sqlite --out .\\metadata_export.json",
            purpose="Metadaten im lokalen Importformat exportieren.",
            writes_enabled=True,
            requires_explicit_db=True,
        ),
        WorkbenchCliCommand(
            name="metadata_import_cli roundtrip",
            command="python -m ims.api.metadata_import_cli roundtrip --db .\\.ims_workbench\\metadata.sqlite",
            purpose="Export-/Import-/Schreibvertragsgrenzen ohne Schreiben pruefen.",
            writes_enabled=False,
            requires_explicit_db=True,
        ),
        WorkbenchCliCommand(
            name="metadata_write_contracts",
            command="python -m ims.api.metadata_write_contracts",
            purpose="Vorbereitete Workbench-Schreibgrenzen beschreibend ausgeben.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="metadata_write_contracts check",
            command="python -m ims.api.metadata_write_contracts check .\\metadata_import.json",
            purpose="Importdatei gegen den lokalen Schreibvertrag pruefen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="metadata_import_cli import --db",
            command="python -m ims.api.metadata_import_cli import .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite",
            purpose="Validierte Metadaten in eine explizite SQLite-Datei importieren.",
            writes_enabled=True,
            requires_explicit_db=True,
        ),
    )
    return WorkbenchCliOverviewResult(
        status="ok",
        mode="cli_overview",
        commands=commands,
        boundaries={
            "writes_enabled": False,
            "read_only_commands": [
                "workbench_diagnostics",
                "workbench_start_plan",
                "metadata_import_cli check",
                "metadata_import_cli preview",
                "metadata_import_cli snapshot",
                "metadata_import_cli roundtrip",
                "metadata_write_contracts",
                "metadata_write_contracts check",
            ],
            "write_commands": ["metadata_import_cli export", "metadata_import_cli import --db"],
            "export_requires_explicit_out": True,
            "import_requires_explicit_db": True,
            "execution_enabled": False,
            "starts_server": False,
            "creates_sqlite_file": False,
        },
        rest_plan={
            "remaining_prs_estimate": "5-11",
            "next_blocks": [
                "Lokale Start-/Konfigurationsnutzung konsolidieren: 0-1 PRs",
                "Lesende Szenario-/Run-Arbeitsflaechen abrunden: 0-1 PRs",
                "Kontrollierte lokale Schreibpfade vorbereiten: 2-4 PRs",
                "Spaetere Run-Steuerungsgrenze entwerfen, noch ohne echte Simulation: 2-3 PRs",
                "v1-Haertung, Doku, Smoke-/Preview-Checks: 3-4 PRs",
            ],
            "deferred_blocks": [
                "Fachvalidierung",
                "historische Vollgleichheit",
            ],
        },
    )


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = tuple(sys.argv[1:] if argv is None else argv)
    if effective_argv:
        raise SystemExit("workbench_cli_overview does not accept arguments")
    print(json.dumps(build_workbench_cli_overview().to_dict(), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
