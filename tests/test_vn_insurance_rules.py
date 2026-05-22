import pytest

from ims.model.entities import Insurer, Policyholder
from ims.model.vn_damage_rules import VNDamageRuleDraws, VNDamageRuleParameters
from ims.model.vn_insurance_rules import (
    VNCompulsoryInsuranceRuleDraws,
    VNBestInfoInsuranceRuleParameters,
    VNPreferenceInsuranceRuleDraws,
    VNPreferenceInsuranceRuleParameters,
    VNPreferenceInsurerInput,
    VNInsuranceRuleKind,
    VNRandomInsuranceRuleDraws,
    VNRandomInsuranceRuleParameters,
    VNSampleSearchInsuranceRuleDraws,
    VNSampleSearchInsuranceRuleParameters,
    VNSampleSearchInsurerInput,
    VNSearchInsuranceRuleDraws,
    VNSearchInsuranceRuleParameters,
    apply_vn_best_info_insurance_rule,
    apply_vn_compulsory_insurance_rule,
    apply_vn_insurance_rule_snapshots,
    apply_vn_preference_insurance_rule,
    apply_vn_random_insurance_rule,
    apply_vn_sample_search_insurance_rule,
    apply_vn_search_insurance_rule,
    load_active_insurer_ids_from_mapping,
    load_vn_insurance_rule_snapshots_from_mapping,
    load_vn_preference_insurer_inputs_from_mapping,
    load_vn_sample_search_insurer_inputs_from_mapping,
    load_vn_search_insurance_history_from_mapping,
    vn_compulsory_insurance_rule_draws_from_mapping,
    vn_best_info_insurance_rule_parameters_from_mapping,
    vn_preference_insurance_rule_draws_from_mapping,
    vn_preference_insurance_rule_parameters_from_mapping,
    vn_random_insurance_rule_draws_from_mapping,
    vn_random_insurance_rule_parameters_from_mapping,
    vn_sample_search_insurance_rule_draws_from_mapping,
    vn_sample_search_insurance_rule_parameters_from_mapping,
    vn_search_insurance_rule_draws_from_mapping,
    vn_search_insurance_rule_parameters_from_mapping,
)
from ims.model.vn_rules import VNDamageSettlementSnapshot, apply_vn_damage_settlement_snapshot


def test_vn_compulsory_insurance_rule_uses_initial_decisions_in_first_period() -> None:
    result = apply_vn_compulsory_insurance_rule(
        period=1,
        active_insurer_ids=[],
        initial_decisions=[
            {"sector_index": 1, "insured": False},
            {"sector_index": 0, "insured": True, "insurer_id": 12},
        ],
    )

    assert result.selected_insurer_ids == [12, None]
    assert result.insurer_choice_draws is None
    assert [decision.sector_index for decision in result.decisions] == [0, 1]
    assert result.decisions[0].insured is True
    assert result.decisions[0].insurer_id == 12
    assert result.decisions[1].insured is False
    assert result.decisions[1].insurer_id is None


def test_vn_compulsory_insurance_rule_selects_active_insurers_after_first_period() -> None:
    result = apply_vn_compulsory_insurance_rule(
        period=2,
        active_insurer_ids=[13, 11, 12],
        draws=VNCompulsoryInsuranceRuleDraws(insurer_choice_draws=[0.0, 0.99]),
    )

    assert result.selected_insurer_ids == [11, 13]
    assert result.insurer_choice_draws == [0.0, 0.99]
    assert [decision.insured for decision in result.decisions] == [True, True]
    assert [decision.insurer_id for decision in result.decisions] == [11, 13]


def test_vn_compulsory_insurance_rule_validates_start_and_draw_inputs() -> None:
    with pytest.raises(ValueError, match="period must be at least 1"):
        apply_vn_compulsory_insurance_rule(
            period=0,
            active_insurer_ids=[11],
        )

    with pytest.raises(ValueError, match="initial_decisions"):
        apply_vn_compulsory_insurance_rule(
            period=1,
            active_insurer_ids=[11],
        )

    with pytest.raises(ValueError, match="insurer choice draws"):
        apply_vn_compulsory_insurance_rule(
            period=2,
            active_insurer_ids=[11],
        )

    with pytest.raises(ValueError, match="active insurers"):
        apply_vn_compulsory_insurance_rule(
            period=2,
            active_insurer_ids=[],
            draws=VNCompulsoryInsuranceRuleDraws(insurer_choice_draws=[0.0, 0.1]),
        )


def test_vn_compulsory_insurance_rule_draw_loader_validates_shape() -> None:
    draws = vn_compulsory_insurance_rule_draws_from_mapping(
        {"insurer_choice_draws": [0.25]}
    )

    assert draws.insurer_choice_draws == [0.25, 0.25]

    with pytest.raises(ValueError, match="insurer_choice_draws"):
        vn_compulsory_insurance_rule_draws_from_mapping({"insurer_choice_draws": [1.0, 0.2]})


def test_vn_compulsory_insurance_decisions_feed_damage_settlement_path() -> None:
    compulsory_result = apply_vn_compulsory_insurance_rule(
        period=2,
        active_insurer_ids=[11, 12],
        draws=VNCompulsoryInsuranceRuleDraws(insurer_choice_draws=[0.75, 0.0]),
    )
    insurer_11 = Insurer(
        entity_id=11,
        premiums_current_sector=[3.0, 5.0],
        reserves_current=[30.0, 50.0],
        policyholders_current_sector=[0.0, 1.0],
    )
    insurer_12 = Insurer(
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
            trigger_draws=[0.1, 0.1],
            amount_draws=[2.0, 3.0],
        ),
        insurance_decisions=compulsory_result.decisions,
    )

    application = apply_vn_damage_settlement_snapshot(
        Policyholder(entity_id=21),
        [insurer_11, insurer_12],
        snapshot,
    )

    assert compulsory_result.selected_insurer_ids == [12, 11]
    assert application.damage_result.damages == [9.0, 16.0]
    assert application.settlement_result.paid_premium_current == [4.0, 5.0]
    assert application.settlement_result.end_wealth_current == 66.0


def test_vn_preference_insurance_rule_uses_initial_decisions_in_first_period() -> None:
    result = apply_vn_preference_insurance_rule(
        VNPreferenceInsuranceRuleParameters(
            insurance_thresholds_normal=[0.2, 0.3],
            insurance_thresholds_shock=[0.4, 0.5],
        ),
        period=1,
        damage_probabilities=[0.0, 0.0],
        insurer_inputs=[],
        initial_decisions=[
            {"sector_index": 1, "insured": True, "insurer_id": 13},
            {"sector_index": 0, "insured": False},
        ],
    )

    assert result.insured == [False, True]
    assert result.chosen_insurer_ids == [None, 13]
    assert result.selected_insurer_ids == [None, 13]
    assert result.preference_scores == [{}, {}]
    assert result.used_fallback == [False, False]


def test_vn_preference_insurance_rule_uses_thresholds_and_max_advertising() -> None:
    result = apply_vn_preference_insurance_rule(
        VNPreferenceInsuranceRuleParameters(
            insurance_thresholds_normal=[0.25, 0.75],
            insurance_thresholds_shock=[0.9, 0.9],
        ),
        period=2,
        damage_probabilities=[0.25, 0.8],
        insurer_inputs=[
            {"insurer_id": 12, "advertising_current_sector": [10.0, 5.0]},
            {"insurer_id": 11, "advertising_current_sector": [10.0, 30.0]},
            {"insurer_id": 13, "advertising_current_sector": [5.0, 30.0]},
        ],
    )

    assert result.insured == [False, True]
    assert result.chosen_insurer_ids == [None, 11]
    assert result.selected_insurer_ids == [11, 11]
    assert result.preference_scores[0] == {11: 0.4, 12: 0.4, 13: 0.2}
    assert result.preference_scores[1] == {11: 30.0 / 65.0, 12: 5.0 / 65.0, 13: 30.0 / 65.0}
    assert result.used_fallback == [False, False]


def test_vn_preference_insurance_rule_uses_shock_thresholds() -> None:
    result = apply_vn_preference_insurance_rule(
        VNPreferenceInsuranceRuleParameters(
            insurance_thresholds_normal=[0.9, 0.9],
            insurance_thresholds_shock=[0.2, 0.8],
        ),
        period=2,
        damage_probabilities=[0.2, 0.81],
        insurer_inputs=[{"insurer_id": 7, "advertising_current_sector": [1.0, 1.0]}],
        change_shock=True,
    )

    assert result.insured == [False, True]
    assert result.chosen_insurer_ids == [None, 7]
    assert result.selected_insurer_ids == [7, 7]


def test_vn_preference_insurance_rule_uses_fallback_draws_without_active_advertising() -> None:
    result = apply_vn_preference_insurance_rule(
        VNPreferenceInsuranceRuleParameters(
            insurance_thresholds_normal=[0.1, 0.1],
            insurance_thresholds_shock=[0.1, 0.1],
        ),
        period=2,
        damage_probabilities=[0.5, 0.5],
        insurer_inputs=[
            {"insurer_id": 10, "advertising_current_sector": [0.0, 0.0]},
            {"insurer_id": 20, "advertising_current_sector": [0.0, 0.0]},
            {"insurer_id": 30, "advertising_current_sector": [0.0, 0.0]},
        ],
        draws=VNPreferenceInsuranceRuleDraws(fallback_insurer_choice_draws=[0.0, 0.99]),
    )

    assert result.insured == [True, True]
    assert result.chosen_insurer_ids == [10, 30]
    assert result.selected_insurer_ids == [10, 30]
    assert result.preference_scores == [{10: 0.0, 20: 0.0, 30: 0.0}, {10: 0.0, 20: 0.0, 30: 0.0}]
    assert result.used_fallback == [True, True]
    assert result.fallback_insurer_choice_draws == [0.0, 0.99]


def test_vn_preference_insurance_rule_validates_inputs() -> None:
    parameters = VNPreferenceInsuranceRuleParameters(
        insurance_thresholds_normal=[0.1, 0.1],
        insurance_thresholds_shock=[0.1, 0.1],
    )

    with pytest.raises(ValueError, match="period must be at least 1"):
        apply_vn_preference_insurance_rule(
            parameters,
            period=0,
            damage_probabilities=[0.1, 0.2],
            insurer_inputs=[],
        )

    with pytest.raises(ValueError, match="initial_decisions"):
        apply_vn_preference_insurance_rule(
            parameters,
            period=1,
            damage_probabilities=[0.1, 0.2],
            insurer_inputs=[],
        )

    with pytest.raises(ValueError, match="non-negative"):
        apply_vn_preference_insurance_rule(
            parameters,
            period=2,
            damage_probabilities=[-0.1, 0.2],
            insurer_inputs=[{"insurer_id": 10, "advertising_current_sector": [1.0, 0.0]}],
        )

    with pytest.raises(ValueError, match="active insurer inputs"):
        apply_vn_preference_insurance_rule(
            parameters,
            period=2,
            damage_probabilities=[0.5, 0.5],
            insurer_inputs=[],
        )

    with pytest.raises(ValueError, match="fallback draws"):
        apply_vn_preference_insurance_rule(
            parameters,
            period=2,
            damage_probabilities=[0.5, 0.5],
            insurer_inputs=[{"insurer_id": 10, "advertising_current_sector": [0.0, 0.0]}],
        )


def test_vn_preference_insurance_rule_loaders_validate_shape() -> None:
    parameters = vn_preference_insurance_rule_parameters_from_mapping(
        {
            "insurance_thresholds_normal": [0.2],
            "insurance_thresholds_shock": [0.3, 0.4],
        }
    )
    draws = vn_preference_insurance_rule_draws_from_mapping(
        {"fallback_insurer_choice_draws": [0.25]}
    )
    inputs = load_vn_preference_insurer_inputs_from_mapping(
        [
            {"insurer_id": 12, "advertising_current_sector": [2.0]},
            {"insurer_id": 11, "advertising_current_sector": [1.0, 3.0]},
        ]
    )

    assert parameters.insurance_thresholds_normal == [0.2, 0.2]
    assert parameters.insurance_thresholds_shock == [0.3, 0.4]
    assert draws.fallback_insurer_choice_draws == [0.25, 0.25]
    assert [item.insurer_id for item in inputs] == [11, 12]
    assert inputs[1].advertising_current_sector == [2.0, 2.0]

    typed_inputs = load_vn_preference_insurer_inputs_from_mapping(
        [
            VNPreferenceInsurerInput(insurer_id=14, advertising_current_sector=[5.0]),
            VNPreferenceInsurerInput(insurer_id=13, advertising_current_sector=[]),
        ]
    )

    assert [item.insurer_id for item in typed_inputs] == [13, 14]
    assert typed_inputs[0].advertising_current_sector == [0.0, 0.0]
    assert typed_inputs[1].advertising_current_sector == [5.0, 5.0]

    with pytest.raises(ValueError, match="duplicate insurer_ids"):
        load_vn_preference_insurer_inputs_from_mapping(
            [
                {"insurer_id": 11, "advertising_current_sector": [1.0, 2.0]},
                {"insurer_id": 11, "advertising_current_sector": [3.0, 4.0]},
            ]
        )

    with pytest.raises(ValueError, match="non-negative"):
        load_vn_preference_insurer_inputs_from_mapping(
            [{"insurer_id": 11, "advertising_current_sector": [-1.0, 0.0]}]
        )

    with pytest.raises(ValueError, match="non-negative"):
        load_vn_preference_insurer_inputs_from_mapping(
            [VNPreferenceInsurerInput(insurer_id=11, advertising_current_sector=[-1.0])]
        )

    with pytest.raises(ValueError, match="fallback_insurer_choice_draws"):
        vn_preference_insurance_rule_draws_from_mapping({"fallback_insurer_choice_draws": [1.0, 0.0]})


def test_vn_preference_insurance_decisions_feed_damage_settlement_path() -> None:
    preference_result = apply_vn_preference_insurance_rule(
        VNPreferenceInsuranceRuleParameters(
            insurance_thresholds_normal=[0.1, 0.2],
            insurance_thresholds_shock=[0.1, 0.2],
        ),
        period=2,
        damage_probabilities=[0.5, 0.8],
        insurer_inputs=[
            {"insurer_id": 11, "advertising_current_sector": [1.0, 9.0]},
            {"insurer_id": 12, "advertising_current_sector": [9.0, 1.0]},
        ],
    )
    insurer_11 = Insurer(
        entity_id=11,
        premiums_current_sector=[3.0, 5.0],
        reserves_current=[30.0, 50.0],
        policyholders_current_sector=[0.0, 1.0],
    )
    insurer_12 = Insurer(
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
            trigger_draws=[0.1, 0.1],
            amount_draws=[2.0, 3.0],
        ),
        insurance_decisions=preference_result.decisions,
    )

    application = apply_vn_damage_settlement_snapshot(
        Policyholder(entity_id=21),
        [insurer_11, insurer_12],
        snapshot,
    )

    assert preference_result.selected_insurer_ids == [12, 11]
    assert application.damage_result.damages == [9.0, 16.0]
    assert application.settlement_result.paid_premium_current == [4.0, 5.0]
    assert application.settlement_result.end_wealth_current == 66.0


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
    assert result.selected_insurer_ids == [12, 11]
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
    assert result.selected_insurer_ids == [7, 9]


def test_vn_random_insurance_rule_rejects_missing_active_insurers_before_status_branch() -> None:
    with pytest.raises(ValueError, match="active insurers"):
        apply_vn_random_insurance_rule(
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


def test_vn_random_insurance_rule_keeps_uninsured_decisions_without_insurer_reference() -> None:
    result = apply_vn_random_insurance_rule(
        VNRandomInsuranceRuleParameters(
            insurance_thresholds_normal=[0.9, 0.9],
            insurance_thresholds_shock=[0.9, 0.9],
        ),
        active_insurer_ids=[11, 12],
        draws=VNRandomInsuranceRuleDraws(
            status_draws=[0.1, 0.2],
            insurer_choice_draws=[0.0, 0.99],
        ),
    )

    assert result.insured == [False, False]
    assert result.chosen_insurer_ids == [None, None]
    assert result.selected_insurer_ids == [11, 12]
    assert result.decisions[0].insurer_id is None
    assert result.decisions[1].insurer_id is None


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
    assert random_result.selected_insurer_ids == [12, 11]
    assert application.damage_result.damages == [9.0, 0.0]
    assert application.settlement_result.paid_premium_current == [4.0, 0.0]
    assert application.settlement_result.end_wealth_current == 87.0


def test_vn_search_insurance_rule_uses_initial_decisions_in_first_period() -> None:
    result = apply_vn_search_insurance_rule(
        VNSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.2, 0.3],
            insurance_thresholds_shock=[0.4, 0.5],
        ),
        period=1,
        damage_probabilities=[0.0, 0.0],
        history=[],
        active_insurer_ids=[],
        initial_decisions=[
            {"sector_index": 1, "insured": True, "insurer_id": 13},
            {"sector_index": 0, "insured": False},
        ],
    )

    assert result.insured == [False, True]
    assert result.chosen_insurer_ids == [None, 13]
    assert result.selected_insurer_ids == [None, 13]
    assert result.selected_history_periods == [None, None]
    assert result.used_fallback == [False, False]


