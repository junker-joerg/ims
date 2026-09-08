from copy import deepcopy
import importlib
import json
from pathlib import Path

from ims.model.vu_rules import (
    VUExpectedClaimRuleSnapshot,
    VUForeignInfoRuleKind,
    VUForeignInfoRuleSnapshot,
    VUFreeLinearRuleSnapshot,
    VUMarketShareMarkupRuleSnapshot,
    VUNetSwitcherMarkupRuleSnapshot,
    VURandomNormalRuleSnapshot,
    VURandomUniformRuleSnapshot,
    VUReserveMarkupRuleSnapshot,
)
from ims.strategies import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION,
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VERSION,
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION,
    STRATEGY_DEFINITIONS,
    STRATEGY_PARAMETER_SCHEMAS,
    VU_DRAW_SOURCE_POLICY_ID,
    VU_FALLBACK_POLICY_ID,
    VU_SNAPSHOT_MATERIALIZATION_TARGETS,
    VU_THRESHOLD_SOURCE_POLICY_ID,
    materialize_strategy_assignment_vu_snapshots,
    strategy_assignment_vu_snapshot_materialization_operation_contract_payload,
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


def _request() -> dict[str, object]:
    draft = json.loads(BASE_DRAFT.read_text(encoding="utf-8"))
    draft_id = "synthetic-pr121-all-vu-strategies"
    draft["draft_id"] = draft_id
    draft["assignments"] = []
    context_entries = []
    state_entries = []
    for insurer_id in range(1, 11):
        strategy_id = f"vu.vrvu{insurer_id:02d}"
        strategy = _STRATEGIES_BY_ID[strategy_id]
        schema = _SCHEMAS_BY_ID[strategy.parameter_schema]
        draft["assignments"].append(
            {
                "actor_type": "insurer",
                "target_id": insurer_id,
                "strategy_id": strategy_id,
                "activation_period": 1,
                "active_through_run": 100,
                "logical_time": 1,
                "parameter_schema": strategy.parameter_schema,
                "parameter_values": {
                    field.field_name: [1.0, 1.0] for field in schema.fields
                },
            }
        )
        target = _TARGETS_BY_ID[strategy_id]
        context_entries.append(
            {
                "actor_type": "insurer",
                "target_id": insurer_id,
                "strategy_id": strategy_id,
                "values": {
                    field_name: deepcopy(_VALUE_BY_FIELD[field_name])
                    for field_name in target.open_snapshot_fields
                },
            }
        )
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
        state_entries.append(
            {
                "insurer_id": insurer_id,
                "strategy_id": strategy_id,
                "values": state_values,
            }
        )

    return {
        "input": {
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
                "period": 2,
                "entries": context_entries,
            },
        },
        "state": {
            "schema_version": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION,
            "input_schema_version": (
                STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION
            ),
            "base_model": "Vdefmd6",
            "scope": "vu_snapshot_materialization_provenance_state",
            "draft_id": draft_id,
            "period": 2,
            "period_state": {
                "interest_rate": 0.02,
                "change_shock": False,
                "active_policyholder_count": 200,
            },
            "entries": state_entries,
        },
    }


