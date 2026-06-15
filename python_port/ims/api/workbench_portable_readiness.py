from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence


WorkbenchPortableLayout = Literal["auto", "repo", "portable"]
WorkbenchPortablePathType = Literal["directory", "file"]


@dataclass(frozen=True)
class WorkbenchPortableReadinessIssue:
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
class WorkbenchPortableReadinessCheck:
    name: str
    ready: bool
    required: bool
    path: str
    expected_type: str
    exists: bool
    actual_type: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "ready": self.ready,
            "required": self.required,
            "path": self.path,
            "expected_type": self.expected_type,
            "exists": self.exists,
            "actual_type": self.actual_type,
        }


@dataclass(frozen=True)
class WorkbenchPortableReadinessResult:
    status: str
    mode: str
    root: str
    layout: str
    portable_layout_ready: bool
    python_port_available: bool
    frontend_dist_available: bool
    start_script_available: bool
    check_script_available: bool
    metadata_dir_available: bool
    logs_dir_available: bool
    writes_enabled: bool
    execution_enabled: bool
    issues: tuple[WorkbenchPortableReadinessIssue, ...]
    checks: tuple[WorkbenchPortableReadinessCheck, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "root": self.root,
            "layout": self.layout,
            "portable_layout_ready": self.portable_layout_ready,
            "python_port_available": self.python_port_available,
            "frontend_dist_available": self.frontend_dist_available,
            "start_script_available": self.start_script_available,
            "check_script_available": self.check_script_available,
            "metadata_dir_available": self.metadata_dir_available,
            "logs_dir_available": self.logs_dir_available,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "issues": [issue.to_dict() for issue in self.issues],
            "checks": [check.to_dict() for check in self.checks],
        }


def build_workbench_portable_readiness(
    root: Path | str = ".",
    *,
    layout: WorkbenchPortableLayout = "auto",
) -> WorkbenchPortableReadinessResult:
    resolved_root = Path(root).expanduser().resolve()
    if layout not in {"auto", "repo", "portable"}:
        raise ValueError(f"unsupported portable readiness layout: {layout}")
    if not resolved_root.is_dir():
        issue = WorkbenchPortableReadinessIssue(
            code="portable_root_missing",
            severity="error",
            message=f"portable workbench root does not exist: {resolved_root}",
        )
        return WorkbenchPortableReadinessResult(
            status="error",
            mode="workbench_portable_readiness",
            root=str(resolved_root),
            layout="missing",
            portable_layout_ready=False,
            python_port_available=False,
            frontend_dist_available=False,
            start_script_available=False,
            check_script_available=False,
            metadata_dir_available=False,
            logs_dir_available=False,
            writes_enabled=False,
            execution_enabled=False,
            issues=(issue,),
            checks=(),
        )

    selected_layout = _select_layout(resolved_root, layout)
    checks = _layout_checks(resolved_root, selected_layout)
    issues = _issues_from_checks(checks, selected_layout)
    status = _status_from_issues(issues)
    check_map = {check.name: check.ready for check in checks}
    return WorkbenchPortableReadinessResult(
        status=status,
        mode="workbench_portable_readiness",
        root=str(resolved_root),
        layout=selected_layout,
        portable_layout_ready=not any(check.required and not check.ready for check in checks),
        python_port_available=check_map.get("python_port", False),
        frontend_dist_available=check_map.get("frontend_dist", False),
        start_script_available=check_map.get("start_script", False),
        check_script_available=check_map.get("check_script", False),
        metadata_dir_available=check_map.get("metadata_dir", False),
        logs_dir_available=check_map.get("logs_dir", False),
        writes_enabled=False,
        execution_enabled=False,
        issues=tuple(issues),
        checks=tuple(checks),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_workbench_portable_readiness(args.root, layout=args.layout)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _select_layout(root: Path, layout: WorkbenchPortableLayout) -> str:
    if layout != "auto":
        return layout
    portable_score = _layout_score(root, "portable")
    repo_score = _layout_score(root, "repo")
    if portable_score > repo_score:
        return "portable"
    return "repo"


def _layout_score(root: Path, layout: str) -> int:
    return sum(1 for check in _layout_checks(root, layout) if check.required and check.ready)


def _layout_checks(root: Path, layout: str) -> tuple[WorkbenchPortableReadinessCheck, ...]:
    if layout == "portable":
        return (
            _check("python_port", root / "app" / "python_port", expected_type="directory", required=True),
            _check(
                "frontend_dist",
                root / "app" / "frontend" / "dist" / "index.html",
                expected_type="file",
                required=True,
            ),
            _check("start_script", root / "start-workbench.cmd", expected_type="file", required=True),
            _check("check_script", root / "check-workbench.cmd", expected_type="file", required=True),
            _check("metadata_dir", root / "data" / ".ims_workbench", expected_type="directory", required=False),
            _check("logs_dir", root / "logs", expected_type="directory", required=False),
        )
    return (
        _check("python_port", root / "python_port", expected_type="directory", required=True),
        _check("frontend_dist", root / "frontend" / "dist" / "index.html", expected_type="file", required=True),
        _check(
            "start_script",
            root / "scripts" / "workbench" / "start-workbench.cmd",
            expected_type="file",
            required=True,
        ),
        _check(
            "check_script",
            root / "scripts" / "workbench" / "check-workbench.cmd",
            expected_type="file",
            required=True,
        ),
        _check("metadata_dir", root / ".ims_workbench", expected_type="directory", required=False),
        _check("logs_dir", root / "logs", expected_type="directory", required=False),
    )


def _check(
    name: str,
    path: Path,
    *,
    expected_type: WorkbenchPortablePathType,
    required: bool,
) -> WorkbenchPortableReadinessCheck:
    exists = path.exists()
    actual_type = _actual_path_type(path)
    return WorkbenchPortableReadinessCheck(
        name=name,
        ready=exists and actual_type == expected_type,
        required=required,
        path=str(path),
        expected_type=expected_type,
        exists=exists,
        actual_type=actual_type,
    )


def _actual_path_type(path: Path) -> str:
    if path.is_file():
        return "file"
    if path.is_dir():
        return "directory"
    if path.exists():
        return "other"
    return "missing"


def _issues_from_checks(
    checks: Sequence[WorkbenchPortableReadinessCheck],
    layout: str,
) -> list[WorkbenchPortableReadinessIssue]:
    issues: list[WorkbenchPortableReadinessIssue] = []
    for check in checks:
        if check.ready:
            continue
        if not check.exists:
            if not check.required:
                continue
            issues.append(
                WorkbenchPortableReadinessIssue(
                    code=f"{check.name}_missing",
                    severity="error",
                    message=f"{layout} workbench path is missing: {check.path}",
                )
            )
            continue
        issues.append(
            WorkbenchPortableReadinessIssue(
                code=f"{check.name}_wrong_type",
                severity="error" if check.required else "warning",
                message=(
                    f"{layout} workbench path has wrong type: {check.path}; "
                    f"expected {check.expected_type}, got {check.actual_type}"
                ),
            )
        )
    return issues


def _status_from_issues(issues: Sequence[WorkbenchPortableReadinessIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_portable_readiness",
        description="Prueft eine lokale oder portable Workbench-Struktur, ohne Dateien zu erzeugen.",
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Zu pruefender Workbench-Wurzelpfad.")
    parser.add_argument(
        "--layout",
        choices=("auto", "repo", "portable"),
        default="auto",
        help="Erwartete Struktur: repo, portable oder automatische Erkennung.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
