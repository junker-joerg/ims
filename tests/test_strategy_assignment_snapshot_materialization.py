from copy import deepcopy
import importlib
import json
from pathlib import Path

from ims.model.vn_insurance_rules import (
    VNCompulsoryInsuranceRuleDraws,
    VNInsuranceRuleKind,
    VNPreferenceInsurerInput,
    VNRandomInsuranceRuleParameters,
    VNSampleSearchInsurerInput,
    VNSearchInsuranceHistoryEntry,
)
from ims.model.vn_rules import VNInsuranceDecision
from ims.strategies import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION,
    materialize_strategy_assignment_snapshots,
    strategy_assignment_snapshot_materialization_operation_contract_payload,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_assignment_snapshot_materialization_validation_v1.json"
)


def _request() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _period_one_request() -> dict[str, object]:
    request = _request()
    request["context"]["period"] = 1
    for entry in request["context"]["entries"]:
        values = entry["values"]
        values["initial_decisions"] = [
            {
                "sector_index": 0,
                "insured": True,
                "insurer_id": 1,
                "premium": 1.1,
            },
            {"sector_index": 1, "insured": False, "premium": 0.0},
        ]
        values["draws"] = {"not_consumed_in_period_one": True}
        values["insurer_inputs"] = [{"not_consumed_in_period_one": True}]
        values["history"] = [{"not_consumed_in_period_one": True}]
    return request


def test_materializes_all_six_vn_snapshots_with_typed_nested_values() -> None:
    report = materialize_strategy_assignment_snapshots(_request())

    assert report.materialization_complete is True
    assert report.input_valid is True
    assert report.expected_snapshot_count == 6
    assert report.snapshot_loader_invocation_count == 6
    assert report.nested_loader_invocation_count == 7
    assert report.issues == ()
    assert [entry.strategy_id for entry in report.snapshots] == [
        f"vn.vrvn{index:02d}" for index in range(1, 7)
    ]

    snapshots = [entry.snapshot for entry in report.snapshots]
    assert snapshots[0].rule_kind is VNInsuranceRuleKind.COMPULSORY
    assert isinstance(snapshots[0].draws, VNCompulsoryInsuranceRuleDraws)
    assert isinstance(snapshots[1].parameters, VNRandomInsuranceRuleParameters)
    assert isinstance(snapshots[2].insurer_inputs[0], VNPreferenceInsurerInput)
    assert isinstance(snapshots[3].history[0], VNSearchInsuranceHistoryEntry)
    assert isinstance(snapshots[4].insurer_inputs[0], VNSampleSearchInsurerInput)
    assert isinstance(snapshots[5].insurer_inputs[0], VNSampleSearchInsurerInput)

    payload = report.to_dict()
    assert payload["schema_version"] == (
        STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION
    )
    assert payload["snapshot_count"] == 6
    assert payload["snapshots"][3]["snapshot"]["rule_kind"] == "search_history"
    assert payload["partial_results_returned"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_ready"] is False
    assert payload["runner_invoked"] is False
    assert payload["simulation_performed"] is False


def test_period_one_materializes_only_typed_initial_decisions() -> None:
    report = materialize_strategy_assignment_snapshots(_period_one_request())

    assert report.materialization_complete is True
    assert report.snapshot_loader_invocation_count == 6
    assert report.nested_loader_invocation_count == 6
    for entry in report.snapshots:
        snapshot = entry.snapshot
        assert isinstance(snapshot.initial_decisions[0], VNInsuranceDecision)
        assert snapshot.draws is None
        assert snapshot.insurer_inputs is None
        assert snapshot.history is None
        assert snapshot.active_insurer_ids is None
        assert snapshot.market_damage_indicator is None


def test_invalid_input_never_reaches_snapshot_loader(monkeypatch) -> None:
    module = importlib.import_module("ims.model.vn_insurance_rules")

    def reject_invocation(value: object) -> object:
        raise AssertionError(f"snapshot loader was invoked with {value!r}")

    monkeypatch.setattr(
        module,
        "vn_insurance_rule_snapshot_from_mapping",
        reject_invocation,
    )
    request = _request()
    invalid = deepcopy(request)
    invalid["context"]["entries"][4]["values"]["draws"][
        "insurer_choice_draws_by_sector"
    ][0] = [0.1]

    report = materialize_strategy_assignment_snapshots(invalid)

    assert report.input_valid is False
    assert report.materialization_complete is False
    assert report.snapshot_loader_invocation_count == 0
    assert report.nested_loader_invocation_count == 0
    assert report.snapshots == ()
    assert report.issues[0].code == "sample_draw_count_insufficient"


def test_snapshot_loader_failure_discards_all_partial_snapshots(monkeypatch) -> None:
    module = importlib.import_module("ims.model.vn_insurance_rules")
    original = module.vn_insurance_rule_snapshot_from_mapping
    invoked_ids: list[int] = []

    def fail_for_four(mapping: dict[str, object]) -> object:
        target_id = mapping["policyholder_id"]
        assert isinstance(target_id, int)
        invoked_ids.append(target_id)
        if target_id == 4:
            raise ValueError("synthetic loader failure")
        return original(mapping)

    monkeypatch.setattr(
        module,
        "vn_insurance_rule_snapshot_from_mapping",
        fail_for_four,
    )

    report = materialize_strategy_assignment_snapshots(_request())

    assert invoked_ids == [1, 2, 3, 4, 5, 6]
    assert report.input_valid is True
    assert report.materialization_complete is False
    assert report.snapshot_loader_invocation_count == 6
    assert report.snapshots == ()
    assert [issue.code for issue in report.issues] == ["snapshot_loader_rejected"]
    assert report.to_dict()["partial_results_returned"] is False


def test_materialization_does_not_invoke_rule_execution(monkeypatch) -> None:
    module = importlib.import_module("ims.model.vn_insurance_rules")

    def reject_execution(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"rule execution invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(module, "apply_vn_insurance_rule_snapshots", reject_execution)

    report = materialize_strategy_assignment_snapshots(_request())

    assert report.materialization_complete is True
    assert report.to_dict()["execution_performed"] is False


def test_materialization_operation_contract_keeps_execution_closed() -> None:
    payload = strategy_assignment_snapshot_materialization_operation_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION
    )
    assert payload["validation_required"] is True
    assert payload["validated_rule_count"] == 6
    assert payload["snapshot_loader_invocation_enabled"] is True
    assert payload["snapshots_published_only_after_complete_success"] is True
    assert payload["partial_results_allowed"] is False
    assert payload["persistence_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["simulation_performed"] is False
