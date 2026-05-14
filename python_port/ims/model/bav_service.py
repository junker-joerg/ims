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


@dataclass(slots=True)
class BAVForeignInfoResult:
    """Kleines Ergebnisobjekt für den portierten Frmdinf-Teilschnitt."""

    insurer: BAVForeignInfoInsurer
    policyholder: BAVForeignInfoPolicyholder


def _reset_service_state_for_zero_foreign_info(bav: BAV) -> BAVForeignInfoResult:
    bav.service_state.insurer = BAVForeignInfoInsurer()
    bav.service_state.policyholder = BAVForeignInfoPolicyholder()
    bav.service_state.computation_meta = BAVServiceComputationMeta(
        used_previous_period_values=False,
        foreign_info_available=False,
        leader_insurer_id=None,
    )
    return BAVForeignInfoResult(
        insurer=bav.service_state.insurer,
        policyholder=bav.service_state.policyholder,
    )


def initialize_bav_first_run(context: SimulationContext, bav: BAV) -> None:
    """
    Setzt beim ersten historischen Startlauf die bislang portierten Fremdinformationsfelder auf Null.
    """

    if context.run_index <= 1 and context.period <= 1:
        _reset_service_state_for_zero_foreign_info(bav)


def initialize_bav_followup_run(context: SimulationContext, bav: BAV) -> None:
    """
    Setzt beim ersten Periodenschritt nachfolgender Läufe dieselben Fremdinformationen auf Null.
    """

    if context.run_index > 1 and context.period <= 1:
        _reset_service_state_for_zero_foreign_info(bav)


def refresh_bav_activity_state(bav: BAV, insurers: list[Insurer], policyholders: list[Policyholder]) -> None:
    """
    Aktualisiert explizit Vorperioden- und aktuelle Aktivitätsmengen im BAV-Servicezustand.
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

    Im Mittelpunkt stehen Vorperiodenwerte und explizite Vorperiodenaktivität. Dieser
    PR modelliert weder vollständige Aktivierungsschock-Semantik noch Agrsich oder
    vollständige VU-/VN-Regelportierungen.
    """

    refresh_bav_activity_state(bav, insurers, policyholders)

    if context.period <= 1:
        return _reset_service_state_for_zero_foreign_info(bav)

    previous_active_insurers = [insurer for insurer in insurers if insurer.active_prev]
    previous_active_policyholders = [policyholder for policyholder in policyholders if policyholder.active_prev]

    leader_insurer_id: int | None = None
    if previous_active_insurers:
        count_insurers = len(previous_active_insurers)
        dp = sum(insurer.premiums_prev for insurer in previous_active_insurers) / count_insurers
        dw = sum(insurer.advertising_prev for insurer in previous_active_insurers) / count_insurers
        pm = min(insurer.premiums_prev for insurer in previous_active_insurers)
        wm = max(insurer.advertising_prev for insurer in previous_active_insurers)
        market_leader = max(previous_active_insurers, key=lambda insurer: insurer.reserves_prev)
        leader_insurer_id = market_leader.entity_id
        mp = market_leader.premiums_prev
        mw = market_leader.advertising_prev
    else:
        dp = dw = pm = wm = mp = mw = 0.0

    if previous_active_policyholders:
        dg = sum(policyholder.insured_prev for policyholder in previous_active_policyholders) / len(previous_active_policyholders)
    else:
        dg = 0.0

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
        leader_insurer_id=leader_insurer_id,
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
    Kompatibilitätsname für den früheren kleineren Slice.

    Der Funktionsname bleibt vorerst erhalten, delegiert aber auf den erweiterten
    Frmdinf-Kern dieses PRs.
    """

    return compute_extended_foreign_info(context, bav, insurers, policyholders)
