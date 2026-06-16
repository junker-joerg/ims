from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.workbench_artifact_manifest import (
    WorkbenchArtifactManifestFile,
    WorkbenchArtifactManifestIssue,
    build_workbench_artifact_manifest,
)


@dataclass(frozen=True)
class WorkbenchBundlePlanIssue:
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
class WorkbenchBundlePlanResult:
    status: str
    mode: str
    root: str
    frontend_dist: str
    recommended_bundle_name: str
    file_count: int
    total_bytes: int
    files: tuple[WorkbenchArtifactManifestFile, ...]
    excluded_paths: tuple[str, ...]
    writes_performed: bool
    archive_created: bool
    execution_performed: bool
    issues: tuple[WorkbenchBundlePlanIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "root": self.root,
            "frontend_dist": self.frontend_dist,
            "recommended_bundle_name": self.recommended_bundle_name,
            "file_count": self.file_count,
            "total_bytes": self.total_bytes,
            "files": [file.to_dict() for file in self.files],
            "excluded_paths": list(self.excluded_paths),
            "writes_performed": self.writes_performed,
            "archive_created": self.archive_created,
            "execution_performed": self.execution_performed,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_workbench_bundle_plan(
    *,
    root: Path | str = ".",
    frontend_dist: Path | str | None = None,
) -> WorkbenchBundlePlanResult:
    manifest = build_workbench_artifact_manifest(root=root, frontend_dist=frontend_dist)
    issues = tuple(_issue_from_manifest_issue(issue) for issue in manifest.issues)
    root_path = Path(manifest.root)
    return WorkbenchBundlePlanResult(
        status=_status_from_issues(issues),
        mode="workbench_bundle_plan",
        root=manifest.root,
        frontend_dist=manifest.frontend_dist,
        recommended_bundle_name=f"{root_path.name or 'ims-workbench'}-local-workbench.zip",
        file_count=manifest.file_count,
        total_bytes=manifest.total_bytes,
        files=manifest.files,
        excluded_paths=manifest.excluded_paths,
        writes_performed=False,
        archive_created=False,
        execution_performed=False,
        issues=issues,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_workbench_bundle_plan(root=args.root, frontend_dist=args.frontend_dist)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _issue_from_manifest_issue(issue: WorkbenchArtifactManifestIssue) -> WorkbenchBundlePlanIssue:
    return WorkbenchBundlePlanIssue(
        code=issue.code,
        severity=issue.severity,
        message=issue.message,
    )


def _status_from_issues(issues: Sequence[WorkbenchBundlePlanIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_bundle_plan",
        description="Plant ein lokales Workbench-Bundle, ohne Dateien zu kopieren oder ein Archiv zu erzeugen.",
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Workbench-Repo- oder Artefaktwurzel.")
    parser.add_argument("--frontend-dist", type=Path, help="Expliziter Frontend-Dist-Pfad.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
