from __future__ import annotations

from dataclasses import dataclass

from ims.model.entities import Insurer, Policyholder


VDEFMD6_INITIAL_PERIOD = 1
VDEFMD6_MAX_PERIODS = 100
VDEFMD6_INSURER_COUNT = 25
VDEFMD6_POLICYHOLDER_COUNT = 200

_VU_RULE_CLASSES = (0, 1, 1, 2, 2, 2, 2, 3, 3, 3)
_VN_RULE_CLASSES = (0, 1, 1, 2, 2, 3, 3)


@dataclass(frozen=True, slots=True)
class LegacyActivationDefinition:
    activation_period: int
    active_through_run: int


@dataclass(frozen=True, slots=True)
class LegacyActionDefinition:
    rule_id: int
    logical_time: int = 1


@dataclass(frozen=True, slots=True)
class Vdefmd6InsurerDefinition:
    entity_id: int
    action: LegacyActionDefinition
    rule_class: int
    activation: LegacyActivationDefinition
    aspiration_sector_1: tuple[float, float, float]
    aspiration_sector_2: tuple[float, float, float]
    initial_premiums: tuple[float, float]
    initial_advertising: tuple[float, float]
    parameters: tuple[float, ...]
    name: str = ""


@dataclass(frozen=True, slots=True)
class Vdefmd6PolicyholderDefinition:
    entity_id: int
    action: LegacyActionDefinition
    rule_class: int
    activation: LegacyActivationDefinition
    initial_insurance_status: tuple[int, int]
    initial_insurer_ids: tuple[int, int]
    initial_wealth: float
    parameters: tuple[float, ...]


@dataclass(slots=True)
class Vdefmd6Population:
    initial_period: int
    insurers: list[Insurer]
    policyholders: list[Policyholder]
    insurer_definitions: tuple[Vdefmd6InsurerDefinition, ...]
    policyholder_definitions: tuple[Vdefmd6PolicyholderDefinition, ...]
    max_periods: int = VDEFMD6_MAX_PERIODS


@dataclass(frozen=True, slots=True)
class _InsurerGroup:
    start: int
    end: int
    rule_id: int
    aspiration_sector_1: tuple[float, float, float]
    aspiration_sector_2: tuple[float, float, float]
    initial_premiums: tuple[float, float]
    initial_advertising: tuple[float, float]
    parameters: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class _PolicyholderGroup:
    start: int
    end: int
    rule_id: int
    activation_period: int
    parameters: tuple[float, ...]


