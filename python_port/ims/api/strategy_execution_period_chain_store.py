from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import Mapping

from ims.api.metadata_repository import connect_metadata_db
from ims.api.sqlite_readonly import readonly_sqlite_uri
from ims.api.strategy_execution_period_chain_build import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION,
    build_strategy_execution_period_chain,
    calculate_strategy_execution_period_chain_content_digest,
    strategy_execution_period_chain_build_provenance_payload,
    strategy_execution_period_chain_execution_boundaries_payload,
    strategy_execution_period_chain_id_from_digest,
)
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)
from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_SECTIONS,
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)
from ims.strategies.execution_period_chain_validation import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
    validate_strategy_execution_period_chain_input,
)


STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION = (
    "ims.strategy-execution-period-chain-store.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION = (
    "ims.strategy-execution-period-chain-store-request.v1"
)

STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_SCHEMA = """
CREATE TABLE IF NOT EXISTS strategy_execution_period_chains (
    chain_id TEXT PRIMARY KEY,
    chain_schema_version TEXT NOT NULL,
    first_period INTEGER NOT NULL CHECK (first_period = 1),
    last_period INTEGER NOT NULL CHECK (last_period >= 2 AND last_period <= 100),
    period_count INTEGER NOT NULL CHECK (period_count >= 2 AND period_count <= 100),
    run_index INTEGER NOT NULL CHECK (run_index >= 0),
    max_periods INTEGER NOT NULL CHECK (max_periods >= 2 AND max_periods <= 100),
    content_digest TEXT NOT NULL UNIQUE,
    stored_at TEXT NOT NULL,
    chain_payload_json TEXT NOT NULL
)
"""

_STORE_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "period_chain_input",
        "expected_chain_id",
        "expected_content_digest",
        "stored_at",
        "explicit_storage_release",
    }
)
_CHAIN_CONTENT_SECTION_IDS = tuple(
    definition.section_id
    for definition in STRATEGY_EXECUTION_PERIOD_CHAIN_SECTIONS
    if definition.section_id != "identity"
)
_CHAIN_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "mode",
        "base_model",
        "identity",
        *_CHAIN_CONTENT_SECTION_IDS,
    }
)
_CHAIN_IDENTITY_FIELDS = frozenset(
    {"chain_id", "content_digest", "schema_version"}
)
_CHAIN_HORIZON_FIELDS = frozenset(
    {"first_period", "last_period", "period_count", "run_index", "max_periods"}
)


class StrategyExecutionPeriodChainStoreError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainStoreRequest:
    period_chain_input: dict[str, object]
    expected_chain_id: str
    expected_content_digest: str
    stored_at: str
    explicit_storage_release: bool
    schema_version: str = STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainStoreRecord:
    chain_id: str
    content_digest: str
    first_period: int
    last_period: int
    period_count: int
    run_index: int
    max_periods: int
    stored_at: str
    period_chain: dict[str, object]
    chain_schema_version: str = STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "chain_id": self.chain_id,
            "chain_schema_version": self.chain_schema_version,
            "content_digest": self.content_digest,
            "first_period": self.first_period,
            "last_period": self.last_period,
            "period_count": self.period_count,
            "run_index": self.run_index,
            "max_periods": self.max_periods,
            "stored_at": self.stored_at,
            "period_chain": deepcopy(self.period_chain),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainStoreResult:
    mode: str
    db_path: str
    record: StrategyExecutionPeriodChainStoreRecord
    storage_release_confirmed: bool
    chain_rebuilt: bool
    pre_storage_digest_verified: bool
    post_storage_digest_verified: bool
    new_record_created: bool = False
    replayed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION,
            "request_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION
            ),
            "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
            "build_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION,
            "mode": self.mode,
            "db_path": self.db_path,
            "record": self.record.to_dict(),
            "storage_release_confirmed": self.storage_release_confirmed,
            "chain_rebuilt": self.chain_rebuilt,
            "pre_storage_digest_verified": self.pre_storage_digest_verified,
            "post_storage_digest_verified": self.post_storage_digest_verified,
            "period_chain_persisted": True,
            "new_record_created": self.new_record_created,
            "replayed": self.replayed,
            "writes_performed": self.new_record_created,
            "carryover_invocation_performed": False,
            "runner_invocation_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR140",
        }


