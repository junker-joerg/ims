"""Digest-bound, idempotent storage for the separate IMS 2.x life chain."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import connect_metadata_db
from ims.api.sqlite_readonly import readonly_sqlite_uri


LIFE_RESULT_START_VERSION = "ims.life-result-start.v1"
LIFE_RESULT_DELIVERY_VERSION = "ims.life-result-delivery.v1"
LIFE_API_TIMEOUT_SECONDS = 20.0
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
_RESULT_ID = re.compile(r"life-[0-9a-f]{24}\Z")
_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{7,63}\Z")
_FIELDS = frozenset((
    "schema_version", "life_chain_input", "expected_input_digest",
    "expected_result_digest", "idempotency_key", "explicit_storage_release",
))
_SCHEMA = """
CREATE TABLE IF NOT EXISTS life_chain_results (
    result_id TEXT PRIMARY KEY,
    idempotency_key TEXT NOT NULL UNIQUE,
    input_digest TEXT NOT NULL,
    result_digest TEXT NOT NULL,
    record_digest TEXT NOT NULL,
    input_json TEXT NOT NULL,
    report_json TEXT NOT NULL,
    stored_at TEXT NOT NULL
)
"""


class LifeResultError(ValueError):
    def __init__(self, code: str, status_code: int) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def result_id_for(key: str, input_digest: str) -> str:
    raw = f"{key}\0{input_digest}".encode("ascii")
    return "life-" + hashlib.sha256(raw).hexdigest()[:24]


def _record_digest(result_id: str, key: str, input_digest: str, result_digest: str, stored_at: str) -> str:
    return digest({
        "result_id": result_id, "idempotency_key": key,
        "input_digest": input_digest, "result_digest": result_digest,
        "stored_at": stored_at,
    })


def parse_start(value: object) -> dict:
    if type(value) is not dict or frozenset(value) != _FIELDS:
        raise LifeResultError("start_request_fields_invalid", 400)
    if value.get("schema_version") != LIFE_RESULT_START_VERSION:
        raise LifeResultError("start_request_version_invalid", 400)
    if value.get("explicit_storage_release") is not True:
        raise LifeResultError("storage_release_required", 403)
    if type(value.get("life_chain_input")) is not dict:
        raise LifeResultError("life_chain_input_invalid", 400)
    key = value.get("idempotency_key")
    if type(key) is not str or not _KEY.fullmatch(key):
        raise LifeResultError("idempotency_key_invalid", 400)
    for name in ("expected_input_digest", "expected_result_digest"):
        candidate = value.get(name)
        if type(candidate) is not str or not _DIGEST.fullmatch(candidate):
            raise LifeResultError(f"{name}_invalid", 400)
    try:
        actual_digest = digest(value["life_chain_input"])
    except (TypeError, ValueError) as exc:
        raise LifeResultError("life_chain_input_unserializable", 400) from exc
    if actual_digest != value["expected_input_digest"]:
        raise LifeResultError("input_digest_mismatch", 409)
    return value


def _verified(row: sqlite3.Row) -> dict:
    try:
        request = json.loads(row["input_json"])
        report = json.loads(row["report_json"])
        valid = (
            type(request) is dict and type(report) is dict
            and report.get("valid") is True
            and report.get("calculated_period_count") == len(report.get("rows", []))
            and report.get("calculated_period_count") == len(report.get("resolved_sources", []))
            and digest(request) == row["input_digest"]
            and digest(report) == row["result_digest"]
            and result_id_for(row["idempotency_key"], row["input_digest"]) == row["result_id"]
            and _record_digest(
                row["result_id"], row["idempotency_key"], row["input_digest"],
                row["result_digest"], row["stored_at"],
            ) == row["record_digest"]
        )
    except (TypeError, ValueError, KeyError):
        valid = False
    if not valid:
        raise LifeResultError("stored_life_result_corrupt", 409)
    return {
        "schema_version": LIFE_RESULT_DELIVERY_VERSION,
        "status": "ok",
        "result_id": row["result_id"],
        "input_digest": row["input_digest"],
        "result_digest": row["result_digest"],
        "record_digest": row["record_digest"],
        "stored_at": row["stored_at"],
        "life_chain_input": request,
        "report": report,
        "storage_kind": "sqlite",
        "stored_result_verified": True,
        "historical_full_equality_claim": False,
    }


def get_life_result(db_path: Path, result_id: str) -> dict:
    if not _RESULT_ID.fullmatch(result_id):
        raise LifeResultError("result_id_invalid", 400)
    if not db_path.is_file():
        raise LifeResultError("life_result_not_found", 404)
    try:
        connection = sqlite3.connect(
            readonly_sqlite_uri(db_path, description="life result store"), uri=True,
        )
        connection.row_factory = sqlite3.Row
        try:
            row = connection.execute(
                "SELECT * FROM life_chain_results WHERE result_id = ?", (result_id,),
            ).fetchone()
        finally:
            connection.close()
    except MetadataImportError as exc:
        raise LifeResultError("life_result_store_unavailable", 503) from exc
    except sqlite3.Error as exc:
        if "no such table" in str(exc):
            raise LifeResultError("life_result_not_found", 404) from exc
        raise LifeResultError("life_result_store_unavailable", 503) from exc
    if row is None:
        raise LifeResultError("life_result_not_found", 404)
    return _verified(row)


def list_life_results(db_path: Path) -> dict:
    if not db_path.is_file():
        return {"schema_version": LIFE_RESULT_DELIVERY_VERSION, "status": "ok", "results": [], "writes_performed": False}
    try:
        connection = sqlite3.connect(
            readonly_sqlite_uri(db_path, description="life result store"), uri=True,
        )
        connection.row_factory = sqlite3.Row
        try:
            rows = connection.execute(
                "SELECT * FROM life_chain_results ORDER BY stored_at DESC, result_id LIMIT 100",
            ).fetchall()
        finally:
            connection.close()
    except MetadataImportError as exc:
        raise LifeResultError("life_result_store_unavailable", 503) from exc
    except sqlite3.Error as exc:
        if "no such table" in str(exc):
            rows = []
        else:
            raise LifeResultError("life_result_store_unavailable", 503) from exc
    results = []
    for row in rows:
        record = _verified(row)
        results.append({
            "result_id": record["result_id"],
            "insurer_id": record["report"]["insurer_id"],
            "period_count": record["report"]["calculated_period_count"],
            "stored_at": record["stored_at"],
            "input_digest": record["input_digest"],
            "result_digest": record["result_digest"],
            "record_digest": record["record_digest"],
        })
    return {
        "schema_version": LIFE_RESULT_DELIVERY_VERSION,
        "status": "ok", "results": results,
        "writes_performed": False,
    }


def replay_life_result(db_path: Path, request: dict) -> dict | None:
    if not db_path.is_file():
        return None
    try:
        connection = sqlite3.connect(
            readonly_sqlite_uri(db_path, description="life result store"), uri=True,
        )
        connection.row_factory = sqlite3.Row
        try:
            row = connection.execute(
                "SELECT * FROM life_chain_results WHERE idempotency_key = ?",
                (request["idempotency_key"],),
            ).fetchone()
        finally:
            connection.close()
    except MetadataImportError as exc:
        raise LifeResultError("life_result_store_unavailable", 503) from exc
    except sqlite3.Error as exc:
        if "no such table" in str(exc):
            return None
        raise LifeResultError("life_result_store_unavailable", 503) from exc
    if row is None:
        return None
    record = _verified(row)
    if (record["input_digest"] != request["expected_input_digest"]
            or record["result_digest"] != request["expected_result_digest"]):
        raise LifeResultError("idempotency_key_conflict", 409)
    return {**record, "replayed": True, "writes_performed": False}


def persist_life_result(db_path: Path, request: dict, report: dict) -> dict:
    if report.get("valid") is not True:
        raise LifeResultError("life_chain_invalid", 422)
    input_digest = digest(request["life_chain_input"])
    result_digest = digest(report)
    if input_digest != request["expected_input_digest"]:
        raise LifeResultError("input_digest_mismatch", 409)
    if result_digest != request["expected_result_digest"]:
        raise LifeResultError("result_digest_mismatch", 409)
    result_id = result_id_for(request["idempotency_key"], input_digest)
    stored_at = datetime.now(timezone.utc).isoformat()
    record_digest = _record_digest(
        result_id, request["idempotency_key"], input_digest,
        result_digest, stored_at,
    )
    try:
        connection = connect_metadata_db(db_path)
        try:
            connection.execute("PRAGMA busy_timeout = 5000")
            connection.execute(_SCHEMA)
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute(
                    "SELECT * FROM life_chain_results WHERE idempotency_key = ?",
                    (request["idempotency_key"],),
                ).fetchone()
                if row is not None:
                    record = _verified(row)
                    if (record["input_digest"] != input_digest
                            or record["result_digest"] != result_digest):
                        raise LifeResultError("idempotency_key_conflict", 409)
                    return {**record, "replayed": True, "writes_performed": False}
                connection.execute(
                    "INSERT INTO life_chain_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        result_id, request["idempotency_key"], input_digest,
                        result_digest, record_digest,
                        canonical_json(request["life_chain_input"]),
                        canonical_json(report), stored_at,
                    ),
                )
                row = connection.execute(
                    "SELECT * FROM life_chain_results WHERE result_id = ?", (result_id,),
                ).fetchone()
                record = _verified(row)
        finally:
            connection.close()
    except sqlite3.Error as exc:
        raise LifeResultError("life_result_store_unavailable", 503) from exc
    return {**record, "replayed": False, "writes_performed": True}


def contract_payload() -> dict[str, object]:
    return {
        "schema_version": LIFE_RESULT_DELIVERY_VERSION,
        "start_request_schema_version": LIFE_RESULT_START_VERSION,
        "preview_endpoint": "/api/accounting/life-period-chain/preview",
        "start_endpoint": "/api/accounting/life-period-chain/start",
        "results_endpoint": "/api/accounting/life-period-chain/results",
        "result_endpoint": "/api/accounting/life-period-chain/result/{result_id}",
        "xlsx_endpoint": "/api/accounting/life-period-chain/result/{result_id}.xlsx",
        "timeout_seconds": LIFE_API_TIMEOUT_SECONDS,
        "explicit_storage_release_required": True,
        "expected_input_and_result_digests_required": True,
        "xlsx_if_match_required": True,
        "xlsx_amount_cells": "canonical_text",
        "historical_full_equality_claim": False,
    }
