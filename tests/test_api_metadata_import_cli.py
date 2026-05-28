import json
import sqlite3
from pathlib import Path

import pytest

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import_cli import (
    check_metadata_import,
    export_metadata_import_bundle,
    export_metadata_import_bundle_to_file,
    export_metadata_snapshot,
    import_metadata_to_db,
    main,
    preview_metadata_import,
)
from ims.api.metadata_repository import (
    build_seeded_metadata_repository,
    initialize_metadata_schema,
    seed_metadata,
)


def test_metadata_import_cli_check_validates_without_writing(tmp_path):
    import_path = tmp_path / "metadata_import.json"
    db_path = tmp_path / "metadata.sqlite"
    import_path.write_text(json.dumps(_valid_import_payload()), encoding="utf-8")

    result = check_metadata_import(import_path)

    assert result.mode == "check"
    assert result.scenario_count == 1
    assert result.run_count == 1
    assert result.scenario_ids == ("local-imported-scenario",)
    assert result.run_ids == ("local-imported-run",)
    assert not db_path.exists()


def test_metadata_import_cli_preview_reports_summary_without_writing(tmp_path):
    import_path = tmp_path / "metadata_import.json"
    db_path = tmp_path / "metadata.sqlite"
    import_path.write_text(json.dumps(_valid_import_payload()), encoding="utf-8")

    result = preview_metadata_import(import_path)

    assert result.mode == "preview"
    assert result.scenario_count == 1
    assert result.run_count == 1
    assert result.scenario_ids == ("local-imported-scenario",)
    assert result.run_ids == ("local-imported-run",)
    assert result.existing_scenario_ids == ()
    assert result.existing_run_ids == ()
    assert result.new_scenario_ids == ("local-imported-scenario",)
    assert result.new_run_ids == ("local-imported-run",)
    assert result.runs_with_missing_scenario == ()
    assert result.runs_with_execution_enabled == ()
    assert result.writes_performed is False
    assert not db_path.exists()


def test_metadata_import_cli_preview_reports_existing_seed_ids(tmp_path):
    import_path = tmp_path / "metadata_import.json"
    payload = _valid_import_payload()
    payload["scenarios"][0]["id"] = "agrsich-reference-window"
    payload["runs"][0]["id"] = "baseline-python-tests"
    payload["runs"][0]["scenario_id"] = "agrsich-reference-window"
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    result = preview_metadata_import(import_path)

    assert result.existing_scenario_ids == ("agrsich-reference-window",)
    assert result.existing_run_ids == ("baseline-python-tests",)
    assert result.new_scenario_ids == ()
    assert result.new_run_ids == ()


