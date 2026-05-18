import csv
import json
from pathlib import Path

from ims.model.legacy_validation_run import (
    LegacyValidationArtifact,
    LegacyValidationArtifactManifest,
    LegacyValidationBatchRunManifestCheck,
    LegacyValidationBatchRunManifestCheckBundleArtifactManifest,
    LegacyValidationBatchRunManifestCheckBundle,
    LegacyValidationBatchRunManifestIssue,
    LegacyValidationBatchRunManifestCheckPayloadSummary,
    LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest,
    LegacyValidationBatchRunManifestCheckPayloadSummaryBundle,
    LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest,
    LegacyValidationAcceptanceVerdict,
    LegacyValidationAcceptanceVerdictArtifactManifest,
    LegacyValidationReportPayloadSummary,
    LegacyValidationReportSummaryBundle,
    LegacyValidationReportSummaryBundleArtifactManifest,
    LegacyValidationBatchRunItem,
    LegacyValidationBatchRunResult,
    LegacyValidationRunResult,
    LegacyValidationTarget,
    check_legacy_validation_batch_run_manifests,
    check_legacy_validation_batch_run_manifests_from_directory,
    build_legacy_validation_batch_run_manifest_check_payload_summary,
    build_legacy_validation_batch_run_manifest_check_payload_summary_bundle,
    build_legacy_validation_acceptance_verdict,
    build_legacy_validation_acceptance_verdict_from_summary_bundle_manifest,
    build_legacy_validation_report_summary_bundle,
    check_legacy_validation_batch_run_manifest,
    legacy_validation_batch_run_manifest_check_bundle_to_dict,
    legacy_validation_batch_run_manifest_check_payload_summary_bundle_to_dict,
    legacy_validation_batch_run_manifest_check_payload_summary_to_dict,
    legacy_validation_acceptance_verdict_to_dict,
    legacy_validation_batch_run_manifest_check_to_dict,
    legacy_validation_batch_run_result_to_dict,
    legacy_validation_report_payload_summary_to_dict,
    legacy_validation_report_summary_bundle_to_dict,
    load_legacy_validation_batch_run_manifest,
    load_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest,
    load_legacy_validation_batch_run_manifest_check_bundle_payload_from_manifest,
    load_legacy_validation_batch_run_manifest_check_bundle_payloads_from_directory,
    load_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest,
    load_legacy_validation_batch_run_manifest_check_payload_summary_from_manifest,
    load_legacy_validation_batch_run_manifest_check_payload_summary_payloads_from_directory,
    load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifact_manifest,
    load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest,
    load_legacy_validation_acceptance_verdict_artifact_manifest,
    load_legacy_validation_acceptance_verdict_from_manifest,
    load_legacy_validation_artifact_manifest,
    load_legacy_validation_report_payload_from_manifest,
    load_legacy_validation_report_summary_bundle_artifact_manifest,
    load_legacy_validation_report_summary_bundle_payload_from_manifest,
    run_legacy_validation_batch_from_fixture,
    run_legacy_validation_from_fixture,
    summarize_legacy_validation_report_payload_from_manifest,
    summarize_legacy_validation_batch_run_manifest_check_payloads_from_directory,
    summarize_legacy_validation_batch_run_manifest_check_payload_summaries_from_directory,
    summarize_legacy_validation_report_payloads_from_directory,
    summarize_legacy_validation_report_payloads_from_manifests,
    write_legacy_validation_report_summary_bundle_artifacts,
    write_legacy_validation_report_summary_bundle_artifacts_from_directory,
    write_legacy_validation_report_summary_bundle_artifacts_from_manifests,
    write_legacy_validation_report_summary_bundle_csv,
    write_legacy_validation_report_summary_bundle_json,
    write_legacy_validation_batch_run_manifest,
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts,
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory,
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_manifests,
    write_legacy_validation_batch_run_manifest_check_bundle_csv,
    write_legacy_validation_batch_run_manifest_check_bundle_json,
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts,
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory,
    write_legacy_validation_batch_run_manifest_check_payload_summary_csv,
    write_legacy_validation_batch_run_manifest_check_payload_summary_json,
    write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts,
    write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts_from_directory,
    write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_csv,
    write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_json,
    write_legacy_validation_acceptance_verdict_artifacts,
    write_legacy_validation_acceptance_verdict_artifacts_from_summary_bundle_manifest,
    write_legacy_validation_acceptance_verdict_csv,
    write_legacy_validation_acceptance_verdict_json,
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


def test_legacy_validation_artifact_manifest_prefers_manifest_relative_paths(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_from_fixture(
        FIXTURE_DIR / "legacy_validation_bundle.json",
        tmp_path / "report",
    )
    manifest_path = result.artifacts[-1].path
    stale_report_path = Path("legacy_validation_bundle.json")
    stale_report_path.write_text(
        json.dumps(
            {
                "matches": False,
                "total_files": 999,
                "total_rows": 999,
                "matched_rows": 0,
                "mismatched_rows": 999,
            }
        ),
        encoding="utf-8",
    )
    try:
        payload = load_legacy_validation_report_payload_from_manifest(manifest_path)
    finally:
        stale_report_path.unlink()

    assert payload["matches"] is True
    assert payload["total_files"] == 4
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

    batch_manifest_payload = load_legacy_validation_batch_run_manifest(
        result.batch_manifest_path
    )
    assert batch_manifest_payload["batch_name"] == "legacy_validation_batch"
    assert batch_manifest_payload["run_count"] == 2
    assert batch_manifest_payload["total_rows"] == 80
    assert batch_manifest_payload["summary_manifest_path"] == str(
        Path("summary") / "legacy_validation_batch_artifacts.json"
    )
    assert [item["name"] for item in batch_manifest_payload["runs"]] == [
        "legacy_validation_bundle_a",
        "legacy_validation_bundle_b",
    ]
    assert batch_manifest_payload["runs"][0]["report_manifest_path"] == str(
        Path("bundle_a") / "legacy_validation_bundle_artifacts.json"
    )
    assert legacy_validation_batch_run_result_to_dict(
        result,
        manifest_base_path=tmp_path,
    )["run_count"] == 2


def test_legacy_validation_batch_manifest_check_reports_valid_manifest(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )

    check = check_legacy_validation_batch_run_manifest(result.batch_manifest_path)

    assert isinstance(check, LegacyValidationBatchRunManifestCheck)
    assert check.matches is True
    assert check.run_count == 2
    assert check.checked_artifact_count == 7
    assert check.issues == []
    assert legacy_validation_batch_run_manifest_check_to_dict(check) == {
        "manifest_path": str(result.batch_manifest_path.resolve()),
        "matches": True,
        "run_count": 2,
        "checked_artifact_count": 7,
        "issues": [],
    }


def test_legacy_validation_batch_manifest_check_reports_invalid_manifest(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["total_rows"] = 999
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    check = check_legacy_validation_batch_run_manifest(result.batch_manifest_path)

    assert check.matches is False
    assert check.run_count == 0
    assert check.checked_artifact_count == 0
    assert len(check.issues) == 1
    assert isinstance(check.issues[0], LegacyValidationBatchRunManifestIssue)
    assert check.issues[0].code == "batch_run_manifest_invalid"
    assert "report manifest field total_rows" in check.issues[0].message
    assert check.issues[0].path == result.batch_manifest_path.resolve()
    payload = legacy_validation_batch_run_manifest_check_to_dict(check)
    assert payload["matches"] is False
    assert payload["issues"][0]["code"] == "batch_run_manifest_invalid"


def test_legacy_validation_batch_manifest_check_bundle_from_manifests(
    tmp_path: Path,
) -> None:
    first = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "first",
    )
    second = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "second",
    )

    bundle = check_legacy_validation_batch_run_manifests(
        [first.batch_manifest_path, second.batch_manifest_path]
    )

    assert isinstance(bundle, LegacyValidationBatchRunManifestCheckBundle)
    assert bundle.matches is True
    assert bundle.manifest_count == 2
    assert bundle.total_runs == 4
    assert bundle.checked_artifact_count == 14
    assert bundle.issue_count == 0
    payload = legacy_validation_batch_run_manifest_check_bundle_to_dict(bundle)
    assert payload["manifest_count"] == 2
    assert payload["checks"][0]["matches"] is True


def test_legacy_validation_batch_manifest_check_bundle_tracks_mixed_results(
    tmp_path: Path,
) -> None:
    first = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "first",
    )
    second = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "second",
    )
    payload = json.loads(second.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["total_rows"] = 999
    second.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    bundle = check_legacy_validation_batch_run_manifests(
        [first.batch_manifest_path, second.batch_manifest_path]
    )

    assert bundle.matches is False
    assert bundle.manifest_count == 2
    assert bundle.total_runs == 2
    assert bundle.checked_artifact_count == 7
    assert bundle.issue_count == 1
    assert bundle.checks[1].issues[0].code == "batch_run_manifest_invalid"


def test_legacy_validation_batch_manifest_check_bundle_from_directory_writes_json(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "first",
    )
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "second",
    )

    bundle = check_legacy_validation_batch_run_manifests_from_directory(tmp_path)
    json_path = write_legacy_validation_batch_run_manifest_check_bundle_json(
        bundle,
        tmp_path / "diagnostics" / "batch_manifest_checks.json",
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["matches"] is True
    assert payload["manifest_count"] == 2
    assert payload["total_runs"] == 4
    assert payload["checked_artifact_count"] == 14


def test_legacy_validation_batch_manifest_check_bundle_writes_csv(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "first",
    )
    second = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "second",
    )
    payload = json.loads(second.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["total_rows"] = 999
    second.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    bundle = check_legacy_validation_batch_run_manifests_from_directory(tmp_path)
    csv_path = write_legacy_validation_batch_run_manifest_check_bundle_csv(
        bundle,
        tmp_path / "diagnostics" / "batch_manifest_checks.csv",
    )

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 2
    assert rows[0]["matches"] == "True"
    assert rows[0]["issue_count"] == "0"
    assert rows[1]["matches"] == "False"
    assert rows[1]["issue_count"] == "1"
    assert rows[1]["issue_codes"] == "batch_run_manifest_invalid"
    assert "report manifest field total_rows" in rows[1]["issue_messages"]


def test_legacy_validation_batch_manifest_check_bundle_artifacts_roundtrip(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "first",
    )
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "second",
    )
    bundle = check_legacy_validation_batch_run_manifests_from_directory(tmp_path)

    manifest = write_legacy_validation_batch_run_manifest_check_bundle_artifacts(
        bundle,
        tmp_path / "diagnostics",
        bundle_name="batch_manifest_checks",
    )

    assert isinstance(manifest, LegacyValidationBatchRunManifestCheckBundleArtifactManifest)
    assert manifest.bundle_name == "batch_manifest_checks"
    assert manifest.matches is True
    assert manifest.manifest_count == 2
    assert manifest.total_runs == 4
    assert manifest.checked_artifact_count == 14
    assert manifest.issue_count == 0
    assert [artifact.kind for artifact in manifest.artifacts] == [
        "batch_manifest_check_bundle_json",
        "batch_manifest_check_bundle_csv",
        "batch_manifest_check_bundle_manifest_json",
    ]
    assert all(artifact.path.exists() for artifact in manifest.artifacts)

    loaded_manifest = load_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest(
        manifest.artifacts[-1].path
    )
    assert loaded_manifest.manifest_count == 2
    assert loaded_manifest.artifact_for_kind("batch_manifest_check_bundle_json") is not None
    payload = load_legacy_validation_batch_run_manifest_check_bundle_payload_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload == legacy_validation_batch_run_manifest_check_bundle_to_dict(bundle)


