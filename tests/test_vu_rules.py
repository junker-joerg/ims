import pytest

from ims.model.entities import BAV, Insurer
from ims.model.vu_rules import (
    VUExpectedClaimRuleParameters,
    VUForeignInfoRuleKind,
    VUForeignInfoRuleParameters,
    VUMarketShareMarkupRuleParameters,
    VUReserveMarkupRuleParameters,
    apply_vu_expected_claim_rule,
    apply_vu_expected_claim_rule_snapshots,
    apply_vu_expected_claim_rule_to_insurer,
    apply_vu_foreign_info_rule_snapshots,
    apply_vu_foreign_info_rule,
    apply_vu_foreign_info_rule_to_insurer,
    apply_vu_market_share_markup_rule,
    apply_vu_market_share_markup_rule_snapshots,
    apply_vu_market_share_markup_rule_to_insurer,
    apply_vu_reserve_markup_rule,
    apply_vu_reserve_markup_rule_snapshots,
    apply_vu_reserve_markup_rule_to_insurer,
    load_vu_expected_claim_rule_snapshots_from_mapping,
    load_vu_foreign_info_rule_snapshots_from_mapping,
    load_vu_market_share_markup_rule_snapshots_from_mapping,
    load_vu_reserve_markup_rule_snapshots_from_mapping,
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


def _reserve_markup_parameters() -> VUReserveMarkupRuleParameters:
    return VUReserveMarkupRuleParameters(
        premium_below_normal=[1.1, 1.2],
        premium_above_normal=[0.9, 0.8],
        advertising_below_normal=[1.3, 1.4],
        advertising_above_normal=[0.7, 0.6],
        premium_below_shock=[2.1, 2.2],
        premium_above_shock=[1.9, 1.8],
        advertising_below_shock=[2.3, 2.4],
        advertising_above_shock=[1.7, 1.6],
    )


def _expected_claim_parameters() -> VUExpectedClaimRuleParameters:
    return VUExpectedClaimRuleParameters(
        premium_below_normal=[1.1, 1.2],
        premium_above_normal=[0.9, 0.8],
        advertising_below_normal=[1.3, 1.4],
        advertising_above_normal=[0.7, 0.6],
        premium_below_shock=[2.1, 2.2],
        premium_above_shock=[1.9, 1.8],
        advertising_below_shock=[2.3, 2.4],
        advertising_above_shock=[1.7, 1.6],
    )


def _expected_claim_parameter_mapping() -> dict[str, list[float]]:
    return {
        "premium_below_normal": [1.1, 1.2],
        "premium_above_normal": [0.9, 0.8],
        "advertising_below_normal": [1.3, 1.4],
        "advertising_above_normal": [0.7, 0.6],
        "premium_below_shock": [2.1, 2.2],
        "premium_above_shock": [1.9, 1.8],
        "advertising_below_shock": [2.3, 2.4],
        "advertising_above_shock": [1.7, 1.6],
    }


def _market_share_markup_parameters() -> VUMarketShareMarkupRuleParameters:
    return VUMarketShareMarkupRuleParameters(
        premium_below_normal=[1.1, 1.2],
        premium_above_normal=[0.9, 0.8],
        advertising_below_normal=[1.3, 1.4],
        advertising_above_normal=[0.7, 0.6],
        premium_below_shock=[2.1, 2.2],
        premium_above_shock=[1.9, 1.8],
        advertising_below_shock=[2.3, 2.4],
        advertising_above_shock=[1.7, 1.6],
    )


def _market_share_markup_parameter_mapping() -> dict[str, list[float]]:
    return {
        "premium_below_normal": [1.1, 1.2],
        "premium_above_normal": [0.9, 0.8],
        "advertising_below_normal": [1.3, 1.4],
        "advertising_above_normal": [0.7, 0.6],
        "premium_below_shock": [2.1, 2.2],
        "premium_above_shock": [1.9, 1.8],
        "advertising_below_shock": [2.3, 2.4],
        "advertising_above_shock": [1.7, 1.6],
    }


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


def test_vu_foreign_info_rule_snapshots_load_and_apply_to_matching_insurers() -> None:
    bav = _bav_with_foreign_info()
    insurers = [Insurer(entity_id=7, reserves_current=[100.0, 200.0]), Insurer(entity_id=8)]
    snapshots = load_vu_foreign_info_rule_snapshots_from_mapping(
        [
            {
                "insurer_id": 7,
                "rule_kind": "average",
                "interest_rate": 0.05,
                "parameters": {
                    "premium_intercept_normal": [1.0, 2.0],
                    "premium_factor_normal": [0.5, 0.25],
                    "advertising_intercept_normal": [3.0, 4.0],
                    "advertising_factor_normal": [0.1, 0.2],
                    "premium_intercept_shock": [10.0, 20.0],
                    "premium_factor_shock": [1.0, 2.0],
                    "advertising_intercept_shock": [30.0, 40.0],
                    "advertising_factor_shock": [3.0, 4.0],
                },
            }
        ]
    )

    applications = apply_vu_foreign_info_rule_snapshots(insurers, bav, snapshots, period=2)

    assert len(applications) == 1
    assert applications[0].insurer_id == 7
    assert applications[0].rule_kind == VUForeignInfoRuleKind.AVERAGE
    assert insurers[0].premiums_current_sector == [151.0, 102.0]
    assert insurers[0].advertising_current_sector == [6.0, 12.0]
    assert insurers[0].reserves_current == [105.0, 210.0]
    assert insurers[1].premiums_current_sector == []


def test_vu_foreign_info_rule_snapshots_support_change_shock() -> None:
    bav = _bav_with_foreign_info()
    insurers = [Insurer(entity_id=7, reserves_current=[10.0, 20.0])]
    snapshots = load_vu_foreign_info_rule_snapshots_from_mapping(
        [
            {
                "insurer_id": 7,
                "rule_kind": "dumping",
                "change_shock": True,
                "parameters": {
                    "premium_intercept_normal": [1.0, 2.0],
                    "premium_factor_normal": [0.5, 0.25],
                    "advertising_intercept_normal": [3.0, 4.0],
                    "advertising_factor_normal": [0.1, 0.2],
                    "premium_intercept_shock": [10.0, 20.0],
                    "premium_factor_shock": [1.0, 2.0],
                    "advertising_intercept_shock": [30.0, 40.0],
                    "advertising_factor_shock": [3.0, 4.0],
                },
            }
        ]
    )

    apply_vu_foreign_info_rule_snapshots(insurers, bav, snapshots, period=2)

    assert insurers[0].premiums_current_sector == [110.0, 420.0]
    assert insurers[0].advertising_current_sector == [60.0, 120.0]


def test_vu_foreign_info_rule_snapshots_reject_unknown_insurer() -> None:
    snapshots = load_vu_foreign_info_rule_snapshots_from_mapping(
        [
            {
                "insurer_id": 99,
                "rule_kind": "attack",
                "parameters": {
                    "premium_intercept_normal": [1.0, 2.0],
                    "premium_factor_normal": [0.5, 0.25],
                    "advertising_intercept_normal": [3.0, 4.0],
                    "advertising_factor_normal": [0.1, 0.2],
                    "premium_intercept_shock": [10.0, 20.0],
                    "premium_factor_shock": [1.0, 2.0],
                    "advertising_intercept_shock": [30.0, 40.0],
                    "advertising_factor_shock": [3.0, 4.0],
                },
            }
        ]
    )

    with pytest.raises(ValueError, match="unknown insurer"):
        apply_vu_foreign_info_rule_snapshots([], _bav_with_foreign_info(), snapshots, period=2)


def test_vu_foreign_info_rule_snapshots_reject_duplicate_insurer_targets() -> None:
    snapshots = [
        load_vu_foreign_info_rule_snapshots_from_mapping(
            [
                {
                    "insurer_id": 7,
                    "rule_kind": "attack",
                    "parameters": {
                        "premium_intercept_normal": [1.0, 2.0],
                        "premium_factor_normal": [0.5, 0.25],
                        "advertising_intercept_normal": [3.0, 4.0],
                        "advertising_factor_normal": [0.1, 0.2],
                        "premium_intercept_shock": [10.0, 20.0],
                        "premium_factor_shock": [1.0, 2.0],
                        "advertising_intercept_shock": [30.0, 40.0],
                        "advertising_factor_shock": [3.0, 4.0],
                    },
                }
            ]
        )[0]
        for _ in range(2)
    ]

    with pytest.raises(ValueError, match="duplicate"):
        apply_vu_foreign_info_rule_snapshots([Insurer(entity_id=7)], _bav_with_foreign_info(), snapshots, period=2)


def test_vu_foreign_info_rule_snapshots_reject_missing_parameter_lists() -> None:
    with pytest.raises(ValueError, match="premium_factor_normal"):
        load_vu_foreign_info_rule_snapshots_from_mapping(
            [
                {
                    "insurer_id": 7,
                    "rule_kind": "average",
                    "parameters": {
                        "premium_intercept_normal": [1.0, 2.0],
                    },
                }
            ]
        )


def test_vu_foreign_info_rule_snapshots_reject_bad_rule_kind() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        load_vu_foreign_info_rule_snapshots_from_mapping(
            [
                {
                    "insurer_id": 7,
                    "rule_kind": "not-historical",
                    "parameters": {
                        "premium_intercept_normal": [1.0, 2.0],
                        "premium_factor_normal": [0.5, 0.25],
                        "advertising_intercept_normal": [3.0, 4.0],
                        "advertising_factor_normal": [0.1, 0.2],
                        "premium_intercept_shock": [10.0, 20.0],
                        "premium_factor_shock": [1.0, 2.0],
                        "advertising_intercept_shock": [30.0, 40.0],
                        "advertising_factor_shock": [3.0, 4.0],
                    },
                }
            ]
        )


def test_vu_reserve_markup_rule_uses_reserve_thresholds_for_normal_case() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
    )

    result = apply_vu_reserve_markup_rule(
        insurer,
        _reserve_markup_parameters(),
        period=2,
        reserve_thresholds=[75.0, 100.0],
        interest_rate=0.05,
    )

    assert result.premiums_current_sector == pytest.approx([110.0, 160.0])
    assert result.advertising_current_sector == pytest.approx([13.0, 12.0])
    assert result.reserves_current == pytest.approx([52.5, 157.5])
    assert result.threshold_comparison_values == [75.0, 100.0]


