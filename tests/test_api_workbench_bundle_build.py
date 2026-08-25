import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from ims.api.workbench_bundle_build import (
    WorkbenchBundleBuildIssue,
    WorkbenchBundleBuildResult,
    build_workbench_bundle_zip,
    main,
)


def test_workbench_bundle_build_writes_explicit_zip(tmp_path):
    _build_repo_fixture(tmp_path)
    _touch(tmp_path / "frontend" / "dist" / "assets" / "app.js", "bundle")
    out_path = tmp_path / "dist" / "ims-workbench-local.zip"
    out_path.parent.mkdir()

    payload = build_workbench_bundle_zip(root=tmp_path, out_path=out_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_bundle_build"
    assert payload["out_path"] == str(out_path.resolve())
    assert payload["archive_created"] is True
    assert payload["writes_performed"] is True
    assert payload["execution_performed"] is False
    assert payload["zip_bytes"] > 0
    assert len(payload["zip_sha256"]) == 64
    assert out_path.is_file()
    with zipfile.ZipFile(out_path) as archive:
        names = archive.namelist()
    assert names == payload["entries"]
    assert "frontend/dist/index.html" in names
    assert "frontend/dist/assets/app.js" in names


def test_workbench_bundle_build_zip_smoke_covers_expected_bundle_boundaries(tmp_path):
    _build_repo_fixture(tmp_path)
    _touch(tmp_path / "python_port" / "ims" / "api" / "app.py", "app")
    _touch(tmp_path / "python_port" / "ims" / "__pycache__" / "ignored.pyc", "cache")
    _touch(tmp_path / "frontend" / "dist" / "assets" / "app.js", "bundle")
    _touch(tmp_path / "frontend" / "node_modules" / "pkg" / "ignored.js", "ignored")
    _touch(tmp_path / ".ims_workbench" / "metadata.sqlite", "local")
    _touch(tmp_path / "logs" / "workbench.log", "log")
    out_path = tmp_path / "dist" / "ims-workbench-local.zip"
    out_path.parent.mkdir()

    payload = build_workbench_bundle_zip(root=tmp_path, out_path=out_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["archive_created"] is True
    assert payload["writes_performed"] is True
    assert payload["execution_performed"] is False
    with zipfile.ZipFile(out_path) as archive:
        names = archive.namelist()
        metadata_by_name = {info.filename: info for info in archive.infolist()}
    assert names == payload["entries"]
    assert "python_port/__init__.py" in names
    assert "python_port/ims/api/app.py" in names
    assert "frontend/dist/index.html" in names
    assert "frontend/dist/assets/app.js" in names
    assert "scripts/workbench/check-workbench.cmd" in names
    assert "scripts/workbench/start-workbench.cmd" in names
    assert "scripts/workbench/README.md" in names
    assert "README.md" in names
    assert "docs/migration/workbench_shell.md" in names
    assert "docs/migration/workbench_packaging_plan.md" in names
    assert "docs/migration/workbench_release_checklist.md" in names
    assert "python_port/ims/__pycache__/ignored.pyc" not in names
    assert "frontend/node_modules/pkg/ignored.js" not in names
    assert ".ims_workbench/metadata.sqlite" not in names
    assert "logs/workbench.log" not in names
    assert metadata_by_name["frontend/dist/index.html"].date_time == (1980, 1, 1, 0, 0, 0)
    assert metadata_by_name["frontend/dist/index.html"].create_system == 3
    assert metadata_by_name["frontend/dist/index.html"].external_attr >> 16 == 0o644


def test_workbench_bundle_build_excludes_local_runtime_paths(tmp_path):
    _build_repo_fixture(tmp_path)
    _touch(tmp_path / ".ims_workbench" / "metadata.sqlite", "local")
    _touch(tmp_path / "logs" / "workbench.log", "log")
    _touch(tmp_path / "frontend" / "node_modules" / "pkg" / "ignored.js", "ignored")
    _touch(tmp_path / "python_port" / "ims" / "__pycache__" / "ignored.pyc", "cache")
    out_path = tmp_path / "bundle.zip"

    payload = build_workbench_bundle_zip(root=tmp_path, out_path=out_path).to_dict()

    with zipfile.ZipFile(out_path) as archive:
        names = archive.namelist()
    assert payload["status"] == "ok"
    assert ".ims_workbench/metadata.sqlite" not in names
    assert "logs/workbench.log" not in names
    assert "frontend/node_modules/pkg/ignored.js" not in names
    assert "python_port/ims/__pycache__/ignored.pyc" not in names


def test_workbench_bundle_build_preserves_external_frontend_paths(tmp_path):
    repo_root = tmp_path / "repo"
    external_dist = tmp_path / "external dist"
    _build_repo_fixture(repo_root, include_frontend=False)
    _touch(external_dist / "assets" / "app.js", "asset")
    _touch(external_dist / "nested" / "app.js", "nested")
    out_path = tmp_path / "bundle.zip"

    payload = build_workbench_bundle_zip(root=repo_root, frontend_dist=external_dist, out_path=out_path).to_dict()

    with zipfile.ZipFile(out_path) as archive:
        names = archive.namelist()
    assert payload["status"] == "ok"
    assert "frontend_dist/assets/app.js" in names
    assert "frontend_dist/nested/app.js" in names
    assert len(names) == len(set(names))


def test_workbench_bundle_build_does_not_write_on_plan_error(tmp_path):
    _build_repo_fixture(tmp_path, include_frontend=False)
    out_path = tmp_path / "bundle.zip"

    payload = build_workbench_bundle_zip(root=tmp_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "frontend_dist_missing" in issue_codes
    assert payload["archive_created"] is False
    assert payload["writes_performed"] is False
    assert not out_path.exists()


def test_workbench_bundle_build_rejects_missing_output_parent(tmp_path):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "missing" / "bundle.zip"

    payload = build_workbench_bundle_zip(root=tmp_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "out_parent_missing" in issue_codes
    assert not out_path.exists()


def test_workbench_bundle_build_rejects_output_inside_excluded_path(tmp_path):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "logs" / "bundle.zip"
    out_path.parent.mkdir()

    payload = build_workbench_bundle_zip(root=tmp_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "out_path_excluded" in issue_codes
    assert not out_path.exists()


def test_workbench_bundle_build_rejects_output_inside_included_frontend_dist(tmp_path):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "frontend" / "dist" / "workbench.zip"

    payload = build_workbench_bundle_zip(root=tmp_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "out_path_inside_included_source" in issue_codes
    assert not out_path.exists()


def test_workbench_bundle_build_rejects_output_inside_frontend_dist_with_only_nested_files(tmp_path):
    _build_repo_fixture(tmp_path, include_frontend=False)
    _touch(tmp_path / "frontend" / "dist" / "assets" / "app.js", "bundle")
    out_path = tmp_path / "frontend" / "dist" / "workbench.zip"

    payload = build_workbench_bundle_zip(root=tmp_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "out_path_inside_included_source" in issue_codes
    assert not out_path.exists()


def test_workbench_bundle_build_rejects_output_inside_python_port(tmp_path):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "python_port" / "workbench.zip"

    payload = build_workbench_bundle_zip(root=tmp_path, out_path=out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "out_path_inside_included_source" in issue_codes
    assert not out_path.exists()


def test_workbench_bundle_build_uses_stable_zip_entry_metadata(tmp_path):
    _build_repo_fixture(tmp_path)
    source = tmp_path / "frontend" / "dist" / "index.html"
    first_out = tmp_path / "first.zip"
    second_out = tmp_path / "second.zip"

    os.utime(source, (1_700_000_000, 1_700_000_000))
    first_payload = build_workbench_bundle_zip(root=tmp_path, out_path=first_out).to_dict()
    os.utime(source, (1_800_000_000, 1_800_000_000))
    second_payload = build_workbench_bundle_zip(root=tmp_path, out_path=second_out).to_dict()

    assert first_payload["status"] == "ok"
    assert second_payload["status"] == "ok"
    assert first_payload["zip_sha256"] == second_payload["zip_sha256"]
    with zipfile.ZipFile(first_out) as archive:
        info = archive.getinfo("frontend/dist/index.html")
    assert info.date_time == (1980, 1, 1, 0, 0, 0)
    assert info.create_system == 3
    assert info.external_attr >> 16 == 0o644


def test_workbench_bundle_build_cli_requires_out(tmp_path, capsys):
    _build_repo_fixture(tmp_path)

    with pytest.raises(SystemExit):
        main(["--root", str(tmp_path)])

    assert capsys.readouterr().out == ""


def test_workbench_bundle_build_cli_prints_stable_json(tmp_path, capsys):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "bundle.zip"

    exit_code = main(["--root", str(tmp_path), "--frontend-dist", "frontend/dist", "--out", str(out_path)])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_bundle_build"
    assert payload["archive_created"] is True


def test_workbench_bundle_build_module_entrypoint_prints_json(tmp_path):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "bundle.zip"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.workbench_bundle_build",
            "--root",
            str(tmp_path),
            "--frontend-dist",
            "frontend/dist",
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
    assert payload["mode"] == "workbench_bundle_build"


def test_workbench_bundle_build_public_types_importable():
    assert WorkbenchBundleBuildIssue is not None
    assert WorkbenchBundleBuildResult is not None


def _build_repo_fixture(tmp_path: Path, *, include_frontend: bool = True) -> None:
    _touch(tmp_path / "python_port" / "__init__.py")
    _touch(tmp_path / "scripts" / "workbench" / "check-workbench.cmd", "check")
    _touch(tmp_path / "scripts" / "workbench" / "start-workbench.cmd", "start")
    _touch(tmp_path / "scripts" / "workbench" / "README.md", "scripts")
    _touch(tmp_path / "README.md", "readme")
    _touch(tmp_path / "docs" / "migration" / "workbench_shell.md", "workbench doc")
    _touch(tmp_path / "docs" / "migration" / "workbench_packaging_plan.md", "packaging plan")
    _touch(tmp_path / "docs" / "migration" / "workbench_release_checklist.md", "release checklist")
    if include_frontend:
        _touch(tmp_path / "frontend" / "dist" / "index.html", "<html></html>")


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
