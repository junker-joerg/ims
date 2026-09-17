"""Digest-bound, idempotent storage for the IMS 2.x health period chain."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ims.accounting.health_period_chain import (
    HEALTH_PERIOD_CHAIN_HORIZONS,
    HEALTH_PERIOD_CHAIN_INPUT_VERSION,
    HEALTH_PERIOD_CHAIN_RESULT_VERSION,
)
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import connect_metadata_db
from ims.api.sqlite_readonly import readonly_sqlite_uri


HEALTH_RESULT_START_VERSION = "ims.health-result-start.v1"
HEALTH_RESULT_DELIVERY_VERSION = "ims.health-result-delivery.v1"
HEALTH_API_TIMEOUT_SECONDS = 20.0
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
_RESULT_ID = re.compile(r"health-[0-9a-f]{24}\Z")
_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{7,63}\Z")
_FIELDS = frozenset((
    "schema_version", "health_chain_input", "expected_input_digest",
    "expected_result_digest", "idempotency_key", "explicit_storage_release",
))
_SCHEMA = """
CREATE TABLE IF NOT EXISTS health_chain_results (
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


class HealthResultError(ValueError):
    def __init__(self, code: str, status_code: int) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def result_id_for(key: str, input_digest: str) -> str:
    return "health-" + hashlib.sha256(f"{key}\0{input_digest}".encode("ascii")).hexdigest()[:24]


def _record_digest(result_id: str, key: str, input_digest: str, result_digest: str, stored_at: str) -> str:
    return digest({
        "result_id": result_id, "idempotency_key": key,
        "input_digest": input_digest, "result_digest": result_digest,
        "stored_at": stored_at,
    })


def parse_start(value: object) -> dict:
    if type(value) is not dict or frozenset(value) != _FIELDS:
        raise HealthResultError("start_request_fields_invalid", 400)
    if value.get("schema_version") != HEALTH_RESULT_START_VERSION:
        raise HealthResultError("start_request_version_invalid", 400)
    if value.get("explicit_storage_release") is not True:
        raise HealthResultError("storage_release_required", 403)
    if type(value.get("health_chain_input")) is not dict:
        raise HealthResultError("health_chain_input_invalid", 400)
    key = value.get("idempotency_key")
    if type(key) is not str or not _KEY.fullmatch(key):
        raise HealthResultError("idempotency_key_invalid", 400)
    for field in ("expected_input_digest", "expected_result_digest"):
        candidate = value.get(field)
        if type(candidate) is not str or not _DIGEST.fullmatch(candidate):
            raise HealthResultError(f"{field}_invalid", 400)
    try:
        actual = digest(value["health_chain_input"])
    except (TypeError, ValueError) as exc:
        raise HealthResultError("health_chain_input_unserializable", 400) from exc
    if actual != value["expected_input_digest"]:
        raise HealthResultError("input_digest_mismatch", 409)
    return value


def _verified(row: sqlite3.Row) -> dict:
    try:
        request = json.loads(row["input_json"])
        report = json.loads(row["report_json"])
        sources = request.get("sources") if type(request) is dict else None
        periods = request.get("periods") if type(request) is dict else None
        rows = report.get("rows") if type(report) is dict else None
        count = report.get("calculated_period_count") if type(report) is dict else None
        valid = (
            type(request) is dict and type(report) is dict
            and type(sources) is dict and type(periods) is list
            and type(rows) is list and count in HEALTH_PERIOD_CHAIN_HORIZONS
            and len(rows) == count == len(periods)
            and all(type(item) is dict and item.get("period") == index + 1 for index, item in enumerate(rows))
            and report.get("valid") is True
            and report.get("health_period_chain_calculated") is True
            and report.get("schema_version") == HEALTH_PERIOD_CHAIN_RESULT_VERSION
            and request.get("schema_version") == HEALTH_PERIOD_CHAIN_INPUT_VERSION
            and report.get("requested_period_count") == count
            and report.get("insurer_id") == request.get("insurer_id")
            and report.get("scenario_id") == sources.get("scenario_id")
            and report.get("variant_id") == sources.get("variant_id")
            and digest(request) == row["input_digest"]
            and digest(report) == row["result_digest"]
            and result_id_for(row["idempotency_key"], row["input_digest"]) == row["result_id"]
            and _record_digest(
                row["result_id"], row["idempotency_key"], row["input_digest"],
                row["result_digest"], row["stored_at"],
            ) == row["record_digest"]
        )
    except (TypeError, ValueError, KeyError, IndexError, UnicodeError):
        valid = False
    if not valid:
        raise HealthResultError("stored_health_result_corrupt", 409)
    return {
        "schema_version": HEALTH_RESULT_DELIVERY_VERSION,
        "status": "ok",
        "result_id": row["result_id"],
        "input_digest": row["input_digest"],
        "result_digest": row["result_digest"],
        "record_digest": row["record_digest"],
        "stored_at": row["stored_at"],
        "health_chain_input": request,
        "report": report,
        "storage_kind": "sqlite",
        "stored_result_verified": True,
        "historical_full_equality_claim": False,
    }


def get_health_result(db_path: Path, result_id: str) -> dict:
    if type(result_id) is not str or not _RESULT_ID.fullmatch(result_id):
        raise HealthResultError("result_id_invalid", 400)
    if not db_path.is_file():
        raise HealthResultError("health_result_not_found", 404)
    try:
        connection = sqlite3.connect(
            readonly_sqlite_uri(db_path, description="health result store"), uri=True,
        )
        connection.row_factory = sqlite3.Row
        try:
            row = connection.execute(
                "SELECT * FROM health_chain_results WHERE result_id = ?", (result_id,),
            ).fetchone()
        finally:
            connection.close()
    except MetadataImportError as exc:
        raise HealthResultError("health_result_store_unavailable", 503) from exc
    except sqlite3.Error as exc:
        if "no such table" in str(exc):
            raise HealthResultError("health_result_not_found", 404) from exc
        raise HealthResultError("health_result_store_unavailable", 503) from exc
    if row is None:
        raise HealthResultError("health_result_not_found", 404)
    return _verified(row)


def list_health_results(db_path: Path) -> dict:
    if not db_path.is_file():
        rows = []
    else:
        try:
            connection = sqlite3.connect(
                readonly_sqlite_uri(db_path, description="health result store"), uri=True,
            )
            connection.row_factory = sqlite3.Row
            try:
                rows = connection.execute(
                    "SELECT * FROM health_chain_results ORDER BY stored_at DESC, result_id LIMIT 100",
                ).fetchall()
            finally:
                connection.close()
        except MetadataImportError as exc:
            raise HealthResultError("health_result_store_unavailable", 503) from exc
        except sqlite3.Error as exc:
            if "no such table" in str(exc):
                rows = []
            else:
                raise HealthResultError("health_result_store_unavailable", 503) from exc
    results = []
    for row in rows:
        record = _verified(row)
        report = record["report"]
        results.append({
            "result_id": record["result_id"],
            "insurer_id": report["insurer_id"],
            "scenario_id": report["scenario_id"],
            "variant_id": report["variant_id"],
            "period_count": report["calculated_period_count"],
            "stored_at": record["stored_at"],
            "input_digest": record["input_digest"],
            "result_digest": record["result_digest"],
            "record_digest": record["record_digest"],
        })
    return {
        "schema_version": HEALTH_RESULT_DELIVERY_VERSION,
        "status": "ok", "results": results, "writes_performed": False,
    }


def replay_health_result(db_path: Path, request: dict) -> dict | None:
    if not db_path.is_file():
        return None
    try:
        connection = sqlite3.connect(
            readonly_sqlite_uri(db_path, description="health result store"), uri=True,
        )
        connection.row_factory = sqlite3.Row
        try:
            row = connection.execute(
                "SELECT * FROM health_chain_results WHERE idempotency_key = ?",
                (request["idempotency_key"],),
            ).fetchone()
        finally:
            connection.close()
    except MetadataImportError as exc:
        raise HealthResultError("health_result_store_unavailable", 503) from exc
    except sqlite3.Error as exc:
        if "no such table" in str(exc):
            return None
        raise HealthResultError("health_result_store_unavailable", 503) from exc
    if row is None:
        return None
    record = _verified(row)
    if (record["input_digest"] != request["expected_input_digest"]
            or record["result_digest"] != request["expected_result_digest"]):
        raise HealthResultError("idempotency_key_conflict", 409)
    return {**record, "replayed": True, "writes_performed": False}


def persist_health_result(db_path: Path, request: dict, report: dict) -> dict:
    if report.get("valid") is not True:
        raise HealthResultError("health_chain_invalid", 422)
    input_digest = digest(request["health_chain_input"])
    result_digest = digest(report)
    if input_digest != request["expected_input_digest"]:
        raise HealthResultError("input_digest_mismatch", 409)
    if result_digest != request["expected_result_digest"]:
        raise HealthResultError("result_digest_mismatch", 409)
    result_id = result_id_for(request["idempotency_key"], input_digest)
    stored_at = datetime.now(timezone.utc).isoformat()
    record_digest = _record_digest(
        result_id, request["idempotency_key"], input_digest, result_digest, stored_at,
    )
    try:
        connection = connect_metadata_db(db_path)
        try:
            connection.execute("PRAGMA busy_timeout = 5000")
            connection.execute(_SCHEMA)
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute(
                    "SELECT * FROM health_chain_results WHERE idempotency_key = ?",
                    (request["idempotency_key"],),
                ).fetchone()
                if row is not None:
                    record = _verified(row)
                    if (record["input_digest"] != input_digest
                            or record["result_digest"] != result_digest):
                        raise HealthResultError("idempotency_key_conflict", 409)
                    return {**record, "replayed": True, "writes_performed": False}
                connection.execute(
                    "INSERT INTO health_chain_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        result_id, request["idempotency_key"], input_digest,
                        result_digest, record_digest,
                        canonical_json(request["health_chain_input"]),
                        canonical_json(report), stored_at,
                    ),
                )
                row = connection.execute(
                    "SELECT * FROM health_chain_results WHERE result_id = ?", (result_id,),
                ).fetchone()
                record = _verified(row)
        finally:
            connection.close()
    except sqlite3.Error as exc:
        raise HealthResultError("health_result_store_unavailable", 503) from exc
    return {**record, "replayed": False, "writes_performed": True}


def contract_payload() -> dict[str, object]:
    base = "/api/accounting/health-period-chain"
    return {
        "schema_version": HEALTH_RESULT_DELIVERY_VERSION,
        "start_request_schema_version": HEALTH_RESULT_START_VERSION,
        "preview_endpoint": f"{base}/preview",
        "start_endpoint": f"{base}/start",
        "results_endpoint": f"{base}/results",
        "result_endpoint": f"{base}/result/{{result_id}}",
        "csv_endpoint": f"{base}/result/{{result_id}}.csv",
        "json_endpoint": f"{base}/result/{{result_id}}.json",
        "xlsx_endpoint": f"{base}/result/{{result_id}}.xlsx",
        "timeout_seconds": HEALTH_API_TIMEOUT_SECONDS,
        "explicit_storage_release_required": True,
        "expected_input_and_result_digests_required": True,
        "export_if_match_required": True,
        "export_amount_cells": "canonical_text",
        "historical_full_equality_claim": False,
    }
