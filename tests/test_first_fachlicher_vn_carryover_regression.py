from pathlib import Path

from ims.engine.explicit_transition_carryover_probe import (
    probe_explicit_transition_carryover,
)


VN_POLICYHOLDER_PLAN = Path("tests/fixtures/replay_vn_policyholder_transition_plan.json")


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

    assert transition["source_fields"]["vn_insurers"] == [
        "active",
        "advertising_current_sector",
        "claims_count_current",
        "claims_sum_current",
        "policyholders_current",
        "policyholders_current_sector",
        "premiums_current_sector",
        "reserves_current",
    ]
    assert transition["source_fields"]["vn_policyholders"] == [
        "active",
        "chosen_insurer_current",
        "chosen_insurer_sector_current",
        "claim_sum_current",
        "end_wealth_current",
        "end_wealth_sector_current",
        "insured_current",
        "insured_current_sector",
        "insurer_id",
        "paid_premium_current",
        "self_damage_current",
    ]
    assert transition["carried_insurer_state"]["11"]["active_prev"] is True
    assert transition["carried_insurer_state"]["11"]["premiums_current"] == 101.0
    assert transition["carried_insurer_state"]["11"]["policyholders_current"] == 1.0
    assert transition["carried_policyholder_state"]["21"]["active_prev"] is True
    assert transition["carried_policyholder_state"]["21"]["insurer_id"] == 11
    assert transition["carried_policyholder_state"]["21"]["chosen_insurer_current"] == 11
    assert transition["carried_policyholder_state"]["21"]["insured_current"] == 1.0
    assert transition["carried_policyholder_state"]["21"]["end_wealth_current"] == 999.0

    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
