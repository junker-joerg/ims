import importlib
import json
from pathlib import Path
import sqlite3

import pytest

from ims.api.strategy_execution_candidate_run_control import (
    STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_CHECK_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
    StrategyExecutionCandidateRunControlError,
    check_strategy_execution_candidate_run_control_release,
    parse_strategy_execution_candidate_run_control_request,
    strategy_execution_candidate_run_control_contract_payload,
)
from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
    persist_strategy_execution_candidate,
)
from ims.strategies import (
    build_default_strategy_execution_scenario_profiles,
    build_strategy_execution_candidate,
    strategy_execution_scenario_profile_root,
)
from ims.strategies.execution_candidate_build import (
    strategy_execution_candidate_id_from_digest,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_execution_candidate_input_v1.json"
)


def _persist_candidate(db_path: Path) -> tuple[str, str]:
    candidate_input = json.loads(FIXTURE.read_text(encoding="utf-8"))
    profiles = build_default_strategy_execution_scenario_profiles()
    profile_root = strategy_execution_scenario_profile_root()
    build = build_strategy_execution_candidate(
        candidate_input,
        profiles=profiles,
        trusted_profile_root=profile_root,
    )
    assert build.candidate is not None
    candidate_id = build.candidate.candidate_id
    digest = build.candidate.content_digest
    persist_strategy_execution_candidate(
        {
            "schema_version": STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
            "candidate_input": candidate_input,
            "expected_candidate_id": candidate_id,
            "expected_content_digest": digest,
            "stored_at": "2026-09-08T12:00:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=db_path,
        profiles=profiles,
        trusted_profile_root=profile_root,
    )
    return candidate_id, digest


def _request(candidate_id: str, digest: str) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
        "candidate_id": candidate_id,
        "expected_content_digest": digest,
        "idempotency_key": "pr129-release-check-001",
        "explicit_run_control_release": True,
        "released_by": "test-reviewer",
        "released_at": "2026-09-08T10:30:00Z",
        "release_reason": "Kontrollierte Kandidatenpruefung fuer PR129",
    }


def test_contract_opens_only_candidate_release_check() -> None:
    payload = strategy_execution_candidate_run_control_contract_payload()

    assert payload["contract_endpoint"] == (
        "/api/run-control/strategy-candidate-contract"
    )
    assert payload["release_check_endpoint"] == (
        "/api/run-control/strategy-candidate-release-check"
    )
    assert payload["candidate_resolution_enabled"] is True
    assert payload["candidate_digest_reverification_enabled"] is True
    assert payload["run_control_release_check_enabled"] is True
    assert payload["queue_write_enabled"] is False
    assert payload["preflight_enabled"] is False
    assert payload["adapter_start_allowed"] is False
    assert payload["runner_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["effect_probe_execution_enabled"] is True
    assert payload["effect_probe_idempotency_persistence_enabled"] is True
    assert payload["effect_probe_result_persistence_enabled"] is True
    assert payload["effect_probe_ui_start_enabled"] is True
    assert payload["next_gate"] == "PR136"


def test_parser_accepts_exact_identity_and_audit_fields() -> None:
    digest = "sha256:" + "1" * 64
    value = _request(strategy_execution_candidate_id_from_digest(digest), digest)

    parsed = parse_strategy_execution_candidate_run_control_request(value)

    assert parsed.to_dict() == value


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"explicit_run_control_release": False}, "run_control_release_required"),
        ({"candidate_id": "candidate-1"}, "candidate_id_invalid"),
        ({"expected_content_digest": "sha256:ABC"}, "content_digest_invalid"),
        ({"released_at": "2026-09-08T10:30:00+02:00"}, "released_at_invalid"),
        ({"released_by": ""}, "released_by_required"),
        ({"unexpected": True}, "unknown_request_fields"),
    ],
)
def test_parser_rejects_ambiguous_or_incomplete_requests(
    change: dict[str, object],
    expected_code: str,
) -> None:
    digest = "sha256:" + "1" * 64
    value = _request(strategy_execution_candidate_id_from_digest(digest), digest)
    value.update(change)

    with pytest.raises(StrategyExecutionCandidateRunControlError) as exc_info:
        parse_strategy_execution_candidate_run_control_request(value)

    assert exc_info.value.code == expected_code


def test_release_check_resolves_and_reverifies_persisted_candidate(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    request = parse_strategy_execution_candidate_run_control_request(
        _request(candidate_id, digest)
    )

    payload = check_strategy_execution_candidate_run_control_release(
        request,
        db_path=db_path,
    ).to_dict()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_CHECK_VERSION
    )
    assert payload["status"] == "ready"
    assert payload["candidate"]["candidate_id"] == candidate_id
    assert payload["candidate"]["content_digest"] == digest
    assert "candidate" not in payload["candidate"]
    assert payload["candidate_resolved"] is True
    assert payload["candidate_digest_reverified"] is True
    assert payload["release_ready"] is True
    assert payload["queue_entry_created"] is False
    assert payload["preflight_performed"] is False
    assert payload["adapter_start_allowed"] is False
    assert payload["runner_invocation_performed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_release_check_rejects_incoherent_id_before_store_access(tmp_path) -> None:
    digest = "sha256:" + "1" * 64
    request = parse_strategy_execution_candidate_run_control_request(
        _request("strategy-candidate-" + "2" * 24, digest)
    )

    result = check_strategy_execution_candidate_run_control_release(
        request,
        db_path=tmp_path / "missing.sqlite",
    )

    assert result.release_ready is False
    assert result.candidate is None
    assert result.issues[0]["code"] == "request_identity_consistent"
    assert not (tmp_path / "missing.sqlite").exists()


def test_release_check_rejects_full_digest_mismatch_with_same_id(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    changed_last = "0" if digest[-1] != "0" else "1"
    different_digest = digest[:-1] + changed_last
    assert strategy_execution_candidate_id_from_digest(different_digest) == candidate_id
    request = parse_strategy_execution_candidate_run_control_request(
        _request(candidate_id, different_digest)
    )

    result = check_strategy_execution_candidate_run_control_release(
        request,
        db_path=db_path,
    )

    assert result.release_ready is False
    assert result.candidate is not None
    assert {issue["code"] for issue in result.issues} == {"expected_digest_matches"}


def test_release_check_reports_unknown_and_corrupted_candidates(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    unknown_digest = "sha256:" + "f" * 64
    unknown_request = parse_strategy_execution_candidate_run_control_request(
        _request(
            strategy_execution_candidate_id_from_digest(unknown_digest),
            unknown_digest,
        )
    )

    unknown = check_strategy_execution_candidate_run_control_release(
        unknown_request,
        db_path=db_path,
    )
    assert unknown.release_ready is False
    assert unknown.issues[0]["code"] == "candidate_not_found"

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE strategy_execution_candidates SET draft_id = ? WHERE candidate_id = ?",
            ("damaged-draft", candidate_id),
        )
    damaged_request = parse_strategy_execution_candidate_run_control_request(
        _request(candidate_id, digest)
    )
    damaged = check_strategy_execution_candidate_run_control_release(
        damaged_request,
        db_path=db_path,
    )
    assert damaged.release_ready is False
    assert damaged.issues[0]["code"] == "stored_candidate_metadata_mismatch"


def test_release_check_does_not_invoke_runner(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"runner invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)

    result = check_strategy_execution_candidate_run_control_release(
        parse_strategy_execution_candidate_run_control_request(
            _request(candidate_id, digest)
        ),
        db_path=db_path,
    )

    assert result.release_ready is True
    assert result.to_dict()["runner_invocation_performed"] is False
