from copy import deepcopy
from hashlib import sha256
import importlib
import json
import sqlite3

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_period_chain_build import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_CONTRACT_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_ID_PREFIX,
    build_strategy_execution_period_chain,
    calculate_strategy_execution_period_chain_content_digest,
    strategy_execution_period_chain_build_contract_payload,
    strategy_execution_period_chain_id_from_digest,
)
from ims.api.strategy_execution_period_chain_resolution import (
    StrategyExecutionPeriodChainResolutionReport,
    StrategyExecutionPeriodChainResolvedCandidate,
)
from ims.strategies import (
    strategy_execution_candidate_id_from_digest,
)
from tests.period_chain_test_support import (
    CHAIN_INPUT_FIXTURE,
    chain_input as _chain_input,
    persist_chain_candidates as _persist_chain_candidates,
)


def _issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_builds_deterministic_chain_with_independently_verified_digest(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    request = _chain_input(references)

    first = build_strategy_execution_period_chain(request, db_path=db_path)
    second = build_strategy_execution_period_chain(
        deepcopy(request),
        db_path=db_path,
    )

    assert first.schema_version == STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION
    assert first.build_complete is True
    assert first.to_dict() == second.to_dict()
    assert first.chain is not None
    chain = first.chain.to_dict()
    identity = chain["identity"]
    sections = {
        key: value
        for key, value in chain.items()
        if key not in {"schema_version", "mode", "base_model", "identity"}
    }
    basis = {
        "period_chain_schema_version": chain["schema_version"],
        "base_model": chain["base_model"],
        **sections,
    }
    encoded = json.dumps(
        basis,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    expected_digest = f"sha256:{sha256(encoded).hexdigest()}"

    assert identity["content_digest"] == expected_digest
    assert identity["chain_id"] == (
        f"{STRATEGY_EXECUTION_PERIOD_CHAIN_ID_PREFIX}"
        f"{expected_digest.removeprefix('sha256:')[:24]}"
    )
    assert calculate_strategy_execution_period_chain_content_digest(
        sections=sections
    ) == expected_digest
    assert strategy_execution_period_chain_id_from_digest(expected_digest) == (
        identity["chain_id"]
    )
    assert chain["horizon"] == {
        "first_period": 1,
        "last_period": 2,
        "period_count": 2,
        "run_index": 7,
        "max_periods": 2,
    }
    assert chain["period_candidates"] == references
    assert chain["provenance"]["chain_build_schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_VERSION
    )
    assert "execution_transition_records" not in chain["provenance"]
    assert "candidate" not in chain["period_candidates"][0]
    assert first.to_dict()["period_chain_persisted"] is False


def test_storage_metadata_is_excluded_from_chain_identity(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    request = _chain_input(references)
    before = build_strategy_execution_period_chain(request, db_path=db_path)
    assert before.chain is not None

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE strategy_execution_candidates SET stored_at = ?",
            ("2099-12-31T23:59:59Z",),
        )
    after = build_strategy_execution_period_chain(request, db_path=db_path)

    assert after.chain is not None
    assert after.chain.content_digest == before.chain.content_digest
    assert after.chain.chain_id == before.chain.chain_id


def test_explicit_transition_change_changes_complete_chain_digest(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    with_carryover = _chain_input(references)
    without_vu_carryover = deepcopy(with_carryover)
    without_vu_carryover["transitions"][0]["carry_forward_vu_state"] = False

    first = build_strategy_execution_period_chain(with_carryover, db_path=db_path)
    second = build_strategy_execution_period_chain(
        without_vu_carryover,
        db_path=db_path,
    )

    assert first.build_complete is True
    assert second.build_complete is True
    assert first.chain is not None
    assert second.chain is not None
    assert first.chain.content_digest != second.chain.content_digest
    assert first.chain.chain_id != second.chain.chain_id


def test_builds_complete_100_period_horizon_from_resolved_candidates(
    monkeypatch,
    tmp_path,
) -> None:
    build_module = importlib.import_module(
        "ims.api.strategy_execution_period_chain_build"
    )
    candidates = []
    references = []
    for period in range(1, 101):
        digest = f"sha256:{period:02x}{'0' * 62}"
        candidate_id = strategy_execution_candidate_id_from_digest(digest)
        references.append(
            {
                "candidate_id": candidate_id,
                "content_digest": digest,
                "period": period,
            }
        )
        candidates.append(
            StrategyExecutionPeriodChainResolvedCandidate(
                candidate_id=candidate_id,
                content_digest=digest,
                period=period,
                draft_id=f"draft-{period}",
                profile_id=f"profile-{period}",
                profile_content_digest=f"sha256:{'f' * 64}",
                context_run_index=7,
                context_max_periods=100,
                bav_id=1,
                insurer_ids=(1,),
                policyholder_ids=(1,),
            )
        )
    resolution = StrategyExecutionPeriodChainResolutionReport(
        input_validated=True,
        resolution_complete=True,
        digests_reverified=True,
        contexts_consistent=True,
        actor_identities_consistent=True,
        run_index=7,
        max_periods=100,
        expected_candidate_count=100,
        resolved_candidate_count=100,
        digest_verified_candidate_count=100,
        context_verified_candidate_count=100,
        candidates=tuple(candidates),
        issues=(),
    )
    monkeypatch.setattr(
        build_module,
        "resolve_strategy_execution_period_chain_input",
        lambda value, *, db_path: resolution,
    )
    request = json.loads(CHAIN_INPUT_FIXTURE.read_text(encoding="utf-8"))
    request["run_index"] = 7
    request["max_periods"] = 100
    request["period_candidates"] = references
    request["transitions"] = [
        {
            "from_period": period,
            "to_period": period + 1,
            "carry_forward_vu_state": True,
            "carry_forward_vn_state": True,
        }
        for period in range(1, 100)
    ]

    report = build_strategy_execution_period_chain(
        request,
        db_path=tmp_path / "not-used.sqlite",
    )

    assert report.build_complete is True
    assert report.chain is not None
    chain = report.chain.to_dict()
    assert chain["horizon"]["last_period"] == 100
    assert chain["horizon"]["period_count"] == 100
    assert len(chain["period_candidates"]) == 100
    assert len(chain["transitions"]) == 99


def test_invalid_input_stops_before_storage_and_returns_no_partial_chain(
    monkeypatch,
    tmp_path,
) -> None:
    resolution_module = importlib.import_module(
        "ims.api.strategy_execution_period_chain_resolution"
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(f"candidate store invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(
        resolution_module,
        "get_strategy_execution_candidate",
        fail_if_called,
    )
    request = json.loads(CHAIN_INPUT_FIXTURE.read_text(encoding="utf-8"))
    request["transitions"] = []

    report = build_strategy_execution_period_chain(
        request,
        db_path=tmp_path / "absent.sqlite",
    )
    payload = report.to_dict()

    assert report.build_complete is False
    assert report.input_validated is False
    assert "transition_count_mismatch" in _issue_codes(report)
    assert payload["period_chain"] is None
    assert payload["period_chain_digest_calculated"] is False
    assert payload["partial_chain_returned"] is False


def test_tampered_stored_candidate_blocks_chain_and_digest(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT candidate_payload_json FROM strategy_execution_candidates "
            "WHERE candidate_id = ?",
            (references[1]["candidate_id"],),
        ).fetchone()
        payload = json.loads(row[0])
        payload["source_documents"]["assignment_draft"]["label"] = "veraendert"
        connection.execute(
            "UPDATE strategy_execution_candidates SET candidate_payload_json = ? "
            "WHERE candidate_id = ?",
            (json.dumps(payload), references[1]["candidate_id"]),
        )

    report = build_strategy_execution_period_chain(
        _chain_input(references),
        db_path=db_path,
    )
    result = report.to_dict()

    assert report.build_complete is False
    assert "candidate_digest_verification_failed" in _issue_codes(report)
    assert result["period_chain"] is None
    assert result["period_chain_created"] is False
    assert result["period_chain_digest_calculated"] is False


def test_build_is_read_only_and_does_not_call_carryover_or_runner(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    vu_runner = importlib.import_module("ims.engine.vu_rule_runner")
    vn_runner = importlib.import_module("ims.engine.vn_rule_runner")
    period_runner = importlib.import_module("ims.engine.explicit_period_runner")

    def fail_if_called(*args, **kwargs):
        raise AssertionError(f"operation invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(vu_runner, "apply_vu_foreign_info_carryover", fail_if_called)
    monkeypatch.setattr(vn_runner, "apply_vn_state_carryover", fail_if_called)
    monkeypatch.setattr(period_runner, "run_loaded_explicit_period", fail_if_called)
    before = db_path.read_bytes()

    report = build_strategy_execution_period_chain(
        _chain_input(references),
        db_path=db_path,
    )
    payload = report.to_dict()

    assert report.build_complete is True
    assert db_path.read_bytes() == before
    assert payload["writes_performed"] is False
    assert payload["carryover_invocation_performed"] is False
    assert payload["runner_invocation_performed"] is False
    assert payload["simulation_performed"] is False


def test_build_contract_opens_only_ephemeral_chain_and_digest() -> None:
    payload = strategy_execution_period_chain_build_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_BUILD_CONTRACT_VERSION
    )
    assert payload["candidate_resolution_enabled"] is True
    assert payload["candidate_digest_reverification_enabled"] is True
    assert payload["period_chain_creation_enabled"] is True
    assert payload["period_chain_digest_enabled"] is True
    assert payload["partial_chain_allowed"] is False
    assert payload["candidate_payloads_embedded"] is False
    assert payload["digest"]["identity_fields_excluded"] == [
        "chain_id",
        "content_digest",
    ]
    assert payload["period_chain_persistence_enabled"] is False
    assert payload["carryover_invocation_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR139"


def test_build_api_uses_configured_store_and_enforces_methods(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    contract_endpoint = "/api/strategies/execution-period-chain-build-contract"
    build_endpoint = "/api/strategies/execution-period-chain-build"

    contract = client.get(contract_endpoint)
    response = client.post(build_endpoint, json=_chain_input(references))

    assert contract.status_code == 200
    assert contract.json()["candidate_payloads_embedded"] is False
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["period_chain_created"] is True
    assert payload["period_chain"]["identity"]["content_digest"].startswith(
        "sha256:"
    )
    assert payload["period_chain_persisted"] is False
    assert payload["execution_performed"] is False
    assert client.post(contract_endpoint, json={}).status_code == 405
    assert client.get(build_endpoint).status_code == 405
    assert client.put(build_endpoint, json={}).status_code == 405
    assert client.delete(build_endpoint).status_code == 405


def test_build_api_rejects_unconfigured_store_and_invalid_json(
    monkeypatch,
    tmp_path,
) -> None:
    endpoint = "/api/strategies/execution-period-chain-build"
    memory_client = TestClient(create_app(frontend_dist=tmp_path))

    unavailable = memory_client.post(endpoint, json={})

    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )
    assert unavailable.json()["period_chain"] is None
    assert unavailable.json()["writes_performed"] is False

    db_path = tmp_path / "metadata.sqlite"
    _persist_chain_candidates(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    sqlite_client = TestClient(create_app(frontend_dist=tmp_path))

    invalid_json = sqlite_client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )

    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert invalid_json.json()["period_chain"] is None
    assert invalid_json.json()["next_gate"] == "PR139"
