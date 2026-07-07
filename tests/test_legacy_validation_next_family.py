import json
from pathlib import Path

from ims.model.legacy_validation_next_family import (
    LegacyValidationNextFamilyPlan,
    build_legacy_validation_next_family_plan,
    main,
)


FIXTURE_DIR = Path("tests/fixtures")
MIGRATION_DOC = Path("docs/migration/agrsich_validation_report.md")


def test_next_family_plan_reports_reference_blockers_for_current_bundle() -> None:
    result = build_legacy_validation_next_family_plan(FIXTURE_DIR / "legacy_validation_bundle.json")
    payload = result.to_dict()

    assert isinstance(result, LegacyValidationNextFamilyPlan)
    assert payload["status"] == "warning"
    assert payload["mode"] == "legacy_agrsich_next_family_plan"
    assert payload["available_reference_count"] == 13
    assert payload["covered_file_count"] == 13
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert {action["next_action"] for action in payload["actions"]} == {"await_historical_reference"}
    assert [action["family"] for action in payload["actions"]] == [
        "policyholder_class",
        "insurer_class",
        "parameter_output",
    ]
    assert {action["family"] for action in payload["actions"]}.isdisjoint({"policyholder_rule"})
    assert payload["actions"][0]["candidate_files"] == ["IMSVNVK*.DAT"]
    assert payload["actions"][0]["blocked_by"] == ["missing_historical_reference"]


def test_next_family_plan_selects_uncovered_available_reference(tmp_path: Path) -> None:
    reference_dir = tmp_path / "references" / "legacy_agrsich"
    reference_dir.mkdir(parents=True)
    covered_reference = reference_dir / "IMSVNR05.DAT"
    uncovered_reference = reference_dir / "IMSVNR06.DAT"
    covered_reference.write_text("placeholder\n", encoding="utf-8")
    uncovered_reference.write_text("placeholder\n", encoding="utf-8")
    fixture_path = tmp_path / "partial_bundle.json"
    fixture_path.write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "subject_type": "policyholder",
                        "legacy_path": str(covered_reference),
                        "export_filename": "imsvnr05.dat",
                        "periods": [1],
                        "level": "II",
                        "selector_kind": "rule",
                        "selector_value": 5,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = build_legacy_validation_next_family_plan(fixture_path, reference_dir=reference_dir)
    payload = result.to_dict()
    action_by_family = {action["family"]: action for action in payload["actions"]}

    assert payload["status"] == "ok"
    assert action_by_family["policyholder_rule"]["next_action"] == "add_to_validation_bundle"
    assert action_by_family["policyholder_rule"]["candidate_files"] == ["IMSVNR06.DAT"]
    assert action_by_family["policyholder_rule"]["blocked_by"] == []


def test_next_family_plan_keeps_warning_status_with_actionable_candidate(tmp_path: Path) -> None:
    reference_dir = tmp_path / "references" / "legacy_agrsich"
    writer_reference_dir = tmp_path / "references" / "agrsich"
    reference_dir.mkdir(parents=True)
    writer_reference_dir.mkdir(parents=True)
    covered_reference = reference_dir / "IMSVNR05.DAT"
    uncovered_reference = reference_dir / "IMSVNR06.DAT"
    writer_reference = writer_reference_dir / "imsvnr05.dat"
    covered_reference.write_text("placeholder\n", encoding="utf-8")
    uncovered_reference.write_text("placeholder\n", encoding="utf-8")
    writer_reference.write_text("placeholder\n", encoding="utf-8")
    fixture_path = tmp_path / "mixed_bundle.json"
    fixture_path.write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "subject_type": "policyholder",
                        "legacy_path": str(covered_reference),
                        "export_filename": "imsvnr05.dat",
                        "periods": [1],
                        "level": "II",
                        "selector_kind": "rule",
                        "selector_value": 5,
                    },
                    {
                        "subject_type": "policyholder",
                        "legacy_path": str(writer_reference),
                        "export_filename": "imsvnr05.dat",
                        "periods": [1],
                        "level": "II",
                        "selector_kind": "rule",
                        "selector_value": 5,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = build_legacy_validation_next_family_plan(fixture_path, reference_dir=reference_dir)
    payload = result.to_dict()
    action_by_family = {action["family"]: action for action in payload["actions"]}

    assert payload["status"] == "warning"
    assert payload["issues"][0]["code"] == "legacy_reference_excluded"
    assert action_by_family["policyholder_rule"]["next_action"] == "add_to_validation_bundle"
    assert action_by_family["policyholder_rule"]["candidate_files"] == ["IMSVNR06.DAT"]


def test_next_family_plan_propagates_coverage_errors(tmp_path: Path) -> None:
    missing_reference = tmp_path / "references" / "legacy_agrsich" / "MISSING.DAT"
    fixture_path = tmp_path / "bad_bundle.json"
    fixture_path.write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "subject_type": "insurer",
                        "legacy_path": str(missing_reference),
                        "export_filename": "missing.dat",
                        "periods": [1],
                        "level": "I",
                        "selector_kind": "entity",
                        "selector_value": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = build_legacy_validation_next_family_plan(
        fixture_path,
        reference_dir=tmp_path / "references" / "legacy_agrsich",
    )
    payload = result.to_dict()

    assert payload["status"] == "error"
    assert payload["issues"][0]["code"] == "legacy_reference_missing"


def test_next_family_plan_cli_prints_stable_json(capsys) -> None:
    exit_code = main([str(FIXTURE_DIR / "legacy_validation_bundle.json")])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "warning"
    assert payload["mode"] == "legacy_agrsich_next_family_plan"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_next_family_plan_is_documented() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "## Naechste Legacy-Dateifamilie" in doc
    assert "python -m ims.model.legacy_validation_next_family tests/fixtures/legacy_validation_bundle.json" in doc
    assert 'mode = "legacy_agrsich_next_family_plan"' in doc
    assert "keine Writer-Referenzen als historische Quellen" in doc
