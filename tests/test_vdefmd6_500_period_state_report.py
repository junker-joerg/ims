import copy
from dataclasses import replace
import json
from pathlib import Path

from ims.api.vdefmd6_500_period_state_report import (
    CONTRACT_BASE_SEED,
    EXPECTED_EXPORT_FILENAMES,
    build_vdefmd6_500_period_state_report,
    main,
)
from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_500_PERIOD_EXECUTION_ORDER,
    VDEFMD6_500_PERIOD_STATE_POLICY_ID,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
    run_vdefmd6_300_periods,
    run_vdefmd6_500_periods,
)
from ims.model.agrsich_export import ExportTable
from ims.model.vdefmd6_population import build_vdefmd6_population_for_horizon


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "vdefmd6_500_period_state_contract.json"
)
MIGRATION_PATH = (
    REPO_ROOT / "docs" / "migration" / "vdefmd6_500_period_state_contract.md"
)
MIGRATION_README = REPO_ROOT / "docs" / "migration" / "README.md"


def test_500_period_runner_is_deterministic_and_keeps_both_prefixes() -> None:
    baseline_100, baseline_300, extended, repeated = _controlled_results()
    tables_100 = _tables_by_filename(baseline_100)
    tables_300 = _tables_by_filename(baseline_300)
    tables_500 = _tables_by_filename(extended)

    assert extended == repeated
    assert baseline_100.period_results == extended.period_results[:99]
    assert baseline_300.period_results == extended.period_results[:299]
    assert set(tables_100) == set(EXPECTED_EXPORT_FILENAMES)
    assert set(tables_300) == set(EXPECTED_EXPORT_FILENAMES)
    assert set(tables_500) == set(EXPECTED_EXPORT_FILENAMES)
    assert all(len(table.rows) == 500 for table in tables_500.values())
    for filename in EXPECTED_EXPORT_FILENAMES:
        assert tables_100[filename].spec == tables_500[filename].spec
        assert tables_100[filename].header == tables_500[filename].header
        assert tables_100[filename].rows == tables_500[filename].rows[:100]
        assert tables_300[filename].spec == tables_500[filename].spec
        assert tables_300[filename].header == tables_500[filename].header
        assert tables_300[filename].rows == tables_500[filename].rows[:300]


