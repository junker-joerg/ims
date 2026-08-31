import json
from dataclasses import replace
from pathlib import Path

import pytest

import ims.api.historical_500_period_vusk1_delivery as delivery_module
from ims.api.historical_500_period_vusk1_delivery import (
    EXPECTED_COMPARISON,
    REFERENCE_FILENAMES,
    build_historical_500_period_vusk1_delivery,
    main,
)
from ims.engine.vdefmd6_repeat_corpus import run_vdefmd6_100_period_repetitions
from ims.model.agrsich_export import ExportTable


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def repeat_corpus():
    return run_vdefmd6_100_period_repetitions(base_seed=20260001, run_count=5)


def test_vusk1_diagnostics_use_five_separate_100_period_runs(repeat_corpus) -> None:
    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()

    assert payload["status"] == "ready"
    assert payload["mode"] == "historical_500_row_vusk1_repeat_diagnostics"
    assert payload["controlled_execution_performed"] is False
    assert payload["controlled_run_seeds"] == [
        20260001,
        20260002,
        20260003,
        20260004,
        20260005,
    ]
    assert payload["historical_run_count"] == 5
    assert payload["historical_periods_per_run"] == 100
    assert payload["historical_result_row_count"] == 500
    assert payload["prefix_validation_status"] == "not_applicable_repeated_runs"
    assert payload["historical_single_run_horizon_claimed"] is False
    assert payload["historical_rng_reproduction_required"] is False
    assert payload["simulation_performed"] is False


def test_vusk1_diagnostics_map_result_blocks_to_run_local_periods(repeat_corpus) -> None:
    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()
    targets = payload["targets"]

    assert [target["reference_filename"] for target in targets] == list(
        REFERENCE_FILENAMES
    )
    assert [target["run_index"] for target in targets] == [1, 2, 3, 4, 5]
    assert all(target["local_period_start"] == 1 for target in targets)
    assert all(target["local_period_end"] == 100 for target in targets)
    assert [target["result_row_start"] for target in targets] == [1, 101, 201, 301, 401]
    assert [target["result_row_end"] for target in targets] == [100, 200, 300, 400, 500]
    assert targets[1]["layer_id"] == "vusk1l4_direct_04410ef"
    assert targets[1]["allowed_claim"] == "versioned_fixture_regression_only"


def test_vusk1_diagnostics_freeze_current_observations(repeat_corpus) -> None:
    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()
    targets = {target["reference_filename"]: target for target in payload["targets"]}

    assert payload["historical_compared_row_count"] == 500
    assert payload["historical_matched_row_count"] == 4
    assert payload["historical_mismatched_row_count"] == 496
    assert payload["historical_compared_field_count"] == 7000
    assert payload["historical_exact_field_match_count"] == 1052
    assert payload["historical_tolerated_numeric_difference_count"] == 64
    assert payload["historical_blocking_numeric_difference_count"] == 5884
    for filename, expected in EXPECTED_COMPARISON.items():
        for key, value in expected.items():
            target_key = {
                "period_start": "result_row_start",
                "period_end": "result_row_end",
            }.get(key, key)
            assert targets[filename][target_key] == value


def test_vusk1_diagnostics_keep_partial_corpus_release_closed(repeat_corpus) -> None:
    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()

    assert payload["cumulative_delivered_export_count"] == 5
    assert payload["cumulative_delivered_period_count"] == 1300
    assert payload["missing_export_count"] == 10
    assert payload["missing_period_count"] == 5000
    assert payload["production_corpus_status"] == "blocked"
    assert payload["production_release_approved"] is False


def test_vusk1_diagnostics_reject_repeat_boundary_drift(repeat_corpus) -> None:
    changed = replace(repeat_corpus, run_seeds=(*repeat_corpus.run_seeds[:-1], 999))

    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        repeat_corpus=changed,
    ).to_dict()

    assert payload["status"] == "error"
    assert "repeat_corpus_boundary_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_vusk1_diagnostics_reject_shortened_result_rows(repeat_corpus) -> None:
    table = next(
        table
        for table in repeat_corpus.export_tables
        if table.spec.filename.lower() == "imsvusk1.dat"
    )
    shortened = ExportTable(
        spec=table.spec,
        header=table.header,
        rows=list(table.rows[:-1]),
    )

    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
        repeat_tables=(shortened,),
    ).to_dict()

    assert payload["status"] == "error"
    assert "repeat_corpus_period_boundary_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_vusk1_diagnostics_reject_reference_hash_drift(
    monkeypatch: pytest.MonkeyPatch,
    repeat_corpus,
) -> None:
    monkeypatch.setitem(delivery_module.REFERENCE_SHA256, "VUSK1L5.DAT", "0" * 64)

    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()

    assert payload["status"] == "error"
    assert "legacy_reference_hash_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_vusk1_diagnostics_cli_keeps_historical_claims_closed(
    monkeypatch: pytest.MonkeyPatch,
    repeat_corpus,
    capsys,
) -> None:
    monkeypatch.setattr(
        delivery_module,
        "_run_controlled_repetitions",
        lambda issues: repeat_corpus,
    )

    assert main(["--root", str(REPO_ROOT)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready"
    assert payload["historical_full_equality_claimed"] is False
    assert payload["historical_rng_equality_claimed"] is False
    assert payload["simulation_performed"] is False


def test_vusk1_repeat_documentation_records_corrected_semantics() -> None:
    document = (
        REPO_ROOT / "docs/migration/historical_500_period_vusk1_delivery.md"
    ).read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "fuenf getrennte 100-Perioden-Laeufe" in normalized
    assert "kein historischer 500-Perioden-Lauf" in normalized
    assert "historische RNG-Folge" in normalized
    assert "diagnostisch" in normalized
