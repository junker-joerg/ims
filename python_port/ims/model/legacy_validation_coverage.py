from dataclasses import dataclass, field
import argparse
import fnmatch
import json
from pathlib import Path
from typing import Any


LEGACY_AGRSICH_BACKLOG_CANDIDATES = {
    "insurer_stage_all": ["VUSK1L1.DAT", "VUSK1L2.DAT", "VUSK1L3.DAT", "VUSK1L4.DAT", "VUSK1L5.DAT"],
    "policyholder_rule": [
        "IMSVNR01.DAT",
        "IMSVNR02.DAT",
        "IMSVNR03.DAT",
        "IMSVNR04.DAT",
        "IMSVNR05.DAT",
        "IMSVNR06.DAT",
    ],
    "policyholder_class": ["IMSVNVK*.DAT"],
    "insurer_class": ["IMSVUVK*.DAT"],
    "parameter_output": ["VU014PR1.DAT"],
}


@dataclass(slots=True)
class LegacyValidationCoverageIssue:
    code: str
    message: str
    severity: str = "error"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(slots=True)
class LegacyValidationCoverageEntry:
    legacy_filename: str
    legacy_path: str
    legacy_source: str
    is_legacy_reference: bool
    subject_type: str
    export_filename: str
    level: str
    selector_kind: str
    selector_value: int | str | None
    start_period: int
    end_period: int
    period_count: int
    row_count: int
    covered: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "legacy_filename": self.legacy_filename,
            "legacy_path": self.legacy_path,
            "legacy_source": self.legacy_source,
            "is_legacy_reference": self.is_legacy_reference,
            "subject_type": self.subject_type,
            "export_filename": self.export_filename,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "start_period": self.start_period,
            "end_period": self.end_period,
            "period_count": self.period_count,
            "row_count": self.row_count,
            "covered": self.covered,
        }


@dataclass(slots=True)
class LegacyValidationCoverageGap:
    code: str
    legacy_filename: str
    legacy_path: str | None = None
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "legacy_filename": self.legacy_filename,
            "legacy_path": self.legacy_path,
            "message": self.message,
        }


@dataclass(slots=True)
class LegacyValidationCoverageBacklogEntry:
    family: str
    candidates: list[str]
    available_files: list[str]
    covered_files: list[str]
    missing_files: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "candidates": list(self.candidates),
            "available_files": list(self.available_files),
            "covered_files": list(self.covered_files),
            "missing_files": list(self.missing_files),
        }