def test_legacy_validation_batch_manifest_check_bundle_artifacts_from_manifests(
    tmp_path: Path,
) -> None:
    first = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "first",
    )
    second = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "second",
    )

    manifest = write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_manifests(
        [first.batch_manifest_path, second.batch_manifest_path],
        tmp_path / "diagnostics",
        bundle_name="batch_manifest_checks_from_manifests",
    )

    assert manifest.bundle_name == "batch_manifest_checks_from_manifests"
    assert manifest.matches is True
    assert manifest.manifest_count == 2
    assert manifest.total_runs == 4
    payload = load_legacy_validation_batch_run_manifest_check_bundle_payload_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload["manifest_count"] == 2
    assert [artifact.path.name for artifact in manifest.artifacts] == [
        "batch_manifest_checks_from_manifests.json",
        "batch_manifest_checks_from_manifests.csv",
        "batch_manifest_checks_from_manifests_artifacts.json",
    ]


def test_legacy_validation_batch_manifest_check_bundle_artifacts_from_directory(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "first",
    )
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "second",
    )

    manifest = write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics",
        bundle_name="batch_manifest_checks_from_directory",
    )

    assert manifest.bundle_name == "batch_manifest_checks_from_directory"
    assert manifest.matches is True
    assert manifest.manifest_count == 2
    assert manifest.total_runs == 4
    payload = load_legacy_validation_batch_run_manifest_check_bundle_payload_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload["checked_artifact_count"] == 14


