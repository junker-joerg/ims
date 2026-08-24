import json
from pathlib import Path

import pytest

from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportFileSpec,
    ExportRow,
    ExportTable,
)
from ims.model.legacy_calculated_comparison import (
    build_calculated_legacy_comparison_plan,
    compare_calculated_export_tables_to_legacy_fixture,
)


CORE_BUNDLE = Path("tests/fixtures/legacy_validation_bundle.json")
MIGRATION_DOC = Path("docs/migration/calculated_legacy_multi_period_contract.md")


def _required_export(plan, filename: str):
    return next(item for item in plan.required_exports if item.filename == filename)


def _write_small_fixture(tmp_path: Path) -> Path:
    legacy_path = tmp_path / "legacy_agrsich" / "CALCULATED.DAT"
    legacy_path.parent.mkdir()
    legacy_path.write_text(
        "#t Pr1 Wa1 Rs1 Vn1 Sa1 Sh1 Pr2 Wa2 Rs2 Vn2 Sa2 Sh2\n"
        "0001 040.0 000.0 +000000.0 00 000 0000.0 035.0 000.0 +000000.0 000 000 0000.0\n"
        "0002 038.8 000.0 +000019.1 02 002 0060.1 033.3 000.0 +000006.4 002 002 0062.7\n",
        encoding="utf-8",
    )
    fixture_path = tmp_path / "calculated_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "subject_type": "insurer",
                        "legacy_path": "legacy_agrsich/CALCULATED.DAT",
                        "export_filename": "imsvu014.dat",
                        "periods": [1, 2],
                        "level": "I",
                        "selector_kind": "entity",
                        "selector_value": 14,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return fixture_path


def _calculated_table(*, periods: list[int] | None = None, reserves_1: float = 19.1) -> ExportTable:
    rows_by_period = {
        1: [1, 40.0, 0.0, 0.0, 0, 0, 0.0, 35.0, 0.0, 0.0, 0, 0, 0.0],
        2: [2, 38.8, 0.0, reserves_1, 2, 2, 60.1, 33.3, 0.0, 6.4, 2, 2, 62.7],
        3: [3, 38.0, 0.0, 0.0, 0, 0, 0.0, 33.0, 0.0, 0.0, 0, 0, 0.0],
    }
    selected_periods = periods if periods is not None else [1, 2]
    return ExportTable(
        spec=ExportFileSpec(
            filename="imsvu014.dat",
            subject_type="insurer",
            level="I",
            selector_kind="entity",
            selector_value=14,
        ),
        header=INSURER_HEADER,
        rows=[ExportRow(values=rows_by_period[period]) for period in selected_periods],
    )


def _write_policyholder_fixture(tmp_path: Path) -> Path:
    legacy_path = tmp_path / "legacy_agrsich" / "CALCULATED_VN.DAT"
    legacy_path.parent.mkdir(exist_ok=True)
    legacy_path.write_text(
        "#t Vu1 Vs1 Vp1 Ev1 Sh1 Vu2 Vs2 Vp2 Ev2 Sh2 Vm\n"
        "0001 014 001 0040.0 0100.0 0000.0 015 001 0035.0 0200.0 0000.0 0300.0\n",
        encoding="utf-8",
    )
    fixture_path = tmp_path / "calculated_vn_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "subject_type": "policyholder",
                        "legacy_path": "legacy_agrsich/CALCULATED_VN.DAT",
                        "export_filename": "imsvnr01.dat",
                        "periods": [1],
                        "level": "II",
                        "selector_kind": "rule",
                        "selector_value": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return fixture_path


def _calculated_policyholder_table() -> ExportTable:
    return ExportTable(
        spec=ExportFileSpec(
            filename="imsvnr01.dat",
            subject_type="policyholder",
            level="II",
            selector_kind="rule",
            selector_value=1,
        ),
        header=POLICYHOLDER_HEADER,
        rows=[
            ExportRow(
                values=[1, 14, 1, 40.0, 100.0, 0.0, 15, 1, 35.0, 200.0, 0.0, 300.0]
            )
        ],
    )


