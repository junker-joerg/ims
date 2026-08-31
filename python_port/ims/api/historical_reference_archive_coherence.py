from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence

from ims.api.historical_archive_manifest import DEFAULT_ARCHIVE_PATHS


CONTRACT_VERSION = "pr89-v1"
CLASSIFICATIONS = (
    "exact_archive_member",
    "exact_window_slice",
    "same_name_divergent",
    "unresolved",
)


@dataclass(frozen=True)
class HistoricalReferenceSpec:
    reference_filename: str
    archive_filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str
    period_start: int
    period_end: int

    @property
    def expected_row_count(self) -> int:
        return self.period_end - self.period_start + 1


REFERENCE_SPECS = (
    HistoricalReferenceSpec("VU14L1.DAT", "IMSVU014.DAT", "insurer", "I", "entity", 14, 1, 100),
    HistoricalReferenceSpec("VUSK1L1.DAT", "IMSVUSK1.DAT", "insurer", "IV", "all", "SK1", 401, 500),
    HistoricalReferenceSpec("VUSK1L2.DAT", "IMSVUSK1.DAT", "insurer", "IV", "all", "SK1", 301, 400),
    HistoricalReferenceSpec("VUSK1L3.DAT", "IMSVUSK1.DAT", "insurer", "IV", "all", "SK1", 201, 300),
    HistoricalReferenceSpec("VUSK1L4.DAT", "IMSVUSK1.DAT", "insurer", "IV", "all", "SK1", 101, 200),
    HistoricalReferenceSpec("VUSK1L5.DAT", "IMSVUSK1.DAT", "insurer", "IV", "all", "SK1", 1, 100),
    HistoricalReferenceSpec("IMSVNSK1.DAT", "IMSVNSK1.DAT", "policyholder", "IV", "all", "SK1", 1, 500),
    HistoricalReferenceSpec("IMSVNR01.DAT", "IMSVNR01.DAT", "policyholder", "II", "rule", 1, 1, 300),
    HistoricalReferenceSpec("IMSVNR02.DAT", "IMSVNR02.DAT", "policyholder", "II", "rule", 2, 1, 300),
    HistoricalReferenceSpec("IMSVNR03.DAT", "IMSVNR03.DAT", "policyholder", "II", "rule", 3, 1, 500),
    HistoricalReferenceSpec("IMSVNR04.DAT", "IMSVNR04.DAT", "policyholder", "II", "rule", 4, 1, 500),
    HistoricalReferenceSpec("IMSVNR05.DAT", "IMSVNR05.DAT", "policyholder", "II", "rule", 5, 1, 500),
    HistoricalReferenceSpec("IMSVNR06.DAT", "IMSVNR06.DAT", "policyholder", "II", "rule", 6, 1, 500),
    HistoricalReferenceSpec("IMSVNVK1.DAT", "IMSVNVK1.DAT", "policyholder", "III", "rule_class", 1, 1, 500),
    HistoricalReferenceSpec("IMSVNVK2.DAT", "IMSVNVK2.DAT", "policyholder", "III", "rule_class", 2, 1, 500),
    HistoricalReferenceSpec("IMSVNVK3.DAT", "IMSVNVK3.DAT", "policyholder", "III", "rule_class", 3, 1, 500),
    HistoricalReferenceSpec("IMSVUVK1.DAT", "IMSVUVK1.DAT", "insurer", "III", "rule_class", 1, 1, 500),
    HistoricalReferenceSpec("IMSVUVK2.DAT", "IMSVUVK2.DAT", "insurer", "III", "rule_class", 2, 1, 500),
    HistoricalReferenceSpec("IMSVUVK3.DAT", "IMSVUVK3.DAT", "insurer", "III", "rule_class", 3, 1, 500),
)


@dataclass(frozen=True)
class HistoricalReferenceArchiveIssue:
    code: str
    severity: str
    path: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "path": self.path,
            "message": self.message,
        }


