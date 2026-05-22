from dataclasses import dataclass

from ims.model.vn_rules import VNInsuranceDecision, load_vn_insurance_decisions_from_mapping


@dataclass(slots=True)
class VNCompulsoryInsuranceRuleDraws:
    """Explizite Gleichverteilungsziehungen fuer Vrvn01-VU-Auswahl."""

    insurer_choice_draws: list[float]


@dataclass(slots=True)
class VNCompulsoryInsuranceRuleResult:
    """Aus Vrvn01 abgeleitete Pflichtversicherungsentscheidungen je Sparte."""

    decisions: list[VNInsuranceDecision]
    selected_insurer_ids: list[int | None]
    insurer_choice_draws: list[float] | None = None


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
    selected_insurer_ids: list[int]
    status_draws: list[float]
    insurer_choice_draws: list[float]


@dataclass(slots=True)
class VNPreferenceInsuranceRuleParameters:
    """Versicherungsstatus-Schwellen fuer Vrvn03 / Praeferenz."""

    insurance_thresholds_normal: list[float]
    insurance_thresholds_shock: list[float]


@dataclass(slots=True)
class VNPreferenceInsuranceRuleDraws:
    """Explizite Gleichverteilungsziehungen fuer Vrvn03-Fallbackauswahl."""

    fallback_insurer_choice_draws: list[float]


@dataclass(slots=True)
class VNPreferenceInsurerInput:
    """Aktiver VU-Werbeblock fuer die Vrvn03-Praeferenzwahl."""

    insurer_id: int
    advertising_current_sector: list[float]


@dataclass(slots=True)
class VNPreferenceInsuranceRuleResult:
    """Aus Vrvn03 abgeleitete Versicherungsentscheidungen je Sparte."""

    decisions: list[VNInsuranceDecision]
    insured: list[bool]
    chosen_insurer_ids: list[int | None]
    selected_insurer_ids: list[int | None]
    preference_scores: list[dict[int, float]]
    used_fallback: list[bool]
    fallback_insurer_choice_draws: list[float] | None = None


@dataclass(slots=True)
class VNSearchInsuranceRuleParameters:
    """Versicherungsstatus-Schwellen fuer Vrvn04 / Suche."""

    insurance_thresholds_normal: list[float]
    insurance_thresholds_shock: list[float]


@dataclass(slots=True)
class VNSearchInsuranceRuleDraws:
    """Explizite Gleichverteilungsziehungen fuer Vrvn04-Fallbackauswahl."""

    fallback_insurer_choice_draws: list[float]


@dataclass(slots=True)
class VNSearchInsuranceHistoryEntry:
    """Historische VN-Versicherungsentscheidung fuer die Vrvn04-Suche."""

    period: int
    sector_index: int
    insured: bool
    premium: float
    insurer_id: int | None = None


@dataclass(slots=True)
class VNSearchInsuranceRuleResult:
    """Aus Vrvn04 abgeleitete Versicherungsentscheidungen je Sparte."""

    decisions: list[VNInsuranceDecision]
    insured: list[bool]
    chosen_insurer_ids: list[int | None]
    selected_insurer_ids: list[int | None]
    selected_history_periods: list[int | None]
    used_fallback: list[bool]
    fallback_insurer_choice_draws: list[float] | None = None


@dataclass(slots=True)
class VNSampleSearchInsuranceRuleParameters:
    """Versicherungsstatus- und Stichprobengroessen fuer Vrvn05 / Suche."""

    insurance_thresholds_normal: list[float]
    insurance_thresholds_shock: list[float]
    sample_sizes_normal: list[int]
    sample_sizes_shock: list[int]


@dataclass(slots=True)
class VNSampleSearchInsuranceRuleDraws:
    """Explizite Gleichverteilungsziehungen fuer die Vrvn05-Stichprobensuche."""

    insurer_choice_draws_by_sector: list[list[float]]


@dataclass(slots=True)
class VNSampleSearchInsurerInput:
    """Aktiver VU-Praemienblock fuer die Vrvn05-Stichprobensuche."""

    insurer_id: int
    premiums_current_sector: list[float]


@dataclass(slots=True)
class VNSampleSearchInsuranceRuleResult:
    """Aus Vrvn05 abgeleitete Versicherungsentscheidungen je Sparte."""

    decisions: list[VNInsuranceDecision]
    insured: list[bool]
    chosen_insurer_ids: list[int | None]
    selected_insurer_ids: list[int | None]
    selected_premiums: list[float | None]
    sampled_insurer_ids: list[list[int]]
    used_insurer_choice_draws_by_sector: list[list[float]]
    information_cost: float


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


def _required_two_float_values(
    mapping: dict[str, object],
    key: str,
    *,
    rule_name: str = "VN random insurance rule",
) -> list[float]:
    value = mapping.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{rule_name} requires list field: {key}")
    return _two_float_values(value, fallback=0.0)


