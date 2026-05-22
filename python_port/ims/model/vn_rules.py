from collections.abc import Callable
from dataclasses import dataclass

from ims.model.entities import Insurer, Policyholder
from ims.model.vn_damage_rules import (
    VNDamageRuleDraws,
    VNDamageRuleParameters,
    VNDamageRuleResult,
    apply_vn_damage_rule,
    vn_damage_rule_draws_from_mapping,
    vn_damage_rule_parameters_from_mapping,
)


@dataclass(slots=True)
class VNInsuranceDecision:
    """Explizite VN-Versicherungsentscheidung fuer eine Sparte ohne Schadenhoehe."""

    sector_index: int
    insured: bool
    insurer_id: int | None = None
    premium: float | None = None


@dataclass(slots=True)
class VNSectorSettlementDecision:
    """Explizite VN-Entscheidung und Schadenrealisation fuer eine Sparte."""

    sector_index: int
    insured: bool
    damage: float
    insurer_id: int | None = None
    premium: float | None = None


@dataclass(slots=True)
class VNSettlementSnapshot:
    """Expliziter Snapshot fuer den deterministischen Abrechnungsteil der VN-Regeln."""

    policyholder_id: int
    decisions: list[VNSectorSettlementDecision]
    previous_wealth: float
    previous_wealth_sector: list[float] | None = None


@dataclass(slots=True)
class VNSettlementResult:
    """Aktualisierter VN-Zustand nach Abrechnung beider Sparten."""

    chosen_insurer_sector_current: list[int | None]
    insured_current_sector: list[float]
    paid_premium_current: list[float]
    self_damage_current: list[float]
    claim_sum_current: list[float]
    end_wealth_sector_current: list[float]
    end_wealth_current: float


@dataclass(slots=True)
class VNSettlementApplication:
    """Diagnose eines angewendeten VN-Settlement-Snapshots."""

    policyholder_id: int
    result: VNSettlementResult


@dataclass(slots=True)
class VNDamageSettlementSnapshot:
    """Expliziter VN-Periodensnapshot fuer Schadenkern plus Abrechnung."""

    policyholder_id: int
    parameters: VNDamageRuleParameters
    damage_thresholds: list[float]
    previous_wealth: float
    insurance_decisions: list[VNInsuranceDecision] | None = None
    draws: VNDamageRuleDraws | None = None
    previous_wealth_sector: list[float] | None = None
    change_shock: bool = False


@dataclass(slots=True)
class VNDamageSettlementApplication:
    """Diagnose eines angewendeten expliziten VN-Schaden-Abrechnungs-Snapshots."""

    policyholder_id: int
    damage_result: VNDamageRuleResult
    settlement_result: VNSettlementResult


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


def _decision_list(value: object) -> list[VNSectorSettlementDecision]:
    if not isinstance(value, list):
        raise ValueError("VN settlement snapshot requires list field: decisions")
    decisions = [vn_sector_settlement_decision_from_mapping(item) for item in value]
    sectors = [decision.sector_index for decision in decisions]
    if sorted(sectors) != [0, 1]:
        raise ValueError("VN settlement snapshot requires exactly one decision for sector_index 0 and 1")
    return decisions


def _insurance_decision_list(value: object) -> list[VNInsuranceDecision]:
    if not isinstance(value, list):
        raise ValueError("VN insurance decisions require a list")
    decisions = [
        item if isinstance(item, VNInsuranceDecision) else vn_insurance_decision_from_mapping(item)
        for item in value
    ]
    sectors = [decision.sector_index for decision in decisions]
    if sorted(sectors) != [0, 1]:
        raise ValueError("VN insurance decisions require exactly one decision for sector_index 0 and 1")
    return decisions


def _optional_two_float_values(value: object) -> list[float] | None:
    if value is None:
        return None
    return _two_float_values(value, fallback=0.0)


