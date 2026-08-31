import json
from pathlib import Path

import pytest

import ims.api.historical_horizon_contract as contract_module
from ims.api.historical_horizon_contract import (
    CONTRACT_VERSION,
    LayeredExportTableSnapshot,
    build_historical_horizon_contract,
    main,
    validate_historical_horizon_prefixes,
)
from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportFileSpec,
    ExportRow,
    ExportTable,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_repeat_contract_freezes_fifteen_exports_and_three_row_counts() -> None:
    payload = build_historical_horizon_contract(root=REPO_ROOT).to_dict()

    assert payload["status"] == "ready"
    assert payload["contract_version"] == CONTRACT_VERSION
    assert payload["configured_horizons"] == [100, 300, 500]
    assert payload["configured_result_row_counts"] == [100, 300, 500]
    assert payload["prefix_checkpoints"] == [100, 300]
    assert payload["historical_periods_per_run"] == 100
    assert payload["historical_single_run_max_periods"] == 100
    assert payload["historical_result_numbering_formula"] == (
        "(run_index - 1) * run_period_count + local_period"
    )
    assert payload["required_export_count"] == 15
    assert payload["reference_target_count"] == 19
    assert payload["required_period_count"] == 6300
    assert payload["horizon_export_counts"] == {"100": 2, "300": 2, "500": 11}
    assert payload["reference_layer_status"] == "warning"
    assert payload["reference_layer_gate_decision"] == "go_separate_reference_tests"
    assert payload["issues"] == []
    assert payload["prefix_validation_available"] is False
    assert payload["modern_extension_prefix_validation_available"] is True
    assert payload["prefix_validation_performed"] is False
    assert payload["full_window_comparison_performed"] is False
    assert payload["legacy_bundle_changed"] is False
    assert payload["execution_performed"] is False
    assert payload["runner_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_run_identity_claimed"] is False
    assert payload["historical_300_500_single_run_claimed"] is False
    assert payload["historical_rng_reproduction_required"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False


def test_repeat_contract_assigns_expected_exports_to_each_result_row_count() -> None:
    contract = build_historical_horizon_contract(root=REPO_ROOT)
    exports_by_horizon = {
        horizon: {
            entry.filename
            for entry in contract.entries
            if entry.required_horizon == horizon
        }
        for horizon in contract.configured_horizons
    }

    assert exports_by_horizon[100] == {"imsvnsk1.dat", "imsvu014.dat"}
    assert exports_by_horizon[300] == {"imsvnr01.dat", "imsvnr02.dat"}
    assert exports_by_horizon[500] == {
        "imsvnr03.dat",
        "imsvnr04.dat",
        "imsvnr05.dat",
        "imsvnr06.dat",
        "imsvnvk1.dat",
        "imsvnvk2.dat",
        "imsvnvk3.dat",
        "imsvusk1.dat",
        "imsvuvk1.dat",
        "imsvuvk2.dat",
        "imsvuvk3.dat",
    }


def test_repeat_contract_maps_vusk1_blocks_to_five_runs_and_keeps_layers_separate() -> None:
    contract = build_historical_horizon_contract(root=REPO_ROOT)
    entry = _entry(contract, "imsvusk1.dat")

    assert entry.identity == ("insurer", "IV", "all", "SK1")
    assert entry.required_horizon == 500
    assert entry.required_run_count == 5
    assert entry.prefix_checkpoints == (100, 300)
    assert entry.layer_ids == ("wvemod2_archive", "vusk1l4_direct_04410ef")
    assert dict(entry.horizon_layer_ids) == {
        100: ("wvemod2_archive",),
        300: ("wvemod2_archive", "vusk1l4_direct_04410ef"),
        500: ("wvemod2_archive", "vusk1l4_direct_04410ef"),
    }
    assert entry.allowed_claims == (
        "archive_content_match_only",
        "versioned_fixture_regression_only",
    )
    assert [item.reference_filename for item in entry.reference_slices] == [
        "VUSK1L5.DAT",
        "VUSK1L4.DAT",
        "VUSK1L3.DAT",
        "VUSK1L2.DAT",
        "VUSK1L1.DAT",
    ]
    assert [
        (item.period_start, item.period_end) for item in entry.reference_slices
    ] == [(1, 100), (101, 200), (201, 300), (301, 400), (401, 500)]
    assert [item.run_start for item in entry.reference_slices] == [1, 2, 3, 4, 5]
    assert [item.run_end for item in entry.reference_slices] == [1, 2, 3, 4, 5]
    assert all(item.local_period_start == 1 for item in entry.reference_slices)
    assert all(item.local_period_end == 100 for item in entry.reference_slices)
    assert entry.reference_slices[1].coherence_class == (
        "contradictory_or_unresolved"
    )
    assert entry.reference_slices[1].allowed_claim == (
        "versioned_fixture_regression_only"
    )


def test_prefix_validation_accepts_exact_100_300_500_snapshots() -> None:
    contract = build_historical_horizon_contract(root=REPO_ROOT)
    entry = _entry(contract, "imsvusk1.dat")
    snapshots = tuple(_snapshot(entry, horizon) for horizon in (100, 300, 500))

    payload = validate_historical_horizon_prefixes(contract, snapshots).to_dict()

    assert payload["status"] == "ok"
    assert payload["snapshot_count"] == 3
    assert payload["comparison_count"] == 3
    assert payload["compared_row_count"] == 500
    assert payload["one_hundred_prefix_comparison_count"] == 2
    assert payload["prefix_stable"] is True
    assert payload["comparison_is_exact"] is True
    assert payload["mode"] == "modern_extension_prefix_validation"
    assert payload["historical_repeat_relationship_claimed"] is False
    assert payload["tolerance_applied"] is False
    assert payload["issues"] == []
    assert payload["execution_performed"] is False
    assert payload["runner_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_prefix_validation_rejects_changed_early_period() -> None:
    contract = build_historical_horizon_contract(root=REPO_ROOT)
    entry = _entry(contract, "imsvusk1.dat")
    snapshots = [_snapshot(entry, horizon) for horizon in (100, 300, 500)]
    snapshots[-1].table.rows[49].values[1] = -1

    payload = validate_historical_horizon_prefixes(contract, snapshots).to_dict()

    assert payload["status"] == "error"
    assert {
        (issue["code"], issue["path"]) for issue in payload["issues"]
    } == {("prefix_row_mismatch", "imsvusk1.dat@500")}
    assert "period 50" in payload["issues"][0]["message"]


def test_prefix_validation_requires_intermediate_checkpoint() -> None:
    contract = build_historical_horizon_contract(root=REPO_ROOT)
    entry = _entry(contract, "imsvusk1.dat")
    snapshots = (_snapshot(entry, 100), _snapshot(entry, 500))

    payload = validate_historical_horizon_prefixes(contract, snapshots).to_dict()

    assert payload["status"] == "error"
    assert payload["comparison_count"] == 1
    assert payload["compared_row_count"] == 100
    assert payload["issues"] == [
        {
            "code": "prefix_checkpoint_missing",
            "path": "imsvusk1.dat@500",
            "message": "required prefix snapshot is missing: 300",
        }
    ]


def test_prefix_validation_rejects_empty_snapshot_set() -> None:
    contract = build_historical_horizon_contract(root=REPO_ROOT)

    payload = validate_historical_horizon_prefixes(contract, ()).to_dict()

    assert payload["status"] == "error"
    assert payload["issues"] == [
        {
            "code": "extended_snapshot_missing",
            "path": contract.fixture_path,
            "message": "prefix validation requires at least one extended snapshot",
        }
    ]


def test_horizon_snapshot_accepts_canonical_level_iv_all_alias() -> None:
    contract = build_historical_horizon_contract(root=REPO_ROOT)
    entry = _entry(contract, "imsvnsk1.dat")
    snapshot = _snapshot(entry, 100)
    snapshot.table.spec.selector_value = "all"

    payload = validate_historical_horizon_prefixes(
        contract,
        (snapshot,),
    ).to_dict()

    assert "snapshot_identity_mismatch" not in {
        issue["code"] for issue in payload["issues"]
    }


def test_prefix_validation_rejects_wrong_layers_and_period_boundaries() -> None:
    contract = build_historical_horizon_contract(root=REPO_ROOT)
    entry = _entry(contract, "imsvusk1.dat")
    wrong_layers = _snapshot(entry, 300, layer_ids=("wvemod2_archive",))
    wrong_periods = _snapshot(entry, 500)
    wrong_periods.table.rows[0].values[0] = 0

    payload = validate_historical_horizon_prefixes(
        contract,
        (_snapshot(entry, 100), wrong_layers, wrong_periods),
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert issue_codes == {
        "snapshot_layer_ids_mismatch",
        "snapshot_period_boundary_mismatch",
    }


def test_horizon_contract_rejects_missing_or_unsorted_horizons() -> None:
    missing = build_historical_horizon_contract(
        root=REPO_ROOT,
        configured_horizons=(100, 500),
    ).to_dict()
    unsorted = build_historical_horizon_contract(
        root=REPO_ROOT,
        configured_horizons=(300, 100, 500),
    ).to_dict()

    assert missing["status"] == "error"
    assert "required_horizon_not_configured" in {
        issue["code"] for issue in missing["issues"]
    }
    assert unsorted["status"] == "error"
    assert "configured_horizons_invalid" in {
        issue["code"] for issue in unsorted["issues"]
    }


def test_repeat_contract_rejects_missing_historical_numbering_anchor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        contract_module,
        "HISTORICAL_RESULT_NUMBERING_NEEDLE",
        "missing-result-numbering-formula",
    )

    payload = build_historical_horizon_contract(root=REPO_ROOT).to_dict()

    assert payload["status"] == "error"
    assert "historical_result_numbering_anchor_missing" in {
        issue["code"] for issue in payload["issues"]
    }


def test_horizon_contract_cli_is_read_only(capsys) -> None:
    exit_code = main(["--root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "historical_repeat_corpus_contract"
    assert payload["status"] == "ready"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["runner_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def _entry(contract, filename: str):
    return next(entry for entry in contract.entries if entry.filename == filename)


def _snapshot(entry, horizon: int, *, layer_ids=None) -> LayeredExportTableSnapshot:
    header = INSURER_HEADER if entry.subject_type == "insurer" else POLICYHOLDER_HEADER
    table = ExportTable(
        spec=ExportFileSpec(
            filename=entry.filename,
            subject_type=entry.subject_type,
            level=entry.level,
            selector_kind=entry.selector_kind,
            selector_value=entry.selector_value,
        ),
        header=header,
        rows=[ExportRow(values=[period, float(period)]) for period in range(1, horizon + 1)],
    )
    return LayeredExportTableSnapshot(
        horizon=horizon,
        layer_ids=(
            dict(entry.horizon_layer_ids)[horizon]
            if layer_ids is None
            else layer_ids
        ),
        table=table,
    )
