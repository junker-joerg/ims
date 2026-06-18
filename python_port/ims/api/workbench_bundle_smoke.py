from __future__ import annotations

import argparse
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


REQUIRED_ENTRIES = (
    "README.md",
    "python_port/__init__.py",
    "frontend/dist/index.html",
    "scripts/workbench/check-workbench.cmd",
    "scripts/workbench/start-workbench.cmd",
    "scripts/workbench/README.md",
    "docs/migration/workbench_shell.md",
    "docs/migration/workbench_packaging_plan.md",
)

FORBIDDEN_PREFIXES = (
    ".git/",
    ".ims_workbench/",
    "logs/",
    "frontend/node_modules/",
    "frontend/.npm-cache/",
    "frontend/dist/.vite/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
)


@dataclass(frozen=True)
class WorkbenchBundleSmokeIssue:
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
class WorkbenchBundleSmokeResult:
    status: str
    mode: str
    zip_path: str
    entry_count: int
    required_entries_present: bool
    forbidden_entries_present: bool
    stable_metadata: bool
    writes_performed: bool
    execution_performed: bool
    issues: tuple[WorkbenchBundleSmokeIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "zip_path": self.zip_path,
            "entry_count": self.entry_count,
            "required_entries_present": self.required_entries_present,
            "forbidden_entries_present": self.forbidden_entries_present,
            "stable_metadata": self.stable_metadata,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def smoke_workbench_bundle_zip(zip_path: Path | str) -> WorkbenchBundleSmokeResult:
    resolved_zip_path = Path(zip_path).expanduser().resolve()
    issues: list[WorkbenchBundleSmokeIssue] = []
    names: tuple[str, ...] = ()
    metadata_stable = False

    if not resolved_zip_path.is_file():
        issues.append(
            WorkbenchBundleSmokeIssue(
                code="zip_missing",
                severity="error",
                message=f"workbench bundle ZIP does not exist: {resolved_zip_path}",
            )
        )
    elif resolved_zip_path.suffix.lower() != ".zip":
        issues.append(
            WorkbenchBundleSmokeIssue(
                code="zip_path_not_zip",
                severity="error",
                message=f"workbench bundle smoke expects a .zip file: {resolved_zip_path}",
            )
        )
    else:
        try:
            with zipfile.ZipFile(resolved_zip_path) as archive:
                names = tuple(sorted(archive.namelist()))
                issues.extend(_entry_issues(names))
                metadata_stable = _metadata_is_stable(archive.infolist(), issues)
        except zipfile.BadZipFile as exc:
            issues.append(
                WorkbenchBundleSmokeIssue(
                    code="zip_unreadable",
                    severity="error",
                    message=f"workbench bundle ZIP is not readable: {exc}",
                )
            )

    missing_required = any(issue.code == "required_entry_missing" for issue in issues)
    forbidden_present = any(issue.code == "forbidden_entry_present" for issue in issues)
    status = _status_from_issues(issues)
    return WorkbenchBundleSmokeResult(
        status=status,
        mode="workbench_bundle_smoke",
        zip_path=str(resolved_zip_path),
        entry_count=len(names),
        required_entries_present=not missing_required and bool(names),
        forbidden_entries_present=forbidden_present,
        stable_metadata=metadata_stable and bool(names),
        writes_performed=False,
        execution_performed=False,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = smoke_workbench_bundle_zip(args.zip_path)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _entry_issues(names: Sequence[str]) -> list[WorkbenchBundleSmokeIssue]:
    issue_list: list[WorkbenchBundleSmokeIssue] = []
    name_set = set(names)
    for required_entry in REQUIRED_ENTRIES:
        if required_entry not in name_set:
            issue_list.append(
                WorkbenchBundleSmokeIssue(
                    code="required_entry_missing",
                    severity="error",
                    message=f"workbench bundle ZIP is missing required entry: {required_entry}",
                )
            )
    for name in names:
        if _is_forbidden_entry(name):
            issue_list.append(
                WorkbenchBundleSmokeIssue(
                    code="forbidden_entry_present",
                    severity="error",
                    message=f"workbench bundle ZIP contains forbidden entry: {name}",
                )
            )
    return issue_list


def _is_forbidden_entry(name: str) -> bool:
    return (
        name.startswith(FORBIDDEN_PREFIXES)
        or "/__pycache__/" in name
        or name.startswith("__pycache__/")
        or name.endswith((".pyc", ".pyo"))
    )


def _metadata_is_stable(
    infos: Sequence[zipfile.ZipInfo],
    issues: list[WorkbenchBundleSmokeIssue],
) -> bool:
    stable = True
    for info in infos:
        if info.is_dir():
            continue
        if info.date_time != (1980, 1, 1, 0, 0, 0) or info.create_system != 3 or info.external_attr >> 16 != 0o644:
            stable = False
            issues.append(
                WorkbenchBundleSmokeIssue(
                    code="unstable_zip_entry_metadata",
                    severity="error",
                    message=f"workbench bundle ZIP entry has unstable metadata: {info.filename}",
                )
            )
    return stable


def _status_from_issues(issues: Sequence[WorkbenchBundleSmokeIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_bundle_smoke",
        description="Prueft ein explizit erzeugtes lokales Workbench-ZIP, ohne es dauerhaft zu entpacken.",
    )
    parser.add_argument("--zip-path", type=Path, required=True, help="Expliziter ZIP-Pfad.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
