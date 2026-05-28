import json

from ims.api.workbench_start_plan import build_workbench_start_plan, main


def test_workbench_start_plan_reports_default_shape(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)

    payload = build_workbench_start_plan(frontend_dist=frontend_dist).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "start_plan"
    assert payload["host"] == "127.0.0.1"
    assert payload["port"] == 8000
    assert payload["frontend_dist"] == str(frontend_dist.resolve())
    assert payload["metadata_db"] is None
    assert payload["recommended_command"] == (
        "python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000"
    )
    assert "python -m ims.api.workbench_diagnostics" in payload["diagnostics_command"]
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["issues"] == []


def test_workbench_start_plan_uses_explicit_config(tmp_path):
    config_dir = tmp_path / "local-config"
    config_dir.mkdir()
    frontend_dist = _frontend_dist(config_dir)
    db_path = config_dir / ".ims_workbench" / "metadata.sqlite"
    db_path.parent.mkdir()
    db_path.write_bytes(b"sqlite placeholder")
    config_path = config_dir / "workbench.local.json"
    config_path.write_text(
        json.dumps(
            {
                "host": "127.0.0.1",
                "port": 8010,
                "frontend_dist": "dist",
                "metadata_db": ".ims_workbench/metadata.sqlite",
            }
        ),
        encoding="utf-8",
    )

    payload = build_workbench_start_plan(config_path=config_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["host"] == "127.0.0.1"
    assert payload["port"] == 8010
    assert payload["frontend_dist"] == str(frontend_dist.resolve())
    assert payload["metadata_db"] == str(db_path.resolve())
    assert "--port 8010" in payload["recommended_command"]
    assert str(db_path.resolve()) in payload["diagnostics_command"]


def test_workbench_start_plan_resolves_config_relative_paths_from_other_cwd(tmp_path, monkeypatch):
    config_dir = tmp_path / "local-config"
    config_dir.mkdir()
    frontend_dist = _frontend_dist(config_dir)
    db_path = config_dir / ".ims_workbench" / "metadata.sqlite"
    db_path.parent.mkdir()
    db_path.write_bytes(b"sqlite placeholder")
    config_path = config_dir / "workbench.local.json"
    config_path.write_text(
        json.dumps(
            {
                "frontend_dist": "dist",
                "metadata_db": ".ims_workbench/metadata.sqlite",
            }
        ),
        encoding="utf-8",
    )
    other_cwd = tmp_path / "other-cwd"
    other_cwd.mkdir()

    monkeypatch.chdir(other_cwd)

    payload = build_workbench_start_plan(config_path=config_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["frontend_dist"] == str(frontend_dist.resolve())
    assert payload["metadata_db"] == str(db_path.resolve())


def test_workbench_start_plan_does_not_create_missing_config(tmp_path):
    config_path = tmp_path / "missing.json"

    payload = build_workbench_start_plan(config_path=config_path, frontend_dist=_frontend_dist(tmp_path)).to_dict()

    assert payload["status"] == "error"
    assert any(issue["code"] == "workbench_config_invalid" for issue in payload["issues"])
    assert config_path.exists() is False


def test_workbench_start_plan_does_not_create_missing_metadata_db(tmp_path):
    frontend_dist = _frontend_dist(tmp_path)
    db_path = tmp_path / "metadata.sqlite"

    payload = build_workbench_start_plan(frontend_dist=frontend_dist, db_path=db_path).to_dict()

    assert payload["status"] == "warning"
    assert payload["metadata_db"] == str(db_path.resolve())
    assert any(issue["code"] == "metadata_db_missing" for issue in payload["issues"])
    assert db_path.exists() is False


def test_workbench_start_plan_cli_prints_stable_json(tmp_path, capsys):
    frontend_dist = _frontend_dist(tmp_path)

    exit_code = main(["--frontend-dist", str(frontend_dist)])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "start_plan"
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False


def _frontend_dist(tmp_path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_text("<!doctype html><title>IMS Workbench</title>", encoding="utf-8")
    return dist_dir
