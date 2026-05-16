from dataclasses import dataclass
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
class LegacyValidationRunResult:
    targets: list[LegacyValidationTarget]
    comparison: MultiPeriodLegacyComparison
    report: LegacyValidationReport
    written_reports: list[Path]
    artifacts: list[LegacyValidationArtifact]


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


def _artifact_to_mapping(artifact: LegacyValidationArtifact) -> dict:
    return {
        "kind": artifact.kind,
        "filename": artifact.path.name,
        "path": str(artifact.path),
    }


def _artifact_from_mapping(data: dict, manifest_base_path: Path) -> LegacyValidationArtifact:
    kind = str(data.get("kind", "")).strip()
    if not kind:
        raise ValueError("legacy validation artifact must contain a kind")
    path_data = str(data.get("path", "")).strip()
    if not path_data:
        raise ValueError("legacy validation artifact must contain a path")
    artifact_path = Path(path_data)
    if not artifact_path.is_absolute():
        artifact_path = manifest_base_path / artifact_path
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
            _artifact_to_mapping(artifact)
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


def summarize_legacy_validation_report_payloads_from_directory(
    path: str | Path,
    *,
    pattern: str = "**/*_artifacts.json",
    require_existing_artifacts: bool = True,
) -> LegacyValidationReportSummaryBundle:
    directory_path = Path(path)
    if not directory_path.is_dir():
        raise ValueError("legacy validation report summary directory must exist")
    manifest_paths = sorted(directory_path.glob(pattern))
    if not manifest_paths:
        raise ValueError("legacy validation report summary directory contains no manifests")
    return summarize_legacy_validation_report_payloads_from_manifests(
        manifest_paths,
        require_existing_artifacts=require_existing_artifacts,
    )


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
