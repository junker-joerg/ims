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


@dataclass(slots=True)
class VUForeignInfoRuleSnapshot:
    """Expliziter Parameter-Snapshot fuer einen VU-Frmdinf-Regelkern-Aufruf."""

    insurer_id: int
    rule_kind: VUForeignInfoRuleKind
    parameters: VUForeignInfoRuleParameters
    interest_rate: float = 0.0
    change_shock: bool = False


@dataclass(slots=True)
class VUForeignInfoRuleApplication:
    """Diagnose eines angewendeten expliziten VU-Regelparameter-Snapshots."""

    insurer_id: int
    rule_kind: VUForeignInfoRuleKind
    result: VUForeignInfoRuleResult


@dataclass(slots=True)
class VUReserveMarkupRuleParameters:
    """Multiplikatoren fuer den portierten Vrvu03-Mark-Up-I-Ausschnitt."""

    premium_below_normal: list[float]
    premium_above_normal: list[float]
    advertising_below_normal: list[float]
    advertising_above_normal: list[float]
    premium_below_shock: list[float]
    premium_above_shock: list[float]
    advertising_below_shock: list[float]
    advertising_above_shock: list[float]


@dataclass(slots=True)
class VUReserveMarkupRuleResult:
    """Berechneter VU-Zielzustand fuer Vrvu03 / Mark-Up I."""

    premiums_current_sector: list[float]
    advertising_current_sector: list[float]
    reserves_current: list[float]
    threshold_comparison_values: list[float]


@dataclass(slots=True)
class VUReserveMarkupRuleSnapshot:
    """Expliziter Parameter-Snapshot fuer den Vrvu03-Mark-Up-I-Ausschnitt."""

    insurer_id: int
    parameters: VUReserveMarkupRuleParameters
    reserve_thresholds: list[float]
    interest_rate: float = 0.0
    change_shock: bool = False


@dataclass(slots=True)
class VUReserveMarkupRuleApplication:
    """Diagnose eines angewendeten Vrvu03-Mark-Up-I-Snapshots."""

    insurer_id: int
    result: VUReserveMarkupRuleResult


@dataclass(slots=True)
class VUExpectedClaimRuleParameters:
    """Multiplikatoren fuer den portierten Vrvu06-Erwartungsschaden-Ausschnitt."""

    premium_below_normal: list[float]
    premium_above_normal: list[float]
    advertising_below_normal: list[float]
    advertising_above_normal: list[float]
    premium_below_shock: list[float]
    premium_above_shock: list[float]
    advertising_below_shock: list[float]
    advertising_above_shock: list[float]


@dataclass(slots=True)
class VUExpectedClaimRuleResult:
    """Berechneter VU-Zielzustand fuer Vrvu06 / Erwartungsschaden."""

    premiums_current_sector: list[float]
    advertising_current_sector: list[float]
    reserves_current: list[float]
    expected_claim_values: list[float]


@dataclass(slots=True)
class VUExpectedClaimRuleSnapshot:
    """Expliziter Parameter-Snapshot fuer den Vrvu06-Erwartungsschaden-Ausschnitt."""

    insurer_id: int
    parameters: VUExpectedClaimRuleParameters
    interest_rate: float = 0.0
    change_shock: bool = False


@dataclass(slots=True)
class VUExpectedClaimRuleApplication:
    """Diagnose eines angewendeten Vrvu06-Erwartungsschaden-Snapshots."""

    insurer_id: int
    result: VUExpectedClaimRuleResult


@dataclass(slots=True)
class VUMarketShareMarkupRuleParameters:
    """Multiplikatoren fuer den portierten Vrvu05-Mark-Up-III-Ausschnitt."""

    premium_below_normal: list[float]
    premium_above_normal: list[float]
    advertising_below_normal: list[float]
    advertising_above_normal: list[float]
    premium_below_shock: list[float]
    premium_above_shock: list[float]
    advertising_below_shock: list[float]
    advertising_above_shock: list[float]


