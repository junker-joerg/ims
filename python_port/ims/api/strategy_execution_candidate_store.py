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
from ims.strategies.execution_candidate_build import (
    StrategyExecutionScenarioProfileDefinition,
    build_strategy_execution_candidate,
    calculate_strategy_execution_candidate_content_digest,
    strategy_execution_candidate_id_from_digest,
)
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_SECTIONS,
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)


STRATEGY_EXECUTION_CANDIDATE_STORE_VERSION = (
    "ims.strategy-execution-candidate-store.v1"
)
STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION = (
    "ims.strategy-execution-candidate-store-request.v1"
)
STRATEGY_EXECUTION_CANDIDATE_OVERVIEW_VERSION = (
    "ims.strategy-execution-candidate-overview.v1"
)

STRATEGY_EXECUTION_CANDIDATE_STORE_SCHEMA = """
CREATE TABLE IF NOT EXISTS strategy_execution_candidates (
    candidate_id TEXT PRIMARY KEY,
    candidate_schema_version TEXT NOT NULL,
    draft_id TEXT NOT NULL,
    period INTEGER NOT NULL CHECK (period >= 1),
    profile_id TEXT NOT NULL,
    profile_content_digest TEXT NOT NULL,
    content_digest TEXT NOT NULL UNIQUE,
    stored_at TEXT NOT NULL,
    candidate_payload_json TEXT NOT NULL
)
"""

_STORE_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "candidate_input",
        "expected_candidate_id",
        "expected_content_digest",
        "stored_at",
        "explicit_storage_release",
    }
)
_CANDIDATE_CONTENT_SECTION_IDS = tuple(
    definition.section_id
    for definition in STRATEGY_EXECUTION_CANDIDATE_SECTIONS
    if definition.section_id != "identity"
)
_CANDIDATE_TOP_LEVEL_FIELDS = frozenset(
    {"schema_version", "mode", "identity", *_CANDIDATE_CONTENT_SECTION_IDS}
)
_CANDIDATE_IDENTITY_FIELDS = frozenset(
    {"candidate_id", "draft_id", "period", "content_digest"}
)


class StrategyExecutionCandidateStoreError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateStoreRequest:
    candidate_input: dict[str, object]
    expected_candidate_id: str
    expected_content_digest: str
    stored_at: str
    explicit_storage_release: bool
    schema_version: str = STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateStoreRecord:
    candidate_id: str
    draft_id: str
    period: int
    profile_id: str
    profile_content_digest: str
    content_digest: str
    stored_at: str
    candidate: dict[str, object]
    candidate_schema_version: str = STRATEGY_EXECUTION_CANDIDATE_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_schema_version": self.candidate_schema_version,
            "draft_id": self.draft_id,
            "period": self.period,
            "profile_id": self.profile_id,
            "profile_content_digest": self.profile_content_digest,
            "content_digest": self.content_digest,
            "stored_at": self.stored_at,
            "candidate": deepcopy(self.candidate),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateStoreResult:
    mode: str
    db_path: str
    record: StrategyExecutionCandidateStoreRecord
    storage_release_confirmed: bool
    candidate_rebuilt: bool
    pre_storage_digest_verified: bool
    post_storage_digest_verified: bool
    new_record_created: bool = False
    replayed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "schema_version": STRATEGY_EXECUTION_CANDIDATE_STORE_VERSION,
            "mode": self.mode,
            "db_path": self.db_path,
            "record": self.record.to_dict(),
            "storage_release_confirmed": self.storage_release_confirmed,
            "candidate_rebuilt": self.candidate_rebuilt,
            "pre_storage_digest_verified": self.pre_storage_digest_verified,
            "post_storage_digest_verified": self.post_storage_digest_verified,
            "candidate_persisted": True,
            "new_record_created": self.new_record_created,
            "replayed": self.replayed,
            "writes_performed": self.new_record_created,
            "run_control_connected": False,
            "runner_invocation_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateOverviewResult:
    db_path: str
    store_initialized: bool
    candidates: tuple[dict[str, object], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "schema_version": STRATEGY_EXECUTION_CANDIDATE_OVERVIEW_VERSION,
            "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
            "mode": "strategy_execution_candidate_overview_read_only",
            "storage": {
                "kind": "sqlite",
                "configured": True,
                "path": self.db_path,
                "store_initialized": self.store_initialized,
                "immutable": True,
            },
            "candidate_count": len(self.candidates),
            "candidates": [deepcopy(candidate) for candidate in self.candidates],
            "all_candidate_digests_verified": all(
                candidate["digest_verified"] for candidate in self.candidates
            ),
            "writes_performed": False,
            "run_control_connected": True,
            "run_control_release_check_available": True,
            "runner_invocation_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
        }


