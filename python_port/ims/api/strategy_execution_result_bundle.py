"""Read-only, in-memory exports of the released 100-period effect probe."""

from __future__ import annotations

import csv
from hashlib import sha256
from io import BytesIO, StringIO
import json
import re
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from ims.api.strategy_execution_period_chain_extended_probe import (
    EXTENDED_PROBE_RESULT_VERSION,
)


BUNDLE_VERSION = "ims.strategy-execution-result-bundle.v1"
METRICS_VERSION = "ims.strategy-execution-period-metrics.v1"
COLUMNS = (
    "chain_id",
    "content_digest",
    "effect_digest",
    "period",
    "global_period",
    "stage",
    "actor_kind",
    "actor_id",
    "sector_index",
    "metric",
    "value_type",
    "value",
)
_WORKER_FIELDS = frozenset(
    {
        "schema_version", "status", "period_count", "period_chain_identity",
        "period_effects", "transition_effects", "runner_invocation_count",
        "carryover_invocation_count", "candidate_reverified_count",
        "prefix_equal", "result_persisted", "partial_result_returned",
        "simulation_performed", "historical_full_equality_claim",
    }
)
_DECORATION_FIELDS = frozenset(
    {
        "effect_digest", "prefix_proof", "peak_worker_rss_bytes",
        "chain_payload_bytes", "result_payload_bytes", "wall_elapsed_seconds",
    }
)
_MAX_ROWS = 50_000
_MAX_BUNDLE_BYTES = 64 * 1024 * 1024
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
_FIELD = re.compile(r"[a-z][a-z0-9_]*\Z")
_CHAIN_ID = re.compile(r"strategy-period-chain-[0-9a-f]{24}\Z")


class ResultBundleError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def _digest(value: bytes) -> str:
    return "sha256:" + sha256(value).hexdigest()


def _verified_source(result: object) -> tuple[dict, list, dict, dict]:
    if not isinstance(result, dict) or set(result) != _WORKER_FIELDS | _DECORATION_FIELDS:
        raise ResultBundleError("result_invalid", "Vollstaendiges PR149-Ergebnis erforderlich")
    worker = {key: result[key] for key in _WORKER_FIELDS}
    try:
        raw = _canonical(worker)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ResultBundleError("result_invalid", "Ergebnis ist nicht kanonisch") from exc
    if (
        result["schema_version"] != EXTENDED_PROBE_RESULT_VERSION
        or result["status"] != "ok"
        or type(result["period_count"]) is not int
        or result["period_count"] != 100
        or result["prefix_equal"] is not True
        or result["result_persisted"] is not False
        or result["partial_result_returned"] is not False
        or result["effect_digest"] != _digest(raw)
        or result["result_payload_bytes"] != len(raw)
        or not isinstance(result["prefix_proof"], dict)
        or result["prefix_proof"].get("canonical_json_byte_equal") is not True
    ):
        raise ResultBundleError("result_invalid", "100-Perioden-Nachweis weicht ab")
    identity = result["period_chain_identity"]
    effects = result["period_effects"]
    transitions = result["transition_effects"]
    if (
        not isinstance(identity, dict)
        or not isinstance(identity.get("chain_id"), str)
        or not _CHAIN_ID.fullmatch(identity["chain_id"])
        or not isinstance(identity.get("content_digest"), str)
        or not _DIGEST.fullmatch(identity["content_digest"])
        or not isinstance(effects, list)
        or len(effects) != 100
        or not isinstance(transitions, list)
        or len(transitions) != 99
    ):
        raise ResultBundleError("result_invalid", "Kettenidentitaet oder Perioden fehlen")
    return identity, effects, transitions, result


def _scalar(value: object) -> tuple[str, str]:
    if value is None:
        return "null", "-"
    if type(value) is bool:
        return "boolean", "true" if value else "false"
    if type(value) is int:
        return "integer", str(value)
    if type(value) is float:
        try:
            return "number", _canonical(value).decode("ascii")
        except ValueError as exc:
            raise ResultBundleError("metric_invalid", "Nichtendliche Kennzahl") from exc
    raise ResultBundleError("metric_invalid", "Nur vorhandene skalare Kennzahlen erlaubt")


