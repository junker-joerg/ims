from copy import deepcopy
import importlib
import json
from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_SCHEMA,
)
from ims.api.strategy_execution_period_chain_resolution import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_CONTRACT_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_VERSION,
    resolve_strategy_execution_period_chain_input,
    strategy_execution_period_chain_resolution_contract_payload,
)
from ims.strategies import (
    StrategyExecutionScenarioProfileDefinition,
    build_strategy_execution_candidate,
    calculate_strategy_execution_candidate_content_digest,
    strategy_execution_candidate_id_from_digest,
)


ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_INPUT_FIXTURE = (
    ROOT / "tests" / "fixtures" / "strategy_execution_candidate_input_v1.json"
)
CHAIN_INPUT_FIXTURE = (
    ROOT / "tests" / "fixtures" / "strategy_execution_period_chain_input_v1.json"
)
PROFILE_FIXTURE = (
    ROOT
    / "python_port"
    / "ims"
    / "strategies"
    / "profiles"
    / "strategy_execution_candidate_profile_v1.json"
)


def _candidate_input(period: int) -> dict[str, object]:
    value = json.loads(CANDIDATE_INPUT_FIXTURE.read_text(encoding="utf-8"))
    value["snapshot_context"]["period"] = period
    if period == 1:
        value["snapshot_context"]["entries"][1]["values"][
            "initial_decisions"
        ] = [
            {"sector_index": 0, "insured": False, "insurer_id": None},
            {"sector_index": 1, "insured": False, "insurer_id": None},
        ]
    value["vu_state_provenance"]["period"] = period
    value["scenario_profile_reference"]["period"] = period
    value["vn_process_input"]["period"] = period
    return value


def _profile(
    period: int,
    *,
    run_index: int,
    max_periods: int,
) -> dict[str, object]:
    value = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))
    value["period"] = period
    value["context"]["period"] = period
    value["context"]["run_index"] = run_index
    value["context"]["max_periods"] = max_periods
    value["context"]["rng_seed"] = 1300 + period
    return value


def _persist_chain_candidates(
    db_path: Path,
    profile_root: Path,
    *,
    run_indices: dict[int, int] | None = None,
) -> list[dict[str, object]]:
    references: list[dict[str, object]] = []
    with sqlite3.connect(db_path) as connection:
        connection.execute(STRATEGY_EXECUTION_CANDIDATE_STORE_SCHEMA)
        for period in (1, 2):
            run_index = (run_indices or {}).get(period, 7)
            profile_path = profile_root / f"profile-{period}.json"
            profile_path.write_text(
                json.dumps(
                    _profile(period, run_index=run_index, max_periods=2),
                    ensure_ascii=True,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            profile_id = "synthetic-joint-single-period-v1"
            build = build_strategy_execution_candidate(
                _candidate_input(period),
                profiles={
                    profile_id: StrategyExecutionScenarioProfileDefinition(
                        profile_id=profile_id,
                        path=profile_path,
                    )
                },
                trusted_profile_root=profile_root,
            )
            assert build.candidate is not None, build.issues
            candidate = build.candidate
            payload = candidate.to_dict()
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
                    f"2026-09-11T07:0{period}:00Z",
                    json.dumps(
                        payload,
                        ensure_ascii=True,
                        allow_nan=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                ),
            )
            references.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "content_digest": candidate.content_digest,
                    "period": period,
                }
            )
    return references


def _chain_input(references: list[dict[str, object]]) -> dict[str, object]:
    value = json.loads(CHAIN_INPUT_FIXTURE.read_text(encoding="utf-8"))
    value["run_index"] = 7
    value["max_periods"] = 2
    value["period_candidates"] = deepcopy(references)
    return value