@dataclass(slots=True)
class VUMarketShareMarkupRuleResult:
    """Berechneter VU-Zielzustand fuer Vrvu05 / Mark-Up III."""

    premiums_current_sector: list[float]
    advertising_current_sector: list[float]
    reserves_current: list[float]
    market_share_values: list[float]


@dataclass(slots=True)
class VUMarketShareMarkupRuleSnapshot:
    """Expliziter Parameter-Snapshot fuer den Vrvu05-Mark-Up-III-Ausschnitt."""

    insurer_id: int
    parameters: VUMarketShareMarkupRuleParameters
    market_share_thresholds: list[float]
    active_policyholder_count: int
    interest_rate: float = 0.0
    change_shock: bool = False


@dataclass(slots=True)
class VUMarketShareMarkupRuleApplication:
    """Diagnose eines angewendeten Vrvu05-Mark-Up-III-Snapshots."""

    insurer_id: int
    result: VUMarketShareMarkupRuleResult


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


def _required_list(mapping: dict[str, object], key: str) -> list[float]:
    value = mapping.get(key)
    if not isinstance(value, list):
        raise ValueError(f"VU foreign-info rule parameters require list field: {key}")
    return _two_values(value, fallback=0.0)


def vu_foreign_info_rule_parameters_from_mapping(mapping: dict[str, object]) -> VUForeignInfoRuleParameters:
    """Laedt den kleinen VU-Frmdinf-Parameterblock aus einer Mapping-Struktur."""

    if not isinstance(mapping, dict):
        raise ValueError("VU foreign-info rule parameters must be an object")
    return VUForeignInfoRuleParameters(
        premium_intercept_normal=_required_list(mapping, "premium_intercept_normal"),
        premium_factor_normal=_required_list(mapping, "premium_factor_normal"),
        advertising_intercept_normal=_required_list(mapping, "advertising_intercept_normal"),
        advertising_factor_normal=_required_list(mapping, "advertising_factor_normal"),
        premium_intercept_shock=_required_list(mapping, "premium_intercept_shock"),
        premium_factor_shock=_required_list(mapping, "premium_factor_shock"),
        advertising_intercept_shock=_required_list(mapping, "advertising_intercept_shock"),
        advertising_factor_shock=_required_list(mapping, "advertising_factor_shock"),
    )


def vu_foreign_info_rule_snapshot_from_mapping(mapping: dict[str, object]) -> VUForeignInfoRuleSnapshot:
    """Laedt einen expliziten VU-Frmdinf-Regelparameter-Snapshot."""

    if not isinstance(mapping, dict):
        raise ValueError("VU foreign-info rule snapshot must be an object")
    if "insurer_id" not in mapping:
        raise ValueError("VU foreign-info rule snapshot requires field: insurer_id")
    if "rule_kind" not in mapping:
        raise ValueError("VU foreign-info rule snapshot requires field: rule_kind")
    parameters = mapping.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("VU foreign-info rule snapshot requires object field: parameters")
    try:
        rule_kind = VUForeignInfoRuleKind(str(mapping["rule_kind"]))
    except ValueError as exc:
        raise ValueError(f"unsupported VU foreign-info rule kind: {mapping['rule_kind']}") from exc
    return VUForeignInfoRuleSnapshot(
        insurer_id=int(mapping["insurer_id"]),
        rule_kind=rule_kind,
        parameters=vu_foreign_info_rule_parameters_from_mapping(parameters),
        interest_rate=float(mapping.get("interest_rate", 0.0)),
        change_shock=bool(mapping.get("change_shock", False)),
    )


def load_vu_foreign_info_rule_snapshots_from_mapping(value: object) -> list[VUForeignInfoRuleSnapshot]:
    """Laedt mehrere explizite VU-Frmdinf-Regelparameter-Snapshots aus In-Memory-Daten."""

    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("VU foreign-info rule snapshots must be a list")
    return [vu_foreign_info_rule_snapshot_from_mapping(item) for item in value]