_INSURER_GROUPS = (
    _InsurerGroup(
        1,
        2,
        1,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (40.0, 40.0),
        (0.0, 0.0),
        (60.0, 70.0, 50.0, 40.0, 20.0, 20.0, 20.0, 20.0) + (0.0,) * 8,
    ),
    _InsurerGroup(
        3,
        4,
        2,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (40.0, 40.0),
        (10.0, 10.0),
        (30.0, 40.0, 5.0, 7.0, 30.0, 40.0, 5.0, 8.0)
        + (10.0, 10.0, 0.0, 0.0, 10.0, 10.0, 0.0, 0.0),
    ),
    _InsurerGroup(
        5,
        7,
        3,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (40.0, 40.0),
        (10.0, 10.0),
        (1.03, 1.1, 0.97, 0.9, 1.04, 1.05, 0.97, 0.99)
        + (1.03, 1.1, 0.97, 0.9, 1.08, 1.01, 0.92, 0.99),
    ),
    _InsurerGroup(
        8,
        10,
        4,
        (0.0, 2.0, 0.0),
        (0.2, 0.0, 0.0),
        (40.0, 40.0),
        (10.0, 10.0),
        (1.008, 1.01, 0.99, 0.98, 1.008, 1.01, 0.99, 0.98)
        + (1.008, 1.01, 0.97, 1.0, 1.05, 1.0, 0.95, 1.0),
    ),
    _InsurerGroup(
        11,
        13,
        5,
        (0.0, 0.0, 0.04),
        (0.0, 0.0, 0.04),
        (40.0, 40.0),
        (10.0, 10.0),
        (1.01, 1.02, 0.99, 0.98, 1.008, 1.01, 0.99, 0.98)
        + (1.02, 1.03, 0.98, 1.01, 1.02, 1.03, 0.98, 1.0),
    ),
    _InsurerGroup(
        14,
        14,
        6,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (40.0, 40.0),
        (10.0, 10.0),
        (1.02, 1.03, 0.98, 0.99, 1.02, 1.01, 0.98, 0.99)
        + (1.0, 1.06, 1.03, 1.06, 1.0, 1.06, 1.03, 1.06),
    ),
    _InsurerGroup(
        15,
        16,
        6,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (40.0, 40.0),
        (10.0, 10.0),
        (1.02, 1.03, 0.98, 0.99, 1.02, 1.01, 0.98, 0.99)
        + (1.05, 1.08, 0.95, 0.97, 1.09, 1.06, 0.95, 0.97),
    ),
    _InsurerGroup(
        17,
        19,
        7,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (40.0, 40.0),
        (0.0, 0.0),
        (1.07, 1.04, 1.07, 1.04, 1.07, 1.04, 1.07, 1.04) + (0.0,) * 8,
    ),
    _InsurerGroup(
        20,
        22,
        8,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (40.0, 40.0),
        (10.0, 10.0),
        (0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0) * 2,
    ),
    _InsurerGroup(
        23,
        25,
        9,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (40.0, 40.0),
        (0.0, 0.0),
        (0.0, 0.0, 0.99, 0.95, 0.0, 0.0, 0.99, 0.95) + (0.0,) * 8,
    ),
)

_STANDARD_DAMAGE_PARAMETERS = (30.0, 30.0, 5.0, 5.0) * 2
_LATE_DAMAGE_PARAMETERS = (50.0, 50.0, 15.0, 15.0) * 2

_POLICYHOLDER_GROUPS = (
    _PolicyholderGroup(1, 15, 1, 1, _STANDARD_DAMAGE_PARAMETERS + (0.0,) * 8),
    _PolicyholderGroup(
        16,
        30,
        2,
        1,
        _STANDARD_DAMAGE_PARAMETERS + (0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0),
    ),
    _PolicyholderGroup(
        31,
        60,
        3,
        1,
        _STANDARD_DAMAGE_PARAMETERS + (0.3, 0.3, 0.3, 0.3, 0.0, 0.0, 0.0, 0.0),
    ),
    _PolicyholderGroup(
        61,
        90,
        4,
        1,
        _STANDARD_DAMAGE_PARAMETERS + (0.3, 0.3, 0.3, 0.3, 0.0, 0.0, 0.0, 0.0),
    ),
    _PolicyholderGroup(
        91,
        120,
        5,
        1,
        _STANDARD_DAMAGE_PARAMETERS + (0.3, 0.3, 0.3, 0.3, 8.0, 10.0, 8.0, 10.0),
    ),
    _PolicyholderGroup(
        121,
        150,
        6,
        1,
        _STANDARD_DAMAGE_PARAMETERS + (0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0),
    ),
    _PolicyholderGroup(
        151,
        190,
        3,
        50,
        _LATE_DAMAGE_PARAMETERS + (0.9, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0),
    ),
    _PolicyholderGroup(
        191,
        200,
        2,
        50,
        _LATE_DAMAGE_PARAMETERS + (0.9, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0),
    ),
)


def build_vdefmd6_population() -> Vdefmd6Population:
    """Build the source-bound Vdefmd6 entities at the start of period one."""

    return _build_vdefmd6_population(max_periods=VDEFMD6_MAX_PERIODS)


def build_vdefmd6_population_for_horizon(
    *,
    max_periods: int,
) -> Vdefmd6Population:
    """Build the same source population with an explicit modern run horizon."""

    if type(max_periods) is not int or max_periods < VDEFMD6_MAX_PERIODS:
        raise ValueError("Vdefmd6 max_periods must be an integer of at least 100")
    return _build_vdefmd6_population(max_periods=max_periods)


