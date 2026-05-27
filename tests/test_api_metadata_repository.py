from dataclasses import replace

import pytest

from ims.api.metadata import RUNS, SCENARIOS, list_run_metadata, list_scenario_metadata
from ims.api.metadata_repository import (
    MetadataValidationError,
    WorkbenchMetadataRepository,
    build_seeded_metadata_repository,
    connect_metadata_db,
    initialize_metadata_schema,
    seed_metadata,
)


def test_seeded_sqlite_repository_matches_metadata_dto_boundary(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")

    assert repository.list_scenarios() == list_scenario_metadata()
    assert repository.list_runs() == list_run_metadata()


def test_sqlite_schema_can_be_seeded_explicitly(tmp_path):
    connection = connect_metadata_db(tmp_path / "workbench.sqlite")
    initialize_metadata_schema(connection)
    seed_metadata(connection)
    repository = WorkbenchMetadataRepository(connection)

    scenarios = repository.list_scenarios()
    runs = repository.list_runs()

    assert scenarios["schema_version"] == "ims.workbench.metadata.v1"
    assert scenarios["items"][0]["source"]["path"] == "tests/fixtures"
    assert runs["items"][0]["execution_enabled"] is False
    assert runs["items"][1]["period_window"] == "keine Simulation"


def test_repository_reads_single_scenario_and_run_by_id(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")

    scenario = repository.get_scenario("agrsich-reference-window")
    run = repository.get_run("baseline-python-tests")

    assert scenario is not None
    assert scenario["display_name"] == "Agrsich Referenzfenster"
    assert run is not None
    assert run["scenario_id"] == "agrsich-reference-window"
    assert run["execution_enabled"] is False


def test_repository_returns_none_for_missing_metadata_ids(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")

    assert repository.get_scenario("missing-scenario") is None
    assert repository.get_run("missing-run") is None


def test_repository_creates_parent_directory_for_local_db(tmp_path):
    db_path = tmp_path / "nested" / "metadata.sqlite"

    repository = build_seeded_metadata_repository(db_path)

    assert db_path.is_file()
    assert repository.list_runs()["items"][0]["validation"]["scope"] == "560 Tests"


def test_seed_metadata_does_not_overwrite_existing_local_rows(tmp_path):
    connection = connect_metadata_db(tmp_path / "metadata.sqlite")
    initialize_metadata_schema(connection)
    seed_metadata(connection)
    repository = WorkbenchMetadataRepository(connection)

    edited = replace(SCENARIOS[0], display_name="Lokale Bearbeitung")
    repository.upsert_scenario(edited)
    seed_metadata(connection)

    scenarios = repository.list_scenarios()["items"]
    assert scenarios[0]["id"] == "agrsich-reference-window"
    assert scenarios[0]["display_name"] == "Lokale Bearbeitung"


def test_repository_upsert_run_keeps_execution_control_disabled(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    unsafe_run = replace(RUNS[0], execution_enabled=True)

    with pytest.raises(MetadataValidationError, match="execution_enabled"):
        repository.upsert_run(unsafe_run)


def test_repository_rejects_empty_metadata_fields(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    invalid_scenario = replace(SCENARIOS[0], display_name=" ")

    with pytest.raises(MetadataValidationError, match="display_name"):
        repository.upsert_scenario(invalid_scenario)
