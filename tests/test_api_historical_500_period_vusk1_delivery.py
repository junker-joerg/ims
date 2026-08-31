import copy
from dataclasses import replace
import json
from pathlib import Path

import pytest

import ims.api.historical_500_period_vusk1_delivery as delivery_module
from ims.api.historical_500_period_vusk1_delivery import (
    CALCULATION_ORIGIN,
    CONTRACT_VERSION,
    EXPECTED_REFERENCE_PATHS,
    REFERENCE_FILENAMES,
    REFERENCE_SHA256,
    build_historical_500_period_vusk1_delivery,
    main,
)
from ims.api.historical_horizon_contract import build_historical_horizon_contract
from ims.engine.vdefmd6_pre_shock_runner import (
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
    run_vdefmd6_300_periods,
    run_vdefmd6_500_periods,
)
from ims.model.agrsich_export import ExportTable


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def controlled_results() -> tuple[
    Vdefmd6PreShockRunResult,
    Vdefmd6PreShockRunResult,
    Vdefmd6PreShockRunResult,
]:
    return (
        run_vdefmd6_100_periods(base_seed=20260001),
        run_vdefmd6_300_periods(base_seed=20260001),
        run_vdefmd6_500_periods(base_seed=20260001),
    )


def test_delivery_compares_five_windows_and_delivers_five_tables_cumulatively(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline_100, baseline_300, extended = controlled_results
    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
    ).to_dict()

    assert payload["status"] == "ready"
    assert payload["contract_version"] == CONTRACT_VERSION
    assert payload["calculation_origin"] == CALCULATION_ORIGIN
    assert payload["source_contracts"] == [
        "pr91-v1",
        "pr92-v1",
        "pr93-v1",
        "pr94-v1",
        "pr95-v1",
        "pr96-v1",
    ]
    assert payload["current_delivery_export_count"] == 1
    assert payload["current_delivery_reference_test_count"] == 5
    assert payload["current_delivery_period_count"] == 500
    assert payload["cumulative_delivered_export_count"] == 5
    assert payload["cumulative_delivered_period_count"] == 1300
    assert payload["required_export_count"] == 15
    assert payload["missing_export_count"] == 10
    assert payload["missing_period_count"] == 5000
    assert payload["production_corpus_status"] == "blocked"
    assert payload["issues"] == []


def test_delivery_freezes_prefixes_layers_and_documented_differences(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline_100, baseline_300, extended = controlled_results
    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
    ).to_dict()
    targets = {
        target["reference_filename"]: target for target in payload["targets"]
    }

    assert payload["prefix_validation_status"] == "ok"
    assert payload["prefix_snapshot_count"] == 3
    assert payload["prefix_comparison_count"] == 3
    assert payload["prefix_compared_row_count"] == 500
    assert payload["historical_comparison_status"] == "documented_differences"
    assert payload["historical_comparison_matches"] is False
    assert payload["historical_compared_row_count"] == 500
    assert payload["historical_matched_row_count"] == 1
    assert payload["historical_mismatched_row_count"] == 499
    assert payload["historical_compared_field_count"] == 7000
    assert payload["historical_exact_field_match_count"] == 1021
    assert payload["historical_tolerated_numeric_difference_count"] == 29
    assert payload["historical_blocking_numeric_difference_count"] == 5950
    assert payload["historical_open_field_question_count"] == 0
    assert set(targets) == set(REFERENCE_FILENAMES)
    assert targets["VUSK1L5.DAT"]["matched_rows"] == 1
    assert targets["VUSK1L4.DAT"]["layer_id"] == "vusk1l4_direct_04410ef"
    assert targets["VUSK1L4.DAT"]["coherence_class"] == (
        "contradictory_or_unresolved"
    )
    assert targets["VUSK1L4.DAT"]["allowed_claim"] == (
        "versioned_fixture_regression_only"
    )
    assert {
        target["layer_id"]
        for name, target in targets.items()
        if name != "VUSK1L4.DAT"
    } == {"wvemod2_archive"}


def test_delivery_uses_injected_runs_without_starting_controlled_execution(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline_100, baseline_300, extended = controlled_results
    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
    ).to_dict()

    assert payload["status"] == "ready"
    assert payload["controlled_execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_delivery_is_deterministic_for_vusk1_table(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    _, _, expected = controlled_results
    repeated = run_vdefmd6_500_periods(base_seed=20260001)

    assert _vusk1_tables(repeated) == _vusk1_tables(expected)


def test_delivery_rejects_missing_and_additional_vusk1_targets(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline_100, baseline_300, extended = controlled_results
    tables = _vusk1_tables(extended)
    additional = copy.deepcopy(tables[0])
    additional.spec = replace(additional.spec, filename="imsvusk2.dat")

    missing = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
        extended_tables=(),
    ).to_dict()
    extra = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
        extended_tables=(*tables, additional),
    ).to_dict()

    assert missing["status"] == "error"
    assert "extended_target_set_mismatch" in _issue_codes(missing)
    assert "production_delivery_count_mismatch" in _issue_codes(missing)
    assert extra["status"] == "error"
    assert "extended_target_set_mismatch" in _issue_codes(extra)