def test_vn_search_insurance_rule_uses_cheapest_prior_insured_history() -> None:
    result = apply_vn_search_insurance_rule(
        VNSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.25, 0.75],
            insurance_thresholds_shock=[0.9, 0.9],
        ),
        period=4,
        damage_probabilities=[0.25, 0.8],
        history=[
            {"period": 1, "sector_index": 0, "insured": True, "insurer_id": 12, "premium": 8.0},
            {"period": 2, "sector_index": 0, "insured": True, "insurer_id": 11, "premium": 3.0},
            {"period": 3, "sector_index": 0, "insured": True, "insurer_id": 13, "premium": 3.0},
            {"period": 2, "sector_index": 1, "insured": False, "premium": 0.0},
            {"period": 3, "sector_index": 1, "insured": True, "insurer_id": 14, "premium": 6.0},
            {"period": 4, "sector_index": 1, "insured": True, "insurer_id": 15, "premium": 1.0},
        ],
        active_insurer_ids=[],
    )

    assert result.insured == [False, True]
    assert result.chosen_insurer_ids == [None, 14]
    assert result.selected_insurer_ids == [11, 14]
    assert result.selected_history_periods == [2, 3]
    assert result.used_fallback == [False, False]


def test_vn_search_insurance_rule_uses_fallback_without_prior_insured_history() -> None:
    result = apply_vn_search_insurance_rule(
        VNSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.1, 0.1],
            insurance_thresholds_shock=[0.1, 0.1],
        ),
        period=3,
        damage_probabilities=[0.5, 0.5],
        history=[
            {"period": 1, "sector_index": 0, "insured": False, "premium": 0.0},
            {"period": 1, "sector_index": 1, "insured": True, "insurer_id": 20, "premium": 7.0},
        ],
        active_insurer_ids=[10, 20, 30],
        draws=VNSearchInsuranceRuleDraws(fallback_insurer_choice_draws=[0.99, 0.0]),
    )

    assert result.insured == [True, True]
    assert result.chosen_insurer_ids == [30, 20]
    assert result.selected_insurer_ids == [30, 20]
    assert result.selected_history_periods == [None, 1]
    assert result.used_fallback == [True, False]
    assert result.fallback_insurer_choice_draws == [0.99, 0.0]


def test_vn_search_insurance_rule_uses_shock_thresholds() -> None:
    result = apply_vn_search_insurance_rule(
        VNSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.9, 0.9],
            insurance_thresholds_shock=[0.2, 0.8],
        ),
        period=2,
        damage_probabilities=[0.2, 0.81],
        history=[
            {"period": 1, "sector_index": 0, "insured": True, "insurer_id": 7, "premium": 1.0},
            {"period": 1, "sector_index": 1, "insured": True, "insurer_id": 9, "premium": 1.0},
        ],
        active_insurer_ids=[],
        change_shock=True,
    )

    assert result.insured == [False, True]
    assert result.chosen_insurer_ids == [None, 9]
    assert result.selected_insurer_ids == [7, 9]


def test_vn_search_insurance_rule_validates_inputs() -> None:
    parameters = VNSearchInsuranceRuleParameters(
        insurance_thresholds_normal=[0.1, 0.1],
        insurance_thresholds_shock=[0.1, 0.1],
    )

    with pytest.raises(ValueError, match="period must be at least 1"):
        apply_vn_search_insurance_rule(
            parameters,
            period=0,
            damage_probabilities=[0.1, 0.2],
            history=[],
            active_insurer_ids=[],
        )

    with pytest.raises(ValueError, match="initial_decisions"):
        apply_vn_search_insurance_rule(
            parameters,
            period=1,
            damage_probabilities=[0.1, 0.2],
            history=[],
            active_insurer_ids=[],
        )

    with pytest.raises(ValueError, match="non-negative"):
        apply_vn_search_insurance_rule(
            parameters,
            period=2,
            damage_probabilities=[-0.1, 0.2],
            history=[],
            active_insurer_ids=[],
        )

    with pytest.raises(ValueError, match="fallback draws"):
        apply_vn_search_insurance_rule(
            parameters,
            period=2,
            damage_probabilities=[0.5, 0.5],
            history=[],
            active_insurer_ids=[11],
        )

    with pytest.raises(ValueError, match="active insurers"):
        apply_vn_search_insurance_rule(
            parameters,
            period=2,
            damage_probabilities=[0.5, 0.5],
            history=[],
            active_insurer_ids=[],
            draws=VNSearchInsuranceRuleDraws(fallback_insurer_choice_draws=[0.0, 0.0]),
        )


def test_vn_search_insurance_rule_loaders_validate_shape() -> None:
    parameters = vn_search_insurance_rule_parameters_from_mapping(
        {
            "insurance_thresholds_normal": [0.2],
            "insurance_thresholds_shock": [0.3, 0.4],
        }
    )
    draws = vn_search_insurance_rule_draws_from_mapping(
        {"fallback_insurer_choice_draws": [0.25]}
    )
    history = load_vn_search_insurance_history_from_mapping(
        [
            {"period": 2, "sector_index": 1, "insured": True, "insurer_id": 12, "premium": 3.0},
            {"period": 1, "sector_index": 0, "insured": False, "premium": 0.0},
        ]
    )

    assert parameters.insurance_thresholds_normal == [0.2, 0.2]
    assert parameters.insurance_thresholds_shock == [0.3, 0.4]
    assert draws.fallback_insurer_choice_draws == [0.25, 0.25]
    assert [(item.period, item.sector_index) for item in history] == [(1, 0), (2, 1)]

    with pytest.raises(ValueError, match="duplicate period/sector"):
        load_vn_search_insurance_history_from_mapping(
            [
                {"period": 1, "sector_index": 0, "insured": False, "premium": 0.0},
                {"period": 1, "sector_index": 0, "insured": True, "insurer_id": 11, "premium": 1.0},
            ]
        )

    with pytest.raises(ValueError, match="requires insurer_id"):
        load_vn_search_insurance_history_from_mapping(
            [{"period": 1, "sector_index": 0, "insured": True, "premium": 1.0}]
        )

    with pytest.raises(ValueError, match="boolean"):
        load_vn_search_insurance_history_from_mapping(
            [{"period": 1, "sector_index": 0, "insured": "false", "premium": 0.0}]
        )

    with pytest.raises(ValueError, match="fallback_insurer_choice_draws"):
        vn_search_insurance_rule_draws_from_mapping({"fallback_insurer_choice_draws": [1.0, 0.0]})


