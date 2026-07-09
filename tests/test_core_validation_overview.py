import json
from pathlib import Path

from ims.engine.core_validation_overview import (
    CoreCarryoverProbeContract,
    CoreExecutionSummaryContract,
    CoreValidationOverviewResult,
    build_carryover_probe_contract,
    build_execution_summary_contract,
    build_core_validation_overview,
    main,
)


FIXTURE_DIR = Path("tests/fixtures")
LEGACY_FIXTURE = FIXTURE_DIR / "legacy_validation_bundle.json"
VU14_PLAN = FIXTURE_DIR / "replay_vu14_period_plan.json"
VUSK1_PLAN = FIXTURE_DIR / "replay_vusk1_period_plan.json"
MIGRATION_DOC = Path("docs/migration/agrsich_validation_report.md")
RESUME_PLAN = Path("docs/plans/ims_core_fachlogik_resume_plan.md")


def test_core_validation_overview_combines_existing_read_only_diagnostics() -> None:
    result = build_core_validation_overview(
        legacy_fixture_path=LEGACY_FIXTURE,
        period_plan_paths=[VU14_PLAN, VUSK1_PLAN],
    )
    payload = result.to_dict()

    assert isinstance(result, CoreValidationOverviewResult)
    assert payload["status"] == "warning"
    assert payload["mode"] == "ims_core_validation_overview"
    assert payload["plan_count"] == 2
    assert payload["period_count"] == 8
    assert payload["global_periods"] == [1, 2, 3, 4, 101, 102, 103, 104]
    assert payload["legacy_reference_count"] == 19
    assert payload["legacy_covered_rows"] == 6300
    assert payload["legacy_covered_periods"] == 6300
    assert payload["next_validation_actions"] == ["await_historical_reference"]
    assert payload["execution_summary_available"] is False
    assert payload["execution_summary_next_action"] == "await_precomputed_execution_summary"
    assert payload["execution_summary_contract"]["mode"] == "explicit_multi_period_execution_summary_contract"
    assert payload["execution_summary_contract"]["summary_mode"] == "explicit_multi_period_execution_summary"
    assert payload["execution_summary_contract"]["overview_starts_runner"] is False
    assert payload["execution_summary_contract"]["overview_accepts_summary_input"] is False
    assert payload["execution_summary_contract"]["execution_performed"] is False
    assert payload["carryover_probe_available"] is False
    assert payload["carryover_probe_next_action"] == "provide_precomputed_carryover_probe"
    assert payload["carryover_probe_contract"]["mode"] == "explicit_transition_carryover_probe_contract"
    assert payload["carryover_probe_contract"]["probe_mode"] == "explicit_transition_carryover_probe"
    assert payload["carryover_probe_contract"]["overview_starts_probe"] is False
    assert payload["carryover_probe_contract"]["overview_accepts_probe_input"] is False
    assert payload["carryover_probe_contract"]["execution_performed"] is False
    assert payload["carryover_probe_contract"]["simulation_performed"] is False
    assert payload["period_diagnostics"]["mode"] == "explicit_period_diagnostics_bundle"
    assert payload["legacy_validation"]["mode"] == "legacy_agrsich_validation_overview"
    assert payload["coverage_matrix"]["mode"] == "legacy_agrsich_coverage_matrix"
    assert payload["next_family_plan"]["mode"] == "legacy_agrsich_next_family_plan"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_core_validation_overview_carryover_probe_contract_is_stable() -> None:
    contract = build_carryover_probe_contract()
    payload = contract.to_dict()

    assert isinstance(contract, CoreCarryoverProbeContract)
    assert payload["source_builder"] == (
        "ims.engine.explicit_transition_carryover_probe.probe_explicit_transition_carryover"
    )
    assert payload["required_fields"] == [
        "status",
        "mode",
        "plan_path",
        "transition_count",
        "vu_carryover_requested",
        "vn_carryover_requested",
        "in_memory_carryover_performed",
        "transitions",
        "issues",
        "writes_performed",
        "execution_performed",
        "simulation_performed",
        "automatic_historical_rule_selection_performed",
    ]
    assert payload["transition_fields"] == [
        "from_period",
        "to_period",
        "from_global_period",
        "to_global_period",
        "diagnostic_candidate_ids_match",
        "previous_result_source",
    ]
    assert payload["carryover_request_fields"] == [
        "vu_carryover_requested",
        "vn_carryover_requested",
        "vu_carryover_executed",
        "vn_carryover_executed",
    ]
    assert "carried_insurer_state" in payload["carried_entity_fields"]
    assert payload["boundary_fields"] == [
        "writes_performed",
        "execution_performed",
        "simulation_performed",
        "automatic_historical_rule_selection_performed",
    ]
    assert payload["next_action"] == "provide_precomputed_carryover_probe"
    assert payload["requires_precomputed_probe"] is True
    assert payload["overview_accepts_probe_input"] is False
    assert payload["overview_starts_probe"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False


def test_core_validation_overview_execution_summary_contract_is_stable() -> None:
    contract = build_execution_summary_contract()
    payload = contract.to_dict()

    assert isinstance(contract, CoreExecutionSummaryContract)
    assert payload["source_builder"] == (
        "ims.engine.explicit_period_runner.build_explicit_multi_period_execution_summary"
    )
    assert payload["required_fields"] == [
        "mode",
        "period_count",
        "processed_local_periods",
        "processed_global_periods",
        "total_vu_rule_applications",
        "total_vn_insurance_rule_applications",
        "total_vn_settlement_applications",
        "total_vn_damage_settlement_applications",
        "carryover_count",
        "vu_carryover_count",
        "vn_carryover_count",
        "written_file_count",
        "legacy_comparison_performed",
        "legacy_comparison_matches",
        "legacy_report_written_file_count",
        "writes_performed",
        "execution_performed",
        "automatic_historical_rule_selection_performed",
        "simulation_performed",
    ]
    assert payload["period_axis_fields"] == [
        "period_count",
        "processed_local_periods",
        "processed_global_periods",
    ]
    assert "total_vu_rule_applications" in payload["application_count_fields"]
    assert "vn_carryover_count" in payload["carryover_fields"]
    assert "legacy_comparison_matches" in payload["legacy_fields"]
    assert payload["boundary_fields"] == [
        "writes_performed",
        "execution_performed",
        "automatic_historical_rule_selection_performed",
        "simulation_performed",
    ]
    assert payload["next_action"] == "provide_precomputed_execution_summary"
    assert payload["requires_precomputed_summary"] is True
    assert payload["overview_starts_runner"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_core_validation_overview_propagates_period_diagnostic_errors(tmp_path: Path) -> None:
    missing_plan = tmp_path / "missing_period_plan.json"

    result = build_core_validation_overview(
        legacy_fixture_path=LEGACY_FIXTURE,
        period_plan_paths=[VU14_PLAN, missing_plan],
    )
    payload = result.to_dict()

    assert payload["status"] == "error"
    assert payload["period_diagnostics"]["error_plan_count"] == 1
    assert payload["issues"][0]["source"] == "period_diagnostics"
    assert payload["issues"][0]["code"] == "explicit_period_diagnostics_failed"
    assert not missing_plan.exists()


def test_core_validation_overview_threads_reference_dir_to_coverage_and_next_family(
    tmp_path: Path,
) -> None:
    reference_dir = tmp_path / "historical_refs" / "legacy_agrsich"
    reference_dir.mkdir(parents=True)
    covered_reference = reference_dir / "IMSVNR05.DAT"
    uncovered_reference = reference_dir / "IMSVNR06.DAT"
    covered_reference.write_text(
        Path("tests/references/legacy_agrsich/IMSVNR05.DAT").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    uncovered_reference.write_text(
        Path("tests/references/legacy_agrsich/IMSVNR05.DAT").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    fixture_path = tmp_path / "fixtures" / "legacy_validation_bundle.json"
    fixture_path.parent.mkdir()
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

    result = build_core_validation_overview(
        legacy_fixture_path=fixture_path,
        period_plan_paths=[VU14_PLAN],
        reference_dir=reference_dir,
    )
    payload = result.to_dict()
    action_by_family = {action["family"]: action for action in payload["next_family_plan"]["actions"]}

    assert payload["status"] == "warning"
    assert payload["reference_dir"] == str(reference_dir.resolve())
    assert payload["coverage_matrix"]["reference_dir"] == str(reference_dir.resolve())
    assert payload["coverage_matrix"]["gaps"][0]["legacy_filename"] == "IMSVNR06.DAT"
    assert action_by_family["policyholder_rule"]["next_action"] == "add_to_validation_bundle"
    assert action_by_family["policyholder_rule"]["candidate_files"] == ["IMSVNR06.DAT"]


def test_core_validation_overview_cli_prints_stable_json(capsys) -> None:
    exit_code = main(
        [
            "--legacy-fixture",
            str(LEGACY_FIXTURE),
            str(VU14_PLAN),
            str(VUSK1_PLAN),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "warning"
    assert payload["mode"] == "ims_core_validation_overview"
    assert payload["plan_count"] == 2
    assert payload["legacy_covered_rows"] == 6300
    assert payload["execution_summary_contract"]["next_action"] == "provide_precomputed_execution_summary"
    assert payload["carryover_probe_contract"]["next_action"] == "provide_precomputed_carryover_probe"
    assert payload["carryover_probe_contract"]["overview_starts_probe"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_core_validation_overview_cli_accepts_reference_dir(tmp_path: Path, capsys) -> None:
    reference_dir = tmp_path / "historical_refs" / "legacy_agrsich"
    reference_dir.mkdir(parents=True)
    reference_path = reference_dir / "IMSVNR05.DAT"
    reference_path.write_text(
        Path("tests/references/legacy_agrsich/IMSVNR05.DAT").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    fixture_path = tmp_path / "legacy_validation_bundle.json"
    fixture_path.write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "subject_type": "policyholder",
                        "legacy_path": str(reference_path),
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

    exit_code = main(
        [
            "--legacy-fixture",
            str(fixture_path),
            "--reference-dir",
            str(reference_dir),
            str(VU14_PLAN),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["reference_dir"] == str(reference_dir.resolve())
    assert payload["coverage_matrix"]["reference_dir"] == str(reference_dir.resolve())


def test_core_validation_overview_cli_returns_error_for_missing_plan(
    tmp_path: Path,
    capsys,
) -> None:
    missing_plan = tmp_path / "missing_period_plan.json"

    exit_code = main(["--legacy-fixture", str(LEGACY_FIXTURE), str(missing_plan)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"
    assert payload["period_diagnostics"]["error_plan_count"] == 1


def test_core_validation_overview_is_documented() -> None:
    migration_doc = MIGRATION_DOC.read_text(encoding="utf-8")
    resume_plan = RESUME_PLAN.read_text(encoding="utf-8")

    assert "## IMS-Kernvalidierungsueberblick" in migration_doc
    assert "python -m ims.engine.core_validation_overview" in migration_doc
    assert 'mode = "ims_core_validation_overview"' in migration_doc
    assert "`explicit_multi_period_execution_summary`-Payloads" in migration_doc
    assert "keine Summary-Datei entgegen" in migration_doc
    assert "Run-Control-Bruecke zum Kernblick" in migration_doc
    assert "ims.api.run_control_core_diagnostics_bridge.build_run_control_core_diagnostics_bridge" in migration_doc
    assert '"run_control_core_diagnostics_bridge"' in migration_doc
    assert "GET /api/run-control/core-diagnostics-bridge" in migration_doc
    assert "Run-Control-Kernblick-Bruecke" in migration_doc
    assert "keinen Startbutton, keinen Upload und keinen Ausfuehrungsadapter" in migration_doc
    assert "Aktualisierte PR-Restplanung" in resume_plan
    assert "IMS-Kernvalidierungsueberblick" in resume_plan
    assert "Execution-Summary-Vertrag" in resume_plan
    assert "Carryover-Probe-Vertrag" in migration_doc
    assert "explicit_transition_carryover_probe_contract" in migration_doc
    assert "GET /api/core-validation/carryover-probe-contract" in migration_doc
    assert "core_validation_carryover_probe_api_contract" in migration_doc
    assert "api_starts_probe = false" in migration_doc
    assert "provide_precomputed_carryover_probe" in migration_doc
    assert "keinen Probe aus dem Overview heraus" in migration_doc
    assert "keine Ausfuehrung aus dem Overview heraus" in resume_plan
