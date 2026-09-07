from dataclasses import replace
import importlib

from ims.strategies import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION,
    VU_SNAPSHOT_MATERIALIZATION_TARGETS,
    VU_SNAPSHOT_RUNTIME_FIELDS,
    strategy_assignment_vu_snapshot_materialization_contract_payload,
    strategy_vu_snapshot_materialization_contract_issues,
)


def test_vu_materialization_inventory_covers_all_targets_and_open_fields() -> None:
    assert strategy_vu_snapshot_materialization_contract_issues() == ()

    payload = strategy_assignment_vu_snapshot_materialization_contract_payload()
    targets = {target["strategy_id"]: target for target in payload["targets"]}

    assert payload["schema_version"] == (
        STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION
    )
    assert set(targets) == {f"vu.vrvu{index:02d}" for index in range(1, 11)}
    assert payload["strategy_count"] == 10
    assert payload["vdefmd6_strategy_count"] == 9
    assert payload["outside_vdefmd6_strategy_count"] == 1
    assert payload["snapshot_type_count"] == 8
    assert payload["snapshot_collection_count"] == 8
    assert len(payload["runtime_field_definitions"]) == 9
    assert len(payload["external_state_dependencies"]) == 5
    assert payload["contract_issue_count"] == 0

    fields_by_strategy = {strategy_id: set() for strategy_id in targets}
    for definition in payload["runtime_field_definitions"]:
        for strategy_id in definition["strategy_ids"]:
            fields_by_strategy[strategy_id].add(definition["field_name"])
    for strategy_id, target in targets.items():
        assert fields_by_strategy[strategy_id] == set(target["open_snapshot_fields"])


def test_vu_materialization_inventory_keeps_foreign_info_variants_and_vrvu10_boundary() -> None:
    payload = strategy_assignment_vu_snapshot_materialization_contract_payload()
    targets = {target["strategy_id"]: target for target in payload["targets"]}
    foreign_targets = [targets[f"vu.vrvu{index:02d}"] for index in range(7, 10)]

    assert {target["snapshot_type"] for target in foreign_targets} == {
        "VUForeignInfoRuleSnapshot"
    }
    assert {target["snapshot_loader"] for target in foreign_targets} == {
        "vu_foreign_info_rule_snapshot_from_mapping"
    }
    assert [target["rule_kind"] for target in foreign_targets] == [
        "dumping",
        "average",
        "attack",
    ]
    assert targets["vu.vrvu10"]["included_in_vdefmd6"] is False
    assert targets["vu.vrvu04"]["rule_period_condition"] == "period_at_least_three"


def test_vu_materialization_inventory_does_not_invoke_snapshot_loaders(monkeypatch) -> None:
    vu_rules = importlib.import_module("ims.model.vu_rules")

    def fail_if_called(mapping):
        raise AssertionError(f"snapshot loader was called with {mapping!r}")

    monkeypatch.setattr(
        vu_rules,
        "vu_random_uniform_rule_snapshot_from_mapping",
        fail_if_called,
    )

    assert strategy_vu_snapshot_materialization_contract_issues() == ()
    payload = strategy_assignment_vu_snapshot_materialization_contract_payload()
    assert payload["snapshot_loader_invocation_enabled"] is False
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["simulation_performed"] is False


def test_vu_materialization_inventory_reports_target_and_field_drift() -> None:
    targets = (
        replace(VU_SNAPSHOT_MATERIALIZATION_TARGETS[0], snapshot_loader="missing_loader"),
        *VU_SNAPSHOT_MATERIALIZATION_TARGETS[1:],
    )
    runtime_fields = (
        replace(
            VU_SNAPSHOT_RUNTIME_FIELDS[0],
            strategy_ids=VU_SNAPSHOT_RUNTIME_FIELDS[0].strategy_ids[:-1],
        ),
        *VU_SNAPSHOT_RUNTIME_FIELDS[1:],
    )

    issues = strategy_vu_snapshot_materialization_contract_issues(
        targets=targets,
        runtime_fields=runtime_fields,
    )

    assert "VU-Snapshotziel weicht von PR110 ab: vu.vrvu01" in issues
    assert "VU-Snapshotloader fehlt: vu.vrvu01" in issues
    assert "Offene VU-Snapshotfelder sind nicht exakt dokumentiert: vu.vrvu10" in issues