def test_materializes_all_ten_vu_strategies_with_existing_snapshot_types() -> None:
    report = materialize_strategy_assignment_vu_snapshots(_request())

    assert report.materialization_complete is True
    assert report.input_valid is True
    assert report.expected_snapshot_count == 10
    assert report.snapshot_loader_invocation_count == 10
    assert report.issues == ()
    assert [entry.strategy_id for entry in report.snapshots] == [
        f"vu.vrvu{index:02d}" for index in range(1, 11)
    ]
    assert [type(entry.snapshot) for entry in report.snapshots] == [
        VURandomUniformRuleSnapshot,
        VURandomNormalRuleSnapshot,
        VUReserveMarkupRuleSnapshot,
        VUNetSwitcherMarkupRuleSnapshot,
        VUMarketShareMarkupRuleSnapshot,
        VUExpectedClaimRuleSnapshot,
        VUForeignInfoRuleSnapshot,
        VUForeignInfoRuleSnapshot,
        VUForeignInfoRuleSnapshot,
        VUFreeLinearRuleSnapshot,
    ]
    assert report.snapshots[2].snapshot.reserve_thresholds == [50.0, 60.0]
    assert report.snapshots[3].snapshot.previous_policyholders_sector == [10.0, 20.0]
    assert report.snapshots[4].snapshot.active_policyholder_count == 200
    assert [entry.snapshot.rule_kind for entry in report.snapshots[6:9]] == [
        VUForeignInfoRuleKind.DUMPING,
        VUForeignInfoRuleKind.AVERAGE,
        VUForeignInfoRuleKind.ATTACK,
    ]

    payload = report.to_dict()
    assert payload["schema_version"] == (
        STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VERSION
    )
    assert payload["snapshots"][6]["snapshot"]["rule_kind"] == "dumping"
    assert payload["state_provenance_validated"] is True
    assert payload["context_values_consumed"] is True
    assert payload["state_values_consumed"] is False
    assert payload["partial_results_returned"] is False
    assert payload["execution_ready"] is False
    assert payload["runner_invoked"] is False
    assert payload["simulation_performed"] is False


def test_materialization_is_deterministic_and_does_not_change_input() -> None:
    request = _request()
    unchanged = deepcopy(request)

    first = materialize_strategy_assignment_vu_snapshots(request)
    second = materialize_strategy_assignment_vu_snapshots(request)

    assert first.to_dict() == second.to_dict()
    assert request == unchanged


def test_invalid_provenance_never_reaches_snapshot_loader(monkeypatch) -> None:
    module = importlib.import_module("ims.model.vu_rules")

    def reject_invocation(value: object) -> object:
        raise AssertionError(f"snapshot loader was invoked with {value!r}")

    monkeypatch.setattr(
        module,
        "vu_random_uniform_rule_snapshot_from_mapping",
        reject_invocation,
    )
    request = _request()
    request["state"]["period_state"]["interest_rate"] = 0.03

    report = materialize_strategy_assignment_vu_snapshots(request)

    assert report.input_valid is False
    assert report.materialization_complete is False
    assert report.snapshot_loader_invocation_count == 0
    assert report.snapshots == ()
    assert report.issues[0].code == "period_state_mismatch"


def test_snapshot_loader_failure_discards_all_partial_snapshots(monkeypatch) -> None:
    module = importlib.import_module("ims.model.vu_rules")

    def fail_for_vrvu04(mapping: dict[str, object]) -> object:
        raise ValueError(f"synthetic loader failure for {mapping['insurer_id']}")

    monkeypatch.setattr(
        module,
        "vu_net_switcher_markup_rule_snapshot_from_mapping",
        fail_for_vrvu04,
    )

    report = materialize_strategy_assignment_vu_snapshots(_request())

    assert report.input_valid is True
    assert report.materialization_complete is False
    assert report.snapshot_loader_invocation_count == 10
    assert report.snapshots == ()
    assert [issue.code for issue in report.issues] == ["snapshot_loader_rejected"]
    assert report.to_dict()["partial_results_returned"] is False


def test_materialization_does_not_invoke_vu_rule_execution(monkeypatch) -> None:
    module = importlib.import_module("ims.model.vu_rules")

    def reject_execution(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"rule execution invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(
        module,
        "apply_vu_random_uniform_rule_snapshots",
        reject_execution,
    )

    report = materialize_strategy_assignment_vu_snapshots(_request())

    assert report.materialization_complete is True
    assert report.to_dict()["execution_performed"] is False


def test_vu_materialization_contract_keeps_execution_closed() -> None:
    payload = (
        strategy_assignment_vu_snapshot_materialization_operation_contract_payload()
    )

    assert payload["schema_version"] == (
        STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VERSION
    )
    assert payload["validation_required"] is True
    assert payload["state_provenance_validation_required"] is True
    assert payload["validated_strategy_count"] == 10
    assert payload["snapshot_type_count"] == 8
    assert payload["snapshot_loader_invocation_enabled"] is True
    assert payload["snapshots_published_only_after_complete_success"] is True
    assert payload["partial_results_allowed"] is False
    assert payload["state_values_consumed"] is False
    assert payload["persistence_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["simulation_performed"] is False