def test_vu_reserve_markup_rule_uses_zero_threshold_for_change_shock() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[-1.0, 150.0],
    )

    result = apply_vu_reserve_markup_rule(
        insurer,
        _reserve_markup_parameters(),
        period=2,
        reserve_thresholds=[999.0, 999.0],
        interest_rate=0.0,
        change_shock=True,
    )

    assert result.premiums_current_sector == [210.0, 360.0]
    assert result.advertising_current_sector == [23.0, 32.0]
    assert result.threshold_comparison_values == [0.0, 0.0]


def test_vu_reserve_markup_rule_keeps_start_values_for_first_period() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
    )

    result = apply_vu_reserve_markup_rule(
        insurer,
        _reserve_markup_parameters(),
        period=1,
        reserve_thresholds=[0.0, 0.0],
        interest_rate=0.1,
    )

    assert result.premiums_current_sector == [100.0, 200.0]
    assert result.advertising_current_sector == [10.0, 20.0]
    assert result.reserves_current == pytest.approx([55.0, 165.0])


def test_vu_reserve_markup_rule_can_update_insurer_snapshot() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
    )

    result = apply_vu_reserve_markup_rule_to_insurer(
        insurer,
        _reserve_markup_parameters(),
        period=2,
        reserve_thresholds=[75.0, 100.0],
        interest_rate=0.05,
    )

    assert insurer.premiums_current_sector == result.premiums_current_sector
    assert insurer.advertising_current_sector == result.advertising_current_sector
    assert insurer.premiums_current == pytest.approx(110.0)
    assert insurer.advertising_current == pytest.approx(13.0)
    assert insurer.reserves_current == pytest.approx([52.5, 157.5])


