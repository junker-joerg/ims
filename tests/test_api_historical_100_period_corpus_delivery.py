import json
from pathlib import Path

from ims.api.historical_100_period_corpus_delivery import (
    CALCULATION_ORIGIN,
    CONTRACT_VERSION,
    DELIVERY_FILENAMES,
    build_historical_100_period_corpus_delivery,
    main,
)
from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportFileSpec,
    ExportRow,
    ExportTable,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_delivery_binds_two_controlled_100_period_tables() -> None:
    payload = build_historical_100_period_corpus_delivery(REPO_ROOT).to_dict()
    targets = {target["filename"]: target for target in payload["targets"]}

    assert payload["status"] == "ready"
    assert payload["contract_version"] == CONTRACT_VERSION
    assert payload["source_contracts"] == ["pr86-v1", "pr91-v1", "pr92-v1"]
    assert payload["calculation_origin"] == CALCULATION_ORIGIN
    assert payload["delivered_export_count"] == 2
    assert payload["delivered_period_count"] == 200
    assert payload["required_export_count"] == 15
    assert payload["missing_export_count"] == 13
    assert payload["missing_period_count"] == 6100
    assert set(targets) == set(DELIVERY_FILENAMES)
    assert targets["imsvu014.dat"]["layer_ids"] == ["wvemod1_archive"]
    assert targets["imsvnsk1.dat"]["layer_ids"] == ["wvemod1_archive"]
    assert {target["period_count"] for target in targets.values()} == {100}
    assert payload["production_corpus_status"] == "blocked"
    assert payload["production_release_decision"] == (
        "blocked_calculated_core_validation"
    )
    assert payload["issues"] == []


def test_delivery_canonicalizes_generated_level_iv_all_selector() -> None:
    payload = build_historical_100_period_corpus_delivery(REPO_ROOT).to_dict()
    target = next(
        item for item in payload["targets"] if item["filename"] == "imsvnsk1.dat"
    )

    assert target["level"] == "IV"
    assert target["selector_kind"] == "all"
    assert target["raw_selector_value"] == "all"
    assert target["selector_value"] == "SK1"


def test_delivery_accepts_injected_tables_without_starting_controlled_run() -> None:
    payload = build_historical_100_period_corpus_delivery(
        REPO_ROOT,
        export_tables=_valid_tables(),
    ).to_dict()

    assert payload["status"] == "ready"
    assert payload["controlled_execution_performed"] is False
    assert payload["delivered_export_count"] == 2
    assert payload["simulation_performed"] is False


def test_delivery_rejects_missing_target() -> None:
    payload = build_historical_100_period_corpus_delivery(
        REPO_ROOT,
        export_tables=(_valid_tables()[0],),
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["delivered_export_count"] == 1
    assert "delivery_target_missing" in issue_codes
    assert "production_delivery_count_mismatch" in issue_codes


def test_delivery_rejects_wrong_period_boundary() -> None:
    insurer, policyholder = _valid_tables()
    policyholder.rows.pop()

    payload = build_historical_100_period_corpus_delivery(
        REPO_ROOT,
        export_tables=(insurer, policyholder),
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "delivery_period_boundary_mismatch" in issue_codes
    assert payload["delivered_export_count"] == 1


def test_delivery_rejects_wrong_header_and_unexpected_target() -> None:
    insurer, policyholder = _valid_tables()
    insurer.header = POLICYHOLDER_HEADER
    unexpected = _table(
        "imsvnr01.dat",
        "policyholder",
        "II",
        "rule",
        1,
    )

    payload = build_historical_100_period_corpus_delivery(
        REPO_ROOT,
        export_tables=(insurer, policyholder, unexpected),
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "delivery_header_mismatch" in issue_codes
    assert "delivery_target_unexpected" in issue_codes
    assert payload["production_release_approved"] is False


def test_delivery_rejects_wrong_row_width() -> None:
    insurer, policyholder = _valid_tables()
    insurer.rows[0].values.pop()

    payload = build_historical_100_period_corpus_delivery(
        REPO_ROOT,
        export_tables=(insurer, policyholder),
    ).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert "delivery_row_width_mismatch" in issue_codes
    assert payload["delivered_export_count"] == 1


def test_delivery_cli_reports_blocked_production_without_simulation(capsys) -> None:
    exit_code = main(["--root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ready"
    assert payload["production_corpus_status"] == "blocked"
    assert payload["controlled_execution_performed"] is True
    assert payload["writes_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False


def _valid_tables() -> tuple[ExportTable, ExportTable]:
    return (
        _table("imsvu014.dat", "insurer", "I", "entity", 14),
        _table("imsvnsk1.dat", "policyholder", "IV", "all", "all"),
    )


def _table(
    filename: str,
    subject_type: str,
    level: str,
    selector_kind: str,
    selector_value: int | str,
) -> ExportTable:
    column_count = 13 if subject_type == "insurer" else 12
    header = INSURER_HEADER if subject_type == "insurer" else POLICYHOLDER_HEADER
    return ExportTable(
        spec=ExportFileSpec(
            filename=filename,
            subject_type=subject_type,
            level=level,
            selector_kind=selector_kind,
            selector_value=selector_value,
        ),
        header=header,
        rows=[
            ExportRow(values=[period, *([0.0] * (column_count - 1))])
            for period in range(1, 101)
        ],
    )
