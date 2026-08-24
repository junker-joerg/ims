import json
from pathlib import Path

from ims.model.agrsich_export import INSURER_HEADER, ExportFileSpec, ExportRow, ExportTable
from ims.model.legacy_calculated_deviation_report import (
    build_calculated_legacy_deviation_report,
)


CORE_BUNDLE = Path("tests/fixtures/legacy_validation_bundle.json")
MIGRATION_DOC = Path("docs/migration/calculated_legacy_deviation_report.md")


def _write_fixture(tmp_path: Path) -> Path:
    legacy_path = tmp_path / "legacy_agrsich" / "CALCULATED.DAT"
    legacy_path.parent.mkdir()
    legacy_path.write_text(
        "#t Pr1 Wa1 Rs1 Vn1 Sa1 Sh1 Pr2 Wa2 Rs2 Vn2 Sa2 Sh2\n"
        "0001 040.0 000.0 +000000.0 00 000 0000.0 035.0 000.0 +000000.0 000 000 0000.0\n"
        "0002 038.8 000.0 +000019.1 02 002 0060.1 033.3 000.0 +000006.4 002 002 0062.7\n",
        encoding="utf-8",
    )
    fixture_path = tmp_path / "calculated_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "subject_type": "insurer",
                        "legacy_path": "legacy_agrsich/CALCULATED.DAT",
                        "export_filename": "imsvu014.dat",
                        "periods": [1, 2],
                        "level": "I",
                        "selector_kind": "entity",
                        "selector_value": 14,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return fixture_path


def _table(
    *,
    periods: list[int] | None = None,
    reserves_1: float = 19.1,
    header: str = INSURER_HEADER,
) -> ExportTable:
    rows_by_period = {
        1: [1, 40.0, 0.0, 0.0, 0, 0, 0.0, 35.0, 0.0, 0.0, 0, 0, 0.0],
        2: [2, 38.8, 0.0, reserves_1, 2, 2, 60.1, 33.3, 0.0, 6.4, 2, 2, 62.7],
    }
    selected_periods = periods if periods is not None else [1, 2]
    return ExportTable(
        spec=ExportFileSpec(
            filename="imsvu014.dat",
            subject_type="insurer",
            level="I",
            selector_kind="entity",
            selector_value=14,
        ),
        header=header,
        rows=[ExportRow(values=rows_by_period[period]) for period in selected_periods],
    )


def test_core_deviation_report_exposes_missing_calculated_exports_as_blockers() -> None:
    report = build_calculated_legacy_deviation_report(
        CORE_BUNDLE,
        [],
        calculation_origin="explicit_period_runner_pending",
    )

    assert report.status == "blocked_input"
    assert report.target_count == 19
    assert report.target_period_count == 6300
    assert report.required_export_count == 15
    assert report.supplied_export_count == 0
    assert len(report.input_issues) == 15
    assert {issue.code for issue in report.input_issues} == {"required_export_missing"}
    assert report.comparison_performed is False
    assert report.matches is None
    assert report.compared_row_count == 0
    assert report.writes_performed is False
    assert report.execution_performed is False
    assert report.simulation_performed is False
    assert report.historical_equivalence_claimed is False
    payload = report.to_dict()
    assert payload["status"] == "blocked_input"
    assert payload["input_issue_count"] == 15
    assert payload["matches"] is None
    assert payload["comparison_performed"] is False
    assert payload["historical_equivalence_claimed"] is False


def test_deviation_report_classifies_exact_matches(tmp_path: Path) -> None:
    report = build_calculated_legacy_deviation_report(
        _write_fixture(tmp_path),
        [_table()],
        calculation_origin="unit_test_explicit_calculation",
    )

    assert report.status == "matches"
    assert report.matches is True
    assert report.compared_row_count == 2
    assert report.matched_row_count == 2
    assert report.mismatched_row_count == 0
    assert report.exact_field_match_count == 28
    assert report.tolerated_numeric_differences == []
    assert report.blocking_numeric_differences == []
    assert report.open_field_questions == []
    assert report.comparison_performed is True
    assert report.historical_equivalence_claimed is False


