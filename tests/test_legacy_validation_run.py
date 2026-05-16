import csv
import json
from pathlib import Path

from ims.model.legacy_validation_run import (
    LegacyValidationArtifact,
    LegacyValidationArtifactManifest,
    LegacyValidationReportPayloadSummary,
    LegacyValidationReportSummaryBundle,
    LegacyValidationReportSummaryBundleArtifactManifest,
    LegacyValidationBatchRunItem,
    LegacyValidationBatchRunResult,
    LegacyValidationRunResult,
    LegacyValidationTarget,
    build_legacy_validation_report_summary_bundle,
    legacy_validation_report_payload_summary_to_dict,
    legacy_validation_report_summary_bundle_to_dict,
    load_legacy_validation_artifact_manifest,
    load_legacy_validation_report_payload_from_manifest,
    load_legacy_validation_report_summary_bundle_artifact_manifest,
    load_legacy_validation_report_summary_bundle_payload_from_manifest,
    run_legacy_validation_batch_from_fixture,
    run_legacy_validation_from_fixture,
    summarize_legacy_validation_report_payload_from_manifest,
    summarize_legacy_validation_report_payloads_from_directory,
    summarize_legacy_validation_report_payloads_from_manifests,
    write_legacy_validation_report_summary_bundle_artifacts,
    write_legacy_validation_report_summary_bundle_artifacts_from_directory,
    write_legacy_validation_report_summary_bundle_artifacts_from_manifests,
    write_legacy_validation_report_summary_bundle_csv,
    write_legacy_validation_report_summary_bundle_json,
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
        "legacy_validation_bundle_fields.csv",
        "legacy_validation_bundle_groups.csv",
        "legacy_validation_bundle_periods.csv",
        "legacy_validation_bundle_deviations.csv",
        "legacy_validation_bundle_artifacts.json",
    ]
    assert [artifact.kind for artifact in result.artifacts] == [
        "report_json",
        "file_summary_csv",
        "field_summary_csv",
        "group_summary_csv",
        "period_summary_csv",
        "deviation_index_csv",
        "artifact_manifest_json",
    ]
    payload = json.loads((tmp_path / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    assert payload["matches"] is True
    assert payload["total_rows"] == 40
    assert payload["files"][1]["filename"] == "imsvu014.dat"
    assert payload["files"][1]["subject_type"] == "insurer"
    assert payload["files"][1]["level"] == "I"
    assert payload["files"][1]["selector_kind"] == "entity"
    assert payload["files"][1]["selector_value"] == 14
    assert payload["files"][1]["end_period"] == 10
    assert payload["files"][2]["filename"] == "imsvnsk1.dat"
    assert payload["files"][2]["subject_type"] == "policyholder"
    assert payload["files"][2]["level"] == "IV"
    assert payload["files"][2]["selector_kind"] == "all"
    assert payload["files"][2]["selector_value"] == "SK1"
    assert payload["files"][3]["filename"] == "imsvnr05.dat"
    assert payload["files"][3]["start_period"] == 1
    assert [(item["subject_type"], item["level"], item["row_count"]) for item in payload["group_summaries"]] == [
        ("insurer", "IV", 10),
        ("insurer", "I", 10),
        ("policyholder", "IV", 10),
        ("policyholder", "II", 10),
    ]
    assert payload["period_summaries"][0]["global_period"] == 101
    assert payload["period_summaries"][0]["filenames"] == ["imsvusk1.dat"]
    assert payload["period_summaries"][10]["global_period"] == 1
    assert payload["period_summaries"][10]["filenames"] == [
        "imsvu014.dat",
        "imsvnsk1.dat",
        "imsvnr05.dat",
    ]
    assert payload["deviation_index"] == []

    with (tmp_path / "legacy_validation_bundle.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[1]["level"] == "I"
    assert rows[1]["selector_kind"] == "entity"
    assert rows[1]["selector_value"] == "14"
    assert rows[2]["level"] == "IV"
    assert rows[2]["selector_kind"] == "all"
    assert rows[2]["selector_value"] == "SK1"

    with (tmp_path / "legacy_validation_bundle_groups.csv").open("r", encoding="utf-8", newline="") as handle:
        group_rows = list(csv.DictReader(handle))
    assert group_rows[0]["subject_type"] == "insurer"
    assert group_rows[0]["level"] == "IV"
    assert group_rows[0]["row_count"] == "10"
    assert group_rows[0]["filenames"] == "imsvusk1.dat"

    with (tmp_path / "legacy_validation_bundle_periods.csv").open("r", encoding="utf-8", newline="") as handle:
        period_rows = list(csv.DictReader(handle))
    assert period_rows[0]["global_period"] == "101"
    assert period_rows[0]["filenames"] == "imsvusk1.dat"
    assert period_rows[10]["global_period"] == "1"
    assert period_rows[10]["row_count"] == "3"

    with (tmp_path / "legacy_validation_bundle_deviations.csv").open("r", encoding="utf-8", newline="") as handle:
        deviation_rows = list(csv.DictReader(handle))
    assert deviation_rows == []

    manifest = json.loads((tmp_path / "legacy_validation_bundle_artifacts.json").read_text(encoding="utf-8"))
    assert manifest["report_name"] == "legacy_validation_bundle"
    assert manifest["matches"] is True
    assert manifest["total_files"] == 4
    assert manifest["total_rows"] == 40
    assert manifest["artifact_count"] == 7
    assert [artifact["kind"] for artifact in manifest["artifacts"]] == [
        "report_json",
        "file_summary_csv",
        "field_summary_csv",
        "group_summary_csv",
        "period_summary_csv",
        "deviation_index_csv",
        "artifact_manifest_json",
    ]
    assert manifest["artifacts"][-1]["filename"] == "legacy_validation_bundle_artifacts.json"

    loaded_manifest = load_legacy_validation_artifact_manifest(
        tmp_path / "legacy_validation_bundle_artifacts.json"
    )
    assert isinstance(loaded_manifest, LegacyValidationArtifactManifest)
    assert loaded_manifest.report_name == "legacy_validation_bundle"
    assert loaded_manifest.matches is True
    assert loaded_manifest.total_rows == 40
    assert [artifact.kind for artifact in loaded_manifest.artifacts] == [
        "report_json",
        "file_summary_csv",
        "field_summary_csv",
        "group_summary_csv",
        "period_summary_csv",
        "deviation_index_csv",
        "artifact_manifest_json",
    ]
    assert all(artifact.path.exists() for artifact in loaded_manifest.artifacts)
    assert loaded_manifest.artifact_for_kind("report_json") is not None
    assert loaded_manifest.artifact_for_kind("unknown") is None

    report_payload = load_legacy_validation_report_payload_from_manifest(
        tmp_path / "legacy_validation_bundle_artifacts.json"
    )
    assert report_payload["matches"] is True
    assert report_payload["total_rows"] == 40
    assert report_payload["total_files"] == 4

    report_summary = summarize_legacy_validation_report_payload_from_manifest(
        tmp_path / "legacy_validation_bundle_artifacts.json"
    )
    assert isinstance(report_summary, LegacyValidationReportPayloadSummary)
    assert report_summary.report_name == "legacy_validation_bundle"
    assert report_summary.matches is True
    assert report_summary.total_files == 4
    assert report_summary.total_rows == 40
    assert report_summary.matched_rows == 40
    assert report_summary.mismatched_rows == 0
    assert report_summary.match_rate == 1.0
    assert report_summary.artifact_kinds == [
        "report_json",
        "file_summary_csv",
        "field_summary_csv",
        "group_summary_csv",
        "period_summary_csv",
        "deviation_index_csv",
        "artifact_manifest_json",
    ]
    assert report_summary.filenames_with_differences == []
    assert report_summary.periods_with_differences == []
    assert report_summary.fields_with_differences == []
    assert report_summary.deviation_count == 0


def test_legacy_validation_artifact_manifest_loads_relative_output_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fixture_path = (Path.cwd() / FIXTURE_DIR / "legacy_validation_bundle.json").resolve()
    monkeypatch.chdir(tmp_path)

    result = run_legacy_validation_from_fixture(fixture_path, Path("relative_reports"))
    manifest_path = result.artifacts[-1].path

    loaded_manifest = load_legacy_validation_artifact_manifest(manifest_path)
    assert all(artifact.path.exists() for artifact in loaded_manifest.artifacts)
    assert loaded_manifest.artifact_for_kind("report_json") is not None

    payload = load_legacy_validation_report_payload_from_manifest(manifest_path)
    assert payload["total_rows"] == 40


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


def test_legacy_validation_fixture_rejects_missing_target_level(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    data["targets"][0]["level"] = " "
    fixture_path = tmp_path / "missing_level_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_from_fixture(fixture_path)
    except ValueError as exc:
        assert "level" in str(exc)
    else:
        raise AssertionError("missing level should fail")


def test_legacy_validation_fixture_rejects_missing_selector_kind(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    data["targets"][0]["selector_kind"] = " "
    fixture_path = tmp_path / "missing_selector_kind_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_from_fixture(fixture_path)
    except ValueError as exc:
        assert "selector_kind" in str(exc)
    else:
        raise AssertionError("missing selector_kind should fail")


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


def test_legacy_validation_artifact_manifest_rejects_bad_count(tmp_path: Path) -> None:
    result = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path,
    )
    manifest_path = result.artifacts[-1].path
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["artifact_count"] = 999
    bad_path = tmp_path / "bad_artifacts.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        load_legacy_validation_artifact_manifest(bad_path)
    except ValueError as exc:
        assert "artifact_count" in str(exc)
    else:
        raise AssertionError("bad artifact_count should fail")


def test_legacy_validation_artifact_manifest_rejects_missing_artifact(tmp_path: Path) -> None:
    result = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path,
    )
    missing_path = result.artifacts[1].path
    missing_path.unlink()

    try:
        load_legacy_validation_artifact_manifest(result.artifacts[-1].path)
    except ValueError as exc:
        assert "missing artifacts" in str(exc)
    else:
        raise AssertionError("missing artifact should fail")


def test_legacy_validation_report_payload_rejects_manifest_mismatch(tmp_path: Path) -> None:
    result = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path,
    )
    report_path = result.artifacts[0].path
    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    report_data["total_rows"] = 999
    report_path.write_text(json.dumps(report_data), encoding="utf-8")

    try:
        load_legacy_validation_report_payload_from_manifest(result.artifacts[-1].path)
    except ValueError as exc:
        assert "total_rows" in str(exc)
    else:
        raise AssertionError("report and manifest mismatch should fail")


def test_legacy_validation_report_payload_summary_tracks_deviations(tmp_path: Path) -> None:
    result = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path,
    )
    report_path = result.artifacts[0].path
    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    report_data["matches"] = False
    report_data["matched_rows"] = 39
    report_data["mismatched_rows"] = 1
    report_data["match_rate"] = 0.975
    report_data["files"][1]["matches"] = False
    report_data["files"][1]["matched_rows"] = 9
    report_data["files"][1]["mismatched_rows"] = 1
    report_data["files"][1]["match_rate"] = 0.9
    report_data["files"][1]["periods_with_differences"] = [2]
    report_data["files"][1]["fields_with_differences"] = ["Pr1"]
    report_data["deviation_index"] = [
        {
            "filename": "imsvu014.dat",
            "subject_type": "insurer",
            "level": "I",
            "selector_kind": "entity",
            "selector_value": 14,
            "global_period": 2,
            "field_name": "Pr1",
            "actual": 99.0,
            "expected": 100.0,
        }
    ]
    report_path.write_text(json.dumps(report_data), encoding="utf-8")

    manifest_path = result.artifacts[-1].path
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_data["matches"] = False
    manifest_data["matched_rows"] = 39
    manifest_data["mismatched_rows"] = 1
    manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

    summary = summarize_legacy_validation_report_payload_from_manifest(manifest_path)

    assert summary.matches is False
    assert summary.matched_rows == 39
    assert summary.mismatched_rows == 1
    assert summary.match_rate == 0.975
    assert summary.filenames_with_differences == ["imsvu014.dat"]
    assert summary.periods_with_differences == [2]
    assert summary.fields_with_differences == ["Pr1"]
    assert summary.deviation_count == 1


def test_legacy_validation_report_payload_summary_rejects_bad_files_shape(tmp_path: Path) -> None:
    result = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path,
    )
    report_path = result.artifacts[0].path
    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    report_data["files"] = {}
    report_path.write_text(json.dumps(report_data), encoding="utf-8")

    try:
        summarize_legacy_validation_report_payload_from_manifest(result.artifacts[-1].path)
    except ValueError as exc:
        assert "files must be a list" in str(exc)
    else:
        raise AssertionError("bad files shape should fail")


