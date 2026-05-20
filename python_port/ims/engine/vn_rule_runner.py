from dataclasses import dataclass, field

from ims.engine.context import SimulationContext
from ims.model.entities import Insurer, Policyholder
from ims.model.vn_rules import (
    VNSettlementApplication,
    VNSettlementSnapshot,
    apply_vn_settlement_snapshots,
)


@dataclass(slots=True)
class VNSettlementPeriodRunResult:
    """Kleines Ergebnis eines expliziten VN-Settlement-Periodenschritts."""

    period: int
    settlement_applications: list[VNSettlementApplication] = field(default_factory=list)

    @property
    def total_settlement_applications(self) -> int:
        return len(self.settlement_applications)


def run_vn_settlement_period(
    context: SimulationContext,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
    *,
    settlement_snapshots: list[VNSettlementSnapshot] | None = None,
) -> VNSettlementPeriodRunResult:
    """
    Wendet explizite VN-Settlement-Snapshots fuer eine Periode an.

    Dieser Runner ist bewusst kein historischer PlanVN-Scheduler. Er stellt nur den
    portierten deterministischen Abrechnungskern als kleinen Periodenschritt bereit.
    """

    applications = apply_vn_settlement_snapshots(
        policyholders,
        insurers,
        settlement_snapshots or [],
    )
    return VNSettlementPeriodRunResult(
        period=context.period,
        settlement_applications=applications,
    )
