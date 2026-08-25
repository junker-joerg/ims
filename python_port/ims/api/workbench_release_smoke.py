from __future__ import annotations

import argparse
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.workbench_bundle_smoke import smoke_workbench_bundle_zip
from ims.api.workbench_portable_staging_smoke import smoke_workbench_portable_staging


CHECKLIST_VERSION = "pr67-v1"
RELEASE_CHECKLIST_ENTRY = "docs/migration/workbench_release_checklist.md"
REPO_SCRIPTS = (
    "scripts/workbench/check-workbench.cmd",
    "scripts/workbench/start-workbench.cmd",
)
FORBIDDEN_PRODUCTION_SCRIPT_FRAGMENTS = (
    "run_control_browser_demo_smoke",
    "controlled_smoke_adapter",
    "ims.api.controlled_execution_adapter",
)


@dataclass(frozen=True)
class WorkbenchReleaseSmokeIssue:
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
class WorkbenchReleaseSmokeResult:
    status: str
    mode: str
    checklist_version: str
    repo_root: str
    zip_path: str
    portable_root: str
    release_ready: bool
    bundle_ready: bool
    portable_ready: bool
    production_scripts_ready: bool
    artifact_scripts_match_repo: bool
    pr66_demo_adapter_separated: bool
    writes_performed: bool
    execution_performed: bool
    simulation_performed: bool
    historical_full_equality_claimed: bool
    bundle_smoke: dict[str, object]
    portable_smoke: dict[str, object]
    issues: tuple[WorkbenchReleaseSmokeIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "checklist_version": self.checklist_version,
            "repo_root": self.repo_root,
            "zip_path": self.zip_path,
            "portable_root": self.portable_root,
            "release_ready": self.release_ready,
            "bundle_ready": self.bundle_ready,
            "portable_ready": self.portable_ready,
            "production_scripts_ready": self.production_scripts_ready,
            "artifact_scripts_match_repo": self.artifact_scripts_match_repo,
            "pr66_demo_adapter_separated": self.pr66_demo_adapter_separated,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
            "bundle_smoke": self.bundle_smoke,
            "portable_smoke": self.portable_smoke,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def smoke_workbench_release(
    *,
    repo_root: Path | str,
    zip_path: Path | str,
    portable_root: Path | str,
) -> WorkbenchReleaseSmokeResult:
    resolved_repo_root = Path(repo_root).expanduser().resolve()
    resolved_zip_path = Path(zip_path).expanduser().resolve()
    resolved_portable_root = Path(portable_root).expanduser().resolve()

    bundle_smoke = smoke_workbench_bundle_zip(resolved_zip_path).to_dict()
    portable_smoke = smoke_workbench_portable_staging(resolved_portable_root).to_dict()
    issues = _nested_issues("bundle", bundle_smoke)
    issues.extend(_nested_issues("portable", portable_smoke))
    issues.extend(_release_artifact_issues(resolved_repo_root, resolved_zip_path, resolved_portable_root))

    status = _status_from_issues(issues)
    bundle_ready = bundle_smoke.get("status") == "ok"
    portable_ready = portable_smoke.get("status") == "ok"
    production_scripts_ready = (
        bundle_ready
        and portable_ready
        and not any(issue.code.startswith("production_script_") for issue in issues)
    )
    artifact_scripts_match_repo = bundle_ready and not any(
        issue.code.startswith("artifact_script_") for issue in issues
    )
    pr66_demo_adapter_separated = production_scripts_ready and not any(
        issue.code == "production_script_demo_adapter_reference" for issue in issues
    )
    release_ready = (
        status == "ok"
        and bundle_ready
        and portable_ready
        and production_scripts_ready
        and artifact_scripts_match_repo
        and pr66_demo_adapter_separated
    )
    return WorkbenchReleaseSmokeResult(
        status=status,
        mode="workbench_release_smoke",
        checklist_version=CHECKLIST_VERSION,
        repo_root=str(resolved_repo_root),
        zip_path=str(resolved_zip_path),
        portable_root=str(resolved_portable_root),
        release_ready=release_ready,
        bundle_ready=bundle_ready,
        portable_ready=portable_ready,
        production_scripts_ready=production_scripts_ready,
        artifact_scripts_match_repo=artifact_scripts_match_repo,
        pr66_demo_adapter_separated=pr66_demo_adapter_separated,
        writes_performed=False,
        execution_performed=False,
        simulation_performed=False,
        historical_full_equality_claimed=False,
        bundle_smoke=bundle_smoke,
        portable_smoke=portable_smoke,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = smoke_workbench_release(
        repo_root=args.repo_root,
        zip_path=args.zip_path,
        portable_root=args.portable_root,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.release_ready else 1


def _nested_issues(prefix: str, payload: dict[str, object]) -> list[WorkbenchReleaseSmokeIssue]:
    issues: list[WorkbenchReleaseSmokeIssue] = []
    for issue in payload.get("issues", []):
        if not isinstance(issue, dict):
            continue
        issues.append(
            WorkbenchReleaseSmokeIssue(
                code=f"{prefix}_{issue.get('code', 'failed')}",
                severity=str(issue.get("severity", "error")),
                message=str(issue.get("message", f"{prefix} smoke failed")),
            )
        )
    return issues


def _release_artifact_issues(repo_root: Path, zip_path: Path, portable_root: Path) -> list[WorkbenchReleaseSmokeIssue]:
    issues: list[WorkbenchReleaseSmokeIssue] = []
    repo_contents: dict[str, str] = {}
    for relative_path in REPO_SCRIPTS:
        script_path = repo_root / Path(relative_path)
        content = _read_script(script_path, f"repo:{relative_path}", issues)
        if content is not None:
            repo_contents[relative_path] = content
            issues.extend(_production_script_issues(f"repo:{relative_path}", content, portable=False))

    archive_contents = _read_archive_scripts(zip_path, issues)
    for relative_path, repo_content in repo_contents.items():
        archive_content = archive_contents.get(relative_path)
        if archive_content is None:
            continue
        if _normalized_newlines(archive_content) != _normalized_newlines(repo_content):
            issues.append(
                WorkbenchReleaseSmokeIssue(
                    code="artifact_script_repo_mismatch",
                    severity="error",
                    message=f"ZIP script does not match repository script: {relative_path}",
                )
            )
        issues.extend(_production_script_issues(f"zip:{relative_path}", archive_content, portable=False))

    portable_scripts = {
        "check-workbench.cmd": portable_root / "check-workbench.cmd",
        "start-workbench.cmd": portable_root / "start-workbench.cmd",
    }
    for relative_path, script_path in portable_scripts.items():
        content = _read_script(script_path, f"portable:{relative_path}", issues)
        if content is not None:
            issues.extend(_production_script_issues(f"portable:{relative_path}", content, portable=True))
    return issues


def _read_archive_scripts(zip_path: Path, issues: list[WorkbenchReleaseSmokeIssue]) -> dict[str, str]:
    if not zip_path.is_file():
        return {}
    contents: dict[str, str] = {}
    try:
        with zipfile.ZipFile(zip_path) as archive:
            names = set(archive.namelist())
            if RELEASE_CHECKLIST_ENTRY not in names:
                issues.append(
                    WorkbenchReleaseSmokeIssue(
                        code="artifact_release_checklist_missing",
                        severity="error",
                        message=f"ZIP is missing frozen release checklist: {RELEASE_CHECKLIST_ENTRY}",
                    )
                )
            for relative_path in REPO_SCRIPTS:
                if relative_path not in names:
                    issues.append(
                        WorkbenchReleaseSmokeIssue(
                            code="artifact_script_missing",
                            severity="error",
                            message=f"ZIP is missing production script: {relative_path}",
                        )
                    )
                    continue
                try:
                    contents[relative_path] = archive.read(relative_path).decode("utf-8")
                except UnicodeDecodeError as exc:
                    issues.append(
                        WorkbenchReleaseSmokeIssue(
                            code="artifact_script_unreadable",
                            severity="error",
                            message=f"ZIP production script is not UTF-8: {relative_path}: {exc}",
                        )
                    )
    except (OSError, zipfile.BadZipFile):
        return {}
    return contents


def _read_script(
    script_path: Path,
    label: str,
    issues: list[WorkbenchReleaseSmokeIssue],
) -> str | None:
    if not script_path.is_file():
        issues.append(
            WorkbenchReleaseSmokeIssue(
                code="production_script_missing",
                severity="error",
                message=f"production script is missing: {label}: {script_path}",
            )
        )
        return None
    try:
        return script_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        issues.append(
            WorkbenchReleaseSmokeIssue(
                code="production_script_unreadable",
                severity="error",
                message=f"production script is not UTF-8: {label}: {exc}",
            )
        )
        return None


def _production_script_issues(label: str, content: str, *, portable: bool) -> list[WorkbenchReleaseSmokeIssue]:
    issues: list[WorkbenchReleaseSmokeIssue] = []
    normalized = content.lower()
    for fragment in FORBIDDEN_PRODUCTION_SCRIPT_FRAGMENTS:
        if fragment.lower() in normalized:
            issues.append(
                WorkbenchReleaseSmokeIssue(
                    code="production_script_demo_adapter_reference",
                    severity="error",
                    message=f"production script references isolated demo adapter {fragment}: {label}",
                )
            )

    if label.endswith("start-workbench.cmd"):
        app_dir = "app/python_port" if portable else "python_port"
        required = (
            "python -m uvicorn ims.api.app:app",
            f"--app-dir {app_dir}",
            'IMS_WORKBENCH_HOST=127.0.0.1'.lower(),
        )
    else:
        required = (
            "ims.api.workbench_diagnostics",
            "ims.api.workbench_readiness",
        )
        if "uvicorn" in normalized:
            issues.append(
                WorkbenchReleaseSmokeIssue(
                    code="production_script_check_starts_server",
                    severity="error",
                    message=f"production check script must not start uvicorn: {label}",
                )
            )
    for fragment in required:
        if fragment.lower() not in normalized:
            issues.append(
                WorkbenchReleaseSmokeIssue(
                    code="production_script_contract_missing",
                    severity="error",
                    message=f"production script is missing required contract fragment {fragment}: {label}",
                )
            )
    return issues


def _normalized_newlines(content: str) -> str:
    return content.replace("\r\n", "\n").replace("\r", "\n")


def _status_from_issues(issues: Sequence[WorkbenchReleaseSmokeIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_release_smoke",
        description="Prueft ein vorbereitetes Workbench-ZIP und sein portables Staging rein lesend.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Expliziter Repository-Root.")
    parser.add_argument("--zip-path", type=Path, required=True, help="Expliziter Pfad zum vorbereiteten ZIP.")
    parser.add_argument("--portable-root", type=Path, required=True, help="Expliziter portabler Staging-Root.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