def _rows(identity: dict, effects: list, digest: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    origin = {
        "chain_id": identity["chain_id"],
        "content_digest": identity["content_digest"],
        "effect_digest": digest,
    }

    def add(period: int, global_period: int, stage: str, kind: str, actor_id: str,
            sector: str, metric: str, value: object) -> None:
        if not _FIELD.fullmatch(metric.removeprefix("vu.").removeprefix("vn.")):
            raise ResultBundleError("metric_invalid", "Ungueltiger Kennzahlenname")
        value_type, rendered = _scalar(value)
        rows.append({
            **origin, "period": str(period), "global_period": str(global_period),
            "stage": stage, "actor_kind": kind, "actor_id": actor_id or "-",
            "sector_index": sector or "-", "metric": metric,
            "value_type": value_type, "value": rendered,
        })
        if len(rows) > _MAX_ROWS:
            raise ResultBundleError("result_too_large", "Zu viele Kennzahlenzeilen")

    for index, effect in enumerate(effects, 1):
        if (
            not isinstance(effect, dict)
            or type(effect.get("period")) is not int
            or effect["period"] != index
            or type(effect.get("global_period")) is not int
        ):
            raise ResultBundleError("result_invalid", "Periodenfolge weicht ab")
        global_period = effect["global_period"]
        applications = effect.get("applications")
        if not isinstance(applications, dict):
            raise ResultBundleError("result_invalid", "Regelanwendungen fehlen")
        for name in sorted(applications):
            value = applications[name]
            if isinstance(value, dict):
                for rule in sorted(value):
                    add(index, global_period, "applications", "runner", "", "",
                        f"{name}.{rule}", value[rule])
            else:
                add(index, global_period, "applications", "runner", "", "",
                    name, value)
        for stage in ("state_before", "state_after"):
            state = effect.get(stage)
            if not isinstance(state, dict) or set(state) != {"insurers", "policyholders"}:
                raise ResultBundleError("result_invalid", "Periodenzustand fehlt")
            for collection, id_field in (("insurers", "insurer_id"),
                                         ("policyholders", "policyholder_id")):
                actors = state[collection]
                if not isinstance(actors, list):
                    raise ResultBundleError("result_invalid", "Akteurszustand fehlt")
                seen: set[int] = set()
                for actor in actors:
                    if not isinstance(actor, dict) or type(actor.get(id_field)) is not int:
                        raise ResultBundleError("result_invalid", "Akteurs-ID fehlt")
                    actor_id = actor[id_field]
                    if actor_id in seen:
                        raise ResultBundleError("result_invalid", "Doppelte Akteurs-ID")
                    seen.add(actor_id)
                    for metric in sorted(set(actor) - {id_field}):
                        value = actor[metric]
                        if isinstance(value, list):
                            for sector, item in enumerate(value):
                                add(index, global_period, stage, collection, str(actor_id),
                                    str(sector), metric, item)
                        else:
                            add(index, global_period, stage, collection, str(actor_id),
                                "", metric, value)
    return rows


def _csv_bytes(rows: list[dict[str, str]]) -> bytes:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def _xlsx_bytes(rows: list[dict[str, str]]) -> bytes:
    from openpyxl import Workbook
    from openpyxl.cell import WriteOnlyCell

    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet("Kennzahlen")
    sheet.append(COLUMNS)
    for row in rows:
        cells = []
        for name in COLUMNS:
            cell = WriteOnlyCell(sheet, value=row[name])
            cell.data_type = "s"  # All canonical values remain text, never formulas.
            cells.append(cell)
        sheet.append(cells)
    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()


def build_result_bundle(result: object) -> bytes:
    """Build one atomic download; no filesystem writes or result persistence."""

    identity, effects, _, source = _verified_source(result)
    rows = _rows(identity, effects, source["effect_digest"])
    try:
        files = {
            "ergebnis.json": _canonical({
                "schema_version": METRICS_VERSION,
                "columns": list(COLUMNS),
                "rows": rows,
                "source_result": source,
            }),
            "kennzahlen.csv": _csv_bytes(rows),
            "kennzahlen.xlsx": _xlsx_bytes(rows),
        }
    except (TypeError, ValueError, OverflowError) as exc:
        raise ResultBundleError("result_invalid", "Exportdaten sind ungueltig") from exc
    if sum(map(len, files.values())) > _MAX_BUNDLE_BYTES:
        raise ResultBundleError("result_too_large", "Export ueberschreitet 64 MiB")
    manifest = {
        "schema_version": BUNDLE_VERSION,
        "period_count": 100,
        "row_count": len(rows),
        "columns": list(COLUMNS),
        "chain_id": identity["chain_id"],
        "content_digest": identity["content_digest"],
        "effect_digest": source["effect_digest"],
        "result_persisted": False,
        "historical_full_equality_claim": False,
        "files": {name: {"sha256": _digest(data), "byte_count": len(data)}
                  for name, data in files.items()},
    }
    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in (("manifest.json", _canonical(manifest)), *files.items()):
            entry = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, data)
    return stream.getvalue()