def test_legacy_validation_report_payload_summary_bundle_from_manifests(tmp_path: Path) -> None:
    first = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "first",
    )
    second = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "second",
    )

    bundle = summarize_legacy_validation_report_payloads_from_manifests(
        [first.artifacts[-1].path, second.artifacts[-1].path]
    )

    assert isinstance(bundle, LegacyValidationReportSummaryBundle)
    assert bundle.report_count == 2
    assert bundle.matches is True
    assert bundle.total_files == 8
    assert bundle.total_rows == 80
    assert bundle.matched_rows == 80
    assert bundle.mismatched_rows == 0
    assert bundle.match_rate == 1.0
    assert bundle.artifact_count == 14
    assert bundle.report_names == ["legacy_validation_bundle", "legacy_validation_bundle"]
    assert bundle.artifact_kinds == [
        "report_json",
        "file_summary_csv",
        "field_summary_csv",
        "group_summary_csv",
        "period_summary_csv",
        "deviation_index_csv",
        "artifact_manifest_json",
    ]
    assert bundle.filenames_with_differences == []
    assert bundle.periods_with_differences == []
    assert bundle.fields_with_differences == []
    assert bundle.deviation_count == 0


def test_legacy_validation_report_payload_summary_bundle_from_directory(tmp_path: Path) -> None:
    run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "first",
    )
    run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "second",
    )

    bundle = summarize_legacy_validation_report_payloads_from_directory(tmp_path)

    assert bundle.report_count == 2
    assert bundle.total_files == 8
    assert bundle.total_rows == 80
    assert bundle.match_rate == 1.0


