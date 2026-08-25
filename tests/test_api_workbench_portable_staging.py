import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

from ims.api.workbench_bundle_build import build_workbench_bundle_zip
from ims.api.workbench_portable_readiness import build_workbench_portable_readiness
from ims.api.workbench_portable_staging import (
    WorkbenchPortableStagingFile,
    WorkbenchPortableStagingIssue,
    WorkbenchPortableStagingResult,
    main,
    stage_workbench_portable_bundle,
)


def test_portable_staging_creates_portable_layout_from_bundle_zip(tmp_path):
    repo_root = tmp_path / "repo"
    _build_repo_fixture(repo_root)
    _touch(repo_root / "frontend" / "dist" / "assets" / "app.js", "asset")
    zip_path = tmp_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir()
    build_workbench_bundle_zip(root=repo_root, out_path=zip_path)
    out_path = tmp_path / "ims workbench portable"

    payload = stage_workbench_portable_bundle(zip_path=zip_path, out_path=out_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_portable_staging"
    assert payload["zip_path"] == str(zip_path.resolve())
    assert payload["out_path"] == str(out_path.resolve())
    assert payload["writes_performed"] is True
    assert payload["execution_performed"] is False
    assert payload["staged_file_count"] > 0
    assert (out_path / "app" / "python_port" / "__init__.py").is_file()
    assert (out_path / "app" / "frontend" / "dist" / "index.html").is_file()
    assert (out_path / "app" / "frontend" / "dist" / "assets" / "app.js").is_file()
    assert (out_path / "start-workbench.cmd").is_file()
    assert (out_path / "check-workbench.cmd").is_file()
    check_script = (out_path / "check-workbench.cmd").read_text(encoding="utf-8")
    start_script = (out_path / "start-workbench.cmd").read_text(encoding="utf-8")
    assert "IMS_FRONTEND_DIST=%WORKBENCH_ROOT%\\app\\frontend\\dist" in check_script
    assert "IMS_METADATA_DB=%WORKBENCH_ROOT%\\data\\.ims_workbench\\metadata.sqlite" in check_script
    assert '%IMS_FRONTEND_DIST%\\index.html' in check_script
    assert 'if exist "%IMS_METADATA_DB%"' in check_script
    assert '--frontend-dist "%IMS_FRONTEND_DIST%" --db "%IMS_METADATA_DB%"' in check_script
    assert "IMS_WORKBENCH_HOST=127.0.0.1" in start_script
    assert "IMS_WORKBENCH_PORT=8000" in start_script
    assert "app\\python_port" in start_script
    assert "--app-dir app/python_port" in start_script
    assert '--host "%IMS_WORKBENCH_HOST%" --port "%IMS_WORKBENCH_PORT%"' in start_script
    assert (out_path / "data" / ".ims_workbench").is_dir()
    assert (out_path / "logs").is_dir()
    readiness = build_workbench_portable_readiness(out_path, layout="portable").to_dict()
    assert readiness["status"] == "ok"
    assert payload["portable_readiness"]["status"] == "ok"


def test_portable_staging_rejects_non_empty_target_without_overwriting_user_data(tmp_path):
    repo_root = tmp_path / "repo"
    _build_repo_fixture(repo_root)
    zip_path = tmp_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir()
    build_workbench_bundle_zip(root=repo_root, out_path=zip_path)
    out_path = tmp_path / "ims-workbench"
    _touch(out_path / "data" / ".ims_workbench" / "metadata.sqlite", "user data")

    payload = stage_workbench_portable_bundle(zip_path=zip_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["writes_performed"] is False
    assert "out_path_not_empty" in issue_codes
    assert (out_path / "data" / ".ims_workbench" / "metadata.sqlite").read_text(encoding="utf-8") == "user data"
    assert not (out_path / "app").exists()


def test_portable_staging_rejects_bad_bundle_zip(tmp_path):
    zip_path = tmp_path / "bundle.zip"
    zip_path.write_text("not a zip", encoding="utf-8")
    out_path = tmp_path / "ims-workbench"

    payload = stage_workbench_portable_bundle(zip_path=zip_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["writes_performed"] is False
    assert "zip_smoke_failed" in issue_codes
    assert not out_path.exists()


def test_portable_staging_rejects_zip_inside_output_target(tmp_path):
    out_path = tmp_path / "ims-workbench"
    zip_path = out_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir(parents=True)
    zip_path.write_text("not a zip", encoding="utf-8")

    payload = stage_workbench_portable_bundle(zip_path=zip_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["writes_performed"] is False
    assert "zip_path_inside_out_path" in issue_codes


def test_portable_staging_rejects_entry_that_escapes_output_target(tmp_path):
    zip_path = tmp_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir()
    out_path = tmp_path / "ims-workbench"
    _write_zip(
        zip_path,
        {
            "README.md": "readme",
            "python_port/__init__.py": "python",
            "frontend/dist/index.html": "<html></html>",
            "scripts/workbench/check-workbench.cmd": "check",
            "scripts/workbench/start-workbench.cmd": "start",
            "scripts/workbench/README.md": "scripts",
            "docs/migration/workbench_shell.md": "workbench doc",
            "docs/migration/workbench_packaging_plan.md": "packaging plan",
            "python_port/../../outside.txt": "escape",
        },
    )

    payload = stage_workbench_portable_bundle(zip_path=zip_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["writes_performed"] is False
    assert "zip_entry_escapes_out_path" in issue_codes
    assert not (tmp_path / "outside.txt").exists()


def test_portable_staging_rejects_backslash_traversal_entry(tmp_path):
    zip_path = tmp_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir()
    out_path = tmp_path / "ims-workbench"
    entries = _valid_bundle_entries()
    entries["python_port/..\\..\\data\\.ims_workbench\\metadata.sqlite"] = "escape"
    _write_zip(zip_path, entries)

    payload = stage_workbench_portable_bundle(zip_path=zip_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["writes_performed"] is False
    assert "zip_entry_escapes_out_path" in issue_codes
    assert not (tmp_path / "data" / ".ims_workbench" / "metadata.sqlite").exists()


def test_portable_staging_rejects_truncated_backend_tree(tmp_path):
    zip_path = tmp_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir()
    out_path = tmp_path / "ims-workbench"
    _write_zip(
        zip_path,
        {
            "README.md": "readme",
            "python_port/__init__.py": "python",
            "frontend/dist/index.html": "<html></html>",
            "scripts/workbench/check-workbench.cmd": "check",
            "scripts/workbench/start-workbench.cmd": "start",
            "scripts/workbench/README.md": "scripts",
            "docs/migration/workbench_shell.md": "workbench doc",
            "docs/migration/workbench_packaging_plan.md": "packaging plan",
        },
    )

    payload = stage_workbench_portable_bundle(zip_path=zip_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["writes_performed"] is False
    assert "backend_entry_missing" in issue_codes
    assert not out_path.exists()


def test_portable_staging_cli_prints_stable_json(tmp_path, capsys):
    repo_root = tmp_path / "repo"
    _build_repo_fixture(repo_root)
    zip_path = tmp_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir()
    build_workbench_bundle_zip(root=repo_root, out_path=zip_path)
    out_path = tmp_path / "ims-workbench"

    exit_code = main(["--zip-path", str(zip_path), "--out", str(out_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_portable_staging"
    assert payload["portable_readiness"]["layout"] == "portable"


def test_portable_staging_module_entrypoint_prints_json(tmp_path):
    repo_root = tmp_path / "repo"
    _build_repo_fixture(repo_root)
    zip_path = tmp_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir()
    build_workbench_bundle_zip(root=repo_root, out_path=zip_path)
    out_path = tmp_path / "ims-workbench"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.workbench_portable_staging",
            "--zip-path",
            str(zip_path),
            "--out",
            str(out_path),
        ],
        capture_output=True,
        check=True,
        env=env,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["status"] == "ok"
    assert payload["writes_performed"] is True
    assert payload["execution_performed"] is False


def test_portable_staging_public_types_importable():
    assert WorkbenchPortableStagingIssue is not None
    assert WorkbenchPortableStagingFile is not None
    assert WorkbenchPortableStagingResult is not None


def _build_repo_fixture(root: Path) -> None:
    _touch(root / "python_port" / "__init__.py", "python")
    _touch(root / "python_port" / "ims" / "__init__.py", "ims")
    _touch(root / "python_port" / "ims" / "api" / "__init__.py", "api")
    _touch(root / "python_port" / "ims" / "api" / "app.py", "app")
    _touch(root / "python_port" / "ims" / "api" / "workbench_diagnostics.py", "diagnostics")
    _touch(root / "python_port" / "ims" / "api" / "workbench_readiness.py", "readiness")
    _touch(root / "frontend" / "dist" / "index.html", "<html></html>")
    _touch(root / "scripts" / "workbench" / "check-workbench.cmd", "check")
    _touch(root / "scripts" / "workbench" / "start-workbench.cmd", "start")
    _touch(root / "scripts" / "workbench" / "README.md", "scripts")
    _touch(root / "README.md", "readme")
    _touch(root / "docs" / "migration" / "workbench_shell.md", "workbench doc")
    _touch(root / "docs" / "migration" / "workbench_packaging_plan.md", "packaging plan")
    _touch(root / "docs" / "migration" / "workbench_release_checklist.md", "release checklist")
    _touch(root / "docs" / "migration" / "workbench_metadata_recovery.md", "metadata recovery")


def _touch(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_zip(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, content)


def _valid_bundle_entries() -> dict[str, str]:
    return {
        "README.md": "readme",
        "python_port/__init__.py": "python",
        "python_port/ims/__init__.py": "ims",
        "python_port/ims/api/__init__.py": "api",
        "python_port/ims/api/app.py": "app",
        "python_port/ims/api/workbench_diagnostics.py": "diagnostics",
        "python_port/ims/api/workbench_readiness.py": "readiness",
        "frontend/dist/index.html": "<html></html>",
        "scripts/workbench/check-workbench.cmd": "check",
        "scripts/workbench/start-workbench.cmd": "start",
        "scripts/workbench/README.md": "scripts",
        "docs/migration/workbench_shell.md": "workbench doc",
        "docs/migration/workbench_packaging_plan.md": "packaging plan",
    }
