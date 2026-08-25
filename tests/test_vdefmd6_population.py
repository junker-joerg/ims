import json
from pathlib import Path

from ims.api.vdefmd6_population_report import (
    build_vdefmd6_population_report,
    main,
)
from ims.model.vdefmd6_population import build_vdefmd6_population


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = REPO_ROOT / "tests" / "fixtures" / "vdefmd6_population_contract.json"
PLAN_DOC = REPO_ROOT / "docs" / "plans" / "vdefmd6_population_builder_plan.md"


def _contract_data() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_vdefmd6_population_builds_complete_typed_entities() -> None:
    population = build_vdefmd6_population()

    assert population.initial_period == 1
    assert [item.entity_id for item in population.insurers] == list(range(1, 26))
    assert [item.entity_id for item in population.policyholders] == list(range(1, 201))
    assert len(population.insurer_definitions) == 25
    assert len(population.policyholder_definitions) == 200
    assert sum(item.active for item in population.insurers) == 25
    assert sum(item.active for item in population.policyholders) == 150


def test_vdefmd6_population_preserves_executable_rule_ranges() -> None:
    population = build_vdefmd6_population()

    assert [item.action.rule_id for item in population.insurer_definitions] == (
        [1] * 2
        + [2] * 2
        + [3] * 3
        + [4] * 3
        + [5] * 3
        + [6] * 3
        + [7] * 3
        + [8] * 3
        + [9] * 3
    )
    assert [item.action.rule_id for item in population.policyholder_definitions] == (
        [1] * 15
        + [2] * 15
        + [3] * 30
        + [4] * 30
        + [5] * 30
        + [6] * 30
        + [3] * 40
        + [2] * 10
    )
    assert population.policyholder_definitions[189].action.rule_id == 3
    assert population.policyholder_definitions[190].action.rule_id == 2


def test_vdefmd6_population_preserves_activation_and_action_boundaries() -> None:
    population = build_vdefmd6_population()
    definitions = (
        *population.insurer_definitions,
        *population.policyholder_definitions,
    )

    assert all(item.action.logical_time == 1 for item in definitions)
    assert all(item.activation.active_through_run == 100 for item in definitions)
    assert all(len(item.parameters) == 16 for item in definitions)
    assert {
        item.activation.activation_period
        for item in population.insurer_definitions
    } == {1}
    assert [
        item.activation.activation_period
        for item in population.policyholder_definitions
    ] == [1] * 150 + [50] * 50


def test_vdefmd6_population_preserves_selected_group_parameters() -> None:
    population = build_vdefmd6_population()
    vu = {item.entity_id: item for item in population.insurer_definitions}
    vn = {item.entity_id: item for item in population.policyholder_definitions}

    assert vu[1].parameters == (
        60.0, 70.0, 50.0, 40.0, 20.0, 20.0, 20.0, 20.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    )
    assert vu[8].aspiration_sector_1 == (0.0, 2.0, 0.0)
    assert vu[8].aspiration_sector_2 == (0.2, 0.0, 0.0)
    assert vu[11].aspiration_sector_1 == (0.0, 0.0, 0.04)
    assert vu[14].name == "Allianz"
    assert vu[14].initial_premiums == (40.0, 40.0)
    assert vu[14].initial_advertising == (10.0, 10.0)
    assert vu[15].parameters[8:] == (1.05, 1.08, 0.95, 0.97, 1.09, 1.06, 0.95, 0.97)
    assert vu[20].parameters == (0.0, 0.0, 1.0, 1.0) * 4
    assert vu[23].initial_advertising == (0.0, 0.0)
    assert vn[1].parameters[:8] == (30.0, 30.0, 5.0, 5.0) * 2
    assert vn[91].parameters[12:] == (8.0, 10.0, 8.0, 10.0)
    assert vn[151].parameters[:8] == (50.0, 50.0, 15.0, 15.0) * 2
    assert vn[191].parameters[8:12] == (0.9, 0.9, 0.9, 0.9)


def test_vdefmd6_population_report_is_ready_and_read_only() -> None:
    payload = build_vdefmd6_population_report(REPO_ROOT).to_dict()

    assert payload["status"] == "population_built"
    assert payload["contract_version"] == "pr74-v1"
    assert payload["population_ready"] is True
    assert payload["source_anchor_count"] == 13
    assert payload["summary"]["insurer_rule_class_counts"] == {
        "1": 4,
        "2": 12,
        "3": 9,
    }
    assert payload["summary"]["policyholder_rule_class_counts"] == {
        "1": 40,
        "2": 100,
        "3": 60,
    }
    assert payload["writes_performed"] is False
    assert payload["runner_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["issues"] == []


def test_vdefmd6_population_report_rejects_summary_drift(tmp_path: Path) -> None:
    contract = _contract_data()
    contract["expected"]["policyholder_count"] = 199
    path = tmp_path / "bad_population_contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_population_report(REPO_ROOT, contract_path=path)

    assert report.population_ready is False
    assert "population_summary_mismatch" in {issue.code for issue in report.issues}


def test_vdefmd6_population_report_rejects_missing_source_anchor(tmp_path: Path) -> None:
    contract = _contract_data()
    contract["source_anchors"][0]["needle"] = "missing historical definition"
    path = tmp_path / "bad_source_anchor.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_population_report(REPO_ROOT, contract_path=path)

    assert report.population_ready is False
    assert "source_anchor_missing" in {issue.code for issue in report.issues}


def test_vdefmd6_population_report_rejects_execution_boundary_drift(
    tmp_path: Path,
) -> None:
    contract = _contract_data()
    contract["boundaries"]["simulation_performed"] = True
    path = tmp_path / "bad_execution_boundary.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_population_report(REPO_ROOT, contract_path=path)

    assert report.population_ready is False
    assert "execution_boundary_mismatch" in {issue.code for issue in report.issues}


def test_vdefmd6_population_cli_and_plan_keep_execution_closed(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)
    plan = PLAN_DOC.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["population_ready"] is True
    assert payload["execution_performed"] is False
    assert "151-190" in plan and "191-200" in plan
    assert "151-180" in plan and "181-200" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan
