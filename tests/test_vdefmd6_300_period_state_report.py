import copy
from dataclasses import replace
import json
from pathlib import Path

import pytest

from ims.api.vdefmd6_300_period_state_report import (
    CONTRACT_BASE_SEED,
    EXPECTED_EXPORT_FILENAMES,
    build_vdefmd6_300_period_state_report,
    main,
)
from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_300_PERIOD_EXECUTION_ORDER,
    VDEFMD6_300_PERIOD_STATE_POLICY_ID,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
    run_vdefmd6_300_periods,
)
from ims.model.agrsich_export import ExportTable
from ims.model.vdefmd6_population import (
    build_vdefmd6_population,
    build_vdefmd6_population_for_horizon,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "vdefmd6_300_period_state_contract.json"
)
MIGRATION_PATH = (
    REPO_ROOT / "docs" / "migration" / "vdefmd6_300_period_state_contract.md"
)
MIGRATION_README = REPO_ROOT / "docs" / "migration" / "README.md"


@pytest.fixture(scope="module")
def controlled_results() -> tuple[
    Vdefmd6PreShockRunResult,
    Vdefmd6PreShockRunResult,
    Vdefmd6PreShockRunResult,
]:
    return (
        run_vdefmd6_100_periods(base_seed=CONTRACT_BASE_SEED),
        run_vdefmd6_300_periods(base_seed=CONTRACT_BASE_SEED),
        run_vdefmd6_300_periods(base_seed=CONTRACT_BASE_SEED),
    )


