from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest

from ims.api.strategy_execution_candidate_effect_probe import (
    STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_VERSION,
    StrategyExecutionCandidateEffectProbeError,
    parse_strategy_execution_candidate_effect_probe_request,
    run_strategy_execution_candidate_effect_probe,
    strategy_execution_candidate_effect_probe_contract_payload,
)
from ims.api.strategy_execution_candidate_run_control import (
    STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
)
from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
    get_strategy_execution_candidate,
    persist_strategy_execution_candidate,
)
from ims.strategies import (
    build_default_strategy_execution_scenario_profiles,
    build_strategy_execution_candidate,
    strategy_execution_scenario_profile_root,
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
            "stored_at": "2026-09-09T09:00:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=db_path,
        profiles=profiles,
        trusted_profile_root=profile_root,
    )
    return candidate_id, digest


def _release(candidate_id: str, digest: str) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
        "candidate_id": candidate_id,
        "expected_content_digest": digest,
        "idempotency_key": "pr130-effect-probe-001",
        "explicit_run_control_release": True,
        "released_by": "test-reviewer",
        "released_at": "2026-09-09T07:05:00Z",
        "release_reason": "Kontrollierte Einperioden-Wirkungsprobe",
    }


def _request(candidate_id: str, digest: str) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION,
        "release": _release(candidate_id, digest),
        "explicit_effect_probe_execution": True,
    }


def test_effect_probe_contract_opens_only_isolated_single_period_execution() -> None:
    payload = strategy_execution_candidate_effect_probe_contract_payload()

    assert payload["scope"] == (
        "one_released_candidate_one_isolated_period_effect_probe"
    )
    assert payload["contract_endpoint"] == (
        "/api/run-control/strategy-candidate-effect-probe-contract"
    )
    assert payload["execution_endpoint"] == (
        "/api/run-control/strategy-candidate-effect-probe"
    )
    assert payload["explicit_effect_probe_execution_required"] is True
    assert payload["candidate_digest_reverification_required"] is True
    assert payload["isolated_candidate_copy_required"] is True
    assert payload["single_period_only"] is True
    assert payload["effect_probe_execution_enabled"] is True
    assert payload["ui_start_enabled"] is False
    assert payload["idempotency_persistence_enabled"] is False
    assert payload["result_persistence_enabled"] is False
    assert payload["carryover_enabled"] is False
    assert payload["output_files_enabled"] is False
    assert payload["legacy_comparison_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["persistent_start_endpoint"] == (
        "/api/run-control/strategy-candidate-effect-probe-start"
    )
    assert payload["next_gate"] == "PR133"


def test_effect_probe_parser_reuses_exact_pr129_release() -> None:
    digest = "sha256:" + "1" * 64
    candidate_id = "strategy-candidate-" + "1" * 24
    value = _request(candidate_id, digest)

    parsed = parse_strategy_execution_candidate_effect_probe_request(value)

    assert parsed.to_dict() == value


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"explicit_effect_probe_execution": False}, "effect_probe_execution_release_required"),
        ({"schema_version": "wrong"}, "unsupported_schema_version"),
        ({"unexpected": True}, "unknown_request_fields"),
    ],
)
def test_effect_probe_parser_rejects_unreleased_or_ambiguous_requests(
    change: dict[str, object],
    expected_code: str,
) -> None:
    digest = "sha256:" + "1" * 64
    value = _request("strategy-candidate-" + "1" * 24, digest)
    value.update(change)

    with pytest.raises(StrategyExecutionCandidateEffectProbeError) as exc_info:
        parse_strategy_execution_candidate_effect_probe_request(value)

    assert exc_info.value.code == expected_code