def test_legacy_validation_batch_manifest_check_bundle_manifest_rejects_missing_artifact(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "first",
    )
    bundle = check_legacy_validation_batch_run_manifests_from_directory(tmp_path)
    manifest = write_legacy_validation_batch_run_manifest_check_bundle_artifacts(
        bundle,
        tmp_path / "diagnostics",
    )
    manifest.artifacts[0].path.unlink()

    try:
        load_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest(
            manifest.artifacts[-1].path
        )
    except ValueError as exc:
        assert "missing artifacts" in str(exc)
    else:
        raise AssertionError("missing diagnostic bundle artifact should fail")


def test_legacy_validation_batch_manifest_check_bundle_payload_rejects_manifest_mismatch(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "first",
    )
    bundle = check_legacy_validation_batch_run_manifests_from_directory(tmp_path)
    manifest = write_legacy_validation_batch_run_manifest_check_bundle_artifacts(
        bundle,
        tmp_path / "diagnostics",
    )
    json_artifact = manifest.artifact_for_kind("batch_manifest_check_bundle_json")
    assert json_artifact is not None
    payload = json.loads(json_artifact.path.read_text(encoding="utf-8"))
    payload["manifest_count"] = 999
    json_artifact.path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest_check_bundle_payload_from_manifest(
            manifest.artifacts[-1].path
        )
    except ValueError as exc:
        assert "manifest field manifest_count" in str(exc)
    else:
        raise AssertionError("diagnostic bundle payload mismatch should fail")


