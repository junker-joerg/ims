from dataclasses import replace

import pytest

from ims.engine.vdefmd6_repeat_corpus import (
    HISTORICAL_PERIODS_PER_RUN,
    REPEAT_CORPUS_POLICY_ID,
    build_vdefmd6_100_period_repeat_corpus,
    run_vdefmd6_100_period_repetitions,
)


@pytest.fixture(scope="module")
def repeat_corpus():
    return run_vdefmd6_100_period_repetitions(base_seed=20260001, run_count=3)


def test_repeat_corpus_keeps_three_independent_100_period_runs(repeat_corpus) -> None:
    assert repeat_corpus.policy_id == REPEAT_CORPUS_POLICY_ID
    assert repeat_corpus.run_count == 3
    assert repeat_corpus.periods_per_run == HISTORICAL_PERIODS_PER_RUN
    assert repeat_corpus.result_row_count == 300
    assert repeat_corpus.run_seeds == (20260001, 20260002, 20260003)
    assert all(run.max_periods == 100 for run in repeat_corpus.runs)
    assert all(run.simulation_performed is False for run in repeat_corpus.runs)


def test_repeat_corpus_numbers_result_rows_across_runs(repeat_corpus) -> None:
    assert len(repeat_corpus.export_tables) == 15
    for table in repeat_corpus.export_tables:
        assert [int(row.values[0]) for row in table.rows] == list(range(1, 301))
        assert table.rows[0].values[1:] == table.rows[100].values[1:]
        assert table.rows[0].values[1:] == table.rows[200].values[1:]


def test_repeat_corpus_rejects_seed_or_run_length_drift(repeat_corpus) -> None:
    wrong_seed = replace(repeat_corpus.runs[1], base_seed=99)
    wrong_length = replace(repeat_corpus.runs[1], max_periods=300)

    with pytest.raises(ValueError, match="seed differs"):
        build_vdefmd6_100_period_repeat_corpus(
            (repeat_corpus.runs[0], wrong_seed, repeat_corpus.runs[2]),
            base_seed=20260001,
        )
    with pytest.raises(ValueError, match="exceeds 100 periods"):
        build_vdefmd6_100_period_repeat_corpus(
            (repeat_corpus.runs[0], wrong_length, repeat_corpus.runs[2]),
            base_seed=20260001,
        )


@pytest.mark.parametrize("run_count", [0, 101, True, 1.5])
def test_repeat_corpus_rejects_invalid_run_count(run_count) -> None:
    with pytest.raises(ValueError, match="run_count"):
        run_vdefmd6_100_period_repetitions(
            base_seed=20260001,
            run_count=run_count,
        )
