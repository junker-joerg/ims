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
