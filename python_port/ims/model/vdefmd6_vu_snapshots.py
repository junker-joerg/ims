from __future__ import annotations

from dataclasses import dataclass
import random

from ims.engine.rng import rand_normal_standard, rand_uniform_0_1
from ims.model.entities import Insurer, Policyholder
from ims.model.vdefmd6_population import (
    Vdefmd6InsurerDefinition,
    Vdefmd6Population,
)
from ims.model.vu_rules import (
    VUExpectedClaimRuleParameters,
    VUExpectedClaimRuleSnapshot,
    VUForeignInfoRuleKind,
    VUForeignInfoRuleParameters,
    VUForeignInfoRuleSnapshot,
    VUMarketShareMarkupRuleParameters,
    VUMarketShareMarkupRuleSnapshot,
    VUNetSwitcherMarkupRuleParameters,
    VUNetSwitcherMarkupRuleSnapshot,
    VURandomNormalRuleParameters,
    VURandomNormalRuleSnapshot,
    VURandomUniformRuleParameters,
    VURandomUniformRuleSnapshot,
    VUReserveMarkupRuleParameters,
    VUReserveMarkupRuleSnapshot,
)


VDEFMD6_VU_DRAW_POLICY_ID = "vdefmd6-modern-vu-id-major-v1"
VDEFMD6_INTEREST_RATE = 0.02
VDEFMD6_INFORMATION_COST = 0.8

