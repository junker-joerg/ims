from collections import Counter
from dataclasses import dataclass

from ims.engine.context import SimulationContext
from ims.model.entities import BAV, BAVAggregateState, Insurer, Policyholder


@dataclass(slots=True)
class AggregateRecord:
    """Ein kleiner In-Memory-Record für einen portierten Agrsich-Aggregatstand."""

    subject_type: str
    aggregate_level: str
    aggregate_key: int | str | None
    entity_ids: list[int]
    metrics: dict[str, float | int | None]


@dataclass(slots=True)
class AgrsichResult:
    """Ergebnis des kleinen, portierten Agrsich-Kerns."""

    insurer_records: list[AggregateRecord]
    policyholder_records: list[AggregateRecord]


def _count_by(items: list[Insurer] | list[Policyholder], attr_name: str) -> dict[int | None, int]:
    counts: dict[int | None, int] = {}
    for item in items:
        key = getattr(item, attr_name)
        counts[key] = counts.get(key, 0) + 1
    return counts


def refresh_bav_aggregate_state(
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
    *,
    period: int,
) -> None:
    """Aktualisiert den kleinen Agrsich-Aggregatzustand auf Basis aktueller Aktivität."""

    active_insurers = [insurer for insurer in insurers if insurer.active]
    active_policyholders = [policyholder for policyholder in policyholders if policyholder.active]

    bav.service_state.aggregate_state = BAVAggregateState(
        active_insurer_ids_current=[insurer.entity_id for insurer in active_insurers],
        active_policyholder_ids_current=[policyholder.entity_id for policyholder in active_policyholders],
        insurer_rule_counts=_count_by(active_insurers, "rule_id"),
        insurer_rule_class_counts=_count_by(active_insurers, "rule_class"),
        policyholder_rule_counts=_count_by(active_policyholders, "rule_id"),
        policyholder_rule_class_counts=_count_by(active_policyholders, "rule_class"),
        last_agrsich_period=period,
    )


def _mean(values: list[float | int]) -> float:
    return float(sum(values)) / len(values) if values else 0.0


def _mode_smallest(values: list[int | None]) -> int | None:
    if not values:
        return None
    counts = Counter(values)
    max_count = max(counts.values())
    winners = [value for value, count in counts.items() if count == max_count]
    non_none = [value for value in winners if value is not None]
    if non_none:
        return min(non_none)
    return None


def _reserve_sector(item: Insurer, index: int) -> float:
    reserves = item.reserves_current
    if isinstance(reserves, list):
        if len(reserves) > index:
            return float(reserves[index])
        if reserves:
            return float(reserves[-1])
        return 0.0
    return float(reserves)


def _insurer_metrics(items: list[Insurer], *, average: bool) -> dict[str, float | int | None]:
    if not items:
        return {
            "premium_1": 0.0,
            "advertising_1": 0.0,
            "reserves_1": 0.0,
            "policyholders_1": 0.0,
            "claims_count_1": 0.0,
            "claims_sum_1": 0.0,
            "premium_2": 0.0,
            "advertising_2": 0.0,
            "reserves_2": 0.0,
            "policyholders_2": 0.0,
            "claims_count_2": 0.0,
            "claims_sum_2": 0.0,
            "reserves": 0.0,
        }
    if average:
        return {
            "premium_1": _mean([item.premiums_current for item in items]),
            "advertising_1": _mean([item.advertising_current for item in items]),
            "reserves_1": _mean([_reserve_sector(item, 0) for item in items]),
            "policyholders_1": _mean([item.policyholders_current for item in items]),
            "claims_count_1": _mean([item.claims_count_current[0] for item in items]),
            "claims_sum_1": _mean([item.claims_sum_current[0] for item in items]),
            "premium_2": _mean([item.premiums_current for item in items]),
            "advertising_2": _mean([item.advertising_current for item in items]),
            "reserves_2": _mean([_reserve_sector(item, 1) for item in items]),
            "policyholders_2": _mean([item.policyholders_current for item in items]),
            "claims_count_2": _mean([item.claims_count_current[1] for item in items]),
            "claims_sum_2": _mean([item.claims_sum_current[1] for item in items]),
            "reserves": _mean([_reserve_sector(item, 0) for item in items]),
        }
    item = items[0]
    return {
        "premium_1": item.premiums_current,
        "advertising_1": item.advertising_current,
        "reserves_1": _reserve_sector(item, 0),
        "policyholders_1": item.policyholders_current,
        "claims_count_1": item.claims_count_current[0],
        "claims_sum_1": item.claims_sum_current[0],
        "premium_2": item.premiums_current,
        "advertising_2": item.advertising_current,
        "reserves_2": _reserve_sector(item, 1),
        "policyholders_2": item.policyholders_current,
        "claims_count_2": item.claims_count_current[1],
        "claims_sum_2": item.claims_sum_current[1],
        "reserves": _reserve_sector(item, 0),
    }


