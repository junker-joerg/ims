from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import random

from ims.engine.rng import rand_normal_standard, rand_uniform_0_1
from ims.model.entities import Policyholder
from ims.model.vdefmd6_population import VDEFMD6_MAX_PERIODS, Vdefmd6Population
from ims.model.vn_damage_rules import VNDamageRuleDraws, VNDamageRuleParameters
from ims.model.vn_insurance_rules import (
    VNBestInfoInsuranceRuleParameters,
    VNCompulsoryInsuranceRuleDraws,
    VNInsuranceRuleKind,
    VNInsuranceRuleSnapshot,
    VNPreferenceInsuranceRuleDraws,
    VNPreferenceInsuranceRuleParameters,
    VNPreferenceInsurerInput,
    VNRandomInsuranceRuleDraws,
    VNRandomInsuranceRuleParameters,
    VNSampleSearchInsuranceRuleDraws,
    VNSampleSearchInsuranceRuleParameters,
    VNSampleSearchInsurerInput,
    VNSearchInsuranceHistoryEntry,
    VNSearchInsuranceRuleDraws,
    VNSearchInsuranceRuleParameters,
)
from ims.model.vn_rules import VNDamageSettlementSnapshot, VNInsuranceDecision


VDEFMD6_PRE_SHOCK_DRAW_POLICY_ID = "vdefmd6-modern-period-major-v1"
VDEFMD6_INFORMATION_COST = 0.8
VDEFMD6_SHOCK_PERIOD = 50