def test_300_period_runner_is_deterministic_and_keeps_exact_prefix(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended, repeated = controlled_results
    baseline_tables = _tables_by_filename(baseline)
    extended_tables = _tables_by_filename(extended)

    assert extended == repeated
    assert baseline.period_results == extended.period_results[:99]
    assert set(baseline_tables) == set(EXPECTED_EXPORT_FILENAMES)
    assert set(extended_tables) == set(EXPECTED_EXPORT_FILENAMES)
    assert all(len(table.rows) == 300 for table in extended_tables.values())
    assert all(
        baseline_tables[filename].spec == extended_tables[filename].spec
        and baseline_tables[filename].header == extended_tables[filename].header
        and baseline_tables[filename].rows
        == extended_tables[filename].rows[:100]
        for filename in EXPECTED_EXPORT_FILENAMES
    )


def test_300_period_report_freezes_counts_and_closed_boundaries(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended, _ = controlled_results
    payload = build_vdefmd6_300_period_state_report(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=extended,
    ).to_dict()

    assert payload["status"] == "300_period_state_ready"
    assert payload["contract_version"] == "pr94-v1"
    assert payload["state_policy_id"] == VDEFMD6_300_PERIOD_STATE_POLICY_ID
    assert payload["execution_order"] == list(VDEFMD6_300_PERIOD_EXECUTION_ORDER)
    assert payload["summary"]["transition_period_count"] == 299
    assert payload["summary"]["export_count"] == 15
    assert payload["summary"]["export_period_count"] == 4500
    assert payload["prefix_summary"]["state_prefix_stable"] is True
    assert payload["prefix_summary"]["export_prefix_stable"] is True
    assert payload["prefix_summary"]["export_period_count"] == 1500
    assert len(payload["targets"]) == 15
    assert payload["source_anchor_count"] == 9
    assert payload["controlled_execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_comparison_performed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False
    assert payload["issues"] == []


def test_300_period_report_rejects_state_policy_drift(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended, _ = controlled_results
    drifted = replace(extended, state_policy_id="wrong-policy")

    payload = build_vdefmd6_300_period_state_report(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=drifted,
    ).to_dict()

    assert payload["status"] == "error"
    assert "extended_state_policy_mismatch" in _issue_codes(payload)


def test_300_period_report_rejects_changed_export_prefix(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended, _ = controlled_results
    drifted = copy.deepcopy(extended)
    drifted.vu14_export_table.rows[0].values[1] = -1.0

    payload = build_vdefmd6_300_period_state_report(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=drifted,
    ).to_dict()

    assert payload["status"] == "error"
    assert "export_prefix_mismatch" in _issue_codes(payload)
    assert payload["prefix_summary"]["export_prefix_stable"] is False


def test_300_period_report_rejects_missing_export(
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    baseline, extended, _ = controlled_results
    incomplete = replace(
        extended,
        vn_rule_group_1_export_tables=extended.vn_rule_group_1_export_tables[1:],
    )

    payload = build_vdefmd6_300_period_state_report(
        REPO_ROOT,
        baseline_result=baseline,
        extended_result=incomplete,
    ).to_dict()

    assert payload["status"] == "error"
    assert "extended_export_set_mismatch" in _issue_codes(payload)
    assert payload["prefix_summary"]["export_count"] == 14


def test_300_period_report_rejects_contract_drift(
    tmp_path: Path,
    controlled_results: tuple[
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
        Vdefmd6PreShockRunResult,
    ],
) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["expected"]["transition_period_end"] = 299
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    baseline, extended, _ = controlled_results

    payload = build_vdefmd6_300_period_state_report(
        REPO_ROOT,
        contract_path=path,
        baseline_result=baseline,
        extended_result=extended,
    ).to_dict()

    assert payload["status"] == "error"
    assert "expected_mismatch" in _issue_codes(payload)


def test_extended_population_horizon_is_explicit_and_validated() -> None:
    baseline = build_vdefmd6_population()
    extended = build_vdefmd6_population_for_horizon(max_periods=300)
    definitions = (
        *extended.insurer_definitions,
        *extended.policyholder_definitions,
    )

    assert baseline.max_periods == 100
    assert extended.max_periods == 300
    assert all(item.activation.active_through_run == 300 for item in definitions)
    with pytest.raises(ValueError, match="at least 100"):
        build_vdefmd6_population_for_horizon(max_periods=99)
    with pytest.raises(ValueError, match="at least 100"):
        build_vdefmd6_population_for_horizon(max_periods=300.0)  # type: ignore[arg-type]


def test_300_period_report_cli_keeps_historical_release_closed(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "300_period_state_ready"
    assert payload["controlled_execution_performed"] is True
    assert payload["writes_performed"] is False
    assert payload["scheduler_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["full_300_period_legacy_comparison_performed"] is False
    assert payload["historical_run_identity_claimed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_300_period_documentation_separates_modern_state_from_history() -> None:
    document = MIGRATION_PATH.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")
    readme = MIGRATION_README.read_text(encoding="utf-8")

    assert "Vertrag: `pr94-v1`" in document
    assert "15 Kernexporttabellen" in normalized
    assert "4.500" in document
    assert "alle 1.500 Exportzeilen" in normalized
    assert "drei getrennte Sequenzen 1-100" in normalized
    assert "keine historische 300-Perioden-Laufidentitaet" in document
    assert "kein historischer 300-Perioden-Vergleich" in document
    assert "keine historische Vollgleichheitsbehauptung" in document
    assert "keine Produktionsfreigabe" in document
    assert "PR95 bindet ausschliesslich `imsvnr01.dat`" in normalized
    assert "vdefmd6_300_period_state_contract.md" in readme


def _tables_by_filename(
    result: Vdefmd6PreShockRunResult,
) -> dict[str, ExportTable]:
    tables = (
        result.vu14_export_table,
        *result.vu_aggregate_export_tables,
        *result.vn_rule_group_1_export_tables,
        *result.vn_rule_group_2_export_tables,
        *result.vn_aggregate_export_tables,
    )
    return {table.spec.filename: table for table in tables}


def _issue_codes(payload: dict[str, object]) -> set[str]:
    return {
        str(issue["code"])
        for issue in payload["issues"]  # type: ignore[union-attr]
    }
