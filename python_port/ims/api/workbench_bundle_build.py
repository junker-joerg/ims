from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.workbench_bundle_plan import WorkbenchBundlePlanIssue, build_workbench_bundle_plan


@dataclass(frozen=True)
class WorkbenchBundleBuildIssue:
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
class WorkbenchBundleBuildResult:
    status: str
    mode: str
    root: str
    frontend_dist: str
    out_path: str
    file_count: int
    total_bytes: int
    zip_bytes: int
    zip_sha256: str
    archive_created: bool
    writes_performed: bool
    execution_performed: bool
    entries: tuple[str, ...]
    issues: tuple[WorkbenchBundleBuildIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "root": self.root,
            "frontend_dist": self.frontend_dist,
            "out_path": self.out_path,
            "file_count": self.file_count,
            "total_bytes": self.total_bytes,
            "zip_bytes": self.zip_bytes,
            "zip_sha256": self.zip_sha256,
            "archive_created": self.archive_created,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "entries": list(self.entries),
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_workbench_bundle_zip(
    *,
    out_path: Path | str,
    root: Path | str = ".",
    frontend_dist: Path | str | None = None,
) -> WorkbenchBundleBuildResult:
    plan = build_workbench_bundle_plan(root=root, frontend_dist=frontend_dist)
    resolved_out_path = Path(out_path).expanduser().resolve()
    issues = [_issue_from_plan_issue(issue) for issue in plan.issues]
    issues.extend(_output_issues(resolved_out_path, plan))
    status = _status_from_issues(issues)
    if status == "error":
        return WorkbenchBundleBuildResult(
            status="error",
            mode="workbench_bundle_build",
            root=plan.root,
            frontend_dist=plan.frontend_dist,
            out_path=str(resolved_out_path),
            file_count=0,
            total_bytes=0,
            zip_bytes=0,
            zip_sha256="",
            archive_created=False,
            writes_performed=False,
            execution_performed=False,
            entries=(),
            issues=tuple(issues),
        )

    entries = tuple(file.relative_path for file in plan.files)
    _write_zip(resolved_out_path, plan.files)
    return WorkbenchBundleBuildResult(
        status=status,
        mode="workbench_bundle_build",
        root=plan.root,
        frontend_dist=plan.frontend_dist,
        out_path=str(resolved_out_path),
        file_count=plan.file_count,
        total_bytes=plan.total_bytes,
        zip_bytes=resolved_out_path.stat().st_size,
        zip_sha256=_sha256(resolved_out_path),
        archive_created=True,
        writes_performed=True,
        execution_performed=False,
        entries=entries,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_workbench_bundle_zip(root=args.root, frontend_dist=args.frontend_dist, out_path=args.out)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _issue_from_plan_issue(issue: WorkbenchBundlePlanIssue) -> WorkbenchBundleBuildIssue:
    return WorkbenchBundleBuildIssue(
        code=issue.code,
        severity=issue.severity,
        message=issue.message,
    )


def _output_issues(out_path: Path, plan) -> list[WorkbenchBundleBuildIssue]:
    issues: list[WorkbenchBundleBuildIssue] = []
    if out_path.suffix.lower() != ".zip":
        issues.append(
            WorkbenchBundleBuildIssue(
                code="out_path_not_zip",
                severity="error",
                message=f"workbench bundle output must be a .zip file: {out_path}",
            )
        )
    if not out_path.parent.is_dir():
        issues.append(
            WorkbenchBundleBuildIssue(
                code="out_parent_missing",
                severity="error",
                message=f"workbench bundle output parent does not exist: {out_path.parent}",
            )
        )
    if out_path.is_dir():
        issues.append(
            WorkbenchBundleBuildIssue(
                code="out_path_is_directory",
                severity="error",
                message=f"workbench bundle output path is a directory: {out_path}",
            )
        )
    for excluded_path in plan.excluded_paths:
        if _is_under(out_path, Path(excluded_path)):
            issues.append(
                WorkbenchBundleBuildIssue(
                    code="out_path_excluded",
                    severity="error",
                    message=f"workbench bundle output path is inside an excluded path: {out_path}",
                )
            )
            break
    for file in plan.files:
        source = Path(file.source_path)
        if source == out_path or (out_path.exists() and _samefile(out_path, source)):
            issues.append(
                WorkbenchBundleBuildIssue(
                    code="out_path_overwrites_source",
                    severity="error",
                    message=f"workbench bundle output path aliases a source file: {out_path}",
                )
            )
            break
    return issues


def _write_zip(out_path: Path, files) -> None:
    with zipfile.ZipFile(out_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(files, key=lambda item: item.relative_path):
            archive.write(file.source_path, arcname=file.relative_path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _samefile(left: Path, right: Path) -> bool:
    try:
        return left.samefile(right)
    except OSError:
        return False


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _status_from_issues(issues: Sequence[WorkbenchBundleBuildIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_bundle_build",
        description="Erzeugt ein explizites lokales Workbench-ZIP aus dem Bundle-Plan.",
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Workbench-Repo- oder Artefaktwurzel.")
    parser.add_argument("--frontend-dist", type=Path, help="Expliziter Frontend-Dist-Pfad.")
    parser.add_argument("--out", type=Path, required=True, help="Expliziter ZIP-Zielpfad.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
