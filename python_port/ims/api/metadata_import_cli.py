from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata_import import (
    MetadataImportError,
    MetadataImportResult,
    import_metadata_file,
    load_metadata_import,
)
from ims.api.metadata_repository import build_seeded_metadata_repository


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


def check_metadata_import(path: Path | str) -> MetadataImportCliResult:
    bundle = load_metadata_import(path)
    return MetadataImportCliResult(
        mode="check",
        scenario_count=len(bundle.scenarios),
        run_count=len(bundle.runs),
        scenario_ids=tuple(scenario.id for scenario in bundle.scenarios),
        run_ids=tuple(run.id for run in bundle.runs),
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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.metadata_import_cli",
        description="Prueft oder importiert lokale IMS-Workbench-Metadaten.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="JSON-Metadaten pruefen, ohne zu schreiben.")
    check_parser.add_argument("path", type=Path, help="Pfad zur JSON-Importdatei.")

    import_parser = subparsers.add_parser("import", help="JSON-Metadaten in eine explizite SQLite-Datei importieren.")
    import_parser.add_argument("path", type=Path, help="Pfad zur JSON-Importdatei.")
    import_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Zielpfad.")
    return parser


def _print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
