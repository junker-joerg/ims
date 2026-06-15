from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class WorkbenchBuildSnapshotIssue:
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
class WorkbenchBuildSnapshotCheck:
    name: str
    ready: bool
    required: bool
    path: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "ready": self.ready,
            "required": self.required,
            "path": self.path,
        }


@dataclass(frozen=True)
class WorkbenchBuildSnapshotResult:
    status: str
    mode: str
    root: str
    frontend_dist: str
    frontend_index_available: bool
    frontend_asset_count: int
    frontend_asset_bytes: int
    python_port_available: bool
    start_script_available: bool
    check_script_available: bool
    excluded_paths: tuple[str, ...]
    writes_enabled: bool
    execution_enabled: bool
    issues: tuple[WorkbenchBuildSnapshotIssue, ...]
    checks: tuple[WorkbenchBuildSnapshotCheck, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "root": self.root,
            "frontend_dist": self.frontend_dist,
            "frontend_index_available": self.frontend_index_available,
            "frontend_asset_count": self.frontend_asset_count,
            "frontend_asset_bytes": self.frontend_asset_bytes,
            "python_port_available": self.python_port_available,
            "start_script_available": self.start_script_available,
            "check_script_available": self.check_script_available,
            "excluded_paths": list(self.excluded_paths),
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "issues": [issue.to_dict() for issue in self.issues],
            "checks": [check.to_dict() for check in self.checks],
        }


def build_workbench_build_snapshot(
    *,
    root: Path | str = ".",
    frontend_dist: Path | str | None = None,
) -> WorkbenchBuildSnapshotResult:
    resolved_root = Path(root).expanduser().resolve()
    resolved_frontend_dist = _resolve_against_root(resolved_root, frontend_dist or Path("frontend") / "dist")
    excluded_paths = _excluded_paths(resolved_root)

    checks = _build_checks(resolved_root, resolved_frontend_dist)
    issues = _issues_from_checks(checks)
    asset_count, asset_bytes, asset_issues = _frontend_asset_summary(resolved_frontend_dist)
    issues.extend(asset_issues)
    check_map = {check.name: check.ready for check in checks}
    return WorkbenchBuildSnapshotResult(
        status=_status_from_issues(issues),
        mode="workbench_build_snapshot",
        root=str(resolved_root),
        frontend_dist=str(resolved_frontend_dist),
        frontend_index_available=check_map.get("frontend_index", False),
        frontend_asset_count=asset_count,
        frontend_asset_bytes=asset_bytes,
        python_port_available=check_map.get("python_port", False),
        start_script_available=check_map.get("start_script", False),
        check_script_available=check_map.get("check_script", False),
        excluded_paths=excluded_paths,
        writes_enabled=False,
        execution_enabled=False,
        issues=tuple(issues),
        checks=tuple(checks),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_workbench_build_snapshot(root=args.root, frontend_dist=args.frontend_dist)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _resolve_against_root(root: Path, path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def _excluded_paths(root: Path) -> tuple[str, ...]:
    return (
        str(root / ".git"),
        str(root / ".ims_workbench"),
        str(root / "logs"),
        str(root / "frontend" / "node_modules"),
        str(root / "frontend" / ".npm-cache"),
    )


def _build_checks(root: Path, frontend_dist: Path) -> tuple[WorkbenchBuildSnapshotCheck, ...]:
    return (
        _check("root", root, required=True),
        _check("python_port", root / "python_port", required=True),
        _check("frontend_dist", frontend_dist, required=True),
        _check("frontend_index", frontend_dist / "index.html", required=True),
        _check("start_script", root / "scripts" / "workbench" / "start-workbench.cmd", required=True),
        _check("check_script", root / "scripts" / "workbench" / "check-workbench.cmd", required=True),
    )


def _check(name: str, path: Path, *, required: bool) -> WorkbenchBuildSnapshotCheck:
    return WorkbenchBuildSnapshotCheck(
        name=name,
        ready=path.exists(),
        required=required,
        path=str(path),
    )


def _issues_from_checks(checks: Sequence[WorkbenchBuildSnapshotCheck]) -> list[WorkbenchBuildSnapshotIssue]:
    issues: list[WorkbenchBuildSnapshotIssue] = []
    for check in checks:
        if check.ready or not check.required:
            continue
        issues.append(
            WorkbenchBuildSnapshotIssue(
                code=f"{check.name}_missing",
                severity="error",
                message=f"workbench build snapshot path is missing: {check.path}",
            )
        )
    return issues


def _frontend_asset_summary(frontend_dist: Path) -> tuple[int, int, list[WorkbenchBuildSnapshotIssue]]:
    if not frontend_dist.is_dir():
        return 0, 0, []
    count = 0
    size = 0
    issues: list[WorkbenchBuildSnapshotIssue] = []
    for path in sorted(frontend_dist.rglob("*")):
        if not path.is_file():
            continue
        try:
            size += path.stat().st_size
            count += 1
        except OSError as exc:
            issues.append(
                WorkbenchBuildSnapshotIssue(
                    code="frontend_asset_unreadable",
                    severity="warning",
                    message=f"frontend asset is not readable: {path}: {exc}",
                )
            )
    return count, size, issues


def _status_from_issues(issues: Sequence[WorkbenchBuildSnapshotIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_build_snapshot",
        description="Fasst lokale Workbench-Build-Artefakte zusammen, ohne Dateien zu erzeugen.",
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Workbench-Repo- oder Artefaktwurzel.")
    parser.add_argument("--frontend-dist", type=Path, help="Expliziter Frontend-Dist-Pfad.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
