from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from ims.api.metadata import (
    METADATA_GENERATED_AT,
    METADATA_SCHEMA_VERSION,
    RUNS,
    SCENARIOS,
    RunMetadata,
    ScenarioMetadata,
)


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS scenarios (
        id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        status TEXT NOT NULL,
        domain_scope TEXT NOT NULL,
        source_kind TEXT NOT NULL,
        source_label TEXT NOT NULL,
        source_path TEXT,
        validation_status TEXT NOT NULL,
        validation_scope TEXT NOT NULL,
        validation_claim TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        notes TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        scenario_id TEXT NOT NULL,
        status TEXT NOT NULL,
        source_kind TEXT NOT NULL,
        source_label TEXT NOT NULL,
        source_path TEXT,
        validation_status TEXT NOT NULL,
        validation_scope TEXT NOT NULL,
        validation_claim TEXT NOT NULL,
        period_window TEXT NOT NULL,
        execution_enabled INTEGER NOT NULL CHECK (execution_enabled IN (0, 1)),
        updated_at TEXT NOT NULL,
        FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
    )
    """,
)


class MetadataValidationError(ValueError):
    pass


def connect_metadata_db(path: Path | str) -> sqlite3.Connection:
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_metadata_schema(connection: sqlite3.Connection) -> None:
    with connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)


def seed_metadata(
    connection: sqlite3.Connection,
    *,
    scenarios: Iterable[ScenarioMetadata] = SCENARIOS,
    runs: Iterable[RunMetadata] = RUNS,
) -> None:
    with connection:
        for scenario in scenarios:
            connection.execute(
                """
                INSERT OR IGNORE INTO scenarios (
                    id,
                    display_name,
                    status,
                    domain_scope,
                    source_kind,
                    source_label,
                    source_path,
                    validation_status,
                    validation_scope,
                    validation_claim,
                    updated_at,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scenario.id,
                    scenario.display_name,
                    scenario.status,
                    scenario.domain_scope,
                    scenario.source.kind,
                    scenario.source.label,
                    scenario.source.path,
                    scenario.validation.status,
                    scenario.validation.scope,
                    scenario.validation.claim,
                    scenario.updated_at,
                    scenario.notes,
                ),
            )
        for run in runs:
            connection.execute(
                """
                INSERT OR IGNORE INTO runs (
                    id,
                    display_name,
                    scenario_id,
                    status,
                    source_kind,
                    source_label,
                    source_path,
                    validation_status,
                    validation_scope,
                    validation_claim,
                    period_window,
                    execution_enabled,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.display_name,
                    run.scenario_id,
                    run.status,
                    run.source.kind,
                    run.source.label,
                    run.source.path,
                    run.validation.status,
                    run.validation.scope,
                    run.validation.claim,
                    run.period_window,
                    int(run.execution_enabled),
                    run.updated_at,
                ),
            )


class WorkbenchMetadataRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def metadata_source(self) -> dict[str, object]:
        return metadata_source_payload(_metadata_connection_path(self._connection))

    def list_scenarios(self) -> dict[str, object]:
        rows = self._connection.execute(
            """
            SELECT
                id,
                display_name,
                status,
                domain_scope,
                source_kind,
                source_label,
                source_path,
                validation_status,
                validation_scope,
                validation_claim,
                updated_at,
                notes
            FROM scenarios
            ORDER BY id
            """
        ).fetchall()
        return {
            "schema_version": METADATA_SCHEMA_VERSION,
            "generated_at": METADATA_GENERATED_AT,
            "items": [_scenario_row_to_dict(row) for row in rows],
        }

    def get_scenario(self, scenario_id: str) -> dict[str, object] | None:
        row = self._connection.execute(
            """
            SELECT
                id,
                display_name,
                status,
                domain_scope,
                source_kind,
                source_label,
                source_path,
                validation_status,
                validation_scope,
                validation_claim,
                updated_at,
                notes
            FROM scenarios
            WHERE id = ?
            """,
            (scenario_id,),
        ).fetchone()
        if row is None:
            return None
        return _scenario_row_to_dict(row)

    def list_runs(self) -> dict[str, object]:
        rows = self._connection.execute(
            """
            SELECT
                id,
                display_name,
                scenario_id,
                status,
                source_kind,
                source_label,
                source_path,
                validation_status,
                validation_scope,
                validation_claim,
                period_window,
                execution_enabled,
                updated_at
            FROM runs
            ORDER BY id
            """
        ).fetchall()
        return {
            "schema_version": METADATA_SCHEMA_VERSION,
            "generated_at": METADATA_GENERATED_AT,
            "items": [_run_row_to_dict(row) for row in rows],
        }

    def get_run(self, run_id: str) -> dict[str, object] | None:
        row = self._connection.execute(
            """
            SELECT
                id,
                display_name,
                scenario_id,
                status,
                source_kind,
                source_label,
                source_path,
                validation_status,
                validation_scope,
                validation_claim,
                period_window,
                execution_enabled,
                updated_at
            FROM runs
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return _run_row_to_dict(row)

    def validate_scenario(self, scenario: ScenarioMetadata) -> None:
        _validate_scenario_metadata(scenario)

    def validate_run(self, run: RunMetadata) -> None:
        _validate_run_metadata(run)

    def upsert_scenario(self, scenario: ScenarioMetadata) -> None:
        self.validate_scenario(scenario)
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO scenarios (
                    id,
                    display_name,
                    status,
                    domain_scope,
                    source_kind,
                    source_label,
                    source_path,
                    validation_status,
                    validation_scope,
                    validation_claim,
                    updated_at,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    display_name = excluded.display_name,
                    status = excluded.status,
                    domain_scope = excluded.domain_scope,
                    source_kind = excluded.source_kind,
                    source_label = excluded.source_label,
                    source_path = excluded.source_path,
                    validation_status = excluded.validation_status,
                    validation_scope = excluded.validation_scope,
                    validation_claim = excluded.validation_claim,
                    updated_at = excluded.updated_at,
                    notes = excluded.notes
                """,
                _scenario_values(scenario),
            )

    def upsert_run(self, run: RunMetadata) -> None:
        self.validate_run(run)
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO runs (
                    id,
                    display_name,
                    scenario_id,
                    status,
                    source_kind,
                    source_label,
                    source_path,
                    validation_status,
                    validation_scope,
                    validation_claim,
                    period_window,
                    execution_enabled,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    display_name = excluded.display_name,
                    scenario_id = excluded.scenario_id,
                    status = excluded.status,
                    source_kind = excluded.source_kind,
                    source_label = excluded.source_label,
                    source_path = excluded.source_path,
                    validation_status = excluded.validation_status,
                    validation_scope = excluded.validation_scope,
                    validation_claim = excluded.validation_claim,
                    period_window = excluded.period_window,
                    execution_enabled = excluded.execution_enabled,
                    updated_at = excluded.updated_at
                """,
                _run_values(run),
            )


def build_seeded_metadata_repository(path: Path | str = ":memory:") -> WorkbenchMetadataRepository:
    connection = connect_metadata_db(path)
    initialize_metadata_schema(connection)
    seed_metadata(connection)
    return WorkbenchMetadataRepository(connection)


class LazyWorkbenchMetadataRepository:
    def __init__(self, path: Path | str) -> None:
        self._path = path
        self._repository: WorkbenchMetadataRepository | None = None

    def _get_repository(self) -> WorkbenchMetadataRepository:
        if self._repository is None:
            self._repository = build_seeded_metadata_repository(self._path)
        return self._repository

    def metadata_source(self) -> dict[str, object]:
        return metadata_source_payload(self._path)

    def list_scenarios(self) -> dict[str, object]:
        return self._get_repository().list_scenarios()

    def get_scenario(self, scenario_id: str) -> dict[str, object] | None:
        return self._get_repository().get_scenario(scenario_id)

    def list_runs(self) -> dict[str, object]:
        return self._get_repository().list_runs()

    def get_run(self, run_id: str) -> dict[str, object] | None:
        return self._get_repository().get_run(run_id)


def _scenario_row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": row["id"],
        "display_name": row["display_name"],
        "status": row["status"],
        "domain_scope": row["domain_scope"],
        "source": {
            "kind": row["source_kind"],
            "label": row["source_label"],
            "path": row["source_path"],
        },
        "validation": {
            "status": row["validation_status"],
            "scope": row["validation_scope"],
            "claim": row["validation_claim"],
        },
        "updated_at": row["updated_at"],
        "notes": row["notes"],
    }


