"""Atomic, explicit 100-context workshop assembly for the existing runner."""

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_SCHEMA,
    verify_strategy_execution_candidate_payload,
)
from ims.api.strategy_execution_period_chain_build import build_strategy_execution_period_chain
from ims.api.strategy_execution_period_chain_store import STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_SCHEMA
from ims.strategies.execution_candidate_build import (
    StrategyExecutionDeclaredProfileDefinition,
    build_strategy_execution_candidate,
)

INPUT_VERSION = "ims.guided-period-chain-input.v1"
RESULT_VERSION = "ims.guided-period-chain-build.v1"
SEED_POLICY = "sha256-explicit-period-channel-v1"
_FIELDS = {"schema_version", "scenario_id", "variant_id", "seed", "seed_policy", "run_index", "source_note", "period_contexts", "transitions"}
_ROOT = Path(__file__).resolve().parents[1] / "strategies" / "profiles"
_BUNDLE_SCHEMA = """CREATE TABLE IF NOT EXISTS guided_period_chain_bundles (
bundle_id TEXT PRIMARY KEY, content_digest TEXT NOT NULL UNIQUE,
stored_at TEXT NOT NULL, source_input_json TEXT NOT NULL, result_json TEXT NOT NULL)"""


class GuidedChainError(ValueError):
    def __init__(self, code: str, message: str, path: str = "$") -> None:
        super().__init__(message)
        self.code, self.path = code, path


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":"))


def content_digest(value: object) -> str:
    return "sha256:" + sha256(canonical(value).encode("ascii")).hexdigest()


def failed(exc: GuidedChainError) -> dict[str, object]:
    return {"schema_version": RESULT_VERSION, "valid": False, "issues": [{"code": exc.code, "path": exc.path, "message": str(exc)}],
            "content_digest": None, "chains": [], "candidate_count": 0, "partial_chain_returned": False,
            "writes_performed": False, "runner_invocation_performed": False}


def _integer(value: object, name: str, maximum: int) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise GuidedChainError("integer_invalid", f"{name}: Ganzzahl zwischen 0 und {maximum} erforderlich", f"$.{name}")
    return value


def workshop_input(seed: int, run_index: int) -> dict[str, object]:
    """Declared synthetic preset; each period/channel derived independently."""
    _integer(seed, "seed", 2**31 - 1)
    _integer(run_index, "run_index", 0)
    template = json.loads((_ROOT / "guided_candidate_template_v1.json").read_text(encoding="utf-8"))
    ground = json.loads((_ROOT / "strategy_execution_candidate_profile_v1.json").read_text(encoding="utf-8"))
    periods = []
    for period in range(1, 101):
        def number(channel: str) -> int:
            return int.from_bytes(sha256(f"{SEED_POLICY}:{seed}:{period}:{channel}".encode("ascii")).digest()[:4], "big")
        def draw(channel: str) -> float:
            return (number(channel) % 1_000_000) / 1_000_000
        profile, candidate = deepcopy(ground), deepcopy(template)
        profile["period"] = period
        profile["context"].update(period=period, max_periods=100, run_index=run_index, rng_seed=number("context"))
        for field in ("snapshot_context", "vu_state_provenance", "scenario_profile_reference", "vn_process_input"):
            candidate[field]["period"] = period
        candidate["snapshot_context"]["entries"][0]["values"]["random_draws"] = [draw(f"vu1:{i}") for i in range(4)]
        candidate["snapshot_context"]["entries"][1]["values"]["draws"]["insurer_choice_draws"] = [draw(f"vn1:choice:{i}") for i in range(2)]
        damage_draws = candidate["vn_process_input"]["damage_settlement_snapshots"][0]["draws"]
        damage_draws["trigger_draws"] = [2 * draw(f"vn1:trigger:{i}") - 1 for i in range(2)]
        damage_draws["amount_draws"] = [2 * draw(f"vn1:amount:{i}") - 1 for i in range(2)]
        if period == 1:
            candidate["snapshot_context"]["entries"][1]["values"]["initial_decisions"] = [
                {"sector_index": i, "insured": False, "insurer_id": None} for i in range(2)]
        periods.append({"period": period, "profile": profile, "candidate_input": candidate})
    return {"schema_version": INPUT_VERSION, "scenario_id": "declared-management-100", "variant_id": "baseline",
            "seed": seed, "seed_policy": SEED_POLICY, "run_index": run_index,
            "source_note": "Deklarierter synthetischer Vdefmd6-Workshop: ein VU, ein VN, zwei anonyme historische Positionen. Keine Kfz-/Sach-Zuordnung. Alle 100 Kontexte und Zufallswerte sind ausdrücklich enthalten und änderbar.",
            "period_contexts": periods, "transitions": [{"from_period": i, "to_period": i + 1, "carry_forward_vu_state": True, "carry_forward_vn_state": True} for i in range(1, 100)]}


