import csv
import json
from pathlib import Path

from ims.engine.replay_runner import run_agrsich_replay_from_fixture
from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportFileSpec,
    ExportRow,
    ExportTable,
)
from ims.model.legacy_agrsich_multi_period import (
    build_multi_period_legacy_comparison,
    compare_insurer_export_table_to_legacy,
    compare_policyholder_export_table_to_legacy,
)
from ims.model.legacy_agrsich_reference import (
    LegacyInsurerTable,
    compare_export_file_to_legacy_window,
    extract_legacy_row,
    parse_legacy_insurer_dat,
)
from ims.model.legacy_vn_reference import (
    LegacyPolicyholderTable,
    extract_legacy_policyholder_row,
    parse_legacy_policyholder_dat,
)
from ims.model.legacy_validation_report import (
    LegacyFieldDeviationSummary,
    LegacyValidationDeviationRecord,
    LegacyValidationReport,
    LegacyValidationGroupSummary,
    LegacyValidationPeriodSummary,
    build_legacy_validation_report,
    build_legacy_validation_report_from_multi_period_comparison,
    legacy_validation_report_to_dict,
    write_legacy_validation_deviation_index_csv,
    write_legacy_validation_field_summary_csv,
    write_legacy_validation_group_summary_csv,
    write_legacy_validation_period_summary_csv,
    write_legacy_validation_report_csv,
    write_legacy_validation_report_json,
)


FIXTURE_DIR = Path("tests/fixtures")
REFERENCE_DIR = Path("tests/references/legacy_agrsich")


def _non_empty_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _insurer_table_from_legacy_rows(
    legacy_table: LegacyInsurerTable,
    filename: str,
    periods: list[int],
) -> ExportTable:
    rows: list[ExportRow] = []
    for period in periods:
        legacy_row = extract_legacy_row(legacy_table, period)
        assert legacy_row is not None
        rows.append(ExportRow(values=[legacy_row.global_period, *legacy_row.metric_values()]))
    return ExportTable(
        spec=ExportFileSpec(
            filename=filename,
            subject_type="insurer",
            level="I",
            selector_kind="entity",
            selector_value=14,
        ),
        header=INSURER_HEADER,
        rows=rows,
    )


def _policyholder_table_from_legacy_rows(
    legacy_table: LegacyPolicyholderTable,
    filename: str,
    periods: list[int],
) -> ExportTable:
    rows: list[ExportRow] = []
    for period in periods:
        legacy_row = extract_legacy_policyholder_row(legacy_table, period)
        assert legacy_row is not None
        rows.append(ExportRow(values=[legacy_row.global_period, *legacy_row.metric_values()]))
    return ExportTable(
        spec=ExportFileSpec(
            filename=filename,
            subject_type="policyholder",
            level="II",
            selector_kind="rule",
            selector_value=5,
        ),
        header=POLICYHOLDER_HEADER,
        rows=rows,
    )