def _two_int_values(values: object, *, fallback: int) -> list[int]:
    if values is None:
        return [int(fallback), int(fallback)]
    if not isinstance(values, list):
        value = int(values)
        return [value, value]
    if not values:
        return [int(fallback), int(fallback)]
    normalized = [int(value) for value in values[:2]]
    if len(normalized) == 1:
        return [normalized[0], normalized[0]]
    return normalized


def _required_two_int_values(
    mapping: dict[str, object],
    key: str,
    *,
    rule_name: str,
) -> list[int]:
    value = mapping.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{rule_name} requires list field: {key}")
    return _two_int_values(value, fallback=0)


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
        raise ValueError("VN random insurance rule requires active insurers for insurer selection")
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


def vn_preference_insurance_rule_parameters_from_mapping(
    mapping: dict[str, object],
) -> VNPreferenceInsuranceRuleParameters:
    """Laedt den Vrvn03-Schwellenblock fuer Praeferenzentscheidungen."""

    if not isinstance(mapping, dict):
        raise ValueError("VN preference insurance rule parameters must be an object")
    return VNPreferenceInsuranceRuleParameters(
        insurance_thresholds_normal=_required_two_float_values(
            mapping,
            "insurance_thresholds_normal",
        ),
        insurance_thresholds_shock=_required_two_float_values(
            mapping,
            "insurance_thresholds_shock",
        ),
    )


def vn_search_insurance_rule_parameters_from_mapping(
    mapping: dict[str, object],
) -> VNSearchInsuranceRuleParameters:
    """Laedt den Vrvn04-Schwellenblock fuer Suchentscheidungen."""

    if not isinstance(mapping, dict):
        raise ValueError("VN search insurance rule parameters must be an object")
    return VNSearchInsuranceRuleParameters(
        insurance_thresholds_normal=_required_two_float_values(
            mapping,
            "insurance_thresholds_normal",
            rule_name="VN search insurance rule",
        ),
        insurance_thresholds_shock=_required_two_float_values(
            mapping,
            "insurance_thresholds_shock",
            rule_name="VN search insurance rule",
        ),
    )


def vn_sample_search_insurance_rule_parameters_from_mapping(
    mapping: dict[str, object],
) -> VNSampleSearchInsuranceRuleParameters:
    """Laedt den Vrvn05-Schwellen- und Stichprobenblock."""

    if not isinstance(mapping, dict):
        raise ValueError("VN sample search insurance rule parameters must be an object")
    parameters = VNSampleSearchInsuranceRuleParameters(
        insurance_thresholds_normal=_required_two_float_values(
            mapping,
            "insurance_thresholds_normal",
            rule_name="VN sample search insurance rule",
        ),
        insurance_thresholds_shock=_required_two_float_values(
            mapping,
            "insurance_thresholds_shock",
            rule_name="VN sample search insurance rule",
        ),
        sample_sizes_normal=_required_two_int_values(
            mapping,
            "sample_sizes_normal",
            rule_name="VN sample search insurance rule",
        ),
        sample_sizes_shock=_required_two_int_values(
            mapping,
            "sample_sizes_shock",
            rule_name="VN sample search insurance rule",
        ),
    )
    if any(value < 0 for value in parameters.sample_sizes_normal + parameters.sample_sizes_shock):
        raise ValueError("VN sample search insurance rule sample sizes must be non-negative")
    return parameters


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


def vn_preference_insurance_rule_draws_from_mapping(mapping: dict[str, object]) -> VNPreferenceInsuranceRuleDraws:
    """Laedt explizite Vrvn03-Gleichverteilungsziehungen fuer die Fallbackauswahl."""

    if not isinstance(mapping, dict):
        raise ValueError("VN preference insurance rule draws must be an object")
    draws = VNPreferenceInsuranceRuleDraws(
        fallback_insurer_choice_draws=_required_two_float_values(mapping, "fallback_insurer_choice_draws"),
    )
    _validate_unit_interval(draws.fallback_insurer_choice_draws, field_name="fallback_insurer_choice_draws")
    return draws


def vn_search_insurance_rule_draws_from_mapping(mapping: dict[str, object]) -> VNSearchInsuranceRuleDraws:
    """Laedt explizite Vrvn04-Gleichverteilungsziehungen fuer die Fallbackauswahl."""

    if not isinstance(mapping, dict):
        raise ValueError("VN search insurance rule draws must be an object")
    draws = VNSearchInsuranceRuleDraws(
        fallback_insurer_choice_draws=_required_two_float_values(
            mapping,
            "fallback_insurer_choice_draws",
            rule_name="VN search insurance rule",
        ),
    )
    _validate_unit_interval(draws.fallback_insurer_choice_draws, field_name="fallback_insurer_choice_draws")
    return draws