def test_vn_search_insurance_decisions_feed_damage_settlement_path() -> None:
    search_result = apply_vn_search_insurance_rule(
        VNSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.1, 0.9],
            insurance_thresholds_shock=[0.1, 0.9],
        ),
        period=3,
        damage_probabilities=[0.5, 0.1],
        history=[
            {"period": 1, "sector_index": 0, "insured": True, "insurer_id": 12, "premium": 4.0},
            {"period": 2, "sector_index": 1, "insured": True, "insurer_id": 11, "premium": 5.0},
        ],
        active_insurer_ids=[],
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
        insurance_decisions=search_result.decisions,
    )

    application = apply_vn_damage_settlement_snapshot(
        Policyholder(entity_id=21),
        [insurer],
        snapshot,
    )

    assert search_result.chosen_insurer_ids == [12, None]
    assert search_result.selected_insurer_ids == [12, 11]
    assert application.damage_result.damages == [9.0, 0.0]
    assert application.settlement_result.paid_premium_current == [4.0, 0.0]
    assert application.settlement_result.end_wealth_current == 87.0


def test_vn_sample_search_insurance_rule_uses_initial_decisions_in_first_period() -> None:
    result = apply_vn_sample_search_insurance_rule(
        VNSampleSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.2, 0.3],
            insurance_thresholds_shock=[0.4, 0.5],
            sample_sizes_normal=[1, 2],
            sample_sizes_shock=[3, 4],
        ),
        period=1,
        market_damage_indicator=0.0,
        insurer_inputs=[],
        initial_decisions=[
            {"sector_index": 1, "insured": True, "insurer_id": 13, "premium": 5.0},
            {"sector_index": 0, "insured": False},
        ],
    )

    assert result.insured == [False, True]
    assert result.chosen_insurer_ids == [None, 13]
    assert result.selected_insurer_ids == [None, 13]
    assert result.selected_premiums == [None, 5.0]
    assert result.sampled_insurer_ids == [[], []]
    assert result.information_cost == 0.0


def test_vn_sample_search_insurance_rule_samples_active_current_premiums() -> None:
    result = apply_vn_sample_search_insurance_rule(
        VNSampleSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.5, 0.5],
            insurance_thresholds_shock=[0.1, 0.1],
            sample_sizes_normal=[3, 2],
            sample_sizes_shock=[1, 1],
        ),
        period=2,
        market_damage_indicator=0.5,
        insurer_inputs=[
            {"insurer_id": 30, "premiums_current_sector": [9.0, 4.0]},
            {"insurer_id": 10, "premiums_current_sector": [5.0, 7.0]},
            {"insurer_id": 20, "premiums_current_sector": [3.0, 8.0]},
        ],
        draws=VNSampleSearchInsuranceRuleDraws(
            insurer_choice_draws_by_sector=[
                [0.99, 0.34, 0.01],
                [0.0, 0.99],
            ]
        ),
        information_cost_per_sample=2.5,
    )

    assert result.insured == [True, True]
    assert result.sampled_insurer_ids == [[30, 20, 10], [10, 30]]
    assert result.selected_insurer_ids == [20, 30]
    assert result.chosen_insurer_ids == [20, 30]
    assert result.selected_premiums == [3.0, 4.0]
    assert result.used_insurer_choice_draws_by_sector == [[0.99, 0.34, 0.01], [0.0, 0.99]]
    assert result.information_cost == 12.5
    assert result.decisions[0].premium == 3.0
    assert result.decisions[1].premium == 4.0


def test_vn_sample_search_insurance_rule_accepts_high_premium_scale() -> None:
    result = apply_vn_sample_search_insurance_rule(
        VNSampleSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.9, 0.9],
            insurance_thresholds_shock=[0.9, 0.9],
            sample_sizes_normal=[2, 1],
            sample_sizes_shock=[1, 1],
        ),
        period=2,
        market_damage_indicator=0.1,
        insurer_inputs=[
            {"insurer_id": 10, "premiums_current_sector": [1500.0, 2500.0]},
            {"insurer_id": 20, "premiums_current_sector": [1200.0, 2200.0]},
        ],
        draws=VNSampleSearchInsuranceRuleDraws(
            insurer_choice_draws_by_sector=[
                [0.0, 0.99],
                [0.99],
            ]
        ),
    )

    assert result.selected_insurer_ids == [20, 20]
    assert result.selected_premiums == [1200.0, 2200.0]


def test_vn_sample_search_insurance_rule_keeps_selection_diagnostics_when_uninsured() -> None:
    result = apply_vn_sample_search_insurance_rule(
        VNSampleSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.2, 0.8],
            insurance_thresholds_shock=[0.8, 0.8],
            sample_sizes_normal=[1, 1],
            sample_sizes_shock=[1, 1],
        ),
        period=2,
        market_damage_indicator=0.5,
        insurer_inputs=[
            {"insurer_id": 10, "premiums_current_sector": [5.0, 7.0]},
            {"insurer_id": 20, "premiums_current_sector": [3.0, 6.0]},
        ],
        draws=VNSampleSearchInsuranceRuleDraws(
            insurer_choice_draws_by_sector=[
                [0.99],
                [0.99],
            ]
        ),
    )

    assert result.insured == [False, True]
    assert result.selected_insurer_ids == [20, 20]
    assert result.chosen_insurer_ids == [None, 20]
    assert result.decisions[0].insurer_id is None
    assert result.decisions[0].premium is None
    assert result.decisions[1].premium == 6.0