def test_metadata_import_cli_reports_invalid_format(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    payload = _valid_import_payload()
    del payload["scenarios"][0]["display_name"]
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["check", str(import_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "display_name" in output["message"]


def test_metadata_import_cli_preview_reports_invalid_format(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    payload = _valid_import_payload()
    del payload["scenarios"][0]["display_name"]
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["preview", str(import_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "display_name" in output["message"]


def test_metadata_import_cli_check_rejects_unknown_run_scenario_reference(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    payload = _valid_import_payload()
    payload["runs"][0]["scenario_id"] = "missing-scenario"
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["check", str(import_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "unknown scenario_id" in output["message"]


def test_metadata_import_cli_preview_rejects_unknown_run_scenario_reference(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    payload = _valid_import_payload()
    payload["runs"][0]["scenario_id"] = "missing-scenario"
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["preview", str(import_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "unknown scenario_id" in output["message"]


def test_metadata_import_cli_preview_keeps_execution_enabled_forbidden(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    payload = _valid_import_payload()
    payload["runs"][0]["execution_enabled"] = True
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["preview", str(import_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "execution_enabled" in output["message"]


def test_metadata_import_cli_preview_prints_stable_json(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    import_path.write_text(json.dumps(_valid_import_payload()), encoding="utf-8")

    exit_code = main(["preview", str(import_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "ok"
    assert output["mode"] == "preview"
    assert output["new_scenario_ids"] == ["local-imported-scenario"]
    assert output["new_run_ids"] == ["local-imported-run"]
    assert output["runs_with_missing_scenario"] == []
    assert output["runs_with_execution_enabled"] == []
    assert output["writes_performed"] is False


def test_metadata_import_cli_snapshot_reads_seeded_memory_without_writing(tmp_path):
    db_path = tmp_path / "metadata.sqlite"

    result = export_metadata_snapshot()
    payload = result.to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "snapshot"
    assert payload["source"]["storage_kind"] == "memory"
    assert payload["scenarios"]["items"][0]["id"] == "agrsich-reference-window"
    assert payload["runs"]["items"][0]["id"] == "baseline-python-tests"
    assert payload["consistency"]["status"] == "ok"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not db_path.exists()


def test_metadata_import_cli_snapshot_reads_explicit_sqlite_file(tmp_path):
    db_path = tmp_path / "workbench.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    assert repository.get_scenario("agrsich-reference-window") is not None

    result = export_metadata_snapshot(db_path)
    payload = result.to_dict()

    assert payload["source"]["storage_kind"] == "sqlite"
    assert payload["source"]["path"] == str(db_path.resolve())
    assert payload["scenarios"]["items"][0]["id"] == "agrsich-reference-window"
    assert payload["runs"]["items"][0]["execution_enabled"] is False
    assert payload["consistency"]["issue_count"] == 0


def test_metadata_import_cli_snapshot_reads_live_wal_data_from_open_writer(tmp_path):
    db_path = tmp_path / "workbench.sqlite"
    wal_path = Path(f"{db_path}-wal")

    connection = _create_seeded_wal_database_with_open_writer(db_path)
    try:
        assert wal_path.exists()

        result = export_metadata_snapshot(db_path)
    finally:
        connection.close()

    payload = result.to_dict()
    assert payload["status"] == "ok"
    assert payload["scenarios"]["items"][0]["id"] == "agrsich-reference-window"
    assert payload["runs"]["items"][0]["id"] == "baseline-python-tests"
    assert payload["writes_performed"] is False
    assert db_path.exists()


def test_metadata_import_cli_snapshot_rejects_missing_explicit_db(tmp_path, capsys):
    db_path = tmp_path / "missing.sqlite"

    exit_code = main(["snapshot", "--db", str(db_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "does not exist" in output["message"]
    assert not db_path.exists()


def test_metadata_import_cli_snapshot_reports_unreadable_explicit_db(tmp_path, capsys):
    db_path = tmp_path / "broken.sqlite"
    db_path.write_text("not sqlite", encoding="utf-8")

    exit_code = main(["snapshot", "--db", str(db_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "not readable" in output["message"]


def test_metadata_import_cli_snapshot_prints_stable_json(capsys):
    exit_code = main(["snapshot"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "ok"
    assert output["mode"] == "snapshot"
    assert output["source"]["storage_kind"] == "memory"
    assert output["consistency"]["status"] == "ok"
    assert output["writes_performed"] is False
    assert output["execution_performed"] is False


def test_metadata_import_cli_export_reads_seeded_memory_without_writing(tmp_path):
    db_path = tmp_path / "metadata.sqlite"

    payload = export_metadata_import_bundle()

    assert payload["schema_version"] == METADATA_SCHEMA_VERSION
    assert payload["scenarios"][0]["id"] == "agrsich-reference-window"
    assert payload["runs"][0]["id"] == "baseline-python-tests"
    assert payload["runs"][0]["execution_enabled"] is False
    assert not db_path.exists()


def test_metadata_import_cli_export_prints_import_bundle_to_stdout(capsys):
    exit_code = main(["export"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["schema_version"] == METADATA_SCHEMA_VERSION
    assert "status" not in output
    assert output["scenarios"][0]["id"] == "agrsich-reference-window"
    assert output["runs"][0]["execution_enabled"] is False


def test_metadata_import_cli_export_reads_explicit_sqlite_file(tmp_path):
    db_path = tmp_path / "workbench.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    assert repository.get_run("baseline-python-tests") is not None

    payload = export_metadata_import_bundle(db_path)

    assert payload["schema_version"] == METADATA_SCHEMA_VERSION
    assert payload["scenarios"][0]["id"] == "agrsich-reference-window"
    assert payload["runs"][0]["id"] == "baseline-python-tests"


def test_metadata_import_cli_export_writes_only_to_explicit_out_path(tmp_path):
    out_path = tmp_path / "metadata_export.json"
    db_path = tmp_path / "metadata.sqlite"

    result = export_metadata_import_bundle_to_file(out_path)
    output = json.loads(out_path.read_text(encoding="utf-8"))

    assert result.mode == "export"
    assert result.scenario_count == 2
    assert result.run_count == 2
    assert result.out_path == str(out_path.resolve())
    assert result.writes_performed is True
    assert result.execution_performed is False
    assert output["schema_version"] == METADATA_SCHEMA_VERSION
    assert output["runs"][0]["execution_enabled"] is False
    assert not db_path.exists()


def test_metadata_import_cli_export_prints_status_when_out_is_explicit(tmp_path, capsys):
    out_path = tmp_path / "metadata_export.json"

    exit_code = main(["export", "--out", str(out_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "ok"
    assert output["mode"] == "export"
    assert output["out_path"] == str(out_path.resolve())
    assert output["writes_performed"] is True
    assert out_path.exists()


def test_metadata_import_cli_export_rejects_missing_explicit_db(tmp_path, capsys):
    db_path = tmp_path / "missing.sqlite"

    exit_code = main(["export", "--db", str(db_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "does not exist" in output["message"]
    assert not db_path.exists()


def test_metadata_import_cli_import_requires_explicit_db_path(tmp_path):
    import_path = tmp_path / "metadata_import.json"
    import_path.write_text(json.dumps(_valid_import_payload()), encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        main(["import", str(import_path)])

    assert exc.value.code == 2
    assert not (tmp_path / "metadata.sqlite").exists()


def test_metadata_import_cli_import_writes_to_explicit_db_path(tmp_path):
    import_path = tmp_path / "metadata_import.json"
    db_path = tmp_path / "workbench.sqlite"
    import_path.write_text(json.dumps(_valid_import_payload()), encoding="utf-8")

    result = import_metadata_to_db(import_path, db_path)

    repository = build_seeded_metadata_repository(db_path)
    imported_scenario = repository.get_scenario("local-imported-scenario")
    imported_run = repository.get_run("local-imported-run")
    assert result.mode == "import"
    assert result.db_path == str(db_path)
    assert db_path.exists()
    assert imported_scenario is not None
    assert imported_scenario["display_name"] == "Lokal importiertes Szenario"
    assert imported_run is not None
    assert imported_run["execution_enabled"] is False


def test_metadata_import_cli_keeps_execution_enabled_forbidden(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    db_path = tmp_path / "workbench.sqlite"
    payload = _valid_import_payload()
    payload["runs"][0]["execution_enabled"] = True
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["import", str(import_path), "--db", str(db_path)])

    repository = build_seeded_metadata_repository(db_path)
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "execution_enabled" in output["message"]
    assert repository.get_scenario("local-imported-scenario") is None
    assert repository.get_run("local-imported-run") is None


def _valid_import_payload():
    return {
        "schema_version": METADATA_SCHEMA_VERSION,
        "scenarios": [
            {
                "id": "local-imported-scenario",
                "display_name": "Lokal importiertes Szenario",
                "status": "draft",
                "domain_scope": "Metadaten",
                "source": {
                    "kind": "fixture",
                    "label": "Lokale Importdatei",
                    "path": "local/metadata.json",
                },
                "validation": {
                    "status": "planned",
                    "scope": "keine Fachvalidierung",
                    "claim": "Importiert nur Workbench-Metadaten.",
                },
                "updated_at": "2026-05-27T00:00:00Z",
                "notes": "Lokaler Metadatenimport ohne Simulationssteuerung.",
            }
        ],
        "runs": [
            {
                "id": "local-imported-run",
                "display_name": "Importierter Metadatenlauf",
                "scenario_id": "local-imported-scenario",
                "status": "planned",
                "source": {
                    "kind": "fixture",
                    "label": "Lokale Importdatei",
                    "path": "local/metadata.json",
                },
                "validation": {
                    "status": "planned",
                    "scope": "keine Simulation",
                    "claim": "Beschreibender Run-Metadatensatz.",
                },
                "period_window": "keine Simulation",
                "execution_enabled": False,
                "updated_at": "2026-05-27T00:00:00Z",
            }
        ],
    }


def _create_seeded_wal_database_with_open_writer(db_path):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL").fetchone()
    initialize_metadata_schema(connection)
    seed_metadata(connection)
    connection.commit()
    return connection