def vn_sample_search_insurance_rule_draws_from_mapping(
    mapping: dict[str, object],
) -> VNSampleSearchInsuranceRuleDraws:
    """Laedt explizite Vrvn05-Gleichverteilungsziehungen fuer Stichproben."""

    if not isinstance(mapping, dict):
        raise ValueError("VN sample search insurance rule draws must be an object")
    value = mapping.get("insurer_choice_draws_by_sector")
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("VN sample search insurance rule requires two draw lists")
    draw_lists: list[list[float]] = []
    for sector_index, item in enumerate(value):
        if not isinstance(item, list):
            raise ValueError("VN sample search insurance rule draw sectors must be lists")
        draws = [float(draw) for draw in item]
        _validate_unit_interval(draws, field_name=f"insurer_choice_draws_by_sector[{sector_index}]")
        draw_lists.append(draws)
    return VNSampleSearchInsuranceRuleDraws(
        insurer_choice_draws_by_sector=draw_lists,
    )


def vn_compulsory_insurance_rule_draws_from_mapping(mapping: dict[str, object]) -> VNCompulsoryInsuranceRuleDraws:
    """Laedt explizite Vrvn01-Gleichverteilungsziehungen fuer die VU-Auswahl."""

    if not isinstance(mapping, dict):
        raise ValueError("VN compulsory insurance rule draws must be an object")
    draws = VNCompulsoryInsuranceRuleDraws(
        insurer_choice_draws=_required_two_float_values(mapping, "insurer_choice_draws"),
    )
    _validate_unit_interval(draws.insurer_choice_draws, field_name="insurer_choice_draws")
    return draws


def load_active_insurer_ids_from_mapping(value: object) -> list[int]:
    """Laedt die aktive VU-Auswahlbasis fuer den Vrvn02-Zufallspfad."""

    return _active_insurer_ids(value)


def vn_preference_insurer_input_from_mapping(mapping: dict[str, object]) -> VNPreferenceInsurerInput:
    """Laedt einen aktiven VU-Werbeblock fuer die Vrvn03-Praeferenzwahl."""

    if not isinstance(mapping, dict):
        raise ValueError("VN preference insurer input must be an object")
    if "insurer_id" not in mapping:
        raise ValueError("VN preference insurer input requires field: insurer_id")
    insurer_id = int(mapping["insurer_id"])
    if insurer_id <= 0:
        raise ValueError("VN preference insurer input insurer_id must be positive")
    advertising = _two_float_values(mapping.get("advertising_current_sector"), fallback=0.0)
    if any(value < 0.0 for value in advertising):
        raise ValueError("VN preference insurer input advertising must be non-negative")
    return VNPreferenceInsurerInput(
        insurer_id=insurer_id,
        advertising_current_sector=advertising,
    )


def _normalize_preference_insurer_input(value: object) -> VNPreferenceInsurerInput:
    if not isinstance(value, VNPreferenceInsurerInput):
        return vn_preference_insurer_input_from_mapping(value)
    insurer_id = int(value.insurer_id)
    if insurer_id <= 0:
        raise ValueError("VN preference insurer input insurer_id must be positive")
    advertising = _two_float_values(value.advertising_current_sector, fallback=0.0)
    if any(item < 0.0 for item in advertising):
        raise ValueError("VN preference insurer input advertising must be non-negative")
    return VNPreferenceInsurerInput(
        insurer_id=insurer_id,
        advertising_current_sector=advertising,
    )


def load_vn_preference_insurer_inputs_from_mapping(value: object) -> list[VNPreferenceInsurerInput]:
    """Laedt aktive VU-Werbebloecke fuer Vrvn03 aus In-Memory-Daten."""

    if not isinstance(value, list):
        raise ValueError("VN preference insurer inputs must be a list")
    inputs = [_normalize_preference_insurer_input(item) for item in value]
    insurer_ids = [item.insurer_id for item in inputs]
    duplicate_ids = sorted(insurer_id for insurer_id in set(insurer_ids) if insurer_ids.count(insurer_id) > 1)
    if duplicate_ids:
        values = ", ".join(str(insurer_id) for insurer_id in duplicate_ids)
        raise ValueError(f"VN preference insurer inputs reject duplicate insurer_ids: {values}")
    return sorted(inputs, key=lambda item: item.insurer_id)


