import json
import zipfile
from pathlib import Path

from ims.api.historical_reference_archive_coherence import (
    CLASSIFICATIONS,
    CONTRACT_VERSION,
    REFERENCE_SPECS,
    HistoricalReferenceSpec,
    build_historical_reference_archive_coherence,
    main,
)


HEADER = "#t A B"


def test_coherence_prefers_byte_exact_member_and_records_token_match(tmp_path: Path) -> None:
    spec = HistoricalReferenceSpec(
        "REFERENCE.DAT", "ARCHIVE.DAT", "insurer", "I", "entity", 14, 1, 2
    )
    reference_data = _table((1, 2))
    _write_reference(tmp_path, spec.reference_filename, reference_data)
    _write_zip(tmp_path / "exact.zip", {spec.archive_filename: reference_data})
    _write_zip(
        tmp_path / "normalized.zip",
        {spec.archive_filename: "#t   A B\n1  10  20\n2 10 20\n"},
    )

    payload = build_historical_reference_archive_coherence(
        root=tmp_path,
        reference_dir="references",
        archive_paths=["exact.zip", "normalized.zip"],
        reference_specs=[spec],
    ).to_dict()
    target = payload["targets"][0]
    candidates = {candidate["archive_path"]: candidate for candidate in target["candidates"]}

    assert payload["status"] == "ok"
    assert payload["contract_version"] == CONTRACT_VERSION
    assert payload["classification_counts"] == {
        "exact_archive_member": 1,
        "exact_window_slice": 0,
        "same_name_divergent": 0,
        "unresolved": 0,
    }
    assert target["classification"] == "exact_archive_member"
    assert target["selected_archive_path"] == "exact.zip"
    assert target["selected_matching_basis"] == "byte_exact"
    assert candidates["exact.zip"]["byte_matches"] is True
    assert candidates["normalized.zip"]["byte_matches"] is False
    assert candidates["normalized.zip"]["token_normalized_matches"] is True
    assert candidates["normalized.zip"]["matching_basis"] == "token_normalized"


def test_coherence_matches_interior_sk1_window_without_creating_aggregate_levels(
    tmp_path: Path,
) -> None:
    spec = HistoricalReferenceSpec(
        "VUSK1L4.DAT", "IMSVUSK1.DAT", "insurer", "IV", "all", "SK1", 3, 4
    )
    archive_data = _table((1, 2, 3, 4, 5))
    reference_data = _table((3, 4))
    _write_reference(tmp_path, spec.reference_filename, reference_data)
    _write_zip(tmp_path / "window.zip", {spec.archive_filename: archive_data})

    payload = build_historical_reference_archive_coherence(
        root=tmp_path,
        reference_dir="references",
        archive_paths=["window.zip"],
        reference_specs=[spec],
    ).to_dict()
    target = payload["targets"][0]
    candidate = target["candidates"][0]

    assert target["classification"] == "exact_window_slice"
    assert target["level"] == "IV"
    assert target["selector_kind"] == "all"
    assert target["selector_value"] == "SK1"
    assert target["period_start"] == 3
    assert target["period_end"] == 4
    assert candidate["comparison_scope"] == "period_window"
    assert candidate["compared_row_count"] == 2
    assert candidate["byte_matches"] is True
    assert not (tmp_path / "IMSVUSK1.DAT").exists()


def test_coherence_separates_divergent_from_unresolved_targets(tmp_path: Path) -> None:
    divergent = HistoricalReferenceSpec(
        "DIVERGENT.DAT", "MATCH.DAT", "policyholder", "II", "rule", 1, 1, 2
    )
    unresolved = HistoricalReferenceSpec(
        "UNRESOLVED.DAT", "ABSENT.DAT", "policyholder", "II", "rule", 2, 1, 2
    )
    _write_reference(tmp_path, divergent.reference_filename, _table((1, 2)))
    _write_reference(tmp_path, unresolved.reference_filename, _table((1, 2)))
    _write_zip(tmp_path / "family.zip", {"MATCH.DAT": _table((1, 2), value="99")})

    payload = build_historical_reference_archive_coherence(
        root=tmp_path,
        reference_dir="references",
        archive_paths=["family.zip"],
        reference_specs=[divergent, unresolved],
    ).to_dict()
    targets = {target["reference_filename"]: target for target in payload["targets"]}

    assert payload["status"] == "ok"
    assert targets["DIVERGENT.DAT"]["classification"] == "same_name_divergent"
    assert targets["DIVERGENT.DAT"]["candidates"][0]["matching_basis"] == "none"
    assert targets["UNRESOLVED.DAT"]["classification"] == "unresolved"
    assert targets["UNRESOLVED.DAT"]["candidates"] == []