def test_500_period_report_freezes_counts_and_closed_boundaries() -> None:
    baseline_100, baseline_300, extended, _ = _controlled_results()
    payload = build_vdefmd6_500_period_state_report(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
    ).to_dict()

    assert payload["status"] == "500_period_state_ready"
    assert payload["contract_version"] == "pr96-v1"
    assert payload["state_policy_id"] == VDEFMD6_500_PERIOD_STATE_POLICY_ID
    assert payload["execution_order"] == list(VDEFMD6_500_PERIOD_EXECUTION_ORDER)
    assert payload["summary"]["transition_period_count"] == 499
    assert payload["summary"]["export_count"] == 15
    assert payload["summary"]["export_period_count"] == 7500
    prefix_100 = payload["prefix_summaries"]["periods_1_100"]
    prefix_300 = payload["prefix_summaries"]["periods_1_300"]
    assert prefix_100["state_prefix_stable"] is True
    assert prefix_100["export_prefix_stable"] is True
    assert prefix_100["export_period_count"] == 1500
    assert prefix_300["state_prefix_stable"] is True
    assert prefix_300["export_prefix_stable"] is True
    assert prefix_300["export_period_count"] == 4500
    assert len(payload["targets"]) == 15
    assert payload["source_anchor_count"] == 9
    assert payload["controlled_execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_comparison_performed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False
    assert payload["issues"] == []


def test_500_period_report_rejects_state_policy_drift() -> None:
    baseline_100, baseline_300, extended, _ = _controlled_results()
    drifted = replace(extended, state_policy_id="wrong-policy")

    payload = build_vdefmd6_500_period_state_report(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=drifted,
    ).to_dict()

    assert payload["status"] == "error"
    assert "extended_state_policy_mismatch" in _issue_codes(payload)


def test_500_period_report_rejects_changed_100_prefix() -> None:
    baseline_100, baseline_300, extended, _ = _controlled_results()
    drifted = copy.deepcopy(extended)
    drifted.vu14_export_table.rows[0].values[1] = -1.0

    payload = build_vdefmd6_500_period_state_report(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=drifted,
    ).to_dict()

    assert payload["status"] == "error"
    assert "export_100_prefix_mismatch" in _issue_codes(payload)
    assert (
        payload["prefix_summaries"]["periods_1_100"]["export_prefix_stable"]
        is False
    )


def test_500_period_report_rejects_changed_300_prefix() -> None:
    baseline_100, baseline_300, extended, _ = _controlled_results()
    drifted = copy.deepcopy(extended)
    drifted.vu14_export_table.rows[199].values[1] = -1.0

    payload = build_vdefmd6_500_period_state_report(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=drifted,
    ).to_dict()

    assert payload["status"] == "error"
    assert "export_300_prefix_mismatch" in _issue_codes(payload)
    assert (
        payload["prefix_summaries"]["periods_1_100"]["export_prefix_stable"]
        is True
    )
    assert (
        payload["prefix_summaries"]["periods_1_300"]["export_prefix_stable"]
        is False
    )


def test_500_period_report_rejects_missing_export() -> None:
    baseline_100, baseline_300, extended, _ = _controlled_results()
    incomplete = replace(
        extended,
        vn_rule_group_1_export_tables=extended.vn_rule_group_1_export_tables[1:],
    )

    payload = build_vdefmd6_500_period_state_report(
        REPO_ROOT,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=incomplete,
    ).to_dict()

    assert payload["status"] == "error"
    assert "extended_export_set_mismatch" in _issue_codes(payload)
    assert payload["prefix_summaries"]["periods_1_300"]["export_count"] == 14


def test_500_period_report_rejects_contract_drift(tmp_path: Path) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["expected"]["transition_period_end"] = 499
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    baseline_100, baseline_300, extended, _ = _controlled_results()

    payload = build_vdefmd6_500_period_state_report(
        REPO_ROOT,
        contract_path=path,
        baseline_100_result=baseline_100,
        baseline_300_result=baseline_300,
        extended_result=extended,
    ).to_dict()

    assert payload["status"] == "error"
    assert "expected_mismatch" in _issue_codes(payload)


def test_500_period_population_horizon_is_explicit() -> None:
    population = build_vdefmd6_population_for_horizon(max_periods=500)
    definitions = (
        *population.insurer_definitions,
        *population.policyholder_definitions,
    )

    assert population.max_periods == 500
    assert all(item.activation.active_through_run == 500 for item in definitions)


def test_500_period_report_cli_keeps_historical_release_closed(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "500_period_state_ready"
    assert payload["controlled_execution_performed"] is True
    assert payload["writes_performed"] is False
    assert payload["scheduler_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["full_500_period_legacy_comparison_performed"] is False
    assert payload["historical_run_identity_claimed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_500_period_documentation_separates_modern_state_from_history() -> None:
    document = MIGRATION_PATH.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")
    readme = MIGRATION_README.read_text(encoding="utf-8")

    assert "Vertrag: `pr96-v1`" in document
    assert "15 Kernexporttabellen" in normalized
    assert "7.500" in document
    assert "alle 1.500 Exportzeilen" in normalized
    assert "alle 4.500 Exportzeilen" in normalized
    assert "keine historische 500-Perioden-Laufidentitaet" in document
    assert "kein historischer 500-Perioden-Vergleich" in document
    assert "keine historische Vollgleichheitsbehauptung" in document
    assert "keine Produktionsfreigabe" in document
    assert "PR97 bindet als Naechstes" in normalized
    assert "vdefmd6_500_period_state_contract.md" in readme


def _controlled_results() -> tuple[
    Vdefmd6PreShockRunResult,
    Vdefmd6PreShockRunResult,
    Vdefmd6PreShockRunResult,
    Vdefmd6PreShockRunResult,
]:
    cache = getattr(_controlled_results, "cache", None)
    if cache is None:
        cache = (
            run_vdefmd6_100_periods(base_seed=CONTRACT_BASE_SEED),
            run_vdefmd6_300_periods(base_seed=CONTRACT_BASE_SEED),
            run_vdefmd6_500_periods(base_seed=CONTRACT_BASE_SEED),
            run_vdefmd6_500_periods(base_seed=CONTRACT_BASE_SEED),
        )
        setattr(_controlled_results, "cache", cache)
    return cache


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