def vn_search_insurance_history_entry_from_mapping(mapping: dict[str, object]) -> VNSearchInsuranceHistoryEntry:
    """Laedt einen historischen VN-Versicherungsstand fuer die Vrvn04-Suche."""

    if not isinstance(mapping, dict):
        raise ValueError("VN search insurance history entry must be an object")
    for key in ("period", "sector_index", "insured", "premium"):
        if key not in mapping:
            raise ValueError(f"VN search insurance history entry requires field: {key}")
    period = int(mapping["period"])
    if period < 1:
        raise ValueError("VN search insurance history period must be at least 1")
    sector_index = int(mapping["sector_index"])
    if sector_index not in (0, 1):
        raise ValueError(f"VN search insurance history has unsupported sector_index: {sector_index}")
    if not isinstance(mapping["insured"], bool):
        raise ValueError("VN search insurance history insured must be a boolean")
    insured = mapping["insured"]
    premium = float(mapping["premium"])
    if premium < 0.0:
        raise ValueError("VN search insurance history premium must be non-negative")
    insurer_id = None if mapping.get("insurer_id") is None else int(mapping["insurer_id"])
    if insured and insurer_id is None:
        raise ValueError("insured VN search insurance history requires insurer_id")
    if not insured and insurer_id is not None:
        raise ValueError("uninsured VN search insurance history must not reference insurer_id")
    if insurer_id is not None and insurer_id <= 0:
        raise ValueError("VN search insurance history insurer_id must be positive")
    return VNSearchInsuranceHistoryEntry(
        period=period,
        sector_index=sector_index,
        insured=insured,
        premium=premium,
        insurer_id=insurer_id,
    )


def load_vn_search_insurance_history_from_mapping(value: object) -> list[VNSearchInsuranceHistoryEntry]:
    """Laedt historische VN-Versicherungsstaende fuer Vrvn04 aus In-Memory-Daten."""

    if not isinstance(value, list):
        raise ValueError("VN search insurance history must be a list")
    history = [
        item if isinstance(item, VNSearchInsuranceHistoryEntry) else vn_search_insurance_history_entry_from_mapping(item)
        for item in value
    ]
    normalized: list[VNSearchInsuranceHistoryEntry] = []
    keys: set[tuple[int, int]] = set()
    for item in history:
        period = int(item.period)
        if period < 1:
            raise ValueError("VN search insurance history period must be at least 1")
        sector_index = int(item.sector_index)
        if sector_index not in (0, 1):
            raise ValueError(f"VN search insurance history has unsupported sector_index: {sector_index}")
        if not isinstance(item.insured, bool):
            raise ValueError("VN search insurance history insured must be a boolean")
        insured = item.insured
        premium = float(item.premium)
        if premium < 0.0:
            raise ValueError("VN search insurance history premium must be non-negative")
        insurer_id = None if item.insurer_id is None else int(item.insurer_id)
        if insured and insurer_id is None:
            raise ValueError("insured VN search insurance history requires insurer_id")
        if not insured and insurer_id is not None:
            raise ValueError("uninsured VN search insurance history must not reference insurer_id")
        if insurer_id is not None and insurer_id <= 0:
            raise ValueError("VN search insurance history insurer_id must be positive")
        key = (period, sector_index)
        if key in keys:
            raise ValueError("VN search insurance history rejects duplicate period/sector entries")
        keys.add(key)
        normalized.append(
            VNSearchInsuranceHistoryEntry(
                period=period,
                sector_index=sector_index,
                insured=insured,
                premium=premium,
                insurer_id=insurer_id,
            )
        )
    return sorted(normalized, key=lambda item: (item.period, item.sector_index))


def vn_sample_search_insurer_input_from_mapping(mapping: dict[str, object]) -> VNSampleSearchInsurerInput:
    """Laedt einen aktiven VU-Praemienblock fuer die Vrvn05-Stichprobe."""

    if not isinstance(mapping, dict):
        raise ValueError("VN sample search insurer input must be an object")
    if "insurer_id" not in mapping:
        raise ValueError("VN sample search insurer input requires field: insurer_id")
    insurer_id = int(mapping["insurer_id"])
    if insurer_id <= 0:
        raise ValueError("VN sample search insurer input insurer_id must be positive")
    premiums = _two_float_values(mapping.get("premiums_current_sector"), fallback=0.0)
    if any(value < 0.0 for value in premiums):
        raise ValueError("VN sample search insurer input premiums must be non-negative")
    return VNSampleSearchInsurerInput(
        insurer_id=insurer_id,
        premiums_current_sector=premiums,
    )


def _normalize_sample_search_insurer_input(value: object) -> VNSampleSearchInsurerInput:
    if not isinstance(value, VNSampleSearchInsurerInput):
        return vn_sample_search_insurer_input_from_mapping(value)
    insurer_id = int(value.insurer_id)
    if insurer_id <= 0:
        raise ValueError("VN sample search insurer input insurer_id must be positive")
    premiums = _two_float_values(value.premiums_current_sector, fallback=0.0)
    if any(item < 0.0 for item in premiums):
        raise ValueError("VN sample search insurer input premiums must be non-negative")
    return VNSampleSearchInsurerInput(
        insurer_id=insurer_id,
        premiums_current_sector=premiums,
    )


