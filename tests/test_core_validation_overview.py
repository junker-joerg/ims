import json
from pathlib import Path

from ims.engine.core_validation_overview import (
    CoreValidationOverviewResult,
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
    assert payload["legacy_reference_count"] == 4
    assert payload["legacy_covered_rows"] == 400
    assert payload["legacy_covered_periods"] == 400
    assert payload["next_validation_actions"] == ["await_historical_reference"]
    assert payload["period_diagnostics"]["mode"] == "explicit_period_diagnostics_bundle"
    assert payload["legacy_validation"]["mode"] == "legacy_agrsich_validation_overview"
    assert payload["coverage_matrix"]["mode"] == "legacy_agrsich_coverage_matrix"
    assert payload["next_family_plan"]["mode"] == "legacy_agrsich_next_family_plan"
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
    assert payload["legacy_covered_rows"] == 400
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


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
    assert "Aktualisierte PR-Restplanung" in resume_plan
    assert "IMS-Kernvalidierungsueberblick" in resume_plan
