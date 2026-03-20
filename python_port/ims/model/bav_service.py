from dataclasses import dataclass

from ims.engine.context import SimulationContext
from ims.model.entities import (
    BAV,
    BAVForeignInfoInsurer,
    BAVForeignInfoPolicyholder,
    Insurer,
    Policyholder,
)


@dataclass(slots=True)
class BAVForeignInfoResult:
    """Kleines Ergebnisobjekt für den portierten Frmdinf-Teilschnitt."""

    insurer: BAVForeignInfoInsurer
    policyholder: BAVForeignInfoPolicyholder


def _zero_foreign_info(bav: BAV) -> BAVForeignInfoResult:
    bav.service_state.insurer = BAVForeignInfoInsurer()
    bav.service_state.policyholder = BAVForeignInfoPolicyholder()
    return BAVForeignInfoResult(
        insurer=bav.service_state.insurer,
        policyholder=bav.service_state.policyholder,
    )


def initialize_bav_first_run(context: SimulationContext, bav: BAV) -> None:
    """
    Setzt beim ersten historischen Startlauf die kleinen Fremdinformationsfelder auf Null.

    Dieser Slice bleibt absichtlich eng und modelliert keine vollständige historische
    Initialisierungslogik über weitere Status- oder Schockvektoren.
    """

    if context.run_index <= 1 and context.period <= 1:
        _zero_foreign_info(bav)


def initialize_bav_followup_run(context: SimulationContext, bav: BAV) -> None:
    """
    Setzt beim ersten Periodenschritt nachfolgender Läufe dieselben Fremdinformationen auf Null.
    """

    if context.run_index > 1 and context.period <= 1:
        _zero_foreign_info(bav)


def compute_basic_foreign_info(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
) -> BAVForeignInfoResult:
    """
    Portiert einen kleinen, klar begrenzten Frmdinf-Teilschnitt.

    Portiert werden nur Durchschnitts-/Extremwerte auf Basis kleiner Vorperioden-
    Snapshots. Es gibt in diesem PR keine vollständige historische Frmdinf-Portierung,
    keine Aktivierungsschocklogik und keine Aussage historischer Vollgleichheit.
    """

    if context.period <= 1:
        return _zero_foreign_info(bav)

    active_insurers = [insurer for insurer in insurers if insurer.active]
    active_policyholders = [policyholder for policyholder in policyholders if policyholder.active]

    if active_insurers:
        count_insurers = len(active_insurers)
        dp = sum(insurer.premiums_prev for insurer in active_insurers) / count_insurers
        dw = sum(insurer.advertising_prev for insurer in active_insurers) / count_insurers
        pm = min(insurer.premiums_prev for insurer in active_insurers)
        wm = max(insurer.advertising_prev for insurer in active_insurers)
        market_leader = max(active_insurers, key=lambda insurer: insurer.reserves_prev)
        mp = market_leader.premiums_prev
        mw = market_leader.advertising_prev
    else:
        dp = dw = pm = wm = mp = mw = 0.0

    if active_policyholders:
        dg = sum(policyholder.insured_prev for policyholder in active_policyholders) / len(active_policyholders)
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
    return BAVForeignInfoResult(
        insurer=bav.service_state.insurer,
        policyholder=bav.service_state.policyholder,
    )
