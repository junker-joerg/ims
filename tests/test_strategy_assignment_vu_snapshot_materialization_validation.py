from copy import deepcopy
import importlib
import json
from pathlib import Path

import pytest

from ims.strategies import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION,
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION,
    STRATEGY_DEFINITIONS,
    STRATEGY_PARAMETER_SCHEMAS,
    VU_DRAW_SOURCE_POLICY_ID,
    VU_FALLBACK_POLICY_ID,
    VU_SNAPSHOT_MATERIALIZATION_TARGETS,
    VU_THRESHOLD_SOURCE_POLICY_ID,
    strategy_assignment_vu_snapshot_materialization_validation_contract_payload,
    validate_strategy_assignment_vu_snapshot_materialization_input,
)


BASE_DRAFT = Path(__file__).parent / "fixtures" / "strategy_assignment_draft_v1.json"
_STRATEGIES_BY_ID = {strategy.strategy_id: strategy for strategy in STRATEGY_DEFINITIONS}
_SCHEMAS_BY_ID = {schema.schema_id: schema for schema in STRATEGY_PARAMETER_SCHEMAS}
_TARGETS_BY_ID = {
    target.strategy_id: target for target in VU_SNAPSHOT_MATERIALIZATION_TARGETS
}
_VALUE_BY_FIELD = {
    "interest_rate": 0.02,
    "change_shock": False,
    "random_draws": [0.1, 0.2, 0.3, 0.4],
    "normal_draws": [-1.0, 0.0, 1.0, 2.0],
    "reserve_thresholds": [50.0, 60.0],
    "net_switcher_thresholds": [2.0, 3.0],
    "previous_policyholders_sector": [10.0, 20.0],
    "market_share_thresholds": [0.04, 0.05],
    "active_policyholder_count": 200,
}


def _request(strategy_id: str, *, period: int = 2) -> dict[str, object]:
    draft = json.loads(BASE_DRAFT.read_text(encoding="utf-8"))
    strategy = _STRATEGIES_BY_ID[strategy_id]
    schema = _SCHEMAS_BY_ID[strategy.parameter_schema]
    draft_id = f"synthetic-pr119-{strategy_id}"
    draft["draft_id"] = draft_id
    draft["assignments"] = [
        {
            "actor_type": "insurer",
            "target_id": 1,
            "strategy_id": strategy_id,
            "activation_period": 1,
            "active_through_run": 100,
            "logical_time": 1,
            "parameter_schema": strategy.parameter_schema,
            "parameter_values": {
                field.field_name: [1.0, 1.0] for field in schema.fields
            },
        }
    ]
    target = _TARGETS_BY_ID[strategy_id]
    context = {
        "schema_version": "ims.strategy-assignment-snapshot-context.v1",
        "translation_schema_version": (
            "ims.strategy-assignment-snapshot-translation.v1"
        ),
        "base_model": "Vdefmd6",
        "scope": "explicit_single_period_snapshot_context",
        "draft_id": draft_id,
        "period": period,
        "entries": [
            {
                "actor_type": "insurer",
                "target_id": 1,
                "strategy_id": strategy_id,
                "values": {
                    field_name: deepcopy(_VALUE_BY_FIELD[field_name])
                    for field_name in target.open_snapshot_fields
                },
            }
        ],
    }
    return {
        "schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION
        ),
        "threshold_source_policy": VU_THRESHOLD_SOURCE_POLICY_ID,
        "draw_source_policy": VU_DRAW_SOURCE_POLICY_ID,
        "fallback_policy": VU_FALLBACK_POLICY_ID,
        "draft": draft,
        "context": context,
    }


def _issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


@pytest.mark.parametrize(
    "strategy_id",
    [f"vu.vrvu{index:02d}" for index in range(1, 11)],
)
def test_explicit_vu_input_validates_every_catalogued_strategy(strategy_id: str) -> None:
    first = validate_strategy_assignment_vu_snapshot_materialization_input(
        _request(strategy_id)
    )
    second = validate_strategy_assignment_vu_snapshot_materialization_input(
        _request(strategy_id)
    )

    assert first.schema_version == (
        STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
    )
    assert first.valid is True
    assert first.policy_valid is True
    assert first.base_context_valid is True
    assert first.expected_vu_entry_count == first.validated_vu_entry_count == 1
    assert first.expected_value_count == first.validated_value_count
    assert first.rejected_fallback_count == 0
    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["snapshot_loader_invocation_performed"] is False
    assert first.to_dict()["snapshots_created"] is False
    assert first.to_dict()["simulation_performed"] is False