def test_legacy_validation_report_payload_summary_bundle_tracks_mixed_results(tmp_path: Path) -> None:
    first = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "first",
    )
    second = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "second",
    )
    report_path = second.artifacts[0].path
    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    report_data["matches"] = False
    report_data["matched_rows"] = 39
    report_data["mismatched_rows"] = 1
    report_data["match_rate"] = 0.975
    report_data["files"][1]["matches"] = False
    report_data["files"][1]["matched_rows"] = 9
    report_data["files"][1]["mismatched_rows"] = 1
    report_data["deviation_index"] = [
        {
            "filename": "imsvu014.dat",
            "subject_type": "insurer",
            "level": "I",
            "selector_kind": "entity",
            "selector_value": 14,
            "global_period": 2,
            "field_name": "Pr1",
            "actual": 99.0,
            "expected": 100.0,
        }
    ]
    report_path.write_text(json.dumps(report_data), encoding="utf-8")

    manifest_path = second.artifacts[-1].path
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_data["matches"] = False
    manifest_data["matched_rows"] = 39
    manifest_data["mismatched_rows"] = 1
    manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

    bundle = summarize_legacy_validation_report_payloads_from_manifests(
        [first.artifacts[-1].path, second.artifacts[-1].path]
    )

    assert bundle.matches is False
    assert bundle.total_files == 8
    assert bundle.total_rows == 80
    assert bundle.matched_rows == 79
    assert bundle.mismatched_rows == 1
    assert bundle.match_rate == 79 / 80
    assert bundle.filenames_with_differences == ["imsvu014.dat"]
    assert bundle.periods_with_differences == [2]
    assert bundle.fields_with_differences == ["Pr1"]
    assert bundle.deviation_count == 1


