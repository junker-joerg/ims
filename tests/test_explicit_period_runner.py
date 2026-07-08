import json
from pathlib import Path

import pytest

import ims.engine.explicit_period_runner as explicit_period_runner
from ims.engine.explicit_period_runner import (
    ExplicitLegacyTarget,
    ExplicitMultiPeriodRunResult,
    ExplicitPeriodCarryover,
    ExplicitPeriodRunResult,
    build_explicit_multi_period_execution_summary,
    run_explicit_multi_period_from_fixture,
    run_explicit_multi_period_from_mappings,
    run_explicit_period_from_mapping,
)


def _free_linear_parameters() -> dict[str, list[float]]:
    return {
        "premium_intercept_normal": [0.0, 0.0],
        "premium_factor_normal": [2.0, 2.0],
        "advertising_intercept_normal": [0.0, 0.0],
        "advertising_factor_normal": [1.0, 1.0],
        "premium_intercept_shock": [0.0, 0.0],
        "premium_factor_shock": [1.0, 1.0],
        "advertising_intercept_shock": [0.0, 0.0],
        "advertising_factor_shock": [1.0, 1.0],
    }


def _damage_parameters() -> dict[str, list[float]]:
    return {
        "damage_intercept_normal": [5.0, 7.0],
        "damage_factor_normal": [2.0, 3.0],
        "damage_intercept_shock": [50.0, 70.0],
        "damage_factor_shock": [20.0, 30.0],
    }


def _compulsory_insurance_rule_snapshot(*, policyholder_id: int = 21) -> dict:
    return {
        "policyholder_id": policyholder_id,
        "rule_kind": "compulsory",
        "active_insurer_ids": [11],
        "draws": {"insurer_choice_draws": [0.0, 0.0]},
    }


def _scenario(period: int, *, policyholder_id: int = 21) -> dict:
    return {
        "context": {"period": period, "max_periods": 12, "run_index": 0, "rng_seed": 1000 + period},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": 11,
                "name": "VU-11",
                "rule_id": 1,
                "rule_class": 1,
                "premiums_current_sector": [4.0, 6.0],
                "advertising_current_sector": [1.0, 1.0],
                "reserves_current": [40.0, 60.0],
                "policyholders_current_sector": [1.0, 2.0],
                "claims_count_current": [0, 0],
                "claims_sum_current": [0.0, 0.0],
            }
        ],
        "policyholders": [
            {
                "entity_id": policyholder_id,
                "name": f"VN-{policyholder_id}",
                "rule_id": 5,
                "rule_class": 1,
            }
        ],
        "vu_free_linear_rule_snapshots": [
            {
                "insurer_id": 11,
                "interest_rate": 0.0,
                "parameters": _free_linear_parameters(),
            }
        ],
        "vn_damage_settlement_snapshots": [
            {
                "policyholder_id": policyholder_id,
                "previous_wealth": 100.0,
                "damage_thresholds": [0.8, 0.2],
                "parameters": _damage_parameters(),
                "draws": {
                    "trigger_draws": [0.1, 0.5],
                    "amount_draws": [2.0, 3.0],
                },
                "insurance_decisions": [
                    {"sector_index": 0, "insured": True, "insurer_id": 11},
                    {"sector_index": 1, "insured": False},
                ],
            }
        ],
    }


def _non_empty_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_explicit_period_applies_vu_before_vn_and_writes_export(tmp_path: Path) -> None:
    result = run_explicit_period_from_mapping(_scenario(2), output_dir=tmp_path)

    assert isinstance(result, ExplicitPeriodRunResult)
    assert len(result.vu_result.free_linear_applications) == 1
    assert result.vn_result.total_damage_settlement_applications == 1

    insurer = result.vn_result.insurers[0]
    policyholder = result.vn_result.policyholders[0]
    assert insurer.premiums_current_sector == pytest.approx([8.0, 12.0])
    assert insurer.reserves_current == pytest.approx([39.0, 60.0])
    assert insurer.policyholders_current_sector == pytest.approx([2.0, 2.0])
    assert policyholder.paid_premium_current == pytest.approx([8.0, 0.0])
    assert policyholder.claim_sum_current == pytest.approx([9.0, 0.0])

    lines = _non_empty_lines(tmp_path / "imsvu011.dat")
    assert lines[1].split() == [
        "2",
        "8.0",
        "1.0",
        "39.0",
        "2.0",
        "1",
        "9.0",
        "12.0",
        "1.0",
        "60.0",
        "2.0",
        "0",
        "0.0",
    ]