def test_coherence_rejects_missing_reference_and_invalid_archive(tmp_path: Path) -> None:
    spec = HistoricalReferenceSpec(
        "MISSING.DAT", "ARCHIVE.DAT", "insurer", "I", "entity", 1, 1, 1
    )
    (tmp_path / "invalid.zip").write_bytes(b"not a zip")

    payload = build_historical_reference_archive_coherence(
        root=tmp_path,
        reference_dir="references",
        archive_paths=["invalid.zip", "missing.zip"],
        reference_specs=[spec],
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["targets"][0]["classification"] == "unresolved"
    assert "reference_missing" in issue_codes
    assert "archive_invalid_zip" in issue_codes
    assert "archive_missing" in issue_codes
    assert list(tmp_path.iterdir()) == [tmp_path / "invalid.zip"]


def test_coherence_reports_duplicate_archive_basename(tmp_path: Path) -> None:
    spec = HistoricalReferenceSpec(
        "REFERENCE.DAT", "ARCHIVE.DAT", "insurer", "I", "entity", 1, 1, 1
    )
    data = _table((1,))
    _write_reference(tmp_path, spec.reference_filename, data)
    _write_zip(
        tmp_path / "duplicates.zip",
        {"a/ARCHIVE.DAT": data, "b/archive.dat": data},
    )

    payload = build_historical_reference_archive_coherence(
        root=tmp_path,
        reference_dir="references",
        archive_paths=["duplicates.zip"],
        reference_specs=[spec],
    ).to_dict()

    assert payload["status"] == "error"
    assert payload["candidate_count"] == 2
    assert "archive_member_duplicate" in {issue["code"] for issue in payload["issues"]}


def test_default_specs_fix_nineteen_targets_and_five_sk1_windows() -> None:
    assert CLASSIFICATIONS == (
        "exact_archive_member",
        "exact_window_slice",
        "same_name_divergent",
        "unresolved",
    )
    assert len(REFERENCE_SPECS) == 19
    sk1_windows = [spec for spec in REFERENCE_SPECS if spec.reference_filename.startswith("VUSK1L")]
    assert len(sk1_windows) == 5
    assert {spec.level for spec in sk1_windows} == {"IV"}
    assert {spec.selector_kind for spec in sk1_windows} == {"all"}
    assert {spec.selector_value for spec in sk1_windows} == {"SK1"}
    assert {(spec.period_start, spec.period_end) for spec in sk1_windows} == {
        (1, 100),
        (101, 200),
        (201, 300),
        (301, 400),
        (401, 500),
    }
    vn_sk1 = next(spec for spec in REFERENCE_SPECS if spec.reference_filename == "IMSVNSK1.DAT")
    assert (vn_sk1.period_start, vn_sk1.period_end) == (1, 500)


def test_coherence_cli_prints_json_without_execution(tmp_path: Path, capsys) -> None:
    entries: dict[str, str] = {}
    max_period_by_member: dict[str, int] = {}
    for spec in REFERENCE_SPECS:
        max_period_by_member[spec.archive_filename] = max(
            max_period_by_member.get(spec.archive_filename, 0), spec.period_end
        )
        _write_reference(
            tmp_path,
            spec.reference_filename,
            _table(tuple(range(spec.period_start, spec.period_end + 1))),
        )
    for filename, period_end in max_period_by_member.items():
        entries[filename] = _table(tuple(range(1, period_end + 1)))
    _write_zip(tmp_path / "all.zip", entries)

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "--reference-dir",
            "references",
            "--archive",
            "all.zip",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "historical_reference_archive_coherence"
    assert payload["target_count"] == 19
    assert payload["classification_counts"]["unresolved"] == 0
    assert payload["files_extracted"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["archive_family_coherence_claimed"] is False
    assert payload["historical_run_identity_claimed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False


def _write_reference(root: Path, filename: str, content: str) -> None:
    reference_dir = root / "references"
    reference_dir.mkdir(exist_ok=True)
    (reference_dir / filename).write_text(content, encoding="utf-8", newline="")


def _write_zip(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for member_path, content in entries.items():
            archive.writestr(member_path, content.encode("utf-8"))


def _table(periods: tuple[int, ...], *, value: str = "10") -> str:
    rows = "".join(f"{period} {value} 20\n" for period in periods)
    return f"{HEADER}\n{rows}"
