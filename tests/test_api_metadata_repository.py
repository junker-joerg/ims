from ims.api.metadata import list_run_metadata, list_scenario_metadata
from ims.api.metadata_repository import (
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


def test_repository_creates_parent_directory_for_local_db(tmp_path):
    db_path = tmp_path / "nested" / "metadata.sqlite"

    repository = build_seeded_metadata_repository(db_path)

    assert db_path.is_file()
    assert repository.list_runs()["items"][0]["validation"]["scope"] == "548 Tests"