def load_vn_sample_search_insurer_inputs_from_mapping(value: object) -> list[VNSampleSearchInsurerInput]:
    """Laedt aktive VU-Praemienbloecke fuer Vrvn05 aus In-Memory-Daten."""

    if not isinstance(value, list):
        raise ValueError("VN sample search insurer inputs must be a list")
    inputs = [_normalize_sample_search_insurer_input(item) for item in value]
    insurer_ids = [item.insurer_id for item in inputs]
    duplicate_ids = sorted(insurer_id for insurer_id in set(insurer_ids) if insurer_ids.count(insurer_id) > 1)
    if duplicate_ids:
        values = ", ".join(str(insurer_id) for insurer_id in duplicate_ids)
        raise ValueError(f"VN sample search insurer inputs reject duplicate insurer_ids: {values}")
    return sorted(inputs, key=lambda item: item.insurer_id)


def _preference_scores_for_sector(
    insurer_inputs: list[VNPreferenceInsurerInput],
    sector_index: int,
) -> dict[int, float]:
    total_advertising = sum(
        insurer_input.advertising_current_sector[sector_index]
        for insurer_input in insurer_inputs
    )
    if total_advertising <= 0.0:
        return {insurer_input.insurer_id: 0.0 for insurer_input in insurer_inputs}
    return {
        insurer_input.insurer_id: insurer_input.advertising_current_sector[sector_index] / total_advertising
        for insurer_input in insurer_inputs
    }


def _select_preferred_insurer(
    *,
    insurer_inputs: list[VNPreferenceInsurerInput],
    sector_index: int,
    fallback_draw: float | None,
) -> tuple[int, dict[int, float], bool]:
    if not insurer_inputs:
        raise ValueError("VN preference insurance rule requires active insurer inputs")
    scores = _preference_scores_for_sector(insurer_inputs, sector_index)
    selected_id = 0
    selected_score = 0.0
    for insurer_id in sorted(scores):
        score = scores[insurer_id]
        if score > selected_score:
            selected_id = insurer_id
            selected_score = score
    if selected_id != 0:
        return selected_id, scores, False
    if fallback_draw is None:
        raise ValueError("VN preference insurance rule requires fallback draws when no active advertising exists")
    return _choose_insurer([item.insurer_id for item in insurer_inputs], fallback_draw), scores, True


def _select_searched_insurer(
    *,
    history: list[VNSearchInsuranceHistoryEntry],
    sector_index: int,
    active_insurer_ids: list[int],
    fallback_draw: float | None,
    period: int,
) -> tuple[int, int | None, bool]:
    selected_history: VNSearchInsuranceHistoryEntry | None = None
    for item in history:
        if item.period >= period or item.sector_index != sector_index or not item.insured:
            continue
        if selected_history is None or item.premium < selected_history.premium:
            selected_history = item
    if selected_history is not None and selected_history.insurer_id is not None:
        return selected_history.insurer_id, selected_history.period, False
    if fallback_draw is None:
        raise ValueError("VN search insurance rule requires fallback draws when no prior insured period exists")
    return _choose_insurer(active_insurer_ids, fallback_draw), None, True


def _draw_lists_by_sector(value: list[list[float]], *, sample_sizes: list[int]) -> list[list[float]]:
    if len(value) != 2:
        raise ValueError("VN sample search insurance rule requires two draw lists")
    normalized: list[list[float]] = []
    for sector_index, item in enumerate(value):
        if not isinstance(item, list):
            raise ValueError("VN sample search insurance rule draw sectors must be lists")
        draws = [float(draw) for draw in item]
        _validate_unit_interval(draws, field_name=f"insurer_choice_draws_by_sector[{sector_index}]")
        if len(draws) < sample_sizes[sector_index]:
            raise ValueError("VN sample search insurance rule requires enough insurer choice draws")
        normalized.append(draws[: sample_sizes[sector_index]])
    return normalized


def _select_sampled_insurer(
    *,
    insurer_inputs: list[VNSampleSearchInsurerInput],
    sector_index: int,
    draws: list[float],
) -> tuple[int, float, list[int]]:
    if not insurer_inputs:
        raise ValueError("VN sample search insurance rule requires active insurer inputs")
    ids = [item.insurer_id for item in insurer_inputs]
    by_id = {item.insurer_id: item for item in insurer_inputs}
    sampled_ids: list[int] = []
    sampled_premiums: dict[int, float] = {}
    for draw in draws:
        insurer_id = _choose_insurer(ids, draw)
        sampled_ids.append(insurer_id)
        sampled_premiums[insurer_id] = by_id[insurer_id].premiums_current_sector[sector_index]
    selected_id = 0
    selected_premium = 1000.0
    for insurer_id in ids:
        premium = sampled_premiums.get(insurer_id)
        if premium is not None and premium < selected_premium:
            selected_id = insurer_id
            selected_premium = premium
    if selected_id == 0:
        raise ValueError("VN sample search insurance rule sample size must be positive")
    return selected_id, selected_premium, sampled_ids


