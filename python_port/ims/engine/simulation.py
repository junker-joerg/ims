from dataclasses import dataclass
from pathlib import Path

from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
from ims.engine.context import SimulationContext, ensure_context_rng
from ims.io.scenario_loader import load_scenario
from ims.model.bav_updates import BAVUpdateResult, update_bav_central_state
from ims.model.entities import BAV, Insurer, Policyholder


@dataclass(slots=True)
class SimulationStepResult:
    context: SimulationContext
    bav: BAV
    insurers: list[Insurer]
    policyholders: list[Policyholder]
    bav_update: BAVUpdateResult
    aggregate_snapshot: AggregateSnapshot


def run_single_bav_update_step(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
) -> SimulationStepResult:
    loaded = load_scenario(path)

    if initialize_rng:
        ensure_context_rng(loaded.context)

    bav_update = update_bav_central_state(
        loaded.context,
        loaded.bav,
        loaded.insurers,
        loaded.policyholders,
        use_rng_sample=use_rng_sample,
    )
    aggregate_snapshot = collect_basic_aggregates(
        loaded.context,
        loaded.bav,
        loaded.insurers,
        loaded.policyholders,
    )
    return SimulationStepResult(
        context=loaded.context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        bav_update=bav_update,
        aggregate_snapshot=aggregate_snapshot,
    )
