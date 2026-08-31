import json
import shutil
from dataclasses import replace
from pathlib import Path

from ims.api.historical_reference_layer_contract import (
    COHERENCE_CLASSES,
    CONTRACT_VERSION,
    LAYER_DEFINITIONS,
    REFERENCE_LAYER_BINDINGS,
    HistoricalReferenceLayerContractResult,
    build_historical_reference_layer_contract,
    main,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCE_DIR = REPO_ROOT / "tests" / "references" / "legacy_agrsich"


def test_layer_contract_verifies_nineteen_targets_in_four_separate_layers() -> None:
    payload = build_historical_reference_layer_contract(root=REPO_ROOT).to_dict()
    target_counts_by_layer = {
        layer_id: sum(target["layer_id"] == layer_id for target in payload["targets"])
        for layer_id in {target["layer_id"] for target in payload["targets"]}
    }

    assert payload["status"] == "warning"
    assert payload["contract_version"] == CONTRACT_VERSION
    assert payload["target_count"] == 19
    assert payload["verified_target_count"] == 19
    assert payload["layer_count"] == 4
    assert payload["coherence_class_counts"] == {
        "same_run_proven": 0,
        "archive_family_only": 18,
        "mixed_reference_layers": 0,
        "contradictory_or_unresolved": 1,
    }
    assert payload["corpus_coherence_class"] == "mixed_reference_layers"
    assert payload["same_run_proven_target_count"] == 0
    assert payload["unresolved_historical_origin_target_count"] == 1
    assert payload["separated_unresolved_target_count"] == 1
    assert payload["gate_decision"] == "go_separate_reference_tests"
    assert payload["full_window_phase_allowed"] is True
    assert payload["separate_reference_tests_required"] is True
    assert target_counts_by_layer == {
        "zins000_archive": 2,
        "wvemod1_archive": 12,
        "wvemod2_archive": 4,
        "vusk1l4_direct_04410ef": 1,
    }
    assert payload["issues"] == [
        {
            "code": "historical_origin_unresolved",
            "severity": "warning",
            "path": "vusk1l4_direct_04410ef",
            "message": (
                "historical origin remains unresolved; the layer is isolated "
                "for versioned fixture regression only"
            ),
        }
    ]


def test_layer_contract_keeps_vusk1_windows_on_level_iv_and_l4_isolated() -> None:
    payload = build_historical_reference_layer_contract(root=REPO_ROOT).to_dict()
    targets = {target["reference_filename"]: target for target in payload["targets"]}
    windows = [target for filename, target in targets.items() if filename.startswith("VUSK1L")]
    l4 = targets["VUSK1L4.DAT"]

    assert len(windows) == 5
    assert {target["level"] for target in windows} == {"IV"}
    assert {target["selector_kind"] for target in windows} == {"all"}
    assert {target["selector_value"] for target in windows} == {"SK1"}
    assert l4["layer_id"] == "vusk1l4_direct_04410ef"
    assert l4["source_kind"] == "versioned_direct_reference"
    assert l4["source_path"] == "tests/references/legacy_agrsich/VUSK1L4.DAT"
    assert l4["coherence_class"] == "contradictory_or_unresolved"
    assert l4["historical_origin_status"] == "historical_run_and_archive_unresolved"
    assert l4["allowed_claim"] == "versioned_fixture_regression_only"
    assert l4["archive_comparison_classification"] == "same_name_divergent"
    assert l4["matching_basis"] == "versioned_reference_sha256"
    assert l4["separated_for_reference_testing"] is True
    assert l4["same_run_claim_allowed"] is False
    assert payload["coherent_vusk1_500_period_archive_source_claimed"] is False


def test_layer_contract_records_archive_hashes_and_absent_run_metadata() -> None:
    payload = build_historical_reference_layer_contract(root=REPO_ROOT).to_dict()
    layers = {layer["layer_id"]: layer for layer in payload["layers"]}

    assert layers["zins000_archive"]["source_sha256"] == (
        "5839ddea724949e9e1065a4d9f1ac3f27e97c2ed444d819f466f3cd4ee97f190"
    )
    assert layers["wvemod1_archive"]["source_sha256"] == (
        "444c0bddf7a0dcee21e963167c36da56ed9b0a33172487914adf51e2a91206d9"
    )
    assert layers["wvemod2_archive"]["source_sha256"] == (
        "d17f399139ced0c85db424aac46b585ee40f2d98eb84da43b3d5790d445c3eae"
    )
    for layer_id in ("zins000_archive", "wvemod1_archive", "wvemod2_archive"):
        assert layers[layer_id]["coherence_class"] == "archive_family_only"
        assert layers[layer_id]["run_metadata_status"] == "metadata_absent"
        assert layers[layer_id]["allowed_claim"] == "archive_content_match_only"
        assert layers[layer_id]["evidence_contracts"] == ["pr89-v1", "pr90-v1"]


def test_layer_contract_rejects_missing_and_changed_versioned_references(
    tmp_path: Path,
) -> None:
    reference_dir = tmp_path / "references"
    shutil.copytree(REFERENCE_DIR, reference_dir)
    (reference_dir / "IMSVNR01.DAT").unlink()
    with (reference_dir / "IMSVNR02.DAT").open("ab") as handle:
        handle.write(b"\n")

    payload = build_historical_reference_layer_contract(
        root=tmp_path,
        reference_dir=reference_dir,
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["verified_target_count"] == 17
    assert payload["gate_decision"] == "blocked_contract_invalid"
    assert payload["full_window_phase_allowed"] is False
    assert "reference_missing" in issue_codes
    assert "reference_hash_mismatch" in issue_codes


def test_layer_contract_rejects_same_run_claim_without_local_report() -> None:
    layers = (
        replace(LAYER_DEFINITIONS[0], coherence_class="same_run_proven"),
        *LAYER_DEFINITIONS[1:],
    )

    payload = build_historical_reference_layer_contract(
        root=REPO_ROOT,
        layers=layers,
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["gate_decision"] == "blocked_contract_invalid"
    assert payload["full_window_phase_allowed"] is False
    assert "same_run_metadata_missing" in issue_codes
    assert "target_binding_invalid" in issue_codes


def test_layer_contract_blocks_unseparated_unresolved_layer() -> None:
    layers = (
        *LAYER_DEFINITIONS[:-1],
        replace(LAYER_DEFINITIONS[-1], separated_for_reference_testing=False),
    )

    payload = build_historical_reference_layer_contract(
        root=REPO_ROOT,
        layers=layers,
    ).to_dict()

    assert payload["status"] == "error"
    assert payload["gate_decision"] == "blocked_contract_invalid"
    assert payload["full_window_phase_allowed"] is False
    assert "unresolved_layer_not_separated" in {
        issue["code"] for issue in payload["issues"]
    }


def test_layer_contract_rejects_duplicate_target_binding() -> None:
    payload = build_historical_reference_layer_contract(
        root=REPO_ROOT,
        bindings=(*REFERENCE_LAYER_BINDINGS, REFERENCE_LAYER_BINDINGS[0]),
    ).to_dict()

    assert payload["status"] == "error"
    assert payload["gate_decision"] == "blocked_contract_invalid"
    assert "target_binding_duplicate" in {
        issue["code"] for issue in payload["issues"]
    }


def test_layer_contract_cli_reports_warning_without_execution(capsys) -> None:
    exit_code = main(["--root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "historical_reference_layer_contract"
    assert payload["status"] == "warning"
    assert payload["prior_evidence_reused"] is True
    assert payload["source_archives_read"] is False
    assert payload["legacy_bundle_changed"] is False
    assert payload["files_extracted"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["seed_transferred_between_archives"] is False
    assert payload["historical_run_identity_claimed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False
    assert COHERENCE_CLASSES == (
        "same_run_proven",
        "archive_family_only",
        "mixed_reference_layers",
        "contradictory_or_unresolved",
    )
    assert HistoricalReferenceLayerContractResult is not None