_FOREIGN_INFO_KINDS = {
    7: VUForeignInfoRuleKind.DUMPING,
    8: VUForeignInfoRuleKind.AVERAGE,
    9: VUForeignInfoRuleKind.ATTACK,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6VUPreviousStateInput:
    insurer_id: int
    premiums_t_minus_1: tuple[float, float]
    advertising_t_minus_1: tuple[float, float]
    reserves_t_minus_1: tuple[float, float]
    policyholders_t_minus_1: tuple[float, float]
    policyholders_t_minus_2: tuple[float, float]
    claim_count_t_minus_1: tuple[int, int]
    claim_sum_t_minus_1: tuple[float, float]


@dataclass(frozen=True, slots=True)
class Vdefmd6VNPreviousStateInput:
    policyholder_id: int
    insured_t_minus_1: tuple[float, float]


@dataclass(frozen=True, slots=True)
class Vdefmd6BAVPreviousPeriodInputs:
    period: int
    active_insurer_ids_t_minus_1: tuple[int, ...]
    active_policyholder_ids_t_minus_1: tuple[int, ...]
    insurer_states: tuple[Vdefmd6VUPreviousStateInput, ...]
    policyholder_states: tuple[Vdefmd6VNPreviousStateInput, ...]
    interest_rate: float = VDEFMD6_INTEREST_RATE
    information_cost_per_lookup: float = VDEFMD6_INFORMATION_COST


@dataclass(frozen=True, slots=True)
class Vdefmd6InformationCostBoundary:
    historical_rules: tuple[int, ...] = (5, 6)
    historical_wealth_subtraction_evidenced: bool = True
    python_rule_result_exposes_cost: bool = True
    python_settlement_snapshot_accepts_cost: bool = False
    application_ready: bool = False


@dataclass(frozen=True, slots=True)
class Vdefmd6VUSnapshotBatch:
    period: int
    draw_policy_id: str
    bav_previous_period_inputs: Vdefmd6BAVPreviousPeriodInputs
    random_uniform_snapshots: tuple[VURandomUniformRuleSnapshot, ...]
    random_normal_snapshots: tuple[VURandomNormalRuleSnapshot, ...]
    reserve_markup_snapshots: tuple[VUReserveMarkupRuleSnapshot, ...]
    net_switcher_markup_snapshots: tuple[VUNetSwitcherMarkupRuleSnapshot, ...]
    market_share_markup_snapshots: tuple[VUMarketShareMarkupRuleSnapshot, ...]
    expected_claim_snapshots: tuple[VUExpectedClaimRuleSnapshot, ...]
    foreign_info_snapshots: tuple[VUForeignInfoRuleSnapshot, ...]
    uniform_value_count: int
    normal_value_count: int
    information_cost_boundary: Vdefmd6InformationCostBoundary
    runner_started: bool = False
    simulation_performed: bool = False
    historical_rng_equality_claimed: bool = False

    @property
    def snapshot_count(self) -> int:
        return sum(
            len(items)
            for items in (
                self.random_uniform_snapshots,
                self.random_normal_snapshots,
                self.reserve_markup_snapshots,
                self.net_switcher_markup_snapshots,
                self.market_share_markup_snapshots,
                self.expected_claim_snapshots,
                self.foreign_info_snapshots,
            )
        )


class _DrawCounter:
    def __init__(self, rng: random.Random) -> None:
        self._rng = rng
        self.uniform_value_count = 0
        self.normal_value_count = 0

    def four_uniforms(self) -> list[float]:
        self.uniform_value_count += 4
        return [rand_uniform_0_1(self._rng) for _ in range(4)]

    def four_normals(self) -> list[float]:
        self.normal_value_count += 4
        return [rand_normal_standard(self._rng) for _ in range(4)]


def build_vdefmd6_vu_snapshot_batch(
    population: Vdefmd6Population,
    *,
    period: int,
    rng: random.Random,
) -> Vdefmd6VUSnapshotBatch:
    """Materialize one Vdefmd6 VU input batch without applying its snapshots."""

    if type(period) is not int or not 2 <= period <= 49:
        raise ValueError("Vdefmd6 VU snapshot period must be between 2 and 49")
    if not isinstance(rng, random.Random):
        raise TypeError("Vdefmd6 VU snapshots require an explicit random.Random")

    insurer_by_id = _unique_entities(population.insurers, "insurer")
    policyholder_by_id = _unique_entities(population.policyholders, "policyholder")
    active_definitions = tuple(
        item
        for item in population.insurer_definitions
        if item.activation.activation_period <= period
    )
    missing_insurers = sorted(
        item.entity_id
        for item in active_definitions
        if item.entity_id not in insurer_by_id or not insurer_by_id[item.entity_id].active
    )
    if missing_insurers:
        raise ValueError(
            "Vdefmd6 VU population is missing active insurers: "
            + ", ".join(str(item) for item in missing_insurers)
        )

    active_policyholder_ids = tuple(
        sorted(
            item.entity_id
            for item in population.policyholder_definitions
            if item.activation.activation_period <= period
            and item.entity_id in policyholder_by_id
            and policyholder_by_id[item.entity_id].active
        )
    )
    expected_policyholder_ids = {
        item.entity_id
        for item in population.policyholder_definitions
        if item.activation.activation_period <= period
    }
    if set(active_policyholder_ids) != expected_policyholder_ids:
        missing = sorted(expected_policyholder_ids - set(active_policyholder_ids))
        raise ValueError(
            "Vdefmd6 VU snapshot inputs are missing active policyholders: "
            + ", ".join(str(item) for item in missing)
        )

    draws = _DrawCounter(rng)
    random_uniform: list[VURandomUniformRuleSnapshot] = []
    random_normal: list[VURandomNormalRuleSnapshot] = []
    reserve_markup: list[VUReserveMarkupRuleSnapshot] = []
    net_switcher: list[VUNetSwitcherMarkupRuleSnapshot] = []
    market_share: list[VUMarketShareMarkupRuleSnapshot] = []
    expected_claim: list[VUExpectedClaimRuleSnapshot] = []
    foreign_info: list[VUForeignInfoRuleSnapshot] = []

    for definition in active_definitions:
        snapshot = _build_snapshot(
            definition,
            insurer_by_id[definition.entity_id],
            active_policyholder_count=len(active_policyholder_ids),
            draws=draws,
        )
        if isinstance(snapshot, VURandomUniformRuleSnapshot):
            random_uniform.append(snapshot)
        elif isinstance(snapshot, VURandomNormalRuleSnapshot):
            random_normal.append(snapshot)
        elif isinstance(snapshot, VUReserveMarkupRuleSnapshot):
            reserve_markup.append(snapshot)
        elif isinstance(snapshot, VUNetSwitcherMarkupRuleSnapshot):
            net_switcher.append(snapshot)
        elif isinstance(snapshot, VUMarketShareMarkupRuleSnapshot):
            market_share.append(snapshot)
        elif isinstance(snapshot, VUExpectedClaimRuleSnapshot):
            expected_claim.append(snapshot)
        else:
            foreign_info.append(snapshot)

    return Vdefmd6VUSnapshotBatch(
        period=period,
        draw_policy_id=VDEFMD6_VU_DRAW_POLICY_ID,
        bav_previous_period_inputs=_build_bav_inputs(
            population,
            period=period,
            active_policyholder_ids=active_policyholder_ids,
        ),
        random_uniform_snapshots=tuple(random_uniform),
        random_normal_snapshots=tuple(random_normal),
        reserve_markup_snapshots=tuple(reserve_markup),
        net_switcher_markup_snapshots=tuple(net_switcher),
        market_share_markup_snapshots=tuple(market_share),
        expected_claim_snapshots=tuple(expected_claim),
        foreign_info_snapshots=tuple(foreign_info),
        uniform_value_count=draws.uniform_value_count,
        normal_value_count=draws.normal_value_count,
        information_cost_boundary=Vdefmd6InformationCostBoundary(),
    )


def _unique_entities(items: list[object], label: str) -> dict[int, object]:
    result: dict[int, object] = {}
    for item in items:
        entity_id = int(item.entity_id)
        if entity_id in result:
            raise ValueError(f"Vdefmd6 {label} ids must be unique: {entity_id}")
        result[entity_id] = item
    return result


def _two_float_values(values: list[float], fallback: float = 0.0) -> tuple[float, float]:
    normalized = [float(item) for item in values[:2]]
    if not normalized:
        return (float(fallback), float(fallback))
    if len(normalized) == 1:
        return (normalized[0], normalized[0])
    return (normalized[0], normalized[1])


def _two_int_values(values: list[int]) -> tuple[int, int]:
    normalized = [int(item) for item in values[:2]]
    if not normalized:
        return (0, 0)
    if len(normalized) == 1:
        return (normalized[0], normalized[0])
    return (normalized[0], normalized[1])


def _build_bav_inputs(
    population: Vdefmd6Population,
    *,
    period: int,
    active_policyholder_ids: tuple[int, ...],
) -> Vdefmd6BAVPreviousPeriodInputs:
    insurers = tuple(sorted((item for item in population.insurers if item.active), key=lambda item: item.entity_id))
    policyholders = tuple(
        sorted(
            (item for item in population.policyholders if item.entity_id in active_policyholder_ids),
            key=lambda item: item.entity_id,
        )
    )
    return Vdefmd6BAVPreviousPeriodInputs(
        period=period,
        active_insurer_ids_t_minus_1=tuple(item.entity_id for item in insurers),
        active_policyholder_ids_t_minus_1=active_policyholder_ids,
        insurer_states=tuple(_insurer_previous_state(item) for item in insurers),
        policyholder_states=tuple(_policyholder_previous_state(item) for item in policyholders),
    )


def _insurer_previous_state(insurer: Insurer) -> Vdefmd6VUPreviousStateInput:
    return Vdefmd6VUPreviousStateInput(
        insurer_id=insurer.entity_id,
        premiums_t_minus_1=_two_float_values(
            insurer.premiums_current_sector,
            insurer.premiums_current,
        ),
        advertising_t_minus_1=_two_float_values(
            insurer.advertising_current_sector,
            insurer.advertising_current,
        ),
        reserves_t_minus_1=_two_float_values(insurer.reserves_current),
        policyholders_t_minus_1=_two_float_values(
            insurer.policyholders_current_sector,
            insurer.policyholders_current,
        ),
        policyholders_t_minus_2=_two_float_values(
            insurer.policyholders_prev_sector,
            insurer.policyholders_prev,
        ),
        claim_count_t_minus_1=_two_int_values(insurer.claims_count_current),
        claim_sum_t_minus_1=_two_float_values(insurer.claims_sum_current),
    )


def _policyholder_previous_state(
    policyholder: Policyholder,
) -> Vdefmd6VNPreviousStateInput:
    return Vdefmd6VNPreviousStateInput(
        policyholder_id=policyholder.entity_id,
        insured_t_minus_1=_two_float_values(
            policyholder.insured_current_sector,
            policyholder.insured_current,
        ),
    )


def _build_snapshot(
    definition: Vdefmd6InsurerDefinition,
    insurer: Insurer,
    *,
    active_policyholder_count: int,
    draws: _DrawCounter,
) -> object:
    rule_id = definition.action.rule_id
    values = definition.parameters
    if len(values) != 16:
        raise ValueError(f"Vdefmd6 VU {definition.entity_id} requires 16 parameters")
    common = {
        "insurer_id": definition.entity_id,
        "interest_rate": VDEFMD6_INTEREST_RATE,
        "change_shock": False,
    }
    if rule_id == 1:
        return VURandomUniformRuleSnapshot(
            **common,
            parameters=_random_uniform_parameters(values),
            random_draws=draws.four_uniforms(),
        )
    if rule_id == 2:
        return VURandomNormalRuleSnapshot(
            **common,
            parameters=_linear_parameters(values, VURandomNormalRuleParameters),
            normal_draws=draws.four_normals(),
        )
    if rule_id == 3:
        return VUReserveMarkupRuleSnapshot(
            **common,
            parameters=_markup_parameters(values, VUReserveMarkupRuleParameters),
            reserve_thresholds=[
                definition.aspiration_sector_1[0],
                definition.aspiration_sector_2[0],
            ],
        )
    if rule_id == 4:
        return VUNetSwitcherMarkupRuleSnapshot(
            **common,
            parameters=_markup_parameters(values, VUNetSwitcherMarkupRuleParameters),
            net_switcher_thresholds=[
                definition.aspiration_sector_1[1],
                definition.aspiration_sector_2[1],
            ],
            previous_policyholders_sector=list(
                _two_float_values(
                    insurer.policyholders_prev_sector,
                    insurer.policyholders_prev,
                )
            ),
        )
    if rule_id == 5:
        return VUMarketShareMarkupRuleSnapshot(
            **common,
            parameters=_markup_parameters(values, VUMarketShareMarkupRuleParameters),
            market_share_thresholds=[
                definition.aspiration_sector_1[2],
                definition.aspiration_sector_2[2],
            ],
            active_policyholder_count=active_policyholder_count,
        )
    if rule_id == 6:
        return VUExpectedClaimRuleSnapshot(
            **common,
            parameters=_markup_parameters(values, VUExpectedClaimRuleParameters),
        )
    if rule_id in _FOREIGN_INFO_KINDS:
        return VUForeignInfoRuleSnapshot(
            **common,
            rule_kind=_FOREIGN_INFO_KINDS[rule_id],
            parameters=_linear_parameters(values, VUForeignInfoRuleParameters),
        )
    raise ValueError(f"unsupported Vdefmd6 VU rule_id: {rule_id}")


def _random_uniform_parameters(values: tuple[float, ...]) -> VURandomUniformRuleParameters:
    return VURandomUniformRuleParameters(
        premium_factor_normal=[values[0], values[2]],
        advertising_factor_normal=[values[4], values[6]],
        premium_factor_shock=[values[1], values[3]],
        advertising_factor_shock=[values[5], values[7]],
    )


def _linear_parameters(values: tuple[float, ...], parameter_type: type) -> object:
    return parameter_type(
        premium_intercept_normal=[values[0], values[4]],
        premium_factor_normal=[values[2], values[6]],
        advertising_intercept_normal=[values[8], values[12]],
        advertising_factor_normal=[values[10], values[14]],
        premium_intercept_shock=[values[1], values[5]],
        premium_factor_shock=[values[3], values[7]],
        advertising_intercept_shock=[values[9], values[13]],
        advertising_factor_shock=[values[11], values[15]],
    )


def _markup_parameters(values: tuple[float, ...], parameter_type: type) -> object:
    return parameter_type(
        premium_below_normal=[values[0], values[4]],
        premium_above_normal=[values[2], values[6]],
        advertising_below_normal=[values[8], values[12]],
        advertising_above_normal=[values[10], values[14]],
        premium_below_shock=[values[1], values[5]],
        premium_above_shock=[values[3], values[7]],
        advertising_below_shock=[values[9], values[13]],
        advertising_above_shock=[values[11], values[15]],
    )
