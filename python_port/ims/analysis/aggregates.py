from dataclasses import dataclass

from ims.engine.context import SimulationContext
from ims.model.entities import BAV, Insurer, Policyholder


@dataclass(slots=True)
class AggregateSnapshot:
    """Konservativer Snapshot weniger eindeutig ableitbarer Kennzahlen."""

    period: int
    logtime: int
    active_insurers: int
    active_policyholders: int
    assigned_policyholders: int
    unassigned_policyholders: int


def collect_basic_aggregates(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
) -> AggregateSnapshot:
    """Collect a first, strongly simplified aggregate snapshot.

    The passed ``bav`` is currently only a central aggregation reference to keep
    the function signature aligned with later, richer vertical slices.
    """

    _ = bav
    active_insurers = sum(1 for insurer in insurers if insurer.active)
    active_policyholders = sum(1 for policyholder in policyholders if policyholder.active)
    assigned_policyholders = sum(
        1 for policyholder in policyholders if policyholder.insurer_id is not None
    )
    unassigned_policyholders = sum(
        1 for policyholder in policyholders if policyholder.insurer_id is None
    )
    return AggregateSnapshot(
        period=context.period,
        logtime=context.logtime,
        active_insurers=active_insurers,
        active_policyholders=active_policyholders,
        assigned_policyholders=assigned_policyholders,
        unassigned_policyholders=unassigned_policyholders,
    )