@dataclass(frozen=True)
class BuiltGuidedChain:
    source: dict
    result: dict
    candidates: tuple[dict, ...]


def build(value: object) -> BuiltGuidedChain:
    if not isinstance(value, dict) or set(value) != _FIELDS or value.get("schema_version") != INPUT_VERSION:
        raise GuidedChainError("contract_invalid", "Vollständiger geführter Quellenvertrag v1 erforderlich")
    source = deepcopy(value)
    _integer(source["seed"], "seed", 2**31 - 1)
    _integer(source["run_index"], "run_index", 0)
    if source["seed_policy"] != SEED_POLICY:
        raise GuidedChainError("seed_policy_invalid", "Explizite Seed-Policy nicht unterstützt")
    for key in ("scenario_id", "variant_id", "source_note"):
        text = source[key]
        if not isinstance(text, str) or not text.strip() or len(text) > (2000 if key == "source_note" else 80) or not text.isprintable():
            raise GuidedChainError("text_invalid", f"{key}: begrenzter eindeutiger Text erforderlich", f"$.{key}")
    contexts = source["period_contexts"]
    if not isinstance(contexts, list) or len(contexts) != 100:
        raise GuidedChainError("context_count_invalid", "Genau 100 vollständige Periodenkontexte erforderlich", "$.period_contexts")
    transitions = source["transitions"]
    if not isinstance(transitions, list) or len(transitions) != 99:
        raise GuidedChainError("transition_count_invalid", "Genau 99 Übergänge erforderlich", "$.transitions")
    try:
        payload_size = len(canonical(source).encode("ascii"))
    except (ValueError, TypeError, OverflowError) as exc:
        raise GuidedChainError("source_not_canonical", "Quellenvertrag enthält ungültige JSON-Zahlen oder Werte") from exc
    if payload_size > 16 * 1024 * 1024:
        raise GuidedChainError("payload_limit_exceeded", "Quellenvertrag überschreitet 16 MiB")
    # All horizons are freshly materialized. Only max_periods differs in the
    # ground context; 1–5 have exactly the same inputs, seeds and actors.
    candidates, chains = {}, []
    for horizon in (2, 5, 100):
        references, payloads = [], {}
        for period, row in enumerate(contexts[:horizon], 1):
            path = f"$.period_contexts[{period - 1}]"
            if not isinstance(row, dict) or set(row) != {"period", "profile", "candidate_input"} or type(row["period"]) is not int or row["period"] != period:
                raise GuidedChainError("period_order_invalid", "Kontexte müssen lückenlos bei 1 beginnen", path)
            profile, candidate_input = deepcopy(row["profile"]), deepcopy(row["candidate_input"])
            if not isinstance(profile, dict) or not isinstance(profile.get("context"), dict) or not isinstance(candidate_input, dict):
                raise GuidedChainError("context_invalid", "Profil und Kandidateneingabe fehlen", path)
            profile_id = profile.get("profile_id")
            if not isinstance(profile_id, str) or not profile_id.strip():
                raise GuidedChainError("profile_identity_invalid", "Eindeutige textuelle Profil-ID erforderlich", path + ".profile.profile_id")
            context = profile["context"]
            if context.get("period") != period or context.get("max_periods") != 100 or context.get("run_index") != source["run_index"]:
                raise GuidedChainError("context_identity_mismatch", "Perioden-, Horizont- oder Laufkontext stimmt nicht überein", path)
            if not isinstance(profile.get("insurers"), list) or not isinstance(profile.get("policyholders"), list):
                raise GuidedChainError("population_invalid", "VU- und VN-Listen erforderlich", path)
            if len(profile["insurers"]) > 25 or len(profile["policyholders"]) > 200:
                raise GuidedChainError("actor_limit_exceeded", "Workshopgrenze: 25 VU / 200 VN", path)
            context["max_periods"] = horizon
            built = build_strategy_execution_candidate(candidate_input, profiles={profile_id: StrategyExecutionDeclaredProfileDefinition(profile_id=profile_id, payload=profile)}, trusted_profile_root=_ROOT)
            if not built.build_complete:
                issue = built.issues[0]
                raise GuidedChainError(issue.code, f"Periode {period}: {issue.message}", path + issue.path.removeprefix("$"))
            payload = built.candidate.to_dict()
            verified = verify_strategy_execution_candidate_payload(payload, stored_at="")
            payloads[verified.candidate_id] = payload
            candidates[verified.candidate_id] = payload
            references.append({"candidate_id": verified.candidate_id, "content_digest": verified.content_digest, "period": period})
        chain_input = {"schema_version": "ims.strategy-execution-period-chain-input.v1", "period_chain_schema_version": "ims.strategy-execution-period-chain.v1", "candidate_schema_version": "ims.strategy-execution-candidate.v1", "base_model": "Vdefmd6", "scope": "contiguous_local_period_chain_input", "run_index": source["run_index"], "max_periods": horizon, "period_candidates": references, "transitions": deepcopy(transitions[:horizon - 1])}
        chain = build_strategy_execution_period_chain(chain_input, db_path="unused-pure-builder", candidate_payloads=payloads)
        if not chain.build_complete:
            issue = chain.issues[0]
            raise GuidedChainError(issue.code, issue.message, issue.path)
        chains.append({"period_count": horizon, "chain_id": chain.chain.chain_id, "content_digest": chain.chain.content_digest, "period_chain_input": chain_input, "period_chain": chain.chain.to_dict()})
    digest = content_digest({"source_input": source, "chains": chains})
    result = {"schema_version": RESULT_VERSION, "valid": True, "issues": [], "bundle_id": "guided-chain-" + digest[-64:][:24], "content_digest": digest, "source_input_digest": content_digest(source), "chains": chains, "candidate_count": len(candidates), "candidate_reverified_count": len(candidates), "period_context_count": 100, "seed_policy": SEED_POLICY, "partial_chain_returned": False, "writes_performed": False, "runner_invocation_performed": False, "historical_full_equality_claim": False}
    return BuiltGuidedChain(source, result, tuple(candidates.values()))


