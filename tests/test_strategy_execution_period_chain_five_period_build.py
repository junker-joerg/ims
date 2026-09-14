from copy import deepcopy
from dataclasses import replace
import importlib
import json
import sqlite3

from ims.api.strategy_execution_period_chain_build import (
    StrategyExecutionPeriodChain,
    build_strategy_execution_period_chain,
    calculate_strategy_execution_period_chain_content_digest,
    strategy_execution_period_chain_id_from_digest,
)
from ims.api.strategy_execution_period_chain_five_period_build import (
    FIVE_PERIOD_CHAIN_PERIOD_COUNT,
    FIVE_PERIOD_CHAIN_TRANSITION_COUNT,
    STRATEGY_EXECUTION_FIVE_PERIOD_CHAIN_BUILD_CONTRACT_VERSION,
    STRATEGY_EXECUTION_FIVE_PERIOD_CHAIN_BUILD_VERSION,
    build_strategy_execution_five_period_chain,
    strategy_execution_five_period_chain_build_contract_payload,
)
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
)


def _issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_builds_deterministic_canonical_five_period_chain(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = persist_chain_candidates(
        db_path,
        tmp_path,
        max_periods=FIVE_PERIOD_CHAIN_PERIOD_COUNT,
    )
    request = chain_input(
        references,
        max_periods=FIVE_PERIOD_CHAIN_PERIOD_COUNT,
    )

    first = build_strategy_execution_five_period_chain(request, db_path=db_path)
    second = build_strategy_execution_five_period_chain(
        deepcopy(request),
        db_path=db_path,
    )

    assert first.schema_version == STRATEGY_EXECUTION_FIVE_PERIOD_CHAIN_BUILD_VERSION
    assert first.build_complete is True
    assert first.to_dict() == second.to_dict()
    assert first.chain is not None
    chain = first.chain.to_dict()
    assert chain["horizon"] == {
        "first_period": 1,
        "last_period": 5,
        "period_count": 5,
        "run_index": 7,
        "max_periods": 5,
    }
    assert chain["period_candidates"] == references
    assert len(chain["transitions"]) == FIVE_PERIOD_CHAIN_TRANSITION_COUNT
    assert [
        (item["from_period"], item["to_period"])
        for item in chain["transitions"]
    ] == [(1, 2), (2, 3), (3, 4), (4, 5)]
    assert first.chain.content_digest == (
        calculate_strategy_execution_period_chain_content_digest(
            sections=first.chain.sections
        )
    )
    assert first.chain.chain_id == strategy_execution_period_chain_id_from_digest(
        first.chain.content_digest
    )
    payload = first.to_dict()
    assert payload["canonical_chain_validated"] is True
    assert payload["resolved_candidate_count"] == 5
    assert payload["period_chain_persisted"] is False
    assert payload["execution_performed"] is False
    assert payload["next_gate"] == "PR146"


def test_rejects_other_horizon_before_candidate_resolution(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = persist_chain_candidates(db_path, tmp_path, max_periods=2)
    request = chain_input(references, max_periods=2)
    module = importlib.import_module(
        "ims.api.strategy_execution_period_chain_five_period_build"
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(f"generic build invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(module, "build_strategy_execution_period_chain", fail_if_called)

    report = build_strategy_execution_five_period_chain(request, db_path=db_path)

    assert report.build_complete is False
    assert report.input_validated is False
    assert _issue_codes(report) == {"exact_five_period_horizon_required"}
    assert report.to_dict()["period_chain"] is None


def test_tampered_fifth_candidate_blocks_complete_chain(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = persist_chain_candidates(db_path, tmp_path, max_periods=5)
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT candidate_payload_json FROM strategy_execution_candidates "
            "WHERE candidate_id = ?",
            (references[4]["candidate_id"],),
        ).fetchone()
        assert row is not None
        payload = json.loads(row[0])
        payload["source_documents"]["assignment_draft"]["label"] = "veraendert"
        connection.execute(
            "UPDATE strategy_execution_candidates SET candidate_payload_json = ? "
            "WHERE candidate_id = ?",
            (json.dumps(payload), references[4]["candidate_id"]),
        )

    report = build_strategy_execution_five_period_chain(
        chain_input(references, max_periods=5),
        db_path=db_path,
    )

    assert report.build_complete is False
    assert "candidate_digest_verification_failed" in _issue_codes(report)
    assert report.to_dict()["period_chain"] is None
    assert report.to_dict()["partial_chain_returned"] is False


def test_post_build_canonical_validation_suppresses_tampered_chain(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = persist_chain_candidates(db_path, tmp_path, max_periods=5)
    request = chain_input(references, max_periods=5)
    generic = build_strategy_execution_period_chain(request, db_path=db_path)
    assert generic.chain is not None
    sections = deepcopy(generic.chain.sections)
    sections["transitions"][0]["to_period"] = 3
    tampered_chain = StrategyExecutionPeriodChain(
        chain_id=generic.chain.chain_id,
        content_digest=generic.chain.content_digest,
        sections=sections,
    )
    module = importlib.import_module(
        "ims.api.strategy_execution_period_chain_five_period_build"
    )
    monkeypatch.setattr(
        module,
        "build_strategy_execution_period_chain",
        lambda value, *, db_path: replace(generic, chain=tampered_chain),
    )

    report = build_strategy_execution_five_period_chain(request, db_path=db_path)

    assert report.build_complete is False
    assert report.canonical_chain_validated is False
    assert "five_period_transitions_not_canonical" in _issue_codes(report)
    assert "five_period_chain_digest_mismatch" in _issue_codes(report)
    assert report.to_dict()["period_chain"] is None


def test_five_period_build_is_read_only_and_does_not_invoke_runner(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = persist_chain_candidates(db_path, tmp_path, max_periods=5)
    vu_runner = importlib.import_module("ims.engine.vu_rule_runner")
    vn_runner = importlib.import_module("ims.engine.vn_rule_runner")
    period_runner = importlib.import_module("ims.engine.explicit_period_runner")

    def fail_if_called(*args, **kwargs):
        raise AssertionError(f"execution invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(vu_runner, "apply_vu_foreign_info_carryover", fail_if_called)
    monkeypatch.setattr(vn_runner, "apply_vn_state_carryover", fail_if_called)
    monkeypatch.setattr(period_runner, "run_loaded_explicit_period", fail_if_called)
    before = db_path.read_bytes()

    report = build_strategy_execution_five_period_chain(
        chain_input(references, max_periods=5),
        db_path=db_path,
    )
    payload = report.to_dict()

    assert report.build_complete is True
    assert db_path.read_bytes() == before
    assert payload["writes_performed"] is False
    assert payload["carryover_invocation_performed"] is False
    assert payload["runner_invocation_performed"] is False
    assert payload["simulation_performed"] is False


def test_five_period_build_contract_opens_only_atomic_ephemeral_build() -> None:
    payload = strategy_execution_five_period_chain_build_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_FIVE_PERIOD_CHAIN_BUILD_CONTRACT_VERSION
    )
    assert payload["required_period_count"] == 5
    assert payload["required_transition_count"] == 4
    assert payload["required_periods"] == [1, 2, 3, 4, 5]
    assert payload["atomic_validation_enabled"] is True
    assert payload["five_period_candidate_validation_enabled"] is True
    assert payload["five_period_chain_build_enabled"] is True
    assert payload["partial_chain_allowed"] is False
    assert payload["period_chain_persistence_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR146"