def test_delivery_rejects_changed_period_boundary_and_field_fingerprint(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline_100, baseline_300, extended = controlled_results
    wrong_boundary = copy.deepcopy(_vusk1_tables(extended))
    wrong_boundary[0].rows.pop()
    changed_field = copy.deepcopy(_vusk1_tables(extended))
    changed_field[0].rows[0].values[1] = 999

    boundary_payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
        extended_tables=wrong_boundary,
    ).to_dict()
    field_payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
        extended_tables=changed_field,
    ).to_dict()

    assert "extended_period_boundary_mismatch" in _issue_codes(boundary_payload)
    assert "historical_observation_fingerprint_mismatch" in _issue_codes(
        field_payload
    )


def test_delivery_rejects_shortened_controlled_transition_sequence(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline_100, baseline_300, extended = controlled_results
    shortened = replace(extended, period_results=extended.period_results[:-1])

    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=shortened,
    ).to_dict()

    assert payload["status"] == "error"
    assert "controlled_period_boundary_mismatch" in _issue_codes(payload)


def test_delivery_rejects_collapsed_vusk1l4_reference_layer(
    monkeypatch: pytest.MonkeyPatch,
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    contract = build_historical_horizon_contract(REPO_ROOT)
    entry = next(item for item in contract.entries if item.filename == "imsvusk1.dat")
    slices = tuple(
        replace(item, layer_id="wvemod2_archive")
        if item.reference_filename == "VUSK1L4.DAT"
        else item
        for item in entry.reference_slices
    )
    drifted_entry = replace(entry, reference_slices=slices)
    drifted_contract = replace(
        contract,
        entries=tuple(
            drifted_entry if item.filename == "imsvusk1.dat" else item
            for item in contract.entries
        ),
    )
    monkeypatch.setattr(
        delivery_module,
        "build_historical_horizon_contract",
        lambda _root: drifted_contract,
    )
    baseline_100, baseline_300, extended = controlled_results

    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
    ).to_dict()

    assert payload["status"] == "error"
    assert "horizon_layer_boundary_mismatch" in _issue_codes(payload)


def test_delivery_rejects_reference_path_and_hash_contract_drift(
    monkeypatch: pytest.MonkeyPatch,
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline_100, baseline_300, extended = controlled_results
    monkeypatch.setitem(
        EXPECTED_REFERENCE_PATHS,
        "VUSK1L5.DAT",
        Path("tests/references/legacy_agrsich/not-vusk1l5.dat"),
    )
    monkeypatch.setitem(REFERENCE_SHA256, "VUSK1L4.DAT", "0" * 64)

    payload = build_historical_500_period_vusk1_delivery(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
    ).to_dict()

    assert payload["status"] == "error"
    assert "legacy_reference_path_mismatch" in _issue_codes(payload)
    assert "legacy_reference_hash_mismatch" in _issue_codes(payload)


def test_delivery_cli_keeps_release_and_simulation_closed(capsys) -> None:
    exit_code = main(["--root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ready"
    assert payload["controlled_execution_performed"] is True
    assert payload["production_corpus_status"] == "blocked"
    assert payload["production_calculated_comparison_performed"] is False
    assert payload["writes_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_run_identity_claimed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False


def test_delivery_documentation_states_layers_results_and_limits() -> None:
    document = (
        REPO_ROOT / "docs/migration/historical_500_period_vusk1_delivery.md"
    ).read_text(encoding="utf-8")
    readme = (REPO_ROOT / "docs/migration/README.md").read_text(encoding="utf-8")
    normalized = " ".join(document.split())

    assert "VUSK1L5.DAT" in document and "VUSK1L1.DAT" in document
    assert "VUSK1L4.DAT" in document
    assert "vusk1l4_direct_04410ef" in document
    assert "5/15 Tabellen und 1.300/6.300" in document
    assert "499 von 500 Zeilen" in normalized
    assert "keine gemeinsame historische Laufidentitaet" in document
    assert "keine historische Vollgleichheit" in document
    assert "keine Produktionsfreigabe" in document
    assert "PR98" in document and "IMSVNR03.DAT" in document
    assert "historical_500_period_vusk1_delivery.md" in readme


def _vusk1_tables(result: Vdefmd6PreShockRunResult) -> tuple[ExportTable, ...]:
    return tuple(
        table
        for table in result.vu_aggregate_export_tables
        if table.spec.filename == "imsvusk1.dat"
    )


def _issue_codes(payload: dict[str, object]) -> set[str]:
    return {
        str(issue["code"])
        for issue in payload["issues"]  # type: ignore[index]
    }
