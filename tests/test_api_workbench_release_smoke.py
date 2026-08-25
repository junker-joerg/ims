import json
import zipfile
from pathlib import Path

from ims.api.workbench_bundle_build import build_workbench_bundle_zip
from ims.api.workbench_portable_staging import stage_workbench_portable_bundle
from ims.api.workbench_release_smoke import (
    WorkbenchReleaseSmokeIssue,
    WorkbenchReleaseSmokeResult,
    main,
    smoke_workbench_release,
)


REPO_CHECK_SCRIPT = """@echo off
set IMS_WORKBENCH_HOST=127.0.0.1
python -m ims.api.workbench_diagnostics
python -m ims.api.workbench_readiness
"""
REPO_START_SCRIPT = """@echo off
set IMS_WORKBENCH_HOST=127.0.0.1
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
"""


def test_workbench_release_smoke_accepts_prepared_release(tmp_path):
    repo_root, zip_path, portable_root = _prepare_release(tmp_path)

    payload = smoke_workbench_release(
        repo_root=repo_root,
        zip_path=zip_path,
        portable_root=portable_root,
    ).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_release_smoke"
    assert payload["checklist_version"] == "pr67-v1"
    assert payload["release_ready"] is True
    assert payload["bundle_ready"] is True
    assert payload["portable_ready"] is True
    assert payload["production_scripts_ready"] is True
    assert payload["artifact_scripts_match_repo"] is True
    assert payload["pr66_demo_adapter_separated"] is True
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["issues"] == []


def test_workbench_release_smoke_blocks_demo_adapter_in_production_script(tmp_path):
    repo_root, zip_path, portable_root = _prepare_release(tmp_path)
    (portable_root / "start-workbench.cmd").write_text(
        REPO_START_SCRIPT + "python -m ims.api.run_control_browser_demo_smoke\n",
        encoding="utf-8",
    )

    payload = smoke_workbench_release(
        repo_root=repo_root,
        zip_path=zip_path,
        portable_root=portable_root,
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["release_ready"] is False
    assert payload["production_scripts_ready"] is False
    assert payload["pr66_demo_adapter_separated"] is False
    assert "production_script_demo_adapter_reference" in issue_codes


def test_workbench_release_smoke_blocks_repo_script_changed_after_zip_build(tmp_path):
    repo_root, zip_path, portable_root = _prepare_release(tmp_path)
    (repo_root / "scripts" / "workbench" / "start-workbench.cmd").write_text(
        REPO_START_SCRIPT + "rem changed after build\n",
        encoding="utf-8",
    )

    payload = smoke_workbench_release(
        repo_root=repo_root,
        zip_path=zip_path,
        portable_root=portable_root,
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["artifact_scripts_match_repo"] is False
    assert "artifact_script_repo_mismatch" in issue_codes


def test_workbench_release_smoke_requires_frozen_checklist_in_zip(tmp_path):
    repo_root, zip_path, portable_root = _prepare_release(tmp_path)
    _remove_zip_entry(zip_path, "docs/migration/workbench_release_checklist.md")

    payload = smoke_workbench_release(
        repo_root=repo_root,
        zip_path=zip_path,
        portable_root=portable_root,
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["release_ready"] is False
    assert "artifact_release_checklist_missing" in issue_codes


def test_workbench_release_smoke_cli_prints_stable_json(tmp_path, capsys):
    repo_root, zip_path, portable_root = _prepare_release(tmp_path)

    exit_code = main(
        [
            "--repo-root",
            str(repo_root),
            "--zip-path",
            str(zip_path),
            "--portable-root",
            str(portable_root),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["release_ready"] is True


def test_workbench_release_smoke_keeps_missing_inputs_read_only(tmp_path):
    repo_root = tmp_path / "missing-repo"
    zip_path = tmp_path / "missing.zip"
    portable_root = tmp_path / "missing-portable"

    payload = smoke_workbench_release(
        repo_root=repo_root,
        zip_path=zip_path,
        portable_root=portable_root,
    ).to_dict()

    assert payload["status"] == "error"
    assert payload["release_ready"] is False
    assert payload["bundle_ready"] is False
    assert payload["portable_ready"] is False
    assert payload["production_scripts_ready"] is False
    assert payload["artifact_scripts_match_repo"] is False
    assert payload["pr66_demo_adapter_separated"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert not repo_root.exists()
    assert not zip_path.exists()
    assert not portable_root.exists()


def test_workbench_release_smoke_public_types_importable():
    assert WorkbenchReleaseSmokeIssue is not None
    assert WorkbenchReleaseSmokeResult is not None


def _prepare_release(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo_root = tmp_path / "repo"
    _build_repo_fixture(repo_root)
    zip_path = tmp_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir()
    build_result = build_workbench_bundle_zip(root=repo_root, out_path=zip_path)
    assert build_result.status == "ok"
    portable_root = tmp_path / "ims-workbench"
    staging_result = stage_workbench_portable_bundle(zip_path=zip_path, out_path=portable_root)
    assert staging_result.status == "ok"
    return repo_root, zip_path, portable_root


def _build_repo_fixture(root: Path) -> None:
    _touch(root / "python_port" / "__init__.py", "python")
    _touch(root / "python_port" / "ims" / "__init__.py", "# ims\n")
    _touch(root / "python_port" / "ims" / "api" / "__init__.py", "# api\n")
    _touch(root / "python_port" / "ims" / "api" / "app.py", "# app\n")
    _touch(root / "python_port" / "ims" / "api" / "workbench_diagnostics.py", "# diagnostics\n")
    _touch(root / "python_port" / "ims" / "api" / "workbench_readiness.py", "# readiness\n")
    _touch(root / "frontend" / "dist" / "index.html", "<html></html>")
    _touch(root / "scripts" / "workbench" / "check-workbench.cmd", REPO_CHECK_SCRIPT)
    _touch(root / "scripts" / "workbench" / "start-workbench.cmd", REPO_START_SCRIPT)
    _touch(root / "scripts" / "workbench" / "README.md", "scripts")
    _touch(root / "scripts" / "workbench" / "test-release-gate.ps1", "gate")
    _touch(root / "README.md", "readme")
    _touch(root / "docs" / "migration" / "workbench_shell.md", "workbench doc")
    _touch(root / "docs" / "migration" / "workbench_packaging_plan.md", "packaging plan")
    _touch(root / "docs" / "migration" / "workbench_release_checklist.md", "release checklist")
    _touch(root / "docs" / "migration" / "workbench_metadata_recovery.md", "metadata recovery")
    _touch(root / "docs" / "migration" / "production_release_corpus_report.md", "report")
    _touch(root / "docs" / "migration" / "windows_release_gate.md", "gate doc")


def _touch(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _remove_zip_entry(zip_path: Path, removed_entry: str) -> None:
    rewritten_path = zip_path.with_name("rewritten.zip")
    with zipfile.ZipFile(zip_path) as source, zipfile.ZipFile(rewritten_path, mode="w") as target:
        for info in source.infolist():
            if info.filename != removed_entry:
                target.writestr(info, source.read(info.filename))
    rewritten_path.replace(zip_path)
