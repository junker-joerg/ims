from ims.engine.vn_rule_runner import run_vn_settlement_multi_period_from_mappings


def _best_info_snapshot() -> dict:
    return {
        "policyholder_id": 21,
        "rule_kind": "best_info",
        "parameters": {
            "insurance_thresholds_normal": [0.5, 0.1],
            "insurance_thresholds_shock": [0.5, 0.1],
        },
        "market_damage_indicator": 0.5,
        "insurer_inputs": [
            {"insurer_id": 11, "premiums_current_sector": [6.0, 5.0]},
            {"insurer_id": 12, "premiums_current_sector": [4.0, 7.0]},
        ],
        "information_cost_per_insurer": 1.0,
    }


def _damage_parameters_mapping() -> dict:
    return {
        "damage_intercept_normal": [5.0, 7.0],
        "damage_factor_normal": [2.0, 3.0],
        "damage_intercept_shock": [50.0, 70.0],
        "damage_factor_shock": [20.0, 30.0],
    }


def _insurers() -> list[dict]:
    return [
        {
            "entity_id": 11,
            "name": "VU-11",
            "premiums_current_sector": [4.0, 6.0],
            "reserves_current": [40.0, 60.0],
            "policyholders_current_sector": [1.0, 2.0],
        },
        {
            "entity_id": 12,
            "name": "VU-12",
            "premiums_current_sector": [4.0, 6.0],
            "reserves_current": [40.0, 60.0],
            "policyholders_current_sector": [1.0, 2.0],
        },
    ]


def _first_period_scenario() -> dict:
    return {
        "context": {"period": 5, "max_periods": 6, "run_index": 0},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": _insurers(),
        "policyholders": [
            {
                "entity_id": 21,
                "name": "VN-21",
                "insurer_id": 11,
                "insured_current": 0.0,
                "chosen_insurer_current": 11,
                "chosen_insurer_sector_current": [11, 11],
                "paid_premium_current": [0.0, 0.0],
                "end_wealth_current": 100.0,
            }
        ],
        "vn_insurance_rule_snapshots": [_best_info_snapshot()],
        "vn_damage_settlement_snapshots": [
            {
                "policyholder_id": 21,
                "previous_wealth": 100.0,
                "damage_thresholds": [0.8, 0.2],
                "parameters": _damage_parameters_mapping(),
                "draws": {
                    "trigger_draws": [0.1, 0.5],
                    "amount_draws": [2.0, 3.0],
                },
            }
        ],
    }


def _second_period_scenario() -> dict:
    return {
        "context": {"period": 6, "max_periods": 6, "run_index": 0},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": _insurers(),
        "policyholders": [
            {
                "entity_id": 21,
                "name": "VN-21",
                "insurer_id": 11,
                "insured_current": 1.0,
                "chosen_insurer_current": 11,
                "chosen_insurer_sector_current": [11, 11],
                "paid_premium_current": [1.0, 1.0],
                "self_damage_current": [1.0, 1.0],
                "claim_sum_current": [1.0, 1.0],
                "end_wealth_sector_current": [50.0, 50.0],
                "end_wealth_current": 50.0,
            }
        ],
    }


def test_fourth_fachlicher_vn_best_info_result_is_carried_to_next_period() -> None:
    result = run_vn_settlement_multi_period_from_mappings(
        [_first_period_scenario(), _second_period_scenario()],
        carry_forward_vn_state=True,
    )

    assert result.processed_local_periods == [5, 6]
    assert result.processed_global_periods == [5, 6]
    assert result.total_insurance_rule_applications == 1
    assert result.total_damage_settlement_applications == 1
    assert result.total_settlement_applications == 1
    assert len(result.carryovers) == 1
    assert result.carryovers[0].from_period == 5
    assert result.carryovers[0].to_period == 6
    assert result.carryovers[0].from_global_period == 5
    assert result.carryovers[0].to_global_period == 6
    assert result.carryovers[0].insurer_ids == [11, 12]
    assert result.carryovers[0].policyholder_ids == [21]

    first_period = result.period_results[0]
    rule_application = first_period.insurance_rule_applications[0]
    assert [decision.insurer_id for decision in rule_application.decisions] == [12, None]
    assert rule_application.result.information_cost == 4.0
    assert first_period.damage_settlement_applications[0].damage_result.damages == [9.0, 0.0]
    assert first_period.policyholders[0].chosen_insurer_sector_current == [12, None]
    assert first_period.policyholders[0].paid_premium_current == [4.0, 0.0]
    assert first_period.policyholders[0].self_damage_current == [0.0, 0.0]
    assert first_period.policyholders[0].claim_sum_current == [9.0, 0.0]
    assert first_period.policyholders[0].end_wealth_current == 87.0

    second_period = result.period_results[1]
    assert second_period.insurance_rule_applications == []
    assert second_period.damage_settlement_applications == []
    assert second_period.settlement_applications == []
    carried_policyholder = second_period.policyholders[0]
    assert carried_policyholder.active_prev is True
    assert carried_policyholder.insurer_id == 12
    assert carried_policyholder.chosen_insurer_current == 12
    assert carried_policyholder.chosen_insurer_sector_current == [12, None]
    assert carried_policyholder.insured_prev == 1.0
    assert carried_policyholder.insured_current == 1.0
    assert carried_policyholder.paid_premium_current == [4.0, 0.0]
    assert carried_policyholder.self_damage_current == [0.0, 0.0]
    assert carried_policyholder.claim_sum_current == [9.0, 0.0]
    assert carried_policyholder.end_wealth_sector_current == [87.0, 100.0]
    assert carried_policyholder.end_wealth_current == 87.0
