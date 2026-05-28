import json

import ims.api.workbench_readiness as readiness_module
from ims.api.metadata_repository import build_seeded_metadata_repository
from ims.api.workbench_readiness import WorkbenchReadinessCheck, WorkbenchReadinessResult, build_workbench_readiness, main


def test_workbench_readiness_reports_ok_with_explicit_frontend_dist(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)

    payload = build_workbench_readiness(frontend_dist=frontend_dist).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_readiness"
    assert payload["backend_ready"] is True
    assert payload["frontend_ready"] is True
    assert payload["metadata_ready"] is True
    assert payload["cli_ready"] is True
    assert payload["run_control_ready"] is True
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["issues"] == []
    assert [check["name"] for check in payload["checks"]] == [
        "backend",
        "frontend",
        "metadata",
        "cli",
        "run_control",
    ]
    assert WorkbenchReadinessCheck is not None
    assert WorkbenchReadinessResult is not None


def test_workbench_readiness_reads_explicit_sqlite_file(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)

    payload = build_workbench_readiness(
        frontend_dist=frontend_dist,
        db_path=db_path,
        run_id="workbench-shell-preview",
    ).to_dict()

    assert payload["status"] == "ok"
    assert payload["metadata_ready"] is True
    assert payload["run_control_ready"] is True
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False


def test_workbench_readiness_reports_missing_frontend_dist_as_issue(tmp_path):
    payload = build_workbench_readiness(frontend_dist=tmp_path / "missing-dist").to_dict()

    assert payload["status"] == "warning"
    assert payload["frontend_ready"] is False
    assert any(issue["code"] == "frontend_dist_missing" for issue in payload["issues"])
    assert any(check["name"] == "frontend" and check["status"] == "warning" for check in payload["checks"])


def test_workbench_readiness_reports_unknown_run_as_issue(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)

    payload = build_workbench_readiness(frontend_dist=frontend_dist, run_id="missing-run").to_dict()

    assert payload["status"] == "warning"
    assert payload["metadata_ready"] is True
    assert payload["run_control_ready"] is False
    assert any("run metadata not found: missing-run" in issue["message"] for issue in payload["issues"])
    assert payload["execution_enabled"] is False


def test_workbench_readiness_marks_unreadable_explicit_metadata_db_not_ready(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)
    db_path = tmp_path / "metadata.sqlite"
    db_path.write_text("not a sqlite database", encoding="utf-8")

    payload = build_workbench_readiness(frontend_dist=frontend_dist, db_path=db_path).to_dict()

    assert payload["status"] == "error"
    assert payload["metadata_ready"] is False
    assert payload["run_control_ready"] is False
    assert any(issue["code"] == "run_control_preflight_failed" for issue in payload["issues"])
    assert any("metadata run-control-preflight database is not readable" in issue["message"] for issue in payload["issues"])
    assert any(check["name"] == "metadata" and check["status"] == "warning" for check in payload["checks"])
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False


def test_workbench_readiness_marks_raw_sqlite_open_failure_as_metadata_not_ready(tmp_path, monkeypatch):
    frontend_dist = _frontend_dist(tmp_path)
    db_path = tmp_path / "metadata.sqlite"
    db_path.write_text("", encoding="utf-8")

    def fail_preflight(run_id, db_path=None):
        raise OSError("unable to open database file")

    monkeypatch.setattr(readiness_module, "preflight_run_control", fail_preflight)

    payload = build_workbench_readiness(frontend_dist=frontend_dist, db_path=db_path).to_dict()

    assert payload["status"] == "error"
    assert payload["metadata_ready"] is False
    assert payload["run_control_ready"] is False
    assert any(issue["message"] == "unable to open database file" for issue in payload["issues"])


def test_workbench_readiness_does_not_create_missing_explicit_db(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)
    db_path = tmp_path / "missing.sqlite"

    payload = build_workbench_readiness(frontend_dist=frontend_dist, db_path=db_path).to_dict()

    assert payload["status"] == "error"
    assert payload["metadata_ready"] is False
    assert any(issue["code"] == "metadata_db_missing" for issue in payload["issues"])
    assert any(issue["code"] == "run_control_preflight_failed" for issue in payload["issues"])
    assert db_path.exists() is False


def test_workbench_readiness_cli_prints_stable_json(tmp_path, capsys):
    frontend_dist = _frontend_dist(tmp_path)

    exit_code = main(["--frontend-dist", str(frontend_dist), "--run-id", "baseline-python-tests"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "ok"
    assert output["mode"] == "workbench_readiness"
    assert output["run_control_ready"] is True
    assert output["writes_enabled"] is False
    assert output["execution_enabled"] is False


def _frontend_dist(tmp_path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_text("<!doctype html><title>IMS Workbench</title>", encoding="utf-8")
    return dist_dir
