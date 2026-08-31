import hashlib
import json
import zipfile
from pathlib import Path

from ims.api.historical_archive_run_metadata import (
    CONTRACT_VERSION,
    HistoricalArchiveRunMetadataResult,
    build_historical_archive_run_metadata,
    main,
)


def test_run_metadata_reads_report_and_classifies_support_files_locally(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "family.zip"
    report = _report(((1, 2), (1, 2)))
    _write_zip(
        archive_path,
        {
            "exports/IMSVNR01.DAT": "#t A\n1 0\n",
            "notes/IMSREPOR.DAT": report,
            "MODEL.DEF": "definition\n",
            "PARAMETER.TXT": "parameter\n",
            "RUN.LOG": "protocol\n",
            "README.TXT": "unclassified\n",
        },
    )

    payload = build_historical_archive_run_metadata(
        root=tmp_path,
        archive_paths=["family.zip"],
    ).to_dict()
    archive = payload["archives"][0]
    run_report = archive["run_report"]
    support_by_name = {
        support_file["filename"]: support_file
        for support_file in archive["support_files"]
    }

    assert payload["status"] == "ok"
    assert payload["contract_version"] == CONTRACT_VERSION
    assert payload["archive_count"] == 1
    assert payload["archives_with_run_report"] == 1
    assert payload["archives_without_run_report"] == 0
    assert payload["run_report_count"] == 1
    assert payload["support_file_count"] == 5
    assert payload["model_definition_parameter_file_count"] == 2
    assert archive["archive_path"] == "family.zip"
    assert archive["sha256"] == _sha256(archive_path.read_bytes())
    assert archive["entry_count"] == 6
    assert archive["output_entry_count"] == 1
    assert archive["support_entry_count"] == 5
    assert archive["metadata_status"] == "direct_run_report"
    assert archive["run_report_member_path"] == "notes/IMSREPOR.DAT"
    assert support_by_name["IMSREPOR.DAT"]["category"] == "run_report"
    assert support_by_name["IMSREPOR.DAT"]["content_interpreted"] is True
    assert support_by_name["MODEL.DEF"]["category"] == "model_definition"
    assert support_by_name["PARAMETER.TXT"]["category"] == "parameter"
    assert support_by_name["RUN.LOG"]["category"] == "run_protocol"
    assert support_by_name["README.TXT"]["category"] == "unclassified_support"
    assert run_report["platform"] == "MSDOS"
    assert run_report["version"] == "v1.0"
    assert run_report["compiled_at_text"] == "Jun  1 1995 12:34:56"
    assert run_report["seed"] == 5616
    assert run_report["allocated_insurer_count"] == 25
    assert run_report["allocated_insurer_bytes"] == 199200
    assert run_report["allocated_policyholder_count"] == 200
    assert run_report["allocated_policyholder_bytes"] == 1923200
    assert run_report["initial_bv_values"] == [1, 1]
    assert run_report["reset_bv_values"] == [[1, 1]]
    assert run_report["frmdinf_call_count"] == 4
    assert run_report["agrsich_call_count"] == 4
    assert run_report["agrsich_first_argument_values"] == [10]
    assert len(run_report["sequences"]) == 2
    assert all(sequence["period_start"] == 1 for sequence in run_report["sequences"])
    assert all(sequence["period_end"] == 2 for sequence in run_report["sequences"])
    assert all(sequence["periods_contiguous"] for sequence in run_report["sequences"])
    assert run_report["insurer_release_count"] == 1
    assert run_report["policyholder_release_count"] == 1
    assert run_report["final_allocated_bytes"] == 0
    assert run_report["end_marker_present"] is True
    assert not (tmp_path / "exports").exists()
    assert not (tmp_path / "notes").exists()


def test_run_metadata_keeps_missing_values_archive_local(tmp_path: Path) -> None:
    _write_zip(tmp_path / "with-report.zip", {"IMSREPOR.DAT": _report(((1,),))})
    _write_zip(tmp_path / "without-report.zip", {"IMSVNR01.DAT": "#t A\n1 0\n"})

    payload = build_historical_archive_run_metadata(
        root=tmp_path,
        archive_paths=["with-report.zip", "without-report.zip"],
    ).to_dict()
    archives = {archive["archive_filename"]: archive for archive in payload["archives"]}

    assert payload["status"] == "ok"
    assert payload["archives_with_run_report"] == 1
    assert payload["archives_without_run_report"] == 1
    assert archives["with-report.zip"]["run_report"]["seed"] == 5616
    assert archives["without-report.zip"]["metadata_status"] == "metadata_absent"
    assert archives["without-report.zip"]["run_report"] is None
    assert payload["missing_metadata_treated_as_default"] is False
    assert payload["cross_archive_metadata_transfer_performed"] is False
    assert payload["seed_transferred_between_archives"] is False


def test_run_metadata_rejects_incomplete_and_misaligned_reports(tmp_path: Path) -> None:
    incomplete = _report(((1, 2),)).replace("Seed : 5616\n", "")
    misaligned = _report(((1, 2),)).replace("Agrsich(10,2)", "Agrsich(10,3)")
    _write_zip(tmp_path / "incomplete.zip", {"IMSREPOR.DAT": incomplete})
    _write_zip(tmp_path / "misaligned.zip", {"IMSREPOR.DAT": misaligned})

    payload = build_historical_archive_run_metadata(
        root=tmp_path,
        archive_paths=["incomplete.zip", "misaligned.zip"],
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "run_report_seed_missing" in issue_codes
    assert "run_report_call_alignment_mismatch" in issue_codes
    assert all(
        archive["metadata_status"] == "direct_run_report_invalid"
        for archive in payload["archives"]
    )
    assert all(archive["run_report"] is None for archive in payload["archives"])
    assert payload["metadata_content_interpreted"] is False
    assert all(
        archive["support_files"][0]["content_interpreted"] is False
        for archive in payload["archives"]
    )


def test_run_metadata_rejects_duplicate_report_basenames(tmp_path: Path) -> None:
    report = _report(((1,),))
    _write_zip(
        tmp_path / "duplicate.zip",
        {"a/IMSREPOR.DAT": report, "b/imsrepor.dat": report},
    )

    payload = build_historical_archive_run_metadata(
        root=tmp_path,
        archive_paths=["duplicate.zip"],
    ).to_dict()

    assert payload["status"] == "error"
    assert payload["run_report_count"] == 2
    assert payload["archives_with_run_report"] == 0
    assert payload["archives"][0]["metadata_status"] == "direct_run_report_invalid"
    assert "run_report_duplicate" in {issue["code"] for issue in payload["issues"]}


def test_run_metadata_reports_missing_and_invalid_archives(tmp_path: Path) -> None:
    invalid_archive = tmp_path / "invalid.zip"
    invalid_archive.write_bytes(b"not a zip")

    payload = build_historical_archive_run_metadata(
        root=tmp_path,
        archive_paths=["missing.zip", "invalid.zip"],
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["archive_count"] == 2
    assert payload["readable_archive_count"] == 0
    assert "archive_missing" in issue_codes
    assert "archive_invalid_zip" in issue_codes
    assert list(tmp_path.iterdir()) == [invalid_archive]


def test_run_metadata_cli_prints_json_without_execution(tmp_path: Path, capsys) -> None:
    _write_zip(tmp_path / "one.zip", {"IMSREPOR.DAT": _report(((1, 2),))})

    exit_code = main(["--root", str(tmp_path), "--archive", "one.zip"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "historical_archive_run_metadata"
    assert payload["metadata_content_interpreted"] is True
    assert payload["files_extracted"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["archive_family_coherence_claimed"] is False
    assert payload["historical_run_identity_claimed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False
    assert HistoricalArchiveRunMetadataResult is not None


def _report(sequences: tuple[tuple[int, ...], ...]) -> str:
    lines = [
        "IMS Version MSDOS v1.0 (c) mk, compiled on  Jun  1 1995 12:34:56",
        "",
        "********************** IMS-Reportdatei *******************",
        "Seed : 5616",
        "Speicher fuer 25 VUs: 199200 Bytes",
        "Speicher fuer 200 VNs: 1923200 Bytes",
        "Myinitbv:[1,1]",
    ]
    for sequence_index, periods in enumerate(sequences):
        if sequence_index:
            lines.append("Newinibv:[1,1]")
        for period in periods:
            lines.append(f"Frmdinf(1,{period}).akvu(25),akvn(200)")
            lines.append(f"Agrsich(10,{period})")
    lines.extend(
        [
            "********** IMS-Reportdatei ENDE *********",
            "7968 Bytes von VU[1] freigegeben",
            "8620 Bytes von VN[1] freigegeben",
            "Bisher allocierter Speicher: 0 Bytes",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_zip(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for member_path, content in entries.items():
            info = zipfile.ZipInfo(member_path, date_time=(1995, 6, 1, 12, 34, 56))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content.encode("utf-8"))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
