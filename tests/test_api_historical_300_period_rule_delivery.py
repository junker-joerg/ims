import json
from dataclasses import replace
from pathlib import Path

import pytest

import ims.api.historical_300_period_rule_delivery as delivery_module
from ims.api.historical_300_period_rule_delivery import (
    EXPECTED_COMPARISON,
    RULE_FILENAMES,
    build_historical_300_period_rule_delivery,
    main,
)
from ims.engine.vdefmd6_repeat_corpus import run_vdefmd6_100_period_repetitions
from ims.model.agrsich_export import ExportTable


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def repeat_corpus():
    return run_vdefmd6_100_period_repetitions(base_seed=20260001, run_count=3)


def test_rule_diagnostics_use_three_separate_100_period_runs(repeat_corpus) -> None:
    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()

    assert payload["status"] == "ready"
    assert payload["mode"] == "historical_300_row_rule_repeat_diagnostics"
    assert payload["controlled_execution_performed"] is False
    assert payload["controlled_run_seeds"] == [20260001, 20260002, 20260003]
    assert payload["historical_run_count"] == 3
    assert payload["historical_periods_per_run"] == 100
    assert payload["historical_result_row_count"] == 300
    assert payload["prefix_validation_status"] == "not_applicable_repeated_runs"
    assert payload["historical_single_run_horizon_claimed"] is False
    assert payload["historical_rng_reproduction_required"] is False
    assert payload["simulation_performed"] is False


def test_rule_diagnostics_freeze_current_observations(repeat_corpus) -> None:
    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()
    targets = {target["filename"]: target for target in payload["targets"]}

    assert set(targets) == set(RULE_FILENAMES)
    assert payload["historical_compared_row_count"] == 600
    assert payload["historical_matched_row_count"] == 0
    for filename, expected in EXPECTED_COMPARISON.items():
        target = targets[filename]
        assert target["run_start"] == 1
        assert target["run_end"] == 3
        assert target["local_period_start"] == 1
        assert target["local_period_end"] == 100
        for key, value in expected.items():
            assert target[key if key != "period_count" else "result_row_count"] == value


def test_rule_diagnostics_keep_partial_corpus_release_closed(repeat_corpus) -> None:
    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()

    assert payload["cumulative_delivered_export_count"] == 4
    assert payload["cumulative_delivered_period_count"] == 800
    assert payload["missing_export_count"] == 11
    assert payload["missing_period_count"] == 5500
    assert payload["production_corpus_status"] == "blocked"
    assert payload["production_release_approved"] is False


def test_rule_diagnostics_reject_repeat_boundary_drift(repeat_corpus) -> None:
    changed = replace(repeat_corpus, run_seeds=(20260001, 20260002, 999))

    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        repeat_corpus=changed,
    ).to_dict()

    assert payload["status"] == "error"
    assert "repeat_corpus_boundary_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_rule_diagnostics_reject_shortened_result_rows(repeat_corpus) -> None:
    tables = [
        ExportTable(
            spec=table.spec,
            header=table.header,
            rows=list(table.rows[:-1] if table.spec.filename.lower() == RULE_FILENAMES[0] else table.rows),
        )
        for table in repeat_corpus.export_tables
        if table.spec.filename.lower() in RULE_FILENAMES
    ]

    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
        repeat_rule_tables=tables,
    ).to_dict()

    assert payload["status"] == "error"
    assert "repeat_corpus_period_boundary_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_rule_diagnostics_reject_reference_hash_drift(
    monkeypatch: pytest.MonkeyPatch,
    repeat_corpus,
) -> None:
    monkeypatch.setitem(delivery_module.REFERENCE_SHA256, "imsvnr01.dat", "0" * 64)

    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        repeat_corpus=repeat_corpus,
    ).to_dict()

    assert payload["status"] == "error"
    assert "legacy_reference_hash_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_rule_diagnostics_cli_keeps_historical_claims_closed(
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


def test_rule_repeat_documentation_records_corrected_semantics() -> None:
    document = (
        REPO_ROOT / "docs/migration/historical_300_period_rule_delivery.md"
    ).read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "drei getrennte 100-Perioden-Laeufe" in normalized
    assert "kein historischer 300-Perioden-Lauf" in normalized
    assert "historische RNG-Folge" in normalized
    assert "Diagnostischer Befund" in normalized
