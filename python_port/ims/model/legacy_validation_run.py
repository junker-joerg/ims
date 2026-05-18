from dataclasses import dataclass
import csv
import json
from pathlib import Path

from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportFileSpec,
    ExportRow,
    ExportTable,
)
from ims.model.legacy_agrsich_multi_period import (
    MultiPeriodLegacyComparison,
    build_multi_period_legacy_comparison,
    compare_insurer_export_table_to_legacy,
    compare_policyholder_export_table_to_legacy,
)
from ims.model.legacy_agrsich_reference import (
    LegacyInsurerTable,
    extract_legacy_row,
    parse_legacy_insurer_dat,
)
from ims.model.legacy_validation_report import (
    LegacyValidationReport,
    build_legacy_validation_report_from_multi_period_comparison,
    write_legacy_validation_deviation_index_csv,
    write_legacy_validation_field_summary_csv,
    write_legacy_validation_group_summary_csv,
    write_legacy_validation_period_summary_csv,
    write_legacy_validation_report_csv,
    write_legacy_validation_report_json,
)
from ims.model.legacy_vn_reference import (
    LegacyPolicyholderTable,
    extract_legacy_policyholder_row,
    parse_legacy_policyholder_dat,
)


@dataclass(slots=True)
class LegacyValidationTarget:
    subject_type: str
    legacy_path: Path
    export_filename: str
    periods: list[int]
    level: str
    selector_kind: str
    selector_value: int | str | None


@dataclass(slots=True)
class LegacyValidationArtifact:
    kind: str
    path: Path


@dataclass(slots=True)
class LegacyValidationArtifactManifest:
    report_name: str
    fixture_path: Path
    matches: bool
    total_files: int
    total_rows: int
    matched_rows: int
    mismatched_rows: int
    artifacts: list[LegacyValidationArtifact]

    def artifact_for_kind(self, kind: str) -> LegacyValidationArtifact | None:
        for artifact in self.artifacts:
            if artifact.kind == kind:
                return artifact
        return None


@dataclass(slots=True)
class LegacyValidationReportPayloadSummary:
    report_name: str
    manifest_path: Path
    matches: bool
    total_files: int
    total_rows: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    artifact_kinds: list[str]
    filenames_with_differences: list[str]
    periods_with_differences: list[int | None]
    fields_with_differences: list[str]
    deviation_count: int


@dataclass(slots=True)
class LegacyValidationReportSummaryBundle:
    report_count: int
    matches: bool
    total_files: int
    total_rows: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    artifact_count: int
    summaries: list[LegacyValidationReportPayloadSummary]
    report_names: list[str]
    manifest_paths: list[Path]
    artifact_kinds: list[str]
    filenames_with_differences: list[str]
    periods_with_differences: list[int | None]
    fields_with_differences: list[str]
    deviation_count: int


@dataclass(slots=True)
class LegacyValidationReportSummaryBundleArtifactManifest:
    bundle_name: str
    matches: bool
    report_count: int
    total_files: int
    total_rows: int
    matched_rows: int
    mismatched_rows: int
    artifact_count: int
    artifacts: list[LegacyValidationArtifact]

    def artifact_for_kind(self, kind: str) -> LegacyValidationArtifact | None:
        for artifact in self.artifacts:
            if artifact.kind == kind:
                return artifact
        return None


@dataclass(slots=True)
class LegacyValidationRunResult:
    targets: list[LegacyValidationTarget]
    comparison: MultiPeriodLegacyComparison
    report: LegacyValidationReport
    written_reports: list[Path]
    artifacts: list[LegacyValidationArtifact]


@dataclass(slots=True)
class LegacyValidationBatchRunItem:
    name: str
    fixture_path: Path
    output_dir: Path
    result: LegacyValidationRunResult


@dataclass(slots=True)
class LegacyValidationBatchRunResult:
    batch_name: str
    fixture_path: Path
    output_dir: Path
    runs: list[LegacyValidationBatchRunItem]
    summary_manifest: LegacyValidationReportSummaryBundleArtifactManifest
    batch_manifest_path: Path


@dataclass(slots=True)
class LegacyValidationBatchRunManifestIssue:
    code: str
    message: str
    path: Path | None = None


@dataclass(slots=True)
class LegacyValidationBatchRunManifestCheck:
    manifest_path: Path
    matches: bool
    run_count: int
    checked_artifact_count: int
    issues: list[LegacyValidationBatchRunManifestIssue]


@dataclass(slots=True)
class LegacyValidationBatchRunManifestCheckBundle:
    manifest_count: int
    matches: bool
    total_runs: int
    checked_artifact_count: int
    issue_count: int
    checks: list[LegacyValidationBatchRunManifestCheck]


@dataclass(slots=True)
class LegacyValidationBatchRunManifestCheckBundleArtifactManifest:
    bundle_name: str
    matches: bool
    manifest_count: int
    total_runs: int
    checked_artifact_count: int
    issue_count: int
    artifact_count: int
    artifacts: list[LegacyValidationArtifact]

    def artifact_for_kind(self, kind: str) -> LegacyValidationArtifact | None:
        for artifact in self.artifacts:
            if artifact.kind == kind:
                return artifact
        return None


@dataclass(slots=True)
class LegacyValidationBatchRunManifestCheckPayloadSummary:
    bundle_count: int
    matches: bool
    manifest_count: int
    total_runs: int
    checked_artifact_count: int
    issue_count: int
    failing_bundle_count: int


@dataclass(slots=True)
class LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest:
    bundle_name: str
    matches: bool
    bundle_count: int
    manifest_count: int
    total_runs: int
    checked_artifact_count: int
    issue_count: int
    failing_bundle_count: int
    artifact_count: int
    artifacts: list[LegacyValidationArtifact]

    def artifact_for_kind(self, kind: str) -> LegacyValidationArtifact | None:
        for artifact in self.artifacts:
            if artifact.kind == kind:
                return artifact
        return None


@dataclass(slots=True)
class LegacyValidationBatchRunManifestCheckPayloadSummaryBundle:
    summary_count: int
    matches: bool
    bundle_count: int
    manifest_count: int
    total_runs: int
    checked_artifact_count: int
    issue_count: int
    failing_bundle_count: int
    failing_summary_count: int
    summaries: list[LegacyValidationBatchRunManifestCheckPayloadSummary]
    manifest_paths: list[Path]


@dataclass(slots=True)
class LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest:
    bundle_name: str
    matches: bool
    summary_count: int
    bundle_count: int
    manifest_count: int
    total_runs: int
    checked_artifact_count: int
    issue_count: int
    failing_bundle_count: int
    failing_summary_count: int
    artifact_count: int
    artifacts: list[LegacyValidationArtifact]

    def artifact_for_kind(self, kind: str) -> LegacyValidationArtifact | None:
        for artifact in self.artifacts:
            if artifact.kind == kind:
                return artifact
        return None


@dataclass(slots=True)
class LegacyValidationAcceptanceVerdict:
    passed: bool
    status: str
    reason_count: int
    reasons: list[str]
    summary_count: int
    bundle_count: int
    manifest_count: int
    total_runs: int
    checked_artifact_count: int
    issue_count: int
    failing_bundle_count: int
    failing_summary_count: int


@dataclass(slots=True)
class LegacyValidationAcceptanceVerdictArtifactManifest:
    bundle_name: str
    passed: bool
    status: str
    reason_count: int
    artifact_count: int
    artifacts: list[LegacyValidationArtifact]

    def artifact_for_kind(self, kind: str) -> LegacyValidationArtifact | None:
        for artifact in self.artifacts:
            if artifact.kind == kind:
                return artifact
        return None


@dataclass(slots=True)
class LegacyValidationAcceptanceRunResult:
    summary_bundle_manifest: LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest
    verdict_manifest: LegacyValidationAcceptanceVerdictArtifactManifest
    run_manifest_path: Path | None = None


@dataclass(slots=True)
class LegacyValidationAcceptanceRunManifest:
    run_name: str
    passed: bool
    status: str
    summary_bundle_manifest_path: Path
    verdict_manifest_path: Path
    total_runs: int
    issue_count: int
    failing_summary_count: int


def _target_from_mapping(data: dict, fixture_base_path: Path) -> LegacyValidationTarget:
    subject_type = str(data["subject_type"])
    if subject_type not in {"insurer", "policyholder"}:
        raise ValueError(f"unsupported validation target subject_type: {subject_type}")

    legacy_path_data = str(data.get("legacy_path", "")).strip()
    if not legacy_path_data:
        raise ValueError("validation target must contain a legacy_path")

    export_filename = str(data.get("export_filename", "")).strip()
    if not export_filename:
        raise ValueError("validation target must contain an export_filename")

    level = str(data.get("level", "")).strip()
    if not level:
        raise ValueError("validation target must contain a level")

    selector_kind = str(data.get("selector_kind", "")).strip()
    if not selector_kind:
        raise ValueError("validation target must contain a selector_kind")

    periods_data = data.get("periods")
    if not isinstance(periods_data, list) or not periods_data:
        raise ValueError("validation target must contain a non-empty periods list")
    periods = [int(period) for period in periods_data]
    if len(periods) != len(set(periods)):
        raise ValueError("validation target periods must be unique")
    if periods != sorted(periods):
        raise ValueError("validation target periods must be sorted ascending")
    expected_periods = list(range(periods[0], periods[-1] + 1))
    if periods != expected_periods:
        raise ValueError("validation target periods must be contiguous")

    legacy_path = Path(legacy_path_data)
    if not legacy_path.is_absolute():
        legacy_path = fixture_base_path / legacy_path

    return LegacyValidationTarget(
        subject_type=subject_type,
        legacy_path=legacy_path,
        export_filename=export_filename,
        periods=periods,
        level=level,
        selector_kind=selector_kind,
        selector_value=data.get("selector_value"),
    )


def _target_identity(target: LegacyValidationTarget) -> tuple[str, str, str]:
    return (
        target.subject_type,
        str(target.legacy_path.resolve()),
        target.export_filename,
    )


def _validate_unique_targets(targets: list[LegacyValidationTarget]) -> None:
    seen: set[tuple[str, str, str]] = set()
    for target in targets:
        identity = _target_identity(target)
        if identity in seen:
            raise ValueError(
                "legacy validation fixture must not contain duplicate targets: "
                f"{target.subject_type} {target.export_filename} {target.legacy_path}"
            )
        seen.add(identity)


def _insurer_export_table_from_target(target: LegacyValidationTarget, legacy_table: LegacyInsurerTable) -> ExportTable:
    rows: list[ExportRow] = []
    for period in target.periods:
        legacy_row = extract_legacy_row(legacy_table, period)
        if legacy_row is None:
            raise ValueError(f"missing insurer legacy row {period} in {target.legacy_path}")
        rows.append(ExportRow(values=[legacy_row.global_period, *legacy_row.metric_values()]))

    return ExportTable(
        spec=ExportFileSpec(
            filename=target.export_filename,
            subject_type=target.subject_type,
            level=target.level,
            selector_kind=target.selector_kind,
            selector_value=target.selector_value,
        ),
        header=INSURER_HEADER,
        rows=rows,
    )


def _policyholder_export_table_from_target(
    target: LegacyValidationTarget,
    legacy_table: LegacyPolicyholderTable,
) -> ExportTable:
    rows: list[ExportRow] = []
    for period in target.periods:
        legacy_row = extract_legacy_policyholder_row(legacy_table, period)
        if legacy_row is None:
            raise ValueError(f"missing policyholder legacy row {period} in {target.legacy_path}")
        rows.append(ExportRow(values=[legacy_row.global_period, *legacy_row.metric_values()]))

    return ExportTable(
        spec=ExportFileSpec(
            filename=target.export_filename,
            subject_type=target.subject_type,
            level=target.level,
            selector_kind=target.selector_kind,
            selector_value=target.selector_value,
        ),
        header=POLICYHOLDER_HEADER,
        rows=rows,
    )


