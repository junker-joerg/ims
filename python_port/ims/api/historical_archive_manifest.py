from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence

from ims.model.agrsich_export import INSURER_HEADER, POLICYHOLDER_HEADER


CONTRACT_VERSION = "pr88-v1"
CORE_EXPORT_FILENAMES = (
    "IMSVU014.DAT",
    "IMSVUSK1.DAT",
    "IMSVNR01.DAT",
    "IMSVNR02.DAT",
    "IMSVNR03.DAT",
    "IMSVNR04.DAT",
    "IMSVNR05.DAT",
    "IMSVNR06.DAT",
    "IMSVNSK1.DAT",
    "IMSVNVK1.DAT",
    "IMSVNVK2.DAT",
    "IMSVNVK3.DAT",
    "IMSVUVK1.DAT",
    "IMSVUVK2.DAT",
    "IMSVUVK3.DAT",
)
DEFAULT_ARCHIVE_PATHS = (
    Path("incomming/IMS.DAT/VDEFMD5A.ZIP"),
    Path("incomming/IMS.DAT/VDEFMOD5.ZIP"),
    Path("incomming/IMS.DAT/VDEFMOD5/ZINS000.ZIP"),
    Path("incomming/IMS.DAT/VDEFMOD5/ZINS030.ZIP"),
    Path("incomming/IMS.DAT/WVEMOD1.ZIP"),
    Path("incomming/IMS.DAT/WVEMOD2.ZIP"),
    Path("incomming/IMS.DAT/WVEMOD3.ZIP"),
)

_CORE_EXPORTS = frozenset(CORE_EXPORT_FILENAMES)
_METADATA_TOKENS = ("REPORT", "REPOR", "PROTO", "LOG", "RUN", "PARAM", "DEF", "MOD")


@dataclass(frozen=True)
class HistoricalArchiveManifestIssue:
    code: str
    severity: str
    archive_path: str
    member_path: str | None
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "archive_path": self.archive_path,
            "member_path": self.member_path,
            "message": self.message,
        }


@dataclass(frozen=True)
class HistoricalArchiveMember:
    member_path: str
    filename: str
    sha256: str
    size_bytes: int
    compressed_size_bytes: int
    zip_timestamp: str
    subject_type: str
    expected_column_count: int
    header: str | None
    expected_header: str
    header_matches_expected: bool
    row_count: int
    valid_period_count: int
    period_start: int | None
    period_end: int | None
    periods_strictly_increasing: bool
    periods_contiguous: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "member_path": self.member_path,
            "filename": self.filename,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "compressed_size_bytes": self.compressed_size_bytes,
            "zip_timestamp": self.zip_timestamp,
            "subject_type": self.subject_type,
            "expected_column_count": self.expected_column_count,
            "header": self.header,
            "expected_header": self.expected_header,
            "header_matches_expected": self.header_matches_expected,
            "row_count": self.row_count,
            "valid_period_count": self.valid_period_count,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "periods_strictly_increasing": self.periods_strictly_increasing,
            "periods_contiguous": self.periods_contiguous,
        }


@dataclass(frozen=True)
class HistoricalArchiveMetadataCandidate:
    member_path: str
    filename: str
    sha256: str
    size_bytes: int
    compressed_size_bytes: int
    zip_timestamp: str
    matched_tokens: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "member_path": self.member_path,
            "filename": self.filename,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "compressed_size_bytes": self.compressed_size_bytes,
            "zip_timestamp": self.zip_timestamp,
            "matched_tokens": list(self.matched_tokens),
        }


@dataclass(frozen=True)
class HistoricalArchive:
    archive_path: str
    archive_filename: str
    readable: bool
    sha256: str | None
    size_bytes: int | None
    entry_count: int
    dat_entry_count: int
    core_member_count: int
    core_filenames: tuple[str, ...]
    missing_core_filenames: tuple[str, ...]
    core_members: tuple[HistoricalArchiveMember, ...]
    metadata_candidates: tuple[HistoricalArchiveMetadataCandidate, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "archive_path": self.archive_path,
            "archive_filename": self.archive_filename,
            "readable": self.readable,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "entry_count": self.entry_count,
            "dat_entry_count": self.dat_entry_count,
            "core_member_count": self.core_member_count,
            "core_filenames": list(self.core_filenames),
            "missing_core_filenames": list(self.missing_core_filenames),
            "core_members": [member.to_dict() for member in self.core_members],
            "metadata_candidates": [candidate.to_dict() for candidate in self.metadata_candidates],
        }


