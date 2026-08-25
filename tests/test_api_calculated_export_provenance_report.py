import json
from pathlib import Path

from ims.api.calculated_export_provenance_report import (
    build_calculated_export_provenance_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "legacy_validation_bundle.json"
MIGRATION_DOC = REPO_ROOT / "docs" / "migration" / "calculated_export_provenance_map.md"


def test_provenance_report_maps_complete_core_export_contract() -> None:
    report = build_calculated_export_provenance_report(REPO_ROOT)
    payload = report.to_dict()

    assert payload["status"] == "mapped"
    assert payload["report_contract_version"] == "pr71-v1"
    assert payload["required_export_count"] == 15
    assert payload["legacy_reference_count"] == 19
    assert payload["required_period_count"] == 6300
    assert payload["insurer_export_count"] == 5
    assert payload["policyholder_export_count"] == 10
    assert payload["writer_connected_count"] == 15
    assert payload["explicit_runner_connected_count"] == 15
    assert payload["independent_full_window_ready_count"] == 0
    assert payload["issues"] == []


def test_provenance_report_keeps_vusk1_windows_on_one_level_iv_identity() -> None:
    report = build_calculated_export_provenance_report(REPO_ROOT)
    by_filename = {item.filename: item for item in report.entries}
    sk1 = by_filename["imsvusk1.dat"]

    assert sk1.subject_type == "insurer"
    assert sk1.level == "IV"
    assert sk1.selector_kind == "all"
    assert sk1.selector_value == "SK1"
    assert sk1.period_start == 1
    assert sk1.period_end == 500
    assert sk1.required_period_count == 500
    assert sk1.target_count == 5
    assert sk1.legacy_references == (
        "VUSK1L1.DAT",
        "VUSK1L2.DAT",
        "VUSK1L3.DAT",
        "VUSK1L4.DAT",
        "VUSK1L5.DAT",
    )


def test_provenance_report_maps_six_vn_rules_to_existing_snapshot_runner() -> None:
    report = build_calculated_export_provenance_report(REPO_ROOT)
    rule_entries = [
        item
        for item in report.entries
        if item.subject_type == "policyholder" and item.level == "II"
    ]

    assert [item.filename for item in rule_entries] == [
        "imsvnr01.dat",
        "imsvnr02.dat",
        "imsvnr03.dat",
        "imsvnr04.dat",
        "imsvnr05.dat",
        "imsvnr06.dat",
    ]
    assert [item.rule_scope for item in rule_entries] == [
        "Vrvn01/compulsory",
        "Vrvn02/random",
        "Vrvn03/preference",
        "Vrvn04/search_history",
        "Vrvn05/sample_search",
        "Vrvn06/best_info",
    ]
    assert {
        item.python_state_runner_anchor for item in rule_entries
    } == {"ims.engine.vn_rule_runner.run_loaded_vn_settlement_period"}


def test_provenance_report_limits_existing_slice_evidence() -> None:
    report = build_calculated_export_provenance_report(REPO_ROOT)
    payload = report.to_dict()
    by_filename = {item.filename: item for item in report.entries}

    assert payload["explicit_output_evidence_count"] == 2
    assert payload["calculated_comparison_slice_count"] == 1
    assert by_filename["imsvu014.dat"].explicit_output_evidence_periods == (1, 2, 3, 4)
    assert by_filename["imsvu014.dat"].calculated_comparison_slice_periods == (1, 2, 3, 4)
    assert by_filename["imsvusk1.dat"].explicit_output_evidence_periods == (
        101,
        102,
        103,
        104,
    )
    assert by_filename["imsvusk1.dat"].calculated_comparison_slice_periods == ()
    assert all(not item.independent_state_evolution for item in report.entries)
    assert all(not item.independent_full_window_ready for item in report.entries)
    assert all(
        "independent_calculated_export_missing" in item.generation_gap_codes
        for item in report.entries
    )


def test_provenance_report_groups_exports_by_shared_state_path() -> None:
    report = build_calculated_export_provenance_report(REPO_ROOT)
    families = {item.name: item for item in report.state_families}

    assert families["insurer_state"].export_count == 5
    assert families["policyholder_state"].export_count == 10
    assert families["insurer_state"].next_slice == "imsvu014.dat periods 1-100"
    assert "imsvusk1.dat" in families["insurer_state"].export_filenames
    assert "imsvnr01.dat" in families["policyholder_state"].export_filenames
    assert "imsvnsk1.dat" in families["policyholder_state"].export_filenames


def test_provenance_report_rejects_missing_source_evidence(tmp_path: Path) -> None:
    report = build_calculated_export_provenance_report(
        tmp_path,
        fixture_path=FIXTURE,
    )

    assert report.status == "error"
    assert {issue.code for issue in report.issues} == {"source_evidence_missing"}


def test_provenance_report_cli_is_read_only(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "calculated_export_provenance_report"
    assert payload["status"] == "mapped"
    assert payload["production_release_approved"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["runner_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_provenance_plan_keeps_pr71_non_executing() -> None:
    plan = (REPO_ROOT / "docs" / "plans" / "calculated_export_provenance_plan.md").read_text(
        encoding="utf-8"
    )

    assert "15 Identitaeten" in plan
    assert "zwei" in plan and "Zustandsfamilien" in plan
    assert "VUSK1L1-5 bleiben fuenf Zeitfenster derselben Identitaet" in plan
    assert "kein Zugriff auf `incomming/`" in plan
    assert "kein Adapter-, Runner-, Scheduler-, Queue- oder Serverstart" in plan
    assert "keine neue Fachlogik" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan


def test_provenance_document_explains_map_and_rest_plan() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")
    migration_index = (REPO_ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert MIGRATION_DOC.is_file()
    for filename in (
        "imsvu014.dat",
        "imsvusk1.dat",
        "imsvnr01.dat",
        "imsvnr06.dat",
        "imsvnsk1.dat",
        "imsvnvk1.dat",
        "imsvnvk3.dat",
        "imsvuvk1.dat",
        "imsvuvk3.dat",
    ):
        assert filename in doc
    assert "VUSK1L1.DAT` bis `VUSK1L5.DAT" in doc
    assert "fuenf aufeinanderfolgende" in doc
    assert "Mindestserie" in doc and "PR 78" in doc
    assert "calculated_export_provenance_map.md" in migration_index
    assert "python -m ims.api.calculated_export_provenance_report --repo-root ." in readme
