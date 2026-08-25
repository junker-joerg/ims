import json
import os
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

from ims.api.workbench_bundle_build import build_workbench_bundle_zip
from ims.api.workbench_bundle_smoke import (
    WorkbenchBundleSmokeIssue,
    WorkbenchBundleSmokeResult,
    main,
    smoke_workbench_bundle_zip,
)


def test_workbench_bundle_smoke_accepts_valid_bundle_zip(tmp_path):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "dist" / "ims-workbench-local.zip"
    out_path.parent.mkdir()
    build_workbench_bundle_zip(root=tmp_path, out_path=out_path)

    payload = smoke_workbench_bundle_zip(out_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_bundle_smoke"
    assert payload["zip_path"] == str(out_path.resolve())
    assert payload["entry_count"] > 0
    assert payload["required_entries_present"] is True
    assert payload["forbidden_entries_present"] is False
    assert payload["stable_metadata"] is True
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["issues"] == []


def test_workbench_bundle_smoke_reports_missing_required_entries(tmp_path):
    zip_path = tmp_path / "bundle.zip"
    _write_zip(zip_path, {"README.md": "readme"})

    payload = smoke_workbench_bundle_zip(zip_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["required_entries_present"] is False
    assert "required_entry_missing" in issue_codes


def test_workbench_bundle_smoke_reports_forbidden_entries(tmp_path):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "dist" / "ims-workbench-local.zip"
    out_path.parent.mkdir()
    build_workbench_bundle_zip(root=tmp_path, out_path=out_path)
    with zipfile.ZipFile(out_path, mode="a", compression=zipfile.ZIP_DEFLATED) as archive:
        _write_stable_entry(archive, ".ims_workbench/metadata.sqlite", "local")

    payload = smoke_workbench_bundle_zip(out_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["forbidden_entries_present"] is True
    assert "forbidden_entry_present" in issue_codes


def test_workbench_bundle_smoke_reports_unstable_zip_metadata(tmp_path):
    _build_repo_fixture(tmp_path)
    zip_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in (
            "README.md",
            "python_port/__init__.py",
            "frontend/dist/index.html",
            "scripts/workbench/check-workbench.cmd",
            "scripts/workbench/start-workbench.cmd",
            "scripts/workbench/README.md",
            "docs/migration/workbench_shell.md",
            "docs/migration/workbench_packaging_plan.md",
        ):
            archive.writestr(name, "content")

    payload = smoke_workbench_bundle_zip(zip_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["stable_metadata"] is False
    assert "unstable_zip_entry_metadata" in issue_codes


def test_workbench_bundle_smoke_reports_corrupt_payload(tmp_path):
    zip_path = tmp_path / "bundle.zip"
    corrupt_entry = "frontend/dist/index.html"
    corrupt_payload = "frontend payload"
    _write_zip(
        zip_path,
        {
            "README.md": "readme",
            "python_port/__init__.py": "python",
            corrupt_entry: corrupt_payload,
            "scripts/workbench/check-workbench.cmd": "check",
            "scripts/workbench/start-workbench.cmd": "start",
            "scripts/workbench/README.md": "scripts",
            "docs/migration/workbench_shell.md": "workbench doc",
            "docs/migration/workbench_packaging_plan.md": "packaging plan",
        },
        compression=zipfile.ZIP_STORED,
    )
    zip_path.write_bytes(zip_path.read_bytes().replace(corrupt_payload.encode("utf-8"), b"damaged! payload", 1))

    payload = smoke_workbench_bundle_zip(zip_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}
    issue_messages = "\n".join(str(issue["message"]) for issue in payload["issues"])

    assert payload["status"] == "error"
    assert "zip_payload_corrupt" in issue_codes
    assert corrupt_entry in issue_messages


def test_workbench_bundle_smoke_reports_deflate_payload_error_as_json(tmp_path, monkeypatch, capsys):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "dist" / "ims-workbench-local.zip"
    out_path.parent.mkdir()
    build_workbench_bundle_zip(root=tmp_path, out_path=out_path)

    def raise_zlib_error(self):
        raise zlib.error("invalid distance too far back")

    monkeypatch.setattr(zipfile.ZipFile, "testzip", raise_zlib_error)

    exit_code = main(["--zip-path", str(out_path)])
    payload = json.loads(capsys.readouterr().out)
    issue_codes = {issue["code"] for issue in payload["issues"]}
    issue_messages = "\n".join(str(issue["message"]) for issue in payload["issues"])

    assert exit_code == 1
    assert payload["status"] == "error"
    assert "zip_payload_corrupt" in issue_codes
    assert "invalid distance too far back" in issue_messages


def test_workbench_bundle_smoke_reports_missing_zip(tmp_path):
    zip_path = tmp_path / "missing.zip"

    payload = smoke_workbench_bundle_zip(zip_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["entry_count"] == 0
    assert payload["writes_performed"] is False
    assert "zip_missing" in issue_codes
    assert not zip_path.exists()


def test_workbench_bundle_smoke_cli_prints_stable_json(tmp_path, capsys):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "dist" / "ims-workbench-local.zip"
    out_path.parent.mkdir()
    build_workbench_bundle_zip(root=tmp_path, out_path=out_path)

    exit_code = main(["--zip-path", str(out_path)])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_bundle_smoke"


def test_workbench_bundle_smoke_module_entrypoint_prints_json(tmp_path):
    _build_repo_fixture(tmp_path)
    out_path = tmp_path / "dist" / "ims-workbench-local.zip"
    out_path.parent.mkdir()
    build_workbench_bundle_zip(root=tmp_path, out_path=out_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.workbench_bundle_smoke",
            "--zip-path",
            str(out_path),
        ],
        capture_output=True,
        check=True,
        env=env,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_bundle_smoke"


def test_workbench_bundle_smoke_public_types_importable():
    assert WorkbenchBundleSmokeIssue is not None
    assert WorkbenchBundleSmokeResult is not None


def _build_repo_fixture(tmp_path: Path) -> None:
    _touch(tmp_path / "python_port" / "__init__.py")
    _touch(tmp_path / "frontend" / "dist" / "index.html", "<html></html>")
    _touch(tmp_path / "scripts" / "workbench" / "check-workbench.cmd", "check")
    _touch(tmp_path / "scripts" / "workbench" / "start-workbench.cmd", "start")
    _touch(tmp_path / "scripts" / "workbench" / "README.md", "scripts")
    _touch(tmp_path / "README.md", "readme")
    _touch(tmp_path / "docs" / "migration" / "workbench_shell.md", "workbench doc")
    _touch(tmp_path / "docs" / "migration" / "workbench_packaging_plan.md", "packaging plan")
    _touch(tmp_path / "docs" / "migration" / "workbench_release_checklist.md", "release checklist")


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_zip(path: Path, entries: dict[str, str], *, compression: int = zipfile.ZIP_DEFLATED) -> None:
    with zipfile.ZipFile(path, mode="w", compression=compression) as archive:
        for name, content in entries.items():
            _write_stable_entry(archive, name, content, compression=compression)


def _write_stable_entry(
    archive: zipfile.ZipFile,
    name: str,
    content: str,
    *,
    compression: int = zipfile.ZIP_DEFLATED,
) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = compression
    info.create_system = 3
    info.external_attr = 0o644 << 16
    archive.writestr(info, content)
