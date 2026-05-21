from ims.model.vn_damage_rules import (
    VNDamageRuleDraws,
    VNDamageRuleParameters,
    apply_vn_damage_rule,
    vn_damage_rule_draws_from_mapping,
    vn_damage_rule_parameters_from_mapping,
)


def _damage_parameters() -> VNDamageRuleParameters:
    return VNDamageRuleParameters(
        damage_intercept_normal=[10.0, 20.0],
        damage_factor_normal=[2.0, 3.0],
        damage_intercept_shock=[100.0, 200.0],
        damage_factor_shock=[4.0, 5.0],
    )


def test_vn_damage_rule_applies_normal_parameters_with_explicit_draws() -> None:
    result = apply_vn_damage_rule(
        _damage_parameters(),
        damage_thresholds=[0.7, 0.4],
        draws=VNDamageRuleDraws(
            trigger_draws=[0.6, 0.5],
            amount_draws=[1.5, 2.0],
        ),
    )

    assert result.triggered == [True, False]
    assert result.damages == [13.0, 0.0]
    assert result.trigger_draws == [0.6, 0.5]
    assert result.amount_draws == [1.5, 2.0]


def test_vn_damage_rule_uses_shock_parameters() -> None:
    result = apply_vn_damage_rule(
        _damage_parameters(),
        damage_thresholds=[0.9, 0.8],
        draws=VNDamageRuleDraws(
            trigger_draws=[0.1, 0.2],
            amount_draws=[2.0, 3.0],
        ),
        change_shock=True,
    )

    assert result.triggered == [True, True]
    assert result.damages == [108.0, 215.0]


def test_vn_damage_rule_loader_reads_parameter_and_draw_blocks() -> None:
    parameters = vn_damage_rule_parameters_from_mapping(
        {
            "damage_intercept_normal": [1.0, 2.0],
            "damage_factor_normal": [3.0, 4.0],
            "damage_intercept_shock": [5.0, 6.0],
            "damage_factor_shock": [7.0, 8.0],
        }
    )
    draws = vn_damage_rule_draws_from_mapping(
        {
            "trigger_draws": [0.1, 0.2],
            "amount_draws": [0.3, 0.4],
        }
    )

    assert parameters.damage_intercept_normal == [1.0, 2.0]
    assert parameters.damage_factor_shock == [7.0, 8.0]
    assert draws.trigger_draws == [0.1, 0.2]
    assert draws.amount_draws == [0.3, 0.4]
