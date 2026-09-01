from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.workbench_portable_readiness import build_workbench_portable_readiness
from ims.api.workbench_portable_staging import REQUIRED_BACKEND_ENTRIES


BACKEND_IMPORT_MODULES = (
    "ims.api.app",
    "ims.api.workbench_diagnostics",
    "ims.api.workbench_readiness",
)


@dataclass(frozen=True)
class WorkbenchPortableStagingSmokeIssue:
    code: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(frozen=True)
class WorkbenchPortableStagingSmokeResult:
    status: str
    mode: str
    root: str
    portable_layout_ready: bool
    frontend_dist_available: bool
    python_port_available: bool
    backend_ready: bool
    scripts_ready: bool
    writes_performed: bool
    execution_performed: bool
    portable_readiness: dict[str, object]
    issues: tuple[WorkbenchPortableStagingSmokeIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "root": self.root,
            "portable_layout_ready": self.portable_layout_ready,
            "frontend_dist_available": self.frontend_dist_available,
            "python_port_available": self.python_port_available,
            "backend_ready": self.backend_ready,
            "scripts_ready": self.scripts_ready,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "portable_readiness": self.portable_readiness,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def smoke_workbench_portable_staging(root: Path | str) -> WorkbenchPortableStagingSmokeResult:
    resolved_root = Path(root).expanduser().resolve()
    portable_readiness = build_workbench_portable_readiness(resolved_root, layout="portable").to_dict()
    issues = _issues_from_readiness(portable_readiness)
    issues.extend(_backend_issues(resolved_root))
    issues.extend(_backend_import_issues(resolved_root))
    issues.extend(_script_issues(resolved_root))
    status = _status_from_issues(issues)
    return WorkbenchPortableStagingSmokeResult(
        status=status,
        mode="workbench_portable_staging_smoke",
        root=str(resolved_root),
        portable_layout_ready=bool(portable_readiness.get("portable_layout_ready") is True),
        frontend_dist_available=bool(portable_readiness.get("frontend_dist_available") is True),
        python_port_available=bool(portable_readiness.get("python_port_available") is True),
        backend_ready=not any(issue.code in {"backend_entry_missing", "backend_import_failed"} for issue in issues),
        scripts_ready=not any(issue.code.startswith("portable_script_") for issue in issues),
        writes_performed=False,
        execution_performed=False,
        portable_readiness=portable_readiness,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = smoke_workbench_portable_staging(args.root)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _issues_from_readiness(payload: dict[str, object]) -> list[WorkbenchPortableStagingSmokeIssue]:
    issues: list[WorkbenchPortableStagingSmokeIssue] = []
    if payload.get("status") != "error":
        return issues
    for issue in payload.get("issues", []):
        if not isinstance(issue, dict):
            continue
        issues.append(
            WorkbenchPortableStagingSmokeIssue(
                code=f"portable_readiness_{issue.get('code', 'failed')}",
                severity="error",
                message=str(issue.get("message", "portable readiness failed")),
            )
        )
    return issues


def _backend_issues(root: Path) -> list[WorkbenchPortableStagingSmokeIssue]:
    issues: list[WorkbenchPortableStagingSmokeIssue] = []
    for entry in REQUIRED_BACKEND_ENTRIES:
        relative_entry = Path(*Path(entry).parts[1:])
        expected_path = root / "app" / "python_port" / relative_entry
        if not expected_path.is_file():
            issues.append(
                WorkbenchPortableStagingSmokeIssue(
                    code="backend_entry_missing",
                    severity="error",
                    message=f"portable staged backend is missing required entry: {expected_path}",
                )
            )
    return issues


def _backend_import_issues(root: Path) -> list[WorkbenchPortableStagingSmokeIssue]:
    python_port = root / "app" / "python_port"
    if not python_port.is_dir():
        return []

    env = os.environ.copy()
    env["PYTHONPATH"] = str(python_port)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    issues: list[WorkbenchPortableStagingSmokeIssue] = []
    for module in BACKEND_IMPORT_MODULES:
        completed = subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            capture_output=True,
            check=False,
            cwd=root,
            env=env,
            text=True,
        )
        if completed.returncode != 0:
            details = (completed.stderr or completed.stdout or "backend import failed").strip().splitlines()
            message = details[-1] if details else "backend import failed"
            issues.append(
                WorkbenchPortableStagingSmokeIssue(
                    code="backend_import_failed",
                    severity="error",
                    message=f"portable staged backend cannot import {module}: {message}",
                )
            )
    return issues


def _script_issues(root: Path) -> list[WorkbenchPortableStagingSmokeIssue]:
    issues: list[WorkbenchPortableStagingSmokeIssue] = []
    checks = {
        root / "install-workbench.cmd": (
            "Python 3.12 or newer",
            "\\.venv\\Scripts\\python.exe",
            "app\\python_port\\requirements-web.txt",
            "check-workbench.cmd",
        ),
        root / "check-workbench.cmd": (
            "IMS_FRONTEND_DIST=%WORKBENCH_ROOT%\\app\\frontend\\dist",
            "IMS_METADATA_DB=%WORKBENCH_ROOT%\\data\\.ims_workbench\\metadata.sqlite",
            "IMS_PYTHON=%WORKBENCH_ROOT%\\.venv\\Scripts\\python.exe",
            "%IMS_FRONTEND_DIST%\\index.html",
            "app\\python_port",
            '--frontend-dist "%IMS_FRONTEND_DIST%" --db "%IMS_METADATA_DB%"',
        ),
        root / "start-workbench.cmd": (
            "IMS_FRONTEND_DIST=%WORKBENCH_ROOT%\\app\\frontend\\dist",
            "IMS_METADATA_DB=%WORKBENCH_ROOT%\\data\\.ims_workbench\\metadata.sqlite",
            "IMS_WORKBENCH_HOST=127.0.0.1",
            "IMS_WORKBENCH_PORT=8000",
            "IMS_PYTHON=%WORKBENCH_ROOT%\\.venv\\Scripts\\python.exe",
            "%IMS_FRONTEND_DIST%\\index.html",
            "app\\python_port",
            "--app-dir app/python_port",
            '--host "%IMS_WORKBENCH_HOST%" --port "%IMS_WORKBENCH_PORT%"',
        ),
    }
    for script_path, required_fragments in checks.items():
        if not script_path.is_file():
            issues.append(
                WorkbenchPortableStagingSmokeIssue(
                    code="portable_script_missing",
                    severity="error",
                    message=f"portable script is missing: {script_path}",
                )
            )
            continue
        content = script_path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            if fragment not in content:
                issues.append(
                    WorkbenchPortableStagingSmokeIssue(
                        code="portable_script_not_portable",
                        severity="error",
                        message=f"portable script does not reference expected portable path {fragment}: {script_path}",
                    )
                )
    readme_path = root / "BITTE-ZUERST-LESEN.txt"
    if not readme_path.is_file():
        issues.append(
            WorkbenchPortableStagingSmokeIssue(
                code="portable_script_missing",
                severity="error",
                message=f"portable first-read document is missing: {readme_path}",
            )
        )
    else:
        readme = readme_path.read_text(encoding="utf-8")
        for fragment in ("install-workbench.cmd", "start-workbench.cmd", "Dokumentation\\INSTALLATION.pdf"):
            if fragment not in readme:
                issues.append(
                    WorkbenchPortableStagingSmokeIssue(
                        code="portable_script_not_portable",
                        severity="error",
                        message=f"portable first-read document is missing expected text {fragment}: {readme_path}",
                    )
                )
    return issues


def _status_from_issues(issues: Sequence[WorkbenchPortableStagingSmokeIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_portable_staging_smoke",
        description="Prueft eine gestagte portable Workbench-Struktur rein lesend.",
    )
    parser.add_argument("--root", type=Path, required=True, help="Expliziter portabler Workbench-Zielordner.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