def test_legacy_validation_batch_manifest_check_bundle_payloads_from_directory(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "first",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "first",
        bundle_name="first_checks",
    )
    write_legacy_validation_report_summary_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "summary",
        bundle_name="summary_bundle",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "second",
        bundle_name="second_checks",
    )

    payloads = load_legacy_validation_batch_run_manifest_check_bundle_payloads_from_directory(
        tmp_path / "diagnostics"
    )

    assert [payload["manifest_count"] for payload in payloads] == [1, 1]
    assert [payload["total_runs"] for payload in payloads] == [2, 2]
    assert all(payload["matches"] is True for payload in payloads)


def test_legacy_validation_batch_manifest_check_payload_summary_from_directory(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "first",
    )
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "other_runs" / "second",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "first",
        bundle_name="first_checks",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "other_runs",
        tmp_path / "diagnostics" / "second",
        bundle_name="second_checks",
    )

    summary = summarize_legacy_validation_batch_run_manifest_check_payloads_from_directory(
        tmp_path / "diagnostics"
    )

    assert isinstance(summary, LegacyValidationBatchRunManifestCheckPayloadSummary)
    assert summary.bundle_count == 2
    assert summary.matches is True
    assert summary.manifest_count == 2
    assert summary.total_runs == 4
    assert summary.checked_artifact_count == 14
    assert summary.issue_count == 0
    assert summary.failing_bundle_count == 0
    assert legacy_validation_batch_run_manifest_check_payload_summary_to_dict(summary) == {
        "bundle_count": 2,
        "matches": True,
        "manifest_count": 2,
        "total_runs": 4,
        "checked_artifact_count": 14,
        "issue_count": 0,
        "failing_bundle_count": 0,
    }


def test_legacy_validation_batch_manifest_check_payload_summary_tracks_failures(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs",
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["total_rows"] = 999
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics",
        bundle_name="checks",
    )

    payloads = load_legacy_validation_batch_run_manifest_check_bundle_payloads_from_directory(
        tmp_path / "diagnostics"
    )
    summary = build_legacy_validation_batch_run_manifest_check_payload_summary(payloads)

    assert summary.matches is False
    assert summary.bundle_count == 1
    assert summary.failing_bundle_count == 1
    assert summary.issue_count == 1


def test_legacy_validation_batch_manifest_check_payload_summary_artifacts(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "first",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "first",
        bundle_name="first_checks",
    )
    summary = summarize_legacy_validation_batch_run_manifest_check_payloads_from_directory(
        tmp_path / "diagnostics"
    )

    manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts(
        summary,
        tmp_path / "summary_artifacts",
        bundle_name="diagnostic_payload_summary",
    )

    assert isinstance(
        manifest,
        LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest,
    )
    assert manifest.bundle_name == "diagnostic_payload_summary"
    assert manifest.matches is True
    assert manifest.bundle_count == 1
    assert manifest.manifest_count == 1
    assert manifest.total_runs == 2
    assert manifest.checked_artifact_count == 7
    assert manifest.issue_count == 0
    assert manifest.failing_bundle_count == 0
    assert [artifact.path.name for artifact in manifest.artifacts] == [
        "diagnostic_payload_summary.json",
        "diagnostic_payload_summary.csv",
        "diagnostic_payload_summary_artifacts.json",
    ]
    loaded_manifest = load_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest(
        manifest.artifacts[-1].path
    )
    assert loaded_manifest.artifact_count == 3
    payload = load_legacy_validation_batch_run_manifest_check_payload_summary_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload == legacy_validation_batch_run_manifest_check_payload_summary_to_dict(
        summary
    )

    with manifest.artifacts[1].path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows == [
        {
            "matches": "True",
            "bundle_count": "1",
            "manifest_count": "1",
            "total_runs": "2",
            "checked_artifact_count": "7",
            "issue_count": "0",
            "failing_bundle_count": "0",
        }
    ]


def test_legacy_validation_batch_manifest_check_payload_summary_artifacts_from_directory(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "first",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "first",
        bundle_name="first_checks",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "second",
        bundle_name="second_checks",
    )

    manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics",
        tmp_path / "summary_artifacts",
        bundle_name="diagnostic_payload_summary",
    )

    assert manifest.matches is True
    assert manifest.bundle_count == 2
    assert manifest.manifest_count == 2
    assert manifest.total_runs == 4
    assert manifest.checked_artifact_count == 14
    payload = load_legacy_validation_batch_run_manifest_check_payload_summary_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload["bundle_count"] == 2
    assert payload["total_runs"] == 4


def test_legacy_validation_batch_manifest_check_payload_summary_payload_rejects_manifest_mismatch(
    tmp_path: Path,
) -> None:
    summary = build_legacy_validation_batch_run_manifest_check_payload_summary(
        [
            {
                "matches": True,
                "manifest_count": 1,
                "total_runs": 2,
                "checked_artifact_count": 7,
                "issue_count": 0,
            }
        ]
    )
    manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts(
        summary,
        tmp_path / "summary_artifacts",
    )
    json_artifact = manifest.artifact_for_kind(
        "batch_manifest_check_payload_summary_json"
    )
    assert json_artifact is not None
    payload = json.loads(json_artifact.path.read_text(encoding="utf-8"))
    payload["total_runs"] = 999
    json_artifact.path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest_check_payload_summary_from_manifest(
            manifest.artifacts[-1].path
        )
    except ValueError as exc:
        assert "manifest field total_runs" in str(exc)
    else:
        raise AssertionError("diagnostic payload summary mismatch should fail")


