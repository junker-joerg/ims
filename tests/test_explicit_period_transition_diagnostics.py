import json
from pathlib import Path

from ims.engine.explicit_period_transition_diagnostics import (
    ExplicitPeriodTransitionDiagnosticsResult,
    diagnose_explicit_period_transitions,
    main,
)


FIXTURE_DIR = Path("tests/fixtures")
VU14_PLAN = FIXTURE_DIR / "replay_vu14_period_plan.json"
VUSK1_PLAN = FIXTURE_DIR / "replay_vusk1_period_plan.json"
VN_POLICYHOLDER_PLAN = FIXTURE_DIR / "replay_vn_policyholder_transition_plan.json"


def _minimal_transition_plan() -> dict:
    return {
        "metadata": {"purpose": "transition diagnostic test"},
        "base_snapshot": {
            "context": {"period": 0, "max_periods": 10, "run_index": 0, "rng_seed": 0},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 11, "name": "VU-11", "rule_id": 1, "rule_class": 1}],
            "policyholders": [{"entity_id": 21, "name": "VN-21", "rule_id": 5, "rule_class": 1}],
        },
        "period_updates": [
            {
                "context": {"period": 1, "max_periods": 10, "run_index": 0, "rng_seed": 101},
                "insurers": [{"entity_id": 11, "premiums_current": 1.0}],
                "policyholders": [{"entity_id": 21, "active": True}],
            },
            {
                "context": {"period": 2, "max_periods": 10, "run_index": 0, "rng_seed": 102},
                "insurers": [{"entity_id": 11, "policyholders_current": 2.0}],
                "policyholders": [{"entity_id": 21, "active": False}],
            },
        ],
    }


def test_transition_diagnostics_describes_vu14_fixture_without_execution() -> None:
    result = diagnose_explicit_period_transitions(VU14_PLAN)
    payload = result.to_dict()

    assert isinstance(result, ExplicitPeriodTransitionDiagnosticsResult)
    assert payload["status"] == "warning"
    assert payload["mode"] == "explicit_period_transition_diagnostics"
    assert payload["period_count"] == 4
    assert payload["transition_count"] == 3
    assert payload["global_periods"] == [1, 2, 3, 4]
    assert payload["transitions"][0]["from_global_period"] == 1
    assert payload["transitions"][0]["to_global_period"] == 2
    assert payload["transitions"][0]["insurer_ids"] == [14]
    assert payload["transitions"][0]["policyholder_ids"] == []
    assert payload["transitions"][0]["explicit_insurer_update_ids"] == [14]
    assert "premiums_current" in payload["transitions"][0]["explicit_input_fields"]["insurers"]
    assert payload["transitions"][0]["vu_carryover_planned"] is False
    assert payload["transitions"][0]["vn_carryover_planned"] is False
    assert payload["transitions"][0]["execution_performed"] is False
    assert payload["issues"][0]["code"] == "explicit_period_transition_no_policyholders"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False


def test_transition_diagnostics_keeps_vusk1_global_period_window() -> None:
    payload = diagnose_explicit_period_transitions(VUSK1_PLAN).to_dict()

    assert payload["status"] == "warning"
    assert payload["global_periods"] == [101, 102, 103, 104]
    assert payload["transition_count"] == 3
    assert payload["transitions"][0]["from_global_period"] == 101
    assert payload["transitions"][0]["to_global_period"] == 102
    assert payload["transitions"][0]["insurer_ids"] == [77]
    assert payload["transitions"][0]["policyholder_ids"] == []


def test_transition_diagnostics_reports_planned_carryover_without_executing(tmp_path: Path) -> None:
    data = _minimal_transition_plan()
    data["carry_forward_vu_state"] = True
    data["carry_forward_vn_state"] = True
    plan_path = tmp_path / "transition_plan.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    payload = diagnose_explicit_period_transitions(plan_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["transition_count"] == 1
    assert payload["transitions"][0]["policyholder_ids"] == [21]
    assert payload["transitions"][0]["explicit_policyholder_update_ids"] == [21]
    assert payload["transitions"][0]["explicit_input_fields"]["policyholders"] == ["active"]
    assert payload["transitions"][0]["vu_carryover_planned"] is True
    assert payload["transitions"][0]["vn_carryover_planned"] is True
    assert payload["transitions"][0]["vu_carryover_candidate_insurer_ids"] == [11]
    assert payload["transitions"][0]["vn_carryover_candidate_insurer_ids"] == [11]
    assert payload["transitions"][0]["vn_carryover_candidate_policyholder_ids"] == [21]
    assert "premiums_current_sector" in payload["transitions"][0]["carryover_source_fields"]["vu_insurers"]
    assert "claims_count_current" in payload["transitions"][0]["carryover_source_fields"]["vn_insurers"]
    assert "chosen_insurer_current" in payload["transitions"][0]["carryover_source_fields"]["vn_policyholders"]
    assert payload["transitions"][0]["vu_carryover_executed"] is False
    assert payload["transitions"][0]["vn_carryover_executed"] is False
    assert payload["execution_performed"] is False


def test_transition_diagnostics_accepts_versioned_vn_policyholder_fixture() -> None:
    payload = diagnose_explicit_period_transitions(VN_POLICYHOLDER_PLAN).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "explicit_period_transition_diagnostics"
    assert payload["period_count"] == 2
    assert payload["transition_count"] == 1
    assert payload["global_periods"] == [21, 22]
    assert payload["issues"] == []
    assert payload["transitions"][0]["from_global_period"] == 21
    assert payload["transitions"][0]["to_global_period"] == 22
    assert payload["transitions"][0]["insurer_ids"] == [11]
    assert payload["transitions"][0]["policyholder_ids"] == [21]
    assert payload["transitions"][0]["explicit_policyholder_update_ids"] == [21]
    assert payload["transitions"][0]["vn_carryover_planned"] is True
    assert payload["transitions"][0]["vu_carryover_candidate_insurer_ids"] == []
    assert payload["transitions"][0]["vn_carryover_candidate_insurer_ids"] == [11]
    assert payload["transitions"][0]["vn_carryover_candidate_policyholder_ids"] == [21]
    assert "vn_insurers" in payload["transitions"][0]["carryover_source_fields"]
    assert "vn_policyholders" in payload["transitions"][0]["carryover_source_fields"]
    assert "vu_insurers" not in payload["transitions"][0]["carryover_source_fields"]
    assert payload["transitions"][0]["vn_carryover_executed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False


def test_transition_diagnostics_rejects_non_increasing_global_periods(tmp_path: Path) -> None:
    data = _minimal_transition_plan()
    data["period_updates"][1]["context"]["period"] = 1
    plan_path = tmp_path / "bad_transition_plan.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    payload = diagnose_explicit_period_transitions(plan_path).to_dict()

    assert payload["status"] == "error"
    assert payload["issues"][0]["code"] == "explicit_period_transition_non_increasing_global_period"
    assert payload["issues"][0]["from_global_period"] == 1
    assert payload["issues"][0]["to_global_period"] == 1
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_transition_diagnostics_cli_prints_stable_json(capsys) -> None:
    exit_code = main([str(VU14_PLAN)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "explicit_period_transition_diagnostics"
    assert payload["transition_count"] == 3
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_transition_diagnostics_cli_reports_missing_plan_as_error(tmp_path: Path, capsys) -> None:
    missing_path = tmp_path / "missing_transition_plan.json"

    exit_code = main([str(missing_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"
    assert payload["issues"][0]["code"] == "explicit_period_transition_diagnostics_failed"
    assert not missing_path.exists()
