import json

from ims.api.metadata_repository import build_seeded_metadata_repository
from ims.api.workbench_diagnostics import build_workbench_diagnostics, main


def test_workbench_diagnostics_reports_default_memory_source_without_writing(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)
    db_path = tmp_path / "metadata.sqlite"

    result = build_workbench_diagnostics(frontend_dist=frontend_dist)
    payload = result.to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "diagnostics"
    assert payload["api_importable"] is True
    assert payload["web_dependencies_available"] is True
    assert payload["frontend_dist_available"] is True
    assert payload["metadata_source"]["storage_kind"] == "memory"
    assert payload["metadata_source"]["configured"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["issues"] == []
    assert db_path.exists() is False


def test_workbench_diagnostics_reports_explicit_sqlite_source(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)

    payload = build_workbench_diagnostics(frontend_dist=frontend_dist, db_path=db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["metadata_source"]["storage_kind"] == "sqlite"
    assert payload["metadata_source"]["configured"] is True
    assert payload["metadata_source"]["path"] == str(db_path.resolve())
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False


def test_workbench_diagnostics_reports_missing_frontend_dist_as_issue(tmp_path):
    payload = build_workbench_diagnostics(frontend_dist=tmp_path / "missing-dist").to_dict()

    assert payload["status"] == "warning"
    assert payload["frontend_dist_available"] is False
    assert payload["issues"][0]["code"] == "frontend_dist_missing"
    assert payload["issues"][0]["severity"] == "warning"


def test_workbench_diagnostics_does_not_create_missing_explicit_db(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)
    db_path = tmp_path / "missing.sqlite"

    payload = build_workbench_diagnostics(frontend_dist=frontend_dist, db_path=db_path).to_dict()

    assert payload["status"] == "warning"
    assert payload["metadata_source"]["storage_kind"] == "sqlite"
    assert payload["metadata_source"]["path"] == str(db_path.resolve())
    assert any(issue["code"] == "metadata_db_missing" for issue in payload["issues"])
    assert db_path.exists() is False


def test_workbench_diagnostics_cli_prints_stable_json(tmp_path, capsys):
    frontend_dist = _frontend_dist(tmp_path)

    exit_code = main(["--frontend-dist", str(frontend_dist)])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "diagnostics"
    assert payload["frontend_dist_available"] is True
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False


def _frontend_dist(tmp_path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_text("<!doctype html><title>IMS Workbench</title>", encoding="utf-8")
    return dist_dir
