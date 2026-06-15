import json
import os
import subprocess
import sys
from pathlib import Path

from ims.api.workbench_build_snapshot import (
    WorkbenchBuildSnapshotCheck,
    WorkbenchBuildSnapshotIssue,
    WorkbenchBuildSnapshotResult,
    build_workbench_build_snapshot,
    main,
)


def test_workbench_build_snapshot_reports_existing_repo_artifacts(tmp_path):
    _build_repo_fixture(tmp_path)
    _touch(tmp_path / "frontend" / "dist" / "assets" / "index.js", "console.log('ok');")

    payload = build_workbench_build_snapshot(root=tmp_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_build_snapshot"
    assert payload["root"] == str(tmp_path.resolve())
    assert payload["frontend_index_available"] is True
    assert payload["frontend_asset_count"] == 2
    assert payload["frontend_asset_bytes"] > 0
    assert payload["python_port_available"] is True
    assert payload["start_script_available"] is True
    assert payload["check_script_available"] is True
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["issues"] == []
    assert str(tmp_path / "frontend" / "node_modules") in payload["excluded_paths"]
    assert str(tmp_path / ".ims_workbench") in payload["excluded_paths"]


def test_workbench_build_snapshot_resolves_relative_frontend_dist_against_root(tmp_path, monkeypatch):
    _build_repo_fixture(tmp_path, frontend_dist=Path("custom") / "dist")
    other_cwd = tmp_path / "elsewhere"
    other_cwd.mkdir()
    monkeypatch.chdir(other_cwd)

    payload = build_workbench_build_snapshot(root=tmp_path, frontend_dist=Path("custom") / "dist").to_dict()

    assert payload["status"] == "ok"
    assert payload["frontend_dist"] == str((tmp_path / "custom" / "dist").resolve())
    assert payload["frontend_index_available"] is True


def test_workbench_build_snapshot_reports_missing_frontend_dist_without_creating_it(tmp_path):
    _touch(tmp_path / "python_port" / "__init__.py")
    _touch(tmp_path / "scripts" / "workbench" / "start-workbench.cmd")
    _touch(tmp_path / "scripts" / "workbench" / "check-workbench.cmd")

    payload = build_workbench_build_snapshot(root=tmp_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["frontend_index_available"] is False
    assert payload["frontend_asset_count"] == 0
    assert "frontend_dist_missing" in issue_codes
    assert "frontend_index_missing" in issue_codes
    assert not (tmp_path / "frontend" / "dist").exists()
    assert not (tmp_path / ".ims_workbench").exists()


def test_workbench_build_snapshot_cli_prints_stable_json(tmp_path, capsys):
    _build_repo_fixture(tmp_path)

    exit_code = main(["--root", str(tmp_path), "--frontend-dist", "frontend/dist"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_build_snapshot"
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False


def test_workbench_build_snapshot_module_entrypoint_prints_json(tmp_path):
    _build_repo_fixture(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.workbench_build_snapshot",
            "--root",
            str(tmp_path),
            "--frontend-dist",
            "frontend/dist",
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert payload["status"] == "ok"
    assert completed.stderr == ""
    assert WorkbenchBuildSnapshotIssue is not None
    assert WorkbenchBuildSnapshotCheck is not None
    assert WorkbenchBuildSnapshotResult is not None


def _build_repo_fixture(root: Path, *, frontend_dist: Path = Path("frontend") / "dist") -> None:
    _touch(root / "python_port" / "__init__.py")
    _touch(root / frontend_dist / "index.html", "<html></html>")
    _touch(root / "scripts" / "workbench" / "start-workbench.cmd")
    _touch(root / "scripts" / "workbench" / "check-workbench.cmd")


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