def _run_row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": row["id"],
        "display_name": row["display_name"],
        "scenario_id": row["scenario_id"],
        "status": row["status"],
        "source": {
            "kind": row["source_kind"],
            "label": row["source_label"],
            "path": row["source_path"],
        },
        "validation": {
            "status": row["validation_status"],
            "scope": row["validation_scope"],
            "claim": row["validation_claim"],
        },
        "period_window": row["period_window"],
        "execution_enabled": bool(row["execution_enabled"]),
        "updated_at": row["updated_at"],
    }


def seeded_metadata_as_dicts() -> tuple[dict[str, object], dict[str, object]]:
    repository = build_seeded_metadata_repository()
    return repository.list_scenarios(), repository.list_runs()


def _scenario_values(scenario: ScenarioMetadata) -> tuple[object, ...]:
    return (
        scenario.id,
        scenario.display_name,
        scenario.status,
        scenario.domain_scope,
        scenario.source.kind,
        scenario.source.label,
        scenario.source.path,
        scenario.validation.status,
        scenario.validation.scope,
        scenario.validation.claim,
        scenario.updated_at,
        scenario.notes,
    )


def _run_values(run: RunMetadata) -> tuple[object, ...]:
    return (
        run.id,
        run.display_name,
        run.scenario_id,
        run.status,
        run.source.kind,
        run.source.label,
        run.source.path,
        run.validation.status,
        run.validation.scope,
        run.validation.claim,
        run.period_window,
        int(run.execution_enabled),
        run.updated_at,
    )


