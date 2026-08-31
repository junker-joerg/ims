from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Sequence

from ims.api.historical_archive_manifest import DEFAULT_ARCHIVE_PATHS


CONTRACT_VERSION = "pr90-v1"
RUN_REPORT_FILENAME = "IMSREPOR.DAT"

_EXPORT_PATTERN = re.compile(r"^IMSV[A-Z0-9]+\.DAT$")
_VERSION_PATTERN = re.compile(
    r"^IMS Version (?P<platform>\S+) (?P<version>v\S+) .*?compiled on\s+(?P<compiled_at>.+?)\s*$"
)
_SEED_PATTERN = re.compile(r"^Seed\s*:\s*(\d+)\s*$")
_INSURER_MEMORY_PATTERN = re.compile(r"^Speicher fuer (\d+) VUs:\s*(\d+) Bytes\s*$")
_POLICYHOLDER_MEMORY_PATTERN = re.compile(r"^Speicher fuer (\d+) VNs:\s*(\d+) Bytes\s*$")
_INITIAL_BV_PATTERN = re.compile(r"^Myinitbv:\[(\d+),(\d+)\]\s*$")
_RESET_BV_PATTERN = re.compile(r"^Newinibv:\[(\d+),(\d+)\]\s*$")
_FRMDINF_PATTERN = re.compile(
    r"^Frmdinf\((\d+),(\d+)\)\.akvu\((\d+)\),akvn\((\d+)\)\s*$"
)
_AGRSICH_PATTERN = re.compile(r"^Agrsich\((\d+),(\d+)\)\s*$")
_INSURER_RELEASE_PATTERN = re.compile(r"^\d+ Bytes von VU\[(\d+)\] freigegeben\s*$")
_POLICYHOLDER_RELEASE_PATTERN = re.compile(r"^\d+ Bytes von VN\[(\d+)\] freigegeben\s*$")
_ALLOCATED_MEMORY_PATTERN = re.compile(r"^Bisher allocierter Speicher:\s*(\d+) Bytes\s*$")


@dataclass(frozen=True)
class HistoricalArchiveRunMetadataIssue:
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
class HistoricalArchiveSupportFile:
    member_path: str
    filename: str
    category: str
    sha256: str
    size_bytes: int
    compressed_size_bytes: int
    zip_timestamp: str
    content_interpreted: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "member_path": self.member_path,
            "filename": self.filename,
            "category": self.category,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "compressed_size_bytes": self.compressed_size_bytes,
            "zip_timestamp": self.zip_timestamp,
            "content_interpreted": self.content_interpreted,
        }


@dataclass(frozen=True)
class HistoricalReportSequence:
    sequence_index: int
    call_count: int
    period_start: int
    period_end: int
    periods_contiguous: bool
    frmdinf_first_argument_values: tuple[int, ...]
    active_insurer_counts: tuple[int, ...]
    active_policyholder_counts: tuple[int, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "sequence_index": self.sequence_index,
            "call_count": self.call_count,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "periods_contiguous": self.periods_contiguous,
            "frmdinf_first_argument_values": list(self.frmdinf_first_argument_values),
            "active_insurer_counts": list(self.active_insurer_counts),
            "active_policyholder_counts": list(self.active_policyholder_counts),
        }


@dataclass(frozen=True)
class HistoricalRunReport:
    version_line: str | None
    platform: str | None
    version: str | None
    compiled_at_text: str | None
    seed: int | None
    allocated_insurer_count: int | None
    allocated_insurer_bytes: int | None
    allocated_policyholder_count: int | None
    allocated_policyholder_bytes: int | None
    initial_bv_values: tuple[int, int] | None
    reset_bv_values: tuple[tuple[int, int], ...]
    line_count: int
    frmdinf_call_count: int
    agrsich_call_count: int
    agrsich_first_argument_values: tuple[int, ...]
    sequences: tuple[HistoricalReportSequence, ...]
    insurer_release_count: int
    policyholder_release_count: int
    final_allocated_bytes: int | None
    end_marker_present: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "version_line": self.version_line,
            "platform": self.platform,
            "version": self.version,
            "compiled_at_text": self.compiled_at_text,
            "seed": self.seed,
            "allocated_insurer_count": self.allocated_insurer_count,
            "allocated_insurer_bytes": self.allocated_insurer_bytes,
            "allocated_policyholder_count": self.allocated_policyholder_count,
            "allocated_policyholder_bytes": self.allocated_policyholder_bytes,
            "initial_bv_values": (
                list(self.initial_bv_values) if self.initial_bv_values is not None else None
            ),
            "reset_bv_values": [list(values) for values in self.reset_bv_values],
            "line_count": self.line_count,
            "frmdinf_call_count": self.frmdinf_call_count,
            "agrsich_call_count": self.agrsich_call_count,
            "agrsich_first_argument_values": list(self.agrsich_first_argument_values),
            "sequences": [sequence.to_dict() for sequence in self.sequences],
            "insurer_release_count": self.insurer_release_count,
            "policyholder_release_count": self.policyholder_release_count,
            "final_allocated_bytes": self.final_allocated_bytes,
            "end_marker_present": self.end_marker_present,
        }