def vu_reserve_markup_rule_parameters_from_mapping(mapping: dict[str, object]) -> VUReserveMarkupRuleParameters:
    """Laedt den Vrvu03-Mark-Up-I-Parameterblock aus einer Mapping-Struktur."""

    if not isinstance(mapping, dict):
        raise ValueError("VU reserve-markup rule parameters must be an object")
    return VUReserveMarkupRuleParameters(
        premium_below_normal=_required_list(mapping, "premium_below_normal"),
        premium_above_normal=_required_list(mapping, "premium_above_normal"),
        advertising_below_normal=_required_list(mapping, "advertising_below_normal"),
        advertising_above_normal=_required_list(mapping, "advertising_above_normal"),
        premium_below_shock=_required_list(mapping, "premium_below_shock"),
        premium_above_shock=_required_list(mapping, "premium_above_shock"),
        advertising_below_shock=_required_list(mapping, "advertising_below_shock"),
        advertising_above_shock=_required_list(mapping, "advertising_above_shock"),
    )


def vu_reserve_markup_rule_snapshot_from_mapping(mapping: dict[str, object]) -> VUReserveMarkupRuleSnapshot:
    """Laedt einen expliziten Vrvu03-Mark-Up-I-Snapshot."""

    if not isinstance(mapping, dict):
        raise ValueError("VU reserve-markup rule snapshot must be an object")
    if "insurer_id" not in mapping:
        raise ValueError("VU reserve-markup rule snapshot requires field: insurer_id")
    parameters = mapping.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("VU reserve-markup rule snapshot requires object field: parameters")
    return VUReserveMarkupRuleSnapshot(
        insurer_id=int(mapping["insurer_id"]),
        parameters=vu_reserve_markup_rule_parameters_from_mapping(parameters),
        reserve_thresholds=_two_values(mapping.get("reserve_thresholds"), fallback=0.0),
        interest_rate=float(mapping.get("interest_rate", 0.0)),
        change_shock=bool(mapping.get("change_shock", False)),
    )


def load_vu_reserve_markup_rule_snapshots_from_mapping(value: object) -> list[VUReserveMarkupRuleSnapshot]:
    """Laedt mehrere explizite Vrvu03-Mark-Up-I-Snapshots aus In-Memory-Daten."""

    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("VU reserve-markup rule snapshots must be a list")
    return [vu_reserve_markup_rule_snapshot_from_mapping(item) for item in value]


def vu_expected_claim_rule_parameters_from_mapping(mapping: dict[str, object]) -> VUExpectedClaimRuleParameters:
    """Laedt den Vrvu06-Erwartungsschaden-Parameterblock aus einer Mapping-Struktur."""

    if not isinstance(mapping, dict):
        raise ValueError("VU expected-claim rule parameters must be an object")
    return VUExpectedClaimRuleParameters(
        premium_below_normal=_required_list(mapping, "premium_below_normal"),
        premium_above_normal=_required_list(mapping, "premium_above_normal"),
        advertising_below_normal=_required_list(mapping, "advertising_below_normal"),
        advertising_above_normal=_required_list(mapping, "advertising_above_normal"),
        premium_below_shock=_required_list(mapping, "premium_below_shock"),
        premium_above_shock=_required_list(mapping, "premium_above_shock"),
        advertising_below_shock=_required_list(mapping, "advertising_below_shock"),
        advertising_above_shock=_required_list(mapping, "advertising_above_shock"),
    )


def vu_expected_claim_rule_snapshot_from_mapping(mapping: dict[str, object]) -> VUExpectedClaimRuleSnapshot:
    """Laedt einen expliziten Vrvu06-Erwartungsschaden-Snapshot."""

    if not isinstance(mapping, dict):
        raise ValueError("VU expected-claim rule snapshot must be an object")
    if "insurer_id" not in mapping:
        raise ValueError("VU expected-claim rule snapshot requires field: insurer_id")
    parameters = mapping.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("VU expected-claim rule snapshot requires object field: parameters")
    return VUExpectedClaimRuleSnapshot(
        insurer_id=int(mapping["insurer_id"]),
        parameters=vu_expected_claim_rule_parameters_from_mapping(parameters),
        interest_rate=float(mapping.get("interest_rate", 0.0)),
        change_shock=bool(mapping.get("change_shock", False)),
    )


