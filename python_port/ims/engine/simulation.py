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


@dataclass(slots=True)
class TwoStepSimulationResult:
    initial_context: SimulationContext
    first_step: SimulationStepResult
    second_context: SimulationContext
    second_step: SimulationStepResult


def _run_loaded_bav_update_step(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
    *,
    use_rng_sample: bool,
) -> SimulationStepResult:
    bav_update = update_bav_central_state(
        context,
        bav,
        insurers,
        policyholders,
        use_rng_sample=use_rng_sample,
    )
    aggregate_snapshot = collect_basic_aggregates(context, bav, insurers, policyholders)
    return SimulationStepResult(
        context=context,
        bav=bav,
        insurers=insurers,
        policyholders=policyholders,
        bav_update=bav_update,
        aggregate_snapshot=aggregate_snapshot,
    )


def run_single_bav_update_step(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
) -> SimulationStepResult:
    loaded = load_scenario(path)

    if initialize_rng:
        ensure_context_rng(loaded.context)

    return _run_loaded_bav_update_step(
        loaded.context,
        loaded.bav,
        loaded.insurers,
        loaded.policyholders,
        use_rng_sample=use_rng_sample,
    )


def run_two_bav_update_steps(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
    second_step_new_period: bool = False,
) -> TwoStepSimulationResult:
    loaded = load_scenario(path)

    if initialize_rng:
        ensure_context_rng(loaded.context)

    initial_context = loaded.context
    first_step = _run_loaded_bav_update_step(
        initial_context,
        loaded.bav,
        loaded.insurers,
        loaded.policyholders,
        use_rng_sample=use_rng_sample,
    )
    if second_step_new_period:
        second_context = initial_context.advanced(period_increment=1, logtime_increment=0, reset_logtime_to=0)
    else:
        second_context = initial_context.advanced(period_increment=0, logtime_increment=1)

    second_step = _run_loaded_bav_update_step(
        second_context,
        loaded.bav,
        loaded.insurers,
        loaded.policyholders,
        use_rng_sample=use_rng_sample,
    )
    return TwoStepSimulationResult(
        initial_context=initial_context,
        first_step=first_step,
        second_context=second_context,
        second_step=second_step,
    )
