from dataclasses import dataclass, field

from ims.engine.context import SimulationContext
from ims.model.entities import Insurer, Policyholder
from ims.model.vn_rules import (
    VNDamageSettlementApplication,
    VNDamageSettlementSnapshot,
    VNSettlementApplication,
    VNSettlementSnapshot,
    apply_vn_damage_settlement_snapshots,
    apply_vn_settlement_snapshots,
)


@dataclass(slots=True)
class VNSettlementPeriodRunResult:
    """Kleines Ergebnis eines expliziten VN-Periodenschritts."""

    period: int
    damage_settlement_applications: list[VNDamageSettlementApplication] = field(default_factory=list)
    settlement_applications: list[VNSettlementApplication] = field(default_factory=list)

    @property
    def total_settlement_applications(self) -> int:
        return len(self.damage_settlement_applications) + len(self.settlement_applications)

    @property
    def total_damage_settlement_applications(self) -> int:
        return len(self.damage_settlement_applications)


def run_vn_settlement_period(
    context: SimulationContext,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
    *,
    damage_settlement_snapshots: list[VNDamageSettlementSnapshot] | None = None,
    settlement_snapshots: list[VNSettlementSnapshot] | None = None,
) -> VNSettlementPeriodRunResult:
    """
    Wendet explizite VN-Schaden- und Settlement-Snapshots fuer eine Periode an.

    Dieser Runner ist bewusst kein historischer PlanVN-Scheduler. Er stellt nur den
    portierten deterministischen Schaden- und Abrechnungskern als kleinen
    Periodenschritt bereit.
    """

    damage_settlement_applications = apply_vn_damage_settlement_snapshots(
        policyholders,
        insurers,
        damage_settlement_snapshots or [],
    )
    applications = apply_vn_settlement_snapshots(
        policyholders,
        insurers,
        settlement_snapshots or [],
    )
    return VNSettlementPeriodRunResult(
        period=context.period,
        damage_settlement_applications=damage_settlement_applications,
        settlement_applications=applications,
    )