def metadata_source_payload(path: Path | str, *, injected: bool = False) -> dict[str, object]:
    configured = path != ":memory:"
    resolved_path = Path(path).expanduser().resolve() if configured else None
    payload: dict[str, object] = {
        "schema_version": METADATA_SCHEMA_VERSION,
        "storage_kind": "sqlite" if configured else "memory",
        "configured": configured,
        "injected": injected,
        "writes_enabled": False,
        "execution_enabled": False,
    }
    if configured:
        payload["path"] = str(resolved_path)
    return payload


def _metadata_connection_path(connection: sqlite3.Connection) -> Path | str:
    rows = connection.execute("PRAGMA database_list").fetchall()
    for row in rows:
        if row["name"] == "main":
            file_path = row["file"]
            if file_path:
                return Path(file_path).resolve()
    return ":memory:"


def _validate_scenario_metadata(scenario: ScenarioMetadata) -> None:
    _require_text(scenario.id, "scenario.id")
    _require_text(scenario.display_name, "scenario.display_name")
    _require_text(scenario.domain_scope, "scenario.domain_scope")
    _require_text(scenario.updated_at, "scenario.updated_at")
    _require_text(scenario.source.label, "scenario.source.label")
    _require_text(scenario.validation.scope, "scenario.validation.scope")
    _require_text(scenario.validation.claim, "scenario.validation.claim")


def _validate_run_metadata(run: RunMetadata) -> None:
    _require_text(run.id, "run.id")
    _require_text(run.display_name, "run.display_name")
    _require_text(run.scenario_id, "run.scenario_id")
    _require_text(run.period_window, "run.period_window")
    _require_text(run.updated_at, "run.updated_at")
    _require_text(run.source.label, "run.source.label")
    _require_text(run.validation.scope, "run.validation.scope")
    _require_text(run.validation.claim, "run.validation.claim")
    if run.execution_enabled:
        raise MetadataValidationError("run.execution_enabled must remain false until run control exists")


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise MetadataValidationError(f"{field_name} must not be empty")