def test_vn_sample_search_insurance_rule_uses_shock_thresholds_and_sample_sizes() -> None:
    result = apply_vn_sample_search_insurance_rule(
        VNSampleSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.1, 0.1],
            insurance_thresholds_shock=[0.6, 0.4],
            sample_sizes_normal=[1, 1],
            sample_sizes_shock=[2, 1],
        ),
        period=2,
        market_damage_indicator=0.5,
        insurer_inputs=[
            {"insurer_id": 10, "premiums_current_sector": [5.0, 7.0]},
            {"insurer_id": 20, "premiums_current_sector": [3.0, 6.0]},
        ],
        draws=VNSampleSearchInsuranceRuleDraws(
            insurer_choice_draws_by_sector=[
                [0.0, 0.99],
                [0.0, 0.99],
            ]
        ),
        change_shock=True,
    )

    assert result.insured == [True, False]
    assert result.sampled_insurer_ids == [[10, 20], [10]]
    assert result.selected_insurer_ids == [20, 10]
    assert result.chosen_insurer_ids == [20, None]
    assert result.used_insurer_choice_draws_by_sector == [[0.0, 0.99], [0.0]]


def test_vn_sample_search_insurance_rule_validates_inputs() -> None:
    parameters = VNSampleSearchInsuranceRuleParameters(
        insurance_thresholds_normal=[0.1, 0.1],
        insurance_thresholds_shock=[0.1, 0.1],
        sample_sizes_normal=[1, 1],
        sample_sizes_shock=[1, 1],
    )

    with pytest.raises(ValueError, match="period must be at least 1"):
        apply_vn_sample_search_insurance_rule(
            parameters,
            period=0,
            market_damage_indicator=0.1,
            insurer_inputs=[],
        )

    with pytest.raises(ValueError, match="initial_decisions"):
        apply_vn_sample_search_insurance_rule(
            parameters,
            period=1,
            market_damage_indicator=0.1,
            insurer_inputs=[],
        )

    with pytest.raises(ValueError, match="insurer choice draws"):
        apply_vn_sample_search_insurance_rule(
            parameters,
            period=2,
            market_damage_indicator=0.1,
            insurer_inputs=[],
        )

    with pytest.raises(ValueError, match="active insurer inputs"):
        apply_vn_sample_search_insurance_rule(
            parameters,
            period=2,
            market_damage_indicator=0.1,
            insurer_inputs=[],
            draws=VNSampleSearchInsuranceRuleDraws(insurer_choice_draws_by_sector=[[0.0], [0.0]]),
        )

    with pytest.raises(ValueError, match="sample sizes must be positive"):
        apply_vn_sample_search_insurance_rule(
            VNSampleSearchInsuranceRuleParameters(
                insurance_thresholds_normal=[0.1, 0.1],
                insurance_thresholds_shock=[0.1, 0.1],
                sample_sizes_normal=[0, 1],
                sample_sizes_shock=[1, 1],
            ),
            period=2,
            market_damage_indicator=0.1,
            insurer_inputs=[{"insurer_id": 10, "premiums_current_sector": [1.0, 1.0]}],
            draws=VNSampleSearchInsuranceRuleDraws(insurer_choice_draws_by_sector=[[], [0.0]]),
        )

    with pytest.raises(ValueError, match="enough insurer choice draws"):
        apply_vn_sample_search_insurance_rule(
            VNSampleSearchInsuranceRuleParameters(
                insurance_thresholds_normal=[0.1, 0.1],
                insurance_thresholds_shock=[0.1, 0.1],
                sample_sizes_normal=[2, 1],
                sample_sizes_shock=[1, 1],
            ),
            period=2,
            market_damage_indicator=0.1,
            insurer_inputs=[{"insurer_id": 10, "premiums_current_sector": [1.0, 1.0]}],
            draws=VNSampleSearchInsuranceRuleDraws(insurer_choice_draws_by_sector=[[0.0], [0.0]]),
        )


def test_vn_sample_search_insurance_rule_loaders_validate_shape() -> None:
    parameters = vn_sample_search_insurance_rule_parameters_from_mapping(
        {
            "insurance_thresholds_normal": [0.2],
            "insurance_thresholds_shock": [0.3, 0.4],
            "sample_sizes_normal": [2],
            "sample_sizes_shock": [3, 4],
        }
    )
    draws = vn_sample_search_insurance_rule_draws_from_mapping(
        {"insurer_choice_draws_by_sector": [[0.0, 0.5], [0.99]]}
    )
    inputs = load_vn_sample_search_insurer_inputs_from_mapping(
        [
            {"insurer_id": 12, "premiums_current_sector": [2.0]},
            VNSampleSearchInsurerInput(insurer_id=11, premiums_current_sector=[]),
        ]
    )

    assert parameters.insurance_thresholds_normal == [0.2, 0.2]
    assert parameters.insurance_thresholds_shock == [0.3, 0.4]
    assert parameters.sample_sizes_normal == [2, 2]
    assert parameters.sample_sizes_shock == [3, 4]
    assert draws.insurer_choice_draws_by_sector == [[0.0, 0.5], [0.99]]
    assert [item.insurer_id for item in inputs] == [11, 12]
    assert inputs[0].premiums_current_sector == [0.0, 0.0]
    assert inputs[1].premiums_current_sector == [2.0, 2.0]

    with pytest.raises(ValueError, match="non-negative"):
        vn_sample_search_insurance_rule_parameters_from_mapping(
            {
                "insurance_thresholds_normal": [0.2, 0.2],
                "insurance_thresholds_shock": [0.2, 0.2],
                "sample_sizes_normal": [-1, 1],
                "sample_sizes_shock": [1, 1],
            }
        )

    with pytest.raises(ValueError, match="two draw lists"):
        vn_sample_search_insurance_rule_draws_from_mapping(
            {"insurer_choice_draws_by_sector": [[0.0]]}
        )

    with pytest.raises(ValueError, match="duplicate insurer_ids"):
        load_vn_sample_search_insurer_inputs_from_mapping(
            [
                {"insurer_id": 12, "premiums_current_sector": [1.0, 1.0]},
                {"insurer_id": 12, "premiums_current_sector": [2.0, 2.0]},
            ]
        )

    with pytest.raises(ValueError, match="premiums"):
        load_vn_sample_search_insurer_inputs_from_mapping(
            [{"insurer_id": 12, "premiums_current_sector": [-1.0, 1.0]}]
        )


