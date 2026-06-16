import json
import os
import subprocess
import sys
from pathlib import Path

from ims.api.workbench_artifact_manifest import (
    WorkbenchArtifactManifestIssue,
    WorkbenchArtifactManifestPath,
    WorkbenchArtifactManifestResult,
    build_workbench_artifact_manifest,
    main,
)


def test_workbench_artifact_manifest_reports_included_and_excluded_paths(tmp_path):
    _build_repo_fixture(tmp_path)
    _touch(tmp_path / "frontend" / "dist" / "assets" / "index.js", "console.log('ok');")
    _touch(tmp_path / "frontend" / "node_modules" / "pkg" / "ignored.js", "ignored")
    _touch(tmp_path / ".ims_workbench" / "metadata.sqlite", "local")

    payload = build_workbench_artifact_manifest(root=tmp_path).to_dict()
    included_names = [item["name"] for item in payload["included_paths"]]

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_artifact_manifest"
    assert payload["root"] == str(tmp_path.resolve())
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["missing_required_paths"] == []
    assert payload["file_count"] >= 9
    assert payload["total_bytes"] > 0
    assert included_names == [
        "python_port",
        "frontend_dist",
        "check_script",
        "start_script",
        "script_readme",
        "readme",
        "workbench_doc",
        "packaging_plan",
    ]
    assert str(tmp_path / "frontend" / "node_modules") in payload["excluded_paths"]
    assert str(tmp_path / ".ims_workbench") in payload["excluded_paths"]
    assert str(tmp_path / "logs") in payload["excluded_paths"]


def test_workbench_artifact_manifest_resolves_relative_frontend_dist_against_root(tmp_path, monkeypatch):
    _build_repo_fixture(tmp_path, frontend_dist=Path("custom") / "dist")
    other_cwd = tmp_path / "elsewhere"
    other_cwd.mkdir()
    monkeypatch.chdir(other_cwd)

    payload = build_workbench_artifact_manifest(root=tmp_path, frontend_dist=Path("custom") / "dist").to_dict()

    assert payload["status"] == "ok"
    assert payload["frontend_dist"] == str((tmp_path / "custom" / "dist").resolve())


def test_workbench_artifact_manifest_reports_missing_frontend_dist_without_creating_it(tmp_path):
    _build_repo_fixture(tmp_path, include_frontend=False)

    payload = build_workbench_artifact_manifest(root=tmp_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "frontend_dist" in payload["missing_required_paths"]
    assert "frontend_dist_missing" in issue_codes
    assert not (tmp_path / "frontend" / "dist").exists()
    assert not (tmp_path / "metadata.sqlite").exists()


def test_workbench_artifact_manifest_cli_prints_stable_json(tmp_path, capsys):
    _build_repo_fixture(tmp_path)

    exit_code = main(["--root", str(tmp_path), "--frontend-dist", "frontend/dist"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_artifact_manifest"
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False


def test_workbench_artifact_manifest_module_entrypoint_prints_json(tmp_path):
    _build_repo_fixture(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.workbench_artifact_manifest",
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
    assert WorkbenchArtifactManifestIssue is not None
    assert WorkbenchArtifactManifestPath is not None
    assert WorkbenchArtifactManifestResult is not None


def _build_repo_fixture(
    root: Path,
    *,
    frontend_dist: Path = Path("frontend") / "dist",
    include_frontend: bool = True,
) -> None:
    _touch(root / "python_port" / "__init__.py")
    if include_frontend:
        _touch(root / frontend_dist / "index.html", "<html></html>")
    _touch(root / "scripts" / "workbench" / "check-workbench.cmd")
    _touch(root / "scripts" / "workbench" / "start-workbench.cmd")
    _touch(root / "scripts" / "workbench" / "README.md", "scripts")
    _touch(root / "README.md", "readme")
    _touch(root / "docs" / "migration" / "workbench_shell.md", "workbench")
    _touch(root / "docs" / "migration" / "workbench_packaging_plan.md", "packaging")


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