@dataclass(frozen=True)
class HistoricalReferenceArchiveCandidate:
    archive_path: str
    archive_sha256: str
    member_path: str
    member_sha256: str
    member_row_count: int | None
    member_period_start: int | None
    member_period_end: int | None
    comparison_scope: str
    compared_row_count: int
    byte_matches: bool
    token_normalized_matches: bool
    matching_basis: str
    classification: str

    def to_dict(self) -> dict[str, object]:
        return {
            "archive_path": self.archive_path,
            "archive_sha256": self.archive_sha256,
            "member_path": self.member_path,
            "member_sha256": self.member_sha256,
            "member_row_count": self.member_row_count,
            "member_period_start": self.member_period_start,
            "member_period_end": self.member_period_end,
            "comparison_scope": self.comparison_scope,
            "compared_row_count": self.compared_row_count,
            "byte_matches": self.byte_matches,
            "token_normalized_matches": self.token_normalized_matches,
            "matching_basis": self.matching_basis,
            "classification": self.classification,
        }


@dataclass(frozen=True)
class HistoricalReferenceArchiveTarget:
    reference_path: str
    reference_filename: str
    reference_sha256: str | None
    token_normalized_sha256: str | None
    archive_filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str
    period_start: int
    period_end: int
    row_count: int | None
    classification: str
    selected_archive_path: str | None
    selected_member_path: str | None
    selected_matching_basis: str | None
    candidates: tuple[HistoricalReferenceArchiveCandidate, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "reference_path": self.reference_path,
            "reference_filename": self.reference_filename,
            "reference_sha256": self.reference_sha256,
            "token_normalized_sha256": self.token_normalized_sha256,
            "archive_filename": self.archive_filename,
            "subject_type": self.subject_type,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "row_count": self.row_count,
            "classification": self.classification,
            "selected_archive_path": self.selected_archive_path,
            "selected_member_path": self.selected_member_path,
            "selected_matching_basis": self.selected_matching_basis,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }


