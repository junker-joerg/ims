import copy
from dataclasses import replace
import json
from pathlib import Path

import pytest

from ims.api.historical_300_period_rule_delivery import (
    CALCULATION_ORIGIN,
    CONTRACT_VERSION,
    EXPECTED_REFERENCE_PATHS,
    REFERENCE_SHA256,
    RULE_FILENAMES,
    build_historical_300_period_rule_delivery,
    main,
)
from ims.engine.vdefmd6_pre_shock_runner import (
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
    run_vdefmd6_300_periods,
)
from ims.model.agrsich_export import ExportFileSpec, ExportRow, ExportTable


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def controlled_results() -> tuple[
    Vdefmd6PreShockRunResult,
    Vdefmd6PreShockRunResult,
]:
    return (
        run_vdefmd6_100_periods(base_seed=20260001),
        run_vdefmd6_300_periods(base_seed=20260001),
    )


def test_delivery_compares_two_300_period_rules_and_delivers_four_tables(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended = controlled_results
    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        baseline_result=baseline,
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
    ]
    assert payload["current_delivery_export_count"] == 2
    assert payload["current_delivery_period_count"] == 600
    assert payload["cumulative_delivered_export_count"] == 4
    assert payload["cumulative_delivered_period_count"] == 800
    assert payload["required_export_count"] == 15
    assert payload["missing_export_count"] == 11
    assert payload["missing_period_count"] == 5500
    assert payload["production_corpus_status"] == "blocked"
    assert payload["issues"] == []


def test_delivery_freezes_prefix_and_documented_difference_observation(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended = controlled_results
    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=extended,
    ).to_dict()
    targets = {target["filename"]: target for target in payload["targets"]}

    assert payload["prefix_validation_status"] == "ok"
    assert payload["prefix_comparison_count"] == 2
    assert payload["prefix_compared_row_count"] == 200
    assert payload["historical_comparison_status"] == "documented_differences"
    assert payload["historical_comparison_performed"] is True
    assert payload["historical_comparison_matches"] is False
    assert payload["historical_compared_row_count"] == 600
    assert payload["historical_matched_row_count"] == 0
    assert payload["historical_mismatched_row_count"] == 600
    assert set(targets) == set(RULE_FILENAMES)
    assert targets["imsvnr01.dat"]["exact_field_match_count"] == 931
    assert targets["imsvnr01.dat"]["blocking_numeric_difference_count"] == 2967
    assert targets["imsvnr01.dat"]["open_field_question_count"] == 2
    assert targets["imsvnr02.dat"]["exact_field_match_count"] == 608
    assert targets["imsvnr02.dat"]["tolerated_numeric_difference_count"] == 79
    assert targets["imsvnr02.dat"]["blocking_numeric_difference_count"] == 2628
    assert targets["imsvnr02.dat"]["open_field_question_count"] == 585
    assert {tuple(target["layer_ids"]) for target in targets.values()} == {
        ("zins000_archive",)
    }


def test_delivery_uses_injected_runs_without_starting_controlled_execution(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended = controlled_results
    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=extended,
    ).to_dict()

    assert payload["status"] == "ready"
    assert payload["controlled_execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_delivery_is_deterministic_for_both_rule_tables(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    _, expected = controlled_results
    repeated = run_vdefmd6_300_periods(base_seed=20260001)

    assert _rule_tables(repeated) == _rule_tables(expected)


def test_delivery_rejects_missing_and_additional_rule_targets(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended = controlled_results
    baseline_tables = _rule_tables(baseline)
    extended_tables = _rule_tables(extended)
    unexpected = _empty_rule_table("imsvnr99.dat", 99, 300)

    missing = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=extended,
        baseline_rule_tables=baseline_tables,
        extended_rule_tables=extended_tables[:1],
    ).to_dict()
    additional = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=extended,
        baseline_rule_tables=baseline_tables,
        extended_rule_tables=(*extended_tables, unexpected),
    ).to_dict()

    assert missing["status"] == "error"
    assert "extended_target_set_mismatch" in _issue_codes(missing)
    assert "production_delivery_count_mismatch" in _issue_codes(missing)
    assert additional["status"] == "error"
    assert "extended_target_set_mismatch" in _issue_codes(additional)


