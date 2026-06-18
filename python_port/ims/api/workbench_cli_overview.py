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
            name="workbench_readiness",
            command="python -m ims.api.workbench_readiness --frontend-dist frontend/dist",
            purpose="Lokale Workbench-v1-Bereitschaft buendeln.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="workbench_portable_readiness",
            command="python -m ims.api.workbench_portable_readiness --root . --layout repo",
            purpose="Lokale oder portable Workbench-Ordnerstruktur pruefen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="workbench_build_snapshot",
            command="python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist",
            purpose="Lokale Workbench-Build-Artefakte zusammenfassen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="workbench_artifact_manifest",
            command="python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist",
            purpose="Lokale Workbench-Artefaktgrenze als Manifest zusammenfassen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="workbench_bundle_plan",
            command="python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist",
            purpose="Lokales Workbench-Bundle ohne Kopie oder ZIP planen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="workbench_bundle_build",
            command="python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\\dist\\ims-workbench-local.zip",
            purpose="Explizites lokales Workbench-ZIP aus dem Bundle-Plan erzeugen.",
            writes_enabled=True,
        ),
        WorkbenchCliCommand(
            name="workbench_bundle_smoke",
            command="python -m ims.api.workbench_bundle_smoke --zip-path .\\dist\\ims-workbench-local.zip",
            purpose="Explizit erzeugtes Workbench-ZIP pruefen, ohne es dauerhaft zu entpacken.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="workbench_portable_staging",
            command="python -m ims.api.workbench_portable_staging --zip-path .\\dist\\ims-workbench-local.zip --out .\\ims-workbench",
            purpose="Geprueftes Workbench-ZIP in eine portable Zielstruktur stagen.",
            writes_enabled=True,
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
            name="metadata_import_cli dry-run",
            command="python -m ims.api.metadata_import_cli dry-run .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite",
            purpose="Importwirkung gegen eine explizite Metadatenquelle pruefen, ohne zu schreiben.",
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
            name="run_control_contracts",
            command="python -m ims.api.run_control_contracts",
            purpose="Spaetere Run-Steuerungsgrenze ohne Ausfuehrung beschreibend ausgeben.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="run_control_requests check",
            command="python -m ims.api.run_control_requests check .\\run_control_request.json",
            purpose="Lokalen Run-Control-Request gegen die gesperrte Ausfuehrungsgrenze pruefen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="run_control_queue init",
            command="python -m ims.api.run_control_queue init --db .\\.ims_workbench\\metadata.sqlite",
            purpose="Lokales Run-Control-Queue-Schema in expliziter SQLite-Datei anlegen.",
            writes_enabled=True,
            requires_explicit_db=True,
        ),
        WorkbenchCliCommand(
            name="run_control_queue enqueue",
            command="python -m ims.api.run_control_queue enqueue .\\run_control_request.json --db .\\.ims_workbench\\metadata.sqlite",
            purpose="Validierten Run-Control-Request lokal in die Queue schreiben, ohne Ausfuehrung.",
            writes_enabled=True,
            requires_explicit_db=True,
        ),
        WorkbenchCliCommand(
            name="run_control_queue list",
            command="python -m ims.api.run_control_queue list --db .\\.ims_workbench\\metadata.sqlite",
            purpose="Lokale Run-Control-Queue lesend auflisten.",
            writes_enabled=False,
            requires_explicit_db=True,
        ),
        WorkbenchCliCommand(
            name="run_control_preflight",
            command="python -m ims.api.run_control_preflight --run-id baseline-python-tests",
            purpose="Run-Metadaten lokal gegen die gesperrte Steuerungsgrenze pruefen.",
            writes_enabled=False,
        ),
        WorkbenchCliCommand(
            name="metadata_import_cli import --db",
            command="python -m ims.api.metadata_import_cli import .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite",
            purpose="Validierte Metadaten in eine explizite SQLite-Datei importieren und Importbericht ausgeben.",
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
                "workbench_readiness",
                "workbench_portable_readiness",
                "workbench_build_snapshot",
                "workbench_artifact_manifest",
                "workbench_bundle_plan",
                "workbench_bundle_smoke",
                "metadata_import_cli check",
                "metadata_import_cli preview",
                "metadata_import_cli snapshot",
                "metadata_import_cli roundtrip",
                "metadata_import_cli dry-run",
                "metadata_write_contracts",
                "metadata_write_contracts check",
                "run_control_contracts",
                "run_control_requests check",
                "run_control_queue list",
                "run_control_preflight",
            ],
            "write_commands": [
                "metadata_import_cli export",
                "workbench_bundle_build",
                "run_control_queue init",
                "run_control_queue enqueue",
                "metadata_import_cli import --db",
                "workbench_portable_staging",
            ],
            "export_requires_explicit_out": True,
            "bundle_build_requires_explicit_out": True,
            "import_requires_explicit_db": True,
            "execution_enabled": False,
            "starts_server": False,
            "creates_sqlite_file": False,
        },
        rest_plan={
            "remaining_prs_estimate": "0",
            "next_blocks": [],
            "deferred_blocks": [
                "kontrollierte echte Run-Steuerung",
                "UI-/HTTP-Schreibpfade",
                "Szenario-Editor",
                "SQLite-Migration",
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
