from copy import deepcopy
import importlib
import json
from pathlib import Path

import pytest

from ims.strategies import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION,
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION,
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION,
    STRATEGY_DEFINITIONS,
    STRATEGY_PARAMETER_SCHEMAS,
    VU_DRAW_SOURCE_POLICY_ID,
    VU_FALLBACK_POLICY_ID,
    VU_SNAPSHOT_MATERIALIZATION_TARGETS,
    VU_THRESHOLD_SOURCE_POLICY_ID,
    strategy_assignment_vu_snapshot_state_contract_payload,
    strategy_vu_snapshot_state_contract_issues,
    validate_strategy_assignment_vu_snapshot_state,
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
_ASPIRATION_SECTOR_1 = [50.0, 2.0, 0.04]
_ASPIRATION_SECTOR_2 = [60.0, 3.0, 0.05]


def _request(strategy_id: str, *, period: int = 2) -> dict[str, object]:
    draft = json.loads(BASE_DRAFT.read_text(encoding="utf-8"))
    strategy = _STRATEGIES_BY_ID[strategy_id]
    schema = _SCHEMAS_BY_ID[strategy.parameter_schema]
    draft_id = f"synthetic-pr120-{strategy_id}"
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
    materialization_input = {
        "schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION
        ),
        "threshold_source_policy": VU_THRESHOLD_SOURCE_POLICY_ID,
        "draw_source_policy": VU_DRAW_SOURCE_POLICY_ID,
        "fallback_policy": VU_FALLBACK_POLICY_ID,
        "draft": draft,
        "context": {
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
        },
    }
    state_values: dict[str, object] = {}
    if strategy_id in {"vu.vrvu03", "vu.vrvu04", "vu.vrvu05"}:
        state_values.update(
            {
                "aspiration_sector_1": deepcopy(_ASPIRATION_SECTOR_1),
                "aspiration_sector_2": deepcopy(_ASPIRATION_SECTOR_2),
            }
        )
    if strategy_id == "vu.vrvu04":
        state_values["policyholders_t_minus_2"] = [10.0, 20.0]
    return {
        "input": materialization_input,
        "state": {
            "schema_version": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION,
            "input_schema_version": (
                STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION
            ),
            "base_model": "Vdefmd6",
            "scope": "vu_snapshot_materialization_provenance_state",
            "draft_id": draft_id,
            "period": period,
            "period_state": {
                "interest_rate": 0.02,
                "change_shock": False,
                "active_policyholder_count": 200,
            },
            "entries": [
                {
                    "insurer_id": 1,
                    "strategy_id": strategy_id,
                    "values": state_values,
                }
            ],
        },
    }


def _issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


@pytest.mark.parametrize(
    "strategy_id",
    [f"vu.vrvu{index:02d}" for index in range(1, 11)],
)
def test_state_provenance_validates_every_vu_strategy(strategy_id: str) -> None:
    first = validate_strategy_assignment_vu_snapshot_state(_request(strategy_id))
    second = validate_strategy_assignment_vu_snapshot_state(_request(strategy_id))

    assert first.schema_version == (
        STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION
    )
    assert first.valid is True
    assert first.input_valid is True
    assert first.state_shape_valid is True
    assert first.expected_state_entry_count == first.validated_state_entry_count == 1
    assert first.expected_provenance_check_count == (
        first.matched_provenance_check_count
    )
    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["state_values_consumed"] is False
    assert first.to_dict()["snapshots_created"] is False
    assert first.to_dict()["simulation_performed"] is False
    assert first.to_dict()["threshold_values_cross_checked_against_actor_state"] is (
        strategy_id in {"vu.vrvu03", "vu.vrvu04", "vu.vrvu05"}
    )