def test_validation_report_summarizes_matching_replay_windows(tmp_path: Path) -> None:
    vu14 = run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vu14_window.json", tmp_path / "vu14")
    vusk1 = run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vusk1_window.json", tmp_path / "vusk1")

    assert vu14.legacy_comparison is not None
    assert vusk1.legacy_comparison is not None
    report = build_legacy_validation_report([vu14.legacy_comparison, vusk1.legacy_comparison])

    assert isinstance(report, LegacyValidationReport)
    assert report.matches is True
    assert report.total_files == 2
    assert report.total_rows == 8
    assert report.matched_rows == 8
    assert report.mismatched_rows == 0
    assert report.match_rate == 1.0
    assert report.field_summaries == []
    assert report.deviation_index == []
    assert report.group_summaries == [
        LegacyValidationGroupSummary(
            subject_type="insurer",
            level="",
            file_count=2,
            row_count=8,
            matched_rows=8,
            mismatched_rows=0,
            match_rate=1.0,
            matches=True,
            filenames=["imsvu014.dat", "imsvusk1.dat"],
            fields_with_differences=[],
        )
    ]
    assert report.period_summaries == [
        LegacyValidationPeriodSummary(
            global_period=1,
            file_count=1,
            row_count=1,
            matched_rows=1,
            mismatched_rows=0,
            match_rate=1.0,
            matches=True,
            filenames=["imsvu014.dat"],
            fields_with_differences=[],
        ),
        LegacyValidationPeriodSummary(
            global_period=2,
            file_count=1,
            row_count=1,
            matched_rows=1,
            mismatched_rows=0,
            match_rate=1.0,
            matches=True,
            filenames=["imsvu014.dat"],
            fields_with_differences=[],
        ),
        LegacyValidationPeriodSummary(
            global_period=3,
            file_count=1,
            row_count=1,
            matched_rows=1,
            mismatched_rows=0,
            match_rate=1.0,
            matches=True,
            filenames=["imsvu014.dat"],
            fields_with_differences=[],
        ),
        LegacyValidationPeriodSummary(
            global_period=4,
            file_count=1,
            row_count=1,
            matched_rows=1,
            mismatched_rows=0,
            match_rate=1.0,
            matches=True,
            filenames=["imsvu014.dat"],
            fields_with_differences=[],
        ),
        LegacyValidationPeriodSummary(
            global_period=101,
            file_count=1,
            row_count=1,
            matched_rows=1,
            mismatched_rows=0,
            match_rate=1.0,
            matches=True,
            filenames=["imsvusk1.dat"],
            fields_with_differences=[],
        ),
        LegacyValidationPeriodSummary(
            global_period=102,
            file_count=1,
            row_count=1,
            matched_rows=1,
            mismatched_rows=0,
            match_rate=1.0,
            matches=True,
            filenames=["imsvusk1.dat"],
            fields_with_differences=[],
        ),
        LegacyValidationPeriodSummary(
            global_period=103,
            file_count=1,
            row_count=1,
            matched_rows=1,
            mismatched_rows=0,
            match_rate=1.0,
            matches=True,
            filenames=["imsvusk1.dat"],
            fields_with_differences=[],
        ),
        LegacyValidationPeriodSummary(
            global_period=104,
            file_count=1,
            row_count=1,
            matched_rows=1,
            mismatched_rows=0,
            match_rate=1.0,
            matches=True,
            filenames=["imsvusk1.dat"],
            fields_with_differences=[],
        ),
    ]
    assert [summary.filename for summary in report.file_summaries] == ["imsvu014.dat", "imsvusk1.dat"]