def test_legacy_validation_batch_manifest_check_payload_summary_bundle_from_directory(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "first",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "first",
        bundle_name="first_checks",
    )
    first_manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics" / "first",
        tmp_path / "summary_artifacts" / "first",
        bundle_name="first_payload_summary",
    )

    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "second",
        bundle_name="second_checks",
    )
    second_manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics",
        tmp_path / "summary_artifacts" / "second",
        bundle_name="second_payload_summary",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "summary_artifacts" / "unrelated_diagnostic_bundle",
        bundle_name="ignored_check_bundle",
    )

    payloads = load_legacy_validation_batch_run_manifest_check_payload_summary_payloads_from_directory(
        tmp_path / "summary_artifacts"
    )
    bundle = summarize_legacy_validation_batch_run_manifest_check_payload_summaries_from_directory(
        tmp_path / "summary_artifacts"
    )

    assert len(payloads) == 2
    assert isinstance(bundle, LegacyValidationBatchRunManifestCheckPayloadSummaryBundle)
    assert bundle.summary_count == 2
    assert bundle.matches is True
    assert bundle.bundle_count == 3
    assert bundle.manifest_count == 3
    assert bundle.total_runs == 6
    assert bundle.checked_artifact_count == 21
    assert bundle.issue_count == 0
    assert bundle.failing_bundle_count == 0
    assert bundle.failing_summary_count == 0
    assert bundle.manifest_paths == [
        first_manifest.artifacts[-1].path,
        second_manifest.artifacts[-1].path,
    ]
    payload = legacy_validation_batch_run_manifest_check_payload_summary_bundle_to_dict(
        bundle
    )
    assert payload["summary_count"] == 2
    assert payload["bundle_count"] == 3
    assert [summary["bundle_count"] for summary in payload["summaries"]] == [1, 2]


def test_legacy_validation_batch_manifest_check_payload_summary_bundle_tracks_failures(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "good_runs",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "good_runs",
        tmp_path / "diagnostics" / "good",
        bundle_name="good_checks",
    )
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics" / "good",
        tmp_path / "summary_artifacts" / "good",
        bundle_name="good_payload_summary",
    )

    bad_result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "bad_runs",
    )
    payload = json.loads(bad_result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["total_rows"] = 999
    bad_result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "bad_runs",
        tmp_path / "diagnostics" / "bad",
        bundle_name="bad_checks",
    )
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics" / "bad",
        tmp_path / "summary_artifacts" / "bad",
        bundle_name="bad_payload_summary",
    )

    bundle = summarize_legacy_validation_batch_run_manifest_check_payload_summaries_from_directory(
        tmp_path / "summary_artifacts"
    )

    assert bundle.matches is False
    assert bundle.summary_count == 2
    assert bundle.failing_summary_count == 1
    assert bundle.failing_bundle_count == 1
    assert bundle.issue_count == 1


def test_legacy_validation_batch_manifest_check_payload_summary_bundle_artifacts(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "first",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "first",
        bundle_name="first_checks",
    )
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics" / "first",
        tmp_path / "summary_artifacts" / "first",
        bundle_name="first_payload_summary",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "second",
        bundle_name="second_checks",
    )
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics",
        tmp_path / "summary_artifacts" / "second",
        bundle_name="second_payload_summary",
    )
    bundle = summarize_legacy_validation_batch_run_manifest_check_payload_summaries_from_directory(
        tmp_path / "summary_artifacts"
    )

    manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts(
        bundle,
        tmp_path / "bundle_artifacts",
        bundle_name="summary_acceptance_bundle",
    )

    assert isinstance(
        manifest,
        LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest,
    )
    assert manifest.bundle_name == "summary_acceptance_bundle"
    assert manifest.matches is True
    assert manifest.summary_count == 2
    assert manifest.bundle_count == 3
    assert manifest.manifest_count == 3
    assert manifest.total_runs == 6
    assert manifest.checked_artifact_count == 21
    assert manifest.issue_count == 0
    assert manifest.failing_bundle_count == 0
    assert manifest.failing_summary_count == 0
    assert [artifact.path.name for artifact in manifest.artifacts] == [
        "summary_acceptance_bundle.json",
        "summary_acceptance_bundle.csv",
        "summary_acceptance_bundle_artifacts.json",
    ]
    loaded_manifest = load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifact_manifest(
        manifest.artifacts[-1].path
    )
    assert loaded_manifest.artifact_count == 3
    payload = load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload == legacy_validation_batch_run_manifest_check_payload_summary_bundle_to_dict(
        bundle
    )

    with manifest.artifacts[1].path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["bundle_count"] for row in rows] == ["1", "2"]
    assert [row["total_runs"] for row in rows] == ["2", "4"]