@dataclass(slots=True)
class LegacyValidationCoverageMatrixResult:
    status: str
    mode: str
    fixture_path: str
    reference_dir: str
    reference_count: int = 0
    available_reference_count: int = 0
    covered_file_count: int = 0
    covered_rows: int = 0
    covered_periods: int = 0
    coverage: list[LegacyValidationCoverageEntry] = field(default_factory=list)
    gaps: list[LegacyValidationCoverageGap] = field(default_factory=list)
    backlog: list[LegacyValidationCoverageBacklogEntry] = field(default_factory=list)
    excluded_reference_dirs: list[str] = field(default_factory=list)
    issues: list[LegacyValidationCoverageIssue] = field(default_factory=list)
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "fixture_path": self.fixture_path,
            "reference_dir": self.reference_dir,
            "reference_count": self.reference_count,
            "available_reference_count": self.available_reference_count,
            "covered_file_count": self.covered_file_count,
            "covered_rows": self.covered_rows,
            "covered_periods": self.covered_periods,
            "coverage": [entry.to_dict() for entry in self.coverage],
            "gaps": [gap.to_dict() for gap in self.gaps],
            "backlog": [entry.to_dict() for entry in self.backlog],
            "excluded_reference_dirs": list(self.excluded_reference_dirs),
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def _status(issues: list[LegacyValidationCoverageIssue], gaps: list[LegacyValidationCoverageGap]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues or gaps:
        return "warning"
    return "ok"


def _legacy_source(path: Path) -> tuple[str, bool]:
    normalized_parts = tuple(part.lower() for part in path.parts)
    if "legacy_agrsich" in normalized_parts:
        return "legacy_agrsich", True
    return "unknown", False


def _periods_from_mapping(value: object) -> list[int]:
    if not isinstance(value, list) or not value:
        raise ValueError("legacy validation coverage target requires a non-empty periods list")
    periods = [int(period) for period in value]
    if len(periods) != len(set(periods)):
        raise ValueError("legacy validation coverage target periods must be unique")
    if periods != sorted(periods):
        raise ValueError("legacy validation coverage target periods must be sorted ascending")
    if periods != list(range(periods[0], periods[-1] + 1)):
        raise ValueError("legacy validation coverage target periods must be contiguous")
    return periods


def _coverage_entry_from_mapping(
    data: dict[str, object],
    *,
    fixture_base_path: Path,
) -> tuple[LegacyValidationCoverageEntry | None, LegacyValidationCoverageIssue | None]:
    legacy_path_data = str(data.get("legacy_path", "")).strip()
    if not legacy_path_data:
        raise ValueError("legacy validation coverage target requires field: legacy_path")
    legacy_path = Path(legacy_path_data)
    if not legacy_path.is_absolute():
        legacy_path = fixture_base_path / legacy_path
    resolved_legacy_path = legacy_path.resolve()
    legacy_source, is_legacy_reference = _legacy_source(resolved_legacy_path)
    if not is_legacy_reference:
        return None, LegacyValidationCoverageIssue(
            code="legacy_reference_excluded",
            severity="warning",
            message=(
                "legacy validation coverage excludes non-historical reference path: "
                f"{resolved_legacy_path}"
            ),
        )
    if not resolved_legacy_path.is_file():
        return None, LegacyValidationCoverageIssue(
            code="legacy_reference_missing",
            message=f"legacy validation coverage target legacy_path does not exist: {resolved_legacy_path}",
        )

    periods = _periods_from_mapping(data.get("periods"))
    return (
        LegacyValidationCoverageEntry(
            legacy_filename=resolved_legacy_path.name,
            legacy_path=str(resolved_legacy_path),
            legacy_source=legacy_source,
            is_legacy_reference=is_legacy_reference,
            subject_type=str(data.get("subject_type", "")).strip(),
            export_filename=str(data.get("export_filename", "")).strip(),
            level=str(data.get("level", "")).strip(),
            selector_kind=str(data.get("selector_kind", "")).strip(),
            selector_value=data.get("selector_value"),
            start_period=periods[0],
            end_period=periods[-1],
            period_count=len(periods),
            row_count=len(periods),
        ),
        None,
    )


def _available_legacy_references(reference_dir: Path) -> list[Path]:
    if not reference_dir.exists():
        return []
    return sorted(path.resolve() for path in reference_dir.iterdir() if path.is_file())


def _coverage_gaps(
    *,
    available_references: list[Path],
    covered_paths: set[Path],
) -> list[LegacyValidationCoverageGap]:
    gaps: list[LegacyValidationCoverageGap] = []
    for reference_path in available_references:
        if reference_path in covered_paths:
            continue
        gaps.append(
            LegacyValidationCoverageGap(
                code="legacy_reference_not_covered",
                legacy_filename=reference_path.name,
                legacy_path=str(reference_path),
                message=f"historical legacy reference is present but not covered by the fixture: {reference_path.name}",
            )
        )
    return gaps


def _matching_reference_names(names_by_upper: dict[str, str], candidate: str) -> list[str]:
    if "*" in candidate or "?" in candidate:
        return sorted(
            original_name
            for upper_name, original_name in names_by_upper.items()
            if fnmatch.fnmatchcase(upper_name, candidate.upper())
        )
    match = names_by_upper.get(candidate.upper())
    return [] if match is None else [match]


def _backlog_entries(
    available_references: list[Path],
    covered_paths: set[Path],
) -> list[LegacyValidationCoverageBacklogEntry]:
    available_names = {path.name.upper(): path.name for path in available_references}
    covered_names = {path.name.upper(): path.name for path in covered_paths}
    entries: list[LegacyValidationCoverageBacklogEntry] = []
    for family, candidates in LEGACY_AGRSICH_BACKLOG_CANDIDATES.items():
        available_files: list[str] = []
        covered_files: list[str] = []
        missing_files: list[str] = []
        for candidate in candidates:
            available_matches = _matching_reference_names(available_names, candidate)
            covered_matches = _matching_reference_names(covered_names, candidate)
            available_files.extend(available_matches)
            covered_files.extend(covered_matches)
            if not available_matches:
                missing_files.append(candidate)
        entries.append(
            LegacyValidationCoverageBacklogEntry(
                family=family,
                candidates=candidates,
                available_files=sorted(set(available_files)),
                covered_files=sorted(set(covered_files)),
                missing_files=missing_files,
            )
        )
    return entries


def build_legacy_validation_coverage_matrix(
    fixture_path: str | Path,
    *,
    reference_dir: str | Path | None = None,
) -> LegacyValidationCoverageMatrixResult:
    resolved_fixture_path = Path(fixture_path).expanduser().resolve()
    resolved_reference_dir = (
        Path(reference_dir).expanduser().resolve()
        if reference_dir is not None
        else (resolved_fixture_path.parent / "../references/legacy_agrsich").resolve()
    )
    issues: list[LegacyValidationCoverageIssue] = []
    coverage: list[LegacyValidationCoverageEntry] = []
    gaps: list[LegacyValidationCoverageGap] = []
    backlog: list[LegacyValidationCoverageBacklogEntry] = []
    try:
        with resolved_fixture_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("legacy validation coverage fixture must be a JSON object")
        targets = data.get("targets")
        if not isinstance(targets, list):
            raise ValueError("legacy validation coverage fixture requires list field: targets")
        for item in targets:
            if not isinstance(item, dict):
                raise ValueError("legacy validation coverage target must be an object")
            entry, issue = _coverage_entry_from_mapping(item, fixture_base_path=resolved_fixture_path.parent)
            if entry is not None:
                coverage.append(entry)
            if issue is not None:
                issues.append(issue)
        available_references = _available_legacy_references(resolved_reference_dir)
        covered_paths = {Path(entry.legacy_path).resolve() for entry in coverage}
        gaps = _coverage_gaps(
            available_references=available_references,
            covered_paths=covered_paths,
        )
        backlog = _backlog_entries(available_references, covered_paths)
        return LegacyValidationCoverageMatrixResult(
            status=_status(issues, gaps),
            mode="legacy_agrsich_coverage_matrix",
            fixture_path=str(resolved_fixture_path),
            reference_dir=str(resolved_reference_dir),
            reference_count=len(coverage),
            available_reference_count=len(available_references),
            covered_file_count=len({entry.legacy_path for entry in coverage}),
            covered_rows=sum(entry.row_count for entry in coverage),
            covered_periods=sum(entry.period_count for entry in coverage),
            coverage=coverage,
            gaps=gaps,
            backlog=backlog,
            excluded_reference_dirs=[str((resolved_fixture_path.parent / "../references/agrsich").resolve())],
            issues=issues,
        )
    except Exception as exc:
        return LegacyValidationCoverageMatrixResult(
            status="error",
            mode="legacy_agrsich_coverage_matrix",
            fixture_path=str(resolved_fixture_path),
            reference_dir=str(resolved_reference_dir),
            issues=[
                LegacyValidationCoverageIssue(
                    code="legacy_validation_coverage_failed",
                    message=str(exc),
                )
            ],
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize Legacy-Agrsich coverage for an existing validation fixture without writing artifacts.",
    )
    parser.add_argument("fixture_path", help="Path to a legacy validation fixture JSON file.")
    parser.add_argument(
        "--reference-dir",
        help="Optional directory containing historical Legacy-Agrsich reference files.",
    )
    args = parser.parse_args(argv)

    result = build_legacy_validation_coverage_matrix(args.fixture_path, reference_dir=args.reference_dir)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 2 if result.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