def test_legacy_validation_report_payload_summary_bundle_writes_json_and_csv(tmp_path: Path) -> None:
    first = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "first",
    )
    second = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "second",
    )
    bundle = summarize_legacy_validation_report_payloads_from_manifests(
        [first.artifacts[-1].path, second.artifacts[-1].path]
    )

    json_path = write_legacy_validation_report_summary_bundle_json(
        bundle,
        tmp_path / "bundle_summary.json",
    )
    csv_path = write_legacy_validation_report_summary_bundle_csv(
        bundle,
        tmp_path / "bundle_summary.csv",
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload == legacy_validation_report_summary_bundle_to_dict(bundle)
    assert payload["report_count"] == 2
    assert payload["total_files"] == 8
    assert payload["total_rows"] == 80
    assert payload["summaries"][0] == legacy_validation_report_payload_summary_to_dict(
        bundle.summaries[0]
    )

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["report_name"] == "legacy_validation_bundle"
    assert rows[0]["matches"] == "True"
    assert rows[0]["total_files"] == "4"
    assert rows[0]["total_rows"] == "40"
    assert rows[0]["match_rate"] == "1.000000"
    assert rows[0]["artifact_count"] == "7"
    assert rows[0]["deviation_count"] == "0"


def test_legacy_validation_report_summary_bundle_artifacts_roundtrip(tmp_path: Path) -> None:
    first = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "first",
    )
    second = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "second",
    )
    bundle = summarize_legacy_validation_report_payloads_from_manifests(
        [first.artifacts[-1].path, second.artifacts[-1].path]
    )

    manifest = write_legacy_validation_report_summary_bundle_artifacts(
        bundle,
        tmp_path / "bundle",
        bundle_name="validation_batch",
    )

    assert isinstance(manifest, LegacyValidationReportSummaryBundleArtifactManifest)
    assert manifest.bundle_name == "validation_batch"
    assert manifest.matches is True
    assert manifest.report_count == 2
    assert manifest.total_files == 8
    assert manifest.total_rows == 80
    assert manifest.artifact_count == 3
    assert [artifact.kind for artifact in manifest.artifacts] == [
        "summary_bundle_json",
        "summary_bundle_csv",
        "summary_bundle_manifest_json",
    ]
    assert [artifact.path.name for artifact in manifest.artifacts] == [
        "validation_batch.json",
        "validation_batch.csv",
        "validation_batch_artifacts.json",
    ]

    loaded_manifest = load_legacy_validation_report_summary_bundle_artifact_manifest(
        tmp_path / "bundle" / "validation_batch_artifacts.json"
    )
    assert loaded_manifest.bundle_name == "validation_batch"
    assert loaded_manifest.total_rows == 80
    assert loaded_manifest.artifact_for_kind("summary_bundle_json") is not None
    assert loaded_manifest.artifact_for_kind("unknown") is None

    payload = load_legacy_validation_report_summary_bundle_payload_from_manifest(
        tmp_path / "bundle" / "validation_batch_artifacts.json"
    )
    assert payload == legacy_validation_report_summary_bundle_to_dict(bundle)