@pytest.mark.parametrize(
    ("strategy_id", "field_name"),
    [
        ("vu.vrvu01", "random_draws"),
        ("vu.vrvu02", "normal_draws"),
        ("vu.vrvu04", "previous_policyholders_sector"),
        ("vu.vrvu05", "active_policyholder_count"),
    ],
)
def test_nullable_loader_and_runner_fallbacks_are_rejected(
    strategy_id: str,
    field_name: str,
) -> None:
    request = _request(strategy_id)
    request["context"]["entries"][0]["values"][field_name] = None

    report = validate_strategy_assignment_vu_snapshot_materialization_input(request)

    assert report.valid is False
    assert report.base_context_valid is True
    assert report.rejected_fallback_count == 1
    assert _issue_codes(report) == {"fallback_not_allowed"}


@pytest.mark.parametrize(
    ("strategy_id", "field_name"),
    [
        ("vu.vrvu03", "reserve_thresholds"),
        ("vu.vrvu07", "interest_rate"),
    ],
)
def test_missing_loader_default_fields_fail_in_the_base_context(
    strategy_id: str,
    field_name: str,
) -> None:
    request = _request(strategy_id)
    del request["context"]["entries"][0]["values"][field_name]

    report = validate_strategy_assignment_vu_snapshot_materialization_input(request)

    assert report.valid is False
    assert report.base_context_valid is False
    assert "context_value_missing" in _issue_codes(report)


def test_threshold_draw_and_fallback_policy_ids_are_part_of_the_input() -> None:
    request = _request("vu.vrvu03")
    request["threshold_source_policy"] = "unknown-threshold-source"

    report = validate_strategy_assignment_vu_snapshot_materialization_input(request)

    assert report.valid is False
    assert report.policy_valid is False
    assert report.base_context_valid is False
    assert _issue_codes(report) == {"contract_value_mismatch"}


def test_uniform_draw_range_and_non_negative_state_values_are_validated() -> None:
    uniform = _request("vu.vrvu01")
    uniform["context"]["entries"][0]["values"]["random_draws"][3] = 1.0
    previous = _request("vu.vrvu04")
    previous["context"]["entries"][0]["values"]["previous_policyholders_sector"][0] = -1.0
    active = _request("vu.vrvu05")
    active["context"]["entries"][0]["values"]["active_policyholder_count"] = -1

    uniform_report = validate_strategy_assignment_vu_snapshot_materialization_input(
        uniform
    )
    previous_report = validate_strategy_assignment_vu_snapshot_materialization_input(
        previous
    )
    active_report = validate_strategy_assignment_vu_snapshot_materialization_input(
        active
    )

    assert _issue_codes(uniform_report) == {"uniform_draw_out_of_range"}
    assert _issue_codes(previous_report) == {"previous_policyholders_negative"}
    assert _issue_codes(active_report) == {"active_policyholder_count_negative"}


def test_vu_validation_does_not_invoke_snapshot_loader(monkeypatch) -> None:
    vu_rules = importlib.import_module("ims.model.vu_rules")

    def fail_if_called(mapping):
        raise AssertionError(f"snapshot loader was called with {mapping!r}")

    monkeypatch.setattr(
        vu_rules,
        "vu_random_uniform_rule_snapshot_from_mapping",
        fail_if_called,
    )

    report = validate_strategy_assignment_vu_snapshot_materialization_input(
        _request("vu.vrvu01")
    )

    assert report.valid is True
    assert report.to_dict()["snapshot_loader_invocation_performed"] is False


def test_vu_validation_contract_exposes_sources_and_closed_boundaries() -> None:
    payload = (
        strategy_assignment_vu_snapshot_materialization_validation_contract_payload()
    )

    assert payload["schema_version"] == (
        STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
    )
    assert payload["validated_strategy_count"] == 10
    assert payload["materialization_contract_issue_count"] == 0
    assert payload["threshold_source_policy"]["policy_id"] == (
        VU_THRESHOLD_SOURCE_POLICY_ID
    )
    assert payload["draw_source_policy"]["policy_id"] == VU_DRAW_SOURCE_POLICY_ID
    assert payload["fallback_policy"]["allowed_fallbacks"] == ()
    assert payload["threshold_values_cross_checked_against_actor_state"] is False
    assert payload["snapshot_loader_invocation_enabled"] is False
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["simulation_performed"] is False
