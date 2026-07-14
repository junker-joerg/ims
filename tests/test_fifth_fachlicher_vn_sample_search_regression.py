from ims.engine.vn_rule_runner import run_vn_settlement_period_from_mapping
from ims.model.vn_insurance_rules import (
    VNInsuranceRuleKind,
    apply_vn_insurance_rule_snapshots,
    load_vn_insurance_rule_snapshots_from_mapping,
)


def _sample_search_snapshot() -> dict:
    return {
        "policyholder_id": 21,
        "rule_kind": "sample_search",
        "parameters": {
            "insurance_thresholds_normal": [0.5, 0.1],
            "insurance_thresholds_shock": [0.5, 0.1],
            "sample_sizes_normal": [2, 1],
            "sample_sizes_shock": [2, 1],
        },
        "market_damage_indicator": 0.5,
        "insurer_inputs": [
            {"insurer_id": 11, "premiums_current_sector": [6.0, 5.0]},
            {"insurer_id": 12, "premiums_current_sector": [4.0, 7.0]},
        ],
        "draws": {
            "insurer_choice_draws_by_sector": [
                [0.0, 0.99],
                [0.0],
            ]
        },
        "information_cost_per_sample": 1.0,
    }


def _damage_parameters_mapping() -> dict:
    return {
        "damage_intercept_normal": [5.0, 7.0],
        "damage_factor_normal": [2.0, 3.0],
        "damage_intercept_shock": [50.0, 70.0],
        "damage_factor_shock": [20.0, 30.0],
    }


def _vn_period_scenario() -> dict:
    return {
        "context": {"period": 5, "max_periods": 6, "run_index": 0},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
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
        ],
        "policyholders": [{"entity_id": 21, "name": "VN-21"}],
        "vn_insurance_rule_snapshots": [_sample_search_snapshot()],
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


def test_fifth_fachlicher_vn_sample_search_snapshot_regression() -> None:
    snapshots = load_vn_insurance_rule_snapshots_from_mapping([_sample_search_snapshot()])

    applications = apply_vn_insurance_rule_snapshots(snapshots, period=5)

    assert len(applications) == 1
    application = applications[0]
    assert application.policyholder_id == 21
    assert application.rule_kind is VNInsuranceRuleKind.SAMPLE_SEARCH
    assert [decision.sector_index for decision in application.decisions] == [0, 1]
    assert [decision.insured for decision in application.decisions] == [True, False]
    assert [decision.insurer_id for decision in application.decisions] == [12, None]
    assert [decision.premium for decision in application.decisions] == [4.0, None]
    assert application.result.chosen_insurer_ids == [12, None]
    assert application.result.selected_insurer_ids == [12, 11]
    assert application.result.selected_premiums == [4.0, 5.0]
    assert application.result.sampled_insurer_ids == [[11, 12], [11]]
    assert application.result.used_insurer_choice_draws_by_sector == [[0.0, 0.99], [0.0]]
    assert application.result.information_cost == 3.0


def test_fifth_fachlicher_vn_sample_search_snapshot_feeds_runner_boundary() -> None:
    result = run_vn_settlement_period_from_mapping(_vn_period_scenario())

    assert result.period == 5
    assert result.global_period == 5
    assert len(result.insurance_rule_applications) == 1
    assert result.total_damage_settlement_applications == 1
    assert result.total_settlement_applications == 1
    application = result.insurance_rule_applications[0]
    assert application.rule_kind is VNInsuranceRuleKind.SAMPLE_SEARCH
    assert [decision.insurer_id for decision in application.decisions] == [12, None]
    assert application.result.sampled_insurer_ids == [[11, 12], [11]]
    assert application.result.information_cost == 3.0
    damage_application = result.damage_settlement_applications[0]
    assert damage_application.damage_result.damages == [9.0, 0.0]
    assert damage_application.settlement_result.chosen_insurer_sector_current == [12, None]
    assert result.policyholders[0].paid_premium_current == [4.0, 0.0]
    assert result.policyholders[0].claim_sum_current == [9.0, 0.0]
    assert result.policyholders[0].end_wealth_current == 87.0
    assert result.insurers[1].reserves_current == [35.0, 60.0]
    assert result.insurers[1].policyholders_current_sector == [2.0, 2.0]