def vn_insurance_decision_from_mapping(mapping: dict[str, object]) -> VNInsuranceDecision:
    """Laedt eine explizite VN-Versicherungsentscheidung ohne Schadenhoehe."""

    if not isinstance(mapping, dict):
        raise ValueError("VN insurance decision must be an object")
    if "sector_index" not in mapping:
        raise ValueError("VN insurance decision requires field: sector_index")
    if "insured" not in mapping:
        raise ValueError("VN insurance decision requires field: insured")

    sector_index = int(mapping["sector_index"])
    if sector_index not in (0, 1):
        raise ValueError(f"VN insurance decision has unsupported sector_index: {sector_index}")

    premium = None if mapping.get("premium") is None else float(mapping["premium"])
    if premium is not None and premium < 0.0:
        raise ValueError("VN insurance decision premium must be non-negative")

    insurer_id = None if mapping.get("insurer_id") is None else int(mapping["insurer_id"])
    insured = bool(mapping["insured"])
    if insured and insurer_id is None:
        raise ValueError("insured VN insurance decision requires insurer_id")
    if not insured and insurer_id is not None:
        raise ValueError("uninsured VN insurance decision must not reference insurer_id")

    return VNInsuranceDecision(
        sector_index=sector_index,
        insured=insured,
        insurer_id=insurer_id,
        premium=premium,
    )


def vn_sector_settlement_decision_from_mapping(mapping: dict[str, object]) -> VNSectorSettlementDecision:
    """Laedt eine explizite VN-Sektorentscheidung aus einer Mapping-Struktur."""

    if not isinstance(mapping, dict):
        raise ValueError("VN sector settlement decision must be an object")
    if "sector_index" not in mapping:
        raise ValueError("VN sector settlement decision requires field: sector_index")
    if "insured" not in mapping:
        raise ValueError("VN sector settlement decision requires field: insured")
    if "damage" not in mapping:
        raise ValueError("VN sector settlement decision requires field: damage")

    sector_index = int(mapping["sector_index"])
    if sector_index not in (0, 1):
        raise ValueError(f"VN sector settlement decision has unsupported sector_index: {sector_index}")

    damage = float(mapping["damage"])
    if damage < 0.0:
        raise ValueError("VN sector settlement decision damage must be non-negative")

    premium = None if mapping.get("premium") is None else float(mapping["premium"])
    if premium is not None and premium < 0.0:
        raise ValueError("VN sector settlement decision premium must be non-negative")

    insurer_id = None if mapping.get("insurer_id") is None else int(mapping["insurer_id"])
    insured = bool(mapping["insured"])
    if insured and insurer_id is None:
        raise ValueError("insured VN sector settlement decision requires insurer_id")
    if not insured and insurer_id is not None:
        raise ValueError("uninsured VN sector settlement decision must not reference insurer_id")

    return VNSectorSettlementDecision(
        sector_index=sector_index,
        insured=insured,
        damage=damage,
        insurer_id=insurer_id,
        premium=premium,
    )


def vn_settlement_snapshot_from_mapping(mapping: dict[str, object]) -> VNSettlementSnapshot:
    """Laedt einen expliziten VN-Settlement-Snapshot."""

    if not isinstance(mapping, dict):
        raise ValueError("VN settlement snapshot must be an object")
    if "policyholder_id" not in mapping:
        raise ValueError("VN settlement snapshot requires field: policyholder_id")
    if "previous_wealth" not in mapping:
        raise ValueError("VN settlement snapshot requires field: previous_wealth")
    return VNSettlementSnapshot(
        policyholder_id=int(mapping["policyholder_id"]),
        decisions=_decision_list(mapping.get("decisions")),
        previous_wealth=float(mapping["previous_wealth"]),
        previous_wealth_sector=_optional_two_float_values(mapping.get("previous_wealth_sector")),
    )


def load_vn_settlement_snapshots_from_mapping(value: object) -> list[VNSettlementSnapshot]:
    """Laedt mehrere explizite VN-Settlement-Snapshots aus In-Memory-Daten."""

    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("VN settlement snapshots must be a list")
    return [vn_settlement_snapshot_from_mapping(item) for item in value]


