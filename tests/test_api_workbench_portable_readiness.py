import json
import os
import subprocess
import sys
from pathlib import Path

from ims.api.workbench_portable_readiness import (
    WorkbenchPortableReadinessCheck,
    WorkbenchPortableReadinessIssue,
    WorkbenchPortableReadinessResult,
    build_workbench_portable_readiness,
    main,
)


def test_portable_readiness_accepts_repo_layout(tmp_path):
    _touch(tmp_path / "python_port" / "__init__.py")
    _touch(tmp_path / "frontend" / "dist" / "index.html")
    _touch(tmp_path / "scripts" / "workbench" / "start-workbench.cmd")
    _touch(tmp_path / "scripts" / "workbench" / "check-workbench.cmd")

    payload = build_workbench_portable_readiness(tmp_path, layout="repo").to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_portable_readiness"
    assert payload["layout"] == "repo"
    assert payload["portable_layout_ready"] is True
    assert payload["python_port_available"] is True
    assert payload["frontend_dist_available"] is True
    assert payload["start_script_available"] is True
    assert payload["check_script_available"] is True
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["issues"] == []


def test_portable_readiness_accepts_portable_layout_with_optional_dirs(tmp_path):
    _touch(tmp_path / "app" / "python_port" / "__init__.py")
    _touch(tmp_path / "app" / "frontend" / "dist" / "index.html")
    _touch(tmp_path / "start-workbench.cmd")
    _touch(tmp_path / "check-workbench.cmd")
    (tmp_path / "data" / ".ims_workbench").mkdir(parents=True)
    (tmp_path / "logs").mkdir()

    payload = build_workbench_portable_readiness(tmp_path, layout="portable").to_dict()

    assert payload["status"] == "ok"
    assert payload["layout"] == "portable"
    assert payload["portable_layout_ready"] is True
    assert payload["metadata_dir_available"] is True
    assert payload["logs_dir_available"] is True


def test_portable_readiness_auto_detects_portable_layout(tmp_path):
    _touch(tmp_path / "app" / "python_port" / "__init__.py")
    _touch(tmp_path / "app" / "frontend" / "dist" / "index.html")
    _touch(tmp_path / "start-workbench.cmd")
    _touch(tmp_path / "check-workbench.cmd")

    payload = build_workbench_portable_readiness(tmp_path).to_dict()

    assert payload["layout"] == "portable"
    assert payload["portable_layout_ready"] is True


def test_portable_readiness_reports_missing_required_paths(tmp_path):
    _touch(tmp_path / "python_port" / "__init__.py")

    payload = build_workbench_portable_readiness(tmp_path, layout="repo").to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["portable_layout_ready"] is False
    assert "frontend_dist_missing" in issue_codes
    assert "start_script_missing" in issue_codes
    assert "check_script_missing" in issue_codes
    assert not (tmp_path / ".ims_workbench").exists()


def test_portable_readiness_rejects_python_port_file(tmp_path):
    _touch(tmp_path / "python_port")
    _touch(tmp_path / "frontend" / "dist" / "index.html")
    _touch(tmp_path / "scripts" / "workbench" / "start-workbench.cmd")
    _touch(tmp_path / "scripts" / "workbench" / "check-workbench.cmd")

    payload = build_workbench_portable_readiness(tmp_path, layout="repo").to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}
    python_port_check = _check_by_name(payload, "python_port")

    assert payload["status"] == "error"
    assert payload["python_port_available"] is False
    assert "python_port_wrong_type" in issue_codes
    assert python_port_check["expected_type"] == "directory"
    assert python_port_check["actual_type"] == "file"


def test_portable_readiness_rejects_frontend_index_directory(tmp_path):
    _touch(tmp_path / "python_port" / "__init__.py")
    (tmp_path / "frontend" / "dist" / "index.html").mkdir(parents=True)
    _touch(tmp_path / "scripts" / "workbench" / "start-workbench.cmd")
    _touch(tmp_path / "scripts" / "workbench" / "check-workbench.cmd")

    payload = build_workbench_portable_readiness(tmp_path, layout="repo").to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}
    frontend_check = _check_by_name(payload, "frontend_dist")

    assert payload["status"] == "error"
    assert payload["frontend_dist_available"] is False
    assert "frontend_dist_wrong_type" in issue_codes
    assert frontend_check["expected_type"] == "file"
    assert frontend_check["actual_type"] == "directory"


def test_portable_readiness_rejects_start_script_directory(tmp_path):
    _touch(tmp_path / "app" / "python_port" / "__init__.py")
    _touch(tmp_path / "app" / "frontend" / "dist" / "index.html")
    (tmp_path / "start-workbench.cmd").mkdir()
    _touch(tmp_path / "check-workbench.cmd")

    payload = build_workbench_portable_readiness(tmp_path, layout="portable").to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}
    start_script_check = _check_by_name(payload, "start_script")

    assert payload["status"] == "error"
    assert payload["start_script_available"] is False
    assert "start_script_wrong_type" in issue_codes
    assert start_script_check["expected_type"] == "file"
    assert start_script_check["actual_type"] == "directory"


def test_portable_readiness_does_not_create_missing_root(tmp_path):
    missing_root = tmp_path / "missing-workbench"

    payload = build_workbench_portable_readiness(missing_root).to_dict()

    assert payload["status"] == "error"
    assert payload["layout"] == "missing"
    assert payload["issues"][0]["code"] == "portable_root_missing"
    assert not missing_root.exists()


def test_portable_readiness_cli_prints_stable_json(tmp_path, capsys):
    _touch(tmp_path / "app" / "python_port" / "__init__.py")
    _touch(tmp_path / "app" / "frontend" / "dist" / "index.html")
    _touch(tmp_path / "start-workbench.cmd")
    _touch(tmp_path / "check-workbench.cmd")

    exit_code = main(["--root", str(tmp_path), "--layout", "portable"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_portable_readiness"
    assert payload["layout"] == "portable"


def test_portable_readiness_module_entrypoint_prints_json(tmp_path):
    _touch(tmp_path / "python_port" / "__init__.py")
    _touch(tmp_path / "frontend" / "dist" / "index.html")
    _touch(tmp_path / "scripts" / "workbench" / "start-workbench.cmd")
    _touch(tmp_path / "scripts" / "workbench" / "check-workbench.cmd")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.workbench_portable_readiness",
            "--root",
            str(tmp_path),
            "--layout",
            "repo",
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert payload["status"] == "ok"
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert completed.stderr == ""
    assert WorkbenchPortableReadinessIssue is not None
    assert WorkbenchPortableReadinessCheck is not None
    assert WorkbenchPortableReadinessResult is not None


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def _check_by_name(payload: dict[str, object], name: str) -> dict[str, object]:
    checks = payload["checks"]
    assert isinstance(checks, list)
    for check in checks:
        if isinstance(check, dict) and check.get("name") == name:
            return check
    raise AssertionError(f"missing check: {name}")
