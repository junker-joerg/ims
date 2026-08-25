import json
from pathlib import Path

from ims.api.production_release_corpus_report import (
    ProductionReleaseCorpusIssue,
    ProductionReleaseCorpusReport,
    ProductionReleaseEvidence,
    build_production_release_corpus_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_BUNDLE = REPO_ROOT / "tests" / "fixtures" / "legacy_validation_bundle.json"
REFERENCE_DIR = REPO_ROOT / "tests" / "references" / "legacy_agrsich"


def test_production_release_corpus_report_separates_coverage_from_release() -> None:
    payload = build_production_release_corpus_report(REPO_ROOT).to_dict()

    assert payload["status"] == "blocked"
    assert payload["mode"] == "production_release_corpus_report"
    assert payload["report_contract_version"] == "pr69-v1"
    assert payload["release_decision"] == "blocked_calculated_core_validation"
    assert payload["production_release_approved"] is False
    assert payload["reference_count"] == 19
    assert payload["available_reference_count"] == 19
    assert payload["covered_file_count"] == 19
    assert payload["covered_rows"] == 6300
    assert payload["covered_periods"] == 6300
    assert payload["coverage_complete"] is True
    assert payload["required_calculated_export_count"] == 15
    assert payload["supplied_calculated_export_count"] == 0
    assert payload["missing_calculated_export_count"] == 15
    assert len(payload["missing_calculated_exports"]) == 15
    assert payload["calculated_comparison_status"] == "blocked_input"
    assert payload["calculated_comparison_performed"] is False
    assert payload["calculated_core_validation_complete"] is False
    assert payload["operational_evidence_complete"] is True
    assert payload["reviewable_demo_evidence_complete"] is True
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["adapter_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_production_release_corpus_report_lists_expected_export_blockers() -> None:
    payload = build_production_release_corpus_report(REPO_ROOT).to_dict()

    assert payload["missing_calculated_exports"] == [
        "imsvnr01.dat (policyholder/II/rule=1)",
        "imsvnr02.dat (policyholder/II/rule=2)",
        "imsvnr03.dat (policyholder/II/rule=3)",
        "imsvnr04.dat (policyholder/II/rule=4)",
        "imsvnr05.dat (policyholder/II/rule=5)",
        "imsvnr06.dat (policyholder/II/rule=6)",
        "imsvnsk1.dat (policyholder/IV/all=SK1)",
        "imsvnvk1.dat (policyholder/III/rule_class=1)",
        "imsvnvk2.dat (policyholder/III/rule_class=2)",
        "imsvnvk3.dat (policyholder/III/rule_class=3)",
        "imsvu014.dat (insurer/I/entity=14)",
        "imsvusk1.dat (insurer/IV/all=SK1)",
        "imsvuvk1.dat (insurer/III/rule_class=1)",
        "imsvuvk2.dat (insurer/III/rule_class=2)",
        "imsvuvk3.dat (insurer/III/rule_class=3)",
    ]
    assert payload["issues"] == [
        {
            "code": "calculated_core_validation_incomplete",
            "severity": "blocker",
            "message": (
                "independent calculated core corpus validation is incomplete; "
                "15 required exports are missing"
            ),
            "path": str(CORE_BUNDLE),
        }
    ]


def test_production_release_corpus_report_blocks_missing_reference_inventory(tmp_path) -> None:
    empty_reference_dir = tmp_path / "legacy_agrsich"
    empty_reference_dir.mkdir()

    payload = build_production_release_corpus_report(
        REPO_ROOT,
        reference_dir=empty_reference_dir,
    ).to_dict()

    assert payload["status"] == "error"
    assert payload["release_decision"] == "blocked_invalid_evidence"
    assert payload["coverage_complete"] is False
    assert payload["available_reference_count"] == 0
    assert any(issue["code"] == "core_reference_coverage_incomplete" for issue in payload["issues"])
    assert payload["production_release_approved"] is False


def test_production_release_corpus_report_blocks_missing_operational_evidence(tmp_path) -> None:
    payload = build_production_release_corpus_report(
        tmp_path,
        fixture_path=CORE_BUNDLE,
        reference_dir=REFERENCE_DIR,
    ).to_dict()

    assert payload["status"] == "error"
    assert payload["coverage_complete"] is True
    assert payload["operational_evidence_complete"] is False
    assert payload["reviewable_demo_evidence_complete"] is False
    assert sum(issue["code"] == "operational_evidence_missing" for issue in payload["issues"]) == 6


def test_production_release_corpus_report_cli_prints_stable_json(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "blocked"
    assert payload["production_release_approved"] is False
    assert payload["missing_calculated_export_count"] == 15


def test_production_release_corpus_report_public_types_are_importable() -> None:
    assert ProductionReleaseCorpusReport.__name__ == "ProductionReleaseCorpusReport"
    assert ProductionReleaseCorpusIssue.__name__ == "ProductionReleaseCorpusIssue"
    assert ProductionReleaseEvidence.__name__ == "ProductionReleaseEvidence"
