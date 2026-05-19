from dataclasses import dataclass

from ims.engine.context import SimulationContext
from ims.model.entities import (
    BAV,
    BAVActivityState,
    BAVForeignInfoInsurer,
    BAVForeignInfoPolicyholder,
    BAVServiceComputationMeta,
    Insurer,
    Policyholder,
)


SECTOR_COUNT = 2


@dataclass(slots=True)
class BAVForeignInfoResult:
    """Kleines Ergebnisobjekt fuer den portierten Frmdinf-Teilschnitt."""

    insurer: BAVForeignInfoInsurer
    policyholder: BAVForeignInfoPolicyholder


def _reset_service_state_for_zero_foreign_info(bav: BAV) -> BAVForeignInfoResult:
    bav.service_state.insurer = BAVForeignInfoInsurer()
    bav.service_state.policyholder = BAVForeignInfoPolicyholder()
    bav.service_state.computation_meta = BAVServiceComputationMeta(
        used_previous_period_values=False,
        foreign_info_available=False,
        leader_insurer_id=None,
        leader_insurer_ids=[None, None],
    )
    return BAVForeignInfoResult(
        insurer=bav.service_state.insurer,
        policyholder=bav.service_state.policyholder,
    )


def _two_sector_values(values: list[float], scalar: float) -> list[float]:
    if not values:
        return [float(scalar), float(scalar)]
    normalized = [float(value) for value in values[:SECTOR_COUNT]]
    if len(normalized) == 1:
        return [normalized[0], normalized[0]]
    return normalized


def _sector_average(items: list[Insurer], value_name: str, scalar_name: str) -> list[float]:
    if not items:
        return [0.0, 0.0]
    return [
        sum(_two_sector_values(getattr(item, value_name), getattr(item, scalar_name))[sector] for item in items)
        / len(items)
        for sector in range(SECTOR_COUNT)
    ]


def _sector_min_positive(items: list[Insurer], value_name: str, scalar_name: str) -> list[float]:
    result: list[float] = []
    for sector in range(SECTOR_COUNT):
        values = [
            _two_sector_values(getattr(item, value_name), getattr(item, scalar_name))[sector]
            for item in items
            if _two_sector_values(getattr(item, value_name), getattr(item, scalar_name))[sector] > 0.0
        ]
        result.append(min(values) if values else 0.0)
    return result


def _sector_max(items: list[Insurer], value_name: str, scalar_name: str) -> list[float]:
    if not items:
        return [0.0, 0.0]
    return [
        max(_two_sector_values(getattr(item, value_name), getattr(item, scalar_name))[sector] for item in items)
        for sector in range(SECTOR_COUNT)
    ]


def _sector_market_leaders(items: list[Insurer]) -> list[Insurer | None]:
    leaders: list[Insurer | None] = []
    for sector in range(SECTOR_COUNT):
        leader = max(
            items,
            key=lambda item: _two_sector_values(item.reserves_prev_sector, item.reserves_prev)[sector],
            default=None,
        )
        leaders.append(leader)
    return leaders


def _policyholder_sector_average(policyholders: list[Policyholder]) -> list[float]:
    if not policyholders:
        return [0.0, 0.0]
    return [
        sum(_two_sector_values(policyholder.insured_prev_sector, policyholder.insured_prev)[sector] for policyholder in policyholders)
        / len(policyholders)
        for sector in range(SECTOR_COUNT)
    ]


def initialize_bav_first_run(context: SimulationContext, bav: BAV) -> None:
    """
    Setzt beim ersten historischen Startlauf die bislang portierten Fremdinformationsfelder auf Null.
    """

    if context.run_index <= 1 and context.period <= 1:
        _reset_service_state_for_zero_foreign_info(bav)


def initialize_bav_followup_run(context: SimulationContext, bav: BAV) -> None:
    """
    Setzt beim ersten Periodenschritt nachfolgender Laeufe dieselben Fremdinformationen auf Null.
    """

    if context.run_index > 1 and context.period <= 1:
        _reset_service_state_for_zero_foreign_info(bav)