def _compare_target(target: LegacyValidationTarget):
    if target.subject_type == "insurer":
        legacy_table = parse_legacy_insurer_dat(target.legacy_path)
        export_table = _insurer_export_table_from_target(target, legacy_table)
        return compare_insurer_export_table_to_legacy(export_table, legacy_table)

    legacy_table = parse_legacy_policyholder_dat(target.legacy_path)
    export_table = _policyholder_export_table_from_target(target, legacy_table)
    return compare_policyholder_export_table_to_legacy(export_table, legacy_table)


def _artifact_to_mapping(artifact: LegacyValidationArtifact, manifest_base_path: Path | None = None) -> dict:
    artifact_path = artifact.path
    path_text = str(artifact_path)
    if manifest_base_path is not None:
        try:
            path_text = str(artifact_path.resolve().relative_to(manifest_base_path.resolve()))
        except ValueError:
            path_text = str(artifact_path)
    return {
        "kind": artifact.kind,
        "filename": artifact.path.name,
        "path": path_text,
    }


def _resolve_artifact_path(path_data: str, manifest_base_path: Path) -> Path:
    artifact_path = Path(path_data)
    if artifact_path.is_absolute():
        return artifact_path

    candidates = [
        manifest_base_path / artifact_path,
        manifest_base_path.parent / artifact_path,
        artifact_path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return manifest_base_path / artifact_path


def _artifact_from_mapping(data: dict, manifest_base_path: Path) -> LegacyValidationArtifact:
    kind = str(data.get("kind", "")).strip()
    if not kind:
        raise ValueError("legacy validation artifact must contain a kind")
    path_data = str(data.get("path", "")).strip()
    if not path_data:
        raise ValueError("legacy validation artifact must contain a path")
    artifact_path = _resolve_artifact_path(path_data, manifest_base_path)
    return LegacyValidationArtifact(kind=kind, path=artifact_path)


def _write_legacy_validation_artifact_manifest(
    *,
    report_name: str,
    fixture_path: Path,
    report: LegacyValidationReport,
    artifacts: list[LegacyValidationArtifact],
    path: Path,
) -> Path:
    payload = {
        "report_name": report_name,
        "fixture_path": str(fixture_path),
        "matches": report.matches,
        "total_files": report.total_files,
        "total_rows": report.total_rows,
        "matched_rows": report.matched_rows,
        "mismatched_rows": report.mismatched_rows,
        "artifact_count": len(artifacts),
        "artifacts": [
            _artifact_to_mapping(artifact, path.parent)
            for artifact in artifacts
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_legacy_validation_artifact_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationArtifactManifest:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("legacy validation artifact manifest must be a JSON object")

    artifacts_data = data.get("artifacts")
    if not isinstance(artifacts_data, list) or not artifacts_data:
        raise ValueError("legacy validation artifact manifest must contain a non-empty artifacts list")

    artifacts = [
        _artifact_from_mapping(item, manifest_path.parent)
        for item in artifacts_data
    ]
    artifact_count = int(data.get("artifact_count", -1))
    if artifact_count != len(artifacts):
        raise ValueError("legacy validation artifact manifest artifact_count must match artifacts")

    kinds = [artifact.kind for artifact in artifacts]
    if len(kinds) != len(set(kinds)):
        raise ValueError("legacy validation artifact manifest must contain unique artifact kinds")

    if require_existing_artifacts:
        missing = [
            artifact.path
            for artifact in artifacts
            if not artifact.path.exists()
        ]
        if missing:
            raise ValueError(f"legacy validation artifact manifest references missing artifacts: {missing}")

    return LegacyValidationArtifactManifest(
        report_name=str(data.get("report_name", "")),
        fixture_path=Path(str(data.get("fixture_path", ""))),
        matches=bool(data.get("matches")),
        total_files=int(data.get("total_files", 0)),
        total_rows=int(data.get("total_rows", 0)),
        matched_rows=int(data.get("matched_rows", 0)),
        mismatched_rows=int(data.get("mismatched_rows", 0)),
        artifacts=artifacts,
    )


def load_legacy_validation_report_payload_from_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> dict:
    manifest = load_legacy_validation_artifact_manifest(
        path,
        require_existing_artifacts=require_existing_artifacts,
    )
    report_artifact = manifest.artifact_for_kind("report_json")
    if report_artifact is None:
        raise ValueError("legacy validation artifact manifest must contain a report_json artifact")

    with report_artifact.path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("legacy validation report artifact must be a JSON object")

    expected_values = {
        "matches": manifest.matches,
        "total_files": manifest.total_files,
        "total_rows": manifest.total_rows,
        "matched_rows": manifest.matched_rows,
        "mismatched_rows": manifest.mismatched_rows,
    }
    for field_name, expected_value in expected_values.items():
        if payload.get(field_name) != expected_value:
            raise ValueError(
                "legacy validation report artifact does not match manifest "
                f"field {field_name}"
            )
    return payload


def _unique_in_order(values: list) -> list:
    result = []
    seen = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def summarize_legacy_validation_report_payload_from_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationReportPayloadSummary:
    manifest_path = Path(path).resolve()
    manifest = load_legacy_validation_artifact_manifest(
        manifest_path,
        require_existing_artifacts=require_existing_artifacts,
    )
    payload = load_legacy_validation_report_payload_from_manifest(
        manifest_path,
        require_existing_artifacts=require_existing_artifacts,
    )

    files = payload.get("files", [])
    if not isinstance(files, list):
        raise ValueError("legacy validation report artifact files must be a list")
    deviation_index = payload.get("deviation_index", [])
    if not isinstance(deviation_index, list):
        raise ValueError("legacy validation report artifact deviation_index must be a list")

    filenames_with_differences = _unique_in_order(
        [
            str(file_item.get("filename", ""))
            for file_item in files
            if isinstance(file_item, dict) and int(file_item.get("mismatched_rows", 0)) > 0
        ]
    )
    periods_with_differences = _unique_in_order(
        [
            item.get("global_period")
            for item in deviation_index
            if isinstance(item, dict)
        ]
    )
    fields_with_differences = _unique_in_order(
        [
            str(item.get("field_name", ""))
            for item in deviation_index
            if isinstance(item, dict)
        ]
    )

    return LegacyValidationReportPayloadSummary(
        report_name=manifest.report_name,
        manifest_path=manifest_path,
        matches=manifest.matches,
        total_files=manifest.total_files,
        total_rows=manifest.total_rows,
        matched_rows=manifest.matched_rows,
        mismatched_rows=manifest.mismatched_rows,
        match_rate=float(payload.get("match_rate", 0.0)),
        artifact_kinds=[artifact.kind for artifact in manifest.artifacts],
        filenames_with_differences=filenames_with_differences,
        periods_with_differences=periods_with_differences,
        fields_with_differences=fields_with_differences,
        deviation_count=len(deviation_index),
    )


def build_legacy_validation_report_summary_bundle(
    summaries: list[LegacyValidationReportPayloadSummary],
) -> LegacyValidationReportSummaryBundle:
    total_rows = sum(summary.total_rows for summary in summaries)
    matched_rows = sum(summary.matched_rows for summary in summaries)
    mismatched_rows = sum(summary.mismatched_rows for summary in summaries)

    return LegacyValidationReportSummaryBundle(
        report_count=len(summaries),
        matches=bool(summaries) and all(summary.matches for summary in summaries),
        total_files=sum(summary.total_files for summary in summaries),
        total_rows=total_rows,
        matched_rows=matched_rows,
        mismatched_rows=mismatched_rows,
        match_rate=0.0 if total_rows == 0 else matched_rows / total_rows,
        artifact_count=sum(len(summary.artifact_kinds) for summary in summaries),
        summaries=summaries,
        report_names=[summary.report_name for summary in summaries],
        manifest_paths=[summary.manifest_path for summary in summaries],
        artifact_kinds=_unique_in_order(
            [
                kind
                for summary in summaries
                for kind in summary.artifact_kinds
            ]
        ),
        filenames_with_differences=_unique_in_order(
            [
                filename
                for summary in summaries
                for filename in summary.filenames_with_differences
            ]
        ),
        periods_with_differences=_unique_in_order(
            [
                period
                for summary in summaries
                for period in summary.periods_with_differences
            ]
        ),
        fields_with_differences=_unique_in_order(
            [
                field_name
                for summary in summaries
                for field_name in summary.fields_with_differences
            ]
        ),
        deviation_count=sum(summary.deviation_count for summary in summaries),
    )


def summarize_legacy_validation_report_payloads_from_manifests(
    paths: list[str | Path],
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationReportSummaryBundle:
    if not paths:
        raise ValueError("legacy validation report summary bundle requires at least one manifest path")
    return build_legacy_validation_report_summary_bundle(
        [
            summarize_legacy_validation_report_payload_from_manifest(
                path,
                require_existing_artifacts=require_existing_artifacts,
            )
            for path in paths
        ]
    )


def _is_legacy_validation_report_artifact_manifest(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        return False
    return any(
        isinstance(artifact, dict) and artifact.get("kind") == "report_json"
        for artifact in artifacts
    )


def summarize_legacy_validation_report_payloads_from_directory(
    path: str | Path,
    *,
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationReportSummaryBundle:
    directory_path = Path(path)
    if not directory_path.is_dir():
        raise ValueError("legacy validation report summary directory must exist")
    manifest_paths = [
        manifest_path
        for manifest_path in sorted(directory_path.glob(pattern))
        if _is_legacy_validation_report_artifact_manifest(manifest_path)
    ]
    if not manifest_paths:
        raise ValueError("legacy validation report summary directory contains no manifests")
    return summarize_legacy_validation_report_payloads_from_manifests(
        manifest_paths,
        require_existing_artifacts=require_existing_artifacts,
    )


def legacy_validation_report_payload_summary_to_dict(
    summary: LegacyValidationReportPayloadSummary,
) -> dict:
    return {
        "report_name": summary.report_name,
        "manifest_path": str(summary.manifest_path),
        "matches": summary.matches,
        "total_files": summary.total_files,
        "total_rows": summary.total_rows,
        "matched_rows": summary.matched_rows,
        "mismatched_rows": summary.mismatched_rows,
        "match_rate": summary.match_rate,
        "artifact_kinds": summary.artifact_kinds,
        "filenames_with_differences": summary.filenames_with_differences,
        "periods_with_differences": summary.periods_with_differences,
        "fields_with_differences": summary.fields_with_differences,
        "deviation_count": summary.deviation_count,
    }


def legacy_validation_report_summary_bundle_to_dict(
    bundle: LegacyValidationReportSummaryBundle,
) -> dict:
    return {
        "report_count": bundle.report_count,
        "matches": bundle.matches,
        "total_files": bundle.total_files,
        "total_rows": bundle.total_rows,
        "matched_rows": bundle.matched_rows,
        "mismatched_rows": bundle.mismatched_rows,
        "match_rate": bundle.match_rate,
        "artifact_count": bundle.artifact_count,
        "report_names": bundle.report_names,
        "manifest_paths": [str(path) for path in bundle.manifest_paths],
        "artifact_kinds": bundle.artifact_kinds,
        "filenames_with_differences": bundle.filenames_with_differences,
        "periods_with_differences": bundle.periods_with_differences,
        "fields_with_differences": bundle.fields_with_differences,
        "deviation_count": bundle.deviation_count,
        "summaries": [
            legacy_validation_report_payload_summary_to_dict(summary)
            for summary in bundle.summaries
        ],
    }


def write_legacy_validation_report_summary_bundle_json(
    bundle: LegacyValidationReportSummaryBundle,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            legacy_validation_report_summary_bundle_to_dict(bundle),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return output_path


def write_legacy_validation_report_summary_bundle_csv(
    bundle: LegacyValidationReportSummaryBundle,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "report_name",
                "manifest_path",
                "matches",
                "total_files",
                "total_rows",
                "matched_rows",
                "mismatched_rows",
                "match_rate",
                "artifact_count",
                "deviation_count",
                "filenames_with_differences",
                "periods_with_differences",
                "fields_with_differences",
            ],
        )
        writer.writeheader()
        for summary in bundle.summaries:
            writer.writerow(
                {
                    "report_name": summary.report_name,
                    "manifest_path": str(summary.manifest_path),
                    "matches": summary.matches,
                    "total_files": summary.total_files,
                    "total_rows": summary.total_rows,
                    "matched_rows": summary.matched_rows,
                    "mismatched_rows": summary.mismatched_rows,
                    "match_rate": f"{summary.match_rate:.6f}",
                    "artifact_count": len(summary.artifact_kinds),
                    "deviation_count": summary.deviation_count,
                    "filenames_with_differences": ";".join(summary.filenames_with_differences),
                    "periods_with_differences": ";".join(
                        "" if period is None else str(period)
                        for period in summary.periods_with_differences
                    ),
                    "fields_with_differences": ";".join(summary.fields_with_differences),
                }
            )
    return output_path


def _write_legacy_validation_report_summary_bundle_artifact_manifest(
    *,
    bundle_name: str,
    bundle: LegacyValidationReportSummaryBundle,
    artifacts: list[LegacyValidationArtifact],
    path: Path,
) -> Path:
    payload = {
        "bundle_name": bundle_name,
        "matches": bundle.matches,
        "report_count": bundle.report_count,
        "total_files": bundle.total_files,
        "total_rows": bundle.total_rows,
        "matched_rows": bundle.matched_rows,
        "mismatched_rows": bundle.mismatched_rows,
        "artifact_count": len(artifacts),
        "artifacts": [
            _artifact_to_mapping(artifact, path.parent)
            for artifact in artifacts
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_legacy_validation_report_summary_bundle_artifacts(
    bundle: LegacyValidationReportSummaryBundle,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_report_summary_bundle",
) -> LegacyValidationReportSummaryBundleArtifactManifest:
    output_path = Path(output_dir)
    artifacts = [
        LegacyValidationArtifact(
            kind="summary_bundle_json",
            path=write_legacy_validation_report_summary_bundle_json(
                bundle,
                output_path / f"{bundle_name}.json",
            ),
        ),
        LegacyValidationArtifact(
            kind="summary_bundle_csv",
            path=write_legacy_validation_report_summary_bundle_csv(
                bundle,
                output_path / f"{bundle_name}.csv",
            ),
        ),
    ]
    manifest_artifact = LegacyValidationArtifact(
        kind="summary_bundle_manifest_json",
        path=output_path / f"{bundle_name}_artifacts.json",
    )
    artifacts.append(manifest_artifact)
    _write_legacy_validation_report_summary_bundle_artifact_manifest(
        bundle_name=bundle_name,
        bundle=bundle,
        artifacts=artifacts,
        path=manifest_artifact.path,
    )
    return LegacyValidationReportSummaryBundleArtifactManifest(
        bundle_name=bundle_name,
        matches=bundle.matches,
        report_count=bundle.report_count,
        total_files=bundle.total_files,
        total_rows=bundle.total_rows,
        matched_rows=bundle.matched_rows,
        mismatched_rows=bundle.mismatched_rows,
        artifact_count=len(artifacts),
        artifacts=artifacts,
    )


def load_legacy_validation_report_summary_bundle_artifact_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationReportSummaryBundleArtifactManifest:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("legacy validation report summary bundle manifest must be a JSON object")

    artifacts_data = data.get("artifacts")
    if not isinstance(artifacts_data, list) or not artifacts_data:
        raise ValueError("legacy validation report summary bundle manifest must contain artifacts")
    artifacts = [
        _artifact_from_mapping(item, manifest_path.parent)
        for item in artifacts_data
    ]
    artifact_count = int(data.get("artifact_count", -1))
    if artifact_count != len(artifacts):
        raise ValueError("legacy validation report summary bundle manifest artifact_count must match artifacts")
    kinds = [artifact.kind for artifact in artifacts]
    if len(kinds) != len(set(kinds)):
        raise ValueError("legacy validation report summary bundle manifest must contain unique artifact kinds")

    required_kinds = {
        "summary_bundle_json",
        "summary_bundle_csv",
        "summary_bundle_manifest_json",
    }
    missing_kinds = sorted(required_kinds.difference(kinds))
    if missing_kinds:
        raise ValueError(
            "legacy validation report summary bundle manifest is missing artifact kinds: "
            f"{missing_kinds}"
        )

    if require_existing_artifacts:
        missing = [
            artifact.path
            for artifact in artifacts
            if not artifact.path.exists()
        ]
        if missing:
            raise ValueError(
                "legacy validation report summary bundle manifest references missing artifacts: "
                f"{missing}"
            )

    return LegacyValidationReportSummaryBundleArtifactManifest(
        bundle_name=str(data.get("bundle_name", "")),
        matches=bool(data.get("matches")),
        report_count=int(data.get("report_count", 0)),
        total_files=int(data.get("total_files", 0)),
        total_rows=int(data.get("total_rows", 0)),
        matched_rows=int(data.get("matched_rows", 0)),
        mismatched_rows=int(data.get("mismatched_rows", 0)),
        artifact_count=artifact_count,
        artifacts=artifacts,
    )


def load_legacy_validation_report_summary_bundle_payload_from_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> dict:
    manifest = load_legacy_validation_report_summary_bundle_artifact_manifest(
        path,
        require_existing_artifacts=require_existing_artifacts,
    )
    bundle_artifact = manifest.artifact_for_kind("summary_bundle_json")
    if bundle_artifact is None:
        raise ValueError("legacy validation report summary bundle manifest must contain summary_bundle_json")

    with bundle_artifact.path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("legacy validation report summary bundle artifact must be a JSON object")

    expected_values = {
        "matches": manifest.matches,
        "report_count": manifest.report_count,
        "total_files": manifest.total_files,
        "total_rows": manifest.total_rows,
        "matched_rows": manifest.matched_rows,
        "mismatched_rows": manifest.mismatched_rows,
    }
    for field_name, expected_value in expected_values.items():
        if payload.get(field_name) != expected_value:
            raise ValueError(
                "legacy validation report summary bundle artifact does not match manifest "
                f"field {field_name}"
            )
    return payload


def write_legacy_validation_report_summary_bundle_artifacts_from_manifests(
    manifest_paths: list[str | Path],
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_report_summary_bundle",
    require_existing_artifacts: bool = True,
) -> LegacyValidationReportSummaryBundleArtifactManifest:
    bundle = summarize_legacy_validation_report_payloads_from_manifests(
        manifest_paths,
        require_existing_artifacts=require_existing_artifacts,
    )
    return write_legacy_validation_report_summary_bundle_artifacts(
        bundle,
        output_dir,
        bundle_name=bundle_name,
    )


def write_legacy_validation_report_summary_bundle_artifacts_from_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_report_summary_bundle",
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationReportSummaryBundleArtifactManifest:
    bundle = summarize_legacy_validation_report_payloads_from_directory(
        input_dir,
        pattern=pattern,
        require_existing_artifacts=require_existing_artifacts,
    )
    return write_legacy_validation_report_summary_bundle_artifacts(
        bundle,
        output_dir,
        bundle_name=bundle_name,
    )


def _path_to_mapping(path: Path, manifest_base_path: Path | None = None) -> str:
    path_text = str(path)
    if manifest_base_path is not None:
        try:
            path_text = str(path.resolve().relative_to(manifest_base_path.resolve()))
        except ValueError:
            path_text = str(path)
    return path_text


def _batch_run_manifest_item_to_mapping(
    item: LegacyValidationBatchRunItem,
    manifest_base_path: Path,
) -> dict:
    report_manifest_path = item.result.artifacts[-1].path
    return {
        "name": item.name,
        "fixture_path": _path_to_mapping(item.fixture_path, manifest_base_path),
        "output_dir": _path_to_mapping(item.output_dir, manifest_base_path),
        "matches": item.result.report.matches,
        "total_files": item.result.report.total_files,
        "total_rows": item.result.report.total_rows,
        "matched_rows": item.result.report.matched_rows,
        "mismatched_rows": item.result.report.mismatched_rows,
        "report_manifest_path": _path_to_mapping(report_manifest_path, manifest_base_path),
    }


def legacy_validation_batch_run_result_to_dict(
    result: LegacyValidationBatchRunResult,
    *,
    manifest_base_path: Path | None = None,
) -> dict:
    return {
        "batch_name": result.batch_name,
        "fixture_path": _path_to_mapping(result.fixture_path, manifest_base_path),
        "output_dir": _path_to_mapping(result.output_dir, manifest_base_path),
        "run_count": len(result.runs),
        "matches": result.summary_manifest.matches,
        "total_files": result.summary_manifest.total_files,
        "total_rows": result.summary_manifest.total_rows,
        "matched_rows": result.summary_manifest.matched_rows,
        "mismatched_rows": result.summary_manifest.mismatched_rows,
        "summary_manifest_path": _path_to_mapping(
            result.summary_manifest.artifacts[-1].path,
            manifest_base_path,
        ),
        "runs": [
            _batch_run_manifest_item_to_mapping(item, manifest_base_path or Path.cwd())
            for item in result.runs
        ],
    }


def write_legacy_validation_batch_run_manifest(
    result: LegacyValidationBatchRunResult,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            legacy_validation_batch_run_result_to_dict(
                result,
                manifest_base_path=output_path.parent,
            ),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return output_path


def _validate_batch_run_summary_manifest_totals(
    payload: dict,
    summary_manifest: LegacyValidationReportSummaryBundleArtifactManifest,
) -> None:
    expected_fields = {
        "matches": summary_manifest.matches,
        "run_count": summary_manifest.report_count,
        "total_files": summary_manifest.total_files,
        "total_rows": summary_manifest.total_rows,
        "matched_rows": summary_manifest.matched_rows,
        "mismatched_rows": summary_manifest.mismatched_rows,
    }
    for field_name, expected_value in expected_fields.items():
        if payload.get(field_name) != expected_value:
            raise ValueError(
                "legacy validation batch run manifest does not match "
                f"summary manifest field {field_name}"
            )


def _validate_batch_run_item_report_manifest_totals(
    item: dict,
    report_manifest: LegacyValidationArtifactManifest,
) -> None:
    expected_fields = {
        "matches": report_manifest.matches,
        "total_files": report_manifest.total_files,
        "total_rows": report_manifest.total_rows,
        "matched_rows": report_manifest.matched_rows,
        "mismatched_rows": report_manifest.mismatched_rows,
    }
    item_name = str(item.get("name", "")).strip()
    for field_name, expected_value in expected_fields.items():
        if item.get(field_name) != expected_value:
            raise ValueError(
                "legacy validation batch run manifest item "
                f"{item_name} does not match report manifest field {field_name}"
            )


def legacy_validation_batch_run_manifest_check_to_dict(
    check: LegacyValidationBatchRunManifestCheck,
) -> dict:
    return {
        "manifest_path": str(check.manifest_path),
        "matches": check.matches,
        "run_count": check.run_count,
        "checked_artifact_count": check.checked_artifact_count,
        "issues": [
            {
                "code": issue.code,
                "message": issue.message,
                "path": None if issue.path is None else str(issue.path),
            }
            for issue in check.issues
        ],
    }


def legacy_validation_batch_run_manifest_check_bundle_to_dict(
    bundle: LegacyValidationBatchRunManifestCheckBundle,
) -> dict:
    return {
        "manifest_count": bundle.manifest_count,
        "matches": bundle.matches,
        "total_runs": bundle.total_runs,
        "checked_artifact_count": bundle.checked_artifact_count,
        "issue_count": bundle.issue_count,
        "checks": [
            legacy_validation_batch_run_manifest_check_to_dict(check)
            for check in bundle.checks
        ],
    }


def legacy_validation_batch_run_manifest_check_payload_summary_to_dict(
    summary: LegacyValidationBatchRunManifestCheckPayloadSummary,
) -> dict:
    return {
        "bundle_count": summary.bundle_count,
        "matches": summary.matches,
        "manifest_count": summary.manifest_count,
        "total_runs": summary.total_runs,
        "checked_artifact_count": summary.checked_artifact_count,
        "issue_count": summary.issue_count,
        "failing_bundle_count": summary.failing_bundle_count,
    }


def legacy_validation_batch_run_manifest_check_payload_summary_bundle_to_dict(
    bundle: LegacyValidationBatchRunManifestCheckPayloadSummaryBundle,
) -> dict:
    return {
        "summary_count": bundle.summary_count,
        "matches": bundle.matches,
        "bundle_count": bundle.bundle_count,
        "manifest_count": bundle.manifest_count,
        "total_runs": bundle.total_runs,
        "checked_artifact_count": bundle.checked_artifact_count,
        "issue_count": bundle.issue_count,
        "failing_bundle_count": bundle.failing_bundle_count,
        "failing_summary_count": bundle.failing_summary_count,
        "manifest_paths": [str(path) for path in bundle.manifest_paths],
        "summaries": [
            legacy_validation_batch_run_manifest_check_payload_summary_to_dict(summary)
            for summary in bundle.summaries
        ],
    }


def legacy_validation_acceptance_verdict_to_dict(
    verdict: LegacyValidationAcceptanceVerdict,
) -> dict:
    return {
        "passed": verdict.passed,
        "status": verdict.status,
        "reason_count": verdict.reason_count,
        "reasons": verdict.reasons,
        "summary_count": verdict.summary_count,
        "bundle_count": verdict.bundle_count,
        "manifest_count": verdict.manifest_count,
        "total_runs": verdict.total_runs,
        "checked_artifact_count": verdict.checked_artifact_count,
        "issue_count": verdict.issue_count,
        "failing_bundle_count": verdict.failing_bundle_count,
        "failing_summary_count": verdict.failing_summary_count,
    }


def load_legacy_validation_batch_run_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> dict:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("legacy validation batch run manifest must be a JSON object")

    runs = payload.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("legacy validation batch run manifest must contain runs")
    run_count = int(payload.get("run_count", -1))
    if run_count != len(runs):
        raise ValueError("legacy validation batch run manifest run_count must match runs")

    summary_manifest_data = str(payload.get("summary_manifest_path", "")).strip()
    if not summary_manifest_data:
        raise ValueError("legacy validation batch run manifest must contain a summary_manifest_path")

    for item in runs:
        if not isinstance(item, dict):
            raise ValueError("legacy validation batch run manifest run entries must be objects")
        if not str(item.get("name", "")).strip():
            raise ValueError("legacy validation batch run manifest run entries must contain a name")
        if not str(item.get("fixture_path", "")).strip():
            raise ValueError(
                "legacy validation batch run manifest run entries must contain a fixture_path"
            )
        if not str(item.get("output_dir", "")).strip():
            raise ValueError(
                "legacy validation batch run manifest run entries must contain an output_dir"
            )
        if not str(item.get("report_manifest_path", "")).strip():
            raise ValueError(
                "legacy validation batch run manifest run entries must contain a report_manifest_path"
            )

    if require_existing_artifacts:
        summary_manifest_path = _resolve_artifact_path(
            summary_manifest_data,
            manifest_path.parent,
        )
        missing = []
        if not summary_manifest_path.exists():
            missing.append(summary_manifest_path)
        for item in runs:
            fixture_path = _resolve_artifact_path(
                str(item.get("fixture_path", "")),
                manifest_path.parent,
            )
            if not fixture_path.exists():
                missing.append(fixture_path)
            output_dir = _resolve_artifact_path(
                str(item.get("output_dir", "")),
                manifest_path.parent,
            )
            if not output_dir.exists():
                missing.append(output_dir)
            elif not output_dir.is_dir():
                raise ValueError(
                    "legacy validation batch run manifest output_dir must be a directory: "
                    f"{output_dir}"
                )
            report_manifest_path = _resolve_artifact_path(
                str(item.get("report_manifest_path", "")),
                manifest_path.parent,
            )
            if not report_manifest_path.exists():
                missing.append(report_manifest_path)
        if missing:
            raise ValueError(
                "legacy validation batch run manifest references missing artifacts: "
                f"{missing}"
            )
        summary_manifest = load_legacy_validation_report_summary_bundle_artifact_manifest(
            summary_manifest_path
        )
        _validate_batch_run_summary_manifest_totals(payload, summary_manifest)
        for item in runs:
            report_manifest_path = _resolve_artifact_path(
                str(item.get("report_manifest_path", "")),
                manifest_path.parent,
            )
            report_manifest = load_legacy_validation_artifact_manifest(
                report_manifest_path
            )
            _validate_batch_run_item_report_manifest_totals(item, report_manifest)
    return payload


def check_legacy_validation_batch_run_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheck:
    manifest_path = Path(path).resolve()
    run_count = 0
    checked_artifact_count = 0
    issues: list[LegacyValidationBatchRunManifestIssue] = []
    try:
        payload = load_legacy_validation_batch_run_manifest(
            manifest_path,
            require_existing_artifacts=require_existing_artifacts,
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        issues.append(
            LegacyValidationBatchRunManifestIssue(
                code="batch_run_manifest_invalid",
                message=str(exc),
                path=manifest_path,
            )
        )
        return LegacyValidationBatchRunManifestCheck(
            manifest_path=manifest_path,
            matches=False,
            run_count=run_count,
            checked_artifact_count=checked_artifact_count,
            issues=issues,
        )

    runs = payload.get("runs", [])
    if isinstance(runs, list):
        run_count = len(runs)
    if require_existing_artifacts:
        checked_artifact_count = 1 + (3 * run_count)
    return LegacyValidationBatchRunManifestCheck(
        manifest_path=manifest_path,
        matches=True,
        run_count=run_count,
        checked_artifact_count=checked_artifact_count,
        issues=issues,
    )


def build_legacy_validation_batch_run_manifest_check_bundle(
    checks: list[LegacyValidationBatchRunManifestCheck],
) -> LegacyValidationBatchRunManifestCheckBundle:
    if not checks:
        raise ValueError("legacy validation batch run manifest check bundle requires checks")
    issue_count = sum(len(check.issues) for check in checks)
    return LegacyValidationBatchRunManifestCheckBundle(
        manifest_count=len(checks),
        matches=all(check.matches for check in checks),
        total_runs=sum(check.run_count for check in checks),
        checked_artifact_count=sum(check.checked_artifact_count for check in checks),
        issue_count=issue_count,
        checks=checks,
    )


def check_legacy_validation_batch_run_manifests(
    paths: list[str | Path],
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckBundle:
    if not paths:
        raise ValueError("legacy validation batch run manifest check requires paths")
    checks = [
        check_legacy_validation_batch_run_manifest(
            path,
            require_existing_artifacts=require_existing_artifacts,
        )
        for path in paths
    ]
    return build_legacy_validation_batch_run_manifest_check_bundle(checks)


def _is_legacy_validation_batch_run_manifest(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    return "summary_manifest_path" in data and (
        "runs" in data or "run_count" in data
    )


def check_legacy_validation_batch_run_manifests_from_directory(
    input_dir: str | Path,
    *,
    pattern: str = "**/*_batch.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckBundle:
    directory_path = Path(input_dir)
    manifest_paths = [
        manifest_path
        for manifest_path in sorted(directory_path.glob(pattern))
        if _is_legacy_validation_batch_run_manifest(manifest_path)
    ]
    if not manifest_paths:
        raise ValueError("legacy validation batch run manifest directory contains no manifests")
    return check_legacy_validation_batch_run_manifests(
        manifest_paths,
        require_existing_artifacts=require_existing_artifacts,
    )


def write_legacy_validation_batch_run_manifest_check_bundle_json(
    bundle: LegacyValidationBatchRunManifestCheckBundle,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            legacy_validation_batch_run_manifest_check_bundle_to_dict(bundle),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return output_path


def write_legacy_validation_batch_run_manifest_check_bundle_csv(
    bundle: LegacyValidationBatchRunManifestCheckBundle,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "manifest_path",
                "matches",
                "run_count",
                "checked_artifact_count",
                "issue_count",
                "issue_codes",
                "issue_messages",
            ],
        )
        writer.writeheader()
        for check in bundle.checks:
            writer.writerow(
                {
                    "manifest_path": str(check.manifest_path),
                    "matches": str(check.matches),
                    "run_count": check.run_count,
                    "checked_artifact_count": check.checked_artifact_count,
                    "issue_count": len(check.issues),
                    "issue_codes": ";".join(issue.code for issue in check.issues),
                    "issue_messages": ";".join(issue.message for issue in check.issues),
                }
            )
    return output_path


def _write_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest(
    *,
    bundle_name: str,
    bundle: LegacyValidationBatchRunManifestCheckBundle,
    artifacts: list[LegacyValidationArtifact],
    path: Path,
) -> Path:
    payload = {
        "bundle_name": bundle_name,
        "matches": bundle.matches,
        "manifest_count": bundle.manifest_count,
        "total_runs": bundle.total_runs,
        "checked_artifact_count": bundle.checked_artifact_count,
        "issue_count": bundle.issue_count,
        "artifact_count": len(artifacts),
        "artifacts": [
            _artifact_to_mapping(artifact, path.parent)
            for artifact in artifacts
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_legacy_validation_batch_run_manifest_check_bundle_artifacts(
    bundle: LegacyValidationBatchRunManifestCheckBundle,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_batch_manifest_checks",
) -> LegacyValidationBatchRunManifestCheckBundleArtifactManifest:
    output_path = Path(output_dir)
    artifacts = [
        LegacyValidationArtifact(
            kind="batch_manifest_check_bundle_json",
            path=write_legacy_validation_batch_run_manifest_check_bundle_json(
                bundle,
                output_path / f"{bundle_name}.json",
            ),
        ),
        LegacyValidationArtifact(
            kind="batch_manifest_check_bundle_csv",
            path=write_legacy_validation_batch_run_manifest_check_bundle_csv(
                bundle,
                output_path / f"{bundle_name}.csv",
            ),
        ),
    ]
    manifest_artifact = LegacyValidationArtifact(
        kind="batch_manifest_check_bundle_manifest_json",
        path=output_path / f"{bundle_name}_artifacts.json",
    )
    artifacts.append(manifest_artifact)
    _write_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest(
        bundle_name=bundle_name,
        bundle=bundle,
        artifacts=artifacts,
        path=manifest_artifact.path,
    )
    return LegacyValidationBatchRunManifestCheckBundleArtifactManifest(
        bundle_name=bundle_name,
        matches=bundle.matches,
        manifest_count=bundle.manifest_count,
        total_runs=bundle.total_runs,
        checked_artifact_count=bundle.checked_artifact_count,
        issue_count=bundle.issue_count,
        artifact_count=len(artifacts),
        artifacts=artifacts,
    )


def write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_manifests(
    manifest_paths: list[str | Path],
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_batch_manifest_checks",
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckBundleArtifactManifest:
    bundle = check_legacy_validation_batch_run_manifests(
        manifest_paths,
        require_existing_artifacts=require_existing_artifacts,
    )
    return write_legacy_validation_batch_run_manifest_check_bundle_artifacts(
        bundle,
        output_dir,
        bundle_name=bundle_name,
    )


def write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_batch_manifest_checks",
    pattern: str = "**/*_batch.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckBundleArtifactManifest:
    bundle = check_legacy_validation_batch_run_manifests_from_directory(
        input_dir,
        pattern=pattern,
        require_existing_artifacts=require_existing_artifacts,
    )
    return write_legacy_validation_batch_run_manifest_check_bundle_artifacts(
        bundle,
        output_dir,
        bundle_name=bundle_name,
    )


def load_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckBundleArtifactManifest:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("legacy validation batch run manifest check bundle manifest must be a JSON object")

    artifacts_data = data.get("artifacts")
    if not isinstance(artifacts_data, list) or not artifacts_data:
        raise ValueError("legacy validation batch run manifest check bundle manifest must contain artifacts")
    artifacts = [
        _artifact_from_mapping(item, manifest_path.parent)
        for item in artifacts_data
    ]
    artifact_count = int(data.get("artifact_count", -1))
    if artifact_count != len(artifacts):
        raise ValueError(
            "legacy validation batch run manifest check bundle manifest artifact_count must match artifacts"
        )
    kinds = [artifact.kind for artifact in artifacts]
    if len(kinds) != len(set(kinds)):
        raise ValueError(
            "legacy validation batch run manifest check bundle manifest must contain unique artifact kinds"
        )
    required_kinds = {
        "batch_manifest_check_bundle_json",
        "batch_manifest_check_bundle_csv",
        "batch_manifest_check_bundle_manifest_json",
    }
    missing_kinds = sorted(required_kinds.difference(kinds))
    if missing_kinds:
        raise ValueError(
            "legacy validation batch run manifest check bundle manifest is missing artifact kinds: "
            f"{missing_kinds}"
        )
    if require_existing_artifacts:
        missing = [
            artifact.path
            for artifact in artifacts
            if not artifact.path.exists()
        ]
        if missing:
            raise ValueError(
                "legacy validation batch run manifest check bundle manifest references missing artifacts: "
                f"{missing}"
            )
    return LegacyValidationBatchRunManifestCheckBundleArtifactManifest(
        bundle_name=str(data.get("bundle_name", "")),
        matches=bool(data.get("matches")),
        manifest_count=int(data.get("manifest_count", 0)),
        total_runs=int(data.get("total_runs", 0)),
        checked_artifact_count=int(data.get("checked_artifact_count", 0)),
        issue_count=int(data.get("issue_count", 0)),
        artifact_count=artifact_count,
        artifacts=artifacts,
    )


def load_legacy_validation_batch_run_manifest_check_bundle_payload_from_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> dict:
    manifest = load_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest(
        path,
        require_existing_artifacts=require_existing_artifacts,
    )
    bundle_artifact = manifest.artifact_for_kind("batch_manifest_check_bundle_json")
    if bundle_artifact is None:
        raise ValueError(
            "legacy validation batch run manifest check bundle manifest must contain "
            "batch_manifest_check_bundle_json"
        )
    with bundle_artifact.path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("legacy validation batch run manifest check bundle artifact must be a JSON object")
    expected_values = {
        "matches": manifest.matches,
        "manifest_count": manifest.manifest_count,
        "total_runs": manifest.total_runs,
        "checked_artifact_count": manifest.checked_artifact_count,
        "issue_count": manifest.issue_count,
    }
    for field_name, expected_value in expected_values.items():
        if payload.get(field_name) != expected_value:
            raise ValueError(
                "legacy validation batch run manifest check bundle artifact does not match "
                f"manifest field {field_name}"
            )
    return payload


def _is_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest(
    path: Path,
) -> bool:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    artifacts_data = data.get("artifacts")
    if not isinstance(artifacts_data, list):
        return False
    kinds = {
        str(artifact.get("kind", ""))
        for artifact in artifacts_data
        if isinstance(artifact, dict)
    }
    return {
        "batch_manifest_check_bundle_json",
        "batch_manifest_check_bundle_csv",
        "batch_manifest_check_bundle_manifest_json",
    }.issubset(kinds)


def load_legacy_validation_batch_run_manifest_check_bundle_payloads_from_directory(
    input_dir: str | Path,
    *,
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> list[dict]:
    directory_path = Path(input_dir)
    manifest_paths = [
        manifest_path
        for manifest_path in sorted(directory_path.glob(pattern))
        if _is_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest(
            manifest_path
        )
    ]
    if not manifest_paths:
        raise ValueError(
            "legacy validation batch run manifest check bundle directory contains no manifests"
        )
    return [
        load_legacy_validation_batch_run_manifest_check_bundle_payload_from_manifest(
            manifest_path,
            require_existing_artifacts=require_existing_artifacts,
        )
        for manifest_path in manifest_paths
    ]


def build_legacy_validation_batch_run_manifest_check_payload_summary(
    payloads: list[dict],
) -> LegacyValidationBatchRunManifestCheckPayloadSummary:
    if not payloads:
        raise ValueError(
            "legacy validation batch run manifest check payload summary requires payloads"
        )
    for payload in payloads:
        if not isinstance(payload, dict):
            raise ValueError(
                "legacy validation batch run manifest check payload summary entries must be objects"
            )
    return LegacyValidationBatchRunManifestCheckPayloadSummary(
        bundle_count=len(payloads),
        matches=all(bool(payload.get("matches")) for payload in payloads),
        manifest_count=sum(int(payload.get("manifest_count", 0)) for payload in payloads),
        total_runs=sum(int(payload.get("total_runs", 0)) for payload in payloads),
        checked_artifact_count=sum(
            int(payload.get("checked_artifact_count", 0))
            for payload in payloads
        ),
        issue_count=sum(int(payload.get("issue_count", 0)) for payload in payloads),
        failing_bundle_count=sum(
            1 for payload in payloads if not bool(payload.get("matches"))
        ),
    )


def _batch_run_manifest_check_payload_summary_from_mapping(
    payload: dict,
) -> LegacyValidationBatchRunManifestCheckPayloadSummary:
    if not isinstance(payload, dict):
        raise ValueError(
            "legacy validation batch run manifest check payload summary entry must be an object"
        )
    return LegacyValidationBatchRunManifestCheckPayloadSummary(
        bundle_count=int(payload.get("bundle_count", 0)),
        matches=bool(payload.get("matches")),
        manifest_count=int(payload.get("manifest_count", 0)),
        total_runs=int(payload.get("total_runs", 0)),
        checked_artifact_count=int(payload.get("checked_artifact_count", 0)),
        issue_count=int(payload.get("issue_count", 0)),
        failing_bundle_count=int(payload.get("failing_bundle_count", 0)),
    )


def build_legacy_validation_batch_run_manifest_check_payload_summary_bundle(
    payloads: list[dict],
    *,
    manifest_paths: list[str | Path] | None = None,
) -> LegacyValidationBatchRunManifestCheckPayloadSummaryBundle:
    if not payloads:
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle requires payloads"
        )
    summaries = [
        _batch_run_manifest_check_payload_summary_from_mapping(payload)
        for payload in payloads
    ]
    resolved_manifest_paths = [
        Path(path)
        for path in (manifest_paths if manifest_paths is not None else [])
    ]
    if resolved_manifest_paths and len(resolved_manifest_paths) != len(summaries):
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle manifest_paths "
            "must match payloads"
        )
    return LegacyValidationBatchRunManifestCheckPayloadSummaryBundle(
        summary_count=len(summaries),
        matches=all(summary.matches for summary in summaries),
        bundle_count=sum(summary.bundle_count for summary in summaries),
        manifest_count=sum(summary.manifest_count for summary in summaries),
        total_runs=sum(summary.total_runs for summary in summaries),
        checked_artifact_count=sum(
            summary.checked_artifact_count
            for summary in summaries
        ),
        issue_count=sum(summary.issue_count for summary in summaries),
        failing_bundle_count=sum(
            summary.failing_bundle_count
            for summary in summaries
        ),
        failing_summary_count=sum(
            1 for summary in summaries if not summary.matches
        ),
        summaries=summaries,
        manifest_paths=resolved_manifest_paths,
    )


def summarize_legacy_validation_batch_run_manifest_check_payloads_from_directory(
    input_dir: str | Path,
    *,
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckPayloadSummary:
    payloads = load_legacy_validation_batch_run_manifest_check_bundle_payloads_from_directory(
        input_dir,
        pattern=pattern,
        require_existing_artifacts=require_existing_artifacts,
    )
    return build_legacy_validation_batch_run_manifest_check_payload_summary(payloads)


def write_legacy_validation_batch_run_manifest_check_payload_summary_json(
    summary: LegacyValidationBatchRunManifestCheckPayloadSummary,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            legacy_validation_batch_run_manifest_check_payload_summary_to_dict(summary),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return output_path


def write_legacy_validation_batch_run_manifest_check_payload_summary_csv(
    summary: LegacyValidationBatchRunManifestCheckPayloadSummary,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "matches",
                "bundle_count",
                "manifest_count",
                "total_runs",
                "checked_artifact_count",
                "issue_count",
                "failing_bundle_count",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "matches": str(summary.matches),
                "bundle_count": summary.bundle_count,
                "manifest_count": summary.manifest_count,
                "total_runs": summary.total_runs,
                "checked_artifact_count": summary.checked_artifact_count,
                "issue_count": summary.issue_count,
                "failing_bundle_count": summary.failing_bundle_count,
            }
        )
    return output_path


def _write_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest(
    *,
    bundle_name: str,
    summary: LegacyValidationBatchRunManifestCheckPayloadSummary,
    artifacts: list[LegacyValidationArtifact],
    path: Path,
) -> Path:
    payload = {
        "bundle_name": bundle_name,
        "matches": summary.matches,
        "bundle_count": summary.bundle_count,
        "manifest_count": summary.manifest_count,
        "total_runs": summary.total_runs,
        "checked_artifact_count": summary.checked_artifact_count,
        "issue_count": summary.issue_count,
        "failing_bundle_count": summary.failing_bundle_count,
        "artifact_count": len(artifacts),
        "artifacts": [
            _artifact_to_mapping(artifact, path.parent)
            for artifact in artifacts
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts(
    summary: LegacyValidationBatchRunManifestCheckPayloadSummary,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_batch_manifest_check_payload_summary",
) -> LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest:
    output_path = Path(output_dir)
    artifacts = [
        LegacyValidationArtifact(
            kind="batch_manifest_check_payload_summary_json",
            path=write_legacy_validation_batch_run_manifest_check_payload_summary_json(
                summary,
                output_path / f"{bundle_name}.json",
            ),
        ),
        LegacyValidationArtifact(
            kind="batch_manifest_check_payload_summary_csv",
            path=write_legacy_validation_batch_run_manifest_check_payload_summary_csv(
                summary,
                output_path / f"{bundle_name}.csv",
            ),
        ),
    ]
    manifest_artifact = LegacyValidationArtifact(
        kind="batch_manifest_check_payload_summary_manifest_json",
        path=output_path / f"{bundle_name}_artifacts.json",
    )
    artifacts.append(manifest_artifact)
    _write_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest(
        bundle_name=bundle_name,
        summary=summary,
        artifacts=artifacts,
        path=manifest_artifact.path,
    )
    return LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest(
        bundle_name=bundle_name,
        matches=summary.matches,
        bundle_count=summary.bundle_count,
        manifest_count=summary.manifest_count,
        total_runs=summary.total_runs,
        checked_artifact_count=summary.checked_artifact_count,
        issue_count=summary.issue_count,
        failing_bundle_count=summary.failing_bundle_count,
        artifact_count=len(artifacts),
        artifacts=artifacts,
    )


def write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_batch_manifest_check_payload_summary",
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest:
    summary = summarize_legacy_validation_batch_run_manifest_check_payloads_from_directory(
        input_dir,
        pattern=pattern,
        require_existing_artifacts=require_existing_artifacts,
    )
    return write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts(
        summary,
        output_dir,
        bundle_name=bundle_name,
    )


def load_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("legacy validation batch run manifest check payload summary manifest must be a JSON object")

    artifacts_data = data.get("artifacts")
    if not isinstance(artifacts_data, list) or not artifacts_data:
        raise ValueError("legacy validation batch run manifest check payload summary manifest must contain artifacts")
    artifacts = [
        _artifact_from_mapping(item, manifest_path.parent)
        for item in artifacts_data
    ]
    artifact_count = int(data.get("artifact_count", -1))
    if artifact_count != len(artifacts):
        raise ValueError(
            "legacy validation batch run manifest check payload summary manifest artifact_count must match artifacts"
        )
    kinds = [artifact.kind for artifact in artifacts]
    if len(kinds) != len(set(kinds)):
        raise ValueError(
            "legacy validation batch run manifest check payload summary manifest must contain unique artifact kinds"
        )
    required_kinds = {
        "batch_manifest_check_payload_summary_json",
        "batch_manifest_check_payload_summary_csv",
        "batch_manifest_check_payload_summary_manifest_json",
    }
    missing_kinds = sorted(required_kinds.difference(kinds))
    if missing_kinds:
        raise ValueError(
            "legacy validation batch run manifest check payload summary manifest is missing artifact kinds: "
            f"{missing_kinds}"
        )
    if require_existing_artifacts:
        missing = [
            artifact.path
            for artifact in artifacts
            if not artifact.path.exists()
        ]
        if missing:
            raise ValueError(
                "legacy validation batch run manifest check payload summary manifest references missing artifacts: "
                f"{missing}"
            )
    return LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest(
        bundle_name=str(data.get("bundle_name", "")),
        matches=bool(data.get("matches")),
        bundle_count=int(data.get("bundle_count", 0)),
        manifest_count=int(data.get("manifest_count", 0)),
        total_runs=int(data.get("total_runs", 0)),
        checked_artifact_count=int(data.get("checked_artifact_count", 0)),
        issue_count=int(data.get("issue_count", 0)),
        failing_bundle_count=int(data.get("failing_bundle_count", 0)),
        artifact_count=artifact_count,
        artifacts=artifacts,
    )


def load_legacy_validation_batch_run_manifest_check_payload_summary_from_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> dict:
    manifest = load_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest(
        path,
        require_existing_artifacts=require_existing_artifacts,
    )
    summary_artifact = manifest.artifact_for_kind(
        "batch_manifest_check_payload_summary_json"
    )
    if summary_artifact is None:
        raise ValueError(
            "legacy validation batch run manifest check payload summary manifest must contain "
            "batch_manifest_check_payload_summary_json"
        )
    with summary_artifact.path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("legacy validation batch run manifest check payload summary artifact must be a JSON object")
    expected_values = {
        "matches": manifest.matches,
        "bundle_count": manifest.bundle_count,
        "manifest_count": manifest.manifest_count,
        "total_runs": manifest.total_runs,
        "checked_artifact_count": manifest.checked_artifact_count,
        "issue_count": manifest.issue_count,
        "failing_bundle_count": manifest.failing_bundle_count,
    }
    for field_name, expected_value in expected_values.items():
        if payload.get(field_name) != expected_value:
            raise ValueError(
                "legacy validation batch run manifest check payload summary artifact does not match "
                f"manifest field {field_name}"
            )
    return payload


def _is_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest(
    path: Path,
) -> bool:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    artifacts_data = data.get("artifacts")
    if not isinstance(artifacts_data, list):
        return False
    kinds = {
        str(artifact.get("kind", ""))
        for artifact in artifacts_data
        if isinstance(artifact, dict)
    }
    return {
        "batch_manifest_check_payload_summary_json",
        "batch_manifest_check_payload_summary_csv",
        "batch_manifest_check_payload_summary_manifest_json",
    }.issubset(kinds)


def load_legacy_validation_batch_run_manifest_check_payload_summary_payloads_from_directory(
    input_dir: str | Path,
    *,
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> list[dict]:
    directory_path = Path(input_dir)
    manifest_paths = [
        manifest_path
        for manifest_path in sorted(directory_path.glob(pattern))
        if _is_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest(
            manifest_path
        )
    ]
    if not manifest_paths:
        raise ValueError(
            "legacy validation batch run manifest check payload summary directory contains no manifests"
        )
    return [
        load_legacy_validation_batch_run_manifest_check_payload_summary_from_manifest(
            manifest_path,
            require_existing_artifacts=require_existing_artifacts,
        )
        for manifest_path in manifest_paths
    ]


def summarize_legacy_validation_batch_run_manifest_check_payload_summaries_from_directory(
    input_dir: str | Path,
    *,
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckPayloadSummaryBundle:
    directory_path = Path(input_dir)
    manifest_paths = [
        manifest_path
        for manifest_path in sorted(directory_path.glob(pattern))
        if _is_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest(
            manifest_path
        )
    ]
    if not manifest_paths:
        raise ValueError(
            "legacy validation batch run manifest check payload summary directory contains no manifests"
        )
    payloads = [
        load_legacy_validation_batch_run_manifest_check_payload_summary_from_manifest(
            manifest_path,
            require_existing_artifacts=require_existing_artifacts,
        )
        for manifest_path in manifest_paths
    ]
    return build_legacy_validation_batch_run_manifest_check_payload_summary_bundle(
        payloads,
        manifest_paths=manifest_paths,
    )


def write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_json(
    bundle: LegacyValidationBatchRunManifestCheckPayloadSummaryBundle,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            legacy_validation_batch_run_manifest_check_payload_summary_bundle_to_dict(
                bundle
            ),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return output_path


def write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_csv(
    bundle: LegacyValidationBatchRunManifestCheckPayloadSummaryBundle,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "manifest_path",
                "matches",
                "bundle_count",
                "manifest_count",
                "total_runs",
                "checked_artifact_count",
                "issue_count",
                "failing_bundle_count",
            ],
        )
        writer.writeheader()
        for index, summary in enumerate(bundle.summaries):
            manifest_path = (
                str(bundle.manifest_paths[index])
                if index < len(bundle.manifest_paths)
                else ""
            )
            writer.writerow(
                {
                    "manifest_path": manifest_path,
                    "matches": str(summary.matches),
                    "bundle_count": summary.bundle_count,
                    "manifest_count": summary.manifest_count,
                    "total_runs": summary.total_runs,
                    "checked_artifact_count": summary.checked_artifact_count,
                    "issue_count": summary.issue_count,
                    "failing_bundle_count": summary.failing_bundle_count,
                }
            )
    return output_path


def _write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifact_manifest(
    *,
    bundle_name: str,
    bundle: LegacyValidationBatchRunManifestCheckPayloadSummaryBundle,
    artifacts: list[LegacyValidationArtifact],
    path: Path,
) -> Path:
    payload = {
        "bundle_name": bundle_name,
        "matches": bundle.matches,
        "summary_count": bundle.summary_count,
        "bundle_count": bundle.bundle_count,
        "manifest_count": bundle.manifest_count,
        "total_runs": bundle.total_runs,
        "checked_artifact_count": bundle.checked_artifact_count,
        "issue_count": bundle.issue_count,
        "failing_bundle_count": bundle.failing_bundle_count,
        "failing_summary_count": bundle.failing_summary_count,
        "artifact_count": len(artifacts),
        "artifacts": [
            _artifact_to_mapping(artifact, path.parent)
            for artifact in artifacts
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts(
    bundle: LegacyValidationBatchRunManifestCheckPayloadSummaryBundle,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_diagnostic_summary_bundle",
) -> LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest:
    output_path = Path(output_dir)
    artifacts = [
        LegacyValidationArtifact(
            kind="batch_manifest_check_payload_summary_bundle_json",
            path=write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_json(
                bundle,
                output_path / f"{bundle_name}.json",
            ),
        ),
        LegacyValidationArtifact(
            kind="batch_manifest_check_payload_summary_bundle_csv",
            path=write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_csv(
                bundle,
                output_path / f"{bundle_name}.csv",
            ),
        ),
    ]
    manifest_artifact = LegacyValidationArtifact(
        kind="batch_manifest_check_payload_summary_bundle_manifest_json",
        path=output_path / f"{bundle_name}_artifacts.json",
    )
    artifacts.append(manifest_artifact)
    _write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifact_manifest(
        bundle_name=bundle_name,
        bundle=bundle,
        artifacts=artifacts,
        path=manifest_artifact.path,
    )
    return LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest(
        bundle_name=bundle_name,
        matches=bundle.matches,
        summary_count=bundle.summary_count,
        bundle_count=bundle.bundle_count,
        manifest_count=bundle.manifest_count,
        total_runs=bundle.total_runs,
        checked_artifact_count=bundle.checked_artifact_count,
        issue_count=bundle.issue_count,
        failing_bundle_count=bundle.failing_bundle_count,
        failing_summary_count=bundle.failing_summary_count,
        artifact_count=len(artifacts),
        artifacts=artifacts,
    )


def write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts_from_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_diagnostic_summary_bundle",
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest:
    bundle = summarize_legacy_validation_batch_run_manifest_check_payload_summaries_from_directory(
        input_dir,
        pattern=pattern,
        require_existing_artifacts=require_existing_artifacts,
    )
    return write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts(
        bundle,
        output_dir,
        bundle_name=bundle_name,
    )


def load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifact_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("legacy validation batch run manifest check payload summary bundle manifest must be a JSON object")

    artifacts_data = data.get("artifacts")
    if not isinstance(artifacts_data, list) or not artifacts_data:
        raise ValueError("legacy validation batch run manifest check payload summary bundle manifest must contain artifacts")
    artifacts = [
        _artifact_from_mapping(item, manifest_path.parent)
        for item in artifacts_data
    ]
    artifact_count = int(data.get("artifact_count", -1))
    if artifact_count != len(artifacts):
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle manifest artifact_count must match artifacts"
        )
    kinds = [artifact.kind for artifact in artifacts]
    if len(kinds) != len(set(kinds)):
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle manifest must contain unique artifact kinds"
        )
    required_kinds = {
        "batch_manifest_check_payload_summary_bundle_json",
        "batch_manifest_check_payload_summary_bundle_csv",
        "batch_manifest_check_payload_summary_bundle_manifest_json",
    }
    missing_kinds = sorted(required_kinds.difference(kinds))
    if missing_kinds:
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle manifest is missing artifact kinds: "
            f"{missing_kinds}"
        )
    if require_existing_artifacts:
        missing = [
            artifact.path
            for artifact in artifacts
            if not artifact.path.exists()
        ]
        if missing:
            raise ValueError(
                "legacy validation batch run manifest check payload summary bundle manifest references missing artifacts: "
                f"{missing}"
            )
    return LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest(
        bundle_name=str(data.get("bundle_name", "")),
        matches=bool(data.get("matches")),
        summary_count=int(data.get("summary_count", 0)),
        bundle_count=int(data.get("bundle_count", 0)),
        manifest_count=int(data.get("manifest_count", 0)),
        total_runs=int(data.get("total_runs", 0)),
        checked_artifact_count=int(data.get("checked_artifact_count", 0)),
        issue_count=int(data.get("issue_count", 0)),
        failing_bundle_count=int(data.get("failing_bundle_count", 0)),
        failing_summary_count=int(data.get("failing_summary_count", 0)),
        artifact_count=artifact_count,
        artifacts=artifacts,
    )


def load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> dict:
    manifest = load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifact_manifest(
        path,
        require_existing_artifacts=require_existing_artifacts,
    )
    bundle_artifact = manifest.artifact_for_kind(
        "batch_manifest_check_payload_summary_bundle_json"
    )
    if bundle_artifact is None:
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle manifest must contain "
            "batch_manifest_check_payload_summary_bundle_json"
        )
    with bundle_artifact.path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("legacy validation batch run manifest check payload summary bundle artifact must be a JSON object")
    expected_values = {
        "matches": manifest.matches,
        "summary_count": manifest.summary_count,
        "bundle_count": manifest.bundle_count,
        "manifest_count": manifest.manifest_count,
        "total_runs": manifest.total_runs,
        "checked_artifact_count": manifest.checked_artifact_count,
        "issue_count": manifest.issue_count,
        "failing_bundle_count": manifest.failing_bundle_count,
        "failing_summary_count": manifest.failing_summary_count,
    }
    for field_name, expected_value in expected_values.items():
        if payload.get(field_name) != expected_value:
            raise ValueError(
                "legacy validation batch run manifest check payload summary bundle artifact does not match "
                f"manifest field {field_name}"
            )
    return payload


def _legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_mapping(
    payload: dict,
) -> LegacyValidationBatchRunManifestCheckPayloadSummaryBundle:
    if not isinstance(payload, dict):
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle must be an object"
        )
    summaries_data = payload.get("summaries", [])
    if not isinstance(summaries_data, list):
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle summaries must be a list"
        )
    manifest_paths_data = payload.get("manifest_paths", [])
    if not isinstance(manifest_paths_data, list):
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle manifest_paths must be a list"
        )
    summaries = [
        _batch_run_manifest_check_payload_summary_from_mapping(summary)
        for summary in summaries_data
    ]
    manifest_paths = [Path(path) for path in manifest_paths_data]
    summary_count = int(payload.get("summary_count", len(summaries)))
    if summary_count != len(summaries):
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle summary_count must match summaries"
        )
    if manifest_paths and len(manifest_paths) != len(summaries):
        raise ValueError(
            "legacy validation batch run manifest check payload summary bundle manifest_paths must match summaries"
        )
    return LegacyValidationBatchRunManifestCheckPayloadSummaryBundle(
        summary_count=summary_count,
        matches=bool(payload.get("matches")),
        bundle_count=int(payload.get("bundle_count", 0)),
        manifest_count=int(payload.get("manifest_count", 0)),
        total_runs=int(payload.get("total_runs", 0)),
        checked_artifact_count=int(payload.get("checked_artifact_count", 0)),
        issue_count=int(payload.get("issue_count", 0)),
        failing_bundle_count=int(payload.get("failing_bundle_count", 0)),
        failing_summary_count=int(payload.get("failing_summary_count", 0)),
        summaries=summaries,
        manifest_paths=manifest_paths,
    )


def build_legacy_validation_acceptance_verdict(
    bundle: LegacyValidationBatchRunManifestCheckPayloadSummaryBundle,
) -> LegacyValidationAcceptanceVerdict:
    reasons: list[str] = []
    if bundle.summary_count <= 0:
        reasons.append("no diagnostic summary bundles were evaluated")
    if not bundle.matches:
        reasons.append("at least one diagnostic summary bundle did not match")
    if bundle.issue_count > 0:
        reasons.append(f"{bundle.issue_count} diagnostic issue(s) were reported")
    if bundle.failing_bundle_count > 0:
        reasons.append(
            f"{bundle.failing_bundle_count} diagnostic bundle(s) failed"
        )
    if bundle.failing_summary_count > 0:
        reasons.append(
            f"{bundle.failing_summary_count} diagnostic summary bundle(s) failed"
        )
    passed = not reasons
    return LegacyValidationAcceptanceVerdict(
        passed=passed,
        status="passed" if passed else "failed",
        reason_count=len(reasons),
        reasons=reasons,
        summary_count=bundle.summary_count,
        bundle_count=bundle.bundle_count,
        manifest_count=bundle.manifest_count,
        total_runs=bundle.total_runs,
        checked_artifact_count=bundle.checked_artifact_count,
        issue_count=bundle.issue_count,
        failing_bundle_count=bundle.failing_bundle_count,
        failing_summary_count=bundle.failing_summary_count,
    )


def build_legacy_validation_acceptance_verdict_from_summary_bundle_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationAcceptanceVerdict:
    payload = load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest(
        path,
        require_existing_artifacts=require_existing_artifacts,
    )
    bundle = _legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_mapping(
        payload
    )
    return build_legacy_validation_acceptance_verdict(bundle)


def write_legacy_validation_acceptance_verdict_json(
    verdict: LegacyValidationAcceptanceVerdict,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            legacy_validation_acceptance_verdict_to_dict(verdict),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return output_path


def write_legacy_validation_acceptance_verdict_csv(
    verdict: LegacyValidationAcceptanceVerdict,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "passed",
                "status",
                "reason_count",
                "summary_count",
                "bundle_count",
                "manifest_count",
                "total_runs",
                "checked_artifact_count",
                "issue_count",
                "failing_bundle_count",
                "failing_summary_count",
                "reasons",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "passed": str(verdict.passed),
                "status": verdict.status,
                "reason_count": verdict.reason_count,
                "summary_count": verdict.summary_count,
                "bundle_count": verdict.bundle_count,
                "manifest_count": verdict.manifest_count,
                "total_runs": verdict.total_runs,
                "checked_artifact_count": verdict.checked_artifact_count,
                "issue_count": verdict.issue_count,
                "failing_bundle_count": verdict.failing_bundle_count,
                "failing_summary_count": verdict.failing_summary_count,
                "reasons": ";".join(verdict.reasons),
            }
        )
    return output_path


def _write_legacy_validation_acceptance_verdict_artifact_manifest(
    *,
    bundle_name: str,
    verdict: LegacyValidationAcceptanceVerdict,
    artifacts: list[LegacyValidationArtifact],
    path: Path,
) -> Path:
    payload = {
        "bundle_name": bundle_name,
        "passed": verdict.passed,
        "status": verdict.status,
        "reason_count": verdict.reason_count,
        "artifact_count": len(artifacts),
        "artifacts": [
            _artifact_to_mapping(artifact, path.parent)
            for artifact in artifacts
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_legacy_validation_acceptance_verdict_artifacts(
    verdict: LegacyValidationAcceptanceVerdict,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_acceptance_verdict",
) -> LegacyValidationAcceptanceVerdictArtifactManifest:
    output_path = Path(output_dir)
    artifacts = [
        LegacyValidationArtifact(
            kind="acceptance_verdict_json",
            path=write_legacy_validation_acceptance_verdict_json(
                verdict,
                output_path / f"{bundle_name}.json",
            ),
        ),
        LegacyValidationArtifact(
            kind="acceptance_verdict_csv",
            path=write_legacy_validation_acceptance_verdict_csv(
                verdict,
                output_path / f"{bundle_name}.csv",
            ),
        ),
    ]
    manifest_artifact = LegacyValidationArtifact(
        kind="acceptance_verdict_manifest_json",
        path=output_path / f"{bundle_name}_artifacts.json",
    )
    artifacts.append(manifest_artifact)
    _write_legacy_validation_acceptance_verdict_artifact_manifest(
        bundle_name=bundle_name,
        verdict=verdict,
        artifacts=artifacts,
        path=manifest_artifact.path,
    )
    return LegacyValidationAcceptanceVerdictArtifactManifest(
        bundle_name=bundle_name,
        passed=verdict.passed,
        status=verdict.status,
        reason_count=verdict.reason_count,
        artifact_count=len(artifacts),
        artifacts=artifacts,
    )


def write_legacy_validation_acceptance_verdict_artifacts_from_summary_bundle_manifest(
    path: str | Path,
    output_dir: str | Path,
    *,
    bundle_name: str = "legacy_validation_acceptance_verdict",
    require_existing_artifacts: bool = True,
) -> LegacyValidationAcceptanceVerdictArtifactManifest:
    verdict = build_legacy_validation_acceptance_verdict_from_summary_bundle_manifest(
        path,
        require_existing_artifacts=require_existing_artifacts,
    )
    return write_legacy_validation_acceptance_verdict_artifacts(
        verdict,
        output_dir,
        bundle_name=bundle_name,
    )


def write_legacy_validation_acceptance_run_artifacts_from_summary_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    run_name: str = "legacy_validation_acceptance_run",
    summary_bundle_name: str = "legacy_validation_diagnostic_summary_bundle",
    verdict_bundle_name: str = "legacy_validation_acceptance_verdict",
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationAcceptanceRunResult:
    output_path = Path(output_dir)
    summary_manifest = write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts_from_directory(
        input_dir,
        output_path / "summary_bundle",
        bundle_name=summary_bundle_name,
        pattern=pattern,
        require_existing_artifacts=require_existing_artifacts,
    )
    verdict_manifest = write_legacy_validation_acceptance_verdict_artifacts_from_summary_bundle_manifest(
        summary_manifest.artifacts[-1].path,
        output_path / "verdict",
        bundle_name=verdict_bundle_name,
        require_existing_artifacts=require_existing_artifacts,
    )
    run_manifest_path = write_legacy_validation_acceptance_run_manifest(
        run_name=run_name,
        summary_bundle_manifest_path=summary_manifest.artifacts[-1].path,
        verdict_manifest_path=verdict_manifest.artifacts[-1].path,
        output_path=output_path / f"{run_name}.json",
        require_existing_artifacts=require_existing_artifacts,
    )
    return LegacyValidationAcceptanceRunResult(
        summary_bundle_manifest=summary_manifest,
        verdict_manifest=verdict_manifest,
        run_manifest_path=run_manifest_path,
    )


def write_legacy_validation_acceptance_run_manifest(
    *,
    run_name: str,
    summary_bundle_manifest_path: str | Path,
    verdict_manifest_path: str | Path,
    output_path: str | Path,
    require_existing_artifacts: bool = True,
) -> Path:
    summary_payload = load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest(
        summary_bundle_manifest_path,
        require_existing_artifacts=require_existing_artifacts,
    )
    verdict_payload = load_legacy_validation_acceptance_verdict_from_manifest(
        verdict_manifest_path,
        require_existing_artifacts=require_existing_artifacts,
    )
    expected_fields = [
        "total_runs",
        "issue_count",
        "failing_summary_count",
    ]
    for field_name in expected_fields:
        if summary_payload.get(field_name) != verdict_payload.get(field_name):
            raise ValueError(
                "legacy validation acceptance run manifest summary and verdict mismatch "
                f"for field {field_name}"
            )
    payload = {
        "run_name": run_name,
        "passed": bool(verdict_payload.get("passed")),
        "status": str(verdict_payload.get("status", "")),
        "summary_bundle_manifest_path": str(Path(summary_bundle_manifest_path)),
        "verdict_manifest_path": str(Path(verdict_manifest_path)),
        "total_runs": int(verdict_payload.get("total_runs", 0)),
        "issue_count": int(verdict_payload.get("issue_count", 0)),
        "failing_summary_count": int(verdict_payload.get("failing_summary_count", 0)),
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_legacy_validation_acceptance_run_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationAcceptanceRunManifest:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("legacy validation acceptance run manifest must be a JSON object")

    run_name = str(payload.get("run_name", "")).strip()
    if not run_name:
        raise ValueError("legacy validation acceptance run manifest must contain a run_name")

    summary_manifest_data = str(payload.get("summary_bundle_manifest_path", "")).strip()
    verdict_manifest_data = str(payload.get("verdict_manifest_path", "")).strip()
    if not summary_manifest_data:
        raise ValueError(
            "legacy validation acceptance run manifest must contain a summary_bundle_manifest_path"
        )
    if not verdict_manifest_data:
        raise ValueError(
            "legacy validation acceptance run manifest must contain a verdict_manifest_path"
        )
    summary_manifest_path = _resolve_artifact_path(
        summary_manifest_data,
        manifest_path.parent,
    )
    verdict_manifest_path = _resolve_artifact_path(
        verdict_manifest_data,
        manifest_path.parent,
    )

    if require_existing_artifacts:
        missing = [
            item
            for item in [summary_manifest_path, verdict_manifest_path]
            if not item.exists()
        ]
        if missing:
            raise ValueError(
                "legacy validation acceptance run manifest references missing artifacts: "
                f"{missing}"
            )
        summary_payload = load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest(
            summary_manifest_path
        )
        verdict_payload = load_legacy_validation_acceptance_verdict_from_manifest(
            verdict_manifest_path
        )
        expected_fields = {
            "passed": bool(verdict_payload.get("passed")),
            "status": str(verdict_payload.get("status", "")),
            "total_runs": int(verdict_payload.get("total_runs", 0)),
            "issue_count": int(verdict_payload.get("issue_count", 0)),
            "failing_summary_count": int(verdict_payload.get("failing_summary_count", 0)),
        }
        for field_name, expected_value in expected_fields.items():
            if payload.get(field_name) != expected_value:
                raise ValueError(
                    "legacy validation acceptance run manifest does not match "
                    f"verdict field {field_name}"
                )
        for field_name in ["total_runs", "issue_count", "failing_summary_count"]:
            if summary_payload.get(field_name) != verdict_payload.get(field_name):
                raise ValueError(
                    "legacy validation acceptance run manifest summary and verdict mismatch "
                    f"for field {field_name}"
                )

    return LegacyValidationAcceptanceRunManifest(
        run_name=run_name,
        passed=bool(payload.get("passed")),
        status=str(payload.get("status", "")),
        summary_bundle_manifest_path=summary_manifest_path,
        verdict_manifest_path=verdict_manifest_path,
        total_runs=int(payload.get("total_runs", 0)),
        issue_count=int(payload.get("issue_count", 0)),
        failing_summary_count=int(payload.get("failing_summary_count", 0)),
    )


def load_legacy_validation_acceptance_verdict_artifact_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> LegacyValidationAcceptanceVerdictArtifactManifest:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("legacy validation acceptance verdict manifest must be a JSON object")

    artifacts_data = data.get("artifacts")
    if not isinstance(artifacts_data, list) or not artifacts_data:
        raise ValueError("legacy validation acceptance verdict manifest must contain artifacts")
    artifacts = [
        _artifact_from_mapping(item, manifest_path.parent)
        for item in artifacts_data
    ]
    artifact_count = int(data.get("artifact_count", -1))
    if artifact_count != len(artifacts):
        raise ValueError(
            "legacy validation acceptance verdict manifest artifact_count must match artifacts"
        )
    kinds = [artifact.kind for artifact in artifacts]
    if len(kinds) != len(set(kinds)):
        raise ValueError(
            "legacy validation acceptance verdict manifest must contain unique artifact kinds"
        )
    required_kinds = {
        "acceptance_verdict_json",
        "acceptance_verdict_csv",
        "acceptance_verdict_manifest_json",
    }
    missing_kinds = sorted(required_kinds.difference(kinds))
    if missing_kinds:
        raise ValueError(
            "legacy validation acceptance verdict manifest is missing artifact kinds: "
            f"{missing_kinds}"
        )
    if require_existing_artifacts:
        missing = [
            artifact.path
            for artifact in artifacts
            if not artifact.path.exists()
        ]
        if missing:
            raise ValueError(
                "legacy validation acceptance verdict manifest references missing artifacts: "
                f"{missing}"
            )
    return LegacyValidationAcceptanceVerdictArtifactManifest(
        bundle_name=str(data.get("bundle_name", "")),
        passed=bool(data.get("passed")),
        status=str(data.get("status", "")),
        reason_count=int(data.get("reason_count", 0)),
        artifact_count=artifact_count,
        artifacts=artifacts,
    )


def load_legacy_validation_acceptance_verdict_from_manifest(
    path: str | Path,
    *,
    require_existing_artifacts: bool = True,
) -> dict:
    manifest = load_legacy_validation_acceptance_verdict_artifact_manifest(
        path,
        require_existing_artifacts=require_existing_artifacts,
    )
    verdict_artifact = manifest.artifact_for_kind("acceptance_verdict_json")
    if verdict_artifact is None:
        raise ValueError(
            "legacy validation acceptance verdict manifest must contain acceptance_verdict_json"
        )
    with verdict_artifact.path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("legacy validation acceptance verdict artifact must be a JSON object")
    expected_values = {
        "passed": manifest.passed,
        "status": manifest.status,
        "reason_count": manifest.reason_count,
    }
    for field_name, expected_value in expected_values.items():
        if payload.get(field_name) != expected_value:
            raise ValueError(
                "legacy validation acceptance verdict artifact does not match "
                f"manifest field {field_name}"
            )
    return payload


def _batch_item_from_mapping(data: dict, fixture_base_path: Path) -> tuple[str, Path, str]:
    name = str(data.get("name", "")).strip()
    fixture_path_data = str(data.get("fixture_path", "")).strip()
    if not fixture_path_data:
        raise ValueError("legacy validation batch item must contain a fixture_path")
    fixture_path = Path(fixture_path_data)
    if not fixture_path.is_absolute():
        fixture_path = fixture_base_path / fixture_path

    output_subdir = str(data.get("output_subdir", name or fixture_path.stem)).strip()
    if not output_subdir:
        raise ValueError("legacy validation batch item must contain an output_subdir")
    if Path(output_subdir).is_absolute() or ".." in Path(output_subdir).parts:
        raise ValueError("legacy validation batch item output_subdir must be relative")

    return name or fixture_path.stem, fixture_path, output_subdir


def run_legacy_validation_batch_from_fixture(
    path: str | Path,
    output_dir: str | Path,
) -> LegacyValidationBatchRunResult:
    fixture_path = Path(path).resolve()
    with fixture_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("legacy validation batch fixture must be a JSON object")

    batch_name = str(data.get("batch_name", fixture_path.stem)).strip()
    if not batch_name:
        raise ValueError("legacy validation batch fixture must contain a batch_name")

    items_data = data.get("items")
    if not isinstance(items_data, list) or not items_data:
        raise ValueError("legacy validation batch fixture must contain a non-empty items list")

    output_path = Path(output_dir)
    runs: list[LegacyValidationBatchRunItem] = []
    manifest_paths: list[Path] = []
    item_names: set[str] = set()
    output_subdirs: set[str] = set()
    batch_items: list[tuple[str, Path, str]] = []

    for item_data in items_data:
        name, item_fixture_path, output_subdir = _batch_item_from_mapping(item_data, fixture_path.parent)
        if name in item_names:
            raise ValueError(f"legacy validation batch fixture contains duplicate item name: {name}")
        if output_subdir in output_subdirs:
            raise ValueError(
                "legacy validation batch fixture contains duplicate output_subdir: "
                f"{output_subdir}"
            )
        item_names.add(name)
        output_subdirs.add(output_subdir)
        batch_items.append((name, item_fixture_path, output_subdir))

    for name, item_fixture_path, output_subdir in batch_items:
        item_output_dir = output_path / output_subdir
        result = run_legacy_validation_from_fixture(item_fixture_path, item_output_dir)
        if not result.artifacts:
            raise ValueError(f"legacy validation batch item did not write artifacts: {name}")
        manifest_paths.append(result.artifacts[-1].path)
        runs.append(
            LegacyValidationBatchRunItem(
                name=name,
                fixture_path=item_fixture_path,
                output_dir=item_output_dir,
                result=result,
            )
        )

    summary_manifest = write_legacy_validation_report_summary_bundle_artifacts_from_manifests(
        manifest_paths,
        output_path / "summary",
        bundle_name=batch_name,
    )
    result = LegacyValidationBatchRunResult(
        batch_name=batch_name,
        fixture_path=fixture_path,
        output_dir=output_path,
        runs=runs,
        summary_manifest=summary_manifest,
        batch_manifest_path=output_path / f"{batch_name}_batch.json",
    )
    write_legacy_validation_batch_run_manifest(result, result.batch_manifest_path)
    return result


def run_legacy_validation_from_fixture(
    path: str | Path,
    output_dir: str | Path | None = None,
) -> LegacyValidationRunResult:
    fixture_path = Path(path).resolve()
    with fixture_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("legacy validation fixture must be a JSON object")

    target_items = data.get("targets")
    if not isinstance(target_items, list) or not target_items:
        raise ValueError("legacy validation fixture must contain a non-empty targets list")

    targets = [_target_from_mapping(item, fixture_path.parent) for item in target_items]
    _validate_unique_targets(targets)
    comparison = build_multi_period_legacy_comparison([_compare_target(target) for target in targets])
    report = build_legacy_validation_report_from_multi_period_comparison(comparison)

    written_reports: list[Path] = []
    artifacts: list[LegacyValidationArtifact] = []
    if output_dir is not None:
        output_path = Path(output_dir)
        report_name = str(data.get("report_name", fixture_path.stem))
        artifacts = [
            LegacyValidationArtifact(
                kind="report_json",
                path=write_legacy_validation_report_json(report, output_path / f"{report_name}.json"),
            ),
            LegacyValidationArtifact(
                kind="file_summary_csv",
                path=write_legacy_validation_report_csv(report, output_path / f"{report_name}.csv"),
            ),
            LegacyValidationArtifact(
                kind="field_summary_csv",
                path=write_legacy_validation_field_summary_csv(report, output_path / f"{report_name}_fields.csv"),
            ),
            LegacyValidationArtifact(
                kind="group_summary_csv",
                path=write_legacy_validation_group_summary_csv(report, output_path / f"{report_name}_groups.csv"),
            ),
            LegacyValidationArtifact(
                kind="period_summary_csv",
                path=write_legacy_validation_period_summary_csv(report, output_path / f"{report_name}_periods.csv"),
            ),
            LegacyValidationArtifact(
                kind="deviation_index_csv",
                path=write_legacy_validation_deviation_index_csv(report, output_path / f"{report_name}_deviations.csv"),
            ),
        ]
        manifest_artifact = LegacyValidationArtifact(
            kind="artifact_manifest_json",
            path=output_path / f"{report_name}_artifacts.json",
        )
        artifacts.append(manifest_artifact)
        _write_legacy_validation_artifact_manifest(
            report_name=report_name,
            fixture_path=fixture_path,
            report=report,
            artifacts=artifacts,
            path=manifest_artifact.path,
        )
        written_reports = [artifact.path for artifact in artifacts]

    return LegacyValidationRunResult(
        targets=targets,
        comparison=comparison,
        report=report,
        written_reports=written_reports,
        artifacts=artifacts,
    )