def test_explicit_period_uses_vn_rule_dispatch_for_damage_settlement(tmp_path: Path) -> None:
    scenario = _scenario(2)
    scenario["vn_insurance_rule_snapshots"] = [_compulsory_insurance_rule_snapshot()]
    del scenario["vn_damage_settlement_snapshots"][0]["insurance_decisions"]

    result = run_explicit_period_from_mapping(scenario, output_dir=tmp_path)

    assert len(result.vn_result.insurance_rule_applications) == 1
    assert result.vn_result.total_damage_settlement_applications == 1
    insurer = result.vn_result.insurers[0]
    policyholder = result.vn_result.policyholders[0]
    assert insurer.reserves_current == pytest.approx([39.0, 72.0])
    assert insurer.policyholders_current_sector == pytest.approx([2.0, 3.0])
    assert policyholder.paid_premium_current == pytest.approx([8.0, 12.0])
    assert policyholder.end_wealth_current == pytest.approx(71.0)

    lines = _non_empty_lines(tmp_path / "imsvu011.dat")
    assert lines[1].split() == [
        "2",
        "8.0",
        "1.0",
        "39.0",
        "2.0",
        "1",
        "9.0",
        "12.0",
        "1.0",
        "72.0",
        "3.0",
        "0",
        "0.0",
    ]


def test_explicit_multi_period_counts_vu_and_vn_applications(tmp_path: Path) -> None:
    first = _scenario(2)
    second = _scenario(3, policyholder_id=22)
    first["vn_insurance_rule_snapshots"] = [_compulsory_insurance_rule_snapshot(policyholder_id=21)]
    second["vn_insurance_rule_snapshots"] = [_compulsory_insurance_rule_snapshot(policyholder_id=22)]

    result = run_explicit_multi_period_from_mappings(
        [first, second],
        output_dir=tmp_path,
    )

    assert isinstance(result, ExplicitMultiPeriodRunResult)
    assert result.processed_periods == [2, 3]
    assert result.processed_local_periods == [2, 3]
    assert result.processed_global_periods == [2, 3]
    assert result.total_vu_rule_applications == 2
    assert result.total_vn_insurance_rule_applications == 2
    assert [
        len(period_result.vn_result.insurance_rule_applications)
        for period_result in result.period_results
    ] == [1, 1]
    assert result.total_vn_settlement_applications == 2
    assert result.total_vn_damage_settlement_applications == 2
    assert {path.name for path in result.written_files} >= {"imsvu011.dat", "imsvnr05.dat"}


def test_explicit_multi_period_execution_summary_reports_controlled_path(tmp_path: Path) -> None:
    first = _scenario(2)
    second = _scenario(3)
    first["vn_insurance_rule_snapshots"] = [_compulsory_insurance_rule_snapshot()]
    second["vn_insurance_rule_snapshots"] = [_compulsory_insurance_rule_snapshot()]

    result = run_explicit_multi_period_from_mappings(
        [first, second],
        output_dir=tmp_path,
        carry_forward_vu_state=True,
        carry_forward_vn_state=True,
    )

    payload = build_explicit_multi_period_execution_summary(result).to_dict()

    assert payload["mode"] == "explicit_multi_period_execution_summary"
    assert payload["period_count"] == 2
    assert payload["processed_local_periods"] == [2, 3]
    assert payload["processed_global_periods"] == [2, 3]
    assert payload["total_vu_rule_applications"] == 2
    assert payload["total_vn_insurance_rule_applications"] == 2
    assert payload["total_vn_damage_settlement_applications"] == 2
    assert payload["carryover_count"] == 1
    assert payload["vu_carryover_count"] == 1
    assert payload["vn_carryover_count"] == 1
    assert payload["written_file_count"] == len(result.written_files)
    assert payload["legacy_comparison_performed"] is False
    assert payload["legacy_comparison_matches"] is None
    assert payload["writes_performed"] is True
    assert payload["execution_performed"] is True
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["simulation_performed"] is False


