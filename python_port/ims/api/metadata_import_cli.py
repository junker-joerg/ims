from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata import metadata_capabilities
from ims.api.metadata_consistency import metadata_consistency_payload
from ims.api.metadata_import import (
    MetadataImportError,
    MetadataImportResult,
    import_metadata_file,
    load_metadata_import,
    validate_metadata_bundle,
)
from ims.api.metadata_repository import (
    WorkbenchMetadataRepository,
    build_seeded_metadata_repository,
    connect_metadata_db,
)


@dataclass(frozen=True)
class MetadataImportCliResult:
    mode: str
    scenario_count: int
    run_count: int
    scenario_ids: tuple[str, ...]
    run_ids: tuple[str, ...]
    db_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": "ok",
            "mode": self.mode,
            "scenario_count": self.scenario_count,
            "run_count": self.run_count,
            "scenario_ids": list(self.scenario_ids),
            "run_ids": list(self.run_ids),
        }
        if self.db_path is not None:
            payload["db_path"] = self.db_path
        return payload


@dataclass(frozen=True)
class MetadataImportPreviewResult:
    mode: str
    scenario_count: int
    run_count: int
    scenario_ids: tuple[str, ...]
    run_ids: tuple[str, ...]
    existing_scenario_ids: tuple[str, ...]
    existing_run_ids: tuple[str, ...]
    new_scenario_ids: tuple[str, ...]
    new_run_ids: tuple[str, ...]
    runs_with_missing_scenario: tuple[str, ...]
    runs_with_execution_enabled: tuple[str, ...]
    writes_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "scenario_count": self.scenario_count,
            "run_count": self.run_count,
            "scenario_ids": list(self.scenario_ids),
            "run_ids": list(self.run_ids),
            "existing_scenario_ids": list(self.existing_scenario_ids),
            "existing_run_ids": list(self.existing_run_ids),
            "new_scenario_ids": list(self.new_scenario_ids),
            "new_run_ids": list(self.new_run_ids),
            "runs_with_missing_scenario": list(self.runs_with_missing_scenario),
            "runs_with_execution_enabled": list(self.runs_with_execution_enabled),
            "writes_performed": self.writes_performed,
        }


@dataclass(frozen=True)
class MetadataSnapshotResult:
    mode: str
    source: dict[str, object]
    scenarios: dict[str, object]
    runs: dict[str, object]
    consistency: dict[str, object]
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "source": self.source,
            "scenarios": self.scenarios,
            "runs": self.runs,
            "consistency": self.consistency,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def check_metadata_import(path: Path | str) -> MetadataImportCliResult:
    bundle = load_metadata_import(path)
    validate_metadata_bundle(bundle, build_seeded_metadata_repository())
    return MetadataImportCliResult(
        mode="check",
        scenario_count=len(bundle.scenarios),
        run_count=len(bundle.runs),
        scenario_ids=tuple(scenario.id for scenario in bundle.scenarios),
        run_ids=tuple(run.id for run in bundle.runs),
    )


def export_metadata_snapshot(db_path: Path | str | None = None) -> MetadataSnapshotResult:
    repository = _snapshot_repository(db_path)
    try:
        scenarios = repository.list_scenarios()
        runs = repository.list_runs()
        consistency = metadata_consistency_payload(scenarios, runs, metadata_capabilities())
    except sqlite3.DatabaseError as exc:
        raise MetadataImportError(f"metadata snapshot database is not readable: {exc}") from exc
    return MetadataSnapshotResult(
        mode="snapshot",
        source=repository.metadata_source(),
        scenarios=scenarios,
        runs=runs,
        consistency=consistency,
    )