def vn_damage_settlement_snapshot_from_mapping(mapping: dict[str, object]) -> VNDamageSettlementSnapshot:
    """Laedt einen expliziten VN-Schaden-Abrechnungs-Snapshot."""

    if not isinstance(mapping, dict):
        raise ValueError("VN damage settlement snapshot must be an object")
    for key in ("policyholder_id", "previous_wealth", "parameters", "damage_thresholds"):
        if key not in mapping:
            raise ValueError(f"VN damage settlement snapshot requires field: {key}")
    return VNDamageSettlementSnapshot(
        policyholder_id=int(mapping["policyholder_id"]),
        parameters=vn_damage_rule_parameters_from_mapping(mapping["parameters"]),
        damage_thresholds=_two_float_values(mapping["damage_thresholds"], fallback=0.0),
        draws=(
            vn_damage_rule_draws_from_mapping(mapping["draws"])
            if "draws" in mapping
            else None
        ),
        insurance_decisions=(
            load_vn_insurance_decisions_from_mapping(mapping["insurance_decisions"])
            if "insurance_decisions" in mapping
            else None
        ),
        previous_wealth=float(mapping["previous_wealth"]),
        previous_wealth_sector=_optional_two_float_values(mapping.get("previous_wealth_sector")),
        change_shock=bool(mapping.get("change_shock", False)),
    )


def load_vn_damage_settlement_snapshots_from_mapping(value: object) -> list[VNDamageSettlementSnapshot]:
    """Laedt explizite VN-Schaden-Abrechnungs-Snapshots aus In-Memory-Daten."""

    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("VN damage settlement snapshots must be a list")
    return [vn_damage_settlement_snapshot_from_mapping(item) for item in value]


def build_vn_settlement_snapshot_from_damage_result(
    *,
    policyholder_id: int,
    previous_wealth: float,
    insurance_decisions: list[VNInsuranceDecision],
    damage_result: VNDamageRuleResult,
    previous_wealth_sector: list[float] | None = None,
) -> VNSettlementSnapshot:
    """
    Verbindet explizite VN-Versicherungsentscheidungen mit portierten Schaeden.

    Das bleibt bewusst ein reiner Kopplungsschritt: Versichererwahl, Praeferenzlogik
    und die historischen Normalziehungen muessen bereits ausserhalb feststehen.
    """

    decisions = _insurance_decision_list(insurance_decisions)
    damages = _two_float_values(damage_result.damages, fallback=0.0)
    return VNSettlementSnapshot(
        policyholder_id=int(policyholder_id),
        previous_wealth=float(previous_wealth),
        previous_wealth_sector=_optional_two_float_values(previous_wealth_sector),
        decisions=[
            VNSectorSettlementDecision(
                sector_index=decision.sector_index,
                insured=decision.insured,
                insurer_id=decision.insurer_id,
                premium=decision.premium,
                damage=damages[decision.sector_index],
            )
            for decision in sorted(decisions, key=lambda item: item.sector_index)
        ],
    )


def load_vn_insurance_decisions_from_mapping(value: object) -> list[VNInsuranceDecision]:
    """Laedt mehrere explizite VN-Versicherungsentscheidungen aus In-Memory-Daten."""

    return _insurance_decision_list(value)


def apply_vn_damage_settlement_snapshot(
    policyholder: Policyholder,
    insurers: list[Insurer],
    snapshot: VNDamageSettlementSnapshot,
    *,
    damage_draw_provider: Callable[[], VNDamageRuleDraws] | None = None,
) -> VNDamageSettlementApplication:
    """
    Wendet einen expliziten VN-Schaden-Abrechnungs-Snapshot an.

    Der Snapshot enthaelt Parameter, Schwellen und Versicherungsentscheidungen
    explizit. Fehlende Normalziehungen muessen ueber eine explizite Draw-Quelle
    geliefert werden; historische Wahl- und RNG-Logik bleiben ausserhalb dieses
    Slices.
    """

    if policyholder.entity_id != snapshot.policyholder_id:
        raise ValueError(
            "VN damage settlement snapshot policyholder_id does not match policyholder: "
            f"{snapshot.policyholder_id} != {policyholder.entity_id}"
        )
    if snapshot.insurance_decisions is None:
        raise ValueError("VN damage settlement snapshot requires insurance decisions")
    draws = snapshot.draws
    if draws is None:
        if damage_draw_provider is None:
            raise ValueError("VN damage settlement snapshot requires draws or runner draw source")
        draws = damage_draw_provider()
    damage_result = apply_vn_damage_rule(
        snapshot.parameters,
        damage_thresholds=snapshot.damage_thresholds,
        draws=draws,
        change_shock=snapshot.change_shock,
    )
    settlement_snapshot = build_vn_settlement_snapshot_from_damage_result(
        policyholder_id=snapshot.policyholder_id,
        previous_wealth=snapshot.previous_wealth,
        previous_wealth_sector=snapshot.previous_wealth_sector,
        insurance_decisions=snapshot.insurance_decisions,
        damage_result=damage_result,
    )
    settlement_result = apply_vn_settlement_snapshot(policyholder, insurers, settlement_snapshot)
    return VNDamageSettlementApplication(
        policyholder_id=snapshot.policyholder_id,
        damage_result=damage_result,
        settlement_result=settlement_result,
    )