def test_legacy_validation_batch_manifest_check_payload_summary_bundle_artifacts_from_directory(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "first",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "first",
        bundle_name="first_checks",
    )
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics" / "first",
        tmp_path / "summary_artifacts" / "first",
        bundle_name="first_payload_summary",
    )

    manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts_from_directory(
        tmp_path / "summary_artifacts",
        tmp_path / "bundle_artifacts",
        bundle_name="summary_acceptance_bundle",
    )

    assert manifest.matches is True
    assert manifest.summary_count == 1
    assert manifest.bundle_count == 1
    assert manifest.total_runs == 2
    payload = load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload["summary_count"] == 1
    assert payload["total_runs"] == 2


def test_legacy_validation_batch_manifest_check_payload_summary_bundle_rejects_manifest_mismatch(
    tmp_path: Path,
) -> None:
    bundle = build_legacy_validation_batch_run_manifest_check_payload_summary_bundle(
        [
            {
                "matches": True,
                "bundle_count": 1,
                "manifest_count": 1,
                "total_runs": 2,
                "checked_artifact_count": 7,
                "issue_count": 0,
                "failing_bundle_count": 0,
            }
        ]
    )
    manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts(
        bundle,
        tmp_path / "bundle_artifacts",
    )
    json_artifact = manifest.artifact_for_kind(
        "batch_manifest_check_payload_summary_bundle_json"
    )
    assert json_artifact is not None
    payload = json.loads(json_artifact.path.read_text(encoding="utf-8"))
    payload["summary_count"] = 999
    json_artifact.path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest(
            manifest.artifacts[-1].path
        )
    except ValueError as exc:
        assert "manifest field summary_count" in str(exc)
    else:
        raise AssertionError("diagnostic payload summary bundle mismatch should fail")


def test_legacy_validation_acceptance_verdict_passes_for_clean_summary_bundle(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs" / "first",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics" / "first",
        bundle_name="first_checks",
    )
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics" / "first",
        tmp_path / "summary_artifacts" / "first",
        bundle_name="first_payload_summary",
    )
    summary_bundle_manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts_from_directory(
        tmp_path / "summary_artifacts",
        tmp_path / "summary_bundle",
        bundle_name="summary_bundle",
    )
    bundle_payload = load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest(
        summary_bundle_manifest.artifacts[-1].path
    )
    bundle = build_legacy_validation_batch_run_manifest_check_payload_summary_bundle(
        bundle_payload["summaries"],
        manifest_paths=bundle_payload["manifest_paths"],
    )

    verdict = build_legacy_validation_acceptance_verdict(bundle)
    verdict_from_manifest = build_legacy_validation_acceptance_verdict_from_summary_bundle_manifest(
        summary_bundle_manifest.artifacts[-1].path
    )

    assert isinstance(verdict, LegacyValidationAcceptanceVerdict)
    assert verdict.passed is True
    assert verdict.status == "passed"
    assert verdict.reason_count == 0
    assert verdict.reasons == []
    assert verdict.total_runs == 2
    assert verdict_from_manifest == verdict
    assert legacy_validation_acceptance_verdict_to_dict(verdict)["passed"] is True


def test_legacy_validation_acceptance_verdict_tracks_failed_summary_bundle(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs",
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["total_rows"] = 999
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics",
        bundle_name="checks",
    )
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics",
        tmp_path / "summary_artifacts",
        bundle_name="payload_summary",
    )
    summary_bundle_manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts_from_directory(
        tmp_path / "summary_artifacts",
        tmp_path / "summary_bundle",
        bundle_name="summary_bundle",
    )

    verdict = build_legacy_validation_acceptance_verdict_from_summary_bundle_manifest(
        summary_bundle_manifest.artifacts[-1].path
    )

    assert verdict.passed is False
    assert verdict.status == "failed"
    assert verdict.reason_count == 4
    assert verdict.issue_count == 1
    assert verdict.failing_bundle_count == 1
    assert verdict.failing_summary_count == 1
    assert "diagnostic issue" in verdict.reasons[1]


