import json
import os
import subprocess
import sys
import hashlib
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
    assert len(payload["files"]) == payload["file_count"]
    assert included_names == [
        "python_port",
        "frontend_dist",
        "check_script",
        "start_script",
        "script_readme",
        "readme",
        "workbench_doc",
        "packaging_plan",
        "release_checklist",
        "metadata_recovery_doc",
    ]
    assert str(tmp_path / "frontend" / "node_modules") in payload["excluded_paths"]
    assert str(tmp_path / ".ims_workbench") in payload["excluded_paths"]
    assert str(tmp_path / "logs") in payload["excluded_paths"]


def test_workbench_artifact_manifest_files_are_sorted_and_hashed(tmp_path):
    _build_repo_fixture(tmp_path)
    _touch(tmp_path / "frontend" / "dist" / "z.js", "z")
    _touch(tmp_path / "frontend" / "dist" / "a.js", "alpha")

    payload = build_workbench_artifact_manifest(root=tmp_path).to_dict()
    files = payload["files"]
    relative_paths = [file["relative_path"] for file in files]
    alpha_entry = _file_by_relative_path(payload, "frontend/dist/a.js")

    assert relative_paths == sorted(relative_paths)
    assert alpha_entry["size_bytes"] == len("alpha")
    assert alpha_entry["sha256"] == hashlib.sha256(b"alpha").hexdigest()
    assert alpha_entry["group"] == "frontend_dist"
    assert Path(alpha_entry["source_path"]).is_file()


def test_workbench_artifact_manifest_excludes_cache_and_db_files_from_file_entries(tmp_path):
    _build_repo_fixture(tmp_path)
    _touch(tmp_path / "frontend" / "node_modules" / "pkg" / "ignored.js", "ignored")
    _touch(tmp_path / ".ims_workbench" / "metadata.sqlite", "local")
    _touch(tmp_path / "logs" / "workbench.log", "log")
    _touch(tmp_path / ".pytest_cache" / "ignored", "cache")
    _touch(tmp_path / "python_port" / "ims" / "__pycache__" / "ignored.pyc", "cache")

    payload = build_workbench_artifact_manifest(root=tmp_path).to_dict()
    relative_paths = [file["relative_path"] for file in payload["files"]]
    python_port_summary = _included_path_by_name(payload, "python_port")

    assert "frontend/node_modules/pkg/ignored.js" not in relative_paths
    assert ".ims_workbench/metadata.sqlite" not in relative_paths
    assert "logs/workbench.log" not in relative_paths
    assert ".pytest_cache/ignored" not in relative_paths
    assert "python_port/ims/__pycache__/ignored.pyc" not in relative_paths
    assert python_port_summary["file_count"] == 1


def test_workbench_artifact_manifest_preserves_external_frontend_dist_paths(tmp_path):
    repo_root = tmp_path / "repo"
    external_dist = tmp_path / "external dist"
    _build_repo_fixture(repo_root, include_frontend=False)
    _touch(external_dist / "assets" / "app.js", "asset")
    _touch(external_dist / "nested" / "app.js", "nested")

    payload = build_workbench_artifact_manifest(root=repo_root, frontend_dist=external_dist).to_dict()
    relative_paths = [file["relative_path"] for file in payload["files"]]

    assert "frontend_dist/assets/app.js" in relative_paths
    assert "frontend_dist/nested/app.js" in relative_paths
    assert len(relative_paths) == len(set(relative_paths))


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
    _touch(root / "docs" / "migration" / "workbench_release_checklist.md", "checklist")
    _touch(root / "docs" / "migration" / "workbench_metadata_recovery.md", "recovery")


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _file_by_relative_path(payload: dict[str, object], relative_path: str) -> dict[str, object]:
    files = payload["files"]
    assert isinstance(files, list)
    for file in files:
        if isinstance(file, dict) and file.get("relative_path") == relative_path:
            return file
    raise AssertionError(f"missing file: {relative_path}")


def _included_path_by_name(payload: dict[str, object], name: str) -> dict[str, object]:
    paths = payload["included_paths"]
    assert isinstance(paths, list)
    for path in paths:
        if isinstance(path, dict) and path.get("name") == name:
            return path
    raise AssertionError(f"missing included path: {name}")
