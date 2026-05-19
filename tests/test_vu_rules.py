import pytest

from ims.model.entities import BAV, Insurer
from ims.model.vu_rules import (
    VUForeignInfoRuleKind,
    VUForeignInfoRuleParameters,
    apply_vu_foreign_info_rule,
    apply_vu_foreign_info_rule_to_insurer,
)


def _parameters() -> VUForeignInfoRuleParameters:
    return VUForeignInfoRuleParameters(
        premium_intercept_normal=[1.0, 2.0],
        premium_factor_normal=[0.5, 0.25],
        advertising_intercept_normal=[3.0, 4.0],
        advertising_factor_normal=[0.1, 0.2],
        premium_intercept_shock=[10.0, 20.0],
        premium_factor_shock=[1.0, 2.0],
        advertising_intercept_shock=[30.0, 40.0],
        advertising_factor_shock=[3.0, 4.0],
    )


def _bav_with_foreign_info() -> BAV:
    bav = BAV(entity_id=1)
    bav.service_state.insurer.pm = [100.0, 200.0]
    bav.service_state.insurer.wm = [10.0, 20.0]
    bav.service_state.insurer.dp = [300.0, 400.0]
    bav.service_state.insurer.dw = [30.0, 40.0]
    bav.service_state.insurer.mp = [500.0, 600.0]
    bav.service_state.insurer.mw = [50.0, 60.0]
    return bav


def test_vu_foreign_info_rule_uses_dumping_frmdinf_vectors() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[9.0, 8.0],
        advertising_current_sector=[7.0, 6.0],
        reserves_current=[1000.0, 2000.0],
    )

    result = apply_vu_foreign_info_rule(
        insurer,
        _bav_with_foreign_info(),
        _parameters(),
        period=2,
        interest_rate=0.05,
        rule_kind=VUForeignInfoRuleKind.DUMPING,
    )

    assert result.premiums_current_sector == [51.0, 52.0]
    assert result.advertising_current_sector == [4.0, 8.0]
    assert result.reserves_current == [1050.0, 2100.0]


def test_vu_foreign_info_rule_uses_average_and_attack_sources() -> None:
    insurer = Insurer(entity_id=7, reserves_current=[10.0, 20.0])
    bav = _bav_with_foreign_info()

    average_result = apply_vu_foreign_info_rule(
        insurer,
        bav,
        _parameters(),
        period=2,
        interest_rate=0.0,
        rule_kind=VUForeignInfoRuleKind.AVERAGE,
    )
    attack_result = apply_vu_foreign_info_rule(
        insurer,
        bav,
        _parameters(),
        period=2,
        interest_rate=0.0,
        rule_kind=VUForeignInfoRuleKind.ATTACK,
    )

    assert average_result.premiums_current_sector == [151.0, 102.0]
    assert average_result.advertising_current_sector == [6.0, 12.0]
    assert attack_result.premiums_current_sector == [251.0, 152.0]
    assert attack_result.advertising_current_sector == [8.0, 16.0]


def test_vu_foreign_info_rule_uses_shock_parameters_when_requested() -> None:
    insurer = Insurer(entity_id=7, reserves_current=[10.0, 20.0])

    result = apply_vu_foreign_info_rule(
        insurer,
        _bav_with_foreign_info(),
        _parameters(),
        period=2,
        interest_rate=0.0,
        rule_kind=VUForeignInfoRuleKind.DUMPING,
        change_shock=True,
    )

    assert result.premiums_current_sector == [110.0, 420.0]
    assert result.advertising_current_sector == [60.0, 120.0]


def test_vu_foreign_info_rule_keeps_start_values_for_first_period() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current=99.0,
        advertising_current=88.0,
        premiums_current_sector=[11.0, 22.0],
        advertising_current_sector=[33.0, 44.0],
        reserves_current=[100.0, 200.0],
    )

    result = apply_vu_foreign_info_rule(
        insurer,
        _bav_with_foreign_info(),
        _parameters(),
        period=1,
        interest_rate=0.1,
        rule_kind=VUForeignInfoRuleKind.ATTACK,
    )

    assert result.premiums_current_sector == [11.0, 22.0]
    assert result.advertising_current_sector == [33.0, 44.0]
    assert result.reserves_current == pytest.approx([110.0, 220.0])


def test_vu_foreign_info_rule_can_update_insurer_snapshot() -> None:
    insurer = Insurer(entity_id=7, reserves_current=[10.0, 20.0])

    result = apply_vu_foreign_info_rule_to_insurer(
        insurer,
        _bav_with_foreign_info(),
        _parameters(),
        period=2,
        interest_rate=0.1,
        rule_kind=VUForeignInfoRuleKind.DUMPING,
    )

    assert insurer.premiums_current_sector == result.premiums_current_sector
    assert insurer.advertising_current_sector == result.advertising_current_sector
    assert insurer.premiums_current == 51.0
    assert insurer.advertising_current == 4.0
    assert insurer.reserves_current == [11.0, 22.0]