@dataclass(frozen=True)
class HistoricalArchiveManifestResult:
    status: str
    mode: str
    contract_version: str
    root: str
    archives: tuple[HistoricalArchive, ...]
    archive_count: int
    readable_archive_count: int
    entry_count: int
    dat_entry_count: int
    core_member_count: int
    unique_core_filenames: tuple[str, ...]
    archives_with_all_core_members: int
    metadata_candidate_count: int
    files_extracted: bool
    writes_enabled: bool
    execution_enabled: bool
    metadata_content_interpreted: bool
    historical_run_identity_claimed: bool
    historical_full_equality_claimed: bool
    production_release_approved: bool
    issues: tuple[HistoricalArchiveManifestIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": self.contract_version,
            "root": self.root,
            "archives": [archive.to_dict() for archive in self.archives],
            "archive_count": self.archive_count,
            "readable_archive_count": self.readable_archive_count,
            "entry_count": self.entry_count,
            "dat_entry_count": self.dat_entry_count,
            "core_member_count": self.core_member_count,
            "unique_core_filenames": list(self.unique_core_filenames),
            "archives_with_all_core_members": self.archives_with_all_core_members,
            "metadata_candidate_count": self.metadata_candidate_count,
            "files_extracted": self.files_extracted,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "metadata_content_interpreted": self.metadata_content_interpreted,
            "historical_run_identity_claimed": self.historical_run_identity_claimed,
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
            "production_release_approved": self.production_release_approved,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_historical_archive_manifest(
    *,
    root: Path | str = ".",
    archive_paths: Sequence[Path | str] | None = None,
) -> HistoricalArchiveManifestResult:
    resolved_root = Path(root).expanduser().resolve()
    requested_paths = tuple(DEFAULT_ARCHIVE_PATHS if archive_paths is None else archive_paths)
    resolved_paths = tuple(_resolve_against_root(resolved_root, path) for path in requested_paths)
    issues: list[HistoricalArchiveManifestIssue] = []
    archives = tuple(_inspect_archive(resolved_root, path, issues) for path in resolved_paths)
    readable_archives = tuple(archive for archive in archives if archive.readable)
    core_filenames = sorted(
        {filename for archive in readable_archives for filename in archive.core_filenames}
    )
    return HistoricalArchiveManifestResult(
        status=_status_from_issues(issues),
        mode="historical_archive_manifest",
        contract_version=CONTRACT_VERSION,
        root=str(resolved_root),
        archives=archives,
        archive_count=len(archives),
        readable_archive_count=len(readable_archives),
        entry_count=sum(archive.entry_count for archive in readable_archives),
        dat_entry_count=sum(archive.dat_entry_count for archive in readable_archives),
        core_member_count=sum(archive.core_member_count for archive in readable_archives),
        unique_core_filenames=tuple(core_filenames),
        archives_with_all_core_members=sum(
            archive.core_member_count == len(CORE_EXPORT_FILENAMES) for archive in readable_archives
        ),
        metadata_candidate_count=sum(
            len(archive.metadata_candidates) for archive in readable_archives
        ),
        files_extracted=False,
        writes_enabled=False,
        execution_enabled=False,
        metadata_content_interpreted=False,
        historical_run_identity_claimed=False,
        historical_full_equality_claimed=False,
        production_release_approved=False,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_historical_archive_manifest(root=args.root, archive_paths=args.archive)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _inspect_archive(
    root: Path,
    archive_path: Path,
    issues: list[HistoricalArchiveManifestIssue],
) -> HistoricalArchive:
    display_path = _display_path(root, archive_path)
    if not archive_path.is_file():
        issues.append(
            HistoricalArchiveManifestIssue(
                code="archive_missing",
                severity="error",
                archive_path=display_path,
                member_path=None,
                message=f"historical archive is missing or not a file: {display_path}",
            )
        )
        return _unreadable_archive(display_path, archive_path.name)

    archive_hash = _sha256_path(archive_path)
    try:
        with zipfile.ZipFile(archive_path) as archive:
            infos = tuple(info for info in archive.infolist() if not info.is_dir())
            core_members: list[HistoricalArchiveMember] = []
            metadata_candidates: list[HistoricalArchiveMetadataCandidate] = []
            seen_core_filenames: set[str] = set()
            for info in infos:
                member_path = info.filename.replace("\\", "/")
                filename = PurePosixPath(member_path).name.upper()
                if filename not in _CORE_EXPORTS and not _metadata_tokens(filename):
                    continue
                try:
                    data = archive.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile) as error:
                    issues.append(
                        HistoricalArchiveManifestIssue(
                            code="archive_member_read_error",
                            severity="error",
                            archive_path=display_path,
                            member_path=member_path,
                            message=f"archive member could not be read: {error}",
                        )
                    )
                    continue
                if filename in _CORE_EXPORTS:
                    if filename in seen_core_filenames:
                        issues.append(
                            HistoricalArchiveManifestIssue(
                                code="core_member_duplicate",
                                severity="error",
                                archive_path=display_path,
                                member_path=member_path,
                                message=f"core export basename occurs more than once: {filename}",
                            )
                        )
                    seen_core_filenames.add(filename)
                    core_members.append(
                        _inspect_core_member(display_path, info, data, filename, issues)
                    )
                tokens = _metadata_tokens(filename)
                if tokens:
                    metadata_candidates.append(
                        HistoricalArchiveMetadataCandidate(
                            member_path=member_path,
                            filename=filename,
                            sha256=_sha256_bytes(data),
                            size_bytes=info.file_size,
                            compressed_size_bytes=info.compress_size,
                            zip_timestamp=_zip_timestamp(info),
                            matched_tokens=tokens,
                        )
                    )
    except (OSError, zipfile.BadZipFile) as error:
        issues.append(
            HistoricalArchiveManifestIssue(
                code="archive_invalid_zip",
                severity="error",
                archive_path=display_path,
                member_path=None,
                message=f"historical archive is not a readable ZIP file: {error}",
            )
        )
        return HistoricalArchive(
            archive_path=display_path,
            archive_filename=archive_path.name,
            readable=False,
            sha256=archive_hash,
            size_bytes=archive_path.stat().st_size,
            entry_count=0,
            dat_entry_count=0,
            core_member_count=0,
            core_filenames=(),
            missing_core_filenames=CORE_EXPORT_FILENAMES,
            core_members=(),
            metadata_candidates=(),
        )

    core_members.sort(key=lambda member: (member.filename, member.member_path))
    metadata_candidates.sort(key=lambda candidate: candidate.member_path)
    core_names = tuple(sorted({member.filename for member in core_members}))
    return HistoricalArchive(
        archive_path=display_path,
        archive_filename=archive_path.name,
        readable=True,
        sha256=archive_hash,
        size_bytes=archive_path.stat().st_size,
        entry_count=len(infos),
        dat_entry_count=sum(PurePosixPath(info.filename.replace("\\", "/")).suffix.upper() == ".DAT" for info in infos),
        core_member_count=len(core_names),
        core_filenames=core_names,
        missing_core_filenames=tuple(name for name in CORE_EXPORT_FILENAMES if name not in core_names),
        core_members=tuple(core_members),
        metadata_candidates=tuple(metadata_candidates),
    )


def _inspect_core_member(
    archive_path: str,
    info: zipfile.ZipInfo,
    data: bytes,
    filename: str,
    issues: list[HistoricalArchiveManifestIssue],
) -> HistoricalArchiveMember:
    member_path = info.filename.replace("\\", "/")
    subject_type, expected_columns, expected_header = _core_export_contract(filename)
    header: str | None = None
    row_count = 0
    periods: list[int] = []
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        issues.append(
            HistoricalArchiveManifestIssue(
                code="core_member_decode_error",
                severity="error",
                archive_path=archive_path,
                member_path=member_path,
                message=f"core export is not UTF-8/ASCII compatible: {error}",
            )
        )
    else:
        lines = [line for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n") if line.strip()]
        if not lines:
            issues.append(
                HistoricalArchiveManifestIssue(
                    code="core_member_empty",
                    severity="error",
                    archive_path=archive_path,
                    member_path=member_path,
                    message="core export is empty",
                )
            )
        else:
            header = lines[0]
            row_count = len(lines) - 1
            if _normalize_whitespace(header) != _normalize_whitespace(expected_header):
                issues.append(
                    HistoricalArchiveManifestIssue(
                        code="core_member_header_mismatch",
                        severity="error",
                        archive_path=archive_path,
                        member_path=member_path,
                        message=f"core export header does not match {subject_type} contract",
                    )
                )
            for row_number, line in enumerate(lines[1:], start=2):
                parts = line.split()
                if len(parts) != expected_columns:
                    issues.append(
                        HistoricalArchiveManifestIssue(
                            code="core_member_column_count",
                            severity="error",
                            archive_path=archive_path,
                            member_path=member_path,
                            message=(
                                f"row {row_number} has {len(parts)} columns; "
                                f"expected {expected_columns}"
                            ),
                        )
                    )
                    continue
                try:
                    period = int(parts[0])
                    for value in parts[1:]:
                        float(value)
                except ValueError:
                    issues.append(
                        HistoricalArchiveManifestIssue(
                            code="core_member_non_numeric_row",
                            severity="error",
                            archive_path=archive_path,
                            member_path=member_path,
                            message=f"row {row_number} contains a non-numeric value",
                        )
                    )
                    continue
                periods.append(period)

    strictly_increasing = all(left < right for left, right in zip(periods, periods[1:]))
    contiguous = bool(periods) and periods == list(range(periods[0], periods[-1] + 1))
    if periods and not strictly_increasing:
        issues.append(
            HistoricalArchiveManifestIssue(
                code="core_member_period_order",
                severity="error",
                archive_path=archive_path,
                member_path=member_path,
                message="core export periods are not strictly increasing",
            )
        )
    if periods and strictly_increasing and not contiguous:
        issues.append(
            HistoricalArchiveManifestIssue(
                code="core_member_period_gap",
                severity="error",
                archive_path=archive_path,
                member_path=member_path,
                message="core export period window is not contiguous",
            )
        )

    return HistoricalArchiveMember(
        member_path=member_path,
        filename=filename,
        sha256=_sha256_bytes(data),
        size_bytes=info.file_size,
        compressed_size_bytes=info.compress_size,
        zip_timestamp=_zip_timestamp(info),
        subject_type=subject_type,
        expected_column_count=expected_columns,
        header=header,
        expected_header=expected_header,
        header_matches_expected=(
            header is not None
            and _normalize_whitespace(header) == _normalize_whitespace(expected_header)
        ),
        row_count=row_count,
        valid_period_count=len(periods),
        period_start=periods[0] if periods else None,
        period_end=periods[-1] if periods else None,
        periods_strictly_increasing=strictly_increasing,
        periods_contiguous=contiguous,
    )


def _core_export_contract(filename: str) -> tuple[str, int, str]:
    if filename.startswith("IMSVNR") or filename == "IMSVNSK1.DAT" or filename.startswith("IMSVNVK"):
        return "policyholder", 12, POLICYHOLDER_HEADER
    return "insurer", 13, INSURER_HEADER


def _metadata_tokens(filename: str) -> tuple[str, ...]:
    return tuple(token for token in _METADATA_TOKENS if token in filename)


def _unreadable_archive(display_path: str, filename: str) -> HistoricalArchive:
    return HistoricalArchive(
        archive_path=display_path,
        archive_filename=filename,
        readable=False,
        sha256=None,
        size_bytes=None,
        entry_count=0,
        dat_entry_count=0,
        core_member_count=0,
        core_filenames=(),
        missing_core_filenames=CORE_EXPORT_FILENAMES,
        core_members=(),
        metadata_candidates=(),
    )


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _resolve_against_root(root: Path, path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _zip_timestamp(info: zipfile.ZipInfo) -> str:
    year, month, day, hour, minute, second = info.date_time
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def _status_from_issues(issues: Sequence[HistoricalArchiveManifestIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_archive_manifest",
        description="Erfasst historische ZIP-Archive lesend, ohne Dateien zu extrahieren oder zu schreiben.",
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Repo-Wurzel fuer relative Archivpfade.")
    parser.add_argument(
        "--archive",
        action="append",
        type=Path,
        help="Expliziter Archivpfad; ohne Angabe werden die sieben bekannten Archive gelesen.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
