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
    assert payload["reference_count"] == 19
    assert payload["table_count"] == 19
    assert payload["period_count"] == 500
    assert payload["field_summary_count"] == 0
    assert payload["deviation_count"] == 0
    assert payload["matches"] is True
    assert payload["total_rows"] == 6300
    assert payload["matched_rows"] == 6300
    assert payload["mismatched_rows"] == 0
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert [table["filename"] for table in payload["tables"]] == [
        "imsvusk1.dat",
        "imsvusk1.dat",
        "imsvusk1.dat",
        "imsvusk1.dat",
        "imsvusk1.dat",
        "imsvu014.dat",
        "imsvnsk1.dat",
        "imsvnr01.dat",
        "imsvnr02.dat",
        "imsvnr03.dat",
        "imsvnr04.dat",
        "imsvnr05.dat",
        "imsvnr06.dat",
        "imsvnvk1.dat",
        "imsvnvk2.dat",
        "imsvnvk3.dat",
        "imsvuvk1.dat",
        "imsvuvk2.dat",
        "imsvuvk3.dat",
    ]
    assert [(item["subject_type"], item["source"], item["tolerance"]) for item in payload["tolerances"]] == [
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("policyholder", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
        ("insurer", "legacy_compare_default", LEGACY_VALIDATION_DEFAULT_TOLERANCE),
    ]
    assert [entry["filename"] for entry in payload["coverage"]] == [
        "imsvusk1.dat",
        "imsvusk1.dat",
        "imsvusk1.dat",
        "imsvusk1.dat",
        "imsvusk1.dat",
        "imsvu014.dat",
        "imsvnsk1.dat",
        "imsvnr01.dat",
        "imsvnr02.dat",
        "imsvnr03.dat",
        "imsvnr04.dat",
        "imsvnr05.dat",
        "imsvnr06.dat",
        "imsvnvk1.dat",
        "imsvnvk2.dat",
        "imsvnvk3.dat",
        "imsvuvk1.dat",
        "imsvuvk2.dat",
        "imsvuvk3.dat",
    ]
    assert all(entry["legacy_source"] == "legacy_agrsich" for entry in payload["coverage"])
    assert all(entry["is_legacy_reference"] is True for entry in payload["coverage"])
    assert payload["coverage"][0]["filename"] == "imsvusk1.dat"
    assert Path(payload["coverage"][0]["legacy_path"]).parts[-3:] == (
        "references",
        "legacy_agrsich",
        "VUSK1L1.DAT",
    )
    assert payload["coverage"][0]["legacy_source"] == "legacy_agrsich"
    assert payload["coverage"][0]["is_legacy_reference"] is True
    assert payload["coverage"][0]["subject_type"] == "insurer"
    assert payload["coverage"][0]["level"] == "IV"
    assert payload["coverage"][0]["selector_kind"] == "all"
    assert payload["coverage"][0]["selector_value"] == "SK1"
    assert payload["coverage"][0]["start_period"] == 401
    assert payload["coverage"][0]["end_period"] == 500
    assert payload["coverage"][0]["period_count"] == 100
    assert payload["coverage"][0]["row_count"] == 100
    assert payload["coverage"][0]["matches"] is True
    assert [entry["level"] for entry in payload["coverage"][:5]] == ["IV", "IV", "IV", "IV", "IV"]
    assert [entry["selector_value"] for entry in payload["coverage"][:5]] == ["SK1", "SK1", "SK1", "SK1", "SK1"]
    assert payload["coverage"][7]["subject_type"] == "policyholder"
    assert payload["coverage"][7]["selector_kind"] == "rule"
    assert payload["coverage"][7]["selector_value"] == 1
    assert payload["coverage"][7]["start_period"] == 1
    assert payload["coverage"][7]["end_period"] == 300
    assert payload["coverage"][8]["selector_value"] == 2
    assert payload["coverage"][8]["start_period"] == 1
    assert payload["coverage"][8]["end_period"] == 300
    assert payload["coverage"][9]["selector_value"] == 3
    assert payload["coverage"][9]["start_period"] == 1
    assert payload["coverage"][9]["end_period"] == 500
    assert payload["coverage"][10]["selector_value"] == 4
    assert payload["coverage"][10]["start_period"] == 1
    assert payload["coverage"][10]["end_period"] == 500
    assert payload["coverage"][11]["selector_value"] == 5
    assert payload["coverage"][11]["start_period"] == 1
    assert payload["coverage"][11]["end_period"] == 500
    assert payload["coverage"][12]["selector_value"] == 6
    assert payload["coverage"][12]["start_period"] == 1
    assert payload["coverage"][12]["end_period"] == 500
    assert payload["coverage"][13]["filename"] == "imsvnvk1.dat"
    assert payload["coverage"][13]["subject_type"] == "policyholder"
    assert payload["coverage"][13]["level"] == "III"
    assert payload["coverage"][13]["selector_kind"] == "rule_class"
    assert payload["coverage"][13]["selector_value"] == 1
    assert payload["coverage"][13]["start_period"] == 1
    assert payload["coverage"][13]["end_period"] == 500
    assert payload["coverage"][14]["filename"] == "imsvnvk2.dat"
    assert payload["coverage"][14]["selector_kind"] == "rule_class"
    assert payload["coverage"][14]["selector_value"] == 2
    assert payload["coverage"][14]["start_period"] == 1
    assert payload["coverage"][14]["end_period"] == 500
    assert payload["coverage"][15]["filename"] == "imsvnvk3.dat"
    assert payload["coverage"][15]["selector_kind"] == "rule_class"
    assert payload["coverage"][15]["selector_value"] == 3
    assert payload["coverage"][15]["start_period"] == 1
    assert payload["coverage"][15]["end_period"] == 500
    assert payload["coverage"][16]["filename"] == "imsvuvk1.dat"
    assert payload["coverage"][16]["subject_type"] == "insurer"
    assert payload["coverage"][16]["level"] == "III"
    assert payload["coverage"][16]["selector_kind"] == "rule_class"
    assert payload["coverage"][16]["selector_value"] == 1
    assert payload["coverage"][16]["start_period"] == 1
    assert payload["coverage"][16]["end_period"] == 500
    assert payload["coverage"][17]["filename"] == "imsvuvk2.dat"
    assert payload["coverage"][17]["subject_type"] == "insurer"
    assert payload["coverage"][17]["level"] == "III"
    assert payload["coverage"][17]["selector_kind"] == "rule_class"
    assert payload["coverage"][17]["selector_value"] == 2
    assert payload["coverage"][17]["start_period"] == 1
    assert payload["coverage"][17]["end_period"] == 500
    assert payload["coverage"][18]["filename"] == "imsvuvk3.dat"
    assert payload["coverage"][18]["subject_type"] == "insurer"
    assert payload["coverage"][18]["level"] == "III"
    assert payload["coverage"][18]["selector_kind"] == "rule_class"
    assert payload["coverage"][18]["selector_value"] == 3
    assert payload["coverage"][18]["start_period"] == 1
    assert payload["coverage"][18]["end_period"] == 500
    assert set(tmp_path.iterdir()) == before


def test_legacy_validation_overview_keeps_duplicate_export_filename_windows(
    tmp_path: Path, monkeypatch
) -> None:
    first_target = LegacyValidationTarget(
        subject_type="insurer",
        legacy_path=Path("tests/references/legacy_agrsich/VU14L1.DAT"),
        export_filename="same.dat",
        periods=[1, 2],
        level="I",
        selector_kind="entity",
        selector_value=14,
    )
    second_target = LegacyValidationTarget(
        subject_type="insurer",
        legacy_path=Path("tests/references/legacy_agrsich/VUSK1L4.DAT"),
        export_filename="same.dat",
        periods=[101, 102, 103],
        level="IV",
        selector_kind="all",
        selector_value="SK1",
    )
    first_summary = LegacyFileValidationSummary(
        filename="same.dat",
        subject_type="insurer",
        level="I",
        selector_kind="entity",
        selector_value=14,
        export_path=Path("first/same.dat"),
        legacy_path=Path("tests/references/legacy_agrsich/VU14L1.DAT"),
        start_period=1,
        end_period=2,
        matches=True,
        row_count=2,
        matched_rows=2,
        mismatched_rows=0,
        match_rate=1.0,
        compared_periods=[1, 2],
        row_matches=[True, True],
        periods_with_differences=[],
        fields_with_differences=[],
        field_deviations=[],
        field_summaries=[],
    )
    second_summary = LegacyFileValidationSummary(
        filename="same.dat",
        subject_type="insurer",
        level="IV",
        selector_kind="all",
        selector_value="SK1",
        export_path=Path("second/same.dat"),
        legacy_path=Path("tests/references/legacy_agrsich/VUSK1L4.DAT"),
        start_period=101,
        end_period=103,
        matches=True,
        row_count=3,
        matched_rows=3,
        mismatched_rows=0,
        match_rate=1.0,
        compared_periods=[101, 102, 103],
        row_matches=[True, True, True],
        periods_with_differences=[],
        fields_with_differences=[],
        field_deviations=[],
        field_summaries=[],
    )
    fake_result = LegacyValidationRunResult(
        targets=[first_target, second_target],
        comparison=build_multi_period_legacy_comparison([]),
        report=LegacyValidationReport(
            matches=True,
            total_files=2,
            total_rows=5,
            matched_rows=5,
            mismatched_rows=0,
            match_rate=1.0,
            file_summaries=[first_summary, second_summary],
            field_summaries=[],
            group_summaries=[],
            period_summaries=[],
            deviation_index=[],
        ),
        written_reports=[],
        artifacts=[],
    )
    monkeypatch.setattr(
        overview_module,
        "run_legacy_validation_from_fixture",
        lambda path: fake_result,
    )

    payload = build_legacy_validation_overview(tmp_path / "bundle.json").to_dict()

    assert [entry["filename"] for entry in payload["coverage"]] == ["same.dat", "same.dat"]
    assert [
        (
            entry["start_period"],
            entry["end_period"],
            entry["period_count"],
            entry["row_count"],
        )
        for entry in payload["coverage"]
    ] == [(1, 2, 2, 2), (101, 103, 3, 3)]
    assert [entry["selector_value"] for entry in payload["coverage"]] == [14, "SK1"]
    assert [Path(entry["legacy_path"]).parts[-1] for entry in payload["coverage"]] == [
        "VU14L1.DAT",
        "VUSK1L4.DAT",
    ]


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
    assert payload["reference_count"] == 19
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
