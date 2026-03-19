from dataclasses import dataclass

from ims.engine.context import SimulationContext
from ims.engine.rng import rand_uniform_0_1
from ims.model.entities import BAV, Insurer, Policyholder


@dataclass(slots=True)
class BAVUpdateResult:
    period: int
    logtime: int
    active_insurer_count: int
    active_policyholder_count: int
    sample_token: float | None


def update_bav_central_state(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
    *,
    use_rng_sample: bool = False,
) -> BAVUpdateResult:
    active_insurer_count = sum(1 for insurer in insurers if insurer.active)
    active_policyholder_count = sum(
        1 for policyholder in policyholders if policyholder.active
    )

    bav.last_update_period = context.period
    bav.last_update_logtime = context.logtime
    bav.last_active_insurer_count = active_insurer_count
    bav.last_active_policyholder_count = active_policyholder_count

    if use_rng_sample:
        if context.rng is None:
            raise ValueError("context.rng is required when use_rng_sample=True")
        bav.last_sample_token = rand_uniform_0_1(context.rng)

    return BAVUpdateResult(
        period=bav.last_update_period,
        logtime=bav.last_update_logtime,
        active_insurer_count=bav.last_active_insurer_count,
        active_policyholder_count=bav.last_active_policyholder_count,
        sample_token=bav.last_sample_token,
    )
