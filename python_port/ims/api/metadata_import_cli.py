from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata import metadata_capabilities
from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_consistency import metadata_consistency_payload
from ims.api.metadata_import import (
    MetadataImportError,
    MetadataImportResult,
    import_metadata_file,
    load_metadata_import,
    parse_metadata_import_payload,
    validate_metadata_bundle,
)
from ims.api.metadata_repository import (
    WorkbenchMetadataRepository,
    build_seeded_metadata_repository,
)
from ims.api.sqlite_readonly import readonly_sqlite_uri
from ims.api.metadata_write_contracts import validate_metadata_write_contract_payload


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
class MetadataImportReportResult:
    mode: str
    input_path: str
    db_path: str
    scenario_count: int
    run_count: int
    scenario_ids: tuple[str, ...]
    run_ids: tuple[str, ...]
    consistency: dict[str, object]
    writes_performed: bool = True
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "input_path": self.input_path,
            "db_path": self.db_path,
            "scenario_count": self.scenario_count,
            "run_count": self.run_count,
            "scenario_ids": list(self.scenario_ids),
            "run_ids": list(self.run_ids),
            "consistency": self.consistency,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


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


@dataclass(frozen=True)
class MetadataExportResult:
    mode: str
    scenario_count: int
    run_count: int
    scenario_ids: tuple[str, ...]
    run_ids: tuple[str, ...]
    out_path: str
    writes_performed: bool = True
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "scenario_count": self.scenario_count,
            "run_count": self.run_count,
            "scenario_ids": list(self.scenario_ids),
            "run_ids": list(self.run_ids),
            "out_path": self.out_path,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


@dataclass(frozen=True)
class MetadataRoundtripResult:
    mode: str
    source: dict[str, object]
    scenario_count: int
    run_count: int
    scenario_ids: tuple[str, ...]
    run_ids: tuple[str, ...]
    import_valid: bool
    write_contract_valid: bool
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "source": self.source,
            "scenario_count": self.scenario_count,
            "run_count": self.run_count,
            "scenario_ids": list(self.scenario_ids),
            "run_ids": list(self.run_ids),
            "import_valid": self.import_valid,
            "write_contract_valid": self.write_contract_valid,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


@dataclass(frozen=True)
class MetadataImportDryRunResult:
    mode: str
    source: dict[str, object]
    scenario_count: int
    run_count: int
    new_scenario_ids: tuple[str, ...]
    replaced_scenario_ids: tuple[str, ...]
    new_run_ids: tuple[str, ...]
    replaced_run_ids: tuple[str, ...]
    issues: tuple[str, ...] = ()
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "source": self.source,
            "scenario_count": self.scenario_count,
            "run_count": self.run_count,
            "new_scenario_ids": list(self.new_scenario_ids),
            "replaced_scenario_ids": list(self.replaced_scenario_ids),
            "new_run_ids": list(self.new_run_ids),
            "replaced_run_ids": list(self.replaced_run_ids),
            "issues": list(self.issues),
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
    repository = _metadata_read_repository(db_path, mode="snapshot")
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


def export_metadata_import_bundle(db_path: Path | str | None = None) -> dict[str, object]:
    repository = _metadata_read_repository(db_path, mode="export")
    return _export_metadata_import_bundle_from_repository(repository, mode="export")


def _export_metadata_import_bundle_from_repository(
    repository: WorkbenchMetadataRepository,
    *,
    mode: str,
) -> dict[str, object]:
    try:
        scenarios = repository.list_scenarios()
        runs = repository.list_runs()
    except sqlite3.DatabaseError as exc:
        raise MetadataImportError(f"metadata {mode} database is not readable: {exc}") from exc
    return {
        "schema_version": METADATA_SCHEMA_VERSION,
        "scenarios": scenarios.get("items", []),
        "runs": runs.get("items", []),
    }


