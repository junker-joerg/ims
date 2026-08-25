import json
from pathlib import Path

import pytest

from ims.api.vdefmd6_action_seed_report import (
    build_vdefmd6_action_seed_report,
    main,
)
from ims.model.vdefmd6_action_seed import (
    ModernSeedPolicy,
    build_vdefmd6_action_seed_plan,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = REPO_ROOT / "tests" / "fixtures" / "vdefmd6_action_seed_contract.json"
PLAN_DOC = REPO_ROOT / "docs" / "plans" / "vdefmd6_action_seed_plan.md"
MIGRATION_DOC = REPO_ROOT / "docs" / "migration" / "vdefmd6_action_seed_contract.md"


def _contract_data() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _slot(plan, period: int, logical_time: int):
    return next(
        item
        for item in plan.slots
        if item.period == period and item.logical_time == logical_time
    )


def test_vdefmd6_action_plan_covers_effective_slots_and_activation_boundary() -> None:
    plan = build_vdefmd6_action_seed_plan(base_seed=1234)

    assert len(plan.slots) == 200
    assert sum(len(item.invocations) for item in plan.slots) == 20250
    assert len(_slot(plan, 1, 1).invocations) == 176
    assert len(_slot(plan, 49, 1).invocations) == 176
    assert len(_slot(plan, 50, 1).invocations) == 226
    assert len(_slot(plan, 100, 1).invocations) == 226
    assert len(_slot(plan, 1, 10).invocations) == 1

    period_49 = _slot(plan, 49, 1).invocations
    period_50 = _slot(plan, 50, 1).invocations
    assert not any(
        item.subject_type == "policyholder" and item.subject_id == 151
        for item in period_49
    )
    vn_151 = next(
        item
        for item in period_50
        if item.subject_type == "policyholder" and item.subject_id == 151
    )
    vn_191 = next(
        item
        for item in period_50
        if item.subject_type == "policyholder" and item.subject_id == 191
    )
    assert (vn_151.rule_id, vn_151.activation_period) == (3, 50)
    assert (vn_191.rule_id, vn_191.activation_period) == (2, 50)


def test_vdefmd6_same_slot_order_is_only_deterministic_serialization() -> None:
    plan = build_vdefmd6_action_seed_plan(base_seed=1)
    invocations = _slot(plan, 50, 1).invocations

    assert invocations[0].subject_type == "central"
    assert [item.subject_id for item in invocations[1:26]] == list(range(1, 26))
    assert [item.subject_id for item in invocations[26:]] == list(range(1, 201))
    assert plan.same_slot_serialization == ("central", "insurer", "policyholder")
    assert plan.historical_same_slot_order_claimed is False
    assert plan.scheduler_started is False
    assert plan.rng_draws_performed is False
    assert plan.simulation_performed is False


def test_modern_seed_policy_is_explicit_and_reproducible() -> None:
    first = build_vdefmd6_action_seed_plan(base_seed=20260001)
    second = build_vdefmd6_action_seed_plan(base_seed=20260001)
    other = build_vdefmd6_action_seed_plan(base_seed=20260011)

    assert first.run_seeds == second.run_seeds
    assert first.run_seeds[:2] == (20260001, 20260002)
    assert first.run_seeds[-1] == 20260100
    assert first.run_seeds != other.run_seeds
    assert first.seed_policy.historical_seed_known is False


@pytest.mark.parametrize("base_seed", [-1, 1.5, True, "1"])
def test_modern_seed_policy_rejects_invalid_base_seed(base_seed) -> None:
    with pytest.raises(ValueError, match="base_seed"):
        ModernSeedPolicy(base_seed=base_seed)


@pytest.mark.parametrize("run_number", [0, 101, 1.5, True])
def test_modern_seed_policy_rejects_invalid_run_number(run_number) -> None:
    policy = ModernSeedPolicy(base_seed=10)
    with pytest.raises(ValueError, match="run_number"):
        policy.seed_for_run(run_number)


def test_vdefmd6_action_seed_report_is_ready_and_read_only() -> None:
    payload = build_vdefmd6_action_seed_report(REPO_ROOT).to_dict()

    assert payload["status"] == "action_seed_plan_built"
    assert payload["contract_version"] == "pr75-v1"
    assert payload["source_anchor_count"] == 13
    assert payload["summary"]["invocation_count"] == 20250
    assert payload["modern_seed_policy_ready"] is True
    assert payload["historical_seed_known"] is False
    assert payload["same_slot_serialization_is_execution_order"] is False
    assert payload["historical_same_slot_order_claimed"] is False
    assert payload["scheduler_started"] is False
    assert payload["rng_draws_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["issues"] == []


def test_vdefmd6_action_seed_report_rejects_seed_policy_drift(tmp_path: Path) -> None:
    contract = _contract_data()
    contract["seed_policy"]["historical_seed_known"] = True
    path = tmp_path / "bad_seed_contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_action_seed_report(REPO_ROOT, contract_path=path)

    assert report.action_seed_plan_ready is False
    assert "seed_policy_mismatch" in {issue.code for issue in report.issues}


def test_vdefmd6_action_seed_report_rejects_same_slot_claim_drift(tmp_path: Path) -> None:
    contract = _contract_data()
    contract["same_slot"]["historical_order_claimed"] = True
    path = tmp_path / "bad_same_slot_contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_action_seed_report(REPO_ROOT, contract_path=path)

    assert report.action_seed_plan_ready is False
    assert "same_slot_boundary_mismatch" in {issue.code for issue in report.issues}


def test_vdefmd6_action_seed_report_rejects_missing_source_anchor(tmp_path: Path) -> None:
    contract = _contract_data()
    contract["source_anchors"][0]["needle"] = "missing action declaration"
    path = tmp_path / "bad_anchor_contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_action_seed_report(REPO_ROOT, contract_path=path)

    assert report.action_seed_plan_ready is False
    assert "source_anchor_missing" in {issue.code for issue in report.issues}


def test_vdefmd6_action_seed_cli_and_plan_keep_execution_closed(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)
    plan = PLAN_DOC.read_text(encoding="utf-8")
    migration = MIGRATION_DOC.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["action_seed_plan_ready"] is True
    assert payload["execution_performed"] is False
    assert "Darstellungsordnung" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan
    assert "PR 76" in plan
    assert "20.250 wirksame Aufrufe" in migration
    assert "sieben geplante Schritte" in migration