def parse_strategy_execution_period_chain_store_request(
    value: object,
) -> StrategyExecutionPeriodChainStoreRequest:
    if not isinstance(value, dict):
        raise StrategyExecutionPeriodChainStoreError(
            "store_request_object_required",
            "Kettenspeicher-Request muss ein JSON-Objekt sein",
        )
    actual_fields = frozenset(value)
    missing = sorted(_STORE_REQUEST_FIELDS - actual_fields)
    unknown = sorted(actual_fields - _STORE_REQUEST_FIELDS)
    if missing:
        raise StrategyExecutionPeriodChainStoreError(
            "store_request_fields_missing",
            f"Kettenspeicher-Felder fehlen: {', '.join(missing)}",
        )
    if unknown:
        raise StrategyExecutionPeriodChainStoreError(
            "store_request_fields_unknown",
            f"Kettenspeicher-Felder sind nicht erlaubt: {', '.join(unknown)}",
        )
    if value["schema_version"] != STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION:
        raise StrategyExecutionPeriodChainStoreError(
            "store_request_schema_version_mismatch",
            "Kettenspeicher-Schemaversion stimmt nicht ueberein",
        )
    if value["explicit_storage_release"] is not True:
        raise StrategyExecutionPeriodChainStoreError(
            "storage_release_required",
            "Explizite Speicherfreigabe ist erforderlich",
        )
    period_chain_input = value["period_chain_input"]
    if not isinstance(period_chain_input, dict):
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_input_object_required",
            "Periodenketten-Eingang muss ein JSON-Objekt sein",
        )
    expected_digest = _required_text(
        value,
        "expected_content_digest",
        code="expected_content_digest_required",
    )
    try:
        derived_chain_id = strategy_execution_period_chain_id_from_digest(
            expected_digest
        )
    except ValueError as exc:
        raise StrategyExecutionPeriodChainStoreError(
            "expected_content_digest_invalid",
            str(exc),
        ) from exc
    expected_chain_id = _required_text(
        value,
        "expected_chain_id",
        code="expected_chain_id_required",
    )
    if expected_chain_id != derived_chain_id:
        raise StrategyExecutionPeriodChainStoreError(
            "expected_chain_identity_mismatch",
            "Erwartete Ketten-ID passt nicht zum erwarteten Digest",
        )
    stored_at = _required_text(value, "stored_at", code="stored_at_required")
    _validate_timestamp(stored_at)
    return StrategyExecutionPeriodChainStoreRequest(
        period_chain_input=deepcopy(period_chain_input),
        expected_chain_id=expected_chain_id,
        expected_content_digest=expected_digest,
        stored_at=stored_at,
        explicit_storage_release=True,
    )