def test_explicit_multi_period_can_carry_forward_vn_state() -> None:
    result = run_explicit_multi_period_from_mappings(
        [_scenario(2), _scenario(3)],
        carry_forward_vn_state=True,
    )

    assert len(result.carryovers) == 1
    assert isinstance(result.carryovers[0], ExplicitPeriodCarryover)
    assert result.carryovers[0].vn_carryover is not None
    assert result.carryovers[0].vn_carryover.policyholder_ids == [21]
    assert result.period_results[1].vn_result.insurers[0].policyholders_current_sector == pytest.approx([3.0, 2.0])


def test_explicit_multi_period_carryover_reports_global_periods() -> None:
    first = _scenario(2)
    second = _scenario(2)
    second["context"]["run_index"] = 1

    result = run_explicit_multi_period_from_mappings(
        [first, second],
        carry_forward_vu_state=True,
        carry_forward_vn_state=True,
    )

    assert result.processed_periods == [2, 14]
    assert result.processed_local_periods == [2, 2]
    assert result.processed_global_periods == [2, 14]
    assert len(result.carryovers) == 1
    carryover = result.carryovers[0]
    assert carryover.from_period == 2
    assert carryover.to_period == 2
    assert carryover.from_global_period == 2
    assert carryover.to_global_period == 14
    assert carryover.vu_carryover is not None
    assert carryover.vu_carryover.from_global_period == 2
    assert carryover.vu_carryover.to_global_period == 14
    assert carryover.vn_carryover is not None


def test_explicit_multi_period_rejects_duplicate_or_unsorted_periods() -> None:
    with pytest.raises(ValueError, match="duplicate periods"):
        run_explicit_multi_period_from_mappings([_scenario(2), _scenario(2, policyholder_id=22)])

    with pytest.raises(ValueError, match="increasing periods"):
        run_explicit_multi_period_from_mappings([_scenario(3), _scenario(2, policyholder_id=22)])


def test_explicit_multi_period_fixture_supports_boolean_carryover_flags(tmp_path: Path) -> None:
    fixture_path = tmp_path / "explicit_periods.json"
    fixture_path.write_text(
        json.dumps(
            {
                "carry_forward_vn_state": True,
                "periods": [_scenario(2), _scenario(3)],
            }
        ),
        encoding="utf-8",
    )

    result = run_explicit_multi_period_from_fixture(fixture_path)

    assert len(result.carryovers) == 1
    assert result.carryovers[0].vn_carryover is not None