def test_vu_reserve_markup_rule_snapshots_load_and_apply_to_matching_insurers() -> None:
    insurers = [
        Insurer(
            entity_id=7,
            premiums_current_sector=[100.0, 200.0],
            advertising_current_sector=[10.0, 20.0],
            reserves_current=[50.0, 150.0],
        ),
        Insurer(entity_id=8),
    ]
    snapshots = load_vu_reserve_markup_rule_snapshots_from_mapping(
        [
            {
                "insurer_id": 7,
                "reserve_thresholds": [75.0, 100.0],
                "interest_rate": 0.05,
                "parameters": {
                    "premium_below_normal": [1.1, 1.2],
                    "premium_above_normal": [0.9, 0.8],
                    "advertising_below_normal": [1.3, 1.4],
                    "advertising_above_normal": [0.7, 0.6],
                    "premium_below_shock": [2.1, 2.2],
                    "premium_above_shock": [1.9, 1.8],
                    "advertising_below_shock": [2.3, 2.4],
                    "advertising_above_shock": [1.7, 1.6],
                },
            }
        ]
    )

    applications = apply_vu_reserve_markup_rule_snapshots(insurers, snapshots, period=2)

    assert len(applications) == 1
    assert applications[0].insurer_id == 7
    assert insurers[0].premiums_current_sector == pytest.approx([110.0, 160.0])
    assert insurers[0].advertising_current_sector == pytest.approx([13.0, 12.0])
    assert insurers[1].premiums_current_sector == []


