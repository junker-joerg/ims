from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.workbench_config import (
    WorkbenchConfigError,
    WorkbenchConfigLoadResult,
    WorkbenchLocalConfig,
    load_workbench_config_result,
    resolve_workbench_config_path,
)
from ims.api.workbench_diagnostics import WorkbenchDiagnosticIssue


@dataclass(frozen=True)
class WorkbenchStartPlanResult:
    status: str
    mode: str
    host: str
    port: int
    frontend_dist: str
    metadata_db: str | None
    recommended_command: str
    diagnostics_command: str
    writes_enabled: bool
    execution_enabled: bool
    issues: tuple[WorkbenchDiagnosticIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "host": self.host,
            "port": self.port,
            "frontend_dist": self.frontend_dist,
            "metadata_db": self.metadata_db,
            "recommended_command": self.recommended_command,
            "diagnostics_command": self.diagnostics_command,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_workbench_start_plan(
    *,
    config_path: Path | str | None = None,
    host: str | None = None,
    port: int | None = None,
    frontend_dist: Path | str | None = None,
    db_path: Path | str | None = None,
) -> WorkbenchStartPlanResult:
    issues: list[WorkbenchDiagnosticIssue] = []
    config_result: WorkbenchConfigLoadResult | None = None
    if config_path is not None:
        try:
            config_result = load_workbench_config_result(config_path)
        except WorkbenchConfigError as exc:
            issues.append(
                WorkbenchDiagnosticIssue(
                    code="workbench_config_invalid",
                    severity="error",
                    message=str(exc),
                )
            )

    config = config_result.config if config_result is not None else WorkbenchLocalConfig()
    effective_host = host if host is not None else config.host
    effective_port = port if port is not None else config.port
    effective_frontend_dist = _effective_frontend_dist(frontend_dist, config_result)
    effective_metadata_db = _effective_metadata_db(db_path, config_result)
    resolved_frontend_dist = _resolve_frontend_dist(effective_frontend_dist)
    resolved_metadata_db = _resolve_metadata_db(effective_metadata_db)

    if not effective_host.strip():
        issues.append(
            WorkbenchDiagnosticIssue(
                code="host_invalid",
                severity="error",
                message="Host darf nicht leer sein.",
            )
        )
    if effective_port < 1 or effective_port > 65535:
        issues.append(
            WorkbenchDiagnosticIssue(
                code="port_invalid",
                severity="error",
                message="Port muss zwischen 1 und 65535 liegen.",
            )
        )
    if not resolved_frontend_dist.is_dir():
        issues.append(
            WorkbenchDiagnosticIssue(
                code="frontend_dist_missing",
                severity="warning",
                message=f"Frontend-Build nicht gefunden: {resolved_frontend_dist}",
            )
        )
    if resolved_metadata_db is not None and not resolved_metadata_db.is_file():
        issues.append(
            WorkbenchDiagnosticIssue(
                code="metadata_db_missing",
                severity="warning",
                message=f"Explizite Metadaten-Datenbank nicht gefunden: {resolved_metadata_db}",
            )
        )

    return WorkbenchStartPlanResult(
        status=_start_plan_status(issues),
        mode="start_plan",
        host=effective_host,
        port=effective_port,
        frontend_dist=str(resolved_frontend_dist),
        metadata_db=str(resolved_metadata_db) if resolved_metadata_db is not None else None,
        recommended_command=_recommended_command(effective_host, effective_port),
        diagnostics_command=_diagnostics_command(resolved_frontend_dist, resolved_metadata_db),
        writes_enabled=False,
        execution_enabled=False,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_workbench_start_plan(
        config_path=args.config,
        host=args.host,
        port=args.port,
        frontend_dist=args.frontend_dist,
        db_path=args.db,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _effective_frontend_dist(
    frontend_dist: Path | str | None,
    config_result: WorkbenchConfigLoadResult | None,
) -> Path | str | None:
    if frontend_dist is not None:
        return frontend_dist
    if config_result is not None and config_result.has_field("frontend_dist"):
        return resolve_workbench_config_path(config_result, config_result.config.frontend_dist)
    return None


def _effective_metadata_db(
    db_path: Path | str | None,
    config_result: WorkbenchConfigLoadResult | None,
) -> Path | str | None:
    if db_path is not None:
        return db_path
    if (
        config_result is not None
        and config_result.has_field("metadata_db")
        and config_result.config.metadata_db is not None
    ):
        return resolve_workbench_config_path(config_result, config_result.config.metadata_db)
    return None


def _resolve_frontend_dist(frontend_dist: Path | str | None) -> Path:
    if frontend_dist is not None:
        return Path(frontend_dist).expanduser().resolve()
    return Path(__file__).resolve().parents[3] / "frontend" / "dist"


def _resolve_metadata_db(db_path: Path | str | None) -> Path | None:
    if db_path is None:
        return None
    return Path(db_path).expanduser().resolve()


def _recommended_command(host: str, port: int) -> str:
    return f"python -m uvicorn ims.api.app:app --app-dir python_port --host {host} --port {port}"


def _diagnostics_command(frontend_dist: Path, metadata_db: Path | None) -> str:
    command = f"python -m ims.api.workbench_diagnostics --frontend-dist {frontend_dist}"
    if metadata_db is not None:
        command = f"{command} --db {metadata_db}"
    return command


def _start_plan_status(issues: Sequence[WorkbenchDiagnosticIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_start_plan",
        description="Beschreibt den lokalen IMS-Workbench-Start, ohne Server oder Simulation zu starten.",
    )
    parser.add_argument("--config", type=Path, help="Explizite lokale Workbench-Konfigurationsdatei.")
    parser.add_argument("--host", help="Expliziter Host fuer den empfohlenen lokalen Start.")
    parser.add_argument("--port", type=int, help="Expliziter Port fuer den empfohlenen lokalen Start.")
    parser.add_argument("--frontend-dist", type=Path, help="Expliziter Frontend-Build-Pfad.")
    parser.add_argument("--db", type=Path, help="Expliziter SQLite-Metadatenpfad.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
