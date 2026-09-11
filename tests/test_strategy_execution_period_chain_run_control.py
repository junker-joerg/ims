import importlib
import sqlite3

import pytest

from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
    strategy_execution_period_chain_id_from_digest,
)
from ims.api.strategy_execution_period_chain_run_control import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_CHECK_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION,
    StrategyExecutionPeriodChainRunControlError,
    check_strategy_execution_period_chain_run_control_release,
    parse_strategy_execution_period_chain_run_control_request,
    strategy_execution_period_chain_run_control_contract_payload,
)
from ims.api.strategy_execution_period_chain_store import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
    persist_strategy_execution_period_chain,
)
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
)


def _persist_chain(db_path, profile_root) -> tuple[str, str]:
    references = persist_chain_candidates(db_path, profile_root)
    period_chain_input = chain_input(references)
    build = build_strategy_execution_period_chain(
        period_chain_input,
        db_path=db_path,
    )
    assert build.chain is not None, build.issues
    persist_strategy_execution_period_chain(
        {
            "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
            "period_chain_input": period_chain_input,
            "expected_chain_id": build.chain.chain_id,
            "expected_content_digest": build.chain.content_digest,
            "stored_at": "2026-09-11T14:00:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=db_path,
    )
    return build.chain.chain_id, build.chain.content_digest


def _request(chain_id: str, digest: str) -> dict[str, object]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
        ),
        "chain_id": chain_id,
        "expected_content_digest": digest,
        "idempotency_key": "pr138-release-check-001",
        "explicit_run_control_release": True,
        "released_by": "test-reviewer",
        "released_at": "2026-09-11T12:30:00Z",
        "release_reason": "Kontrollierte Kettenpruefung fuer PR138",
    }


def test_contract_opens_only_period_chain_release_check() -> None:
    payload = strategy_execution_period_chain_run_control_contract_payload()

    assert payload["contract_endpoint"] == (
        "/api/run-control/strategy-period-chain-contract"
    )
    assert payload["release_check_endpoint"] == (
        "/api/run-control/strategy-period-chain-release-check"
    )
    assert payload["period_chain_resolution_enabled"] is True
    assert payload["period_chain_digest_reverification_enabled"] is True
    assert payload["period_chain_horizon_check_enabled"] is True
    assert payload["candidate_re_resolution_enabled"] is False
    assert payload["run_control_release_check_enabled"] is True
    assert payload["queue_write_enabled"] is False
    assert payload["preflight_enabled"] is False
    assert payload["period_chain_start_allowed"] is False
    assert payload["carryover_invocation_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR139"


def test_parser_accepts_exact_identity_and_audit_fields() -> None:
    digest = "sha256:" + "1" * 64
    value = _request(strategy_execution_period_chain_id_from_digest(digest), digest)

    parsed = parse_strategy_execution_period_chain_run_control_request(value)

    assert parsed.to_dict() == value


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"explicit_run_control_release": False}, "run_control_release_required"),
        ({"chain_id": "period-chain-1"}, "chain_id_invalid"),
        ({"expected_content_digest": "sha256:ABC"}, "content_digest_invalid"),
        ({"released_at": "2026-09-11T12:30:00+02:00"}, "released_at_invalid"),
        ({"released_by": ""}, "released_by_required"),
        ({"period_chain": {}}, "unknown_request_fields"),
        ({"db_path": "browser.sqlite"}, "unknown_request_fields"),
    ],
)
def test_parser_rejects_ambiguous_or_incomplete_requests(
    change: dict[str, object],
    expected_code: str,
) -> None:
    digest = "sha256:" + "1" * 64
    value = _request(strategy_execution_period_chain_id_from_digest(digest), digest)
    value.update(change)

    with pytest.raises(StrategyExecutionPeriodChainRunControlError) as exc_info:
        parse_strategy_execution_period_chain_run_control_request(value)

    assert exc_info.value.code == expected_code