def test_vn_sample_search_insurance_decisions_feed_damage_settlement_path() -> None:
    sample_search_result = apply_vn_sample_search_insurance_rule(
        VNSampleSearchInsuranceRuleParameters(
            insurance_thresholds_normal=[0.5, 0.1],
            insurance_thresholds_shock=[0.5, 0.1],
            sample_sizes_normal=[2, 1],
            sample_sizes_shock=[2, 1],
        ),
        period=2,
        market_damage_indicator=0.5,
        insurer_inputs=[
            {"insurer_id": 11, "premiums_current_sector": [6.0, 5.0]},
            {"insurer_id": 12, "premiums_current_sector": [4.0, 7.0]},
        ],
        draws=VNSampleSearchInsuranceRuleDraws(
            insurer_choice_draws_by_sector=[
                [0.0, 0.99],
                [0.0],
            ]
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
        insurance_decisions=sample_search_result.decisions,
    )

    application = apply_vn_damage_settlement_snapshot(
        Policyholder(entity_id=21),
        [insurer],
        snapshot,
    )

    assert sample_search_result.chosen_insurer_ids == [12, None]
    assert sample_search_result.selected_insurer_ids == [12, 11]
    assert application.damage_result.damages == [9.0, 0.0]
    assert application.settlement_result.paid_premium_current == [4.0, 0.0]
    assert application.settlement_result.end_wealth_current == 87.0


def test_vn_best_info_insurance_rule_uses_initial_decisions_in_first_period() -> None:
    result = apply_vn_best_info_insurance_rule(
        VNBestInfoInsuranceRuleParameters(
            insurance_thresholds_normal=[0.2, 0.3],
            insurance_thresholds_shock=[0.4, 0.5],
        ),
        period=1,
        market_damage_indicator=0.0,
        insurer_inputs=[],
        initial_decisions=[
            {"sector_index": 1, "insured": True, "insurer_id": 13, "premium": 5.0},
            {"sector_index": 0, "insured": False},
        ],
    )

    assert result.insured == [False, True]
    assert result.chosen_insurer_ids == [None, 13]
    assert result.selected_insurer_ids == [None, 13]
    assert result.selected_premiums == [None, 5.0]
    assert result.considered_insurer_ids == [[], []]
    assert result.information_cost == 0.0


def test_vn_best_info_insurance_rule_selects_best_active_current_premiums() -> None:
    result = apply_vn_best_info_insurance_rule(
        VNBestInfoInsuranceRuleParameters(
            insurance_thresholds_normal=[0.5, 0.5],
            insurance_thresholds_shock=[0.1, 0.1],
        ),
        period=2,
        market_damage_indicator=0.5,
        insurer_inputs=[
            {"insurer_id": 30, "premiums_current_sector": [9.0, 4.0]},
            {"insurer_id": 10, "premiums_current_sector": [5.0, 7.0]},
            {"insurer_id": 20, "premiums_current_sector": [3.0, 8.0]},
        ],
        information_cost_per_insurer=1.5,
    )

    assert result.insured == [True, True]
    assert result.selected_insurer_ids == [20, 30]
    assert result.chosen_insurer_ids == [20, 30]
    assert result.selected_premiums == [3.0, 4.0]
    assert result.considered_insurer_ids == [[10, 20, 30], [10, 20, 30]]
    assert result.information_cost == 9.0
    assert result.decisions[0].premium == 3.0
    assert result.decisions[1].premium == 4.0


def test_vn_best_info_insurance_rule_keeps_selection_diagnostics_when_uninsured() -> None:
    result = apply_vn_best_info_insurance_rule(
        VNBestInfoInsuranceRuleParameters(
            insurance_thresholds_normal=[0.2, 0.8],
            insurance_thresholds_shock=[0.8, 0.8],
        ),
        period=2,
        market_damage_indicator=0.5,
        insurer_inputs=[
            {"insurer_id": 10, "premiums_current_sector": [5.0, 7.0]},
            {"insurer_id": 20, "premiums_current_sector": [3.0, 6.0]},
        ],
    )

    assert result.insured == [False, True]
    assert result.selected_insurer_ids == [20, 20]
    assert result.chosen_insurer_ids == [None, 20]
    assert result.decisions[0].insurer_id is None
    assert result.decisions[0].premium is None
    assert result.decisions[1].premium == 6.0


def test_vn_best_info_insurance_rule_uses_shock_thresholds() -> None:
    result = apply_vn_best_info_insurance_rule(
        VNBestInfoInsuranceRuleParameters(
            insurance_thresholds_normal=[0.1, 0.1],
            insurance_thresholds_shock=[0.6, 0.4],
        ),
        period=2,
        market_damage_indicator=0.5,
        insurer_inputs=[
            {"insurer_id": 10, "premiums_current_sector": [5.0, 7.0]},
            {"insurer_id": 20, "premiums_current_sector": [3.0, 6.0]},
        ],
        change_shock=True,
    )

    assert result.insured == [True, False]
    assert result.selected_insurer_ids == [20, 20]
    assert result.chosen_insurer_ids == [20, None]


def test_vn_best_info_insurance_rule_validates_inputs() -> None:
    parameters = VNBestInfoInsuranceRuleParameters(
        insurance_thresholds_normal=[0.1, 0.1],
        insurance_thresholds_shock=[0.1, 0.1],
    )

    with pytest.raises(ValueError, match="period must be at least 1"):
        apply_vn_best_info_insurance_rule(
            parameters,
            period=0,
            market_damage_indicator=0.1,
            insurer_inputs=[],
        )

    with pytest.raises(ValueError, match="initial_decisions"):
        apply_vn_best_info_insurance_rule(
            parameters,
            period=1,
            market_damage_indicator=0.1,
            insurer_inputs=[],
        )

    with pytest.raises(ValueError, match="active insurer inputs"):
        apply_vn_best_info_insurance_rule(
            parameters,
            period=2,
            market_damage_indicator=0.1,
            insurer_inputs=[],
        )

    with pytest.raises(ValueError, match="information cost"):
        apply_vn_best_info_insurance_rule(
            parameters,
            period=2,
            market_damage_indicator=0.1,
            insurer_inputs=[{"insurer_id": 10, "premiums_current_sector": [1.0, 1.0]}],
            information_cost_per_insurer=-1.0,
        )


def test_vn_best_info_insurance_rule_loader_validates_shape() -> None:
    parameters = vn_best_info_insurance_rule_parameters_from_mapping(
        {
            "insurance_thresholds_normal": [0.2],
            "insurance_thresholds_shock": [0.3, 0.4],
        }
    )

    assert parameters.insurance_thresholds_normal == [0.2, 0.2]
    assert parameters.insurance_thresholds_shock == [0.3, 0.4]

    with pytest.raises(ValueError, match="parameters must be an object"):
        vn_best_info_insurance_rule_parameters_from_mapping([])


def test_vn_best_info_insurance_decisions_feed_damage_settlement_path() -> None:
    best_info_result = apply_vn_best_info_insurance_rule(
        VNBestInfoInsuranceRuleParameters(
            insurance_thresholds_normal=[0.5, 0.1],
            insurance_thresholds_shock=[0.5, 0.1],
        ),
        period=2,
        market_damage_indicator=0.5,
        insurer_inputs=[
            {"insurer_id": 11, "premiums_current_sector": [6.0, 5.0]},
            {"insurer_id": 12, "premiums_current_sector": [4.0, 7.0]},
        ],
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
        insurance_decisions=best_info_result.decisions,
    )

    application = apply_vn_damage_settlement_snapshot(
        Policyholder(entity_id=21),
        [insurer],
        snapshot,
    )

    assert best_info_result.chosen_insurer_ids == [12, None]
    assert best_info_result.selected_insurer_ids == [12, 11]
    assert application.damage_result.damages == [9.0, 0.0]
    assert application.settlement_result.paid_premium_current == [4.0, 0.0]
    assert application.settlement_result.end_wealth_current == 87.0


def test_vn_insurance_rule_dispatch_applies_mixed_rule_snapshots() -> None:
    snapshots = load_vn_insurance_rule_snapshots_from_mapping(
        [
            {
                "policyholder_id": 21,
                "rule_kind": "random",
                "parameters": {
                    "insurance_thresholds_normal": [0.2, 0.8],
                    "insurance_thresholds_shock": [0.2, 0.8],
                },
                "active_insurer_ids": [11, 12],
                "draws": {
                    "status_draws": [0.2, 0.1],
                    "insurer_choice_draws": [0.99, 0.0],
                },
            },
            {
                "policyholder_id": 22,
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
            },
        ]
    )

    applications = apply_vn_insurance_rule_snapshots(snapshots, period=2)

    assert [application.policyholder_id for application in applications] == [21, 22]
    assert applications[0].rule_kind is VNInsuranceRuleKind.RANDOM
    assert [decision.insurer_id for decision in applications[0].decisions] == [12, None]
    assert applications[1].rule_kind is VNInsuranceRuleKind.BEST_INFO
    assert [decision.insurer_id for decision in applications[1].decisions] == [12, None]
    assert applications[1].result.information_cost == 4.0


def test_vn_insurance_rule_dispatch_uses_initial_decisions_in_first_period() -> None:
    snapshots = load_vn_insurance_rule_snapshots_from_mapping(
        [
            {
                "policyholder_id": 21,
                "rule_kind": "random",
                "initial_decisions": [
                    {"sector_index": 0, "insured": True, "insurer_id": 11},
                    {"sector_index": 1, "insured": False},
                ],
            }
        ]
    )

    applications = apply_vn_insurance_rule_snapshots(snapshots, period=1)

    assert applications[0].result is None
    assert [decision.insurer_id for decision in applications[0].decisions] == [11, None]


def test_vn_insurance_rule_dispatch_validates_snapshot_shape() -> None:
    with pytest.raises(ValueError, match="duplicate policyholder_ids"):
        load_vn_insurance_rule_snapshots_from_mapping(
            [
                {"policyholder_id": 21, "rule_kind": "random"},
                {"policyholder_id": 21, "rule_kind": "best_info"},
            ]
        )

    with pytest.raises(ValueError, match="change_shock must be a boolean"):
        load_vn_insurance_rule_snapshots_from_mapping(
            [{"policyholder_id": 21, "rule_kind": "random", "change_shock": "false"}]
        )

    snapshots = load_vn_insurance_rule_snapshots_from_mapping(
        [{"policyholder_id": 21, "rule_kind": "random"}]
    )

    with pytest.raises(ValueError, match="requires parameters"):
        apply_vn_insurance_rule_snapshots(snapshots, period=2)