def load_vu_expected_claim_rule_snapshots_from_mapping(value: object) -> list[VUExpectedClaimRuleSnapshot]:
    """Laedt mehrere explizite Vrvu06-Erwartungsschaden-Snapshots aus In-Memory-Daten."""

    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("VU expected-claim rule snapshots must be a list")
    return [vu_expected_claim_rule_snapshot_from_mapping(item) for item in value]


def vu_market_share_markup_rule_parameters_from_mapping(mapping: dict[str, object]) -> VUMarketShareMarkupRuleParameters:
    """Laedt den Vrvu05-Mark-Up-III-Parameterblock aus einer Mapping-Struktur."""

    if not isinstance(mapping, dict):
        raise ValueError("VU market-share-markup rule parameters must be an object")
    return VUMarketShareMarkupRuleParameters(
        premium_below_normal=_required_list(mapping, "premium_below_normal"),
        premium_above_normal=_required_list(mapping, "premium_above_normal"),
        advertising_below_normal=_required_list(mapping, "advertising_below_normal"),
        advertising_above_normal=_required_list(mapping, "advertising_above_normal"),
        premium_below_shock=_required_list(mapping, "premium_below_shock"),
        premium_above_shock=_required_list(mapping, "premium_above_shock"),
        advertising_below_shock=_required_list(mapping, "advertising_below_shock"),
        advertising_above_shock=_required_list(mapping, "advertising_above_shock"),
    )


def vu_market_share_markup_rule_snapshot_from_mapping(mapping: dict[str, object]) -> VUMarketShareMarkupRuleSnapshot:
    """Laedt einen expliziten Vrvu05-Mark-Up-III-Snapshot."""

    if not isinstance(mapping, dict):
        raise ValueError("VU market-share-markup rule snapshot must be an object")
    if "insurer_id" not in mapping:
        raise ValueError("VU market-share-markup rule snapshot requires field: insurer_id")
    parameters = mapping.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("VU market-share-markup rule snapshot requires object field: parameters")
    return VUMarketShareMarkupRuleSnapshot(
        insurer_id=int(mapping["insurer_id"]),
        parameters=vu_market_share_markup_rule_parameters_from_mapping(parameters),
        market_share_thresholds=_two_values(mapping.get("market_share_thresholds"), fallback=0.0),
        active_policyholder_count=int(mapping.get("active_policyholder_count", 0)),
        interest_rate=float(mapping.get("interest_rate", 0.0)),
        change_shock=bool(mapping.get("change_shock", False)),
    )


def load_vu_market_share_markup_rule_snapshots_from_mapping(value: object) -> list[VUMarketShareMarkupRuleSnapshot]:
    """Laedt mehrere explizite Vrvu05-Mark-Up-III-Snapshots aus In-Memory-Daten."""

    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("VU market-share-markup rule snapshots must be a list")
    return [vu_market_share_markup_rule_snapshot_from_mapping(item) for item in value]


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


def apply_vu_foreign_info_rule_snapshots(
    insurers: list[Insurer],
    bav: BAV,
    snapshots: list[VUForeignInfoRuleSnapshot],
    *,
    period: int,
) -> list[VUForeignInfoRuleApplication]:
    """Wendet explizite VU-Frmdinf-Snapshots deterministisch auf passende Versicherer an."""

    insurers_by_id = {insurer.entity_id: insurer for insurer in insurers}
    applications: list[VUForeignInfoRuleApplication] = []
    seen_insurer_ids: set[int] = set()
    for snapshot in snapshots:
        if snapshot.insurer_id in seen_insurer_ids:
            raise ValueError(f"duplicate VU foreign-info rule snapshot for insurer: {snapshot.insurer_id}")
        seen_insurer_ids.add(snapshot.insurer_id)
        insurer = insurers_by_id.get(snapshot.insurer_id)
        if insurer is None:
            raise ValueError(f"VU foreign-info rule snapshot references unknown insurer: {snapshot.insurer_id}")
        result = apply_vu_foreign_info_rule_to_insurer(
            insurer,
            bav,
            snapshot.parameters,
            period=period,
            interest_rate=snapshot.interest_rate,
            rule_kind=snapshot.rule_kind,
            change_shock=snapshot.change_shock,
        )
        applications.append(
            VUForeignInfoRuleApplication(
                insurer_id=snapshot.insurer_id,
                rule_kind=snapshot.rule_kind,
                result=result,
            )
        )
    return applications


