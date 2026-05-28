from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata_repository import metadata_source_payload


@dataclass(frozen=True)
class WorkbenchDiagnosticIssue:
    code: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(frozen=True)
class WorkbenchDiagnosticsResult:
    status: str
    mode: str
    api_importable: bool
    web_dependencies_available: bool
    frontend_dist_available: bool
    metadata_source: dict[str, object]
    writes_enabled: bool
    execution_enabled: bool
    issues: tuple[WorkbenchDiagnosticIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "api_importable": self.api_importable,
            "web_dependencies_available": self.web_dependencies_available,
            "frontend_dist_available": self.frontend_dist_available,
            "metadata_source": self.metadata_source,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_workbench_diagnostics(
    *,
    frontend_dist: Path | str | None = None,
    db_path: Path | str | None = None,
) -> WorkbenchDiagnosticsResult:
    issues: list[WorkbenchDiagnosticIssue] = []
    api_importable = _module_importable("ims.api.app")
    starlette_available = _module_available("starlette")
    web_dependencies_available = starlette_available
    dist_dir = _resolve_frontend_dist(frontend_dist)
    frontend_dist_available = (dist_dir / "index.html").is_file()
    metadata_source = _diagnostic_metadata_source(db_path)

    if not api_importable:
        issues.append(
            WorkbenchDiagnosticIssue(
                code="api_not_importable",
                severity="error",
                message="ims.api.app kann nicht importiert werden.",
            )
        )
    if not starlette_available:
        issues.append(
            WorkbenchDiagnosticIssue(
                code="starlette_unavailable",
                severity="error",
                message="Starlette ist fuer die lokale Workbench nicht verfuegbar.",
            )
        )
    if not frontend_dist_available:
        issues.append(
            WorkbenchDiagnosticIssue(
                code="frontend_dist_missing",
                severity="warning",
                message=f"Frontend-Build nicht gefunden: {dist_dir}",
            )
        )
    if db_path is not None and not Path(db_path).expanduser().resolve().is_file():
        issues.append(
            WorkbenchDiagnosticIssue(
                code="metadata_db_missing",
                severity="warning",
                message=f"Explizite Metadaten-Datenbank nicht gefunden: {Path(db_path).expanduser().resolve()}",
            )
        )

    return WorkbenchDiagnosticsResult(
        status=_diagnostic_status(issues),
        mode="diagnostics",
        api_importable=api_importable,
        web_dependencies_available=web_dependencies_available,
        frontend_dist_available=frontend_dist_available,
        metadata_source=metadata_source,
        writes_enabled=False,
        execution_enabled=False,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_workbench_diagnostics(
        frontend_dist=args.frontend_dist,
        db_path=args.db,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _resolve_frontend_dist(frontend_dist: Path | str | None) -> Path:
    if frontend_dist is not None:
        return Path(frontend_dist).expanduser().resolve()
    return Path(__file__).resolve().parents[3] / "frontend" / "dist"


def _diagnostic_metadata_source(db_path: Path | str | None) -> dict[str, object]:
    if db_path is None:
        return metadata_source_payload(":memory:")
    return metadata_source_payload(Path(db_path).expanduser().resolve())


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _module_importable(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
    except Exception:
        return False
    return True


def _diagnostic_status(issues: Sequence[WorkbenchDiagnosticIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_diagnostics",
        description="Prueft lokale Startbedingungen der IMS Workbench, ohne Server oder Simulation zu starten.",
    )
    parser.add_argument("--db", type=Path, help="Expliziter SQLite-Metadatenpfad fuer die Diagnose.")
    parser.add_argument("--frontend-dist", type=Path, help="Expliziter Frontend-Build-Pfad fuer die Diagnose.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
