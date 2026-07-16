from ims.engine.vn_rule_runner import run_vn_settlement_period_from_mapping
from ims.model.vn_insurance_rules import VNInsuranceRuleKind


def _damage_parameters_mapping() -> dict:
    return {
        "damage_intercept_normal": [5.0, 7.0],
        "damage_factor_normal": [2.0, 3.0],
        "damage_intercept_shock": [50.0, 70.0],
        "damage_factor_shock": [20.0, 30.0],
    }


def _damage_snapshot(
    policyholder_id: int,
    *,
    trigger_draws: list[float],
    previous_wealth_sector: list[float] | None = None,
) -> dict:
    snapshot = {
        "policyholder_id": policyholder_id,
        "previous_wealth": 100.0,
        "damage_thresholds": [0.8, 0.2],
        "parameters": _damage_parameters_mapping(),
        "draws": {
            "trigger_draws": trigger_draws,
            "amount_draws": [2.0, 3.0],
        },
    }
    if previous_wealth_sector is not None:
        snapshot["previous_wealth_sector"] = previous_wealth_sector
    return snapshot


def _vn_period_scenario() -> dict:
    return {
        "context": {"period": 5, "max_periods": 6, "run_index": 0, "rng_seed": 5400},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": 11,
                "name": "VU-11",
                "premiums_current_sector": [3.0, 5.0],
                "reserves_current": [30.0, 50.0],
                "policyholders_current_sector": [0.0, 1.0],
                "claims_count_current": [0, 0],
                "claims_sum_current": [0.0, 0.0],
            },
            {
                "entity_id": 12,
                "name": "VU-12",
                "premiums_current_sector": [4.0, 6.0],
                "reserves_current": [40.0, 60.0],
                "policyholders_current_sector": [1.0, 2.0],
                "claims_count_current": [0, 0],
                "claims_sum_current": [0.0, 0.0],
            },
        ],
        "policyholders": [
            {"entity_id": 21, "name": "VN-21"},
            {"entity_id": 22, "name": "VN-22"},
            {"entity_id": 23, "name": "VN-23"},
        ],
        "vn_insurance_rule_snapshots": [
            {
                "policyholder_id": 21,
                "rule_kind": "compulsory",
                "active_insurer_ids": [11, 12],
                "draws": {"insurer_choice_draws": [0.75, 0.0]},
            },
            {
                "policyholder_id": 22,
                "rule_kind": "random",
                "parameters": {
                    "insurance_thresholds_normal": [0.1, 0.9],
                    "insurance_thresholds_shock": [0.1, 0.9],
                },
                "active_insurer_ids": [11, 12],
                "draws": {
                    "status_draws": [0.5, 0.1],
                    "insurer_choice_draws": [0.75, 0.0],
                },
            },
            {
                "policyholder_id": 23,
                "rule_kind": "preference",
                "parameters": {
                    "insurance_thresholds_normal": [0.5, 0.1],
                    "insurance_thresholds_shock": [0.5, 0.1],
                },
                "damage_probabilities": [0.6, 0.0],
                "insurer_inputs": [
                    {"insurer_id": 11, "advertising_current_sector": [1.0, 9.0]},
                    {"insurer_id": 12, "advertising_current_sector": [9.0, 1.0]},
                ],
            },
        ],
        "vn_damage_settlement_snapshots": [
            _damage_snapshot(21, trigger_draws=[0.1, 0.1], previous_wealth_sector=[120.0, 80.0]),
            _damage_snapshot(22, trigger_draws=[0.1, 0.5]),
            _damage_snapshot(23, trigger_draws=[0.1, 0.5]),
        ],
    }


def test_ninth_fachlicher_vn_damage_settlement_covers_vrvn01_to_vrvn03_decisions() -> None:
    result = run_vn_settlement_period_from_mapping(_vn_period_scenario())

    assert result.period == 5
    assert result.global_period == 5
    assert result.total_damage_settlement_applications == 3
    assert result.total_settlement_applications == 3
    assert [application.rule_kind for application in result.insurance_rule_applications] == [
        VNInsuranceRuleKind.COMPULSORY,
        VNInsuranceRuleKind.RANDOM,
        VNInsuranceRuleKind.PREFERENCE,
    ]
    assert [
        [decision.insurer_id for decision in application.decisions]
        for application in result.insurance_rule_applications
    ] == [
        [12, 11],
        [12, None],
        [12, None],
    ]

    damage_by_policyholder = {
        application.policyholder_id: application
        for application in result.damage_settlement_applications
    }
    assert damage_by_policyholder[21].damage_result.damages == [9.0, 16.0]
    assert damage_by_policyholder[21].settlement_result.paid_premium_current == [4.0, 5.0]
    assert damage_by_policyholder[21].settlement_result.end_wealth_sector_current == [107.0, 59.0]
    assert damage_by_policyholder[21].settlement_result.end_wealth_current == 66.0
    assert damage_by_policyholder[22].damage_result.damages == [9.0, 0.0]
    assert damage_by_policyholder[22].settlement_result.end_wealth_current == 87.0
    assert damage_by_policyholder[23].damage_result.damages == [9.0, 0.0]
    assert damage_by_policyholder[23].settlement_result.end_wealth_current == 87.0

    insurer_11, insurer_12 = result.insurers
    assert insurer_11.reserves_current == [30.0, 39.0]
    assert insurer_11.policyholders_current_sector == [0.0, 2.0]
    assert insurer_11.claims_count_current == [0, 1]
    assert insurer_11.claims_sum_current == [0.0, 16.0]
    assert insurer_12.reserves_current == [25.0, 60.0]
    assert insurer_12.policyholders_current_sector == [4.0, 2.0]
    assert insurer_12.claims_count_current == [3, 0]
    assert insurer_12.claims_sum_current == [27.0, 0.0]
