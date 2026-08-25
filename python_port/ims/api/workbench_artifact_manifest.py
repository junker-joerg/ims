from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class WorkbenchArtifactManifestIssue:
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
class WorkbenchArtifactManifestPath:
    name: str
    path: str
    kind: str
    required: bool
    exists: bool
    file_count: int
    total_bytes: int

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "path": self.path,
            "kind": self.kind,
            "required": self.required,
            "exists": self.exists,
            "file_count": self.file_count,
            "total_bytes": self.total_bytes,
        }


@dataclass(frozen=True)
class WorkbenchArtifactManifestFile:
    relative_path: str
    source_path: str
    size_bytes: int
    sha256: str
    group: str

    def to_dict(self) -> dict[str, object]:
        return {
            "relative_path": self.relative_path,
            "source_path": self.source_path,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "group": self.group,
        }


@dataclass(frozen=True)
class WorkbenchArtifactManifestResult:
    status: str
    mode: str
    root: str
    frontend_dist: str
    included_paths: tuple[WorkbenchArtifactManifestPath, ...]
    excluded_paths: tuple[str, ...]
    missing_required_paths: tuple[str, ...]
    files: tuple[WorkbenchArtifactManifestFile, ...]
    file_count: int
    total_bytes: int
    writes_enabled: bool
    execution_enabled: bool
    issues: tuple[WorkbenchArtifactManifestIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "root": self.root,
            "frontend_dist": self.frontend_dist,
            "included_paths": [path.to_dict() for path in self.included_paths],
            "excluded_paths": list(self.excluded_paths),
            "missing_required_paths": list(self.missing_required_paths),
            "files": [file.to_dict() for file in self.files],
            "file_count": self.file_count,
            "total_bytes": self.total_bytes,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_workbench_artifact_manifest(
    *,
    root: Path | str = ".",
    frontend_dist: Path | str | None = None,
) -> WorkbenchArtifactManifestResult:
    resolved_root = Path(root).expanduser().resolve()
    resolved_frontend_dist = _resolve_against_root(resolved_root, frontend_dist or Path("frontend") / "dist")
    excluded_paths = _excluded_paths(resolved_root)
    included_paths = _included_paths(resolved_root, resolved_frontend_dist, excluded_paths)
    missing_required = tuple(path.name for path in included_paths if path.required and not path.exists)
    issues = _issues_for_missing_paths(included_paths)
    files = _manifest_files(resolved_root, included_paths, excluded_paths)
    return WorkbenchArtifactManifestResult(
        status=_status_from_issues(issues),
        mode="workbench_artifact_manifest",
        root=str(resolved_root),
        frontend_dist=str(resolved_frontend_dist),
        included_paths=included_paths,
        excluded_paths=excluded_paths,
        missing_required_paths=missing_required,
        files=files,
        file_count=len(files),
        total_bytes=sum(file.size_bytes for file in files),
        writes_enabled=False,
        execution_enabled=False,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_workbench_artifact_manifest(root=args.root, frontend_dist=args.frontend_dist)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _included_paths(
    root: Path,
    frontend_dist: Path,
    excluded_paths: Sequence[str],
) -> tuple[WorkbenchArtifactManifestPath, ...]:
    return (
        _manifest_path("python_port", root / "python_port", kind="directory", required=True, excluded_paths=excluded_paths),
        _manifest_path("frontend_dist", frontend_dist, kind="directory", required=True, excluded_paths=excluded_paths),
        _manifest_path(
            "check_script",
            root / "scripts" / "workbench" / "check-workbench.cmd",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path(
            "start_script",
            root / "scripts" / "workbench" / "start-workbench.cmd",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path(
            "script_readme",
            root / "scripts" / "workbench" / "README.md",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path(
            "windows_release_gate_script",
            root / "scripts" / "workbench" / "test-release-gate.ps1",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path("readme", root / "README.md", kind="file", required=True, excluded_paths=excluded_paths),
        _manifest_path(
            "workbench_doc",
            root / "docs" / "migration" / "workbench_shell.md",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path(
            "packaging_plan",
            root / "docs" / "migration" / "workbench_packaging_plan.md",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path(
            "release_checklist",
            root / "docs" / "migration" / "workbench_release_checklist.md",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path(
            "metadata_recovery_doc",
            root / "docs" / "migration" / "workbench_metadata_recovery.md",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path(
            "production_release_corpus_report",
            root / "docs" / "migration" / "production_release_corpus_report.md",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path(
            "windows_release_gate_doc",
            root / "docs" / "migration" / "windows_release_gate.md",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
        _manifest_path(
            "calculated_export_provenance_doc",
            root / "docs" / "migration" / "calculated_export_provenance_map.md",
            kind="file",
            required=True,
            excluded_paths=excluded_paths,
        ),
    )


def _manifest_path(
    name: str,
    path: Path,
    *,
    kind: str,
    required: bool,
    excluded_paths: Sequence[str],
) -> WorkbenchArtifactManifestPath:
    exists = _path_has_expected_kind(path, kind)
    file_count, total_bytes = _path_summary(path, excluded_paths) if exists else (0, 0)
    return WorkbenchArtifactManifestPath(
        name=name,
        path=str(path),
        kind=kind,
        required=required,
        exists=exists,
        file_count=file_count,
        total_bytes=total_bytes,
    )


def _path_has_expected_kind(path: Path, kind: str) -> bool:
    if kind == "directory":
        return path.is_dir()
    return path.is_file()


def _path_summary(path: Path, excluded_paths: Sequence[str]) -> tuple[int, int]:
    if path.is_file():
        return 1, path.stat().st_size
    count = 0
    size = 0
    excluded = {Path(item) for item in excluded_paths}
    for child in sorted(path.rglob("*")):
        if not child.is_file() or _is_excluded_file(child, excluded):
            continue
        count += 1
        size += child.stat().st_size
    return count, size


def _manifest_files(
    root: Path,
    included_paths: Sequence[WorkbenchArtifactManifestPath],
    excluded_paths: Sequence[str],
) -> tuple[WorkbenchArtifactManifestFile, ...]:
    excluded = {Path(item) for item in excluded_paths}
    files: list[WorkbenchArtifactManifestFile] = []
    for included_path in included_paths:
        source = Path(included_path.path)
        if not included_path.exists:
            continue
        if source.is_file():
            candidates = (source,)
        else:
            candidates = tuple(path for path in sorted(source.rglob("*")) if path.is_file())
        for candidate in candidates:
            if _is_excluded_file(candidate, excluded):
                continue
            files.append(
                WorkbenchArtifactManifestFile(
                    relative_path=_relative_manifest_path(root, source, candidate, included_path.name),
                    source_path=str(candidate),
                    size_bytes=candidate.stat().st_size,
                    sha256=_sha256(candidate),
                    group=included_path.name,
                )
            )
    return tuple(sorted(files, key=lambda file: file.relative_path))


def _relative_manifest_path(root: Path, source: Path, path: Path, group: str) -> str:
    try:
        relative = path.relative_to(root)
        return relative.as_posix()
    except ValueError:
        pass
    try:
        relative_to_source = path.relative_to(source if source.is_dir() else source.parent)
    except ValueError:
        relative_to_source = Path(path.name)
    return (Path(group) / relative_to_source).as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_under_any(path: Path, candidates: set[Path]) -> bool:
    for candidate in candidates:
        try:
            path.relative_to(candidate)
            return True
        except ValueError:
            continue
    return False


def _is_excluded_file(path: Path, candidates: set[Path]) -> bool:
    return _is_under_any(path, candidates) or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}


def _issues_for_missing_paths(
    paths: Sequence[WorkbenchArtifactManifestPath],
) -> list[WorkbenchArtifactManifestIssue]:
    return [
        WorkbenchArtifactManifestIssue(
            code=f"{path.name}_missing",
            severity="error",
            message=f"workbench artifact manifest required path is missing or has wrong type: {path.path}",
        )
        for path in paths
        if path.required and not path.exists
    ]


def _excluded_paths(root: Path) -> tuple[str, ...]:
    return (
        str(root / ".git"),
        str(root / ".ims_workbench"),
        str(root / "logs"),
        str(root / "frontend" / "node_modules"),
        str(root / "frontend" / ".npm-cache"),
        str(root / "frontend" / "dist" / ".vite"),
        str(root / ".pytest_cache"),
        str(root / ".mypy_cache"),
        str(root / ".ruff_cache"),
        str(root / "__pycache__"),
        str(root / "metadata.sqlite"),
    )


def _resolve_against_root(root: Path, path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def _status_from_issues(issues: Sequence[WorkbenchArtifactManifestIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_artifact_manifest",
        description="Erzeugt ein lesendes Workbench-Artefaktmanifest, ohne Dateien zu schreiben.",
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Workbench-Repo- oder Artefaktwurzel.")
    parser.add_argument("--frontend-dist", type=Path, help="Expliziter Frontend-Dist-Pfad.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
