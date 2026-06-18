import json
import os
import subprocess
import sys
from pathlib import Path

from ims.api.workbench_bundle_build import build_workbench_bundle_zip
from ims.api.workbench_portable_staging import stage_workbench_portable_bundle
from ims.api.workbench_portable_staging_smoke import (
    WorkbenchPortableStagingSmokeIssue,
    WorkbenchPortableStagingSmokeResult,
    main,
    smoke_workbench_portable_staging,
)


def test_portable_staging_smoke_accepts_staged_bundle(tmp_path):
    root = _stage_valid_bundle(tmp_path)

    payload = smoke_workbench_portable_staging(root).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_portable_staging_smoke"
    assert payload["root"] == str(root.resolve())
    assert payload["portable_layout_ready"] is True
    assert payload["frontend_dist_available"] is True
    assert payload["python_port_available"] is True
    assert payload["backend_ready"] is True
    assert payload["scripts_ready"] is True
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["issues"] == []


def test_portable_staging_smoke_reports_missing_frontend(tmp_path):
    root = _stage_valid_bundle(tmp_path)
    (root / "app" / "frontend" / "dist" / "index.html").unlink()

    payload = smoke_workbench_portable_staging(root).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["frontend_dist_available"] is False
    assert "portable_readiness_frontend_dist_missing" in issue_codes


def test_portable_staging_smoke_reports_missing_backend_module(tmp_path):
    root = _stage_valid_bundle(tmp_path)
    (root / "app" / "python_port" / "ims" / "api" / "app.py").unlink()

    payload = smoke_workbench_portable_staging(root).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["backend_ready"] is False
    assert "backend_entry_missing" in issue_codes


def test_portable_staging_smoke_reports_repo_scripts(tmp_path):
    root = _stage_valid_bundle(tmp_path)
    (root / "start-workbench.cmd").write_text(
        "python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000",
        encoding="utf-8",
    )

    payload = smoke_workbench_portable_staging(root).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["scripts_ready"] is False
    assert "portable_script_not_portable" in issue_codes


def test_portable_staging_smoke_does_not_create_missing_root(tmp_path):
    root = tmp_path / "missing"

    payload = smoke_workbench_portable_staging(root).to_dict()

    assert payload["status"] == "error"
    assert payload["writes_performed"] is False
    assert not root.exists()


def test_portable_staging_smoke_cli_prints_stable_json(tmp_path, capsys):
    root = _stage_valid_bundle(tmp_path)

    exit_code = main(["--root", str(root)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_portable_staging_smoke"


def test_portable_staging_smoke_module_entrypoint_prints_json(tmp_path):
    root = _stage_valid_bundle(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.workbench_portable_staging_smoke",
            "--root",
            str(root),
        ],
        capture_output=True,
        check=True,
        env=env,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["status"] == "ok"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_portable_staging_smoke_public_types_importable():
    assert WorkbenchPortableStagingSmokeIssue is not None
    assert WorkbenchPortableStagingSmokeResult is not None


def _stage_valid_bundle(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    _build_repo_fixture(repo_root)
    zip_path = tmp_path / "dist" / "ims-workbench-local.zip"
    zip_path.parent.mkdir()
    build_workbench_bundle_zip(root=repo_root, out_path=zip_path)
    out_path = tmp_path / "ims-workbench"
    payload = stage_workbench_portable_bundle(zip_path=zip_path, out_path=out_path).to_dict()
    assert payload["status"] == "ok"
    return out_path


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


def _touch(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
