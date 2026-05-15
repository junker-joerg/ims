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
    assert [target.subject_type for target in result.targets] == ["insurer", "policyholder"]
    assert [target.export_filename for target in result.targets] == ["imsvusk1.dat", "imsvnsk1.dat"]
    assert [target.periods for target in result.targets] == [[101, 102, 103, 104], [1, 2, 3, 4]]
    assert result.comparison.matches is True
    assert result.report.matches is True
    assert result.report.total_files == 2
    assert result.report.total_rows == 8
    assert result.report.matched_rows == 8
    assert [summary.subject_type for summary in result.report.file_summaries] == ["insurer", "policyholder"]

    assert [path.name for path in result.written_reports] == [
        "legacy_validation_bundle.json",
        "legacy_validation_bundle.csv",
    ]
    payload = json.loads((tmp_path / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    assert payload["matches"] is True
    assert payload["total_rows"] == 8
    assert payload["files"][1]["filename"] == "imsvnsk1.dat"
    assert payload["files"][1]["subject_type"] == "policyholder"


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


def test_legacy_validation_fixture_import_shapes() -> None:
    assert LegacyValidationRunResult is not None
    assert LegacyValidationTarget is not None
    assert run_legacy_validation_from_fixture is not None
