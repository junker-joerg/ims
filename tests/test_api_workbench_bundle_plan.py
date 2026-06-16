import json
import os
import subprocess
import sys
from pathlib import Path

from ims.api.workbench_bundle_plan import (
    WorkbenchBundlePlanIssue,
    WorkbenchBundlePlanResult,
    build_workbench_bundle_plan,
    main,
)


def test_workbench_bundle_plan_uses_artifact_manifest_files(tmp_path):
    _build_repo_fixture(tmp_path)
    _touch(tmp_path / "frontend" / "dist" / "assets" / "app.js", "bundle")

    payload = build_workbench_bundle_plan(root=tmp_path).to_dict()
    relative_paths = [file["relative_path"] for file in payload["files"]]

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_bundle_plan"
    assert payload["recommended_bundle_name"] == f"{tmp_path.name}-local-workbench.zip"
    assert payload["file_count"] == len(payload["files"])
    assert payload["total_bytes"] > 0
    assert "frontend/dist/assets/app.js" in relative_paths
    assert payload["files"] == sorted(payload["files"], key=lambda file: file["relative_path"])
    assert all(file["sha256"] for file in payload["files"])
    assert payload["writes_performed"] is False
    assert payload["archive_created"] is False
    assert payload["execution_performed"] is False


def test_workbench_bundle_plan_excludes_local_runtime_paths(tmp_path):
    _build_repo_fixture(tmp_path)
    _touch(tmp_path / ".ims_workbench" / "metadata.sqlite", "local")
    _touch(tmp_path / "logs" / "workbench.log", "log")
    _touch(tmp_path / "frontend" / "node_modules" / "pkg" / "ignored.js", "ignored")
    _touch(tmp_path / "python_port" / "ims" / "__pycache__" / "ignored.pyc", "cache")

    payload = build_workbench_bundle_plan(root=tmp_path).to_dict()
    relative_paths = [file["relative_path"] for file in payload["files"]]

    assert ".ims_workbench/metadata.sqlite" not in relative_paths
    assert "logs/workbench.log" not in relative_paths
    assert "frontend/node_modules/pkg/ignored.js" not in relative_paths
    assert "python_port/ims/__pycache__/ignored.pyc" not in relative_paths


def test_workbench_bundle_plan_reports_missing_frontend_dist_without_writing(tmp_path):
    _build_repo_fixture(tmp_path, include_frontend=False)

    payload = build_workbench_bundle_plan(root=tmp_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "frontend_dist_missing" in issue_codes
    assert payload["writes_performed"] is False
    assert payload["archive_created"] is False
    assert not (tmp_path / "frontend" / "dist").exists()
    assert not (tmp_path / f"{tmp_path.name}-local-workbench.zip").exists()


def test_workbench_bundle_plan_cli_prints_stable_json(tmp_path, capsys):
    _build_repo_fixture(tmp_path)

    exit_code = main(["--root", str(tmp_path), "--frontend-dist", "frontend/dist"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_bundle_plan"
    assert payload["archive_created"] is False


def test_workbench_bundle_plan_module_entrypoint_prints_json(tmp_path):
    _build_repo_fixture(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.workbench_bundle_plan",
            "--root",
            str(tmp_path),
            "--frontend-dist",
            "frontend/dist",
        ],
        capture_output=True,
        check=True,
        env=env,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_bundle_plan"


def test_workbench_bundle_plan_public_types_importable():
    assert WorkbenchBundlePlanIssue is not None
    assert WorkbenchBundlePlanResult is not None


def _build_repo_fixture(tmp_path: Path, *, include_frontend: bool = True) -> None:
    _touch(tmp_path / "python_port" / "__init__.py")
    _touch(tmp_path / "scripts" / "workbench" / "check-workbench.cmd", "check")
    _touch(tmp_path / "scripts" / "workbench" / "start-workbench.cmd", "start")
    _touch(tmp_path / "scripts" / "workbench" / "README.md", "scripts")
    _touch(tmp_path / "README.md", "readme")
    _touch(tmp_path / "docs" / "migration" / "workbench_shell.md", "workbench doc")
    _touch(tmp_path / "docs" / "migration" / "workbench_packaging_plan.md", "packaging plan")
    if include_frontend:
        _touch(tmp_path / "frontend" / "dist" / "index.html", "<html></html>")


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