def apply_vu_reserve_markup_rule(
    insurer: Insurer,
    parameters: VUReserveMarkupRuleParameters,
    *,
    period: int,
    reserve_thresholds: list[float],
    interest_rate: float,
    change_shock: bool = False,
) -> VUReserveMarkupRuleResult:
    """
    Portiert den deterministischen Kern von Vrvu03 / Mark-Up I.

    Die historische Regel vergleicht in der Normalvariante die Vorperiodenreserven
    je Sparte mit Anspruchsniveaus. Im Aenderungsschock-Zweig vergleicht Vrvu03
    dagegen hart gegen 0.0; diese Asymmetrie wird hier bewusst beibehalten.
    """

    previous_premiums = _two_values(insurer.premiums_current_sector, fallback=insurer.premiums_current)
    previous_advertising = _two_values(insurer.advertising_current_sector, fallback=insurer.advertising_current)
    previous_reserves = _two_values(insurer.reserves_current, fallback=0.0)

    if period <= 1:
        return VUReserveMarkupRuleResult(
            premiums_current_sector=previous_premiums,
            advertising_current_sector=previous_advertising,
            reserves_current=[(1.0 + interest_rate) * value for value in previous_reserves],
            threshold_comparison_values=previous_reserves,
        )

    comparison_thresholds = [0.0, 0.0] if change_shock else _two_values(reserve_thresholds, fallback=0.0)
    if change_shock:
        premium_below = _parameter_values(parameters.premium_below_shock)
        premium_above = _parameter_values(parameters.premium_above_shock)
        advertising_below = _parameter_values(parameters.advertising_below_shock)
        advertising_above = _parameter_values(parameters.advertising_above_shock)
    else:
        premium_below = _parameter_values(parameters.premium_below_normal)
        premium_above = _parameter_values(parameters.premium_above_normal)
        advertising_below = _parameter_values(parameters.advertising_below_normal)
        advertising_above = _parameter_values(parameters.advertising_above_normal)

    premium_multipliers = [
        premium_below[index] if previous_reserves[index] <= comparison_thresholds[index] else premium_above[index]
        for index in range(2)
    ]
    advertising_multipliers = [
        advertising_below[index] if previous_reserves[index] <= comparison_thresholds[index] else advertising_above[index]
        for index in range(2)
    ]
    return VUReserveMarkupRuleResult(
        premiums_current_sector=[
            premium_multipliers[index] * previous_premiums[index]
            for index in range(2)
        ],
        advertising_current_sector=[
            advertising_multipliers[index] * previous_advertising[index]
            for index in range(2)
        ],
        reserves_current=[(1.0 + interest_rate) * value for value in previous_reserves],
        threshold_comparison_values=comparison_thresholds,
    )


def apply_vu_reserve_markup_rule_to_insurer(
    insurer: Insurer,
    parameters: VUReserveMarkupRuleParameters,
    *,
    period: int,
    reserve_thresholds: list[float],
    interest_rate: float,
    change_shock: bool = False,
) -> VUReserveMarkupRuleResult:
    """Berechnet Vrvu03 / Mark-Up I und schreibt den aktuellen VU-Snapshot fort."""

    result = apply_vu_reserve_markup_rule(
        insurer,
        parameters,
        period=period,
        reserve_thresholds=reserve_thresholds,
        interest_rate=interest_rate,
        change_shock=change_shock,
    )
    insurer.premiums_current_sector = result.premiums_current_sector
    insurer.advertising_current_sector = result.advertising_current_sector
    insurer.premiums_current = result.premiums_current_sector[0]
    insurer.advertising_current = result.advertising_current_sector[0]
    insurer.reserves_current = result.reserves_current
    return result


