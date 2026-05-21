from dataclasses import dataclass


@dataclass(slots=True)
class VNDamageRuleParameters:
    """Parameter fuer den gemeinsamen Schadenerzeugungskern aus Vrvn01 bis Vrvn03."""

    damage_intercept_normal: list[float]
    damage_factor_normal: list[float]
    damage_intercept_shock: list[float]
    damage_factor_shock: list[float]


@dataclass(slots=True)
class VNDamageRuleDraws:
    """Explizite Normalziehungen fuer Schadeneintritt und Schadenhoehe."""

    trigger_draws: list[float]
    amount_draws: list[float]


@dataclass(slots=True)
class VNDamageRuleResult:
    """Berechnete Schaeden je Sparte fuer den VN-Schadenerzeugungskern."""

    damages: list[float]
    triggered: list[bool]
    trigger_draws: list[float]
    amount_draws: list[float]


def _two_float_values(values: object, *, fallback: float) -> list[float]:
    if values is None:
        return [float(fallback), float(fallback)]
    if not isinstance(values, list):
        value = float(values)
        return [value, value]
    if not values:
        return [float(fallback), float(fallback)]
    normalized = [float(value) for value in values[:2]]
    if len(normalized) == 1:
        return [normalized[0], normalized[0]]
    return normalized


def _required_two_float_values(mapping: dict[str, object], key: str) -> list[float]:
    value = mapping.get(key)
    if not isinstance(value, list):
        raise ValueError(f"VN damage rule requires list field: {key}")
    return _two_float_values(value, fallback=0.0)


def vn_damage_rule_parameters_from_mapping(mapping: dict[str, object]) -> VNDamageRuleParameters:
    """Laedt den Parameterblock des gemeinsamen VN-Schadenerzeugungskerns."""

    if not isinstance(mapping, dict):
        raise ValueError("VN damage rule parameters must be an object")
    return VNDamageRuleParameters(
        damage_intercept_normal=_required_two_float_values(mapping, "damage_intercept_normal"),
        damage_factor_normal=_required_two_float_values(mapping, "damage_factor_normal"),
        damage_intercept_shock=_required_two_float_values(mapping, "damage_intercept_shock"),
        damage_factor_shock=_required_two_float_values(mapping, "damage_factor_shock"),
    )


def vn_damage_rule_draws_from_mapping(mapping: dict[str, object]) -> VNDamageRuleDraws:
    """Laedt explizite Normalziehungen fuer den VN-Schadenerzeugungskern."""

    if not isinstance(mapping, dict):
        raise ValueError("VN damage rule draws must be an object")
    return VNDamageRuleDraws(
        trigger_draws=_required_two_float_values(mapping, "trigger_draws"),
        amount_draws=_required_two_float_values(mapping, "amount_draws"),
    )


def apply_vn_damage_rule(
    parameters: VNDamageRuleParameters,
    *,
    damage_thresholds: list[float],
    draws: VNDamageRuleDraws,
    change_shock: bool = False,
) -> VNDamageRuleResult:
    """
    Portiert den gemeinsamen Schadenerzeugungskern aus Vrvn01 bis Vrvn03.

    Historische Form je Sparte: `(Sw > normal()) * (a + b * normal())`.
    Die Normalziehungen werden in diesem Slice explizit uebergeben.
    """

    thresholds = _two_float_values(damage_thresholds, fallback=0.0)
    trigger_draws = _two_float_values(draws.trigger_draws, fallback=0.0)
    amount_draws = _two_float_values(draws.amount_draws, fallback=0.0)
    if change_shock:
        intercepts = _two_float_values(parameters.damage_intercept_shock, fallback=0.0)
        factors = _two_float_values(parameters.damage_factor_shock, fallback=0.0)
    else:
        intercepts = _two_float_values(parameters.damage_intercept_normal, fallback=0.0)
        factors = _two_float_values(parameters.damage_factor_normal, fallback=0.0)

    triggered = [thresholds[index] > trigger_draws[index] for index in range(2)]
    damages = [
        intercepts[index] + factors[index] * amount_draws[index]
        if triggered[index]
        else 0.0
        for index in range(2)
    ]
    return VNDamageRuleResult(
        damages=damages,
        triggered=triggered,
        trigger_draws=trigger_draws,
        amount_draws=amount_draws,
    )
