import json
from dataclasses import replace
from pathlib import Path

import pytest

import ims.api.historical_500_period_vn_class_delivery as delivery_module
import ims.api.historical_500_period_vn_rule_delivery as shared_delivery_module
from ims.api.historical_500_period_vn_class_delivery import (
    CLASS_FILENAMES,
    EXPECTED_COMPARISON,
    build_historical_500_period_vn_class_delivery,
    main,
)
from ims.engine.vdefmd6_repeat_corpus import run_vdefmd6_100_period_repetitions
from ims.model.agrsich_export import ExportTable


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def repeat_corpus():
    return run_vdefmd6_100_period_repetitions(base_seed=20260001, run_count=5)


def test_vn_class_diagnostics_use_five_separate_100_period_runs(
    repeat_corpus,
) -> None:
    payload = build_historical_500_period_vn_class_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()

    assert payload["status"] == "ready"
    assert payload["mode"] == "historical_500_row_vn_class_repeat_diagnostics"
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
    assert payload["historical_parameterization_match_claimed"] is False
    assert payload["historical_rng_reproduction_required"] is False
    assert payload["simulation_performed"] is False


def test_vn_class_diagnostics_freeze_current_observations(repeat_corpus) -> None:
    payload = build_historical_500_period_vn_class_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()
    targets = {target["filename"]: target for target in payload["targets"]}

    assert set(targets) == set(CLASS_FILENAMES)
    assert payload["historical_compared_row_count"] == 1500
    assert payload["historical_matched_row_count"] == 0
    assert payload["historical_mismatched_row_count"] == 1500
    assert payload["historical_compared_field_count"] == 19500
    assert payload["historical_exact_field_match_count"] == 3917
    assert payload["historical_tolerated_numeric_difference_count"] == 881
    assert payload["historical_blocking_numeric_difference_count"] == 13367
    assert payload["historical_open_field_question_count"] == 1335
    for filename, expected in EXPECTED_COMPARISON.items():
        target = targets[filename]
        assert target["level"] == "III"
        assert target["selector_kind"] == "rule_class"
        assert target["run_start"] == 1
        assert target["run_end"] == 5
        assert target["local_period_start"] == 1
        assert target["local_period_end"] == 100
        assert target["layer_ids"] == ["wvemod1_archive"]
        for key, value in expected.items():
            result_key = "result_row_count" if key == "period_count" else key
            assert target[result_key] == value


def test_vn_class_diagnostics_keep_partial_corpus_release_closed(
    repeat_corpus,
) -> None:
    payload = build_historical_500_period_vn_class_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()

    assert payload["current_delivery_export_count"] == 3
    assert payload["current_delivery_period_count"] == 1500
    assert payload["cumulative_delivered_export_count"] == 12
    assert payload["cumulative_delivered_period_count"] == 4800
    assert payload["missing_export_count"] == 3
    assert payload["missing_period_count"] == 1500
    assert payload["production_corpus_status"] == "blocked"
    assert payload["production_release_approved"] is False


def test_vn_class_diagnostics_reject_repeat_boundary_drift(repeat_corpus) -> None:
    changed = replace(repeat_corpus, run_seeds=(*repeat_corpus.run_seeds[:-1], 999))

    payload = build_historical_500_period_vn_class_delivery(
        REPO_ROOT,
        repeat_corpus=changed,
    ).to_dict()

    assert payload["status"] == "error"
    assert "repeat_corpus_boundary_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_vn_class_diagnostics_reject_shortened_result_rows(repeat_corpus) -> None:
    tables = [
        ExportTable(
            spec=table.spec,
            header=table.header,
            rows=list(
                table.rows[:-1]
                if table.spec.filename.lower() == CLASS_FILENAMES[0]
                else table.rows
            ),
        )
        for table in repeat_corpus.export_tables
        if table.spec.filename.lower() in CLASS_FILENAMES
    ]

    payload = build_historical_500_period_vn_class_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
        repeat_class_tables=tables,
    ).to_dict()

    assert payload["status"] == "error"
    assert "repeat_corpus_period_boundary_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_vn_class_diagnostics_reject_missing_target(repeat_corpus) -> None:
    tables = [
        table
        for table in repeat_corpus.export_tables
        if table.spec.filename.lower() in CLASS_FILENAMES[:-1]
    ]

    payload = build_historical_500_period_vn_class_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
        repeat_class_tables=tables,
    ).to_dict()

    assert payload["status"] == "error"
    assert "repeat_corpus_target_set_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_vn_class_diagnostics_reject_reference_hash_drift(
    monkeypatch: pytest.MonkeyPatch,
    repeat_corpus,
) -> None:
    monkeypatch.setitem(delivery_module.REFERENCE_SHA256, "imsvnvk1.dat", "0" * 64)

    payload = build_historical_500_period_vn_class_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()

    assert payload["status"] == "error"
    assert "legacy_reference_hash_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_vn_class_diagnostics_cli_keeps_historical_claims_closed(
    monkeypatch: pytest.MonkeyPatch,
    repeat_corpus,
    capsys,
) -> None:
    monkeypatch.setattr(
        shared_delivery_module,
        "_run_controlled_repetitions",
        lambda issues: repeat_corpus,
    )

    assert main(["--root", str(REPO_ROOT)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["historical_full_equality_claimed"] is False
    assert payload["historical_rng_equality_claimed"] is False
    assert payload["historical_parameterization_match_claimed"] is False
    assert payload["simulation_performed"] is False


def test_vn_class_repeat_documentation_records_pr100_boundaries() -> None:
    document = (
        REPO_ROOT / "docs/migration/historical_500_period_vn_class_delivery.md"
    ).read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "fuenf getrennte 100-Perioden-Laeufe" in normalized
    assert "kein historischer 500-Perioden-Lauf" in normalized
    assert "3.917/19.500" in normalized
    assert "12/15 Tabellen" in normalized
    assert "PR101" in normalized