def check_metadata_roundtrip(db_path: Path | str | None = None) -> MetadataRoundtripResult:
    repository = _metadata_read_repository(db_path, mode="roundtrip")
    payload = _export_metadata_import_bundle_from_repository(repository, mode="roundtrip")
    bundle = parse_metadata_import_payload(payload)
    validate_metadata_bundle(bundle, build_seeded_metadata_repository())
    validate_metadata_write_contract_payload(payload)
    return MetadataRoundtripResult(
        mode="roundtrip",
        source=repository.metadata_source(),
        scenario_count=len(bundle.scenarios),
        run_count=len(bundle.runs),
        scenario_ids=tuple(scenario.id for scenario in bundle.scenarios),
        run_ids=tuple(run.id for run in bundle.runs),
        import_valid=True,
        write_contract_valid=True,
    )


def export_metadata_import_bundle_to_file(
    out_path: Path | str,
    db_path: Path | str | None = None,
) -> MetadataExportResult:
    payload = export_metadata_import_bundle(db_path)
    resolved_out_path = Path(out_path).expanduser().resolve()
    _reject_export_source_overwrite(resolved_out_path, db_path)
    try:
        resolved_out_path.write_text(_json_line(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        raise MetadataImportError(f"metadata export output is not writable: {exc}") from exc
    scenarios = payload["scenarios"] if isinstance(payload["scenarios"], list) else []
    runs = payload["runs"] if isinstance(payload["runs"], list) else []
    return MetadataExportResult(
        mode="export",
        scenario_count=len(scenarios),
        run_count=len(runs),
        scenario_ids=_metadata_item_ids(scenarios),
        run_ids=_metadata_item_ids(runs),
        out_path=str(resolved_out_path),
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


def dry_run_metadata_import(
    path: Path | str,
    db_path: Path | str | None = None,
) -> MetadataImportDryRunResult:
    raw_payload = _load_raw_import_payload(path)
    bundle = parse_metadata_import_payload(raw_payload)
    repository = _metadata_read_repository(db_path, mode="dry-run")
    try:
        existing_scenario_ids = _repository_ids(repository.list_scenarios())
        existing_run_ids = _repository_ids(repository.list_runs())
        validate_metadata_write_contract_payload(raw_payload, repository)
    except sqlite3.DatabaseError as exc:
        raise MetadataImportError(f"metadata dry-run database is not readable: {exc}") from exc

    scenario_ids = tuple(scenario.id for scenario in bundle.scenarios)
    run_ids = tuple(run.id for run in bundle.runs)
    return MetadataImportDryRunResult(
        mode="dry_run",
        source=repository.metadata_source(),
        scenario_count=len(bundle.scenarios),
        run_count=len(bundle.runs),
        new_scenario_ids=tuple(scenario_id for scenario_id in scenario_ids if scenario_id not in existing_scenario_ids),
        replaced_scenario_ids=tuple(scenario_id for scenario_id in scenario_ids if scenario_id in existing_scenario_ids),
        new_run_ids=tuple(run_id for run_id in run_ids if run_id not in existing_run_ids),
        replaced_run_ids=tuple(run_id for run_id in run_ids if run_id in existing_run_ids),
    )


def import_metadata_to_db(path: Path | str, db_path: Path | str) -> MetadataImportReportResult:
    resolved_input_path = Path(path).expanduser().resolve()
    resolved_db_path = Path(db_path).expanduser().resolve()
    repository = build_seeded_metadata_repository(db_path)
    result = import_metadata_file(path, repository)
    return build_metadata_import_report(result, repository, resolved_input_path, resolved_db_path)


def build_metadata_import_report(
    result: MetadataImportResult,
    repository: WorkbenchMetadataRepository,
    input_path: Path,
    db_path: Path,
) -> MetadataImportReportResult:
    consistency = metadata_consistency_payload(
        repository.list_scenarios(),
        repository.list_runs(),
        metadata_capabilities(),
    )
    return MetadataImportReportResult(
        mode="import",
        input_path=str(input_path),
        db_path=str(db_path),
        scenario_count=result.scenario_count,
        run_count=result.run_count,
        scenario_ids=result.scenario_ids,
        run_ids=result.run_ids,
        consistency=consistency,
    )


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
        elif args.command == "export":
            if args.out is None:
                _print_json(export_metadata_import_bundle(args.db))
            else:
                _print_json(export_metadata_import_bundle_to_file(args.out, args.db).to_dict())
        elif args.command == "roundtrip":
            _print_json(check_metadata_roundtrip(args.db).to_dict())
        elif args.command == "dry-run":
            _print_json(dry_run_metadata_import(args.path, args.db).to_dict())
        elif args.command == "import":
            _print_json(import_metadata_to_db(args.path, args.db).to_dict())
        else:
            parser.error("missing command")
    except MetadataImportError as exc:
        _print_json({"status": "error", "message": str(exc)})
        return 2
    return 0


def _metadata_read_repository(db_path: Path | str | None, *, mode: str) -> WorkbenchMetadataRepository:
    if db_path is None:
        return build_seeded_metadata_repository()
    resolved_path = Path(db_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise MetadataImportError(f"metadata {mode} database does not exist: {resolved_path}")
    return WorkbenchMetadataRepository(_connect_snapshot_db_readonly(resolved_path))


def _reject_export_source_overwrite(resolved_out_path: Path, db_path: Path | str | None) -> None:
    if db_path is None:
        return
    resolved_db_path = Path(db_path).expanduser().resolve()
    if resolved_db_path == resolved_out_path or _paths_reference_same_existing_file(resolved_db_path, resolved_out_path):
        raise MetadataImportError("metadata export output path must differ from the source database path")


def _paths_reference_same_existing_file(left: Path, right: Path) -> bool:
    if not left.exists() or not right.exists():
        return False
    try:
        return left.samefile(right)
    except OSError:
        return False


def _load_raw_import_payload(path: Path | str) -> object:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetadataImportError(f"metadata import JSON is invalid: {exc.msg}") from exc
    except OSError as exc:
        raise MetadataImportError(f"metadata import JSON is not readable: {exc}") from exc


def _connect_snapshot_db_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        _readonly_sqlite_uri(path),
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    return connection


def _readonly_sqlite_uri(path: Path) -> str:
    return readonly_sqlite_uri(path, description="metadata read-only")


def _repository_ids(payload: dict[str, object]) -> tuple[str, ...]:
    items = payload.get("items", [])
    if not isinstance(items, list):
        return ()
    return tuple(
        item["id"]
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    )


def _metadata_item_ids(items: list[object]) -> tuple[str, ...]:
    return tuple(item["id"] for item in items if isinstance(item, dict) and isinstance(item.get("id"), str))


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

    export_parser = subparsers.add_parser("export", help="Workbench-Metadaten im lokalen Importformat exportieren.")
    export_parser.add_argument("--db", type=Path, help="Expliziter SQLite-Quellpfad.")
    export_parser.add_argument("--out", type=Path, help="Expliziter JSON-Zielpfad. Ohne --out wird das Bundle ausgegeben.")

    roundtrip_parser = subparsers.add_parser("roundtrip", help="Export-/Importformat lokal pruefen, ohne zu schreiben.")
    roundtrip_parser.add_argument("--db", type=Path, help="Expliziter SQLite-Quellpfad.")

    dry_run_parser = subparsers.add_parser("dry-run", help="Importwirkung pruefen, ohne zu schreiben.")
    dry_run_parser.add_argument("path", type=Path, help="Pfad zur JSON-Importdatei.")
    dry_run_parser.add_argument("--db", type=Path, help="Expliziter SQLite-Quellpfad fuer Bestandsabgleich.")

    import_parser = subparsers.add_parser("import", help="JSON-Metadaten in eine explizite SQLite-Datei importieren.")
    import_parser.add_argument("path", type=Path, help="Pfad zur JSON-Importdatei.")
    import_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Zielpfad.")
    return parser


def _print_json(payload: dict[str, object]) -> None:
    print(_json_line(payload))


def _json_line(payload: dict[str, object], *, indent: int | None = None) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=indent, sort_keys=True) + ("\n" if indent is not None else "")


if __name__ == "__main__":
    raise SystemExit(main())