def _issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_resolves_reverifies_and_cross_checks_complete_chain(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)

    first = resolve_strategy_execution_period_chain_input(
        _chain_input(references),
        db_path=db_path,
    )
    second = resolve_strategy_execution_period_chain_input(
        _chain_input(references),
        db_path=db_path,
    )

    assert first.schema_version == STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_VERSION
    assert first.resolution_ready is True
    assert first.input_validated is True
    assert first.resolution_complete is True
    assert first.digests_reverified is True
    assert first.contexts_consistent is True
    assert first.actor_identities_consistent is True
    assert first.run_index == 7
    assert first.max_periods == 2
    assert first.resolved_candidate_count == 2
    assert first.digest_verified_candidate_count == 2
    assert first.context_verified_candidate_count == 2
    assert [candidate.period for candidate in first.candidates] == [1, 2]
    assert first.candidates[0].insurer_ids == (1,)
    assert first.candidates[0].policyholder_ids == (1,)
    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["period_chain_created"] is False
    assert first.to_dict()["writes_performed"] is False


def test_invalid_pr134_input_stops_before_candidate_resolution(
    monkeypatch,
    tmp_path,
) -> None:
    module = importlib.import_module(
        "ims.api.strategy_execution_period_chain_resolution"
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(f"candidate store invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(module, "get_strategy_execution_candidate", fail_if_called)
    value = json.loads(CHAIN_INPUT_FIXTURE.read_text(encoding="utf-8"))
    value["transitions"] = []
    value["db_path"] = str(tmp_path / "browser-selected.sqlite")

    report = resolve_strategy_execution_period_chain_input(
        value,
        db_path=tmp_path / "absent.sqlite",
    )

    assert report.resolution_ready is False
    assert report.input_validated is False
    assert report.resolved_candidate_count == 0
    assert "transition_count_mismatch" in _issue_codes(report)
    assert "field_unknown" in _issue_codes(report)
    assert report.to_dict()["partial_resolution_returned"] is False


def test_missing_candidate_blocks_atomic_result(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "DELETE FROM strategy_execution_candidates WHERE candidate_id = ?",
            (references[1]["candidate_id"],),
        )

    report = resolve_strategy_execution_period_chain_input(
        _chain_input(references),
        db_path=db_path,
    )
    payload = report.to_dict()

    assert report.resolution_ready is False
    assert report.resolved_candidate_count == 1
    assert "candidate_not_found" in _issue_codes(report)
    assert payload["candidate_count"] == 0
    assert payload["candidates"] == []
    assert payload["partial_chain_returned"] is False


def test_changed_reference_digest_is_rejected_after_storage_verification(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    digest = str(references[1]["content_digest"])
    references[1]["content_digest"] = digest[:-1] + (
        "0" if digest[-1] != "0" else "1"
    )

    report = resolve_strategy_execution_period_chain_input(
        _chain_input(references),
        db_path=db_path,
    )

    assert report.resolution_complete is True
    assert report.digests_reverified is False
    assert "resolved_candidate_digest_mismatch" in _issue_codes(report)
    assert report.to_dict()["candidates"] == []


def test_tampered_stored_payload_is_rejected_without_partial_result(
    tmp_path,
) -> None:
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

    report = resolve_strategy_execution_period_chain_input(
        _chain_input(references),
        db_path=db_path,
    )

    assert report.resolution_ready is False
    assert "candidate_digest_verification_failed" in _issue_codes(report)
    assert report.to_dict()["candidate_count"] == 0
    assert report.to_dict()["candidate_content_digest_reverified"] is False


def test_candidate_context_must_match_chain_run_and_horizon(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(
        db_path,
        tmp_path,
        run_indices={2: 8},
    )

    report = resolve_strategy_execution_period_chain_input(
        _chain_input(references),
        db_path=db_path,
    )

    assert report.contexts_consistent is False
    assert "candidate_context_run_index_mismatch" in _issue_codes(report)
    assert report.to_dict()["candidate_context_cross_checked"] is False
    assert report.to_dict()["candidates"] == []


def test_actor_identity_must_remain_stable_across_periods(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    second_reference = references[1]
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT candidate_payload_json FROM strategy_execution_candidates "
            "WHERE candidate_id = ?",
            (second_reference["candidate_id"],),
        ).fetchone()
        payload = json.loads(row[0])
        payload["market_ground_state"]["insurers"][0]["entity_id"] = 2
        identity = payload["identity"]
        sections = {
            key: item
            for key, item in payload.items()
            if key not in {"schema_version", "mode", "identity"}
        }
        digest = calculate_strategy_execution_candidate_content_digest(
            draft_id=identity["draft_id"],
            period=identity["period"],
            sections=sections,
            candidate_schema_version=payload["schema_version"],
        )
        candidate_id = strategy_execution_candidate_id_from_digest(digest)
        identity["candidate_id"] = candidate_id
        identity["content_digest"] = digest
        connection.execute(
            """
            UPDATE strategy_execution_candidates
            SET candidate_id = ?, content_digest = ?, candidate_payload_json = ?
            WHERE candidate_id = ?
            """,
            (
                candidate_id,
                digest,
                json.dumps(
                    payload,
                    ensure_ascii=True,
                    allow_nan=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                second_reference["candidate_id"],
            ),
        )
    second_reference["candidate_id"] = candidate_id
    second_reference["content_digest"] = digest

    report = resolve_strategy_execution_period_chain_input(
        _chain_input(references),
        db_path=db_path,
    )

    assert report.digests_reverified is True
    assert report.actor_identities_consistent is False
    assert "candidate_insurer_identity_mismatch" in _issue_codes(report)
    assert report.to_dict()["candidates"] == []


def test_resolution_contract_opens_only_read_only_candidate_checks() -> None:
    payload = strategy_execution_period_chain_resolution_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_RESOLUTION_CONTRACT_VERSION
    )
    assert payload["candidate_resolution_enabled"] is True
    assert payload["candidate_digest_reverification_enabled"] is True
    assert payload["candidate_context_cross_check_enabled"] is True
    assert payload["actor_identity_cross_check_enabled"] is True
    assert payload["partial_resolution_allowed"] is False
    assert payload["free_database_paths_accepted"] is False
    assert "db_path" in payload["forbidden_request_fields"]
    assert payload["period_chain_creation_enabled"] is False
    assert payload["period_chain_digest_enabled"] is False
    assert payload["carryover_invocation_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR137"


def test_resolution_does_not_call_carryover_or_runner(monkeypatch, tmp_path) -> None:
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

    report = resolve_strategy_execution_period_chain_input(
        _chain_input(references),
        db_path=db_path,
    )

    assert report.resolution_ready is True
    assert db_path.read_bytes() == before
    assert report.to_dict()["carryover_invocation_performed"] is False
    assert report.to_dict()["runner_invocation_performed"] is False


def test_resolution_api_uses_only_configured_sqlite_store(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    references = _persist_chain_candidates(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    contract_endpoint = (
        "/api/strategies/execution-period-chain-resolution-contract"
    )
    resolution_endpoint = "/api/strategies/execution-period-chain-resolution"

    contract = client.get(contract_endpoint)
    response = client.post(resolution_endpoint, json=_chain_input(references))

    assert contract.status_code == 200
    assert contract.json()["free_database_paths_accepted"] is False
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["candidate_count"] == 2
    assert payload["candidate_content_digest_reverified"] is True
    assert payload["period_chain_created"] is False
    assert payload["execution_performed"] is False
    assert client.post(contract_endpoint, json={}).status_code == 405
    assert client.get(resolution_endpoint).status_code == 405
    assert client.put(resolution_endpoint, json={}).status_code == 405
    assert client.delete(resolution_endpoint).status_code == 405


def test_resolution_api_rejects_unconfigured_store_and_invalid_json(
    monkeypatch,
    tmp_path,
) -> None:
    endpoint = "/api/strategies/execution-period-chain-resolution"
    memory_client = TestClient(create_app(frontend_dist=tmp_path))

    unavailable = memory_client.post(endpoint, json={})

    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )
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
    assert invalid_json.json()["candidate_count"] == 0
    assert invalid_json.json()["next_gate"] == "PR137"