def test_vu_reserve_markup_rule_snapshots_reject_unknown_and_duplicate_targets() -> None:
    snapshots = load_vu_reserve_markup_rule_snapshots_from_mapping(
        [
            {
                "insurer_id": 7,
                "parameters": {
                    "premium_below_normal": [1.1, 1.2],
                    "premium_above_normal": [0.9, 0.8],
                    "advertising_below_normal": [1.3, 1.4],
                    "advertising_above_normal": [0.7, 0.6],
                    "premium_below_shock": [2.1, 2.2],
                    "premium_above_shock": [1.9, 1.8],
                    "advertising_below_shock": [2.3, 2.4],
                    "advertising_above_shock": [1.7, 1.6],
                },
            }
        ]
    )

    with pytest.raises(ValueError, match="unknown insurer"):
        apply_vu_reserve_markup_rule_snapshots([], snapshots, period=2)

    with pytest.raises(ValueError, match="duplicate"):
        apply_vu_reserve_markup_rule_snapshots([Insurer(entity_id=7)], snapshots + snapshots, period=2)


def test_vu_expected_claim_rule_uses_average_claim_values_for_normal_case() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        claims_count_current=[2, 4],
        claims_sum_current=[250.0, 600.0],
    )

    result = apply_vu_expected_claim_rule(
        insurer,
        _expected_claim_parameters(),
        period=2,
        interest_rate=0.05,
    )

    assert result.expected_claim_values == [125.0, 150.0]
    assert result.premiums_current_sector == pytest.approx([110.0, 160.0])
    assert result.advertising_current_sector == pytest.approx([13.0, 12.0])
    assert result.reserves_current == pytest.approx([52.5, 157.5])


def test_vu_expected_claim_rule_uses_zero_when_claim_count_is_zero() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[0.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        claims_count_current=[0, 0],
        claims_sum_current=[250.0, 600.0],
    )

    result = apply_vu_expected_claim_rule(
        insurer,
        _expected_claim_parameters(),
        period=2,
        interest_rate=0.0,
    )

    assert result.expected_claim_values == [0.0, 0.0]
    assert result.premiums_current_sector == pytest.approx([0.0, 160.0])
    assert result.advertising_current_sector == pytest.approx([13.0, 12.0])


def test_vu_expected_claim_rule_uses_shock_parameters_when_requested() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        claims_count_current=[2, 4],
        claims_sum_current=[250.0, 600.0],
    )

    result = apply_vu_expected_claim_rule(
        insurer,
        _expected_claim_parameters(),
        period=2,
        interest_rate=0.0,
        change_shock=True,
    )

    assert result.premiums_current_sector == pytest.approx([210.0, 360.0])
    assert result.advertising_current_sector == pytest.approx([23.0, 32.0])