def test_delivery_rejects_changed_period_boundary_and_field_fingerprint(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended = controlled_results
    baseline_tables = _rule_tables(baseline)
    wrong_boundary = copy.deepcopy(_rule_tables(extended))
    wrong_boundary[0].rows.pop()
    changed_field = copy.deepcopy(_rule_tables(extended))
    changed_field[0].rows[0].values[1] = 999

    boundary_payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=extended,
        baseline_rule_tables=baseline_tables,
        extended_rule_tables=wrong_boundary,
    ).to_dict()
    field_payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=extended,
        baseline_rule_tables=baseline_tables,
        extended_rule_tables=changed_field,
    ).to_dict()

    assert "extended_period_boundary_mismatch" in _issue_codes(boundary_payload)
    assert "historical_observation_fingerprint_mismatch" in _issue_codes(
        field_payload
    )


def test_delivery_rejects_shortened_controlled_transition_sequence(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended = controlled_results
    shortened = replace(extended, period_results=extended.period_results[:-1])

    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=shortened,
    ).to_dict()

    assert payload["status"] == "error"
    assert "controlled_period_boundary_mismatch" in _issue_codes(payload)


def test_delivery_rejects_reference_path_and_hash_contract_drift(
    monkeypatch: pytest.MonkeyPatch,
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended = controlled_results
    monkeypatch.setitem(
        EXPECTED_REFERENCE_PATHS,
        "imsvnr01.dat",
        Path("tests/references/legacy_agrsich/not-imsvnr01.dat"),
    )
    monkeypatch.setitem(REFERENCE_SHA256, "imsvnr02.dat", "0" * 64)

    payload = build_historical_300_period_rule_delivery(
        REPO_ROOT,
        baseline_result=baseline,
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


def test_delivery_documentation_states_provenance_results_and_limits() -> None:
    document = (
        REPO_ROOT
        / "docs/migration/historical_300_period_rule_delivery.md"
    ).read_text(encoding="utf-8")
    readme = (REPO_ROOT / "docs/migration/README.md").read_text(encoding="utf-8")
    normalized = " ".join(document.split())

    assert "IMSVNR01.DAT" in document and "IMSVNR02.DAT" in document
    assert "ZINS000.ZIP" in document
    assert "4/15 Tabellen und 800/6.300" in document
    assert "600 von 600 Zeilen" in normalized
    assert "keine historische Laufidentitaet" in document
    assert "keine historische Vollgleichheit" in document
    assert "keine Produktionsfreigabe" in document
    assert "PR96" in document and "Periode 500" in normalized
    assert "historical_300_period_rule_delivery.md" in readme


def _rule_tables(result: Vdefmd6PreShockRunResult) -> tuple[ExportTable, ...]:
    return tuple(
        table
        for table in (
            *result.vn_rule_group_1_export_tables,
            *result.vn_rule_group_2_export_tables,
        )
        if table.spec.filename in RULE_FILENAMES
    )


def _empty_rule_table(
    filename: str,
    rule_id: int,
    horizon: int,
) -> ExportTable:
    return ExportTable(
        spec=ExportFileSpec(
            filename=filename,
            subject_type="policyholder",
            level="II",
            selector_kind="rule",
            selector_value=rule_id,
        ),
        header="#t Vu1 Vs1 Vp1 Ev1 Sh1 Vu2 Vs2 Vp2 Ev2 Sh2 Vm",
        rows=[ExportRow([period, *([0.0] * 11)]) for period in range(1, horizon + 1)],
    )


def _issue_codes(payload: dict[str, object]) -> set[str]:
    return {
        str(issue["code"])
        for issue in payload["issues"]  # type: ignore[index]
    }
