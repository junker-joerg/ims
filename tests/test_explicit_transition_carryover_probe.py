import copy
import json
from pathlib import Path

from ims.engine.explicit_transition_carryover_probe import (
    main,
    probe_explicit_transition_carryover,
)


FIXTURE_DIR = Path("tests/fixtures")
VU14_PLAN = FIXTURE_DIR / "replay_vu14_period_plan.json"
VN_POLICYHOLDER_PLAN = FIXTURE_DIR / "replay_vn_policyholder_transition_plan.json"


def _vu_carryover_plan() -> dict:
    return {
        "metadata": {"purpose": "VU carryover probe test"},
        "carry_forward_vu_state": True,
        "base_snapshot": {
            "context": {"period": 0, "logtime": 0, "max_periods": 10, "run_index": 1, "rng_seed": 3000},
            "bav": {"entity_id": 1, "name": "Probe-BAV"},
            "insurers": [
                {
                    "entity_id": 31,
                    "name": "Probe VU 31",
                    "active": True,
                    "active_prev": True,
                    "rule_id": 1,
                    "rule_class": 1,
                    "premiums_current": 10.0,
                    "advertising_current": 2.0,
                    "reserves_current": [30.0, 40.0],
                    "policyholders_current": 5.0,
                }
            ],
            "policyholders": [],
        },
        "period_updates": [
            {
                "context": {"period": 1, "run_index": 1, "rng_seed": 3001},
                "insurers": [{"entity_id": 31, "premiums_current": 111.0, "policyholders_current": 6.0}],
                "policyholders": [],
            },
            {
                "context": {"period": 2, "run_index": 1, "rng_seed": 3002},
                "insurers": [{"entity_id": 31, "premiums_current": 222.0, "policyholders_current": 7.0}],
                "policyholders": [],
            },
        ],
    }


def _write_plan(tmp_path: Path, data: dict, name: str = "plan.json") -> Path:
    plan_path = tmp_path / name
    plan_path.write_text(json.dumps(data), encoding="utf-8")
    return plan_path


def test_carryover_probe_without_opt_in_does_not_apply_state() -> None:
    payload = probe_explicit_transition_carryover(VN_POLICYHOLDER_PLAN).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "explicit_transition_carryover_probe"
    assert payload["transition_count"] == 1
    assert payload["vu_carryover_requested"] is False
    assert payload["vn_carryover_requested"] is False
    assert payload["in_memory_carryover_performed"] is False
    assert payload["transitions"][0]["vn_carryover_planned"] is True
    assert payload["transitions"][0]["vn_carryover_executed"] is False
    assert payload["transitions"][0]["carried_insurer_ids"] == []
    assert payload["transitions"][0]["carried_policyholder_ids"] == []
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False


def test_carryover_probe_applies_vn_opt_in_with_diagnostic_candidate_ids() -> None:
    payload = probe_explicit_transition_carryover(VN_POLICYHOLDER_PLAN, apply_vn=True).to_dict()
    transition = payload["transitions"][0]

    assert payload["status"] == "ok"
    assert payload["vn_carryover_requested"] is True
    assert payload["in_memory_carryover_performed"] is True
    assert transition["from_global_period"] == 21
    assert transition["to_global_period"] == 22
    assert transition["vn_carryover_planned"] is True
    assert transition["vn_carryover_executed"] is True
    assert transition["carried_insurer_ids"] == [11]
    assert transition["carried_policyholder_ids"] == [21]
    assert transition["diagnostic_candidate_ids_match"] is True
    assert transition["previous_result_source"] == "explicit_fixture_snapshot"
    assert "vn_insurers" in transition["source_fields"]
    assert "vn_policyholders" in transition["source_fields"]
    assert transition["carried_insurer_state"]["11"]["premiums_current"] == 101.0
    assert transition["carried_policyholder_state"]["21"]["end_wealth_current"] == 999.0
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_carryover_probe_applies_vu_opt_in_for_planned_fixture(tmp_path: Path) -> None:
    plan_path = _write_plan(tmp_path, _vu_carryover_plan())

    payload = probe_explicit_transition_carryover(plan_path, apply_vu=True).to_dict()
    transition = payload["transitions"][0]

    assert payload["status"] == "warning"
    assert payload["issues"][0]["code"] == "explicit_period_transition_no_policyholders"
    assert transition["vu_carryover_requested"] is True
    assert transition["vu_carryover_planned"] is True
    assert transition["vu_carryover_executed"] is True
    assert transition["carried_insurer_ids"] == [31]
    assert transition["diagnostic_candidate_ids_match"] is True
    assert transition["previous_result_source"] == "explicit_fixture_snapshot"
    assert "vu_insurers" in transition["source_fields"]
    assert transition["carried_insurer_state"]["31"]["premiums_current"] == 111.0
    assert transition["carried_insurer_state"]["31"]["policyholders_current"] == 6.0


def test_carryover_probe_reports_requested_but_unplanned_vu_carryover() -> None:
    payload = probe_explicit_transition_carryover(VU14_PLAN, apply_vu=True).to_dict()
    transition = payload["transitions"][0]

    assert payload["status"] == "warning"
    assert transition["vu_carryover_requested"] is True
    assert transition["vu_carryover_planned"] is False
    assert transition["vu_carryover_executed"] is False
    assert transition["carried_insurer_ids"] == []
    assert transition["issues"][0]["code"] == "explicit_transition_carryover_vu_not_planned"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_carryover_probe_rejects_non_increasing_periods(tmp_path: Path) -> None:
    data = _vu_carryover_plan()
    data = copy.deepcopy(data)
    data["period_updates"][1]["context"]["period"] = 1
    plan_path = _write_plan(tmp_path, data, name="bad_plan.json")

    payload = probe_explicit_transition_carryover(plan_path, apply_vu=True).to_dict()

    assert payload["status"] == "error"
    assert payload["issues"][0]["code"] == "explicit_period_transition_non_increasing_global_period"
    assert payload["transitions"] == []
    assert payload["writes_performed"] is False
    assert payload["simulation_performed"] is False


def test_carryover_probe_cli_prints_stable_json(capsys) -> None:
    exit_code = main(["--apply-vn", str(VN_POLICYHOLDER_PLAN)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "explicit_transition_carryover_probe"
    assert payload["vn_carryover_requested"] is True
    assert payload["transitions"][0]["vn_carryover_executed"] is True
    assert payload["writes_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
