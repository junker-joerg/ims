from dataclasses import dataclass

from ims.model.vn_rules import VNInsuranceDecision


@dataclass(slots=True)
class VNRandomInsuranceRuleParameters:
    """Versicherungsstatus-Schwellen fuer Vrvn02 / Zufall II."""

    insurance_thresholds_normal: list[float]
    insurance_thresholds_shock: list[float]


@dataclass(slots=True)
class VNRandomInsuranceRuleDraws:
    """Explizite Gleichverteilungsziehungen fuer Vrvn02-Status und VU-Auswahl."""

    status_draws: list[float]
    insurer_choice_draws: list[float]


@dataclass(slots=True)
class VNRandomInsuranceRuleResult:
    """Aus Vrvn02 abgeleitete Versicherungsentscheidungen je Sparte."""

    decisions: list[VNInsuranceDecision]
    insured: list[bool]
    chosen_insurer_ids: list[int | None]
    status_draws: list[float]
    insurer_choice_draws: list[float]


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
        raise ValueError(f"VN random insurance rule requires list field: {key}")
    return _two_float_values(value, fallback=0.0)


def _validate_unit_interval(values: list[float], *, field_name: str) -> None:
    for value in values:
        if value < 0.0 or value >= 1.0:
            raise ValueError(f"{field_name} entries must be in [0.0, 1.0)")


def _active_insurer_ids(value: object) -> list[int]:
    if not isinstance(value, list):
        raise ValueError("VN random insurance rule active_insurer_ids must be a list")
    ids = sorted({int(item) for item in value})
    if any(item <= 0 for item in ids):
        raise ValueError("VN random insurance rule active_insurer_ids must be positive")
    return ids


def _choose_insurer(active_insurer_ids: list[int], draw: float) -> int:
    if not active_insurer_ids:
        raise ValueError("VN random insurance rule requires active insurers for insured sectors")
    index = min(int(draw * len(active_insurer_ids)), len(active_insurer_ids) - 1)
    return active_insurer_ids[index]


def vn_random_insurance_rule_parameters_from_mapping(
    mapping: dict[str, object],
) -> VNRandomInsuranceRuleParameters:
    """Laedt den Vrvn02-Schwellenblock fuer zufaelligen VN-Versicherungsstatus."""

    if not isinstance(mapping, dict):
        raise ValueError("VN random insurance rule parameters must be an object")
    return VNRandomInsuranceRuleParameters(
        insurance_thresholds_normal=_required_two_float_values(
            mapping,
            "insurance_thresholds_normal",
        ),
        insurance_thresholds_shock=_required_two_float_values(
            mapping,
            "insurance_thresholds_shock",
        ),
    )


def vn_random_insurance_rule_draws_from_mapping(mapping: dict[str, object]) -> VNRandomInsuranceRuleDraws:
    """Laedt explizite Vrvn02-Gleichverteilungsziehungen."""

    if not isinstance(mapping, dict):
        raise ValueError("VN random insurance rule draws must be an object")
    draws = VNRandomInsuranceRuleDraws(
        status_draws=_required_two_float_values(mapping, "status_draws"),
        insurer_choice_draws=_required_two_float_values(mapping, "insurer_choice_draws"),
    )
    _validate_unit_interval(draws.status_draws, field_name="status_draws")
    _validate_unit_interval(draws.insurer_choice_draws, field_name="insurer_choice_draws")
    return draws


def load_active_insurer_ids_from_mapping(value: object) -> list[int]:
    """Laedt die aktive VU-Auswahlbasis fuer den Vrvn02-Zufallspfad."""

    return _active_insurer_ids(value)


def apply_vn_random_insurance_rule(
    parameters: VNRandomInsuranceRuleParameters,
    *,
    active_insurer_ids: list[int],
    draws: VNRandomInsuranceRuleDraws,
    change_shock: bool = False,
) -> VNRandomInsuranceRuleResult:
    """
    Portiert den Versicherungsstatus- und Zufalls-VU-Auswahlkern aus Vrvn02.

    Historisch gilt je Sparte `vr = threshold <= myrndf()`. Die VU-Auswahl wird
    hier reproduzierbar ueber die sortierte aktive VU-Menge abgebildet; das ist
    keine Behauptung identischer historischer Modulo-RNG-Ziehungen.
    """

    thresholds = _two_float_values(
        parameters.insurance_thresholds_shock if change_shock else parameters.insurance_thresholds_normal,
        fallback=0.0,
    )
    status_draws = _two_float_values(draws.status_draws, fallback=0.0)
    insurer_choice_draws = _two_float_values(draws.insurer_choice_draws, fallback=0.0)
    _validate_unit_interval(status_draws, field_name="status_draws")
    _validate_unit_interval(insurer_choice_draws, field_name="insurer_choice_draws")
    active_ids = _active_insurer_ids(active_insurer_ids)

    decisions: list[VNInsuranceDecision] = []
    insured_values: list[bool] = []
    chosen_insurer_ids: list[int | None] = []
    for sector_index in range(2):
        insured = thresholds[sector_index] <= status_draws[sector_index]
        insurer_id = (
            _choose_insurer(active_ids, insurer_choice_draws[sector_index])
            if insured
            else None
        )
        decisions.append(
            VNInsuranceDecision(
                sector_index=sector_index,
                insured=insured,
                insurer_id=insurer_id,
            )
        )
        insured_values.append(insured)
        chosen_insurer_ids.append(insurer_id)

    return VNRandomInsuranceRuleResult(
        decisions=decisions,
        insured=insured_values,
        chosen_insurer_ids=chosen_insurer_ids,
        status_draws=status_draws,
        insurer_choice_draws=insurer_choice_draws,
    )