def test_deviation_report_classifies_tolerated_numeric_difference(tmp_path: Path) -> None:
    report = build_calculated_legacy_deviation_report(
        _write_fixture(tmp_path),
        [_table(reserves_1=19.13)],
        calculation_origin="unit_test_explicit_calculation",
    )

    assert report.status == "matches_with_tolerated_differences"
    assert report.matches is True
    assert len(report.tolerated_numeric_differences) == 1
    difference = report.tolerated_numeric_differences[0]
    assert difference.classification == "tolerated_numeric_difference"
    assert difference.field_name == "Rs1"
    assert difference.global_period == 2
    assert difference.abs_delta is not None
    assert abs(difference.abs_delta - 0.03) < 1e-9


def test_deviation_report_classifies_blocking_numeric_difference(tmp_path: Path) -> None:
    report = build_calculated_legacy_deviation_report(
        _write_fixture(tmp_path),
        [_table(reserves_1=99.0)],
        calculation_origin="unit_test_explicit_calculation",
    )

    assert report.status == "differences"
    assert report.matches is False
    assert report.matched_row_count == 1
    assert report.mismatched_row_count == 1
    assert len(report.blocking_numeric_differences) == 1
    difference = report.blocking_numeric_differences[0]
    assert difference.classification == "blocking_numeric_difference"
    assert difference.field_name == "Rs1"
    assert difference.global_period == 2
    assert report.open_field_questions == []


def test_deviation_report_classifies_header_mismatch_as_open_field_question(tmp_path: Path) -> None:
    report = build_calculated_legacy_deviation_report(
        _write_fixture(tmp_path),
        [_table(header="#t unresolved")],
        calculation_origin="unit_test_explicit_calculation",
    )

    assert report.status == "differences"
    assert report.matches is False
    assert len(report.open_field_questions) == 2
    assert {difference.classification for difference in report.open_field_questions} == {
        "open_field_question"
    }
    assert {difference.field_name for difference in report.open_field_questions} == {"header"}
    assert report.blocking_numeric_differences == []


def test_deviation_report_blocks_missing_periods_before_comparison(tmp_path: Path) -> None:
    report = build_calculated_legacy_deviation_report(
        _write_fixture(tmp_path),
        [_table(periods=[1])],
        calculation_origin="unit_test_explicit_calculation",
    )

    assert report.status == "blocked_input"
    assert report.comparison_performed is False
    assert report.matches is None
    assert [issue.code for issue in report.input_issues] == ["required_periods_missing"]
    assert report.input_issues[0].periods == [2]


def test_deviation_report_blocks_missing_origin_without_comparison(tmp_path: Path) -> None:
    report = build_calculated_legacy_deviation_report(
        _write_fixture(tmp_path),
        [_table()],
        calculation_origin=" ",
    )

    assert report.status == "blocked_input"
    assert report.comparison_performed is False
    assert [issue.code for issue in report.input_issues] == ["calculation_origin_missing"]


def test_deviation_report_documentation_keeps_findings_conservative() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "Read-only Abweichungsdiagnose fuer berechnete Legacy-Vergleiche" in doc
    assert "keine neue C-Fachlogik" in doc
    assert "Status `blocked_input`" in doc
    assert "15 Issues mit Code `required_export_missing`" in doc
    assert "tolerated_numeric_difference" in doc
    assert "blocking_numeric_difference" in doc
    assert "open_field_question" in doc
    assert "keinen neuen fachlichen Schwellenwert" in doc
    assert "kein Ergebnis eines Neu-/Alt-Laufs" in doc
    assert "historical_equivalence_claimed = false" in doc
    assert "PR 60" in doc and "tatsaechlich berechneten Output" in doc