@pytest.mark.parametrize(
    ("strategy_id", "mutate", "expected_code"),
    [
        (
            "vu.vrvu01",
            lambda request: request["state"]["period_state"].update(
                {"interest_rate": 0.03}
            ),
            "period_state_mismatch",
        ),
        (
            "vu.vrvu03",
            lambda request: request["state"]["entries"][0]["values"][
                "aspiration_sector_1"
            ].__setitem__(0, 51.0),
            "threshold_source_mismatch",
        ),
        (
            "vu.vrvu04",
            lambda request: request["state"]["entries"][0]["values"][
                "policyholders_t_minus_2"
            ].__setitem__(1, 21.0),
            "previous_state_mismatch",
        ),
        (
            "vu.vrvu05",
            lambda request: request["state"]["period_state"].update(
                {"active_policyholder_count": 201}
            ),
            "market_state_mismatch",
        ),
    ],
)
def test_state_provenance_rejects_source_mismatches(
    strategy_id: str,
    mutate,
    expected_code: str,
) -> None:
    request = _request(strategy_id)
    mutate(request)

    report = validate_strategy_assignment_vu_snapshot_state(request)

    assert report.valid is False
    assert report.input_valid is True
    assert report.state_shape_valid is True
    assert expected_code in _issue_codes(report)
    assert report.matched_provenance_check_count < (
        report.expected_provenance_check_count
    )


def test_state_document_requires_exact_version_shape_and_entry_match() -> None:
    wrong_version = _request("vu.vrvu03")
    wrong_version["state"]["schema_version"] = "unknown-state-version"
    wrong_shape = _request("vu.vrvu04")
    wrong_shape["state"]["entries"][0]["values"]["aspiration_sector_1"] = [1.0]
    missing_entry = _request("vu.vrvu05")
    missing_entry["state"]["entries"] = []

    version_report = validate_strategy_assignment_vu_snapshot_state(wrong_version)
    shape_report = validate_strategy_assignment_vu_snapshot_state(wrong_shape)
    entry_report = validate_strategy_assignment_vu_snapshot_state(missing_entry)

    assert "state_contract_value_mismatch" in _issue_codes(version_report)
    assert "state_value_shape_invalid" in _issue_codes(shape_report)
    assert "state_entry_missing" in _issue_codes(entry_report)
    assert version_report.state_shape_valid is False
    assert shape_report.state_shape_valid is False
    assert entry_report.state_shape_valid is False


def test_invalid_pr119_input_stops_before_state_inspection() -> None:
    request = _request("vu.vrvu01")
    request["input"]["context"]["entries"][0]["values"]["random_draws"] = None

    report = validate_strategy_assignment_vu_snapshot_state(request)

    assert report.valid is False
    assert report.input_valid is False
    assert report.state_shape_valid is False
    assert _issue_codes(report) == {"fallback_not_allowed"}
    assert report.to_dict()["state_values_inspected"] is False


def test_state_provenance_does_not_invoke_vu_snapshot_loader(monkeypatch) -> None:
    vu_rules = importlib.import_module("ims.model.vu_rules")

    def fail_if_called(mapping):
        raise AssertionError(f"snapshot loader was called with {mapping!r}")

    monkeypatch.setattr(
        vu_rules,
        "vu_reserve_markup_rule_snapshot_from_mapping",
        fail_if_called,
    )

    report = validate_strategy_assignment_vu_snapshot_state(_request("vu.vrvu03"))

    assert report.valid is True
    assert report.to_dict()["snapshot_loader_invocation_performed"] is False


def test_state_contract_exposes_sources_checks_and_closed_boundaries() -> None:
    payload = strategy_assignment_vu_snapshot_state_contract_payload()

    assert strategy_vu_snapshot_state_contract_issues() == ()
    assert payload["schema_version"] == (
        STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION
    )
    assert payload["state_schema_version"] == (
        STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION
    )
    assert payload["validated_strategy_count"] == 10
    assert payload["provenance_definition_count"] == 7
    assert payload["contract_issue_count"] == 0
    assert payload["threshold_values_cross_checked_against_actor_state"] is True
    assert payload["draw_values_cross_checked_against_draw_plan"] is False
    assert payload["snapshot_loader_invocation_enabled"] is False
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["simulation_performed"] is False