def refresh_bav_activity_state(bav: BAV, insurers: list[Insurer], policyholders: list[Policyholder]) -> None:
    """
    Aktualisiert explizit Vorperioden- und aktuelle Aktivitaetsmengen im BAV-Servicezustand.
    """

    active_insurer_ids_prev = [insurer.entity_id for insurer in insurers if insurer.active_prev]
    active_policyholder_ids_prev = [policyholder.entity_id for policyholder in policyholders if policyholder.active_prev]
    active_insurer_ids_current = [insurer.entity_id for insurer in insurers if insurer.active]
    active_policyholder_ids_current = [policyholder.entity_id for policyholder in policyholders if policyholder.active]

    bav.service_state.activity_state = BAVActivityState(
        active_insurer_ids_prev=active_insurer_ids_prev,
        active_policyholder_ids_prev=active_policyholder_ids_prev,
        active_insurer_ids_current=active_insurer_ids_current,
        active_policyholder_ids_current=active_policyholder_ids_current,
        active_insurer_count_prev=len(active_insurer_ids_prev),
        active_policyholder_count_prev=len(active_policyholder_ids_prev),
        active_insurer_count_current=len(active_insurer_ids_current),
        active_policyholder_count_current=len(active_policyholder_ids_current),
    )


def compute_extended_foreign_info(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
) -> BAVForeignInfoResult:
    """
    Portiert einen erweiterten, aber weiterhin begrenzten Frmdinf-Kern.

    Im Mittelpunkt stehen Vorperiodenwerte und explizite Vorperiodenaktivitaet. Dieser
    PR modelliert weder vollstaendige Aktivierungsschock-Semantik noch Agrsich oder
    vollstaendige VU-/VN-Regelportierungen.
    """

    refresh_bav_activity_state(bav, insurers, policyholders)

    if context.period <= 1:
        return _reset_service_state_for_zero_foreign_info(bav)

    previous_active_insurers = [insurer for insurer in insurers if insurer.active_prev]
    previous_active_policyholders = [policyholder for policyholder in policyholders if policyholder.active_prev]

    if previous_active_insurers:
        dp = _sector_average(previous_active_insurers, "premiums_prev_sector", "premiums_prev")
        dw = _sector_average(previous_active_insurers, "advertising_prev_sector", "advertising_prev")
        pm = _sector_min_positive(previous_active_insurers, "premiums_prev_sector", "premiums_prev")
        wm = _sector_max(previous_active_insurers, "advertising_prev_sector", "advertising_prev")
        market_leaders = _sector_market_leaders(previous_active_insurers)
        leader_insurer_ids = [leader.entity_id if leader is not None else None for leader in market_leaders]
        mp = [
            _two_sector_values(leader.premiums_prev_sector, leader.premiums_prev)[sector] if leader is not None else 0.0
            for sector, leader in enumerate(market_leaders)
        ]
        mw = [
            _two_sector_values(leader.advertising_prev_sector, leader.advertising_prev)[sector] if leader is not None else 0.0
            for sector, leader in enumerate(market_leaders)
        ]
    else:
        dp = [0.0, 0.0]
        dw = [0.0, 0.0]
        pm = [0.0, 0.0]
        wm = [0.0, 0.0]
        mp = [0.0, 0.0]
        mw = [0.0, 0.0]
        leader_insurer_ids = [None, None]

    if previous_active_policyholders:
        dg = _policyholder_sector_average(previous_active_policyholders)
    else:
        dg = [0.0, 0.0]

    bav.service_state.insurer = BAVForeignInfoInsurer(
        dp=dp,
        dw=dw,
        pm=pm,
        wm=wm,
        mp=mp,
        mw=mw,
    )
    bav.service_state.policyholder = BAVForeignInfoPolicyholder(dg=dg)
    bav.service_state.computation_meta = BAVServiceComputationMeta(
        used_previous_period_values=True,
        foreign_info_available=True,
        leader_insurer_id=leader_insurer_ids[0],
        leader_insurer_ids=leader_insurer_ids,
    )
    return BAVForeignInfoResult(
        insurer=bav.service_state.insurer,
        policyholder=bav.service_state.policyholder,
    )


def compute_basic_foreign_info(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
) -> BAVForeignInfoResult:
    """
    Kompatibilitaetsname fuer den frueheren kleineren Slice.

    Der Funktionsname bleibt vorerst erhalten, delegiert aber auf den erweiterten
    Frmdinf-Kern dieses PRs.
    """

    return compute_extended_foreign_info(context, bav, insurers, policyholders)