_RULE_KINDS = {
    1: VNInsuranceRuleKind.COMPULSORY,
    2: VNInsuranceRuleKind.RANDOM,
    3: VNInsuranceRuleKind.PREFERENCE,
    4: VNInsuranceRuleKind.SEARCH_HISTORY,
    5: VNInsuranceRuleKind.SAMPLE_SEARCH,
    6: VNInsuranceRuleKind.BEST_INFO,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6PreShockDrawSummary:
    uniform_values: int
    normal_values: int
    damage_threshold_uniform_values: int
    insurance_uniform_values: int


@dataclass(frozen=True, slots=True)
class Vdefmd6PreShockSnapshotBatch:
    period: int
    draw_policy_id: str
    active_insurer_ids: tuple[int, ...]
    change_shock: bool
    insurance_snapshots: tuple[VNInsuranceRuleSnapshot, ...]
    damage_snapshots: tuple[VNDamageSettlementSnapshot, ...]
    draw_summary: Vdefmd6PreShockDrawSummary
    runner_started: bool = False
    simulation_performed: bool = False
    historical_rng_equality_claimed: bool = False


class _DrawCounter:
    def __init__(self, rng: random.Random) -> None:
        self._rng = rng
        self.uniform_values = 0
        self.normal_values = 0

    def uniform(self) -> float:
        self.uniform_values += 1
        return rand_uniform_0_1(self._rng)

    def normal(self) -> float:
        self.normal_values += 1
        return rand_normal_standard(self._rng)


def build_vdefmd6_pre_shock_snapshot_batch(
    population: Vdefmd6Population,
    *,
    period: int,
    rng: random.Random,
    search_history_by_policyholder: Mapping[
        int, list[VNSearchInsuranceHistoryEntry]
    ]
    | None = None,
    market_damage_indicator: float = 0.0,
) -> Vdefmd6PreShockSnapshotBatch:
    """Materialize one modern Vdefmd6 VN input batch without applying it."""

    if type(period) is not int or not 2 <= period <= 49:
        raise ValueError("Vdefmd6 pre-shock snapshot period must be between 2 and 49")
    return _build_vdefmd6_vn_snapshot_batch(
        population,
        period=period,
        rng=rng,
        search_history_by_policyholder=search_history_by_policyholder,
        market_damage_indicator=market_damage_indicator,
        change_shock=False,
    )


def build_vdefmd6_shock_snapshot_batch(
    population: Vdefmd6Population,
    *,
    period: int,
    rng: random.Random,
    search_history_by_policyholder: Mapping[
        int, list[VNSearchInsuranceHistoryEntry]
    ]
    | None = None,
    market_damage_indicator: float = 0.0,
) -> Vdefmd6PreShockSnapshotBatch:
    """Materialize one modern Vdefmd6 VN batch in the shock regime."""

    if (
        type(period) is not int
        or not VDEFMD6_SHOCK_PERIOD <= period <= VDEFMD6_MAX_PERIODS
    ):
        raise ValueError("Vdefmd6 shock snapshot period must be between 50 and 100")
    return _build_vdefmd6_vn_snapshot_batch(
        population,
        period=period,
        rng=rng,
        search_history_by_policyholder=search_history_by_policyholder,
        market_damage_indicator=market_damage_indicator,
        change_shock=True,
    )


def _build_vdefmd6_vn_snapshot_batch(
    population: Vdefmd6Population,
    *,
    period: int,
    rng: random.Random,
    search_history_by_policyholder: Mapping[
        int, list[VNSearchInsuranceHistoryEntry]
    ]
    | None,
    market_damage_indicator: float,
    change_shock: bool,
) -> Vdefmd6PreShockSnapshotBatch:
    if not isinstance(rng, random.Random):
        raise TypeError("Vdefmd6 VN snapshots require an explicit random.Random")
    if market_damage_indicator < 0.0:
        raise ValueError("market_damage_indicator must be non-negative")

    insurer_by_id = {item.entity_id: item for item in population.insurers}
    policyholder_by_id = {item.entity_id: item for item in population.policyholders}
    active_insurer_ids = tuple(
        sorted(item.entity_id for item in population.insurers if item.active)
    )
    if not active_insurer_ids:
        raise ValueError("Vdefmd6 pre-shock snapshots require active insurers")

    active_definitions = tuple(
        item
        for item in population.policyholder_definitions
        if item.activation.activation_period <= period
    )
    missing_policyholders = sorted(
        item.entity_id
        for item in active_definitions
        if item.entity_id not in policyholder_by_id
        or not policyholder_by_id[item.entity_id].active
    )
    if missing_policyholders:
        raise ValueError(
            "Vdefmd6 pre-shock population is missing active policyholders: "
            + ", ".join(str(item) for item in missing_policyholders)
        )

    preference_inputs = [
        VNPreferenceInsurerInput(
            insurer_id=insurer_id,
            advertising_current_sector=list(
                insurer_by_id[insurer_id].advertising_current_sector
            ),
        )
        for insurer_id in active_insurer_ids
    ]
    sample_inputs = [
        VNSampleSearchInsurerInput(
            insurer_id=insurer_id,
            premiums_current_sector=list(insurer_by_id[insurer_id].premiums_current_sector),
        )
        for insurer_id in active_insurer_ids
    ]
    history_by_id = search_history_by_policyholder or {}
    draws = _DrawCounter(rng)
    insurance_snapshots: list[VNInsuranceRuleSnapshot] = []
    damage_snapshots: list[VNDamageSettlementSnapshot] = []

    for definition in active_definitions:
        policyholder = policyholder_by_id[definition.entity_id]
        damage_thresholds = [draws.uniform(), draws.uniform()]
        sector_1_trigger = draws.normal()
        sector_1_amount = draws.normal()
        sector_2_trigger = draws.normal()
        sector_2_amount = draws.normal()
        initial_decisions = _current_decisions(policyholder)
        insurance_snapshots.append(
            _insurance_snapshot(
                definition.entity_id,
                definition.action.rule_id,
                definition.parameters,
                draws=draws,
                active_insurer_ids=active_insurer_ids,
                initial_decisions=initial_decisions,
                damage_thresholds=damage_thresholds,
                preference_inputs=preference_inputs,
                sample_inputs=sample_inputs,
                history=list(history_by_id.get(definition.entity_id, [])),
                market_damage_indicator=market_damage_indicator,
                change_shock=change_shock,
            )
        )
        damage_snapshots.append(
            VNDamageSettlementSnapshot(
                policyholder_id=definition.entity_id,
                parameters=_damage_parameters(definition.parameters),
                damage_thresholds=damage_thresholds,
                previous_wealth=policyholder.end_wealth_current,
                insurance_decisions=None,
                draws=VNDamageRuleDraws(
                    trigger_draws=[sector_1_trigger, sector_2_trigger],
                    amount_draws=[sector_1_amount, sector_2_amount],
                ),
                previous_wealth_sector=(
                    list(policyholder.end_wealth_sector_current)
                    if policyholder.end_wealth_sector_current
                    else None
                ),
                change_shock=change_shock,
            )
        )

    threshold_draw_count = 2 * len(active_definitions)
    return Vdefmd6PreShockSnapshotBatch(
        period=period,
        draw_policy_id=VDEFMD6_PRE_SHOCK_DRAW_POLICY_ID,
        active_insurer_ids=active_insurer_ids,
        change_shock=change_shock,
        insurance_snapshots=tuple(insurance_snapshots),
        damage_snapshots=tuple(damage_snapshots),
        draw_summary=Vdefmd6PreShockDrawSummary(
            uniform_values=draws.uniform_values,
            normal_values=draws.normal_values,
            damage_threshold_uniform_values=threshold_draw_count,
            insurance_uniform_values=draws.uniform_values - threshold_draw_count,
        ),
    )


def _current_decisions(policyholder: Policyholder) -> list[VNInsuranceDecision]:
    insured_values = list(policyholder.insured_current_sector)
    insurer_ids = list(policyholder.chosen_insurer_sector_current)
    if len(insured_values) != 2 or len(insurer_ids) != 2:
        raise ValueError("Vdefmd6 policyholder state requires two sectors")
    decisions: list[VNInsuranceDecision] = []
    for sector_index in range(2):
        insured = bool(insured_values[sector_index])
        insurer_id = insurer_ids[sector_index] if insured else None
        if insured and insurer_id is None:
            raise ValueError("insured Vdefmd6 policyholder state requires insurer_id")
        decisions.append(
            VNInsuranceDecision(
                sector_index=sector_index,
                insured=insured,
                insurer_id=insurer_id,
            )
        )
    return decisions


def _damage_parameters(values: tuple[float, ...]) -> VNDamageRuleParameters:
    return VNDamageRuleParameters(
        damage_intercept_normal=[values[0], values[4]],
        damage_factor_normal=[values[2], values[6]],
        damage_intercept_shock=[values[1], values[5]],
        damage_factor_shock=[values[3], values[7]],
    )


def _insurance_parameters(values: tuple[float, ...]) -> dict[str, list[float] | list[int]]:
    return {
        "insurance_thresholds_normal": [values[8], values[10]],
        "insurance_thresholds_shock": [values[9], values[11]],
        "sample_sizes_normal": [int(values[12]), int(values[14])],
        "sample_sizes_shock": [int(values[13]), int(values[15])],
    }


def _insurance_snapshot(
    policyholder_id: int,
    rule_id: int,
    values: tuple[float, ...],
    *,
    draws: _DrawCounter,
    active_insurer_ids: tuple[int, ...],
    initial_decisions: list[VNInsuranceDecision],
    damage_thresholds: list[float],
    preference_inputs: list[VNPreferenceInsurerInput],
    sample_inputs: list[VNSampleSearchInsurerInput],
    history: list[VNSearchInsuranceHistoryEntry],
    market_damage_indicator: float,
    change_shock: bool,
) -> VNInsuranceRuleSnapshot:
    parameters = _insurance_parameters(values)
    common = {
        "policyholder_id": policyholder_id,
        "rule_kind": _RULE_KINDS[rule_id],
        "active_insurer_ids": list(active_insurer_ids),
        "initial_decisions": initial_decisions,
        "change_shock": change_shock,
    }
    if rule_id == 1:
        return VNInsuranceRuleSnapshot(
            **common,
            draws=VNCompulsoryInsuranceRuleDraws(
                insurer_choice_draws=[draws.uniform(), draws.uniform()]
            ),
        )
    if rule_id == 2:
        return VNInsuranceRuleSnapshot(
            **common,
            parameters=VNRandomInsuranceRuleParameters(
                insurance_thresholds_normal=parameters["insurance_thresholds_normal"],
                insurance_thresholds_shock=parameters["insurance_thresholds_shock"],
            ),
            draws=VNRandomInsuranceRuleDraws(
                status_draws=[draws.uniform(), draws.uniform()],
                insurer_choice_draws=[draws.uniform(), draws.uniform()],
            ),
        )
    if rule_id == 3:
        return VNInsuranceRuleSnapshot(
            **common,
            parameters=VNPreferenceInsuranceRuleParameters(
                insurance_thresholds_normal=parameters["insurance_thresholds_normal"],
                insurance_thresholds_shock=parameters["insurance_thresholds_shock"],
            ),
            draws=VNPreferenceInsuranceRuleDraws(
                fallback_insurer_choice_draws=[draws.uniform(), draws.uniform()]
            ),
            damage_probabilities=list(damage_thresholds),
            insurer_inputs=list(preference_inputs),
        )
    if rule_id == 4:
        return VNInsuranceRuleSnapshot(
            **common,
            parameters=VNSearchInsuranceRuleParameters(
                insurance_thresholds_normal=parameters["insurance_thresholds_normal"],
                insurance_thresholds_shock=parameters["insurance_thresholds_shock"],
            ),
            draws=VNSearchInsuranceRuleDraws(
                fallback_insurer_choice_draws=[draws.uniform(), draws.uniform()]
            ),
            damage_probabilities=list(damage_thresholds),
            history=history,
        )
    if rule_id == 5:
        sample_sizes = (
            parameters["sample_sizes_shock"]
            if change_shock
            else parameters["sample_sizes_normal"]
        )
        return VNInsuranceRuleSnapshot(
            **common,
            parameters=VNSampleSearchInsuranceRuleParameters(
                insurance_thresholds_normal=parameters["insurance_thresholds_normal"],
                insurance_thresholds_shock=parameters["insurance_thresholds_shock"],
                sample_sizes_normal=sample_sizes,
                sample_sizes_shock=parameters["sample_sizes_shock"],
            ),
            draws=VNSampleSearchInsuranceRuleDraws(
                insurer_choice_draws_by_sector=[
                    [draws.uniform() for _ in range(sample_sizes[0])],
                    [draws.uniform() for _ in range(sample_sizes[1])],
                ]
            ),
            market_damage_indicator=market_damage_indicator,
            insurer_inputs=list(sample_inputs),
            information_cost_per_sample=VDEFMD6_INFORMATION_COST,
        )
    if rule_id == 6:
        return VNInsuranceRuleSnapshot(
            **common,
            parameters=VNBestInfoInsuranceRuleParameters(
                insurance_thresholds_normal=parameters["insurance_thresholds_normal"],
                insurance_thresholds_shock=parameters["insurance_thresholds_shock"],
            ),
            market_damage_indicator=market_damage_indicator,
            insurer_inputs=list(sample_inputs),
            information_cost_per_insurer=VDEFMD6_INFORMATION_COST,
        )
    raise ValueError(f"unsupported Vdefmd6 VN rule_id: {rule_id}")