def apply_vn_damage_settlement_snapshots(
    policyholders: list[Policyholder],
    insurers: list[Insurer],
    snapshots: list[VNDamageSettlementSnapshot],
    *,
    damage_draw_provider: Callable[[], VNDamageRuleDraws] | None = None,
) -> list[VNDamageSettlementApplication]:
    """Wendet explizite VN-Schaden-Abrechnungs-Snapshots auf passende VNs an."""

    policyholders_by_id = {policyholder.entity_id: policyholder for policyholder in policyholders}
    applications: list[VNDamageSettlementApplication] = []
    seen_policyholder_ids: set[int] = set()
    for snapshot in snapshots:
        if snapshot.policyholder_id in seen_policyholder_ids:
            raise ValueError(f"duplicate VN damage settlement snapshot for policyholder: {snapshot.policyholder_id}")
        seen_policyholder_ids.add(snapshot.policyholder_id)
        policyholder = policyholders_by_id.get(snapshot.policyholder_id)
        if policyholder is None:
            raise ValueError(f"VN damage settlement snapshot references unknown policyholder: {snapshot.policyholder_id}")
        application = apply_vn_damage_settlement_snapshot(
            policyholder,
            insurers,
            snapshot,
            damage_draw_provider=damage_draw_provider,
        )
        applications.append(application)
    return applications


def _current_sector_premium(insurer: Insurer, sector_index: int) -> float:
    premiums = _two_float_values(insurer.premiums_current_sector, fallback=insurer.premiums_current)
    return premiums[sector_index]


def _policyholder_vector_for_sector(insurer: Insurer, sector_index: int) -> list[float]:
    if insurer.policyholders_current_sector:
        return _two_float_values(
            insurer.policyholders_current_sector,
            fallback=insurer.policyholders_current,
        )
    policyholders = [0.0, 0.0]
    policyholders[sector_index] = float(insurer.policyholders_current)
    return policyholders


def _insurer_vectors(insurer: Insurer, sector_index: int) -> tuple[list[float], list[float], list[int], list[float]]:
    reserves = _two_float_values(insurer.reserves_current, fallback=0.0)
    policyholders = _policyholder_vector_for_sector(insurer, sector_index)
    claim_counts = _two_int_values(insurer.claims_count_current, fallback=0)
    claim_sums = _two_float_values(insurer.claims_sum_current, fallback=0.0)
    return reserves, policyholders, claim_counts, claim_sums


def _apply_insured_sector(
    insurer: Insurer,
    *,
    sector_index: int,
    premium: float,
    damage: float,
) -> None:
    reserves, policyholders, claim_counts, claim_sums = _insurer_vectors(insurer, sector_index)
    reserves[sector_index] = reserves[sector_index] + premium - damage
    policyholders[sector_index] = policyholders[sector_index] + 1.0
    if damage > 0.0:
        claim_counts[sector_index] = claim_counts[sector_index] + 1
        claim_sums[sector_index] = claim_sums[sector_index] + damage
    insurer.reserves_current = reserves
    insurer.policyholders_current_sector = policyholders
    insurer.policyholders_current = sum(policyholders)
    insurer.claims_count_current = claim_counts
    insurer.claims_sum_current = claim_sums