def apply_vu_reserve_markup_rule_snapshots(
    insurers: list[Insurer],
    snapshots: list[VUReserveMarkupRuleSnapshot],
    *,
    period: int,
) -> list[VUReserveMarkupRuleApplication]:
    """Wendet explizite Vrvu03-Mark-Up-I-Snapshots deterministisch auf passende Versicherer an."""

    insurers_by_id = {insurer.entity_id: insurer for insurer in insurers}
    applications: list[VUReserveMarkupRuleApplication] = []
    seen_insurer_ids: set[int] = set()
    for snapshot in snapshots:
        if snapshot.insurer_id in seen_insurer_ids:
            raise ValueError(f"duplicate VU reserve-markup rule snapshot for insurer: {snapshot.insurer_id}")
        seen_insurer_ids.add(snapshot.insurer_id)
        insurer = insurers_by_id.get(snapshot.insurer_id)
        if insurer is None:
            raise ValueError(f"VU reserve-markup rule snapshot references unknown insurer: {snapshot.insurer_id}")
        result = apply_vu_reserve_markup_rule_to_insurer(
            insurer,
            snapshot.parameters,
            period=period,
            reserve_thresholds=snapshot.reserve_thresholds,
            interest_rate=snapshot.interest_rate,
            change_shock=snapshot.change_shock,
        )
        applications.append(VUReserveMarkupRuleApplication(insurer_id=snapshot.insurer_id, result=result))
    return applications


def _expected_claim_values(claim_counts: list[int], claim_sums: list[float]) -> list[float]:
    counts = _two_values(claim_counts, fallback=0.0)
    sums = _two_values(claim_sums, fallback=0.0)
    return [
        sums[index] / counts[index] if counts[index] != 0 else 0.0
        for index in range(2)
    ]


def apply_vu_expected_claim_rule(
    insurer: Insurer,
    parameters: VUExpectedClaimRuleParameters,
    *,
    period: int,
    interest_rate: float,
    change_shock: bool = False,
) -> VUExpectedClaimRuleResult:
    """
    Portiert den deterministischen Kern von Vrvu06 / Erwartungsschaden.

    Die historische Regel berechnet je Sparte `Sh / Sa` mit Nullschutz und
    vergleicht die Vorperiodenpraemie gegen diesen erwarteten Schadenwert.
    """

    previous_premiums = _two_values(insurer.premiums_current_sector, fallback=insurer.premiums_current)
    previous_advertising = _two_values(insurer.advertising_current_sector, fallback=insurer.advertising_current)
    previous_reserves = _two_values(insurer.reserves_current, fallback=0.0)
    expected_claims = _expected_claim_values(insurer.claims_count_current, insurer.claims_sum_current)

    if period <= 1:
        return VUExpectedClaimRuleResult(
            premiums_current_sector=previous_premiums,
            advertising_current_sector=previous_advertising,
            reserves_current=[(1.0 + interest_rate) * value for value in previous_reserves],
            expected_claim_values=expected_claims,
        )

    if change_shock:
        premium_below = _parameter_values(parameters.premium_below_shock)
        premium_above = _parameter_values(parameters.premium_above_shock)
        advertising_below = _parameter_values(parameters.advertising_below_shock)
        advertising_above = _parameter_values(parameters.advertising_above_shock)
    else:
        premium_below = _parameter_values(parameters.premium_below_normal)
        premium_above = _parameter_values(parameters.premium_above_normal)
        advertising_below = _parameter_values(parameters.advertising_below_normal)
        advertising_above = _parameter_values(parameters.advertising_above_normal)

    premium_multipliers = [
        premium_below[index] if previous_premiums[index] <= expected_claims[index] else premium_above[index]
        for index in range(2)
    ]
    advertising_multipliers = [
        advertising_below[index] if previous_premiums[index] <= expected_claims[index] else advertising_above[index]
        for index in range(2)
    ]
    return VUExpectedClaimRuleResult(
        premiums_current_sector=[
            premium_multipliers[index] * previous_premiums[index]
            for index in range(2)
        ],
        advertising_current_sector=[
            advertising_multipliers[index] * previous_advertising[index]
            for index in range(2)
        ],
        reserves_current=[(1.0 + interest_rate) * value for value in previous_reserves],
        expected_claim_values=expected_claims,
    )