def test_legacy_validation_report_summary_bundle_manifest_loads_relative_output_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fixture_path = (Path.cwd() / FIXTURE_DIR / "legacy_validation_bundle.json").resolve()
    monkeypatch.chdir(tmp_path)
    result = run_legacy_validation_from_fixture(fixture_path, Path("run"))
    bundle = summarize_legacy_validation_report_payloads_from_manifests(
        [result.artifacts[-1].path]
    )

    manifest = write_legacy_validation_report_summary_bundle_artifacts(
        bundle,
        Path("bundle"),
        bundle_name="relative_batch",
    )

    loaded_manifest = load_legacy_validation_report_summary_bundle_artifact_manifest(
        manifest.artifacts[-1].path
    )
    assert all(artifact.path.exists() for artifact in loaded_manifest.artifacts)
    payload = load_legacy_validation_report_summary_bundle_payload_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload["total_rows"] == 40


def test_legacy_validation_report_summary_bundle_manifest_rejects_missing_artifact(tmp_path: Path) -> None:
    result = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "run",
    )
    bundle = summarize_legacy_validation_report_payloads_from_manifests(
        [result.artifacts[-1].path]
    )
    manifest = write_legacy_validation_report_summary_bundle_artifacts(bundle, tmp_path / "bundle")
    manifest.artifacts[1].path.unlink()

    try:
        load_legacy_validation_report_summary_bundle_artifact_manifest(manifest.artifacts[-1].path)
    except ValueError as exc:
        assert "missing artifacts" in str(exc)
    else:
        raise AssertionError("missing bundle artifact should fail")