def test_legacy_validation_acceptance_verdict_artifacts(tmp_path: Path) -> None:
    bundle = build_legacy_validation_batch_run_manifest_check_payload_summary_bundle(
        [
            {
                "matches": True,
                "bundle_count": 1,
                "manifest_count": 1,
                "total_runs": 2,
                "checked_artifact_count": 7,
                "issue_count": 0,
                "failing_bundle_count": 0,
            }
        ],
        manifest_paths=[tmp_path / "summary_artifacts.json"],
    )
    verdict = build_legacy_validation_acceptance_verdict(bundle)

    manifest = write_legacy_validation_acceptance_verdict_artifacts(
        verdict,
        tmp_path / "verdict",
        bundle_name="acceptance",
    )

    assert isinstance(manifest, LegacyValidationAcceptanceVerdictArtifactManifest)
    assert manifest.bundle_name == "acceptance"
    assert manifest.passed is True
    assert manifest.status == "passed"
    assert manifest.reason_count == 0
    assert [artifact.path.name for artifact in manifest.artifacts] == [
        "acceptance.json",
        "acceptance.csv",
        "acceptance_artifacts.json",
    ]
    loaded_manifest = load_legacy_validation_acceptance_verdict_artifact_manifest(
        manifest.artifacts[-1].path
    )
    assert loaded_manifest.artifact_count == 3
    payload = load_legacy_validation_acceptance_verdict_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload == legacy_validation_acceptance_verdict_to_dict(verdict)

    with manifest.artifacts[1].path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["passed"] == "True"
    assert rows[0]["status"] == "passed"
    assert rows[0]["total_runs"] == "2"


def test_legacy_validation_acceptance_verdict_artifacts_from_summary_bundle_manifest(
    tmp_path: Path,
) -> None:
    run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path / "runs",
    )
    write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
        tmp_path / "runs",
        tmp_path / "diagnostics",
        bundle_name="checks",
    )
    write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
        tmp_path / "diagnostics",
        tmp_path / "summary_artifacts",
        bundle_name="payload_summary",
    )
    summary_bundle_manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts_from_directory(
        tmp_path / "summary_artifacts",
        tmp_path / "summary_bundle",
        bundle_name="summary_bundle",
    )

    manifest = write_legacy_validation_acceptance_verdict_artifacts_from_summary_bundle_manifest(
        summary_bundle_manifest.artifacts[-1].path,
        tmp_path / "verdict",
        bundle_name="acceptance",
    )

    payload = load_legacy_validation_acceptance_verdict_from_manifest(
        manifest.artifacts[-1].path
    )
    assert payload["passed"] is True
    assert payload["summary_count"] == 1
    assert payload["total_runs"] == 2


def test_legacy_validation_acceptance_verdict_payload_rejects_manifest_mismatch(
    tmp_path: Path,
) -> None:
    verdict = LegacyValidationAcceptanceVerdict(
        passed=True,
        status="passed",
        reason_count=0,
        reasons=[],
        summary_count=1,
        bundle_count=1,
        manifest_count=1,
        total_runs=2,
        checked_artifact_count=7,
        issue_count=0,
        failing_bundle_count=0,
        failing_summary_count=0,
    )
    manifest = write_legacy_validation_acceptance_verdict_artifacts(
        verdict,
        tmp_path / "verdict",
    )
    json_artifact = manifest.artifact_for_kind("acceptance_verdict_json")
    assert json_artifact is not None
    payload = json.loads(json_artifact.path.read_text(encoding="utf-8"))
    payload["status"] = "failed"
    json_artifact.path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_acceptance_verdict_from_manifest(
            manifest.artifacts[-1].path
        )
    except ValueError as exc:
        assert "manifest field status" in str(exc)
    else:
        raise AssertionError("acceptance verdict mismatch should fail")


def test_legacy_validation_batch_manifest_check_bundle_payloads_from_directory_rejects_empty_input(
    tmp_path: Path,
) -> None:
    try:
        load_legacy_validation_batch_run_manifest_check_bundle_payloads_from_directory(
            tmp_path
        )
    except ValueError as exc:
        assert "contains no manifests" in str(exc)
    else:
        raise AssertionError("empty diagnostic artifact manifest directory should fail")

    try:
        build_legacy_validation_batch_run_manifest_check_payload_summary([])
    except ValueError as exc:
        assert "requires payloads" in str(exc)
    else:
        raise AssertionError("empty diagnostic payload summary input should fail")

    try:
        build_legacy_validation_batch_run_manifest_check_payload_summary_bundle([])
    except ValueError as exc:
        assert "requires payloads" in str(exc)
    else:
        raise AssertionError("empty diagnostic payload summary bundle input should fail")

    try:
        load_legacy_validation_batch_run_manifest_check_payload_summary_payloads_from_directory(
            tmp_path
        )
    except ValueError as exc:
        assert "summary directory contains no manifests" in str(exc)
    else:
        raise AssertionError("empty diagnostic payload summary directory should fail")

    try:
        summarize_legacy_validation_batch_run_manifest_check_payload_summaries_from_directory(
            tmp_path
        )
    except ValueError as exc:
        assert "summary directory contains no manifests" in str(exc)
    else:
        raise AssertionError("empty diagnostic payload summary bundle directory should fail")


def test_legacy_validation_batch_manifest_check_bundle_rejects_empty_inputs(
    tmp_path: Path,
) -> None:
    try:
        check_legacy_validation_batch_run_manifests([])
    except ValueError as exc:
        assert "requires paths" in str(exc)
    else:
        raise AssertionError("empty batch run manifest path list should fail")

    try:
        check_legacy_validation_batch_run_manifests_from_directory(tmp_path)
    except ValueError as exc:
        assert "contains no manifests" in str(exc)
    else:
        raise AssertionError("empty batch run manifest directory should fail")