def apply_vu_expected_claim_rule_to_insurer(
    insurer: Insurer,
    parameters: VUExpectedClaimRuleParameters,
    *,
    period: int,
    interest_rate: float,
    change_shock: bool = False,
) -> VUExpectedClaimRuleResult:
    """Berechnet Vrvu06 / Erwartungsschaden und schreibt den aktuellen VU-Snapshot fort."""

    result = apply_vu_expected_claim_rule(
        insurer,
        parameters,
        period=period,
        interest_rate=interest_rate,
        change_shock=change_shock,
    )
    insurer.premiums_current_sector = result.premiums_current_sector
    insurer.advertising_current_sector = result.advertising_current_sector
    insurer.premiums_current = result.premiums_current_sector[0]
    insurer.advertising_current = result.advertising_current_sector[0]
    insurer.reserves_current = result.reserves_current
    return result


def apply_vu_expected_claim_rule_snapshots(
    insurers: list[Insurer],
    snapshots: list[VUExpectedClaimRuleSnapshot],
    *,
    period: int,
) -> list[VUExpectedClaimRuleApplication]:
    """Wendet explizite Vrvu06-Erwartungsschaden-Snapshots deterministisch auf passende Versicherer an."""

    insurers_by_id = {insurer.entity_id: insurer for insurer in insurers}
    applications: list[VUExpectedClaimRuleApplication] = []
    seen_insurer_ids: set[int] = set()
    for snapshot in snapshots:
        if snapshot.insurer_id in seen_insurer_ids:
            raise ValueError(f"duplicate VU expected-claim rule snapshot for insurer: {snapshot.insurer_id}")
        seen_insurer_ids.add(snapshot.insurer_id)
        insurer = insurers_by_id.get(snapshot.insurer_id)
        if insurer is None:
            raise ValueError(f"VU expected-claim rule snapshot references unknown insurer: {snapshot.insurer_id}")
        result = apply_vu_expected_claim_rule_to_insurer(
            insurer,
            snapshot.parameters,
            period=period,
            interest_rate=snapshot.interest_rate,
            change_shock=snapshot.change_shock,
        )
        applications.append(VUExpectedClaimRuleApplication(insurer_id=snapshot.insurer_id, result=result))
    return applications


def _market_share_values(policyholders: list[float], active_policyholder_count: int) -> list[float]:
    values = _two_values(policyholders, fallback=0.0)
    if active_policyholder_count == 0:
        return [0.0, 0.0]
    return [value / float(active_policyholder_count) for value in values]