def test_validation_report_exports_json_and_csv(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vu14_window.json", tmp_path / "run")
    assert result.validation_report is not None

    json_path = write_legacy_validation_report_json(result.validation_report, tmp_path / "report.json")
    csv_path = write_legacy_validation_report_csv(result.validation_report, tmp_path / "report.csv")
    field_csv_path = write_legacy_validation_field_summary_csv(
        result.validation_report,
        tmp_path / "report_fields.csv",
    )
    group_csv_path = write_legacy_validation_group_summary_csv(
        result.validation_report,
        tmp_path / "report_groups.csv",
    )
    period_csv_path = write_legacy_validation_period_summary_csv(
        result.validation_report,
        tmp_path / "report_periods.csv",
    )
    deviation_csv_path = write_legacy_validation_deviation_index_csv(
        result.validation_report,
        tmp_path / "report_deviations.csv",
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["matches"] is True
    assert payload["field_summaries"] == []
    assert payload["deviation_index"] == []
    assert payload["group_summaries"][0]["subject_type"] == "insurer"
    assert payload["group_summaries"][0]["row_count"] == 4
    assert payload["period_summaries"][0]["global_period"] == 1
    assert payload["period_summaries"][0]["filenames"] == ["imsvu014.dat"]
    assert payload["files"][0]["filename"] == "imsvu014.dat"
    assert payload["files"][0]["compared_periods"] == [1, 2, 3, 4]
    assert payload["files"][0]["field_summaries"] == []
    assert payload["files"][0]["field_deviations"] == []

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["filename"] == "imsvu014.dat"
    assert rows[0]["level"] == ""
    assert rows[0]["selector_kind"] == ""
    assert rows[0]["selector_value"] == ""
    assert rows[0]["match_rate"] == "1.000000"
    assert rows[0]["field_deviation_count"] == "0"
    assert rows[0]["field_summary_count"] == "0"

    with field_csv_path.open("r", encoding="utf-8", newline="") as handle:
        field_rows = list(csv.DictReader(handle))
    assert field_rows == []

    with group_csv_path.open("r", encoding="utf-8", newline="") as handle:
        group_rows = list(csv.DictReader(handle))
    assert group_rows[0]["subject_type"] == "insurer"
    assert group_rows[0]["row_count"] == "4"
    assert group_rows[0]["filenames"] == "imsvu014.dat"

    with period_csv_path.open("r", encoding="utf-8", newline="") as handle:
        period_rows = list(csv.DictReader(handle))
    assert period_rows[0]["global_period"] == "1"
    assert period_rows[0]["row_count"] == "1"
    assert period_rows[0]["filenames"] == "imsvu014.dat"

    with deviation_csv_path.open("r", encoding="utf-8", newline="") as handle:
        deviation_rows = list(csv.DictReader(handle))
    assert deviation_rows == []


def test_validation_report_captures_period_and_field_deviations(tmp_path: Path) -> None:
    run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vu14_window.json", tmp_path)
    export_path = tmp_path / "imsvu014.dat"
    lines = _non_empty_lines(export_path)
    parts = lines[2].split()
    parts[3] = "999.0"
    lines[2] = " ".join(parts)
    export_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    legacy_table = parse_legacy_insurer_dat(REFERENCE_DIR / "VU14L1.DAT")
    comparison = compare_export_file_to_legacy_window(export_path, legacy_table, 1, 4)
    report = build_legacy_validation_report([comparison])
    report_data = legacy_validation_report_to_dict(report)

    assert report.matches is False
    assert report.total_rows == 4
    assert report.matched_rows == 3
    assert report.mismatched_rows == 1
    assert report.file_summaries[0].periods_with_differences == [2]
    assert report.file_summaries[0].fields_with_differences == ["Rs1"]
    assert report.file_summaries[0].field_deviations[0].actual == 999.0
    assert report.deviation_index == [
        LegacyValidationDeviationRecord(
            filename="imsvu014.dat",
            subject_type="insurer",
            level="",
            selector_kind="",
            selector_value=None,
            global_period=2,
            field_name="Rs1",
            actual=999.0,
            expected=204.0,
        )
    ]
    assert report.file_summaries[0].field_summaries == [
        LegacyFieldDeviationSummary(
            filename="imsvu014.dat",
            field_name="Rs1",
            deviation_count=1,
            periods_with_differences=[2],
            numeric_deviation_count=1,
            max_abs_delta=795.0,
        )
    ]
    assert report.field_summaries == report.file_summaries[0].field_summaries
    assert report_data["field_summaries"][0]["field_name"] == "Rs1"
    assert report_data["deviation_index"][0]["filename"] == "imsvu014.dat"
    assert report_data["deviation_index"][0]["global_period"] == 2
    assert report_data["deviation_index"][0]["field_name"] == "Rs1"
    assert report_data["field_summaries"][0]["deviation_count"] == 1
    assert report_data["field_summaries"][0]["max_abs_delta"] == 795.0
    assert report_data["group_summaries"][0]["fields_with_differences"] == ["Rs1"]
    assert report.group_summaries[0].fields_with_differences == ["Rs1"]
    assert report.period_summaries[1].global_period == 2
    assert report.period_summaries[1].matches is False
    assert report.period_summaries[1].fields_with_differences == ["Rs1"]
    assert report_data["period_summaries"][1]["mismatched_rows"] == 1
    assert report_data["files"][0]["field_summaries"][0]["periods_with_differences"] == [2]
    assert report_data["files"][0]["field_deviations"][0]["field_name"] == "Rs1"

    field_csv_path = write_legacy_validation_field_summary_csv(report, tmp_path / "report_fields.csv")
    with field_csv_path.open("r", encoding="utf-8", newline="") as handle:
        field_rows = list(csv.DictReader(handle))
    assert field_rows[0]["filename"] == "imsvu014.dat"
    assert field_rows[0]["field_name"] == "Rs1"
    assert field_rows[0]["deviation_count"] == "1"
    assert field_rows[0]["max_abs_delta"] == "795.000000"

    deviation_csv_path = write_legacy_validation_deviation_index_csv(report, tmp_path / "report_deviations.csv")
    with deviation_csv_path.open("r", encoding="utf-8", newline="") as handle:
        deviation_rows = list(csv.DictReader(handle))
    assert deviation_rows[0]["filename"] == "imsvu014.dat"
    assert deviation_rows[0]["global_period"] == "2"
    assert deviation_rows[0]["field_name"] == "Rs1"
    assert deviation_rows[0]["actual"] == "999.0"
    assert deviation_rows[0]["expected"] == "204.0"


def test_validation_report_summarizes_vu_and_vn_file_families() -> None:
    insurer_legacy = parse_legacy_insurer_dat(REFERENCE_DIR / "VUSK1L4.DAT")
    policyholder_legacy = parse_legacy_policyholder_dat(REFERENCE_DIR / "IMSVNSK1.DAT")
    insurer_export = _insurer_table_from_legacy_rows(insurer_legacy, "imsvusk1.dat", [101, 102])
    policyholder_export = _policyholder_table_from_legacy_rows(policyholder_legacy, "imsvnsk1.dat", [1, 2])

    comparison = build_multi_period_legacy_comparison([
        compare_insurer_export_table_to_legacy(insurer_export, insurer_legacy),
        compare_policyholder_export_table_to_legacy(policyholder_export, policyholder_legacy),
    ])

    report = build_legacy_validation_report_from_multi_period_comparison(comparison)
    report_data = legacy_validation_report_to_dict(report)

    assert report.matches is True
    assert report.total_files == 2
    assert report.total_rows == 4
    assert report.match_rate == 1.0
    assert [(item.filename, item.subject_type) for item in report.file_summaries] == [
        ("imsvusk1.dat", "insurer"),
        ("imsvnsk1.dat", "policyholder"),
    ]
    assert [
        (item.level, item.selector_kind, item.selector_value)
        for item in report.file_summaries
    ] == [
        ("I", "entity", 14),
        ("II", "rule", 5),
    ]
    assert report_data["files"][0]["level"] == "I"
    assert report_data["files"][0]["selector_kind"] == "entity"
    assert report_data["files"][0]["selector_value"] == 14
    assert report_data["files"][1]["subject_type"] == "policyholder"
    assert [(item.subject_type, item.level, item.row_count) for item in report.group_summaries] == [
        ("insurer", "I", 2),
        ("policyholder", "II", 2),
    ]
    assert [(item.global_period, item.row_count) for item in report.period_summaries] == [
        (101, 1),
        (102, 1),
        (1, 1),
        (2, 1),
    ]


def test_validation_report_counts_duplicate_period_mismatches_per_row() -> None:
    insurer_legacy = parse_legacy_insurer_dat(REFERENCE_DIR / "VUSK1L4.DAT")
    insurer_export = _insurer_table_from_legacy_rows(insurer_legacy, "imsvusk1.dat", [101, 101])

    comparison = build_multi_period_legacy_comparison([
        compare_insurer_export_table_to_legacy(insurer_export, insurer_legacy)
    ])
    report = build_legacy_validation_report_from_multi_period_comparison(comparison)

    assert report.matches is False
    assert report.total_rows == 2
    assert report.matched_rows == 1
    assert report.mismatched_rows == 1
    assert report.file_summaries[0].compared_periods == [101, 101]
    assert report.file_summaries[0].row_matches == [True, False]
    assert report.period_summaries == [
        LegacyValidationPeriodSummary(
            global_period=101,
            file_count=1,
            row_count=2,
            matched_rows=1,
            mismatched_rows=1,
            match_rate=0.5,
            matches=False,
            filenames=["imsvusk1.dat"],
            fields_with_differences=["global_period"],
        )
    ]


def test_validation_report_detects_vn_family_deviation() -> None:
    legacy_table = parse_legacy_policyholder_dat(REFERENCE_DIR / "IMSVNR05.DAT")
    export_table = _policyholder_table_from_legacy_rows(legacy_table, "imsvnr05.dat", [1, 2, 3])
    export_table.rows[1].values[3] = 999.0

    comparison = build_multi_period_legacy_comparison([
        compare_policyholder_export_table_to_legacy(export_table, legacy_table)
    ])
    report = build_legacy_validation_report_from_multi_period_comparison(comparison)

    assert report.matches is False
    assert report.total_files == 1
    assert report.total_rows == 3
    assert report.mismatched_rows == 1
    assert report.file_summaries[0].periods_with_differences == [2]
    assert report.file_summaries[0].fields_with_differences == ["Vp1"]
    assert report.file_summaries[0].level == "II"
    assert report.file_summaries[0].selector_kind == "rule"
    assert report.file_summaries[0].selector_value == 5
    assert report.file_summaries[0].field_summaries[0].field_name == "Vp1"
    assert report.file_summaries[0].field_summaries[0].deviation_count == 1
    assert report.field_summaries[0].filename == "imsvnr05.dat"
    assert report.deviation_index[0].subject_type == "policyholder"
    assert report.deviation_index[0].level == "II"
    assert report.deviation_index[0].selector_kind == "rule"
    assert report.deviation_index[0].selector_value == 5
    assert report.group_summaries[0].fields_with_differences == ["Vp1"]
    assert report.period_summaries[1].global_period == 2
    assert report.period_summaries[1].fields_with_differences == ["Vp1"]
