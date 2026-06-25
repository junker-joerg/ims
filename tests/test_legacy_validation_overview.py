import json
from pathlib import Path

import ims.model.legacy_validation_overview as overview_module
from ims.model.legacy_validation_overview import (
    LEGACY_VALIDATION_DEFAULT_TOLERANCE,
    LegacyValidationOverviewResult,
    build_legacy_validation_overview,
    main,
)
from ims.model.legacy_validation_report import (
    LegacyFieldDeviationSummary,
    LegacyFileValidationSummary,
    LegacyValidationDeviationRecord,
    LegacyValidationReport,
    LegacyValidationPeriodSummary,
)
from ims.model.legacy_agrsich_multi_period import build_multi_period_legacy_comparison
from ims.model.legacy_validation_run import LegacyValidationRunResult, LegacyValidationTarget


FIXTURE_DIR = Path("tests/fixtures")


def test_legacy_validation_overview_summarizes_bundle_without_writing(tmp_path: Path) -> None:
    before = set(tmp_path.iterdir())

    result = build_legacy_validation_overview(FIXTURE_DIR / "legacy_validation_bundle.json")
    payload = result.to_dict()

    assert isinstance(result, LegacyValidationOverviewResult)
    assert payload["status"] == "ok"
    assert payload["mode"] == "legacy_agrsich_validation_overview"
    assert payload["reference_count"] == 6
    assert payload["table_count"] == 6
    assert payload["period_count"] == 21
    assert payload["field_summary_count"] == 0
    assert payload["deviation_count"] == 0
    assert payload["matches"] is True
    assert payload["total_rows"] == 42
    assert payload["matched_rows"] == 42
    assert payload["mismatched_rows"] == 0
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert [table["filename"] for table in payload["tables"]] == [
        "imsvusk1.dat",
        "imsvu014.dat",
        "imsvnsk1.dat",
        "imsvnr05.dat",
        "imsvur02.dat",
        "imsvnr11.dat",
    ]
    assert [(item["subject_type"], item["source"], item["tolerance"]) for item in payload["tolerances"]] == [
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
    ]
    assert set(tmp_path.iterdir()) == before


def test_legacy_validation_overview_reports_mismatch_as_warning(tmp_path: Path, monkeypatch) -> None:
    target = LegacyValidationTarget(
        subject_type="insurer",
        legacy_path=Path("legacy.dat"),
        export_filename="imsvu014.dat",
        periods=[1],
        level="I",
        selector_kind="entity",
        selector_value=14,
    )
    table_summary = LegacyFileValidationSummary(
        filename="imsvu014.dat",
        subject_type="insurer",
        level="I",
        selector_kind="entity",
        selector_value=14,
        export_path=Path("imsvu014.dat"),
        legacy_path=Path("legacy.dat"),
        start_period=1,
        end_period=1,
        matches=False,
        row_count=1,
        matched_rows=0,
        mismatched_rows=1,
        match_rate=0.0,
        compared_periods=[1],
        row_matches=[False],
        periods_with_differences=[1],
        fields_with_differences=["Rs1"],
        field_deviations=[],
        field_summaries=[
            LegacyFieldDeviationSummary(
                filename="imsvu014.dat",
                field_name="Rs1",
                deviation_count=1,
                periods_with_differences=[1],
                numeric_deviation_count=1,
                max_abs_delta=1.0,
            )
        ],
    )
    report = LegacyValidationReport(
        matches=False,
        total_files=1,
        total_rows=1,
        matched_rows=0,
        mismatched_rows=1,
        match_rate=0.0,
        file_summaries=[table_summary],
        field_summaries=list(table_summary.field_summaries),
        group_summaries=[],
        period_summaries=[
            LegacyValidationPeriodSummary(
                global_period=1,
                file_count=1,
                row_count=1,
                matched_rows=0,
                mismatched_rows=1,
                match_rate=0.0,
                matches=False,
                filenames=["imsvu014.dat"],
                fields_with_differences=["Rs1"],
            )
        ],
        deviation_index=[
            LegacyValidationDeviationRecord(
                filename="imsvu014.dat",
                subject_type="insurer",
                level="I",
                selector_kind="entity",
                selector_value=14,
                global_period=1,
                field_name="Rs1",
                actual=1.0,
                expected=0.0,
            )
        ],
    )
    fake_result = LegacyValidationRunResult(
        targets=[target],
        comparison=build_multi_period_legacy_comparison([]),
        report=report,
        written_reports=[],
        artifacts=[],
    )
    monkeypatch.setattr(overview_module, "run_legacy_validation_from_fixture", lambda path: fake_result)

    payload = build_legacy_validation_overview(tmp_path / "bundle.json").to_dict()

    assert payload["status"] == "warning"
    assert payload["matches"] is False
    assert payload["deviation_count"] == 1
    assert payload["tables"][0]["filename"] == "imsvu014.dat"
    assert payload["tables"][0]["mismatched_rows"] == 1
    assert payload["field_summaries"][0]["field_name"] == "Rs1"
    assert payload["periods"][0]["global_period"] == 1
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_legacy_validation_overview_cli_prints_stable_json(capsys) -> None:
    exit_code = main([str(FIXTURE_DIR / "legacy_validation_bundle.json")])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "legacy_agrsich_validation_overview"
    assert payload["reference_count"] == 6
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_legacy_validation_overview_cli_reports_errors_as_json(tmp_path: Path, capsys) -> None:
    missing_path = tmp_path / "missing_legacy_validation_bundle.json"

    exit_code = main([str(missing_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"
    assert payload["issues"][0]["code"] == "legacy_validation_overview_failed"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not missing_path.exists()