def _policyholder_metrics(items: list[Policyholder], *, average: bool) -> dict[str, float | int | None]:
    if not items:
        return {
            "paid_premium_1": 0.0,
            "self_damage_1": 0.0,
            "coverage_1": 0.0,
            "chosen_insurer_1": None,
            "claim_sum_1": 0.0,
            "paid_premium_2": 0.0,
            "self_damage_2": 0.0,
            "coverage_2": 0.0,
            "chosen_insurer_2": None,
            "claim_sum_2": 0.0,
            "end_wealth": 0.0,
        }
    if average:
        mode_value = _mode_smallest([item.chosen_insurer_current for item in items])
        return {
            "paid_premium_1": _mean([item.paid_premium_current[0] for item in items]),
            "self_damage_1": _mean([item.self_damage_current[0] for item in items]),
            "coverage_1": _mean([item.insured_current for item in items]),
            "chosen_insurer_1": mode_value,
            "claim_sum_1": _mean([item.claim_sum_current[0] for item in items]),
            "paid_premium_2": _mean([item.paid_premium_current[1] for item in items]),
            "self_damage_2": _mean([item.self_damage_current[1] for item in items]),
            "coverage_2": _mean([item.insured_current for item in items]),
            "chosen_insurer_2": mode_value,
            "claim_sum_2": _mean([item.claim_sum_current[1] for item in items]),
            "end_wealth": _mean([item.end_wealth_current for item in items]),
        }
    item = items[0]
    return {
        "paid_premium_1": item.paid_premium_current[0],
        "self_damage_1": item.self_damage_current[0],
        "coverage_1": item.insured_current,
        "chosen_insurer_1": item.chosen_insurer_current,
        "claim_sum_1": item.claim_sum_current[0],
        "paid_premium_2": item.paid_premium_current[1],
        "self_damage_2": item.self_damage_current[1],
        "coverage_2": item.insured_current,
        "chosen_insurer_2": item.chosen_insurer_current,
        "claim_sum_2": item.claim_sum_current[1],
        "end_wealth": item.end_wealth_current,
    }


def _build_agrsich_records(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
) -> AgrsichResult:
    refresh_bav_aggregate_state(bav, insurers, policyholders, period=context.period)

    active_insurers = [insurer for insurer in insurers if insurer.active]
    active_policyholders = [policyholder for policyholder in policyholders if policyholder.active]

    insurer_records: list[AggregateRecord] = []
    policyholder_records: list[AggregateRecord] = []

    for insurer in active_insurers:
        insurer_records.append(
            AggregateRecord(
                subject_type="insurer",
                aggregate_level="I",
                aggregate_key=insurer.entity_id,
                entity_ids=[insurer.entity_id],
                metrics=_insurer_metrics([insurer], average=False),
            )
        )

    insurer_by_rule: dict[int | None, list[Insurer]] = {}
    insurer_by_class: dict[int | None, list[Insurer]] = {}
    for insurer in active_insurers:
        insurer_by_rule.setdefault(insurer.rule_id, []).append(insurer)
        insurer_by_class.setdefault(insurer.rule_class, []).append(insurer)

    for key, items in sorted(insurer_by_rule.items(), key=lambda entry: (entry[0] is None, entry[0])):
        insurer_records.append(AggregateRecord("insurer", "II", key, [item.entity_id for item in items], _insurer_metrics(items, average=True)))
    for key, items in sorted(insurer_by_class.items(), key=lambda entry: (entry[0] is None, entry[0])):
        insurer_records.append(AggregateRecord("insurer", "III", key, [item.entity_id for item in items], _insurer_metrics(items, average=True)))
    insurer_records.append(AggregateRecord("insurer", "IV", "all", [item.entity_id for item in active_insurers], _insurer_metrics(active_insurers, average=True)))

    for policyholder in active_policyholders:
        policyholder_records.append(
            AggregateRecord(
                subject_type="policyholder",
                aggregate_level="I",
                aggregate_key=policyholder.entity_id,
                entity_ids=[policyholder.entity_id],
                metrics=_policyholder_metrics([policyholder], average=False),
            )
        )

    policyholder_by_rule: dict[int | None, list[Policyholder]] = {}
    policyholder_by_class: dict[int | None, list[Policyholder]] = {}
    for policyholder in active_policyholders:
        policyholder_by_rule.setdefault(policyholder.rule_id, []).append(policyholder)
        policyholder_by_class.setdefault(policyholder.rule_class, []).append(policyholder)

    for key, items in sorted(policyholder_by_rule.items(), key=lambda entry: (entry[0] is None, entry[0])):
        policyholder_records.append(AggregateRecord("policyholder", "II", key, [item.entity_id for item in items], _policyholder_metrics(items, average=True)))
    for key, items in sorted(policyholder_by_class.items(), key=lambda entry: (entry[0] is None, entry[0])):
        policyholder_records.append(AggregateRecord("policyholder", "III", key, [item.entity_id for item in items], _policyholder_metrics(items, average=True)))
    policyholder_records.append(AggregateRecord("policyholder", "IV", "all", [item.entity_id for item in active_policyholders], _policyholder_metrics(active_policyholders, average=True)))

    return AgrsichResult(insurer_records=insurer_records, policyholder_records=policyholder_records)


def collect_basic_agrsich_records(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
) -> AgrsichResult:
    """Kompatibler Einstieg für den bisherigen Agrsich-Slice."""

    return _build_agrsich_records(context, bav, insurers, policyholders)


def collect_extended_agrsich_records(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
) -> AgrsichResult:
    """
    Erweitert den portierten Agrsich-Kern um breitere Messgrößen für Exportrepräsentationen.
    """

    return _build_agrsich_records(context, bav, insurers, policyholders)