def apply_vn_settlement_snapshot(
    policyholder: Policyholder,
    insurers: list[Insurer],
    snapshot: VNSettlementSnapshot,
) -> VNSettlementResult:
    """
    Portiert den deterministischen Abrechnungsblock aus Vrvn01 bis Vrvn03.

    Wahl, Praeferenzbildung und Zufallsziehungen bleiben ausserhalb dieses Slices.
    Der Snapshot enthaelt die bereits feststehenden Entscheidungen und Schaeden.
    """

    if policyholder.entity_id != snapshot.policyholder_id:
        raise ValueError(
            "VN settlement snapshot policyholder_id does not match policyholder: "
            f"{snapshot.policyholder_id} != {policyholder.entity_id}"
        )

    insurers_by_id = {insurer.entity_id: insurer for insurer in insurers}
    chosen_insurers: list[int | None] = [None, None]
    insured_values: list[float] = [0.0, 0.0]
    paid_premiums: list[float] = [0.0, 0.0]
    self_damages: list[float] = [0.0, 0.0]
    claim_sums: list[float] = [0.0, 0.0]
    sector_wealth = (
        list(snapshot.previous_wealth_sector)
        if snapshot.previous_wealth_sector is not None
        else [snapshot.previous_wealth, snapshot.previous_wealth]
    )

    for decision in sorted(snapshot.decisions, key=lambda item: item.sector_index):
        sector_index = decision.sector_index
        damage = decision.damage
        claim_sums[sector_index] = damage
        if decision.insured:
            insurer = insurers_by_id.get(decision.insurer_id)
            if insurer is None:
                raise ValueError(f"VN settlement snapshot references unknown insurer: {decision.insurer_id}")
            premium = (
                decision.premium
                if decision.premium is not None
                else _current_sector_premium(insurer, sector_index)
            )
            chosen_insurers[sector_index] = insurer.entity_id
            insured_values[sector_index] = 1.0
            paid_premiums[sector_index] = premium
            _apply_insured_sector(
                insurer,
                sector_index=sector_index,
                premium=premium,
                damage=damage,
            )
        else:
            premium = 0.0
            self_damages[sector_index] = damage
        sector_wealth[sector_index] = sector_wealth[sector_index] - damage - premium

    result = VNSettlementResult(
        chosen_insurer_sector_current=chosen_insurers,
        insured_current_sector=insured_values,
        paid_premium_current=paid_premiums,
        self_damage_current=self_damages,
        claim_sum_current=claim_sums,
        end_wealth_sector_current=sector_wealth,
        end_wealth_current=snapshot.previous_wealth - sum(claim_sums) - sum(paid_premiums),
    )
    policyholder.chosen_insurer_sector_current = result.chosen_insurer_sector_current
    policyholder.chosen_insurer_current = result.chosen_insurer_sector_current[0]
    policyholder.insurer_id = result.chosen_insurer_sector_current[0]
    policyholder.insured_current_sector = result.insured_current_sector
    policyholder.insured_current = result.insured_current_sector[0]
    policyholder.paid_premium_current = result.paid_premium_current
    policyholder.self_damage_current = result.self_damage_current
    policyholder.claim_sum_current = result.claim_sum_current
    policyholder.end_wealth_sector_current = result.end_wealth_sector_current
    policyholder.end_wealth_current = result.end_wealth_current
    return result


def apply_vn_settlement_snapshots(
    policyholders: list[Policyholder],
    insurers: list[Insurer],
    snapshots: list[VNSettlementSnapshot],
) -> list[VNSettlementApplication]:
    """Wendet explizite VN-Settlement-Snapshots deterministisch auf passende VNs an."""

    policyholders_by_id = {policyholder.entity_id: policyholder for policyholder in policyholders}
    applications: list[VNSettlementApplication] = []
    seen_policyholder_ids: set[int] = set()
    for snapshot in snapshots:
        if snapshot.policyholder_id in seen_policyholder_ids:
            raise ValueError(f"duplicate VN settlement snapshot for policyholder: {snapshot.policyholder_id}")
        seen_policyholder_ids.add(snapshot.policyholder_id)
        policyholder = policyholders_by_id.get(snapshot.policyholder_id)
        if policyholder is None:
            raise ValueError(f"VN settlement snapshot references unknown policyholder: {snapshot.policyholder_id}")
        result = apply_vn_settlement_snapshot(policyholder, insurers, snapshot)
        applications.append(VNSettlementApplication(policyholder_id=snapshot.policyholder_id, result=result))
    return applications