def test_legacy_validation_report_summary_bundle_payload_rejects_manifest_mismatch(tmp_path: Path) -> None:
    result = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "run",
    )
    bundle = summarize_legacy_validation_report_payloads_from_manifests(
        [result.artifacts[-1].path]
    )
    manifest = write_legacy_validation_report_summary_bundle_artifacts(bundle, tmp_path / "bundle")
    payload_path = manifest.artifacts[0].path
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload["total_rows"] = 999
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_report_summary_bundle_payload_from_manifest(manifest.artifacts[-1].path)
    except ValueError as exc:
        assert "total_rows" in str(exc)
    else:
        raise AssertionError("bundle payload and manifest mismatch should fail")


def test_legacy_validation_report_summary_bundle_artifacts_from_manifests(tmp_path: Path) -> None:
    first = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "first",
    )
    second = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "second",
    )

    manifest = write_legacy_validation_report_summary_bundle_artifacts_from_manifests(
        [first.artifacts[-1].path, second.artifacts[-1].path],
        tmp_path / "bundle",
        bundle_name="batch_from_manifests",
    )

    assert manifest.bundle_name == "batch_from_manifests"
    assert manifest.report_count == 2
    assert manifest.total_files == 8
    assert manifest.total_rows == 80
    payload = load_legacy_validation_report_summary_bundle_payload_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload["report_count"] == 2
    assert payload["total_rows"] == 80
    assert [artifact.path.name for artifact in manifest.artifacts] == [
        "batch_from_manifests.json",
        "batch_from_manifests.csv",
        "batch_from_manifests_artifacts.json",
    ]


def test_legacy_validation_report_summary_bundle_artifacts_from_directory(tmp_path: Path) -> None:
    run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "runs" / "first",
    )
    run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "runs" / "second",
    )

    manifest = write_legacy_validation_report_summary_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "bundle",
        bundle_name="batch_from_directory",
    )

    assert manifest.bundle_name == "batch_from_directory"
    assert manifest.report_count == 2
    assert manifest.total_files == 8
    assert manifest.total_rows == 80
    assert manifest.matched_rows == 80
    assert manifest.artifact_count == 3
    assert all(artifact.path.exists() for artifact in manifest.artifacts)


def test_legacy_validation_report_summary_bundle_directory_scan_ignores_summary_manifests(
    tmp_path: Path,
) -> None:
    run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "runs" / "first",
    )
    run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "runs" / "second",
    )
    write_legacy_validation_report_summary_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "runs" / "summary",
        bundle_name="existing_summary",
    )

    bundle = summarize_legacy_validation_report_payloads_from_directory(tmp_path / "runs")

    assert bundle.report_count == 2
    assert bundle.total_files == 8
    assert bundle.total_rows == 80


def test_legacy_validation_report_summary_bundle_artifacts_from_directory_rejects_empty_input(
    tmp_path: Path,
) -> None:
    try:
        write_legacy_validation_report_summary_bundle_artifacts_from_directory(
            tmp_path,
            tmp_path / "bundle",
        )
    except ValueError as exc:
        assert "contains no manifests" in str(exc)
    else:
        raise AssertionError("empty input directory should fail")