def apply_vn_compulsory_insurance_rule(
    *,
    period: int,
    active_insurer_ids: list[int],
    draws: VNCompulsoryInsuranceRuleDraws | None = None,
    initial_decisions: object = None,
) -> VNCompulsoryInsuranceRuleResult:
    """
    Portiert den Versicherungsentscheidungsanteil aus Vrvn01.

    In Periode 1 verwendet der Altcode die initialen VN-Status-/VU-Werte. Ab
    Periode 2 sind beide Sparten pflichtversichert und waehlen je einen aktiven
    Versicherer. Die Auswahl nutzt hier explizite Draws; historische
    Modulo-RNG-Gleichheit wird nicht behauptet.
    """

    if period < 1:
        raise ValueError("VN compulsory insurance rule period must be at least 1")
    if period == 1:
        if initial_decisions is None:
            raise ValueError("VN compulsory insurance rule period 1 requires initial_decisions")
        decisions = sorted(
            load_vn_insurance_decisions_from_mapping(initial_decisions),
            key=lambda item: item.sector_index,
        )
        selected_insurer_ids = [decision.insurer_id for decision in decisions]
        return VNCompulsoryInsuranceRuleResult(
            decisions=decisions,
            selected_insurer_ids=selected_insurer_ids,
        )

    if draws is None:
        raise ValueError("VN compulsory insurance rule periods after 1 require insurer choice draws")
    insurer_choice_draws = _two_float_values(draws.insurer_choice_draws, fallback=0.0)
    _validate_unit_interval(insurer_choice_draws, field_name="insurer_choice_draws")
    active_ids = _active_insurer_ids(active_insurer_ids)
    selected_insurer_ids = [
        _choose_insurer(active_ids, insurer_choice_draws[sector_index])
        for sector_index in range(2)
    ]
    return VNCompulsoryInsuranceRuleResult(
        decisions=[
            VNInsuranceDecision(
                sector_index=sector_index,
                insured=True,
                insurer_id=selected_insurer_ids[sector_index],
            )
            for sector_index in range(2)
        ],
        selected_insurer_ids=selected_insurer_ids,
        insurer_choice_draws=insurer_choice_draws,
    )


def apply_vn_preference_insurance_rule(
    parameters: VNPreferenceInsuranceRuleParameters,
    *,
    period: int,
    damage_probabilities: list[float],
    insurer_inputs: object,
    draws: VNPreferenceInsuranceRuleDraws | None = None,
    initial_decisions: object = None,
    change_shock: bool = False,
) -> VNPreferenceInsuranceRuleResult:
    """
    Portiert den Versicherungsentscheidungsanteil aus Vrvn03.

    In Periode 1 verwendet der Altcode die initialen VN-Status-/VU-Werte. Ab
    Periode 2 folgt der Status aus subjektiven Schadenwahrscheinlichkeiten;
    die VU-Auswahl nimmt den aktiven Versicherer mit maximalem relativen
    Werbeanteil je Sparte und faellt nur bei Null-Werbung auf Zufall zurueck.
    """

    if period < 1:
        raise ValueError("VN preference insurance rule period must be at least 1")
    if period == 1:
        if initial_decisions is None:
            raise ValueError("VN preference insurance rule period 1 requires initial_decisions")
        decisions = sorted(
            load_vn_insurance_decisions_from_mapping(initial_decisions),
            key=lambda item: item.sector_index,
        )
        selected_insurer_ids = [decision.insurer_id for decision in decisions]
        return VNPreferenceInsuranceRuleResult(
            decisions=decisions,
            insured=[decision.insured for decision in decisions],
            chosen_insurer_ids=selected_insurer_ids,
            selected_insurer_ids=selected_insurer_ids,
            preference_scores=[{}, {}],
            used_fallback=[False, False],
        )

    thresholds = _two_float_values(
        parameters.insurance_thresholds_shock if change_shock else parameters.insurance_thresholds_normal,
        fallback=0.0,
    )
    probabilities = _two_float_values(damage_probabilities, fallback=0.0)
    if any(value < 0.0 for value in probabilities):
        raise ValueError("VN preference insurance rule damage probabilities must be non-negative")
    active_inputs = load_vn_preference_insurer_inputs_from_mapping(insurer_inputs)
    fallback_draws = (
        _two_float_values(draws.fallback_insurer_choice_draws, fallback=0.0)
        if draws is not None
        else None
    )
    if fallback_draws is not None:
        _validate_unit_interval(fallback_draws, field_name="fallback_insurer_choice_draws")

    decisions: list[VNInsuranceDecision] = []
    insured_values: list[bool] = []
    chosen_insurer_ids: list[int | None] = []
    selected_insurer_ids: list[int | None] = []
    preference_scores: list[dict[int, float]] = []
    used_fallback: list[bool] = []
    for sector_index in range(2):
        selected_id, scores, fallback_used = _select_preferred_insurer(
            insurer_inputs=active_inputs,
            sector_index=sector_index,
            fallback_draw=(fallback_draws[sector_index] if fallback_draws is not None else None),
        )
        insured = probabilities[sector_index] > thresholds[sector_index]
        insurer_id = selected_id if insured else None
        decisions.append(
            VNInsuranceDecision(
                sector_index=sector_index,
                insured=insured,
                insurer_id=insurer_id,
            )
        )
        insured_values.append(insured)
        chosen_insurer_ids.append(insurer_id)
        selected_insurer_ids.append(selected_id)
        preference_scores.append(scores)
        used_fallback.append(fallback_used)

    return VNPreferenceInsuranceRuleResult(
        decisions=decisions,
        insured=insured_values,
        chosen_insurer_ids=chosen_insurer_ids,
        selected_insurer_ids=selected_insurer_ids,
        preference_scores=preference_scores,
        used_fallback=used_fallback,
        fallback_insurer_choice_draws=fallback_draws,
    )


