from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence

from ims.api.workbench_bundle_smoke import smoke_workbench_bundle_zip
from ims.api.workbench_portable_readiness import build_workbench_portable_readiness


@dataclass(frozen=True)
class WorkbenchPortableStagingIssue:
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
class WorkbenchPortableStagingFile:
    source_entry: str
    target_path: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source_entry": self.source_entry,
            "target_path": self.target_path,
        }


@dataclass(frozen=True)
class WorkbenchPortableStagingResult:
    status: str
    mode: str
    zip_path: str
    out_path: str
    staged_file_count: int
    staged_files: tuple[WorkbenchPortableStagingFile, ...]
    portable_readiness: dict[str, object]
    writes_performed: bool
    execution_performed: bool
    issues: tuple[WorkbenchPortableStagingIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "zip_path": self.zip_path,
            "out_path": self.out_path,
            "staged_file_count": self.staged_file_count,
            "staged_files": [file.to_dict() for file in self.staged_files],
            "portable_readiness": self.portable_readiness,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def stage_workbench_portable_bundle(
    *,
    zip_path: Path | str,
    out_path: Path | str,
) -> WorkbenchPortableStagingResult:
    resolved_zip_path = Path(zip_path).expanduser().resolve()
    resolved_out_path = Path(out_path).expanduser().resolve()
    issues = _preflight_issues(resolved_zip_path, resolved_out_path)
    if not issues:
        smoke = smoke_workbench_bundle_zip(resolved_zip_path)
        issues.extend(_issues_from_smoke(smoke))
    if not issues:
        issues.extend(_staging_entry_issues(resolved_zip_path, resolved_out_path))
    status = _status_from_issues(issues)
    if status == "error":
        return _result(
            status="error",
            zip_path=resolved_zip_path,
            out_path=resolved_out_path,
            staged_files=(),
            portable_readiness={},
            writes_performed=False,
            issues=issues,
        )

    staged_files = _stage_zip(resolved_zip_path, resolved_out_path)
    portable_readiness = build_workbench_portable_readiness(resolved_out_path, layout="portable").to_dict()
    if portable_readiness["status"] == "error":
        issues.append(
            WorkbenchPortableStagingIssue(
                code="portable_readiness_failed",
                severity="error",
                message=f"staged portable workbench is not ready: {resolved_out_path}",
            )
        )
    return _result(
        status=_status_from_issues(issues),
        zip_path=resolved_zip_path,
        out_path=resolved_out_path,
        staged_files=staged_files,
        portable_readiness=portable_readiness,
        writes_performed=True,
        issues=issues,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = stage_workbench_portable_bundle(zip_path=args.zip_path, out_path=args.out)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _preflight_issues(zip_path: Path, out_path: Path) -> list[WorkbenchPortableStagingIssue]:
    issues: list[WorkbenchPortableStagingIssue] = []
    if not zip_path.is_file():
        issues.append(
            WorkbenchPortableStagingIssue(
                code="zip_missing",
                severity="error",
                message=f"portable staging ZIP does not exist: {zip_path}",
            )
        )
    elif zip_path.suffix.lower() != ".zip":
        issues.append(
            WorkbenchPortableStagingIssue(
                code="zip_path_not_zip",
                severity="error",
                message=f"portable staging source must be a .zip file: {zip_path}",
            )
        )
    if out_path.exists() and not out_path.is_dir():
        issues.append(
            WorkbenchPortableStagingIssue(
                code="out_path_not_directory",
                severity="error",
                message=f"portable staging output path is not a directory: {out_path}",
            )
        )
    elif out_path.exists() and any(out_path.iterdir()):
        issues.append(
            WorkbenchPortableStagingIssue(
                code="out_path_not_empty",
                severity="error",
                message=f"portable staging output directory is not empty: {out_path}",
            )
        )
    if _is_under(zip_path, out_path):
        issues.append(
            WorkbenchPortableStagingIssue(
                code="zip_path_inside_out_path",
                severity="error",
                message=f"portable staging ZIP path is inside the output directory: {zip_path}",
            )
        )
    return issues


def _issues_from_smoke(smoke_result) -> list[WorkbenchPortableStagingIssue]:
    smoke_payload = smoke_result.to_dict()
    if smoke_payload["status"] != "error":
        return []
    return [
        WorkbenchPortableStagingIssue(
            code="zip_smoke_failed",
            severity="error",
            message=f"portable staging ZIP smoke failed: {issue['code']}: {issue['message']}",
        )
        for issue in smoke_payload["issues"]
    ]


def _stage_zip(zip_path: Path, out_path: Path) -> tuple[WorkbenchPortableStagingFile, ...]:
    out_path.mkdir(parents=True, exist_ok=True)
    staged_files: list[WorkbenchPortableStagingFile] = []
    with zipfile.ZipFile(zip_path) as archive:
        for info in sorted(archive.infolist(), key=lambda entry: entry.filename):
            if info.is_dir():
                continue
            target_path = _target_path_for_entry(out_path, info.filename)
            if target_path is None:
                continue
            _write_archive_member(archive, info, target_path)
            staged_files.append(
                WorkbenchPortableStagingFile(
                    source_entry=info.filename,
                    target_path=str(target_path),
                )
            )
    staged_files.extend(_write_portable_scripts(out_path))
    (out_path / "data" / ".ims_workbench").mkdir(parents=True, exist_ok=True)
    (out_path / "logs").mkdir(parents=True, exist_ok=True)
    return tuple(staged_files)


def _staging_entry_issues(zip_path: Path, out_path: Path) -> list[WorkbenchPortableStagingIssue]:
    issues: list[WorkbenchPortableStagingIssue] = []
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            try:
                _target_path_for_entry(out_path, info.filename)
            except ValueError as exc:
                issues.append(
                    WorkbenchPortableStagingIssue(
                        code="zip_entry_escapes_out_path",
                        severity="error",
                        message=str(exc),
                    )
                )
    return issues


def _target_path_for_entry(out_path: Path, entry_name: str) -> Path | None:
    entry = PurePosixPath(entry_name)
    parts = entry.parts
    if ".." in parts:
        raise ValueError(f"portable staging entry contains parent path segment: {entry_name}")
    if parts[:1] == ("python_port",):
        return _safe_target(out_path, Path("app", *parts))
    if parts[:2] == ("frontend", "dist"):
        return _safe_target(out_path, Path("app", *parts))
    if parts == ("README.md",):
        return _safe_target(out_path, Path("README.md"))
    return None


def _safe_target(out_path: Path, relative_path: Path) -> Path:
    target_path = (out_path / relative_path).resolve()
    if not _is_under(target_path, out_path):
        raise ValueError(f"portable staging entry escapes output directory: {relative_path}")
    return target_path


def _write_archive_member(archive: zipfile.ZipFile, info: zipfile.ZipInfo, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(info) as source, target_path.open("wb") as target:
        shutil.copyfileobj(source, target)


def _write_portable_scripts(out_path: Path) -> list[WorkbenchPortableStagingFile]:
    scripts = {
        "generated:portable/check-workbench.cmd": (
            out_path / "check-workbench.cmd",
            _portable_check_script(),
        ),
        "generated:portable/start-workbench.cmd": (
            out_path / "start-workbench.cmd",
            _portable_start_script(),
        ),
    }
    staged_files: list[WorkbenchPortableStagingFile] = []
    for source_entry, (target_path, content) in scripts.items():
        target_path.write_text(content, encoding="utf-8", newline="\r\n")
        staged_files.append(WorkbenchPortableStagingFile(source_entry=source_entry, target_path=str(target_path)))
    return staged_files


def _portable_check_script() -> str:
    return """@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%.") do set "WORKBENCH_ROOT=%%~fI"

pushd "%WORKBENCH_ROOT%" >nul
if errorlevel 1 (
  echo IMS Workbench check failed: portable root not found.
  exit /b 1
)

if not exist "app\\frontend\\dist\\index.html" (
  echo IMS Workbench check failed: app\\frontend\\dist is missing.
  popd >nul
  exit /b 1
)

set "PYTHONPATH=%WORKBENCH_ROOT%\\app\\python_port;%PYTHONPATH%"

python -m ims.api.workbench_diagnostics --frontend-dist app/frontend/dist
if errorlevel 1 (
  popd >nul
  exit /b 1
)

python -m ims.api.workbench_readiness --frontend-dist app/frontend/dist
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
"""


def _portable_start_script() -> str:
    return """@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%.") do set "WORKBENCH_ROOT=%%~fI"

pushd "%WORKBENCH_ROOT%" >nul
if errorlevel 1 (
  echo IMS Workbench start failed: portable root not found.
  exit /b 1
)

if not exist "app\\frontend\\dist\\index.html" (
  echo IMS Workbench start failed: app\\frontend\\dist is missing.
  popd >nul
  exit /b 1
)

set "PYTHONPATH=%WORKBENCH_ROOT%\\app\\python_port;%PYTHONPATH%"

echo Starting IMS Workbench at http://127.0.0.1:8000/
python -m uvicorn ims.api.app:app --app-dir app/python_port --host 127.0.0.1 --port 8000
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
"""


def _result(
    *,
    status: str,
    zip_path: Path,
    out_path: Path,
    staged_files: tuple[WorkbenchPortableStagingFile, ...],
    portable_readiness: dict[str, object],
    writes_performed: bool,
    issues: Sequence[WorkbenchPortableStagingIssue],
) -> WorkbenchPortableStagingResult:
    return WorkbenchPortableStagingResult(
        status=status,
        mode="workbench_portable_staging",
        zip_path=str(zip_path),
        out_path=str(out_path),
        staged_file_count=len(staged_files),
        staged_files=staged_files,
        portable_readiness=portable_readiness,
        writes_performed=writes_performed,
        execution_performed=False,
        issues=tuple(issues),
    )


def _status_from_issues(issues: Sequence[WorkbenchPortableStagingIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_portable_staging",
        description="Staged ein geprueftes lokales Workbench-ZIP in eine portable Zielstruktur.",
    )
    parser.add_argument("--zip-path", type=Path, required=True, help="Expliziter Workbench-ZIP-Pfad.")
    parser.add_argument("--out", type=Path, required=True, help="Expliziter leerer Zielordner.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