def test_legacy_validation_batch_fixture_runs_items_and_writes_summary(tmp_path: Path) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )

    assert isinstance(result, LegacyValidationBatchRunResult)
    assert result.batch_name == "legacy_validation_batch"
    assert [item.name for item in result.runs] == [
        "legacy_validation_bundle_a",
        "legacy_validation_bundle_b",
    ]
    assert all(isinstance(item, LegacyValidationBatchRunItem) for item in result.runs)
    assert [item.output_dir.name for item in result.runs] == ["bundle_a", "bundle_b"]
    assert [item.result.report.total_rows for item in result.runs] == [40, 40]
    assert [item.result.report.matches for item in result.runs] == [True, True]

    summary_manifest = result.summary_manifest
    assert summary_manifest.bundle_name == "legacy_validation_batch"
    assert summary_manifest.report_count == 2
    assert summary_manifest.total_files == 8
    assert summary_manifest.total_rows == 80
    assert summary_manifest.matched_rows == 80
    assert summary_manifest.artifact_count == 3
    assert [artifact.path.name for artifact in summary_manifest.artifacts] == [
        "legacy_validation_batch.json",
        "legacy_validation_batch.csv",
        "legacy_validation_batch_artifacts.json",
    ]
    assert all(artifact.path.exists() for artifact in summary_manifest.artifacts)

    payload = load_legacy_validation_report_summary_bundle_payload_from_manifest(
        summary_manifest.artifacts[-1].path
    )
    assert payload["report_count"] == 2
    assert payload["total_rows"] == 80
    assert payload["report_names"] == [
        "legacy_validation_bundle",
        "legacy_validation_bundle",
    ]


def test_legacy_validation_batch_fixture_rejects_duplicate_output_dirs(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_batch.json").read_text(encoding="utf-8"))
    data["items"][1]["output_subdir"] = data["items"][0]["output_subdir"]
    fixture_path = tmp_path / "bad_batch.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_batch_from_fixture(fixture_path, tmp_path / "out")
    except ValueError as exc:
        assert "duplicate output_subdir" in str(exc)
    else:
        raise AssertionError("duplicate batch output_subdir should fail")


def test_legacy_validation_batch_fixture_rejects_absolute_output_dir(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_batch.json").read_text(encoding="utf-8"))
    data["items"][0]["output_subdir"] = str(tmp_path / "absolute")
    fixture_path = tmp_path / "bad_batch.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    try:
        run_legacy_validation_batch_from_fixture(fixture_path, tmp_path / "out")
    except ValueError as exc:
        assert "output_subdir must be relative" in str(exc)
    else:
        raise AssertionError("absolute batch output_subdir should fail")


def test_legacy_validation_report_payload_summary_bundle_rejects_empty_inputs(tmp_path: Path) -> None:
    try:
        summarize_legacy_validation_report_payloads_from_manifests([])
    except ValueError as exc:
        assert "at least one manifest path" in str(exc)
    else:
        raise AssertionError("empty manifest paths should fail")

    try:
        summarize_legacy_validation_report_payloads_from_directory(tmp_path)
    except ValueError as exc:
        assert "contains no manifests" in str(exc)
    else:
        raise AssertionError("empty manifest directory should fail")


def test_legacy_validation_fixture_import_shapes() -> None:
    assert LegacyValidationArtifact is not None
    assert LegacyValidationArtifactManifest is not None
    assert LegacyValidationBatchRunItem is not None
    assert LegacyValidationBatchRunResult is not None
    assert LegacyValidationReportPayloadSummary is not None
    assert LegacyValidationReportSummaryBundle is not None
    assert LegacyValidationReportSummaryBundleArtifactManifest is not None
    assert LegacyValidationRunResult is not None
    assert LegacyValidationTarget is not None
    assert build_legacy_validation_report_summary_bundle is not None
    assert legacy_validation_report_payload_summary_to_dict is not None
    assert legacy_validation_report_summary_bundle_to_dict is not None
    assert load_legacy_validation_artifact_manifest is not None
    assert load_legacy_validation_report_payload_from_manifest is not None
    assert load_legacy_validation_report_summary_bundle_artifact_manifest is not None
    assert load_legacy_validation_report_summary_bundle_payload_from_manifest is not None
    assert run_legacy_validation_batch_from_fixture is not None
    assert run_legacy_validation_from_fixture is not None
    assert summarize_legacy_validation_report_payload_from_manifest is not None
    assert summarize_legacy_validation_report_payloads_from_directory is not None
    assert summarize_legacy_validation_report_payloads_from_manifests is not None
    assert write_legacy_validation_report_summary_bundle_artifacts is not None
    assert write_legacy_validation_report_summary_bundle_artifacts_from_directory is not None
    assert write_legacy_validation_report_summary_bundle_artifacts_from_manifests is not None
    assert write_legacy_validation_report_summary_bundle_csv is not None
    assert write_legacy_validation_report_summary_bundle_json is not None