def apply_vn_search_insurance_rule(
    parameters: VNSearchInsuranceRuleParameters,
    *,
    period: int,
    damage_probabilities: list[float],
    history: object,
    active_insurer_ids: list[int],
    draws: VNSearchInsuranceRuleDraws | None = None,
    initial_decisions: object = None,
    change_shock: bool = False,
) -> VNSearchInsuranceRuleResult:
    """
    Portiert den Versicherungsentscheidungsanteil aus Vrvn04.

    In Periode 1 verwendet der Altcode die initialen VN-Status-/VU-Werte. Ab
    Periode 2 folgt der Status aus subjektiven Schadenwahrscheinlichkeiten;
    die VU-Auswahl sucht je Sparte den guenstigsten frueheren Versicherer und
    faellt nur ohne versicherte Historie auf eine aktive Zufallsauswahl zurueck.
    """

    if period < 1:
        raise ValueError("VN search insurance rule period must be at least 1")
    if period == 1:
        if initial_decisions is None:
            raise ValueError("VN search insurance rule period 1 requires initial_decisions")
        decisions = sorted(
            load_vn_insurance_decisions_from_mapping(initial_decisions),
            key=lambda item: item.sector_index,
        )
        selected_insurer_ids = [decision.insurer_id for decision in decisions]
        return VNSearchInsuranceRuleResult(
            decisions=decisions,
            insured=[decision.insured for decision in decisions],
            chosen_insurer_ids=selected_insurer_ids,
            selected_insurer_ids=selected_insurer_ids,
            selected_history_periods=[None, None],
            used_fallback=[False, False],
        )

    thresholds = _two_float_values(
        parameters.insurance_thresholds_shock if change_shock else parameters.insurance_thresholds_normal,
        fallback=0.0,
    )
    probabilities = _two_float_values(damage_probabilities, fallback=0.0)
    if any(value < 0.0 for value in probabilities):
        raise ValueError("VN search insurance rule damage probabilities must be non-negative")
    history_entries = load_vn_search_insurance_history_from_mapping(history)
    fallback_draws = (
        _two_float_values(draws.fallback_insurer_choice_draws, fallback=0.0)
        if draws is not None
        else None
    )
    if fallback_draws is not None:
        _validate_unit_interval(fallback_draws, field_name="fallback_insurer_choice_draws")
    active_ids = _active_insurer_ids(active_insurer_ids)

    decisions: list[VNInsuranceDecision] = []
    insured_values: list[bool] = []
    chosen_insurer_ids: list[int | None] = []
    selected_insurer_ids: list[int | None] = []
    selected_history_periods: list[int | None] = []
    used_fallback: list[bool] = []
    for sector_index in range(2):
        selected_id, selected_period, fallback_used = _select_searched_insurer(
            history=history_entries,
            sector_index=sector_index,
            active_insurer_ids=active_ids,
            fallback_draw=(fallback_draws[sector_index] if fallback_draws is not None else None),
            period=period,
        )
        insured = probabilities[sector_index] > thresholds[sector_index]
        insurer_id = selected_id if insured else None
        decisions.append(
            VNInsuranceDecision(
                sector_index=sector_index,
                insured=insured,
                insurer_id=insurer_id,
            )
        )
        insured_values.append(insured)
        chosen_insurer_ids.append(insurer_id)
        selected_insurer_ids.append(selected_id)
        selected_history_periods.append(selected_period)
        used_fallback.append(fallback_used)

    return VNSearchInsuranceRuleResult(
        decisions=decisions,
        insured=insured_values,
        chosen_insurer_ids=chosen_insurer_ids,
        selected_insurer_ids=selected_insurer_ids,
        selected_history_periods=selected_history_periods,
        used_fallback=used_fallback,
        fallback_insurer_choice_draws=fallback_draws,
    )


