from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_import_cli import _metadata_read_repository
from ims.api.metadata_repository import WorkbenchMetadataRepository
from ims.api.run_control_contracts import build_run_control_contract


@dataclass(frozen=True)
class WorkbenchRunControlPreflightResult:
    mode: str
    run_id: str
    scenario_id: str | None
    run_found: bool
    scenario_found: bool
    metadata_source: dict[str, object]
    execution_enabled: bool
    execution_allowed: bool
    issues: tuple[str, ...]
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok" if not self.issues else "error",
            "mode": self.mode,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "run_found": self.run_found,
            "scenario_found": self.scenario_found,
            "metadata_source": self.metadata_source,
            "execution_enabled": self.execution_enabled,
            "execution_allowed": self.execution_allowed,
            "issues": list(self.issues),
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def preflight_run_control(
    run_id: str,
    db_path: Path | str | None = None,
) -> WorkbenchRunControlPreflightResult:
    if not run_id.strip():
        raise MetadataImportError("run control preflight requires a non-empty run_id")
    repository = _metadata_read_repository(db_path, mode="run-control-preflight")
    return _preflight_run_control_from_repository(run_id, repository)


def preflight_run_control_from_repository(
    run_id: str,
    repository: WorkbenchMetadataRepository,
) -> WorkbenchRunControlPreflightResult:
    if not run_id.strip():
        raise MetadataImportError("run control preflight requires a non-empty run_id")
    return _preflight_run_control_from_repository(run_id, repository)


def _preflight_run_control_from_repository(
    run_id: str,
    repository: WorkbenchMetadataRepository,
) -> WorkbenchRunControlPreflightResult:
    try:
        run = repository.get_run(run_id)
    except sqlite3.DatabaseError as exc:
        raise MetadataImportError(f"metadata run-control-preflight database is not readable: {exc}") from exc

    issues: list[str] = []
    scenario_id: str | None = None
    scenario_found = False
    execution_enabled = False

    if run is None:
        issues.append(f"run metadata not found: {run_id}")
    else:
        scenario_id = str(run.get("scenario_id", ""))
        execution_enabled = bool(run.get("execution_enabled"))
        if execution_enabled:
            issues.append(f"run execution remains disabled: {run_id}")
        try:
            scenario_found = repository.get_scenario(scenario_id) is not None
        except sqlite3.DatabaseError as exc:
            raise MetadataImportError(f"metadata run-control-preflight database is not readable: {exc}") from exc
        if not scenario_found:
            issues.append(f"scenario metadata not found for run {run_id}: {scenario_id}")

    contract = build_run_control_contract()
    execution_allowed = False
    if contract.execution_enabled or contract.http_enabled or contract.ui_enabled:
        issues.append("run control contract unexpectedly enables execution")

    return WorkbenchRunControlPreflightResult(
        mode="run_control_preflight",
        run_id=run_id,
        scenario_id=scenario_id,
        run_found=run is not None,
        scenario_found=scenario_found,
        metadata_source=repository.metadata_source(),
        execution_enabled=execution_enabled,
        execution_allowed=execution_allowed,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        _print_json(preflight_run_control(args.run_id, args.db).to_dict())
    except MetadataImportError as exc:
        _print_json(
            {
                "status": "error",
                "mode": "run_control_preflight",
                "message": str(exc),
                "issues": [str(exc)],
                "writes_performed": False,
                "execution_performed": False,
            }
        )
        return 2
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.run_control_preflight",
        description="Prueft lokale Run-Control-Metadaten, ohne eine Simulation zu starten.",
    )
    parser.add_argument("--run-id", required=True, help="Run-Metadaten-ID fuer den lokalen Preflight.")
    parser.add_argument("--db", type=Path, help="Expliziter SQLite-Quellpfad.")
    return parser


def _print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
