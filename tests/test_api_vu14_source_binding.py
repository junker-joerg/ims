import json
from pathlib import Path

from ims.api.vu14_source_binding import build_vu14_source_binding_report, main


REPO_ROOT = Path(__file__).resolve().parent.parent
BINDING_PATH = REPO_ROOT / "tests" / "fixtures" / "vu14_vdefmd6_source_binding.json"
MIGRATION_DOC = REPO_ROOT / "docs" / "migration" / "vu14_vdefmd6_source_binding.md"


def _binding_data() -> dict:
    return json.loads(BINDING_PATH.read_text(encoding="utf-8"))


def test_vu14_source_binding_maps_vdefmd6_target() -> None:
    payload = build_vu14_source_binding_report(REPO_ROOT).to_dict()

    assert payload["status"] == "source_bound"
    assert payload["source_binding_version"] == "pr73-v1"
    assert payload["model_id"] == "Vdefmd6"
    assert payload["target"] == {
        "subject_type": "insurer",
        "level": "I",
        "selector_kind": "entity",
        "selector_value": 14,
        "rule_id": 6,
        "rule_class": 2,
        "export_filename": "imsvu014.dat",
        "period_start": 1,
        "period_end": 100,
    }
    assert payload["source_anchor_count"] == 9
    assert payload["source_binding_ready"] is True
    assert payload["issues"] == []


def test_vu14_source_binding_closes_only_four_origin_groups() -> None:
    payload = build_vu14_source_binding_report(REPO_ROOT).to_dict()

    assert payload["evidenced_requirement_codes"] == [
        "complete_population_origin",
        "initial_state_origin",
        "vu14_rule_schedule_origin",
        "state_transition_origin",
    ]
    assert payload["open_requirement_codes"] == [
        "rng_stream_origin",
        "policyholder_claim_origin",
    ]
    assert payload["generation_ready"] is False
    assert payload["independent_full_window_ready"] is False


def test_vu14_source_binding_generates_period_one_before_comparison() -> None:
    payload = build_vu14_source_binding_report(REPO_ROOT).to_dict()
    comparison = payload["period_one_comparison"]

    assert comparison == {
        "period": 1,
        "export_filename": "imsvu014.dat",
        "matches": True,
        "matched_field_count": 14,
        "compared_field_count": 14,
        "state_origin": "Vdefmd6_initialization",
        "legacy_read_after_generation": True,
    }
    assert payload["independent_period_one_ready"] is True
    assert payload["writes_performed"] is False
    assert payload["runner_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_vu14_source_binding_rejects_rule_drift(tmp_path: Path) -> None:
    binding = _binding_data()
    binding["vu14"]["rule_id"] = 14
    path = tmp_path / "bad_binding.json"
    path.write_text(json.dumps(binding), encoding="utf-8")

    report = build_vu14_source_binding_report(REPO_ROOT, binding_path=path)

    assert report.status == "error"
    assert "vu14_identity_mismatch" in {issue.code for issue in report.issues}


def test_vu14_source_binding_rejects_reference_hash_drift(tmp_path: Path) -> None:
    binding = _binding_data()
    binding["reference"]["normalized_sha256"] = "0" * 64
    path = tmp_path / "bad_hash.json"
    path.write_text(json.dumps(binding), encoding="utf-8")

    report = build_vu14_source_binding_report(REPO_ROOT, binding_path=path)

    assert report.status == "error"
    assert "reference_hash_mismatch" in {issue.code for issue in report.issues}


def test_vu14_source_binding_cli_is_read_only(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "source_bound"
    assert payload["independent_period_one_ready"] is True
    assert payload["simulation_performed"] is False


def test_vu14_source_binding_documents_conflict_and_remaining_boundary() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "IMS.E:4602-4605" in doc
    assert "151-190" in doc and "191-200" in doc
    assert "151-180" in doc and "181-200" in doc
    assert "9cf9f137" in doc
    assert "keine historische Vollgleichheit" in doc
    assert "Perioden 2-100" in doc
