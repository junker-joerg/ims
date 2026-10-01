from copy import deepcopy
import sqlite3

import pytest

from ims.api.guided_period_chain import GuidedChainError, build, store, workshop_input
from ims.api.strategy_execution_period_chain_build import build_strategy_execution_period_chain
from ims.api.strategy_execution_period_chain_effect_probe import parse_strategy_execution_period_chain_effect_probe_request
from ims.api.strategy_execution_period_chain_effect_probe_start import start_strategy_execution_period_chain_effect_probe
from ims.api.strategy_execution_period_chain_five_period_effect_probe_start import parse_strategy_execution_five_period_effect_probe_start_request, start_strategy_execution_five_period_effect_probe
from ims.api.strategy_execution_period_chain_extended_probe import EXTENDED_PROBE_REQUEST_VERSION, parse_extended_probe_request, run_extended_probe


def storage_request(source):
    return {"schema_version": "ims.guided-period-chain-store-request.v1", "source_input": source, "expected_content_digest": build(source).result["content_digest"], "stored_at": "2026-10-01T09:00:00+02:00", "explicit_storage_release": True}


def release(chain, key):
    return {"schema_version": "ims.strategy-execution-period-chain-run-control-request.v1", "chain_id": chain["chain_id"], "expected_content_digest": chain["content_digest"], "idempotency_key": key, "explicit_run_control_release": True, "released_by": "guided-workshop-test", "released_at": "2026-10-01T07:01:00Z", "release_reason": "Explizite Referenz- und 100-Perioden-Abnahme"}


def test_fresh_atomic_build_replay_and_existing_chain_verification(tmp_path):
    source = workshop_input(1300, 0)
    before = deepcopy(source)
    built = build(source)
    assert source == before
    assert built.result == build(source).result
    assert built.result["candidate_count"] == 107
    assert built.result["writes_performed"] is False
    path = tmp_path / "metadata.sqlite"
    first = store(storage_request(source), db_path=path)
    snapshot = path.read_bytes()
    second = store(storage_request(source), db_path=path)
    assert first["writes_performed"] and not second["writes_performed"] and second["replayed"]
    assert path.read_bytes() == snapshot
    for entry in built.result["chains"]:
        checked = build_strategy_execution_period_chain(entry["period_chain_input"], db_path=path)
        assert checked.chain.to_dict() == entry["period_chain"]
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT count(*) FROM strategy_execution_candidates").fetchone()[0] == 107
        assert db.execute("SELECT count(*) FROM strategy_execution_period_chains").fetchone()[0] == 3


@pytest.mark.parametrize("kind", ["late_context", "late_draw", "missing", "order", "cycle_transition", "seed_bool", "unknown", "population", "run_index", "profile_id"])
def test_invalid_contexts_never_create_database_or_partial_chain(tmp_path, kind):
    source = workshop_input(1300, 0)
    if kind == "late_context": source["period_contexts"][-1]["profile"]["context"]["period"] = 99
    if kind == "late_draw": source["period_contexts"][-1]["candidate_input"]["vn_process_input"]["damage_settlement_snapshots"][0]["draws"]["trigger_draws"] = [2, 3]
    if kind == "missing": source["period_contexts"].pop()
    if kind == "order": source["period_contexts"][10]["period"] = 1
    if kind == "cycle_transition": source["transitions"][-1]["to_period"] = 1
    if kind == "seed_bool": source["seed"] = True
    if kind == "unknown": source["unused"] = 1
    if kind == "population": source["period_contexts"][-1]["profile"]["insurers"][0]["entity_id"] = 2
    if kind == "run_index": source["run_index"] = 1
    if kind == "profile_id": source["period_contexts"][-1]["profile"]["profile_id"] = ["unhashable-id"]
    request = {"schema_version": "ims.guided-period-chain-store-request.v1", "source_input": source, "expected_content_digest": "sha256:" + "0" * 64, "stored_at": "2026-10-01T09:00:00Z", "explicit_storage_release": True}
    with pytest.raises(GuidedChainError):
        store(request, db_path=tmp_path / "must-not-exist.sqlite")
    assert not (tmp_path / "must-not-exist.sqlite").exists()


def test_changed_seed_and_immutable_conflict_rollback(tmp_path):
    a, b = workshop_input(1300, 0), workshop_input(1301, 0)
    assert a["period_contexts"][0]["profile"]["context"]["rng_seed"] != b["period_contexts"][0]["profile"]["context"]["rng_seed"]
    assert build(a).result["content_digest"] != build(b).result["content_digest"]
    path = tmp_path / "metadata.sqlite"
    stored = store(storage_request(a), db_path=path)
    id_ = stored["chains"][2]["period_chain_input"]["period_candidates"][-1]["candidate_id"]
    with sqlite3.connect(path) as db:
        db.execute("UPDATE strategy_execution_candidates SET content_digest='corrupt' WHERE candidate_id=?", (id_,))
    snapshot = path.read_bytes()
    with pytest.raises(GuidedChainError, match="abweichenden Inhalt"):
        store(storage_request(a), db_path=path)
    assert path.read_bytes() == snapshot


def test_generated_hundred_chain_runs_with_real_two_and_five_prefix_proofs(tmp_path):
    path = tmp_path / "metadata.sqlite"
    stored = store(storage_request(workshop_input(1300, 0)), db_path=path)
    two, five, hundred = stored["chains"]
    two_result = start_strategy_execution_period_chain_effect_probe(parse_strategy_execution_period_chain_effect_probe_request({"schema_version": "ims.strategy-execution-period-chain-effect-probe-request.v1", "release": release(two, "guided-two-001"), "explicit_two_period_effect_probe_execution": True}), db_path=path)
    two_ref = {"chain_id": two_result.record.chain_id, "expected_content_digest": two_result.record.content_digest, "expected_result_digest": two_result.record.result_digest}
    five_result = start_strategy_execution_five_period_effect_probe(parse_strategy_execution_five_period_effect_probe_start_request({"schema_version": "ims.strategy-execution-five-period-effect-probe-start-request.v1", "effect_probe_request": {"schema_version": "ims.strategy-execution-five-period-effect-probe-request.v1", "period_chain_input": five["period_chain_input"], "prefix_baseline": two_ref, "explicit_five_period_effect_probe_execution": True}, "release": release(five, "guided-five-001"), "explicit_five_period_effect_probe_start": True}), db_path=path)
    five_ref = {"chain_id": five_result.record.chain_id, "expected_content_digest": five_result.record.content_digest, "expected_result_digest": five_result.record.result_digest}
    snapshot = path.read_bytes()
    result = run_extended_probe(parse_extended_probe_request({"schema_version": EXTENDED_PROBE_REQUEST_VERSION, "period_chain_input": hundred["period_chain_input"], "five_period_baseline": five_ref, "release": release(hundred, "guided-hundred-001"), "explicit_extended_effect_probe_execution": True}), db_path=path)
    assert result["period_count"] == result["runner_invocation_count"] == 100
    assert result["candidate_reverified_count"] == 100
    assert result["prefix_equal"] and result["prefix_proof"]["canonical_json_byte_equal"]
    assert path.read_bytes() == snapshot