def persist_strategy_execution_period_chain(
    value: object,
    *,
    db_path: Path | str,
) -> StrategyExecutionPeriodChainStoreResult:
    request = parse_strategy_execution_period_chain_store_request(value)
    build = build_strategy_execution_period_chain(
        request.period_chain_input,
        db_path=db_path,
    )
    if not build.build_complete or build.chain is None:
        issue_codes = ", ".join(issue.code for issue in build.issues)
        detail = f": {issue_codes}" if issue_codes else ""
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_rebuild_failed",
            "Periodenkette konnte serverseitig nicht vollstaendig gebaut "
            f"werden{detail}",
        )

    chain = build.chain
    chain_payload = chain.to_dict()
    verified = _verified_period_chain_record_fields(chain_payload)
    if chain.chain_id != request.expected_chain_id:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_id_mismatch",
            "Serverseitig gebaute Ketten-ID stimmt nicht mit der Freigabe ueberein",
        )
    if chain.content_digest != request.expected_content_digest:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_digest_mismatch",
            "Serverseitig gebauter Kettendigest stimmt nicht mit der Freigabe ueberein",
        )

    resolved_path = Path(db_path).expanduser().resolve()
    connection = connect_metadata_db(resolved_path)
    new_record_created = False
    replayed = False
    try:
        with connection:
            connection.execute(STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_SCHEMA)
            row = _period_chain_row(connection, chain.chain_id)
            if row is None:
                try:
                    connection.execute(
                        """
                        INSERT INTO strategy_execution_period_chains (
                            chain_id,
                            chain_schema_version,
                            first_period,
                            last_period,
                            period_count,
                            run_index,
                            max_periods,
                            content_digest,
                            stored_at,
                            chain_payload_json
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            chain.chain_id,
                            chain.schema_version,
                            verified["first_period"],
                            verified["last_period"],
                            verified["period_count"],
                            verified["run_index"],
                            verified["max_periods"],
                            chain.content_digest,
                            request.stored_at,
                            _stable_json(chain_payload),
                        ),
                    )
                except sqlite3.IntegrityError as exc:
                    raise StrategyExecutionPeriodChainStoreError(
                        "immutable_period_chain_conflict",
                        "Periodenkette kollidiert mit einem vorhandenen "
                        "unveraenderlichen Eintrag",
                    ) from exc
                new_record_created = True
                row = _period_chain_row(connection, chain.chain_id)
            else:
                replayed = True
            if row is None:  # pragma: no cover - SQLite insert/select invariant.
                raise StrategyExecutionPeriodChainStoreError(
                    "period_chain_post_storage_missing",
                    "Gespeicherte Periodenkette konnte nicht erneut gelesen werden",
                )
            record = _row_to_verified_period_chain_record(row)
            if record.content_digest != chain.content_digest:
                raise StrategyExecutionPeriodChainStoreError(
                    "immutable_period_chain_digest_conflict",
                    "Vorhandene Periodenkette hat einen abweichenden Digest",
                )
            if _stable_json(record.period_chain) != _stable_json(chain_payload):
                raise StrategyExecutionPeriodChainStoreError(
                    "immutable_period_chain_payload_conflict",
                    "Vorhandene Periodenkette hat einen abweichenden Inhalt",
                )
            if any(
                getattr(record, field) != verified[field]
                for field in (
                    "first_period",
                    "last_period",
                    "period_count",
                    "run_index",
                    "max_periods",
                )
            ):
                raise StrategyExecutionPeriodChainStoreError(
                    "immutable_period_chain_metadata_conflict",
                    "Vorhandene Kettenmetadaten stimmen nicht mit dem Inhalt ueberein",
                )
    finally:
        connection.close()

    return StrategyExecutionPeriodChainStoreResult(
        mode="strategy_execution_period_chain_store_persist",
        db_path=str(resolved_path),
        record=record,
        storage_release_confirmed=True,
        chain_rebuilt=True,
        pre_storage_digest_verified=True,
        post_storage_digest_verified=True,
        new_record_created=new_record_created,
        replayed=replayed,
    )


def get_strategy_execution_period_chain(
    chain_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionPeriodChainStoreResult:
    if not chain_id.strip():
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_id_required",
            "Ketten-ID darf nicht leer sein",
        )
    resolved_path = Path(db_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_store_missing",
            f"Kettenspeicher existiert nicht: {resolved_path}",
        )
    connection = sqlite3.connect(
        readonly_sqlite_uri(
            resolved_path,
            description="strategy execution period chain store",
        ),
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    try:
        try:
            row = _period_chain_row(connection, chain_id)
        except sqlite3.DatabaseError as exc:
            raise StrategyExecutionPeriodChainStoreError(
                "period_chain_store_unreadable",
                f"Kettenspeicher ist nicht lesbar oder initialisiert: {exc}",
            ) from exc
        if row is None:
            raise StrategyExecutionPeriodChainStoreError(
                "period_chain_not_found",
                f"Periodenkette nicht gefunden: {chain_id}",
            )
        record = _row_to_verified_period_chain_record(row)
    finally:
        connection.close()
    return StrategyExecutionPeriodChainStoreResult(
        mode="strategy_execution_period_chain_store_read",
        db_path=str(resolved_path),
        record=record,
        storage_release_confirmed=True,
        chain_rebuilt=False,
        pre_storage_digest_verified=False,
        post_storage_digest_verified=True,
    )


def strategy_execution_period_chain_store_contract_payload() -> dict[str, object]:
    boundary_flags = {
        "explicit_storage_release_required": True,
        "server_side_period_chain_rebuild_required": True,
        "expected_chain_id_required": True,
        "expected_content_digest_required": True,
        "pre_storage_digest_check_enabled": True,
        "post_storage_digest_check_enabled": True,
        "on_read_digest_check_enabled": True,
        "immutable_insert_only_enabled": True,
        "idempotent_exact_replay_enabled": True,
        "period_chain_update_enabled": False,
        "free_database_paths_accepted": False,
        "browser_period_chain_payloads_accepted": False,
        "period_chain_persistence_enabled": True,
        "carryover_invocation_enabled": False,
        "runner_enabled": False,
        "ui_start_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION,
        "request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION
        ),
        "period_chain_input_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "build_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_period_chain_store_contract_read_only",
        "scope": "explicitly_released_immutable_period_chain_storage",
        "contract_endpoint": (
            "/api/strategies/execution-period-chain-store-contract"
        ),
        "persist_endpoint": "/api/strategies/execution-period-chain-store",
        "read_endpoint_template": (
            "/api/strategies/execution-period-chains/{chain_id}"
        ),
        "request_fields": sorted(_STORE_REQUEST_FIELDS),
        "storage_kind": "configured_workbench_sqlite",
        "immutable_identity": ["chain_id", "content_digest"],
        "digest_checks": [
            "after_server_side_rebuild_before_insert",
            "after_insert_or_exact_replay",
            "on_read",
        ],
        "partial_storage_allowed": False,
        "boundary_flags": boundary_flags,
        "next_gate": "PR140",
        **boundary_flags,
    }


def strategy_execution_period_chain_store_error_payload(
    code: str,
    message: str,
) -> dict[str, object]:
    return {
        "status": "error",
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION,
        "request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "mode": "strategy_execution_period_chain_store_error",
        "issues": [{"code": code, "message": message}],
        "storage_release_confirmed": False,
        "chain_rebuilt": False,
        "pre_storage_digest_verified": False,
        "post_storage_digest_verified": False,
        "period_chain_persisted": False,
        "new_record_created": False,
        "replayed": False,
        "writes_performed": False,
        "carryover_invocation_performed": False,
        "runner_invocation_performed": False,
        "execution_performed": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR140",
    }


def _verified_period_chain_record_fields(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_payload_object_required",
            "Ketteninhalt muss ein JSON-Objekt sein",
        )
    if frozenset(payload) != _CHAIN_TOP_LEVEL_FIELDS:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_payload_fields_mismatch",
            "Ketteninhalt hat nicht exakt die vertraglichen Abschnitte",
        )
    if payload.get("schema_version") != STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_schema_version_mismatch",
            "Ketten-Schemaversion stimmt nicht ueberein",
        )
    if payload.get("mode") != "strategy_execution_period_chain":
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_mode_mismatch",
            "Kettenmodus stimmt nicht ueberein",
        )
    if payload.get("base_model") != "Vdefmd6":
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_base_model_mismatch",
            "Ketten-Basismodell stimmt nicht ueberein",
        )

    identity = payload.get("identity")
    if not isinstance(identity, dict) or frozenset(identity) != _CHAIN_IDENTITY_FIELDS:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_identity_fields_mismatch",
            "Kettenidentitaet ist unvollstaendig oder enthaelt unbekannte Felder",
        )
    chain_id = identity.get("chain_id")
    content_digest = identity.get("content_digest")
    if identity.get("schema_version") != STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_identity_schema_version_mismatch",
            "Identitaets-Schemaversion stimmt nicht ueberein",
        )
    if not isinstance(chain_id, str) or not chain_id:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_id_invalid",
            "Ketten-ID ist ungueltig",
        )
    if not isinstance(content_digest, str):
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_digest_invalid",
            "Kettendigest ist ungueltig",
        )

    horizon = payload.get("horizon")
    if not isinstance(horizon, dict) or frozenset(horizon) != _CHAIN_HORIZON_FIELDS:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_horizon_fields_mismatch",
            "Kettenhorizont ist unvollstaendig oder enthaelt unbekannte Felder",
        )
    reconstructed_input = {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "base_model": "Vdefmd6",
        "scope": "contiguous_local_period_chain_input",
        "run_index": horizon.get("run_index"),
        "max_periods": horizon.get("max_periods"),
        "period_candidates": payload.get("period_candidates"),
        "transitions": payload.get("transitions"),
    }
    validation = validate_strategy_execution_period_chain_input(reconstructed_input)
    if not validation.valid:
        issue_codes = ", ".join(issue.code for issue in validation.issues)
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_contract_validation_failed",
            f"Gespeicherte Kettenstruktur ist ungueltig: {issue_codes}",
        )
    expected_horizon = {
        "first_period": validation.first_period,
        "last_period": validation.last_period,
        "period_count": validation.max_periods,
        "run_index": validation.run_index,
        "max_periods": validation.max_periods,
    }
    if horizon != expected_horizon:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_horizon_mismatch",
            "Kettenhorizont stimmt nicht mit Kandidaten und Uebergaengen ueberein",
        )
    if payload.get("provenance") != (
        strategy_execution_period_chain_build_provenance_payload(
            int(validation.expected_candidate_count)
        )
    ):
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_provenance_mismatch",
            "Kettenprovenienz stimmt nicht mit dem Bauvertrag ueberein",
        )
    if payload.get("execution_boundaries") != (
        strategy_execution_period_chain_execution_boundaries_payload()
    ):
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_execution_boundaries_mismatch",
            "Ketten-Ausfuehrungsgrenzen stimmen nicht mit dem Bauvertrag ueberein",
        )

    sections = {
        section_id: payload[section_id]
        for section_id in _CHAIN_CONTENT_SECTION_IDS
    }
    try:
        calculated_digest = calculate_strategy_execution_period_chain_content_digest(
            sections=sections,
            period_chain_schema_version=str(payload["schema_version"]),
            base_model=str(payload["base_model"]),
        )
        derived_chain_id = strategy_execution_period_chain_id_from_digest(
            calculated_digest
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_digest_calculation_failed",
            str(exc),
        ) from exc
    if calculated_digest != content_digest:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_digest_verification_failed",
            "Ketteninhalt stimmt nicht mit seinem Digest ueberein",
        )
    if derived_chain_id != chain_id:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_id_verification_failed",
            "Ketten-ID stimmt nicht mit dem verifizierten Digest ueberein",
        )
    return {
        "chain_id": chain_id,
        "content_digest": content_digest,
        **expected_horizon,
    }


def _row_to_verified_period_chain_record(
    row: sqlite3.Row,
) -> StrategyExecutionPeriodChainStoreRecord:
    try:
        payload = json.loads(row["chain_payload_json"])
    except (TypeError, json.JSONDecodeError) as exc:
        raise StrategyExecutionPeriodChainStoreError(
            "stored_period_chain_json_invalid",
            f"Gespeicherte Periodenkette enthaelt ungueltiges JSON: {exc}",
        ) from exc
    verified = _verified_period_chain_record_fields(payload)
    checks = {
        "chain_id": row["chain_id"],
        "content_digest": row["content_digest"],
        "first_period": row["first_period"],
        "last_period": row["last_period"],
        "period_count": row["period_count"],
        "run_index": row["run_index"],
        "max_periods": row["max_periods"],
    }
    if any(verified[field] != value for field, value in checks.items()):
        raise StrategyExecutionPeriodChainStoreError(
            "stored_period_chain_metadata_mismatch",
            "Gespeicherte Kettenmetadaten stimmen nicht mit dem Inhalt ueberein",
        )
    if row["chain_schema_version"] != STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION:
        raise StrategyExecutionPeriodChainStoreError(
            "stored_period_chain_schema_version_mismatch",
            "Gespeicherte Ketten-Schemaversion stimmt nicht ueberein",
        )
    stored_at = str(row["stored_at"])
    _validate_timestamp(stored_at)
    return StrategyExecutionPeriodChainStoreRecord(
        chain_id=str(verified["chain_id"]),
        content_digest=str(verified["content_digest"]),
        first_period=int(verified["first_period"]),
        last_period=int(verified["last_period"]),
        period_count=int(verified["period_count"]),
        run_index=int(verified["run_index"]),
        max_periods=int(verified["max_periods"]),
        stored_at=stored_at,
        period_chain=payload,
    )


def _period_chain_row(
    connection: sqlite3.Connection,
    chain_id: str,
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT
            chain_id,
            chain_schema_version,
            first_period,
            last_period,
            period_count,
            run_index,
            max_periods,
            content_digest,
            stored_at,
            chain_payload_json
        FROM strategy_execution_period_chains
        WHERE chain_id = ?
        """,
        (chain_id,),
    ).fetchone()


def _required_text(
    value: Mapping[str, object],
    field_name: str,
    *,
    code: str,
) -> str:
    field_value = value.get(field_name)
    if not isinstance(field_value, str) or not field_value.strip():
        raise StrategyExecutionPeriodChainStoreError(
            code,
            f"{field_name} muss eine nichtleere Zeichenkette sein",
        )
    return field_value


def _validate_timestamp(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise StrategyExecutionPeriodChainStoreError(
            "stored_at_invalid",
            "stored_at muss ein ISO-8601-Zeitpunkt sein",
        ) from exc
    if parsed.tzinfo is None:
        raise StrategyExecutionPeriodChainStoreError(
            "stored_at_timezone_required",
            "stored_at muss eine Zeitzone enthalten",
        )


def _stable_json(payload: object) -> str:
    try:
        return json.dumps(
            payload,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise StrategyExecutionPeriodChainStoreError(
            "period_chain_json_serialization_failed",
            str(exc),
        ) from exc