@dataclass(frozen=True)
class HistoricalReferenceArchiveCoherenceResult:
    status: str
    mode: str
    contract_version: str
    root: str
    reference_dir: str
    target_count: int
    candidate_count: int
    classification_counts: dict[str, int]
    targets: tuple[HistoricalReferenceArchiveTarget, ...]
    files_extracted: bool
    writes_enabled: bool
    execution_enabled: bool
    simulation_performed: bool
    archive_family_coherence_claimed: bool
    historical_run_identity_claimed: bool
    historical_full_equality_claimed: bool
    production_release_approved: bool
    issues: tuple[HistoricalReferenceArchiveIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": self.contract_version,
            "root": self.root,
            "reference_dir": self.reference_dir,
            "target_count": self.target_count,
            "candidate_count": self.candidate_count,
            "classification_counts": self.classification_counts,
            "targets": [target.to_dict() for target in self.targets],
            "files_extracted": self.files_extracted,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "simulation_performed": self.simulation_performed,
            "archive_family_coherence_claimed": self.archive_family_coherence_claimed,
            "historical_run_identity_claimed": self.historical_run_identity_claimed,
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
            "production_release_approved": self.production_release_approved,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class _ParsedTable:
    data: bytes
    nonblank_lines: tuple[bytes, ...]
    periods: tuple[int, ...]

    @property
    def row_count(self) -> int:
        return len(self.periods)

    @property
    def period_start(self) -> int | None:
        return self.periods[0] if self.periods else None

    @property
    def period_end(self) -> int | None:
        return self.periods[-1] if self.periods else None


@dataclass(frozen=True)
class _ArchiveMemberData:
    archive_path: str
    archive_sha256: str
    member_path: str
    filename: str
    member_sha256: str
    table: _ParsedTable | None


def build_historical_reference_archive_coherence(
    *,
    root: Path | str = ".",
    reference_dir: Path | str = Path("tests/references/legacy_agrsich"),
    archive_paths: Sequence[Path | str] | None = None,
    reference_specs: Sequence[HistoricalReferenceSpec] = REFERENCE_SPECS,
) -> HistoricalReferenceArchiveCoherenceResult:
    resolved_root = Path(root).expanduser().resolve()
    resolved_reference_dir = _resolve_against_root(resolved_root, reference_dir)
    requested_archives = tuple(DEFAULT_ARCHIVE_PATHS if archive_paths is None else archive_paths)
    resolved_archives = tuple(_resolve_against_root(resolved_root, path) for path in requested_archives)
    issues: list[HistoricalReferenceArchiveIssue] = []
    archive_members = _load_archive_members(
        resolved_root,
        resolved_archives,
        {spec.archive_filename.upper() for spec in reference_specs},
        issues,
    )
    targets = tuple(
        _compare_reference(
            resolved_root,
            resolved_reference_dir,
            spec,
            archive_members,
            issues,
        )
        for spec in reference_specs
    )
    counts = {
        classification: sum(target.classification == classification for target in targets)
        for classification in CLASSIFICATIONS
    }
    return HistoricalReferenceArchiveCoherenceResult(
        status=_status_from_issues(issues),
        mode="historical_reference_archive_coherence",
        contract_version=CONTRACT_VERSION,
        root=str(resolved_root),
        reference_dir=_display_path(resolved_root, resolved_reference_dir),
        target_count=len(targets),
        candidate_count=sum(len(target.candidates) for target in targets),
        classification_counts=counts,
        targets=targets,
        files_extracted=False,
        writes_enabled=False,
        execution_enabled=False,
        simulation_performed=False,
        archive_family_coherence_claimed=False,
        historical_run_identity_claimed=False,
        historical_full_equality_claimed=False,
        production_release_approved=False,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_historical_reference_archive_coherence(
        root=args.root,
        reference_dir=args.reference_dir,
        archive_paths=args.archive,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _compare_reference(
    root: Path,
    reference_dir: Path,
    spec: HistoricalReferenceSpec,
    archive_members: Sequence[_ArchiveMemberData],
    issues: list[HistoricalReferenceArchiveIssue],
) -> HistoricalReferenceArchiveTarget:
    reference_path = reference_dir / spec.reference_filename
    display_path = _display_path(root, reference_path)
    table = _load_reference_table(reference_path, display_path, spec, issues)
    matching_members = tuple(
        member for member in archive_members if member.filename == spec.archive_filename.upper()
    )
    candidates = tuple(
        _compare_candidate(spec, table, member)
        for member in matching_members
        if table is not None
    )
    selected = min(candidates, key=_candidate_rank) if candidates else None
    classification = selected.classification if selected is not None else "unresolved"
    return HistoricalReferenceArchiveTarget(
        reference_path=display_path,
        reference_filename=spec.reference_filename,
        reference_sha256=_sha256_bytes(table.data) if table is not None else None,
        token_normalized_sha256=_token_normalized_sha256(table.data) if table is not None else None,
        archive_filename=spec.archive_filename,
        subject_type=spec.subject_type,
        level=spec.level,
        selector_kind=spec.selector_kind,
        selector_value=spec.selector_value,
        period_start=spec.period_start,
        period_end=spec.period_end,
        row_count=table.row_count if table is not None else None,
        classification=classification,
        selected_archive_path=selected.archive_path if selected is not None else None,
        selected_member_path=selected.member_path if selected is not None else None,
        selected_matching_basis=selected.matching_basis if selected is not None else None,
        candidates=candidates,
    )


def _compare_candidate(
    spec: HistoricalReferenceSpec,
    reference: _ParsedTable,
    member: _ArchiveMemberData,
) -> HistoricalReferenceArchiveCandidate:
    member_table = member.table
    expected_periods = tuple(range(spec.period_start, spec.period_end + 1))
    comparison_scope = "unavailable_window"
    compared_data: bytes | None = None
    compared_rows = 0
    if member_table is not None and member_table.periods == expected_periods:
        comparison_scope = "full_member"
        compared_data = member_table.data
        compared_rows = member_table.row_count
    elif member_table is not None and all(period in member_table.periods for period in expected_periods):
        comparison_scope = "period_window"
        compared_data = _window_bytes(member_table, expected_periods)
        compared_rows = len(expected_periods)

    byte_matches = compared_data == reference.data if compared_data is not None else False
    token_matches = (
        _normalized_tokens(compared_data) == _normalized_tokens(reference.data)
        if compared_data is not None
        else False
    )
    if byte_matches:
        basis = "byte_exact"
    elif token_matches:
        basis = "token_normalized"
    else:
        basis = "none"
    if (byte_matches or token_matches) and comparison_scope == "full_member":
        classification = "exact_archive_member"
    elif (byte_matches or token_matches) and comparison_scope == "period_window":
        classification = "exact_window_slice"
    else:
        classification = "same_name_divergent"
    return HistoricalReferenceArchiveCandidate(
        archive_path=member.archive_path,
        archive_sha256=member.archive_sha256,
        member_path=member.member_path,
        member_sha256=member.member_sha256,
        member_row_count=member_table.row_count if member_table is not None else None,
        member_period_start=member_table.period_start if member_table is not None else None,
        member_period_end=member_table.period_end if member_table is not None else None,
        comparison_scope=comparison_scope,
        compared_row_count=compared_rows,
        byte_matches=byte_matches,
        token_normalized_matches=token_matches,
        matching_basis=basis,
        classification=classification,
    )


def _load_reference_table(
    path: Path,
    display_path: str,
    spec: HistoricalReferenceSpec,
    issues: list[HistoricalReferenceArchiveIssue],
) -> _ParsedTable | None:
    if not path.is_file():
        issues.append(
            HistoricalReferenceArchiveIssue(
                code="reference_missing",
                severity="error",
                path=display_path,
                message=f"versioned historical reference is missing: {display_path}",
            )
        )
        return None
    try:
        table = _parse_table(path.read_bytes())
    except ValueError as error:
        issues.append(
            HistoricalReferenceArchiveIssue(
                code="reference_invalid",
                severity="error",
                path=display_path,
                message=f"versioned historical reference is invalid: {error}",
            )
        )
        return None
    expected_periods = tuple(range(spec.period_start, spec.period_end + 1))
    if table.periods != expected_periods:
        issues.append(
            HistoricalReferenceArchiveIssue(
                code="reference_period_window_mismatch",
                severity="error",
                path=display_path,
                message=(
                    f"reference periods do not match declared window "
                    f"{spec.period_start}-{spec.period_end}"
                ),
            )
        )
        return None
    return table


def _load_archive_members(
    root: Path,
    archive_paths: Sequence[Path],
    target_filenames: set[str],
    issues: list[HistoricalReferenceArchiveIssue],
) -> tuple[_ArchiveMemberData, ...]:
    members: list[_ArchiveMemberData] = []
    for archive_path in archive_paths:
        display_path = _display_path(root, archive_path)
        if not archive_path.is_file():
            issues.append(
                HistoricalReferenceArchiveIssue(
                    code="archive_missing",
                    severity="error",
                    path=display_path,
                    message=f"historical archive is missing or not a file: {display_path}",
                )
            )
            continue
        archive_hash = _sha256_path(archive_path)
        try:
            with zipfile.ZipFile(archive_path) as archive:
                seen: set[str] = set()
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    member_path = info.filename.replace("\\", "/")
                    filename = PurePosixPath(member_path).name.upper()
                    if filename not in target_filenames:
                        continue
                    if filename in seen:
                        issues.append(
                            HistoricalReferenceArchiveIssue(
                                code="archive_member_duplicate",
                                severity="error",
                                path=f"{display_path}/{member_path}",
                                message=f"archive core basename occurs more than once: {filename}",
                            )
                        )
                    seen.add(filename)
                    data = archive.read(info)
                    try:
                        table = _parse_table(data)
                    except ValueError as error:
                        table = None
                        issues.append(
                            HistoricalReferenceArchiveIssue(
                                code="archive_member_invalid",
                                severity="error",
                                path=f"{display_path}/{member_path}",
                                message=f"archive member is not a valid table: {error}",
                            )
                        )
                    members.append(
                        _ArchiveMemberData(
                            archive_path=display_path,
                            archive_sha256=archive_hash,
                            member_path=member_path,
                            filename=filename,
                            member_sha256=_sha256_bytes(data),
                            table=table,
                        )
                    )
        except (OSError, RuntimeError, zipfile.BadZipFile) as error:
            issues.append(
                HistoricalReferenceArchiveIssue(
                    code="archive_invalid_zip",
                    severity="error",
                    path=display_path,
                    message=f"historical archive is not a readable ZIP file: {error}",
                )
            )
    return tuple(members)


def _parse_table(data: bytes) -> _ParsedTable:
    try:
        data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"table is not UTF-8/ASCII compatible: {error}") from error
    lines = tuple(line for line in data.splitlines(keepends=True) if line.strip())
    if not lines:
        raise ValueError("table is empty")
    periods: list[int] = []
    for row_number, line in enumerate(lines[1:], start=2):
        parts = line.split()
        if not parts:
            continue
        try:
            periods.append(int(parts[0]))
        except ValueError as error:
            raise ValueError(f"row {row_number} has no integer period") from error
    if not periods:
        raise ValueError("table has no data rows")
    if len(set(periods)) != len(periods):
        raise ValueError("table contains duplicate periods")
    if any(left >= right for left, right in zip(periods, periods[1:])):
        raise ValueError("table periods are not strictly increasing")
    return _ParsedTable(data=data, nonblank_lines=lines, periods=tuple(periods))


def _window_bytes(table: _ParsedTable, periods: Sequence[int]) -> bytes:
    wanted = set(periods)
    rows = [line for line in table.nonblank_lines[1:] if int(line.split()[0]) in wanted]
    return b"".join((table.nonblank_lines[0], *rows))


def _candidate_rank(candidate: HistoricalReferenceArchiveCandidate) -> tuple[int, int, str, str]:
    classification_rank = {
        "exact_archive_member": 0,
        "exact_window_slice": 1,
        "same_name_divergent": 2,
    }
    basis_rank = {"byte_exact": 0, "token_normalized": 1, "none": 2}
    return (
        classification_rank[candidate.classification],
        basis_rank[candidate.matching_basis],
        candidate.archive_path,
        candidate.member_path,
    )


def _normalized_tokens(data: bytes) -> tuple[str, ...]:
    return tuple(data.decode("utf-8-sig").split())


def _token_normalized_sha256(data: bytes) -> str:
    normalized = "\0".join(_normalized_tokens(data)).encode("utf-8")
    return _sha256_bytes(normalized)


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _resolve_against_root(root: Path, path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _status_from_issues(issues: Sequence[HistoricalReferenceArchiveIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_reference_archive_coherence",
        description="Vergleicht versionierte Referenzen lesend mit historischen ZIP-Eintraegen.",
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Repo-Wurzel.")
    parser.add_argument(
        "--reference-dir",
        type=Path,
        default=Path("tests/references/legacy_agrsich"),
        help="Verzeichnis der versionierten historischen Referenzen.",
    )
    parser.add_argument(
        "--archive",
        action="append",
        type=Path,
        help="Expliziter ZIP-Pfad; ohne Angabe werden die sieben bekannten Archive gelesen.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
