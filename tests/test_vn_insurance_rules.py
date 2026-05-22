import pytest

from ims.model.entities import Insurer, Policyholder
from ims.model.vn_damage_rules import VNDamageRuleDraws, VNDamageRuleParameters
from ims.model.vn_insurance_rules import (
    VNRandomInsuranceRuleDraws,
    VNRandomInsuranceRuleParameters,
    apply_vn_random_insurance_rule,
    load_active_insurer_ids_from_mapping,
    vn_random_insurance_rule_draws_from_mapping,
    vn_random_insurance_rule_parameters_from_mapping,
)
from ims.model.vn_rules import VNDamageSettlementSnapshot, apply_vn_damage_settlement_snapshot


def test_vn_random_insurance_rule_uses_vrvn02_thresholds_and_active_insurers() -> None:
    result = apply_vn_random_insurance_rule(
        VNRandomInsuranceRuleParameters(
            insurance_thresholds_normal=[0.25, 0.75],
            insurance_thresholds_shock=[0.9, 0.9],
        ),
        active_insurer_ids=[13, 11, 12],
        draws=VNRandomInsuranceRuleDraws(
            status_draws=[0.25, 0.74],
            insurer_choice_draws=[0.66, 0.10],
        ),
    )

    assert result.insured == [True, False]
    assert result.chosen_insurer_ids == [12, None]
    assert result.decisions[0].sector_index == 0
    assert result.decisions[0].insured is True
    assert result.decisions[0].insurer_id == 12
    assert result.decisions[1].sector_index == 1
    assert result.decisions[1].insured is False
    assert result.decisions[1].insurer_id is None


def test_vn_random_insurance_rule_uses_shock_thresholds() -> None:
    result = apply_vn_random_insurance_rule(
        VNRandomInsuranceRuleParameters(
            insurance_thresholds_normal=[0.9, 0.9],
            insurance_thresholds_shock=[0.2, 0.8],
        ),
        active_insurer_ids=[7, 9],
        draws=VNRandomInsuranceRuleDraws(
            status_draws=[0.2, 0.79],
            insurer_choice_draws=[0.0, 0.99],
        ),
        change_shock=True,
    )

    assert result.insured == [True, False]
    assert result.chosen_insurer_ids == [7, None]


def test_vn_random_insurance_rule_rejects_missing_active_insurers_when_insured() -> None:
    with pytest.raises(ValueError, match="active insurers"):
        apply_vn_random_insurance_rule(
            VNRandomInsuranceRuleParameters(
                insurance_thresholds_normal=[0.1, 0.9],
                insurance_thresholds_shock=[0.1, 0.9],
            ),
            active_insurer_ids=[],
            draws=VNRandomInsuranceRuleDraws(
                status_draws=[0.5, 0.5],
                insurer_choice_draws=[0.0, 0.0],
            ),
        )


def test_vn_random_insurance_rule_allows_no_active_insurers_when_uninsured() -> None:
    result = apply_vn_random_insurance_rule(
        VNRandomInsuranceRuleParameters(
            insurance_thresholds_normal=[0.9, 0.9],
            insurance_thresholds_shock=[0.9, 0.9],
        ),
        active_insurer_ids=[],
        draws=VNRandomInsuranceRuleDraws(
            status_draws=[0.1, 0.2],
            insurer_choice_draws=[0.0, 0.0],
        ),
    )

    assert result.insured == [False, False]
    assert result.chosen_insurer_ids == [None, None]


def test_vn_random_insurance_rule_loaders_validate_shape() -> None:
    parameters = vn_random_insurance_rule_parameters_from_mapping(
        {
            "insurance_thresholds_normal": [0.2],
            "insurance_thresholds_shock": [0.3, 0.4],
        }
    )
    draws = vn_random_insurance_rule_draws_from_mapping(
        {
            "status_draws": [0.1, 0.2],
            "insurer_choice_draws": [0.3],
        }
    )
    active_ids = load_active_insurer_ids_from_mapping([12, 10, 12])

    assert parameters.insurance_thresholds_normal == [0.2, 0.2]
    assert parameters.insurance_thresholds_shock == [0.3, 0.4]
    assert draws.insurer_choice_draws == [0.3, 0.3]
    assert active_ids == [10, 12]

    with pytest.raises(ValueError, match="status_draws"):
        vn_random_insurance_rule_draws_from_mapping(
            {
                "status_draws": [1.0, 0.2],
                "insurer_choice_draws": [0.3, 0.4],
            }
        )

    with pytest.raises(ValueError, match="active_insurer_ids"):
        load_active_insurer_ids_from_mapping([0])


def test_vn_random_insurance_decisions_feed_damage_settlement_path() -> None:
    random_result = apply_vn_random_insurance_rule(
        VNRandomInsuranceRuleParameters(
            insurance_thresholds_normal=[0.1, 0.9],
            insurance_thresholds_shock=[0.1, 0.9],
        ),
        active_insurer_ids=[11, 12],
        draws=VNRandomInsuranceRuleDraws(
            status_draws=[0.5, 0.1],
            insurer_choice_draws=[0.75, 0.0],
        ),
    )
    insurer = Insurer(
        entity_id=12,
        premiums_current_sector=[4.0, 6.0],
        reserves_current=[40.0, 60.0],
        policyholders_current_sector=[1.0, 2.0],
    )
    snapshot = VNDamageSettlementSnapshot(
        policyholder_id=21,
        previous_wealth=100.0,
        damage_thresholds=[0.8, 0.2],
        parameters=VNDamageRuleParameters(
            damage_intercept_normal=[5.0, 7.0],
            damage_factor_normal=[2.0, 3.0],
            damage_intercept_shock=[50.0, 70.0],
            damage_factor_shock=[20.0, 30.0],
        ),
        draws=VNDamageRuleDraws(
            trigger_draws=[0.1, 0.5],
            amount_draws=[2.0, 3.0],
        ),
        insurance_decisions=random_result.decisions,
    )

    application = apply_vn_damage_settlement_snapshot(
        Policyholder(entity_id=21),
        [insurer],
        snapshot,
    )

    assert random_result.chosen_insurer_ids == [12, None]
    assert application.damage_result.damages == [9.0, 0.0]
    assert application.settlement_result.paid_premium_current == [4.0, 0.0]
    assert application.settlement_result.end_wealth_current == 87.0