def store(value: object, *, db_path: Path | str) -> dict:
    fields = {"schema_version", "source_input", "expected_content_digest", "stored_at", "explicit_storage_release"}
    if not isinstance(value, dict) or set(value) != fields or value.get("schema_version") != "ims.guided-period-chain-store-request.v1" or value.get("explicit_storage_release") is not True:
        raise GuidedChainError("storage_release_required", "Ausdrückliche unveränderliche Speicherfreigabe erforderlich")
    timestamp = value["stored_at"]
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise GuidedChainError("timestamp_invalid", "Zeitpunkt mit Zeitzone erforderlich")
    built = build(value["source_input"])
    if built.result["content_digest"] != value["expected_content_digest"]:
        raise GuidedChainError("digest_mismatch", "Neu gebauter Nachweis weicht von der Freigabe ab")
    path = Path(db_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    replayed = False
    try:
        connection.execute("BEGIN IMMEDIATE")
        for schema in (STRATEGY_EXECUTION_CANDIDATE_STORE_SCHEMA, STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_SCHEMA, _BUNDLE_SCHEMA):
            connection.execute(schema)
        prior = connection.execute("SELECT * FROM guided_period_chain_bundles WHERE bundle_id=?", (built.result["bundle_id"],)).fetchone()
        if prior is not None:
            if prior["content_digest"] != built.result["content_digest"] or prior["source_input_json"] != canonical(built.source) or prior["result_json"] != canonical(built.result):
                raise GuidedChainError("immutable_bundle_conflict", "Vorhandenes Bündel hat abweichenden Inhalt")
            replayed = True
        # Replays also verify every candidate and chain, never silently repair.
        for payload in built.candidates:
            record = verify_strategy_execution_candidate_payload(payload, stored_at=timestamp)
            row = connection.execute("SELECT * FROM strategy_execution_candidates WHERE candidate_id=?", (record.candidate_id,)).fetchone()
            expected = (record.candidate_id, record.candidate_schema_version, record.draft_id, record.period, record.profile_id, record.profile_content_digest, record.content_digest)
            if row is not None:
                actual = tuple(row[k] for k in ("candidate_id", "candidate_schema_version", "draft_id", "period", "profile_id", "profile_content_digest", "content_digest"))
                if actual != expected or canonical(json.loads(row["candidate_payload_json"])) != canonical(payload):
                    raise GuidedChainError("immutable_candidate_conflict", "Vorhandener Kandidat hat abweichenden Inhalt")
            elif replayed:
                raise GuidedChainError("stored_candidate_missing", "Unveränderliches Bündel ist unvollständig")
            else:
                connection.execute("INSERT INTO strategy_execution_candidates VALUES (?,?,?,?,?,?,?,?,?)", (*expected, timestamp, canonical(payload)))
        for entry in built.result["chains"]:
            payload = entry["period_chain"]
            h = payload["horizon"]
            expected = (entry["chain_id"], payload["schema_version"], h["first_period"], h["last_period"], h["period_count"], h["run_index"], h["max_periods"], entry["content_digest"])
            row = connection.execute("SELECT * FROM strategy_execution_period_chains WHERE chain_id=?", (entry["chain_id"],)).fetchone()
            if row is not None:
                actual = tuple(row[k] for k in ("chain_id", "chain_schema_version", "first_period", "last_period", "period_count", "run_index", "max_periods", "content_digest"))
                if actual != expected or canonical(json.loads(row["chain_payload_json"])) != canonical(payload):
                    raise GuidedChainError("immutable_chain_conflict", "Vorhandene Kette hat abweichenden Inhalt")
            elif replayed:
                raise GuidedChainError("stored_chain_missing", "Unveränderliches Bündel ist unvollständig")
            else:
                connection.execute("INSERT INTO strategy_execution_period_chains VALUES (?,?,?,?,?,?,?,?,?,?)", (*expected, timestamp, canonical(payload)))
        if not replayed:
            connection.execute("INSERT INTO guided_period_chain_bundles VALUES (?,?,?,?,?)", (built.result["bundle_id"], built.result["content_digest"], timestamp, canonical(built.source), canonical(built.result)))
        connection.commit()
    except (sqlite3.Error, ValueError, TypeError) as exc:
        connection.rollback()
        if isinstance(exc, GuidedChainError):
            raise
        raise GuidedChainError("storage_failed", f"Atomare Speicherung fehlgeschlagen: {exc}") from exc
    finally:
        connection.close()
    return {**deepcopy(built.result), "stored": True, "replayed": replayed, "writes_performed": not replayed, "all_candidate_digests_verified": True, "all_chain_digests_verified": True}