def parse_strategy_execution_candidate_store_request(
    value: object,
) -> StrategyExecutionCandidateStoreRequest:
    if not isinstance(value, dict):
        raise StrategyExecutionCandidateStoreError(
            "store_request_object_required",
            "Kandidatenspeicher-Request muss ein JSON-Objekt sein",
        )
    actual_fields = frozenset(value)
    missing = sorted(_STORE_REQUEST_FIELDS - actual_fields)
    unknown = sorted(actual_fields - _STORE_REQUEST_FIELDS)
    if missing:
        raise StrategyExecutionCandidateStoreError(
            "store_request_fields_missing",
            f"Kandidatenspeicher-Felder fehlen: {', '.join(missing)}",
        )
    if unknown:
        raise StrategyExecutionCandidateStoreError(
            "store_request_fields_unknown",
            f"Kandidatenspeicher-Felder sind nicht erlaubt: {', '.join(unknown)}",
        )
    if value["schema_version"] != STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION:
        raise StrategyExecutionCandidateStoreError(
            "store_request_schema_version_mismatch",
            "Kandidatenspeicher-Schemaversion stimmt nicht ueberein",
        )
    if value["explicit_storage_release"] is not True:
        raise StrategyExecutionCandidateStoreError(
            "storage_release_required",
            "Explizite Speicherfreigabe ist erforderlich",
        )
    candidate_input = value["candidate_input"]
    if not isinstance(candidate_input, dict):
        raise StrategyExecutionCandidateStoreError(
            "candidate_input_object_required",
            "Kandidateneingang muss ein JSON-Objekt sein",
        )
    expected_digest = _required_text(
        value,
        "expected_content_digest",
        code="expected_content_digest_required",
    )
    try:
        derived_candidate_id = strategy_execution_candidate_id_from_digest(
            expected_digest
        )
    except ValueError as exc:
        raise StrategyExecutionCandidateStoreError(
            "expected_content_digest_invalid",
            str(exc),
        ) from exc
    expected_candidate_id = _required_text(
        value,
        "expected_candidate_id",
        code="expected_candidate_id_required",
    )
    if expected_candidate_id != derived_candidate_id:
        raise StrategyExecutionCandidateStoreError(
            "expected_candidate_identity_mismatch",
            "Erwartete Kandidaten-ID passt nicht zum erwarteten Digest",
        )
    stored_at = _required_text(value, "stored_at", code="stored_at_required")
    _validate_timestamp(stored_at)
    return StrategyExecutionCandidateStoreRequest(
        candidate_input=deepcopy(candidate_input),
        expected_candidate_id=expected_candidate_id,
        expected_content_digest=expected_digest,
        stored_at=stored_at,
        explicit_storage_release=True,
    )