def apply_vn_sample_search_insurance_rule(
    parameters: VNSampleSearchInsuranceRuleParameters,
    *,
    period: int,
    market_damage_indicator: float,
    insurer_inputs: object,
    draws: VNSampleSearchInsuranceRuleDraws | None = None,
    initial_decisions: object = None,
    change_shock: bool = False,
    information_cost_per_sample: float = 0.0,
) -> VNSampleSearchInsuranceRuleResult:
    """
    Portiert den Versicherungsentscheidungsanteil aus Vrvn05.

    In Periode 1 verwendet der Altcode die initialen VN-Status-/VU-Werte. Ab
    Periode 2 folgt der Status aus dem globalen Schadenindikator; die
    VU-Auswahl zieht je Sparte eine Stichprobe aktiver Versicherer und nimmt
    den niedrigsten beobachteten aktuellen Praemienwert.
    """

    if period < 1:
        raise ValueError("VN sample search insurance rule period must be at least 1")
    if information_cost_per_sample < 0.0:
        raise ValueError("VN sample search insurance rule information cost must be non-negative")
    if period == 1:
        if initial_decisions is None:
            raise ValueError("VN sample search insurance rule period 1 requires initial_decisions")
        decisions = sorted(
            load_vn_insurance_decisions_from_mapping(initial_decisions),
            key=lambda item: item.sector_index,
        )
        selected_insurer_ids = [decision.insurer_id for decision in decisions]
        return VNSampleSearchInsuranceRuleResult(
            decisions=decisions,
            insured=[decision.insured for decision in decisions],
            chosen_insurer_ids=selected_insurer_ids,
            selected_insurer_ids=selected_insurer_ids,
            selected_premiums=[decision.premium for decision in decisions],
            sampled_insurer_ids=[[], []],
            used_insurer_choice_draws_by_sector=[[], []],
            information_cost=0.0,
        )

    if draws is None:
        raise ValueError("VN sample search insurance rule periods after 1 require insurer choice draws")
    thresholds = _two_float_values(
        parameters.insurance_thresholds_shock if change_shock else parameters.insurance_thresholds_normal,
        fallback=0.0,
    )
    sample_sizes = _two_int_values(
        parameters.sample_sizes_shock if change_shock else parameters.sample_sizes_normal,
        fallback=0,
    )
    if any(value <= 0 for value in sample_sizes):
        raise ValueError("VN sample search insurance rule sample sizes must be positive")
    active_inputs = load_vn_sample_search_insurer_inputs_from_mapping(insurer_inputs)
    draw_lists = _draw_lists_by_sector(draws.insurer_choice_draws_by_sector, sample_sizes=sample_sizes)
    indicator = float(market_damage_indicator)

    decisions: list[VNInsuranceDecision] = []
    insured_values: list[bool] = []
    chosen_insurer_ids: list[int | None] = []
    selected_insurer_ids: list[int | None] = []
    selected_premiums: list[float | None] = []
    sampled_insurer_ids: list[list[int]] = []
    for sector_index in range(2):
        selected_id, selected_premium, sector_sampled_ids = _select_sampled_insurer(
            insurer_inputs=active_inputs,
            sector_index=sector_index,
            draws=draw_lists[sector_index],
        )
        insured = indicator <= thresholds[sector_index]
        insurer_id = selected_id if insured else None
        premium = selected_premium if insured else None
        decisions.append(
            VNInsuranceDecision(
                sector_index=sector_index,
                insured=insured,
                insurer_id=insurer_id,
                premium=premium,
            )
        )
        insured_values.append(insured)
        chosen_insurer_ids.append(insurer_id)
        selected_insurer_ids.append(selected_id)
        selected_premiums.append(selected_premium)
        sampled_insurer_ids.append(sector_sampled_ids)

    return VNSampleSearchInsuranceRuleResult(
        decisions=decisions,
        insured=insured_values,
        chosen_insurer_ids=chosen_insurer_ids,
        selected_insurer_ids=selected_insurer_ids,
        selected_premiums=selected_premiums,
        sampled_insurer_ids=sampled_insurer_ids,
        used_insurer_choice_draws_by_sector=draw_lists,
        information_cost=float(sum(sample_sizes)) * information_cost_per_sample,
    )


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
    selected_insurer_ids: list[int] = []
    for sector_index in range(2):
        insured = thresholds[sector_index] <= status_draws[sector_index]
        selected_insurer_id = _choose_insurer(active_ids, insurer_choice_draws[sector_index])
        insurer_id = selected_insurer_id if insured else None
        decisions.append(
            VNInsuranceDecision(
                sector_index=sector_index,
                insured=insured,
                insurer_id=insurer_id,
            )
        )
        insured_values.append(insured)
        chosen_insurer_ids.append(insurer_id)
        selected_insurer_ids.append(selected_insurer_id)

    return VNRandomInsuranceRuleResult(
        decisions=decisions,
        insured=insured_values,
        chosen_insurer_ids=chosen_insurer_ids,
        selected_insurer_ids=selected_insurer_ids,
        status_draws=status_draws,
        insurer_choice_draws=insurer_choice_draws,
    )