def test_release_check_resolves_reverifies_and_does_not_write(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)
    request = parse_strategy_execution_period_chain_run_control_request(
        _request(chain_id, digest)
    )
    before = db_path.read_bytes()

    payload = check_strategy_execution_period_chain_run_control_release(
        request,
        db_path=db_path,
    ).to_dict()

    assert db_path.read_bytes() == before
    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_CHECK_VERSION
    )
    assert payload["status"] == "ready"
    assert payload["period_chain"] == {
        "chain_id": chain_id,
        "chain_schema_version": "ims.strategy-execution-period-chain.v1",
        "content_digest": digest,
        "first_period": 1,
        "last_period": 2,
        "period_count": 2,
        "run_index": 7,
        "max_periods": 2,
        "stored_at": "2026-09-11T14:00:00+02:00",
        "storage_status": "persisted_immutable",
    }
    assert "period_candidates" not in payload["period_chain"]
    assert payload["period_chain_resolved"] is True
    assert payload["period_chain_digest_reverified"] is True
    assert payload["release_ready"] is True
    assert payload["queue_entry_created"] is False
    assert payload["preflight_performed"] is False
    assert payload["period_chain_start_allowed"] is False
    assert payload["carryover_invocation_performed"] is False
    assert payload["runner_invocation_performed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_release_check_rejects_incoherent_id_before_store_access(tmp_path) -> None:
    digest = "sha256:" + "1" * 64
    request = parse_strategy_execution_period_chain_run_control_request(
        _request("strategy-period-chain-" + "2" * 24, digest)
    )

    result = check_strategy_execution_period_chain_run_control_release(
        request,
        db_path=tmp_path / "missing.sqlite",
    )

    assert result.release_ready is False
    assert result.period_chain is None
    assert result.issues[0]["code"] == "request_identity_consistent"
    assert not (tmp_path / "missing.sqlite").exists()


def test_release_check_rejects_full_digest_mismatch_with_same_id(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)
    changed_last = "0" if digest[-1] != "0" else "1"
    different_digest = digest[:-1] + changed_last
    assert strategy_execution_period_chain_id_from_digest(different_digest) == chain_id
    request = parse_strategy_execution_period_chain_run_control_request(
        _request(chain_id, different_digest)
    )

    result = check_strategy_execution_period_chain_run_control_release(
        request,
        db_path=db_path,
    )

    assert result.release_ready is False
    assert result.period_chain is not None
    assert {issue["code"] for issue in result.issues} == {
        "expected_digest_matches"
    }


def test_release_check_reports_unknown_and_corrupted_period_chains(
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)
    unknown_digest = "sha256:" + "f" * 64
    unknown_request = parse_strategy_execution_period_chain_run_control_request(
        _request(
            strategy_execution_period_chain_id_from_digest(unknown_digest),
            unknown_digest,
        )
    )

    unknown = check_strategy_execution_period_chain_run_control_release(
        unknown_request,
        db_path=db_path,
    )
    assert unknown.release_ready is False
    assert unknown.issues[0]["code"] == "period_chain_not_found"

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE strategy_execution_period_chains SET run_index = ? "
            "WHERE chain_id = ?",
            (99, chain_id),
        )
    damaged_request = parse_strategy_execution_period_chain_run_control_request(
        _request(chain_id, digest)
    )
    damaged = check_strategy_execution_period_chain_run_control_release(
        damaged_request,
        db_path=db_path,
    )
    assert damaged.release_ready is False
    assert damaged.issues[0]["code"] == "stored_period_chain_metadata_mismatch"


def test_release_check_does_not_resolve_candidates_or_invoke_execution(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persist_chain(db_path, tmp_path)
    resolution = importlib.import_module(
        "ims.api.strategy_execution_period_chain_resolution"
    )
    vu_runner = importlib.import_module("ims.engine.vu_rule_runner")
    vn_runner = importlib.import_module("ims.engine.vn_rule_runner")
    period_runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_operation(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"operation invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(
        resolution,
        "get_strategy_execution_candidate",
        reject_operation,
    )
    monkeypatch.setattr(
        vu_runner,
        "apply_vu_foreign_info_carryover",
        reject_operation,
    )
    monkeypatch.setattr(vn_runner, "apply_vn_state_carryover", reject_operation)
    monkeypatch.setattr(period_runner, "run_loaded_explicit_period", reject_operation)

    result = check_strategy_execution_period_chain_run_control_release(
        parse_strategy_execution_period_chain_run_control_request(
            _request(chain_id, digest)
        ),
        db_path=db_path,
    )

    assert result.release_ready is True
    assert result.to_dict()["period_chain_start_allowed"] is False
    assert result.to_dict()["carryover_invocation_performed"] is False
    assert result.to_dict()["runner_invocation_performed"] is False
    assert result.to_dict()["execution_performed"] is False
    assert result.to_dict()["simulation_performed"] is False