def test_vu_expected_claim_rule_keeps_start_values_for_first_period() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        claims_count_current=[2, 4],
        claims_sum_current=[250.0, 600.0],
    )

    result = apply_vu_expected_claim_rule(
        insurer,
        _expected_claim_parameters(),
        period=1,
        interest_rate=0.1,
    )

    assert result.premiums_current_sector == [100.0, 200.0]
    assert result.advertising_current_sector == [10.0, 20.0]
    assert result.reserves_current == pytest.approx([55.0, 165.0])


def test_vu_expected_claim_rule_can_update_insurer_snapshot() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        claims_count_current=[2, 4],
        claims_sum_current=[250.0, 600.0],
    )

    result = apply_vu_expected_claim_rule_to_insurer(
        insurer,
        _expected_claim_parameters(),
        period=2,
        interest_rate=0.05,
    )

    assert insurer.premiums_current_sector == result.premiums_current_sector
    assert insurer.advertising_current_sector == result.advertising_current_sector
    assert insurer.premiums_current == pytest.approx(110.0)
    assert insurer.advertising_current == pytest.approx(13.0)
    assert insurer.reserves_current == pytest.approx([52.5, 157.5])


def test_vu_expected_claim_rule_snapshots_load_and_apply_to_matching_insurers() -> None:
    insurers = [
        Insurer(
            entity_id=7,
            premiums_current_sector=[100.0, 200.0],
            advertising_current_sector=[10.0, 20.0],
            reserves_current=[50.0, 150.0],
            claims_count_current=[2, 4],
            claims_sum_current=[250.0, 600.0],
        ),
        Insurer(entity_id=8),
    ]
    snapshots = load_vu_expected_claim_rule_snapshots_from_mapping(
        [
            {
                "insurer_id": 7,
                "interest_rate": 0.05,
                "parameters": _expected_claim_parameter_mapping(),
            }
        ]
    )

    applications = apply_vu_expected_claim_rule_snapshots(insurers, snapshots, period=2)

    assert len(applications) == 1
    assert applications[0].insurer_id == 7
    assert insurers[0].premiums_current_sector == pytest.approx([110.0, 160.0])
    assert insurers[0].advertising_current_sector == pytest.approx([13.0, 12.0])
    assert insurers[1].premiums_current_sector == []


def test_vu_expected_claim_rule_snapshots_reject_unknown_and_duplicate_targets() -> None:
    snapshots = load_vu_expected_claim_rule_snapshots_from_mapping(
        [
            {
                "insurer_id": 7,
                "parameters": _expected_claim_parameter_mapping(),
            }
        ]
    )

    with pytest.raises(ValueError, match="unknown insurer"):
        apply_vu_expected_claim_rule_snapshots([], snapshots, period=2)

    with pytest.raises(ValueError, match="duplicate"):
        apply_vu_expected_claim_rule_snapshots([Insurer(entity_id=7)], snapshots + snapshots, period=2)


def test_vu_market_share_markup_rule_uses_market_share_thresholds_for_normal_case() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        policyholders_current_sector=[30.0, 80.0],
    )

    result = apply_vu_market_share_markup_rule(
        insurer,
        _market_share_markup_parameters(),
        period=2,
        market_share_thresholds=[0.4, 0.7],
        active_policyholder_count=100,
        interest_rate=0.05,
    )

    assert result.market_share_values == pytest.approx([0.3, 0.8])
    assert result.premiums_current_sector == pytest.approx([110.0, 160.0])
    assert result.advertising_current_sector == pytest.approx([13.0, 12.0])
    assert result.reserves_current == pytest.approx([52.5, 157.5])


def test_vu_market_share_markup_rule_uses_zero_when_active_policyholder_count_is_zero() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        policyholders_current_sector=[30.0, 80.0],
    )

    result = apply_vu_market_share_markup_rule(
        insurer,
        _market_share_markup_parameters(),
        period=2,
        market_share_thresholds=[0.0, 0.0],
        active_policyholder_count=0,
        interest_rate=0.0,
    )

    assert result.market_share_values == [0.0, 0.0]
    assert result.premiums_current_sector == pytest.approx([110.0, 240.0])
    assert result.advertising_current_sector == pytest.approx([13.0, 28.0])


