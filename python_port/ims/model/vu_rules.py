from dataclasses import dataclass
from enum import StrEnum

from ims.model.entities import BAV, Insurer


class VUForeignInfoRuleKind(StrEnum):
    """Kleiner Ausschnitt der VU-Regeln, die direkt Frmdinf-Vektoren nutzen."""

    DUMPING = "dumping"
    AVERAGE = "average"
    ATTACK = "attack"


@dataclass(slots=True)
class VUForeignInfoRuleParameters:
    """Parameterpaar je Sparte fuer Normal- und Aenderungsschockfall."""

    premium_intercept_normal: list[float]
    premium_factor_normal: list[float]
    advertising_intercept_normal: list[float]
    advertising_factor_normal: list[float]
    premium_intercept_shock: list[float]
    premium_factor_shock: list[float]
    advertising_intercept_shock: list[float]
    advertising_factor_shock: list[float]


@dataclass(slots=True)
class VUForeignInfoRuleResult:
    """Berechneter VU-Zielzustand fuer den kleinen Fremdinformations-Regelkern."""

    premiums_current_sector: list[float]
    advertising_current_sector: list[float]
    reserves_current: list[float]


def _two_values(values: object, *, fallback: float) -> list[float]:
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


def _foreign_info_vectors(bav: BAV, rule_kind: VUForeignInfoRuleKind) -> tuple[list[float], list[float]]:
    insurer_info = bav.service_state.insurer
    if rule_kind == VUForeignInfoRuleKind.DUMPING:
        return insurer_info.pm, insurer_info.wm
    if rule_kind == VUForeignInfoRuleKind.AVERAGE:
        return insurer_info.dp, insurer_info.dw
    if rule_kind == VUForeignInfoRuleKind.ATTACK:
        return insurer_info.mp, insurer_info.mw
    raise ValueError(f"unsupported VU foreign-info rule kind: {rule_kind}")


def _parameter_values(values: list[float]) -> list[float]:
    return _two_values(values, fallback=0.0)


def apply_vu_foreign_info_rule(
    insurer: Insurer,
    bav: BAV,
    parameters: VUForeignInfoRuleParameters,
    *,
    period: int,
    interest_rate: float,
    rule_kind: VUForeignInfoRuleKind,
    change_shock: bool = False,
) -> VUForeignInfoRuleResult:
    """
    Portiert den gemeinsamen Rechenkern der VU-Regeln Dumping, Durchschnitt und Angriff.

    Der historische Code nutzt fuer diese Regeln dieselbe lineare Zielwertformel und
    unterscheidet nur die Frmdinf-Quelle. Dieser Ausschnitt ist bewusst rein
    deterministisch und haengt noch nicht am Scheduler oder am kompletten VU-Zustandslauf.
    """

    previous_premiums = _two_values(insurer.premiums_current_sector, fallback=insurer.premiums_current)
    previous_advertising = _two_values(insurer.advertising_current_sector, fallback=insurer.advertising_current)
    previous_reserves = _two_values(insurer.reserves_current, fallback=0.0)

    if period <= 1:
        return VUForeignInfoRuleResult(
            premiums_current_sector=previous_premiums,
            advertising_current_sector=previous_advertising,
            reserves_current=[(1.0 + interest_rate) * value for value in previous_reserves],
        )

    premium_info, advertising_info = _foreign_info_vectors(bav, rule_kind)
    if change_shock:
        premium_intercepts = _parameter_values(parameters.premium_intercept_shock)
        premium_factors = _parameter_values(parameters.premium_factor_shock)
        advertising_intercepts = _parameter_values(parameters.advertising_intercept_shock)
        advertising_factors = _parameter_values(parameters.advertising_factor_shock)
    else:
        premium_intercepts = _parameter_values(parameters.premium_intercept_normal)
        premium_factors = _parameter_values(parameters.premium_factor_normal)
        advertising_intercepts = _parameter_values(parameters.advertising_intercept_normal)
        advertising_factors = _parameter_values(parameters.advertising_factor_normal)

    premium_info_values = _two_values(premium_info, fallback=0.0)
    advertising_info_values = _two_values(advertising_info, fallback=0.0)

    return VUForeignInfoRuleResult(
        premiums_current_sector=[
            premium_intercepts[index] + premium_factors[index] * premium_info_values[index]
            for index in range(2)
        ],
        advertising_current_sector=[
            advertising_intercepts[index] + advertising_factors[index] * advertising_info_values[index]
            for index in range(2)
        ],
        reserves_current=[(1.0 + interest_rate) * value for value in previous_reserves],
    )


def apply_vu_foreign_info_rule_to_insurer(
    insurer: Insurer,
    bav: BAV,
    parameters: VUForeignInfoRuleParameters,
    *,
    period: int,
    interest_rate: float,
    rule_kind: VUForeignInfoRuleKind,
    change_shock: bool = False,
) -> VUForeignInfoRuleResult:
    """Berechnet den kleinen Regelkern und schreibt den aktuellen VU-Snapshot fort."""

    result = apply_vu_foreign_info_rule(
        insurer,
        bav,
        parameters,
        period=period,
        interest_rate=interest_rate,
        rule_kind=rule_kind,
        change_shock=change_shock,
    )
    insurer.premiums_current_sector = result.premiums_current_sector
    insurer.advertising_current_sector = result.advertising_current_sector
    insurer.premiums_current = result.premiums_current_sector[0]
    insurer.advertising_current = result.advertising_current_sector[0]
    insurer.reserves_current = result.reserves_current
    return result
