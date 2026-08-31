import hashlib
import json
import zipfile
from pathlib import Path

from ims.api.historical_archive_manifest import (
    CONTRACT_VERSION,
    CORE_EXPORT_FILENAMES,
    DEFAULT_ARCHIVE_PATHS,
    HistoricalArchiveManifestResult,
    build_historical_archive_manifest,
    main,
)
from ims.model.agrsich_export import INSURER_HEADER, POLICYHOLDER_HEADER


def test_manifest_reads_core_members_and_metadata_without_extracting(tmp_path: Path) -> None:
    archive_path = tmp_path / "family.zip"
    insurer_data = _table(INSURER_HEADER, 13, (1, 2, 3))
    policyholder_data = _table(POLICYHOLDER_HEADER, 12, (101, 102))
    _write_zip(
        archive_path,
        {
            "exports/IMSVU014.DAT": insurer_data,
            "exports/imsvnr01.dat": policyholder_data,
            "notes/IMSREPOR.DAT": "seed 5616\n",
            "other.txt": "not metadata\n",
        },
    )

    payload = build_historical_archive_manifest(
        root=tmp_path,
        archive_paths=[Path("family.zip")],
    ).to_dict()
    archive = payload["archives"][0]
    members = {member["filename"]: member for member in archive["core_members"]}

    assert payload["status"] == "ok"
    assert payload["contract_version"] == CONTRACT_VERSION
    assert payload["archive_count"] == 1
    assert payload["readable_archive_count"] == 1
    assert payload["entry_count"] == 4
    assert payload["dat_entry_count"] == 3
    assert payload["core_member_count"] == 2
    assert archive["archive_path"] == "family.zip"
    assert archive["sha256"] == _sha256(archive_path.read_bytes())
    assert archive["entry_count"] == 4
    assert archive["dat_entry_count"] == 3
    assert members["IMSVU014.DAT"]["subject_type"] == "insurer"
    assert members["IMSVU014.DAT"]["expected_column_count"] == 13
    assert members["IMSVU014.DAT"]["row_count"] == 3
    assert members["IMSVU014.DAT"]["period_start"] == 1
    assert members["IMSVU014.DAT"]["period_end"] == 3
    assert members["IMSVU014.DAT"]["periods_contiguous"] is True
    assert members["IMSVU014.DAT"]["sha256"] == _sha256(insurer_data.encode())
    assert members["IMSVNR01.DAT"]["subject_type"] == "policyholder"
    assert members["IMSVNR01.DAT"]["row_count"] == 2
    assert members["IMSVNR01.DAT"]["period_start"] == 101
    assert members["IMSVNR01.DAT"]["period_end"] == 102
    assert archive["metadata_candidates"][0]["filename"] == "IMSREPOR.DAT"
    assert archive["metadata_candidates"][0]["matched_tokens"] == ["REPOR"]
    assert payload["files_extracted"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert not (tmp_path / "exports").exists()
    assert not (tmp_path / "notes").exists()


def test_manifest_classifies_all_fifteen_core_export_names(tmp_path: Path) -> None:
    entries: dict[str, str] = {}
    for filename in CORE_EXPORT_FILENAMES:
        policyholder = filename.startswith("IMSVNR") or filename == "IMSVNSK1.DAT" or filename.startswith("IMSVNVK")
        header = POLICYHOLDER_HEADER if policyholder else INSURER_HEADER
        columns = 12 if policyholder else 13
        entries[f"run/{filename.lower()}"] = _table(header, columns, (1,))
    archive_path = tmp_path / "complete.zip"
    _write_zip(archive_path, entries)

    payload = build_historical_archive_manifest(
        root=tmp_path,
        archive_paths=[archive_path],
    ).to_dict()
    archive = payload["archives"][0]

    assert payload["status"] == "ok"
    assert payload["unique_core_filenames"] == sorted(CORE_EXPORT_FILENAMES)
    assert payload["archives_with_all_core_members"] == 1
    assert archive["core_member_count"] == 15
    assert archive["missing_core_filenames"] == []
    assert all(member["header_matches_expected"] for member in archive["core_members"])


def test_manifest_reports_malformed_header_rows_and_period_window(tmp_path: Path) -> None:
    archive_path = tmp_path / "malformed.zip"
    _write_zip(
        archive_path,
        {
            "IMSVU014.DAT": "# wrong\n1 0\n2 " + " ".join("0" for _ in range(12)) + "\n4 " + " ".join("0" for _ in range(12)) + "\n",
            "IMSVNR01.DAT": POLICYHOLDER_HEADER + "\n1 " + " ".join("0" for _ in range(10)) + " bad\n",
        },
    )

    payload = build_historical_archive_manifest(
        root=tmp_path,
        archive_paths=[archive_path],
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}
    insurer = next(
        member
        for member in payload["archives"][0]["core_members"]
        if member["filename"] == "IMSVU014.DAT"
    )

    assert payload["status"] == "error"
    assert "core_member_header_mismatch" in issue_codes
    assert "core_member_column_count" in issue_codes
    assert "core_member_period_gap" in issue_codes
    assert "core_member_non_numeric_row" in issue_codes
    assert insurer["row_count"] == 3
    assert insurer["valid_period_count"] == 2
    assert insurer["period_start"] == 2
    assert insurer["period_end"] == 4
    assert insurer["periods_contiguous"] is False


def test_manifest_reports_duplicate_core_basename(tmp_path: Path) -> None:
    archive_path = tmp_path / "duplicate.zip"
    data = _table(POLICYHOLDER_HEADER, 12, (1,))
    _write_zip(
        archive_path,
        {
            "a/IMSVNR01.DAT": data,
            "b/imsvnr01.dat": data,
        },
    )

    payload = build_historical_archive_manifest(
        root=tmp_path,
        archive_paths=[archive_path],
    ).to_dict()

    assert payload["status"] == "error"
    assert payload["archives"][0]["core_member_count"] == 1
    assert len(payload["archives"][0]["core_members"]) == 2
    assert "core_member_duplicate" in {issue["code"] for issue in payload["issues"]}


def test_manifest_reports_missing_and_invalid_archives_without_writing(tmp_path: Path) -> None:
    invalid_archive = tmp_path / "invalid.zip"
    invalid_archive.write_bytes(b"not a zip")

    payload = build_historical_archive_manifest(
        root=tmp_path,
        archive_paths=["missing.zip", invalid_archive],
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["archive_count"] == 2
    assert payload["readable_archive_count"] == 0
    assert "archive_missing" in issue_codes
    assert "archive_invalid_zip" in issue_codes
    assert list(tmp_path.iterdir()) == [invalid_archive]


def test_manifest_cli_uses_explicit_synthetic_archive(tmp_path: Path, capsys) -> None:
    archive_path = tmp_path / "one.zip"
    _write_zip(archive_path, {"IMSVNSK1.DAT": _table(POLICYHOLDER_HEADER, 12, (1, 2))})

    exit_code = main(["--root", str(tmp_path), "--archive", "one.zip"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "historical_archive_manifest"
    assert payload["archive_count"] == 1
    assert payload["core_member_count"] == 1
    assert payload["historical_run_identity_claimed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False
    assert HistoricalArchiveManifestResult is not None


def test_default_manifest_paths_are_the_seven_known_unversioned_archives() -> None:
    assert len(DEFAULT_ARCHIVE_PATHS) == 7
    assert {path.name for path in DEFAULT_ARCHIVE_PATHS} == {
        "VDEFMD5A.ZIP",
        "VDEFMOD5.ZIP",
        "ZINS000.ZIP",
        "ZINS030.ZIP",
        "WVEMOD1.ZIP",
        "WVEMOD2.ZIP",
        "WVEMOD3.ZIP",
    }
    assert all(path.parts[0] == "incomming" for path in DEFAULT_ARCHIVE_PATHS)


def _write_zip(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for member_path, content in entries.items():
            info = zipfile.ZipInfo(member_path, date_time=(1995, 6, 1, 12, 34, 56))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content.encode("utf-8"))


def _table(header: str, columns: int, periods: tuple[int, ...]) -> str:
    values = " ".join("0" for _ in range(columns - 1))
    rows = "".join(f"{period} {values}\n" for period in periods)
    return f"{header}\n{rows}"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
