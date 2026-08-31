from __future__ import annotations

from dataclasses import dataclass

from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_100_PERIOD_STATE_POLICY_ID,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
)
from ims.model.agrsich_export import ExportRow, ExportTable


HISTORICAL_PERIODS_PER_RUN = 100
REPEAT_CORPUS_POLICY_ID = "vdefmd6-modern-independent-100-period-runs-v1"


@dataclass(frozen=True, slots=True)
class Vdefmd6RepeatCorpusResult:
    base_seed: int
    run_seeds: tuple[int, ...]
    runs: tuple[Vdefmd6PreShockRunResult, ...]
    export_tables: tuple[ExportTable, ...]
    periods_per_run: int = HISTORICAL_PERIODS_PER_RUN
    policy_id: str = REPEAT_CORPUS_POLICY_ID

    @property
    def run_count(self) -> int:
        return len(self.runs)

    @property
    def result_row_count(self) -> int:
        return self.run_count * self.periods_per_run


def run_vdefmd6_100_period_repetitions(
    *,
    base_seed: int,
    run_count: int,
) -> Vdefmd6RepeatCorpusResult:
    if type(base_seed) is not int or base_seed < 0:
        raise ValueError("Vdefmd6 repeat base_seed must be a non-negative integer")
    if type(run_count) is not int or not 1 <= run_count <= 100:
        raise ValueError("Vdefmd6 repeat run_count must be between 1 and 100")
    runs = tuple(
        run_vdefmd6_100_periods(base_seed=base_seed + run_index)
        for run_index in range(run_count)
    )
    return build_vdefmd6_100_period_repeat_corpus(
        runs,
        base_seed=base_seed,
    )


def build_vdefmd6_100_period_repeat_corpus(
    runs: tuple[Vdefmd6PreShockRunResult, ...],
    *,
    base_seed: int,
) -> Vdefmd6RepeatCorpusResult:
    if not runs:
        raise ValueError("Vdefmd6 repeat corpus requires at least one run")
    expected_seeds = tuple(base_seed + index for index in range(len(runs)))
    for run_index, (run, expected_seed) in enumerate(
        zip(runs, expected_seeds, strict=True),
        start=1,
    ):
        if run.base_seed != expected_seed:
            raise ValueError(f"Vdefmd6 repeat run {run_index} seed differs")
        if run.max_periods != HISTORICAL_PERIODS_PER_RUN:
            raise ValueError(f"Vdefmd6 repeat run {run_index} exceeds 100 periods")
        if run.state_policy_id != VDEFMD6_100_PERIOD_STATE_POLICY_ID:
            raise ValueError(f"Vdefmd6 repeat run {run_index} policy differs")
        if tuple(item.period for item in run.period_results) != tuple(range(2, 101)):
            raise ValueError(f"Vdefmd6 repeat run {run_index} periods differ")
        if _crosses_closed_boundary(run):
            raise ValueError(f"Vdefmd6 repeat run {run_index} crossed a closed boundary")
    return Vdefmd6RepeatCorpusResult(
        base_seed=base_seed,
        run_seeds=expected_seeds,
        runs=runs,
        export_tables=_concatenate_export_tables(runs),
    )


def _concatenate_export_tables(
    runs: tuple[Vdefmd6PreShockRunResult, ...],
) -> tuple[ExportTable, ...]:
    first_tables = _all_tables(runs[0])
    filenames = tuple(table.spec.filename.lower() for table in first_tables)
    if len(filenames) != len(set(filenames)):
        raise ValueError("Vdefmd6 repeat export filenames must be unique")
    grouped = {filename: [] for filename in filenames}
    specifications = {
        table.spec.filename.lower(): (table.spec, table.header)
        for table in first_tables
    }
    for run_index, run in enumerate(runs, start=1):
        tables = _all_tables(run)
        by_filename = {table.spec.filename.lower(): table for table in tables}
        if tuple(by_filename) != filenames:
            raise ValueError(f"Vdefmd6 repeat run {run_index} export set differs")
        for filename in filenames:
            table = by_filename[filename]
            expected_spec, expected_header = specifications[filename]
            if table.spec != expected_spec or table.header != expected_header:
                raise ValueError(
                    f"Vdefmd6 repeat run {run_index} export identity differs: {filename}"
                )
            periods = [int(row.values[0]) for row in table.rows]
            if periods != list(range(1, 101)):
                raise ValueError(
                    f"Vdefmd6 repeat run {run_index} export periods differ: {filename}"
                )
            for row in table.rows:
                local_period = int(row.values[0])
                result_row = (
                    (run_index - 1) * HISTORICAL_PERIODS_PER_RUN + local_period
                )
                grouped[filename].append(
                    ExportRow(values=[result_row, *row.values[1:]])
                )
    return tuple(
        ExportTable(
            spec=specifications[filename][0],
            header=specifications[filename][1],
            rows=grouped[filename],
        )
        for filename in filenames
    )


def _all_tables(result: Vdefmd6PreShockRunResult) -> tuple[ExportTable, ...]:
    return (
        result.vu14_export_table,
        *result.vu_aggregate_export_tables,
        *result.vn_rule_group_1_export_tables,
        *result.vn_rule_group_2_export_tables,
        *result.vn_aggregate_export_tables,
    )


def _crosses_closed_boundary(result: Vdefmd6PreShockRunResult) -> bool:
    return bool(
        result.legacy_rows_used_as_generation_input
        or result.writes_performed
        or result.scheduler_started
        or result.simulation_performed
        or result.historical_same_slot_order_claimed
        or result.historical_rng_equality_claimed
        or result.historical_full_equality_claimed
    )
