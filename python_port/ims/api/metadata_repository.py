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
                INSERT OR REPLACE INTO scenarios (
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
                INSERT OR REPLACE INTO runs (
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


def build_seeded_metadata_repository(path: Path | str = ":memory:") -> WorkbenchMetadataRepository:
    connection = connect_metadata_db(path)
    initialize_metadata_schema(connection)
    seed_metadata(connection)
    return WorkbenchMetadataRepository(connection)


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
