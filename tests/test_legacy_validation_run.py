import json
from pathlib import Path

from ims.model.legacy_validation_run import (
    LegacyValidationRunResult,
    LegacyValidationTarget,
    run_legacy_validation_from_fixture,
)


FIXTURE_DIR = Path("tests/fixtures")


def test_legacy_validation_fixture_runs_multiple_file_families(tmp_path: Path) -> None:
    result = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path,
    )

    assert isinstance(result, LegacyValidationRunResult)
    assert [target.subject_type for target in result.targets] == [
        "insurer",
        "insurer",
        "policyholder",
        "policyholder",
    ]
    assert [target.export_filename for target in result.targets] == [
        "imsvusk1.dat",
        "imsvu014.dat",
        "imsvnsk1.dat",
        "imsvnr05.dat",
    ]
    assert [target.periods for target in result.targets] == [
        list(range(101, 111)),
        list(range(1, 11)),
        list(range(1, 11)),
        list(range(1, 11)),
    ]
    assert result.comparison.matches is True
    assert result.report.matches is True
    assert result.report.total_files == 4
    assert result.report.total_rows == 40
    assert result.report.matched_rows == 40
    assert [summary.subject_type for summary in result.report.file_summaries] == [
        "insurer",
        "insurer",
        "policyholder",
        "policyholder",
    ]

    assert [path.name for path in result.written_reports] == [
        "legacy_validation_bundle.json",
        "legacy_validation_bundle.csv",
    ]
    payload = json.loads((tmp_path / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    assert payload["matches"] is True
    assert payload["total_rows"] == 40
    assert payload["files"][1]["filename"] == "imsvu014.dat"
    assert payload["files"][1]["subject_type"] == "insurer"
    assert payload["files"][1]["end_period"] == 10
    assert payload["files"][2]["filename"] == "imsvnsk1.dat"
    assert payload["files"][2]["subject_type"] == "policyholder"
    assert payload["files"][3]["filename"] == "imsvnr05.dat"
    assert payload["files"][3]["start_period"] == 1


def test_legacy_validation_fixture_rejects_unknown_subject_type(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    data["targets"][0]["subject_type"] = "unknown"
    fixture_path = tmp_path / "bad_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_from_fixture(fixture_path)
    except ValueError as exc:
        assert "unsupported validation target subject_type" in str(exc)
    else:
        raise AssertionError("unknown subject_type should fail")


def test_legacy_validation_fixture_rejects_duplicate_target_periods(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    data["targets"][0]["periods"] = [101, 102, 102]
    fixture_path = tmp_path / "duplicate_periods_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_from_fixture(fixture_path)
    except ValueError as exc:
        assert "periods must be unique" in str(exc)
    else:
        raise AssertionError("duplicate target periods should fail")


def test_legacy_validation_fixture_rejects_unsorted_target_periods(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    data["targets"][0]["periods"] = [101, 103, 102]
    fixture_path = tmp_path / "unsorted_periods_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_from_fixture(fixture_path)
    except ValueError as exc:
        assert "periods must be sorted ascending" in str(exc)
    else:
        raise AssertionError("unsorted target periods should fail")


def test_legacy_validation_fixture_rejects_gapped_target_periods(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    data["targets"][0]["periods"] = [101, 102, 104]
    fixture_path = tmp_path / "gapped_periods_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_from_fixture(fixture_path)
    except ValueError as exc:
        assert "periods must be contiguous" in str(exc)
    else:
        raise AssertionError("gapped target periods should fail")


def test_legacy_validation_fixture_rejects_missing_file_identity(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    data["targets"][0]["export_filename"] = " "
    fixture_path = tmp_path / "missing_export_filename_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_from_fixture(fixture_path)
    except ValueError as exc:
        assert "export_filename" in str(exc)
    else:
        raise AssertionError("missing export_filename should fail")


def test_legacy_validation_fixture_rejects_duplicate_targets(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    data["targets"].append(dict(data["targets"][0]))
    fixture_path = tmp_path / "duplicate_targets_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_from_fixture(fixture_path)
    except ValueError as exc:
        assert "duplicate targets" in str(exc)
    else:
        raise AssertionError("duplicate validation targets should fail")


def test_legacy_validation_fixture_import_shapes() -> None:
    assert LegacyValidationRunResult is not None
    assert LegacyValidationTarget is not None
    assert run_legacy_validation_from_fixture is not None