@dataclass(frozen=True)
class HistoricalArchiveRunMetadata:
    archive_path: str
    archive_filename: str
    readable: bool
    sha256: str | None
    size_bytes: int | None
    entry_count: int
    output_entry_count: int
    support_entry_count: int
    metadata_status: str
    run_report_member_path: str | None
    run_report: HistoricalRunReport | None
    support_files: tuple[HistoricalArchiveSupportFile, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "archive_path": self.archive_path,
            "archive_filename": self.archive_filename,
            "readable": self.readable,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "entry_count": self.entry_count,
            "output_entry_count": self.output_entry_count,
            "support_entry_count": self.support_entry_count,
            "metadata_status": self.metadata_status,
            "run_report_member_path": self.run_report_member_path,
            "run_report": self.run_report.to_dict() if self.run_report is not None else None,
            "support_files": [support_file.to_dict() for support_file in self.support_files],
        }


@dataclass(frozen=True)
class HistoricalArchiveRunMetadataResult:
    status: str
    mode: str
    contract_version: str
    root: str
    archive_count: int
    readable_archive_count: int
    archives_with_run_report: int
    archives_without_run_report: int
    run_report_count: int
    support_file_count: int
    model_definition_parameter_file_count: int
    archives: tuple[HistoricalArchiveRunMetadata, ...]
    files_extracted: bool
    writes_enabled: bool
    execution_enabled: bool
    simulation_performed: bool
    metadata_content_interpreted: bool
    missing_metadata_treated_as_default: bool
    cross_archive_metadata_transfer_performed: bool
    seed_transferred_between_archives: bool
    archive_family_coherence_claimed: bool
    historical_run_identity_claimed: bool
    historical_full_equality_claimed: bool
    production_release_approved: bool
    issues: tuple[HistoricalArchiveRunMetadataIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": self.contract_version,
            "root": self.root,
            "archive_count": self.archive_count,
            "readable_archive_count": self.readable_archive_count,
            "archives_with_run_report": self.archives_with_run_report,
            "archives_without_run_report": self.archives_without_run_report,
            "run_report_count": self.run_report_count,
            "support_file_count": self.support_file_count,
            "model_definition_parameter_file_count": self.model_definition_parameter_file_count,
            "archives": [archive.to_dict() for archive in self.archives],
            "files_extracted": self.files_extracted,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "simulation_performed": self.simulation_performed,
            "metadata_content_interpreted": self.metadata_content_interpreted,
            "missing_metadata_treated_as_default": self.missing_metadata_treated_as_default,
            "cross_archive_metadata_transfer_performed": (
                self.cross_archive_metadata_transfer_performed
            ),
            "seed_transferred_between_archives": self.seed_transferred_between_archives,
            "archive_family_coherence_claimed": self.archive_family_coherence_claimed,
            "historical_run_identity_claimed": self.historical_run_identity_claimed,
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
            "production_release_approved": self.production_release_approved,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class _FrmdinfCall:
    first_argument: int
    period: int
    active_insurers: int
    active_policyholders: int


def build_historical_archive_run_metadata(
    *,
    root: Path | str = ".",
    archive_paths: Sequence[Path | str] | None = None,
) -> HistoricalArchiveRunMetadataResult:
    resolved_root = Path(root).expanduser().resolve()
    requested_paths = tuple(DEFAULT_ARCHIVE_PATHS if archive_paths is None else archive_paths)
    resolved_paths = tuple(_resolve_against_root(resolved_root, path) for path in requested_paths)
    issues: list[HistoricalArchiveRunMetadataIssue] = []
    archives = tuple(_inspect_archive(resolved_root, path, issues) for path in resolved_paths)
    readable_archives = tuple(archive for archive in archives if archive.readable)
    support_files = tuple(
        support_file for archive in readable_archives for support_file in archive.support_files
    )
    run_report_count = sum(
        support_file.category == "run_report" for support_file in support_files
    )
    return HistoricalArchiveRunMetadataResult(
        status=_status_from_issues(issues),
        mode="historical_archive_run_metadata",
        contract_version=CONTRACT_VERSION,
        root=str(resolved_root),
        archive_count=len(archives),
        readable_archive_count=len(readable_archives),
        archives_with_run_report=sum(
            archive.run_report is not None for archive in readable_archives
        ),
        archives_without_run_report=sum(
            archive.run_report is None for archive in readable_archives
        ),
        run_report_count=run_report_count,
        support_file_count=len(support_files),
        model_definition_parameter_file_count=sum(
            support_file.category in {"model_definition", "parameter"}
            for support_file in support_files
        ),
        archives=archives,
        files_extracted=False,
        writes_enabled=False,
        execution_enabled=False,
        simulation_performed=False,
        metadata_content_interpreted=any(
            archive.run_report is not None for archive in readable_archives
        ),
        missing_metadata_treated_as_default=False,
        cross_archive_metadata_transfer_performed=False,
        seed_transferred_between_archives=False,
        archive_family_coherence_claimed=False,
        historical_run_identity_claimed=False,
        historical_full_equality_claimed=False,
        production_release_approved=False,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_historical_archive_run_metadata(root=args.root, archive_paths=args.archive)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _inspect_archive(
    root: Path,
    archive_path: Path,
    issues: list[HistoricalArchiveRunMetadataIssue],
) -> HistoricalArchiveRunMetadata:
    display_path = _display_path(root, archive_path)
    if not archive_path.is_file():
        issues.append(
            HistoricalArchiveRunMetadataIssue(
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
            support_files: list[HistoricalArchiveSupportFile] = []
            run_reports: list[tuple[zipfile.ZipInfo, bytes]] = []
            output_entry_count = 0
            for info in infos:
                member_path = info.filename.replace("\\", "/")
                filename = PurePosixPath(member_path).name.upper()
                if _EXPORT_PATTERN.fullmatch(filename):
                    output_entry_count += 1
                    continue
                data = archive.read(info)
                category = _support_file_category(filename)
                support_files.append(
                    HistoricalArchiveSupportFile(
                        member_path=member_path,
                        filename=filename,
                        category=category,
                        sha256=_sha256_bytes(data),
                        size_bytes=info.file_size,
                        compressed_size_bytes=info.compress_size,
                        zip_timestamp=_zip_timestamp(info),
                        content_interpreted=False,
                    )
                )
                if filename == RUN_REPORT_FILENAME:
                    run_reports.append((info, data))
    except (OSError, RuntimeError, zipfile.BadZipFile) as error:
        issues.append(
            HistoricalArchiveRunMetadataIssue(
                code="archive_invalid_zip",
                severity="error",
                archive_path=display_path,
                member_path=None,
                message=f"historical archive is not a readable ZIP file: {error}",
            )
        )
        return _unreadable_archive(
            display_path,
            archive_path.name,
            sha256=archive_hash,
            size_bytes=archive_path.stat().st_size,
        )

    support_files.sort(key=lambda support_file: support_file.member_path)
    run_report: HistoricalRunReport | None = None
    run_report_member_path: str | None = None
    if len(run_reports) > 1:
        issues.append(
            HistoricalArchiveRunMetadataIssue(
                code="run_report_duplicate",
                severity="error",
                archive_path=display_path,
                member_path=None,
                message=f"archive contains {len(run_reports)} entries named {RUN_REPORT_FILENAME}",
            )
        )
        metadata_status = "direct_run_report_invalid"
    elif run_reports:
        info, data = run_reports[0]
        run_report_member_path = info.filename.replace("\\", "/")
        run_report = _parse_run_report(display_path, run_report_member_path, data, issues)
        metadata_status = (
            "direct_run_report" if run_report is not None else "direct_run_report_invalid"
        )
    elif support_files:
        metadata_status = "support_files_only"
    else:
        metadata_status = "metadata_absent"
    if run_report is not None:
        support_files = [
            replace(
                support_file,
                content_interpreted=(support_file.member_path == run_report_member_path),
            )
            for support_file in support_files
        ]

    return HistoricalArchiveRunMetadata(
        archive_path=display_path,
        archive_filename=archive_path.name,
        readable=True,
        sha256=archive_hash,
        size_bytes=archive_path.stat().st_size,
        entry_count=len(infos),
        output_entry_count=output_entry_count,
        support_entry_count=len(support_files),
        metadata_status=metadata_status,
        run_report_member_path=run_report_member_path,
        run_report=run_report,
        support_files=tuple(support_files),
    )


def _parse_run_report(
    archive_path: str,
    member_path: str,
    data: bytes,
    issues: list[HistoricalArchiveRunMetadataIssue],
) -> HistoricalRunReport | None:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        issues.append(
            HistoricalArchiveRunMetadataIssue(
                code="run_report_decode_error",
                severity="error",
                archive_path=archive_path,
                member_path=member_path,
                message=f"run report is not UTF-8/ASCII compatible: {error}",
            )
        )
        return None

    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    version_line = next((line.strip() for line in lines if line.startswith("IMS Version ")), None)
    version_match = _VERSION_PATTERN.fullmatch(version_line) if version_line is not None else None
    seed_match = _first_match(lines, _SEED_PATTERN)
    insurer_match = _first_match(lines, _INSURER_MEMORY_PATTERN)
    policyholder_match = _first_match(lines, _POLICYHOLDER_MEMORY_PATTERN)
    initial_bv_match = _first_match(lines, _INITIAL_BV_PATTERN)
    frmdinf_calls = tuple(
        _FrmdinfCall(*map(int, match.groups()))
        for line in lines
        if (match := _FRMDINF_PATTERN.fullmatch(line.strip()))
    )
    agrsich_calls = tuple(
        tuple(map(int, match.groups()))
        for line in lines
        if (match := _AGRSICH_PATTERN.fullmatch(line.strip()))
    )
    required = (
        (version_match, "run_report_version_missing", "version and compile line"),
        (seed_match, "run_report_seed_missing", "seed"),
        (insurer_match, "run_report_insurer_memory_missing", "VU allocation"),
        (policyholder_match, "run_report_policyholder_memory_missing", "VN allocation"),
        (initial_bv_match, "run_report_initial_bv_missing", "initial BV values"),
        (frmdinf_calls, "run_report_frmdinf_missing", "Frmdinf calls"),
        (agrsich_calls, "run_report_agrsich_missing", "Agrsich calls"),
    )
    invalid = False
    for value, code, label in required:
        if value:
            continue
        invalid = True
        issues.append(
            HistoricalArchiveRunMetadataIssue(
                code=code,
                severity="error",
                archive_path=archive_path,
                member_path=member_path,
                message=f"run report does not contain a recognizable {label}",
            )
        )

    frmdinf_periods = tuple(call.period for call in frmdinf_calls)
    agrsich_periods = tuple(period for _, period in agrsich_calls)
    if frmdinf_calls and agrsich_calls and frmdinf_periods != agrsich_periods:
        invalid = True
        issues.append(
            HistoricalArchiveRunMetadataIssue(
                code="run_report_call_alignment_mismatch",
                severity="error",
                archive_path=archive_path,
                member_path=member_path,
                message="Frmdinf and Agrsich period sequences differ",
            )
        )

    sequences = _split_sequences(frmdinf_calls)
    if any(not sequence.periods_contiguous for sequence in sequences):
        invalid = True
        issues.append(
            HistoricalArchiveRunMetadataIssue(
                code="run_report_period_sequence_gap",
                severity="error",
                archive_path=archive_path,
                member_path=member_path,
                message="at least one observed Frmdinf period sequence is not contiguous",
            )
        )

    end_marker_present = any("IMS-Reportdatei ENDE" in line for line in lines)
    if not end_marker_present:
        invalid = True
        issues.append(
            HistoricalArchiveRunMetadataIssue(
                code="run_report_end_marker_missing",
                severity="error",
                archive_path=archive_path,
                member_path=member_path,
                message="run report end marker is missing",
            )
        )
    if invalid:
        return None

    allocated_memory_values = tuple(
        int(match.group(1))
        for line in lines
        if (match := _ALLOCATED_MEMORY_PATTERN.fullmatch(line.strip()))
    )
    assert version_match is not None
    assert seed_match is not None
    assert insurer_match is not None
    assert policyholder_match is not None
    assert initial_bv_match is not None
    return HistoricalRunReport(
        version_line=version_line,
        platform=version_match.group("platform"),
        version=version_match.group("version"),
        compiled_at_text=version_match.group("compiled_at"),
        seed=int(seed_match.group(1)),
        allocated_insurer_count=int(insurer_match.group(1)),
        allocated_insurer_bytes=int(insurer_match.group(2)),
        allocated_policyholder_count=int(policyholder_match.group(1)),
        allocated_policyholder_bytes=int(policyholder_match.group(2)),
        initial_bv_values=(int(initial_bv_match.group(1)), int(initial_bv_match.group(2))),
        reset_bv_values=tuple(
            (int(match.group(1)), int(match.group(2)))
            for line in lines
            if (match := _RESET_BV_PATTERN.fullmatch(line.strip()))
        ),
        line_count=len(lines),
        frmdinf_call_count=len(frmdinf_calls),
        agrsich_call_count=len(agrsich_calls),
        agrsich_first_argument_values=tuple(sorted({argument for argument, _ in agrsich_calls})),
        sequences=sequences,
        insurer_release_count=sum(
            _INSURER_RELEASE_PATTERN.fullmatch(line.strip()) is not None for line in lines
        ),
        policyholder_release_count=sum(
            _POLICYHOLDER_RELEASE_PATTERN.fullmatch(line.strip()) is not None for line in lines
        ),
        final_allocated_bytes=allocated_memory_values[-1] if allocated_memory_values else None,
        end_marker_present=end_marker_present,
    )


def _split_sequences(calls: Sequence[_FrmdinfCall]) -> tuple[HistoricalReportSequence, ...]:
    groups: list[list[_FrmdinfCall]] = []
    for call in calls:
        if not groups or call.period <= groups[-1][-1].period:
            groups.append([])
        groups[-1].append(call)
    return tuple(
        HistoricalReportSequence(
            sequence_index=index,
            call_count=len(group),
            period_start=group[0].period,
            period_end=group[-1].period,
            periods_contiguous=[call.period for call in group]
            == list(range(group[0].period, group[-1].period + 1)),
            frmdinf_first_argument_values=tuple(sorted({call.first_argument for call in group})),
            active_insurer_counts=tuple(sorted({call.active_insurers for call in group})),
            active_policyholder_counts=tuple(
                sorted({call.active_policyholders for call in group})
            ),
        )
        for index, group in enumerate(groups, start=1)
    )


def _first_match(lines: Sequence[str], pattern: re.Pattern[str]) -> re.Match[str] | None:
    return next((match for line in lines if (match := pattern.fullmatch(line.strip()))), None)


def _support_file_category(filename: str) -> str:
    stem = PurePosixPath(filename).stem.upper()
    suffix = PurePosixPath(filename).suffix.upper()
    if filename == RUN_REPORT_FILENAME:
        return "run_report"
    if suffix == ".DEF" or "MODEL" in stem or "DEFINITION" in stem:
        return "model_definition"
    if "PARAM" in stem:
        return "parameter"
    if suffix == ".LOG" or "PROTO" in stem:
        return "run_protocol"
    return "unclassified_support"


def _unreadable_archive(
    display_path: str,
    filename: str,
    *,
    sha256: str | None = None,
    size_bytes: int | None = None,
) -> HistoricalArchiveRunMetadata:
    return HistoricalArchiveRunMetadata(
        archive_path=display_path,
        archive_filename=filename,
        readable=False,
        sha256=sha256,
        size_bytes=size_bytes,
        entry_count=0,
        output_entry_count=0,
        support_entry_count=0,
        metadata_status="archive_unreadable",
        run_report_member_path=None,
        run_report=None,
        support_files=(),
    )


def _resolve_against_root(root: Path, path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _zip_timestamp(info: zipfile.ZipInfo) -> str:
    year, month, day, hour, minute, second = info.date_time
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"


def _status_from_issues(issues: Sequence[HistoricalArchiveRunMetadataIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_archive_run_metadata",
        description=(
            "Wertet historische Laufmetadaten archivlokal aus, ohne Dateien zu "
            "extrahieren, Werte zu uebertragen oder eine Simulation zu starten."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repo-Wurzel fuer relative Archivpfade.",
    )
    parser.add_argument(
        "--archive",
        action="append",
        type=Path,
        help="Expliziter Archivpfad; ohne Angabe werden die sieben bekannten Archive gelesen.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
