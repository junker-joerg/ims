import json
from pathlib import Path

from ims.engine.explicit_legacy_deviation_adapter import (
    _select_and_merge_required_exports,
    build_explicit_legacy_deviation_report,
)
from ims.engine.explicit_period_runner import run_explicit_multi_period_from_fixture
from ims.model.legacy_export_identity import build_legacy_export_identity


EXPLICIT_FIXTURE = Path("tests/fixtures/calculated_vu14_explicit_slice.json")
SLICE_VALIDATION_FIXTURE = Path("tests/fixtures/calculated_vu14_validation_slice.json")
CORE_BUNDLE = Path("tests/fixtures/legacy_validation_bundle.json")
MIGRATION_DOC = Path("docs/migration/explicit_vu14_calculated_deviation_slice.md")


def _run_calculated_slice():
    return run_explicit_multi_period_from_fixture(EXPLICIT_FIXTURE)


def test_explicit_vu14_slice_declares_reference_aligned_state_boundary() -> None:
    explicit_fixture = json.loads(EXPLICIT_FIXTURE.read_text(encoding="utf-8"))
    validation_fixture = json.loads(SLICE_VALIDATION_FIXTURE.read_text(encoding="utf-8"))

    assert explicit_fixture["metadata"]["state_origin"] == "explicit_reference_aligned_snapshots"
    assert (
        explicit_fixture["metadata"]["calculation_scope"]
        == "agrsich_aggregation_and_export_from_explicit_state_snapshots"
    )
    assert validation_fixture["metadata"]["validation_scope"] == "VU14L1 periods 1-4 only"
    assert validation_fixture["metadata"]["historical_equivalence_claimed"] is False


def test_explicit_vu14_slice_feeds_calculated_deviation_report() -> None:
    source_result = _run_calculated_slice()

    assert source_result.processed_global_periods == [1, 2, 3, 4]
    assert source_result.written_files == []
    assert source_result.written_legacy_report_files == []
    assert source_result.legacy_comparison is None
    assert source_result.total_vu_rule_applications == 0
    assert source_result.total_vn_insurance_rule_applications == 0
    assert source_result.total_vn_settlement_applications == 0
    assert source_result.total_vn_damage_settlement_applications == 0

    adapter_result = build_explicit_legacy_deviation_report(
        source_result,
        SLICE_VALIDATION_FIXTURE,
    )
    report = adapter_result.deviation_report

    assert adapter_result.mode == "explicit_multi_period_legacy_deviation_adapter"
    assert adapter_result.calculation_origin == "explicit_multi_period_run_result"
    assert (
        adapter_result.calculation_scope
        == "agrsich_aggregation_and_export_from_explicit_state_snapshots"
    )
    assert adapter_result.source_period_count == 4
    assert adapter_result.source_processed_global_periods == [1, 2, 3, 4]
    assert adapter_result.source_export_table_count == 20
    assert adapter_result.selected_export_count == 1
    assert adapter_result.ignored_source_export_table_count == 16
    assert adapter_result.ignored_export_identities == [
        "imsvnsk1.dat (policyholder/IV/all=all)",
        "imsvur14.dat (insurer/II/rule=14)",
        "imsvusk1.dat (insurer/IV/all=all)",
        "imsvuvk1.dat (insurer/III/rule_class=1)",
    ]
    assert adapter_result.source_execution_performed is True
    assert adapter_result.source_writes_performed is False
    assert adapter_result.source_legacy_comparison_performed is False
    assert adapter_result.adapter_writes_performed is False
    assert adapter_result.simulation_performed is False
    assert adapter_result.automatic_historical_rule_selection_performed is False
    assert adapter_result.source_state_origin_verified is False
    assert adapter_result.independent_historical_state_evolution_verified is False
    assert adapter_result.historical_equivalence_claimed is False

    assert report.status == "matches"
    assert report.calculation_origin == "explicit_multi_period_run_result"
    assert report.target_count == 1
    assert report.target_period_count == 4
    assert report.required_export_count == 1
    assert report.supplied_export_count == 1
    assert report.comparison_performed is True
    assert report.matches is True
    assert report.compared_row_count == 4
    assert report.matched_row_count == 4
    assert report.mismatched_row_count == 0
    assert report.exact_field_match_count == 56
    assert report.tolerated_numeric_differences == []
    assert report.blocking_numeric_differences == []
    assert report.open_field_questions == []
    assert report.historical_equivalence_claimed is False