def preview_metadata_import(path: Path | str) -> MetadataImportPreviewResult:
    bundle = load_metadata_import(path)
    repository = build_seeded_metadata_repository()
    existing_scenario_ids = _repository_ids(repository.list_scenarios())
    existing_run_ids = _repository_ids(repository.list_runs())
    scenario_ids = tuple(scenario.id for scenario in bundle.scenarios)
    run_ids = tuple(run.id for run in bundle.runs)
    known_scenario_ids = set(existing_scenario_ids) | set(scenario_ids)
    runs_with_missing_scenario = tuple(
        run.id for run in bundle.runs if run.scenario_id not in known_scenario_ids
    )
    runs_with_execution_enabled = tuple(run.id for run in bundle.runs if run.execution_enabled)

    validate_metadata_bundle(bundle, repository)
    return MetadataImportPreviewResult(
        mode="preview",
        scenario_count=len(bundle.scenarios),
        run_count=len(bundle.runs),
        scenario_ids=scenario_ids,
        run_ids=run_ids,
        existing_scenario_ids=tuple(scenario_id for scenario_id in scenario_ids if scenario_id in existing_scenario_ids),
        existing_run_ids=tuple(run_id for run_id in run_ids if run_id in existing_run_ids),
        new_scenario_ids=tuple(scenario_id for scenario_id in scenario_ids if scenario_id not in existing_scenario_ids),
        new_run_ids=tuple(run_id for run_id in run_ids if run_id not in existing_run_ids),
        runs_with_missing_scenario=runs_with_missing_scenario,
        runs_with_execution_enabled=runs_with_execution_enabled,
    )


def import_metadata_to_db(path: Path | str, db_path: Path | str) -> MetadataImportCliResult:
    repository = build_seeded_metadata_repository(db_path)
    result = import_metadata_file(path, repository)
    return _cli_result_from_import(result, db_path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            _print_json(check_metadata_import(args.path).to_dict())
        elif args.command == "preview":
            _print_json(preview_metadata_import(args.path).to_dict())
        elif args.command == "snapshot":
            _print_json(export_metadata_snapshot(args.db).to_dict())
        elif args.command == "import":
            _print_json(import_metadata_to_db(args.path, args.db).to_dict())
        else:
            parser.error("missing command")
    except MetadataImportError as exc:
        _print_json({"status": "error", "message": str(exc)})
        return 2
    return 0


def _cli_result_from_import(result: MetadataImportResult, db_path: Path | str) -> MetadataImportCliResult:
    return MetadataImportCliResult(
        mode="import",
        scenario_count=result.scenario_count,
        run_count=result.run_count,
        scenario_ids=result.scenario_ids,
        run_ids=result.run_ids,
        db_path=str(db_path),
    )


def _snapshot_repository(db_path: Path | str | None) -> WorkbenchMetadataRepository:
    if db_path is None:
        return build_seeded_metadata_repository()
    resolved_path = Path(db_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise MetadataImportError(f"metadata snapshot database does not exist: {resolved_path}")
    return WorkbenchMetadataRepository(connect_metadata_db(resolved_path))


def _repository_ids(payload: dict[str, object]) -> tuple[str, ...]:
    items = payload.get("items", [])
    if not isinstance(items, list):
        return ()
    return tuple(
        item["id"]
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.metadata_import_cli",
        description="Prueft oder importiert lokale IMS-Workbench-Metadaten.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="JSON-Metadaten pruefen, ohne zu schreiben.")
    check_parser.add_argument("path", type=Path, help="Pfad zur JSON-Importdatei.")

    preview_parser = subparsers.add_parser("preview", help="JSON-Metadaten pruefen und Importvorschau ausgeben.")
    preview_parser.add_argument("path", type=Path, help="Pfad zur JSON-Importdatei.")

    snapshot_parser = subparsers.add_parser("snapshot", help="Workbench-Metadaten lokal lesen und als JSON-Snapshot ausgeben.")
    snapshot_parser.add_argument("--db", type=Path, help="Expliziter SQLite-Quellpfad.")

    import_parser = subparsers.add_parser("import", help="JSON-Metadaten in eine explizite SQLite-Datei importieren.")
    import_parser.add_argument("path", type=Path, help="Pfad zur JSON-Importdatei.")
    import_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Zielpfad.")
    return parser


def _print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