def apply_vu_market_share_markup_rule(
    insurer: Insurer,
    parameters: VUMarketShareMarkupRuleParameters,
    *,
    period: int,
    market_share_thresholds: list[float],
    active_policyholder_count: int,
    interest_rate: float,
    change_shock: bool = False,
) -> VUMarketShareMarkupRuleResult:
    """
    Portiert den deterministischen Kern von Vrvu05 / Mark-Up III.

    Die historische Regel berechnet je Sparte den Marktanteil `Vn / akvn`
    mit Nullschutz und vergleicht ihn gegen ein Anspruchsniveau.
    """

    previous_premiums = _two_values(insurer.premiums_current_sector, fallback=insurer.premiums_current)
    previous_advertising = _two_values(insurer.advertising_current_sector, fallback=insurer.advertising_current)
    previous_reserves = _two_values(insurer.reserves_current, fallback=0.0)
    previous_policyholders = _two_values(insurer.policyholders_current_sector, fallback=insurer.policyholders_current)
    market_shares = _market_share_values(previous_policyholders, active_policyholder_count)

    if period <= 1:
        return VUMarketShareMarkupRuleResult(
            premiums_current_sector=previous_premiums,
            advertising_current_sector=previous_advertising,
            reserves_current=[(1.0 + interest_rate) * value for value in previous_reserves],
            market_share_values=market_shares,
        )

    if change_shock:
        premium_below = _parameter_values(parameters.premium_below_shock)
        premium_above = _parameter_values(parameters.premium_above_shock)
        advertising_below = _parameter_values(parameters.advertising_below_shock)
        advertising_above = _parameter_values(parameters.advertising_above_shock)
    else:
        premium_below = _parameter_values(parameters.premium_below_normal)
        premium_above = _parameter_values(parameters.premium_above_normal)
        advertising_below = _parameter_values(parameters.advertising_below_normal)
        advertising_above = _parameter_values(parameters.advertising_above_normal)

    thresholds = _two_values(market_share_thresholds, fallback=0.0)
    premium_multipliers = [
        premium_below[index] if market_shares[index] <= thresholds[index] else premium_above[index]
        for index in range(2)
    ]
    advertising_multipliers = [
        advertising_below[index] if market_shares[index] <= thresholds[index] else advertising_above[index]
        for index in range(2)
    ]
    return VUMarketShareMarkupRuleResult(
        premiums_current_sector=[
            premium_multipliers[index] * previous_premiums[index]
            for index in range(2)
        ],
        advertising_current_sector=[
            advertising_multipliers[index] * previous_advertising[index]
            for index in range(2)
        ],
        reserves_current=[(1.0 + interest_rate) * value for value in previous_reserves],
        market_share_values=market_shares,
    )


def apply_vu_market_share_markup_rule_to_insurer(
    insurer: Insurer,
    parameters: VUMarketShareMarkupRuleParameters,
    *,
    period: int,
    market_share_thresholds: list[float],
    active_policyholder_count: int,
    interest_rate: float,
    change_shock: bool = False,
) -> VUMarketShareMarkupRuleResult:
    """Berechnet Vrvu05 / Mark-Up III und schreibt den aktuellen VU-Snapshot fort."""

    result = apply_vu_market_share_markup_rule(
        insurer,
        parameters,
        period=period,
        market_share_thresholds=market_share_thresholds,
        active_policyholder_count=active_policyholder_count,
        interest_rate=interest_rate,
        change_shock=change_shock,
    )
    insurer.premiums_current_sector = result.premiums_current_sector
    insurer.advertising_current_sector = result.advertising_current_sector
    insurer.premiums_current = result.premiums_current_sector[0]
    insurer.advertising_current = result.advertising_current_sector[0]
    insurer.reserves_current = result.reserves_current
    return result


def apply_vu_market_share_markup_rule_snapshots(
    insurers: list[Insurer],
    snapshots: list[VUMarketShareMarkupRuleSnapshot],
    *,
    period: int,
) -> list[VUMarketShareMarkupRuleApplication]:
    """Wendet explizite Vrvu05-Mark-Up-III-Snapshots deterministisch auf passende Versicherer an."""

    insurers_by_id = {insurer.entity_id: insurer for insurer in insurers}
    applications: list[VUMarketShareMarkupRuleApplication] = []
    seen_insurer_ids: set[int] = set()
    for snapshot in snapshots:
        if snapshot.insurer_id in seen_insurer_ids:
            raise ValueError(f"duplicate VU market-share-markup rule snapshot for insurer: {snapshot.insurer_id}")
        seen_insurer_ids.add(snapshot.insurer_id)
        insurer = insurers_by_id.get(snapshot.insurer_id)
        if insurer is None:
            raise ValueError(f"VU market-share-markup rule snapshot references unknown insurer: {snapshot.insurer_id}")
        result = apply_vu_market_share_markup_rule_to_insurer(
            insurer,
            snapshot.parameters,
            period=period,
            market_share_thresholds=snapshot.market_share_thresholds,
            active_policyholder_count=snapshot.active_policyholder_count,
            interest_rate=snapshot.interest_rate,
            change_shock=snapshot.change_shock,
        )
        applications.append(VUMarketShareMarkupRuleApplication(insurer_id=snapshot.insurer_id, result=result))
    return applications