def test_effect_probe_runs_once_on_isolated_copy_without_writes(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    source_before = get_strategy_execution_candidate(
        candidate_id,
        db_path=db_path,
    ).record.to_dict()
    database_digest_before = sha256(db_path.read_bytes()).hexdigest()
    parsed = parse_strategy_execution_candidate_effect_probe_request(
        _request(candidate_id, digest)
    )

    result = run_strategy_execution_candidate_effect_probe(
        parsed,
        db_path=db_path,
    )

    payload = result.to_dict()
    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_VERSION
    )
    assert payload["status"] == "ok"
    assert payload["candidate_digest_reverified"] is True
    assert payload["candidate_copy_isolated"] is True
    assert payload["source_candidate_mutated"] is False
    assert payload["period_count"] == 1
    assert payload["runner_invocation_count"] == 1
    assert payload["execution_performed"] is True
    assert payload["writes_performed"] is False
    assert payload["result_persisted"] is False
    assert payload["idempotency_persisted"] is False
    assert payload["carryover_performed"] is False
    assert payload["output_files_written"] is False
    assert payload["legacy_comparison_performed"] is False
    assert payload["simulation_performed"] is False
    effect = payload["effect"]
    assert effect["period"] == 2
    assert effect["applications"]["vu_total"] == 1
    assert effect["applications"]["vn"]["insurance_rule"] == 1
    assert effect["applications"]["vn"]["damage_settlement"] == 1
    assert effect["state_changed"] is True
    assert effect["changed_insurer_ids"] == [1]
    assert effect["changed_policyholder_ids"] == [1]
    assert effect["in_memory_export"]["table_count"] > 0
    assert effect["in_memory_export"]["written_file_count"] == 0
    assert get_strategy_execution_candidate(
        candidate_id,
        db_path=db_path,
    ).record.to_dict() == source_before
    assert sha256(db_path.read_bytes()).hexdigest() == database_digest_before
    assert {path.name for path in tmp_path.iterdir()} == {"metadata.sqlite"}


def test_effect_probe_is_deterministic_but_not_yet_idempotency_persisted(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    request = parse_strategy_execution_candidate_effect_probe_request(
        _request(candidate_id, digest)
    )

    first = run_strategy_execution_candidate_effect_probe(request, db_path=db_path)
    second = run_strategy_execution_candidate_effect_probe(request, db_path=db_path)

    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["idempotency_persisted"] is False
    assert first.to_dict()["result_persisted"] is False


def test_effect_probe_blocks_failed_digest_check_before_runner(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    changed_last = "0" if digest[-1] != "0" else "1"
    request = parse_strategy_execution_candidate_effect_probe_request(
        _request(candidate_id, digest[:-1] + changed_last)
    )

    def reject_runner(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"runner invoked with {args!r} {kwargs!r}")

    result = run_strategy_execution_candidate_effect_probe(
        request,
        db_path=db_path,
        runner=reject_runner,
    )

    payload = result.to_dict()
    assert payload["status"] == "blocked"
    assert payload["issues"][0]["code"] == "expected_digest_matches"
    assert payload["runner_invocation_performed"] is False
    assert payload["execution_performed"] is False


def test_effect_probe_reports_runner_failure_without_result_or_write(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    candidate_id, digest = _persist_candidate(db_path)
    source_before = deepcopy(
        get_strategy_execution_candidate(candidate_id, db_path=db_path).record.to_dict()
    )
    request = parse_strategy_execution_candidate_effect_probe_request(
        _request(candidate_id, digest)
    )

    def failing_runner(loaded, *, output_dir=None):
        assert output_dir is None
        raise RuntimeError("synthetic runner failure")

    with pytest.raises(StrategyExecutionCandidateEffectProbeError) as exc_info:
        run_strategy_execution_candidate_effect_probe(
            request,
            db_path=db_path,
            runner=failing_runner,
        )

    assert exc_info.value.code == "effect_probe_runner_failed"
    assert exc_info.value.runner_invocation_performed is True
    assert get_strategy_execution_candidate(
        candidate_id,
        db_path=db_path,
    ).record.to_dict() == source_before