def test_legacy_validation_batch_manifest_rejects_missing_report_manifest(tmp_path: Path) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    result.runs[0].result.artifacts[-1].path.unlink()

    try:
        load_legacy_validation_batch_run_manifest(result.batch_manifest_path)
    except ValueError as exc:
        assert "missing artifacts" in str(exc)
    else:
        raise AssertionError("missing batch report manifest should fail")


def test_legacy_validation_batch_manifest_rejects_bad_run_count(tmp_path: Path) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["run_count"] = 999
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest(result.batch_manifest_path)
    except ValueError as exc:
        assert "run_count" in str(exc)
    else:
        raise AssertionError("bad batch run_count should fail")


def test_legacy_validation_batch_manifest_rejects_summary_total_mismatch(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["total_rows"] = 999
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest(result.batch_manifest_path)
    except ValueError as exc:
        assert "summary manifest field total_rows" in str(exc)
    else:
        raise AssertionError("batch summary total mismatch should fail")


def test_legacy_validation_batch_manifest_summary_total_check_is_io_bound(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["total_rows"] = 999
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    loaded_payload = load_legacy_validation_batch_run_manifest(
        result.batch_manifest_path,
        require_existing_artifacts=False,
    )

    assert loaded_payload["total_rows"] == 999


def test_legacy_validation_batch_manifest_rejects_run_report_total_mismatch(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["total_rows"] = 999
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest(result.batch_manifest_path)
    except ValueError as exc:
        assert "report manifest field total_rows" in str(exc)
        assert "legacy_validation_bundle_a" in str(exc)
    else:
        raise AssertionError("batch run report total mismatch should fail")


def test_legacy_validation_batch_manifest_run_report_total_check_is_io_bound(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["total_rows"] = 999
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    loaded_payload = load_legacy_validation_batch_run_manifest(
        result.batch_manifest_path,
        require_existing_artifacts=False,
    )

    assert loaded_payload["runs"][0]["total_rows"] == 999


def test_legacy_validation_batch_manifest_validates_run_entry_shape_without_io(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0] = "bad"
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest(
            result.batch_manifest_path,
            require_existing_artifacts=False,
        )
    except ValueError as exc:
        assert "run entries must be objects" in str(exc)
    else:
        raise AssertionError("bad run entry shape should fail without IO checks")


def test_legacy_validation_batch_manifest_validates_required_paths_without_io(
    tmp_path: Path,
) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["summary_manifest_path"] = " "
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest(
            result.batch_manifest_path,
            require_existing_artifacts=False,
        )
    except ValueError as exc:
        assert "summary_manifest_path" in str(exc)
    else:
        raise AssertionError("missing summary_manifest_path should fail without IO checks")

    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["summary_manifest_path"] = "summary/legacy_validation_batch_artifacts.json"
    payload["runs"][0]["output_dir"] = ""
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest(
            result.batch_manifest_path,
            require_existing_artifacts=False,
        )
    except ValueError as exc:
        assert "output_dir" in str(exc)
    else:
        raise AssertionError("missing output_dir should fail without IO checks")

    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["output_dir"] = str(Path("bundle_a"))
    payload["runs"][0]["report_manifest_path"] = ""
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest(
            result.batch_manifest_path,
            require_existing_artifacts=False,
        )
    except ValueError as exc:
        assert "report_manifest_path" in str(exc)
    else:
        raise AssertionError("missing report_manifest_path should fail without IO checks")


def test_legacy_validation_batch_manifest_rejects_missing_run_output_dir(tmp_path: Path) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["output_dir"] = "missing-output"
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest(result.batch_manifest_path)
    except ValueError as exc:
        assert "missing artifacts" in str(exc)
        assert "missing-output" in str(exc)
    else:
        raise AssertionError("missing batch run output_dir should fail")


def test_legacy_validation_batch_manifest_rejects_file_as_run_output_dir(tmp_path: Path) -> None:
    result = run_legacy_validation_batch_from_fixture(
        FIXTURE_DIR / "legacy_validation_batch.json",
        tmp_path,
    )
    payload = json.loads(result.batch_manifest_path.read_text(encoding="utf-8"))
    payload["runs"][0]["output_dir"] = str(Path("bundle_a") / "legacy_validation_bundle.json")
    result.batch_manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        load_legacy_validation_batch_run_manifest(result.batch_manifest_path)
    except ValueError as exc:
        assert "output_dir must be a directory" in str(exc)
    else:
        raise AssertionError("file as batch run output_dir should fail")


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
    assert legacy_validation_batch_run_result_to_dict is not None
    assert legacy_validation_report_payload_summary_to_dict is not None
    assert legacy_validation_report_summary_bundle_to_dict is not None
    assert load_legacy_validation_batch_run_manifest is not None
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
    assert write_legacy_validation_batch_run_manifest is not None
