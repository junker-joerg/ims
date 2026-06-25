import json
from pathlib import Path

from ims.model.legacy_validation_coverage import (
    LegacyValidationCoverageMatrixResult,
    build_legacy_validation_coverage_matrix,
    main,
)


FIXTURE_DIR = Path("tests/fixtures")
MIGRATION_DOC = Path("docs/migration/agrsich_validation_report.md")


def test_legacy_validation_coverage_matrix_summarizes_current_bundle() -> None:
    result = build_legacy_validation_coverage_matrix(FIXTURE_DIR / "legacy_validation_bundle.json")
    payload = result.to_dict()

    assert isinstance(result, LegacyValidationCoverageMatrixResult)
    assert payload["status"] == "ok"
    assert payload["mode"] == "legacy_agrsich_coverage_matrix"
    assert payload["reference_count"] == 4
    assert payload["available_reference_count"] == 4
    assert payload["covered_file_count"] == 4
    assert payload["covered_rows"] == 400
    assert payload["covered_periods"] == 400
    assert payload["gaps"] == []
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert [entry["legacy_filename"] for entry in payload["coverage"]] == [
        "VUSK1L4.DAT",
        "VU14L1.DAT",
        "IMSVNSK1.DAT",
        "IMSVNR05.DAT",
    ]
    assert payload["coverage"][0]["start_period"] == 101
    assert payload["coverage"][0]["end_period"] == 200
    assert payload["coverage"][0]["period_count"] == 100
    assert payload["coverage"][0]["row_count"] == 100
    assert all(entry["legacy_source"] == "legacy_agrsich" for entry in payload["coverage"])
    assert all(entry["is_legacy_reference"] is True for entry in payload["coverage"])
    assert all(entry["covered"] is True for entry in payload["coverage"])
    assert payload["backlog"][0]["family"] == "insurer_stage_all"
    assert payload["backlog"][0]["available_files"] == ["VUSK1L4.DAT"]
    assert payload["backlog"][0]["covered_files"] == ["VUSK1L4.DAT"]
    assert "VUSK1L1.DAT" in payload["backlog"][0]["missing_files"]


def test_legacy_validation_coverage_matrix_reports_available_uncovered_reference(
    tmp_path: Path,
) -> None:
    data = json.loads((FIXTURE_DIR / "legacy_validation_bundle.json").read_text(encoding="utf-8"))
    data["targets"] = data["targets"][1:]
    for target in data["targets"]:
        target["legacy_path"] = str((FIXTURE_DIR / target["legacy_path"]).resolve())
    fixture_path = tmp_path / "partial_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    result = build_legacy_validation_coverage_matrix(
        fixture_path,
        reference_dir=FIXTURE_DIR / "../references/legacy_agrsich",
    )
    payload = result.to_dict()

    assert payload["status"] == "warning"
    assert payload["reference_count"] == 3
    assert payload["covered_rows"] == 300
    assert payload["gaps"] == [
        {
            "code": "legacy_reference_not_covered",
            "legacy_filename": "VUSK1L4.DAT",
            "legacy_path": str((FIXTURE_DIR / "../references/legacy_agrsich/VUSK1L4.DAT").resolve()),
            "message": "historical legacy reference is present but not covered by the fixture: VUSK1L4.DAT",
        }
    ]


def test_legacy_validation_coverage_matrix_excludes_writer_references(
    tmp_path: Path,
) -> None:
    data = {
        "targets": [
            {
                "subject_type": "insurer",
                "legacy_path": str((Path.cwd() / "tests/references/agrsich/imsvusk1.dat").resolve()),
                "export_filename": "imsvusk1.dat",
                "periods": [1],
                "level": "IV",
                "selector_kind": "all",
                "selector_value": "SK1",
            }
        ]
    }
    fixture_path = tmp_path / "writer_reference_bundle.json"
    fixture_path.write_text(json.dumps(data), encoding="utf-8")

    result = build_legacy_validation_coverage_matrix(fixture_path)
    payload = result.to_dict()

    assert payload["status"] == "warning"
    assert payload["reference_count"] == 0
    assert payload["covered_rows"] == 0
    assert payload["coverage"] == []
    assert payload["issues"][0]["code"] == "legacy_reference_excluded"
    assert Path(payload["excluded_reference_dirs"][0]).parts[-2:] == ("references", "agrsich")


def test_legacy_validation_coverage_matrix_cli_prints_stable_json(capsys) -> None:
    exit_code = main([str(FIXTURE_DIR / "legacy_validation_bundle.json")])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "legacy_agrsich_coverage_matrix"
    assert payload["covered_rows"] == 400
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_legacy_validation_coverage_matrix_cli_reports_errors_as_json(
    tmp_path: Path,
    capsys,
) -> None:
    missing_path = tmp_path / "missing_bundle.json"

    exit_code = main([str(missing_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"
    assert payload["issues"][0]["code"] == "legacy_validation_coverage_failed"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_legacy_validation_coverage_matrix_is_documented() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "## Legacy-Coverage-Matrix" in doc
    assert "python -m ims.model.legacy_validation_coverage tests/fixtures/legacy_validation_bundle.json" in doc
    assert 'mode =\n"legacy_agrsich_coverage_matrix"' in doc
    assert "Kuratierte Writer-Referenzen unter `tests/references/agrsich/`" in doc
    assert "behauptet keine historische Vollgleichheit" in doc
