from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.run_control_contracts import build_run_control_contract
from ims.api.run_control_preflight import preflight_run_control
from ims.api.workbench_cli_overview import build_workbench_cli_overview
from ims.api.workbench_diagnostics import WorkbenchDiagnosticIssue, build_workbench_diagnostics


@dataclass(frozen=True)
class WorkbenchReadinessCheck:
    name: str
    ready: bool
    status: str
    detail: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "ready": self.ready,
            "status": self.status,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class WorkbenchReadinessResult:
    status: str
    mode: str
    backend_ready: bool
    frontend_ready: bool
    metadata_ready: bool
    cli_ready: bool
    run_control_ready: bool
    writes_enabled: bool
    execution_enabled: bool
    issues: tuple[WorkbenchDiagnosticIssue, ...]
    checks: tuple[WorkbenchReadinessCheck, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "backend_ready": self.backend_ready,
            "frontend_ready": self.frontend_ready,
            "metadata_ready": self.metadata_ready,
            "cli_ready": self.cli_ready,
            "run_control_ready": self.run_control_ready,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "issues": [issue.to_dict() for issue in self.issues],
            "checks": [check.to_dict() for check in self.checks],
        }


def build_workbench_readiness(
    *,
    frontend_dist: Path | str | None = None,
    db_path: Path | str | None = None,
    run_id: str = "baseline-python-tests",
) -> WorkbenchReadinessResult:
    diagnostics = build_workbench_diagnostics(frontend_dist=frontend_dist, db_path=db_path)
    diagnostic_payload = diagnostics.to_dict()
    overview = build_workbench_cli_overview().to_dict()
    contract = build_run_control_contract().to_dict()

    issues: list[WorkbenchDiagnosticIssue] = list(diagnostics.issues)
    preflight_payload = _preflight_payload(run_id, db_path, issues)

    backend_ready = bool(diagnostic_payload["api_importable"] and diagnostic_payload["web_dependencies_available"])
    frontend_ready = bool(diagnostic_payload["frontend_dist_available"])
    metadata_ready = _metadata_ready(issues)
    cli_ready = _cli_overview_ready(overview)
    run_control_ready = bool(
        preflight_payload["run_found"]
        and preflight_payload["scenario_found"]
        and preflight_payload["execution_allowed"] is False
        and contract["execution_enabled"] is False
    )
    writes_enabled = False
    execution_enabled = False
    checks = (
        WorkbenchReadinessCheck(
            name="backend",
            ready=backend_ready,
            status="ok" if backend_ready else "error",
            detail="API importierbar und lokale Web-Abhaengigkeiten verfuegbar.",
        ),
        WorkbenchReadinessCheck(
            name="frontend",
            ready=frontend_ready,
            status="ok" if frontend_ready else "warning",
            detail="Frontend-Dist ist vorhanden." if frontend_ready else "Frontend-Dist fehlt.",
        ),
        WorkbenchReadinessCheck(
            name="metadata",
            ready=metadata_ready,
            status="ok" if metadata_ready else "warning",
            detail=str(diagnostic_payload["metadata_source"].get("storage_kind", "unknown")),
        ),
        WorkbenchReadinessCheck(
            name="cli",
            ready=cli_ready,
            status="ok" if cli_ready else "error",
            detail="Lokale CLI-Uebersicht enthaelt Readiness- und Run-Control-Grenzen.",
        ),
        WorkbenchReadinessCheck(
            name="run_control",
            ready=run_control_ready,
            status="ok" if run_control_ready else "warning",
            detail=f"Run-Control-Preflight fuer {run_id}; Ausfuehrung bleibt gesperrt.",
        ),
    )
    return WorkbenchReadinessResult(
        status=_readiness_status(issues, checks),
        mode="workbench_readiness",
        backend_ready=backend_ready,
        frontend_ready=frontend_ready,
        metadata_ready=metadata_ready,
        cli_ready=cli_ready,
        run_control_ready=run_control_ready,
        writes_enabled=writes_enabled,
        execution_enabled=execution_enabled,
        issues=tuple(issues),
        checks=checks,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_workbench_readiness(
        frontend_dist=args.frontend_dist,
        db_path=args.db,
        run_id=args.run_id,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _preflight_payload(
    run_id: str,
    db_path: Path | str | None,
    issues: list[WorkbenchDiagnosticIssue],
) -> dict[str, object]:
    try:
        payload = preflight_run_control(run_id, db_path).to_dict()
    except Exception as exc:
        issues.append(
            WorkbenchDiagnosticIssue(
                code="run_control_preflight_failed",
                severity="error",
                message=str(exc),
            )
        )
        return {
            "run_found": False,
            "scenario_found": False,
            "execution_allowed": False,
            "issues": [str(exc)],
        }
    for issue in payload["issues"]:
        issues.append(
            WorkbenchDiagnosticIssue(
                code="run_control_preflight_issue",
                severity="warning",
                message=str(issue),
            )
        )
    return payload


def _cli_overview_ready(payload: dict[str, object]) -> bool:
    commands = payload.get("commands", [])
    if not isinstance(commands, list):
        return False
    names = {command.get("name") for command in commands if isinstance(command, dict)}
    boundaries = payload.get("boundaries", {})
    return (
        "workbench_readiness" in names
        and "run_control_preflight" in names
        and isinstance(boundaries, dict)
        and boundaries.get("execution_enabled") is False
    )


def _metadata_ready(issues: Sequence[WorkbenchDiagnosticIssue]) -> bool:
    metadata_issue_codes = {"metadata_db_missing", "metadata_db_unreadable"}
    return not any(
        issue.code in metadata_issue_codes
        or (
            issue.code == "run_control_preflight_failed"
            and issue.message.startswith("metadata run-control-preflight database ")
        )
        for issue in issues
    )


def _readiness_status(
    issues: Sequence[WorkbenchDiagnosticIssue],
    checks: Sequence[WorkbenchReadinessCheck],
) -> str:
    if any(issue.severity == "error" for issue in issues) or any(check.status == "error" for check in checks):
        return "error"
    if issues or any(check.status == "warning" for check in checks):
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_readiness",
        description="Buendelt lokale Workbench-v1-Bereitschaft, ohne Server oder Simulation zu starten.",
    )
    parser.add_argument("--frontend-dist", type=Path, help="Expliziter Frontend-Build-Pfad.")
    parser.add_argument("--db", type=Path, help="Expliziter SQLite-Metadatenpfad.")
    parser.add_argument("--run-id", default="baseline-python-tests", help="Run-ID fuer den lokalen Preflight.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