def _build_vdefmd6_population(*, max_periods: int) -> Vdefmd6Population:

    insurer_definitions = tuple(
        _expand_insurer_group(group, max_periods=max_periods)
        for group in _INSURER_GROUPS
    )
    insurer_definitions = tuple(item for group in insurer_definitions for item in group)
    policyholder_definitions = tuple(
        _expand_policyholder_group(group, max_periods=max_periods)
        for group in _POLICYHOLDER_GROUPS
    )
    policyholder_definitions = tuple(
        item for group in policyholder_definitions for item in group
    )
    return Vdefmd6Population(
        initial_period=VDEFMD6_INITIAL_PERIOD,
        insurers=[_build_insurer(item) for item in insurer_definitions],
        policyholders=[_build_policyholder(item) for item in policyholder_definitions],
        insurer_definitions=insurer_definitions,
        policyholder_definitions=policyholder_definitions,
        max_periods=max_periods,
    )


def _expand_insurer_group(
    group: _InsurerGroup,
    *,
    max_periods: int,
) -> tuple[Vdefmd6InsurerDefinition, ...]:
    return tuple(
        Vdefmd6InsurerDefinition(
            entity_id=entity_id,
            name="Allianz" if entity_id == 14 else "",
            action=LegacyActionDefinition(rule_id=group.rule_id),
            rule_class=_VU_RULE_CLASSES[group.rule_id],
            activation=LegacyActivationDefinition(1, max_periods),
            aspiration_sector_1=group.aspiration_sector_1,
            aspiration_sector_2=group.aspiration_sector_2,
            initial_premiums=group.initial_premiums,
            initial_advertising=group.initial_advertising,
            parameters=group.parameters,
        )
        for entity_id in range(group.start, group.end + 1)
    )


def _expand_policyholder_group(
    group: _PolicyholderGroup,
    *,
    max_periods: int,
) -> tuple[Vdefmd6PolicyholderDefinition, ...]:
    return tuple(
        Vdefmd6PolicyholderDefinition(
            entity_id=entity_id,
            action=LegacyActionDefinition(rule_id=group.rule_id),
            rule_class=_VN_RULE_CLASSES[group.rule_id],
            activation=LegacyActivationDefinition(
                group.activation_period,
                max_periods,
            ),
            initial_insurance_status=(0, 0),
            initial_insurer_ids=(0, 0),
            initial_wealth=0.0,
            parameters=group.parameters,
        )
        for entity_id in range(group.start, group.end + 1)
    )


def _build_insurer(definition: Vdefmd6InsurerDefinition) -> Insurer:
    active = definition.activation.activation_period <= VDEFMD6_INITIAL_PERIOD
    return Insurer(
        entity_id=definition.entity_id,
        active=active,
        active_prev=False,
        name=definition.name,
        rule_id=definition.action.rule_id,
        rule_class=definition.rule_class,
        premiums_current=definition.initial_premiums[0],
        advertising_current=definition.initial_advertising[0],
        premiums_current_sector=list(definition.initial_premiums),
        advertising_current_sector=list(definition.initial_advertising),
        policyholders_current_sector=[0.0, 0.0],
    )


def _build_policyholder(definition: Vdefmd6PolicyholderDefinition) -> Policyholder:
    active = definition.activation.activation_period <= VDEFMD6_INITIAL_PERIOD
    chosen_insurers = [
        insurer_id if insurer_id > 0 else None
        for insurer_id in definition.initial_insurer_ids
    ]
    insured = [float(status) for status in definition.initial_insurance_status]
    return Policyholder(
        entity_id=definition.entity_id,
        active=active,
        active_prev=False,
        name=f"VN[{definition.entity_id:03d}]",
        insurer_id=chosen_insurers[0],
        rule_id=definition.action.rule_id,
        rule_class=definition.rule_class,
        insured_current=insured[0],
        insured_current_sector=insured,
        chosen_insurer_current=chosen_insurers[0],
        chosen_insurer_sector_current=chosen_insurers,
        end_wealth_current=definition.initial_wealth,
    )
