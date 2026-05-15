import csv
import json
from pathlib import Path

from ims.engine.replay_runner import run_agrsich_replay_from_fixture
from ims.model.legacy_agrsich_reference import (
    compare_export_file_to_legacy_window,
    parse_legacy_insurer_dat,
)
from ims.model.legacy_validation_report import (
    LegacyValidationReport,
    build_legacy_validation_report,
    legacy_validation_report_to_dict,
    write_legacy_validation_report_csv,
    write_legacy_validation_report_json,
)


FIXTURE_DIR = Path("tests/fixtures")
REFERENCE_DIR = Path("tests/references/legacy_agrsich")


def _non_empty_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
    assert [summary.filename for summary in report.file_summaries] == ["imsvu014.dat", "imsvusk1.dat"]


def test_validation_report_exports_json_and_csv(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vu14_window.json", tmp_path / "run")
    assert result.validation_report is not None

    json_path = write_legacy_validation_report_json(result.validation_report, tmp_path / "report.json")
    csv_path = write_legacy_validation_report_csv(result.validation_report, tmp_path / "report.csv")

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["matches"] is True
    assert payload["files"][0]["filename"] == "imsvu014.dat"
    assert payload["files"][0]["field_deviations"] == []

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["filename"] == "imsvu014.dat"
    assert rows[0]["match_rate"] == "1.000000"
    assert rows[0]["field_deviation_count"] == "0"


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
    assert report_data["files"][0]["field_deviations"][0]["field_name"] == "Rs1"
