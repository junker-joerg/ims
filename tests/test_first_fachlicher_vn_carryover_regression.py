from pathlib import Path

from ims.engine.explicit_period_transition_diagnostics import (
    VN_CARRYOVER_INSURER_SOURCE_FIELDS,
    VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS,
)
from ims.engine.explicit_transition_carryover_probe import (
    probe_explicit_transition_carryover,
)


VN_POLICYHOLDER_PLAN = Path("tests/fixtures/replay_vn_policyholder_transition_plan.json")
BOUNDARY_FLAGS = (
    "writes_performed",
    "execution_performed",
    "simulation_performed",
    "automatic_historical_rule_selection_performed",
)


def test_first_fachlicher_vn_carryover_slice_regression() -> None:
    payload = probe_explicit_transition_carryover(
        VN_POLICYHOLDER_PLAN,
        apply_vn=True,
    ).to_dict()
    transition = payload["transitions"][0]

    assert payload["status"] == "ok"
    assert payload["mode"] == "explicit_transition_carryover_probe"
    assert payload["plan_path"].replace("\\", "/").endswith(
        "tests/fixtures/replay_vn_policyholder_transition_plan.json"
    )
    assert payload["transition_count"] == 1
    assert payload["vu_carryover_requested"] is False
    assert payload["vn_carryover_requested"] is True
    assert payload["in_memory_carryover_performed"] is True
    assert payload["issues"] == []

    assert transition["from_period"] == 1
    assert transition["to_period"] == 2
    assert transition["from_global_period"] == 21
    assert transition["to_global_period"] == 22
    assert transition["vu_carryover_requested"] is False
    assert transition["vn_carryover_requested"] is True
    assert transition["vu_carryover_planned"] is False
    assert transition["vn_carryover_planned"] is True
    assert transition["vu_carryover_executed"] is False
    assert transition["vn_carryover_executed"] is True
    assert transition["carried_insurer_ids"] == [11]
    assert transition["carried_policyholder_ids"] == [21]
    assert transition["diagnostic_candidate_ids_match"] is True
    assert transition["previous_result_source"] == "explicit_fixture_snapshot"
    assert transition["issues"] == []

    assert set(transition["source_fields"]) == {"vn_insurers", "vn_policyholders"}
    assert transition["source_fields"]["vn_insurers"] == list(VN_CARRYOVER_INSURER_SOURCE_FIELDS)
    assert transition["source_fields"]["vn_policyholders"] == list(VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS)
    assert transition["carried_insurer_state"]["11"]["active_prev"] is True
    assert transition["carried_insurer_state"]["11"]["premiums_current"] == 101.0
    assert transition["carried_insurer_state"]["11"]["policyholders_current"] == 1.0
    assert transition["carried_policyholder_state"]["21"]["active_prev"] is True
    assert transition["carried_policyholder_state"]["21"]["insurer_id"] == 11
    assert transition["carried_policyholder_state"]["21"]["chosen_insurer_current"] == 11
    assert transition["carried_policyholder_state"]["21"]["insured_current"] == 1.0
    assert transition["carried_policyholder_state"]["21"]["end_wealth_current"] == 999.0

    assert {flag: payload[flag] for flag in BOUNDARY_FLAGS} == {
        "writes_performed": False,
        "execution_performed": False,
        "simulation_performed": False,
        "automatic_historical_rule_selection_performed": False,
    }