def test_vu_market_share_markup_rule_uses_shock_parameters_when_requested() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        policyholders_current_sector=[30.0, 80.0],
    )

    result = apply_vu_market_share_markup_rule(
        insurer,
        _market_share_markup_parameters(),
        period=2,
        market_share_thresholds=[0.4, 0.7],
        active_policyholder_count=100,
        interest_rate=0.0,
        change_shock=True,
    )

    assert result.market_share_values == pytest.approx([0.3, 0.8])
    assert result.premiums_current_sector == pytest.approx([210.0, 360.0])
    assert result.advertising_current_sector == pytest.approx([23.0, 32.0])


def test_vu_market_share_markup_rule_keeps_start_values_for_first_period() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        policyholders_current_sector=[30.0, 80.0],
    )

    result = apply_vu_market_share_markup_rule(
        insurer,
        _market_share_markup_parameters(),
        period=1,
        market_share_thresholds=[0.4, 0.7],
        active_policyholder_count=100,
        interest_rate=0.1,
    )

    assert result.premiums_current_sector == [100.0, 200.0]
    assert result.advertising_current_sector == [10.0, 20.0]
    assert result.reserves_current == pytest.approx([55.0, 165.0])
    assert result.market_share_values == pytest.approx([0.3, 0.8])


def test_vu_market_share_markup_rule_can_update_insurer_snapshot() -> None:
    insurer = Insurer(
        entity_id=7,
        premiums_current_sector=[100.0, 200.0],
        advertising_current_sector=[10.0, 20.0],
        reserves_current=[50.0, 150.0],
        policyholders_current_sector=[30.0, 80.0],
    )

    result = apply_vu_market_share_markup_rule_to_insurer(
        insurer,
        _market_share_markup_parameters(),
        period=2,
        market_share_thresholds=[0.4, 0.7],
        active_policyholder_count=100,
        interest_rate=0.05,
    )

    assert insurer.premiums_current_sector == result.premiums_current_sector
    assert insurer.advertising_current_sector == result.advertising_current_sector
    assert insurer.premiums_current == pytest.approx(110.0)
    assert insurer.advertising_current == pytest.approx(13.0)
    assert insurer.reserves_current == pytest.approx([52.5, 157.5])


def test_vu_market_share_markup_rule_snapshots_load_and_apply_to_matching_insurers() -> None:
    insurers = [
        Insurer(
            entity_id=7,
            premiums_current_sector=[100.0, 200.0],
            advertising_current_sector=[10.0, 20.0],
            reserves_current=[50.0, 150.0],
            policyholders_current_sector=[30.0, 80.0],
        ),
        Insurer(entity_id=8),
    ]
    snapshots = load_vu_market_share_markup_rule_snapshots_from_mapping(
        [
            {
                "insurer_id": 7,
                "market_share_thresholds": [0.4, 0.7],
                "active_policyholder_count": 100,
                "interest_rate": 0.05,
                "parameters": _market_share_markup_parameter_mapping(),
            }
        ]
    )

    applications = apply_vu_market_share_markup_rule_snapshots(insurers, snapshots, period=2)

    assert len(applications) == 1
    assert applications[0].insurer_id == 7
    assert insurers[0].premiums_current_sector == pytest.approx([110.0, 160.0])
    assert insurers[0].advertising_current_sector == pytest.approx([13.0, 12.0])
    assert insurers[1].premiums_current_sector == []


def test_vu_market_share_markup_rule_snapshots_reject_unknown_and_duplicate_targets() -> None:
    snapshots = load_vu_market_share_markup_rule_snapshots_from_mapping(
        [
            {
                "insurer_id": 7,
                "active_policyholder_count": 100,
                "parameters": _market_share_markup_parameter_mapping(),
            }
        ]
    )

    with pytest.raises(ValueError, match="unknown insurer"):
        apply_vu_market_share_markup_rule_snapshots([], snapshots, period=2)

    with pytest.raises(ValueError, match="duplicate"):
        apply_vu_market_share_markup_rule_snapshots([Insurer(entity_id=7)], snapshots + snapshots, period=2)