def test_explicit_multi_period_fixture_rejects_non_boolean_carryover_flags(tmp_path: Path) -> None:
    fixture_path = tmp_path / "bad_explicit_periods.json"
    fixture_path.write_text(
        json.dumps({"carry_forward_vu_state": "false", "periods": [_scenario(2)]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="carry_forward_vu_state must be a boolean"):
        run_explicit_multi_period_from_fixture(fixture_path)


def test_explicit_multi_period_compares_insurer_legacy_target(tmp_path: Path) -> None:
    legacy_path = tmp_path / "reference_imsvu011.dat"
    legacy_path.write_text(
        "\n".join(
            [
                "#t Pr1 Wer1 Rs1 Vn1 Sc1 Sh1 Pr2 Wer2 Rs2 Vn2 Sc2 Sh2",
                "2 8.0 1.0 39.0 2.0 1 9.0 12.0 1.0 60.0 2.0 0 0.0",
                "3 8.0 1.0 39.0 2.0 1 9.0 12.0 1.0 60.0 2.0 0 0.0",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_explicit_multi_period_from_mappings(
        [_scenario(2), _scenario(3, policyholder_id=22)],
        output_dir=tmp_path / "out",
        legacy_targets=[
            ExplicitLegacyTarget(
                legacy_path=legacy_path,
                export_filename="imsvu011.dat",
                subject_type="insurer",
            )
        ],
    )

    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is True
    assert result.legacy_report is not None
    assert result.legacy_report.matches is True


def test_explicit_multi_period_flags_missing_legacy_period(tmp_path: Path) -> None:
    legacy_path = tmp_path / "reference_imsvu011.dat"
    legacy_path.write_text(
        "\n".join(
            [
                "#t Pr1 Wer1 Rs1 Vn1 Sc1 Sh1 Pr2 Wer2 Rs2 Vn2 Sc2 Sh2",
                "2 8.0 1.0 39.0 2.0 1 9.0 12.0 1.0 60.0 2.0 0 0.0",
                "3 8.0 1.0 39.0 2.0 1 9.0 12.0 1.0 60.0 2.0 0 0.0",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_explicit_multi_period_from_mappings(
        [_scenario(2)],
        output_dir=tmp_path / "out",
        legacy_targets=[
            ExplicitLegacyTarget(
                legacy_path=legacy_path,
                export_filename="imsvu011.dat",
                subject_type="insurer",
            )
        ],
    )

    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is False
    assert result.legacy_report is not None
    assert result.legacy_report.matches is False
    assert result.legacy_report.deviation_index[0].global_period == 3
    assert result.legacy_report.deviation_index[0].actual == "missing export row"


def test_explicit_multi_period_fixture_loads_legacy_targets_and_writes_report(tmp_path: Path) -> None:
    legacy_path = tmp_path / "legacy" / "reference_imsvu011.dat"
    legacy_path.parent.mkdir()
    legacy_path.write_text(
        "\n".join(
            [
                "#t Pr1 Wer1 Rs1 Vn1 Sc1 Sh1 Pr2 Wer2 Rs2 Vn2 Sc2 Sh2",
                "2 8.0 1.0 39.0 2.0 1 9.0 12.0 1.0 60.0 2.0 0 0.0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fixture_path = tmp_path / "explicit_with_legacy.json"
    fixture_path.write_text(
        json.dumps(
            {
                "periods": [_scenario(2)],
                "legacy_report_name": "explicit_validation",
                "legacy_targets": [
                    {
                        "legacy_path": "legacy/reference_imsvu011.dat",
                        "export_filename": "imsvu011.dat",
                        "subject_type": "insurer",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_explicit_multi_period_from_fixture(fixture_path, output_dir=tmp_path / "out")

    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is True
    assert result.legacy_report is not None
    assert result.legacy_report.matches is True
    assert [path.name for path in result.written_legacy_report_files] == [
        "explicit_validation.json",
        "explicit_validation.csv",
        "explicit_validation_fields.csv",
        "explicit_validation_groups.csv",
        "explicit_validation_periods.csv",
        "explicit_validation_deviations.csv",
    ]
    assert (tmp_path / "out" / "explicit_validation.json").exists()


def test_explicit_multi_period_fixture_passes_resolved_legacy_base_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    fixture_path = real_dir / "explicit_with_legacy.json"
    fixture_path.write_text(
        json.dumps(
            {
                "periods": [_scenario(2)],
                "legacy_targets": [
                    {
                        "legacy_path": "legacy/reference_imsvu011.dat",
                        "export_filename": "imsvu011.dat",
                        "subject_type": "insurer",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    captured_base_paths: list[Path] = []

    def _capture_legacy_base_path(value: object, *, fixture_base_path: Path) -> list:
        captured_base_paths.append(fixture_base_path)
        return []

    monkeypatch.setattr(explicit_period_runner, "_load_legacy_targets", _capture_legacy_base_path)
    indirect_path = tmp_path / "unused" / ".." / "real" / fixture_path.name

    run_explicit_multi_period_from_fixture(indirect_path, output_dir=tmp_path / "out")

    assert captured_base_paths == [fixture_path.resolve().parent]