def test_core_calculated_comparison_plan_fixes_full_input_boundary() -> None:
    plan = build_calculated_legacy_comparison_plan(CORE_BUNDLE)

    assert plan.mode == "calculated_legacy_comparison_plan"
    assert plan.target_count == 19
    assert plan.target_period_count == 6300
    assert plan.required_export_count == 15
    assert plan.comparison_performed is False
    assert plan.writes_performed is False
    assert plan.execution_performed is False
    assert plan.simulation_performed is False

    insurer_sk1 = _required_export(plan, "imsvusk1.dat")
    assert insurer_sk1.subject_type == "insurer"
    assert insurer_sk1.level == "IV"
    assert insurer_sk1.selector_kind == "all"
    assert insurer_sk1.selector_value == "SK1"
    assert insurer_sk1.periods == list(range(1, 501))
    assert insurer_sk1.target_count == 5

    policyholder_sk1 = _required_export(plan, "imsvnsk1.dat")
    assert policyholder_sk1.periods == list(range(1, 101))
    assert policyholder_sk1.target_count == 1
    assert all("zins000" not in str(path).lower() for item in plan.required_exports for path in item.legacy_paths)


def test_calculated_tables_are_compared_without_fixture_echo(tmp_path: Path) -> None:
    result = compare_calculated_export_tables_to_legacy_fixture(
        _write_small_fixture(tmp_path),
        [_calculated_table()],
        calculation_origin="unit_test_explicit_calculation",
    )

    assert result.matches is True
    assert result.report.total_files == 1
    assert result.report.total_rows == 2
    assert result.report.matched_rows == 2
    assert result.calculation_origin == "unit_test_explicit_calculation"
    assert result.comparison_performed is True
    assert result.calculated_export_tables_supplied is True
    assert result.calculation_origin_verified is False
    assert result.legacy_fixture_rows_used_as_export is False
    assert result.writes_performed is False
    assert result.execution_performed is False
    assert result.simulation_performed is False


def test_calculated_policyholder_table_uses_vn_reference_parser(tmp_path: Path) -> None:
    result = compare_calculated_export_tables_to_legacy_fixture(
        _write_policyholder_fixture(tmp_path),
        [_calculated_policyholder_table()],
        calculation_origin="unit_test_explicit_vn_calculation",
    )

    assert result.matches is True
    assert result.report.total_files == 1
    assert result.report.total_rows == 1
    assert result.report.file_summaries[0].subject_type == "policyholder"


def test_calculated_comparison_reports_numeric_difference(tmp_path: Path) -> None:
    result = compare_calculated_export_tables_to_legacy_fixture(
        _write_small_fixture(tmp_path),
        [_calculated_table(reserves_1=99.0)],
        calculation_origin="unit_test_explicit_calculation",
    )

    assert result.matches is False
    assert result.report.total_rows == 2
    assert result.report.matched_rows == 1
    assert result.report.mismatched_rows == 1


@pytest.mark.parametrize("periods", [[1], [1, 2, 3], [2, 1], [1, 1]])
def test_calculated_comparison_rejects_wrong_period_boundary(
    tmp_path: Path,
    periods: list[int],
) -> None:
    with pytest.raises(ValueError, match="periods must match the required sorted boundary"):
        compare_calculated_export_tables_to_legacy_fixture(
            _write_small_fixture(tmp_path),
            [_calculated_table(periods=periods)],
            calculation_origin="unit_test_explicit_calculation",
        )


def test_calculated_comparison_rejects_wrong_export_identity(tmp_path: Path) -> None:
    table = _calculated_table()
    table.spec.level = "II"

    with pytest.raises(ValueError, match="export set does not match fixture requirements"):
        compare_calculated_export_tables_to_legacy_fixture(
            _write_small_fixture(tmp_path),
            [table],
            calculation_origin="unit_test_explicit_calculation",
        )


def test_calculated_comparison_requires_declared_origin(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="requires a calculation_origin"):
        compare_calculated_export_tables_to_legacy_fixture(
            _write_small_fixture(tmp_path),
            [_calculated_table()],
            calculation_origin=" ",
        )


def test_calculated_comparison_documentation_keeps_claims_conservative() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "Vertrag fuer berechnete Legacy-Mehrperiodenvergleiche" in doc
    assert "15 eindeutig benoetigte berechnete Exporttabellen" in doc
    assert "19 historische Ziele" in doc
    assert "6.300 Zielperioden" in doc
    assert "fuenf Zeitfenstern desselben `SK1`-/`all`-Aggregats" in doc
    assert "ZINS000 ist nicht Teil dieses Sollplans" in doc
    assert "legacy_fixture_rows_used_as_export = false" in doc
    assert "calculation_origin_verified = false" in doc
    assert "startet keine Simulation" in doc
    assert "historische" in doc and "Vollgleichheit" in doc
    assert "PR 59" in doc and "read-only Abweichungsbericht" in doc