def test_adapter_selects_runtime_all_table_for_historical_level_iv_sk1_identity() -> None:
    required_identity = build_legacy_export_identity(
        "imsvusk1.dat",
        "insurer",
        "IV",
        "all",
        "SK1",
    )

    selected, ignored_count, ignored_identities = _select_and_merge_required_exports(
        _run_calculated_slice(),
        {required_identity},
    )

    assert len(selected) == 1
    assert selected[0].spec.selector_value == "all"
    assert [row.values[0] for row in selected[0].rows] == [1, 2, 3, 4]
    assert ignored_count == 16
    assert "imsvusk1.dat (insurer/IV/all=all)" not in ignored_identities


def test_explicit_vu14_slice_remains_incomplete_for_core_bundle() -> None:
    adapter_result = build_explicit_legacy_deviation_report(
        _run_calculated_slice(),
        CORE_BUNDLE,
    )
    report = adapter_result.deviation_report

    assert report.status == "blocked_input"
    assert report.target_count == 19
    assert report.target_period_count == 6300
    assert report.required_export_count == 15
    assert report.comparison_performed is False
    assert report.matches is None
    assert any(issue.code == "required_export_missing" for issue in report.input_issues)
    assert any(issue.code == "required_periods_missing" for issue in report.input_issues)
    assert report.historical_equivalence_claimed is False


def test_explicit_vu14_adapter_reports_missing_slice_period_before_comparison() -> None:
    source_result = _run_calculated_slice()
    source_result.period_results.pop()

    adapter_result = build_explicit_legacy_deviation_report(
        source_result,
        SLICE_VALIDATION_FIXTURE,
    )
    report = adapter_result.deviation_report

    assert report.status == "blocked_input"
    assert report.comparison_performed is False
    assert [issue.code for issue in report.input_issues] == ["required_periods_missing"]
    assert report.input_issues[0].periods == [4]


def test_explicit_vu14_adapter_payload_keeps_execution_boundaries_visible() -> None:
    adapter_result = build_explicit_legacy_deviation_report(
        _run_calculated_slice(),
        SLICE_VALIDATION_FIXTURE,
    )

    payload = adapter_result.to_dict()
    assert payload["calculation_origin"] == "explicit_multi_period_run_result"
    assert (
        payload["calculation_scope"]
        == "agrsich_aggregation_and_export_from_explicit_state_snapshots"
    )
    assert payload["source_execution_performed"] is True
    assert payload["source_writes_performed"] is False
    assert payload["source_legacy_comparison_performed"] is False
    assert payload["adapter_writes_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["source_state_origin_verified"] is False
    assert payload["independent_historical_state_evolution_verified"] is False
    assert payload["historical_equivalence_claimed"] is False
    assert payload["deviation_report"]["status"] == "matches"
    assert payload["deviation_report"]["historical_equivalence_claimed"] is False


def test_explicit_vu14_slice_documentation_keeps_scope_conservative() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "Erster berechneter VU14-Diagnoseslice" in doc
    assert "portiert keine neue C-Fachlogik" in doc
    assert "explizite, referenzausgerichtete Snapshots" in doc
    assert "source_state_origin_verified = false" in doc
    assert "independent_historical_state_evolution_verified = false" in doc
    assert "20 einzelne" in doc and "Exporttabellen" in doc
    assert "`4/4` passende Zeilen" in doc
    assert "`56/56` exakte Feldvergleiche" in doc
    assert "kein Vollgleichheitsnachweis" in doc
    assert "`selector_value = \"all\"`" in doc
    assert "historischen Selektorwert `SK1`" in doc
    assert "nicht still gleichgesetzt" in doc
    assert "PR 61" in doc and "Level-IV-Selektormetadaten" in doc