def persist_strategy_execution_candidate(
    value: object,
    *,
    db_path: Path | str,
    profiles: Mapping[str, StrategyExecutionScenarioProfileDefinition],
    trusted_profile_root: Path | str,
) -> StrategyExecutionCandidateStoreResult:
    request = parse_strategy_execution_candidate_store_request(value)
    build = build_strategy_execution_candidate(
        request.candidate_input,
        profiles=profiles,
        trusted_profile_root=trusted_profile_root,
    )
    if not build.build_complete or build.candidate is None:
        issue_codes = ", ".join(issue.code for issue in build.issues)
        detail = f": {issue_codes}" if issue_codes else ""
        raise StrategyExecutionCandidateStoreError(
            "candidate_rebuild_failed",
            f"Kandidat konnte serverseitig nicht vollstaendig gebaut werden{detail}",
        )

    candidate = build.candidate
    candidate_payload = candidate.to_dict()
    verified = _verified_candidate_record_fields(candidate_payload)
    if candidate.candidate_id != request.expected_candidate_id:
        raise StrategyExecutionCandidateStoreError(
            "candidate_id_mismatch",
            "Serverseitig gebaute Kandidaten-ID stimmt nicht mit der Freigabe ueberein",
        )
    if candidate.content_digest != request.expected_content_digest:
        raise StrategyExecutionCandidateStoreError(
            "candidate_digest_mismatch",
            "Serverseitig gebauter Kandidatendigest stimmt nicht mit der Freigabe ueberein",
        )

    resolved_path = Path(db_path).expanduser().resolve()
    connection = connect_metadata_db(resolved_path)
    new_record_created = False
    replayed = False
    try:
        with connection:
            connection.execute(STRATEGY_EXECUTION_CANDIDATE_STORE_SCHEMA)
            row = _candidate_row(connection, candidate.candidate_id)
            if row is None:
                try:
                    connection.execute(
                        """
                        INSERT INTO strategy_execution_candidates (
                            candidate_id,
                            candidate_schema_version,
                            draft_id,
                            period,
                            profile_id,
                            profile_content_digest,
                            content_digest,
                            stored_at,
                            candidate_payload_json
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            candidate.candidate_id,
                            candidate.schema_version,
                            candidate.draft_id,
                            candidate.period,
                            candidate.profile_id,
                            candidate.profile_content_digest,
                            candidate.content_digest,
                            request.stored_at,
                            _stable_json(candidate_payload),
                        ),
                    )
                except sqlite3.IntegrityError as exc:
                    raise StrategyExecutionCandidateStoreError(
                        "immutable_candidate_conflict",
                        "Kandidat kollidiert mit einem vorhandenen unveraenderlichen Eintrag",
                    ) from exc
                new_record_created = True
                row = _candidate_row(connection, candidate.candidate_id)
            else:
                replayed = True
            if row is None:  # pragma: no cover - SQLite insert/select invariant.
                raise StrategyExecutionCandidateStoreError(
                    "candidate_post_storage_missing",
                    "Gespeicherter Kandidat konnte nicht erneut gelesen werden",
                )
            record = _row_to_verified_record(row)
            if record.content_digest != candidate.content_digest:
                raise StrategyExecutionCandidateStoreError(
                    "immutable_candidate_digest_conflict",
                    "Vorhandener Kandidat hat einen abweichenden Digest",
                )
            if _stable_json(record.candidate) != _stable_json(candidate_payload):
                raise StrategyExecutionCandidateStoreError(
                    "immutable_candidate_payload_conflict",
                    "Vorhandener Kandidat hat einen abweichenden Inhalt",
                )
            if (
                record.draft_id != verified["draft_id"]
                or record.period != verified["period"]
                or record.profile_id != verified["profile_id"]
                or record.profile_content_digest
                != verified["profile_content_digest"]
            ):
                raise StrategyExecutionCandidateStoreError(
                    "immutable_candidate_metadata_conflict",
                    "Vorhandene Kandidatenmetadaten stimmen nicht mit dem Inhalt ueberein",
                )
    finally:
        connection.close()

    return StrategyExecutionCandidateStoreResult(
        mode="strategy_execution_candidate_store_persist",
        db_path=str(resolved_path),
        record=record,
        storage_release_confirmed=True,
        candidate_rebuilt=True,
        pre_storage_digest_verified=True,
        post_storage_digest_verified=True,
        new_record_created=new_record_created,
        replayed=replayed,
    )


def get_strategy_execution_candidate(
    candidate_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionCandidateStoreResult:
    if not candidate_id.strip():
        raise StrategyExecutionCandidateStoreError(
            "candidate_id_required",
            "Kandidaten-ID darf nicht leer sein",
        )
    resolved_path = Path(db_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise StrategyExecutionCandidateStoreError(
            "candidate_store_missing",
            f"Kandidatenspeicher existiert nicht: {resolved_path}",
        )
    connection = sqlite3.connect(
        readonly_sqlite_uri(
            resolved_path,
            description="strategy execution candidate store",
        ),
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    try:
        try:
            row = _candidate_row(connection, candidate_id)
        except sqlite3.DatabaseError as exc:
            raise StrategyExecutionCandidateStoreError(
                "candidate_store_unreadable",
                f"Kandidatenspeicher ist nicht lesbar oder initialisiert: {exc}",
            ) from exc
        if row is None:
            raise StrategyExecutionCandidateStoreError(
                "candidate_not_found",
                f"Kandidat nicht gefunden: {candidate_id}",
            )
        record = _row_to_verified_record(row)
    finally:
        connection.close()
    return StrategyExecutionCandidateStoreResult(
        mode="strategy_execution_candidate_store_read",
        db_path=str(resolved_path),
        record=record,
        storage_release_confirmed=True,
        candidate_rebuilt=False,
        pre_storage_digest_verified=False,
        post_storage_digest_verified=True,
    )


def list_strategy_execution_candidates(
    *,
    db_path: Path | str,
) -> StrategyExecutionCandidateOverviewResult:
    """Liest verifizierte Kandidatenkurzsaetze ohne die Ablage anzulegen."""

    resolved_path = Path(db_path).expanduser().resolve()
    if not resolved_path.is_file():
        return StrategyExecutionCandidateOverviewResult(
            db_path=str(resolved_path),
            store_initialized=False,
            candidates=(),
        )
    connection = sqlite3.connect(
        readonly_sqlite_uri(
            resolved_path,
            description="strategy execution candidate overview",
        ),
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    try:
        try:
            table_exists = connection.execute(
                """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table' AND name = 'strategy_execution_candidates'
                """
            ).fetchone()
            if table_exists is None:
                return StrategyExecutionCandidateOverviewResult(
                    db_path=str(resolved_path),
                    store_initialized=False,
                    candidates=(),
                )
            rows = connection.execute(
                """
                SELECT
                    candidate_id,
                    candidate_schema_version,
                    draft_id,
                    period,
                    profile_id,
                    profile_content_digest,
                    content_digest,
                    stored_at,
                    candidate_payload_json
                FROM strategy_execution_candidates
                ORDER BY stored_at DESC, candidate_id
                """
            ).fetchall()
        except sqlite3.DatabaseError as exc:
            raise StrategyExecutionCandidateStoreError(
                "candidate_store_unreadable",
                f"Kandidatenspeicher ist nicht lesbar oder initialisiert: {exc}",
            ) from exc
        candidates = tuple(
            _candidate_overview_payload(_row_to_verified_record(row))
            for row in rows
        )
    finally:
        connection.close()
    return StrategyExecutionCandidateOverviewResult(
        db_path=str(resolved_path),
        store_initialized=True,
        candidates=candidates,
    )


def strategy_execution_candidate_overview_unavailable_payload(
    *,
    storage_kind: str,
    configured: bool,
) -> dict[str, object]:
    return {
        "status": "ok",
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_OVERVIEW_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_candidate_overview_read_only",
        "storage": {
            "kind": storage_kind,
            "configured": configured,
            "path": None,
            "store_initialized": False,
            "immutable": True,
        },
        "candidate_count": 0,
        "candidates": [],
        "all_candidate_digests_verified": True,
        "writes_performed": False,
        "run_control_connected": False,
        "run_control_release_check_available": True,
        "runner_invocation_performed": False,
        "execution_performed": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }


def strategy_execution_candidate_store_contract_payload() -> dict[str, object]:
    boundary_flags = {
        "explicit_storage_release_required": True,
        "server_side_candidate_rebuild_required": True,
        "expected_candidate_id_required": True,
        "expected_content_digest_required": True,
        "pre_storage_digest_check_enabled": True,
        "post_storage_digest_check_enabled": True,
        "immutable_insert_only_enabled": True,
        "idempotent_exact_replay_enabled": True,
        "candidate_update_enabled": False,
        "free_database_paths_accepted": False,
        "browser_candidate_payloads_accepted": False,
        "candidate_persistence_enabled": True,
        "run_control_enabled": False,
        "runner_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_STORE_VERSION,
        "request_schema_version": STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_candidate_store_contract_read_only",
        "scope": "explicitly_released_immutable_candidate_storage",
        "contract_endpoint": "/api/strategies/execution-candidate-store-contract",
        "persist_endpoint": "/api/strategies/execution-candidate-store",
        "read_endpoint_template": "/api/strategies/execution-candidates/{candidate_id}",
        "overview_endpoint": "/api/strategies/execution-candidates",
        "request_fields": sorted(_STORE_REQUEST_FIELDS),
        "storage_kind": "configured_workbench_sqlite",
        "immutable_identity": ["candidate_id", "content_digest"],
        "digest_checks": ["before_insert", "after_insert_or_exact_replay", "on_read"],
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }


def _candidate_overview_payload(
    record: StrategyExecutionCandidateStoreRecord,
) -> dict[str, object]:
    candidate = record.candidate
    source_documents = _mapping(candidate, "source_documents")
    assignment_draft = _mapping(source_documents, "assignment_draft")
    market_ground_state = _mapping(candidate, "market_ground_state")
    contract_versions = _mapping(candidate, "contract_versions")
    vu_rule_snapshots = _mapping(candidate, "vu_rule_snapshots")
    vn_rule_snapshots = _mapping(candidate, "vn_rule_snapshots")
    vn_process_snapshots = _mapping(candidate, "vn_process_snapshots")
    vu_collections = _mapping(vu_rule_snapshots, "collections")
    vn_rule_collections = _mapping(vn_rule_snapshots, "collections")
    vn_process_collections = _mapping(vn_process_snapshots, "collections")
    insurers = market_ground_state.get("insurers")
    policyholders = market_ground_state.get("policyholders")
    return {
        "candidate_id": record.candidate_id,
        "draft_id": record.draft_id,
        "draft_label": str(assignment_draft.get("label", record.draft_id)),
        "period": record.period,
        "profile_id": record.profile_id,
        "profile_content_digest": record.profile_content_digest,
        "content_digest": record.content_digest,
        "digest_algorithm": "sha256",
        "digest_verified": True,
        "stored_at": record.stored_at,
        "storage_status": "persisted_immutable",
        "source_document_count": len(source_documents),
        "contract_version_count": len(contract_versions),
        "insurer_count": len(insurers) if isinstance(insurers, list) else 0,
        "policyholder_count": (
            len(policyholders) if isinstance(policyholders, list) else 0
        ),
        "vu_snapshot_count": _snapshot_count(vu_collections),
        "vn_rule_snapshot_count": _snapshot_count(vn_rule_collections),
        "vn_process_snapshot_count": _snapshot_count(vn_process_collections),
        "readiness": {
            "candidate_complete": True,
            "source_documents_present": bool(source_documents),
            "market_ground_state_present": bool(market_ground_state),
            "storage_integrity_verified": True,
            "run_control_ready": True,
            "run_control_release_check_available": True,
            "effect_probe_available": True,
            "effect_probe_start_available": True,
            "effect_probe_result_persistence_available": True,
            "execution_ready": False,
            "next_gate": "PR135",
        },
    }


def _verified_candidate_record_fields(
    payload: object,
) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise StrategyExecutionCandidateStoreError(
            "candidate_payload_object_required",
            "Kandidateninhalt muss ein JSON-Objekt sein",
        )
    if frozenset(payload) != _CANDIDATE_TOP_LEVEL_FIELDS:
        raise StrategyExecutionCandidateStoreError(
            "candidate_payload_fields_mismatch",
            "Kandidateninhalt hat nicht exakt die vertraglichen Abschnitte",
        )
    if payload.get("schema_version") != STRATEGY_EXECUTION_CANDIDATE_VERSION:
        raise StrategyExecutionCandidateStoreError(
            "candidate_schema_version_mismatch",
            "Kandidaten-Schemaversion stimmt nicht ueberein",
        )
    if payload.get("mode") != "strategy_execution_candidate":
        raise StrategyExecutionCandidateStoreError(
            "candidate_mode_mismatch",
            "Kandidatenmodus stimmt nicht ueberein",
        )
    identity = payload.get("identity")
    if not isinstance(identity, dict) or frozenset(identity) != _CANDIDATE_IDENTITY_FIELDS:
        raise StrategyExecutionCandidateStoreError(
            "candidate_identity_fields_mismatch",
            "Kandidatenidentitaet ist unvollstaendig oder enthaelt unbekannte Felder",
        )
    candidate_id = identity.get("candidate_id")
    draft_id = identity.get("draft_id")
    period = identity.get("period")
    content_digest = identity.get("content_digest")
    if not isinstance(candidate_id, str) or not candidate_id:
        raise StrategyExecutionCandidateStoreError(
            "candidate_id_invalid",
            "Kandidaten-ID ist ungueltig",
        )
    if not isinstance(draft_id, str) or not draft_id:
        raise StrategyExecutionCandidateStoreError(
            "candidate_draft_id_invalid",
            "Kandidaten-Entwurfs-ID ist ungueltig",
        )
    if isinstance(period, bool) or not isinstance(period, int) or period < 1:
        raise StrategyExecutionCandidateStoreError(
            "candidate_period_invalid",
            "Kandidatenperiode ist ungueltig",
        )
    if not isinstance(content_digest, str):
        raise StrategyExecutionCandidateStoreError(
            "candidate_digest_invalid",
            "Kandidatendigest ist ungueltig",
        )
    sections = {
        section_id: payload[section_id]
        for section_id in _CANDIDATE_CONTENT_SECTION_IDS
    }
    try:
        calculated_digest = calculate_strategy_execution_candidate_content_digest(
            draft_id=draft_id,
            period=period,
            sections=sections,
            candidate_schema_version=str(payload["schema_version"]),
        )
        derived_candidate_id = strategy_execution_candidate_id_from_digest(
            calculated_digest
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise StrategyExecutionCandidateStoreError(
            "candidate_digest_calculation_failed",
            str(exc),
        ) from exc
    if calculated_digest != content_digest:
        raise StrategyExecutionCandidateStoreError(
            "candidate_digest_verification_failed",
            "Kandidateninhalt stimmt nicht mit seinem Digest ueberein",
        )
    if derived_candidate_id != candidate_id:
        raise StrategyExecutionCandidateStoreError(
            "candidate_id_verification_failed",
            "Kandidaten-ID stimmt nicht mit dem verifizierten Digest ueberein",
        )
    ground_state = payload.get("market_ground_state")
    if not isinstance(ground_state, dict):
        raise StrategyExecutionCandidateStoreError(
            "candidate_ground_state_invalid",
            "Marktgrundzustand des Kandidaten ist ungueltig",
        )
    profile_id = ground_state.get("profile_id")
    profile_digest = ground_state.get("profile_content_digest")
    if not isinstance(profile_id, str) or not profile_id:
        raise StrategyExecutionCandidateStoreError(
            "candidate_profile_id_invalid",
            "Kandidaten-Profil-ID ist ungueltig",
        )
    if not isinstance(profile_digest, str) or not profile_digest:
        raise StrategyExecutionCandidateStoreError(
            "candidate_profile_digest_invalid",
            "Kandidaten-Profildigest ist ungueltig",
        )
    return {
        "candidate_id": candidate_id,
        "draft_id": draft_id,
        "period": period,
        "profile_id": profile_id,
        "profile_content_digest": profile_digest,
        "content_digest": content_digest,
    }


def _row_to_verified_record(
    row: sqlite3.Row,
) -> StrategyExecutionCandidateStoreRecord:
    try:
        payload = json.loads(row["candidate_payload_json"])
    except (TypeError, json.JSONDecodeError) as exc:
        raise StrategyExecutionCandidateStoreError(
            "stored_candidate_json_invalid",
            f"Gespeicherter Kandidat enthaelt ungueltiges JSON: {exc}",
        ) from exc
    verified = _verified_candidate_record_fields(payload)
    checks = {
        "candidate_id": row["candidate_id"],
        "draft_id": row["draft_id"],
        "period": row["period"],
        "profile_id": row["profile_id"],
        "profile_content_digest": row["profile_content_digest"],
        "content_digest": row["content_digest"],
    }
    if any(verified[field] != value for field, value in checks.items()):
        raise StrategyExecutionCandidateStoreError(
            "stored_candidate_metadata_mismatch",
            "Gespeicherte Kandidatenmetadaten stimmen nicht mit dem Inhalt ueberein",
        )
    if row["candidate_schema_version"] != STRATEGY_EXECUTION_CANDIDATE_VERSION:
        raise StrategyExecutionCandidateStoreError(
            "stored_candidate_schema_version_mismatch",
            "Gespeicherte Kandidaten-Schemaversion stimmt nicht ueberein",
        )
    return StrategyExecutionCandidateStoreRecord(
        candidate_id=str(verified["candidate_id"]),
        candidate_schema_version=str(row["candidate_schema_version"]),
        draft_id=str(verified["draft_id"]),
        period=int(verified["period"]),
        profile_id=str(verified["profile_id"]),
        profile_content_digest=str(verified["profile_content_digest"]),
        content_digest=str(verified["content_digest"]),
        stored_at=str(row["stored_at"]),
        candidate=payload,
    )


def _candidate_row(
    connection: sqlite3.Connection,
    candidate_id: str,
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT
            candidate_id,
            candidate_schema_version,
            draft_id,
            period,
            profile_id,
            profile_content_digest,
            content_digest,
            stored_at,
            candidate_payload_json
        FROM strategy_execution_candidates
        WHERE candidate_id = ?
        """,
        (candidate_id,),
    ).fetchone()


def _required_text(
    value: Mapping[str, object],
    field_name: str,
    *,
    code: str,
) -> str:
    field_value = value.get(field_name)
    if not isinstance(field_value, str) or not field_value.strip():
        raise StrategyExecutionCandidateStoreError(
            code,
            f"{field_name} muss eine nichtleere Zeichenkette sein",
        )
    return field_value


def _mapping(value: Mapping[str, object], field_name: str) -> dict[str, object]:
    nested = value.get(field_name)
    return nested if isinstance(nested, dict) else {}


def _snapshot_count(collections: Mapping[str, object]) -> int:
    return sum(
        len(snapshots)
        for snapshots in collections.values()
        if isinstance(snapshots, list)
    )


def _validate_timestamp(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise StrategyExecutionCandidateStoreError(
            "stored_at_invalid",
            "stored_at muss ein ISO-8601-Zeitpunkt sein",
        ) from exc
    if parsed.tzinfo is None:
        raise StrategyExecutionCandidateStoreError(
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
        raise StrategyExecutionCandidateStoreError(
            "candidate_json_serialization_failed",
            str(exc),
        ) from exc
