import json
from pathlib import Path

from ims.engine.explicit_period_diagnostics_bundle import (
    ExplicitPeriodDiagnosticsBundleResult,
    build_explicit_period_diagnostics_bundle,
    main,
)


FIXTURE_DIR = Path("tests/fixtures")
VU14_PLAN = FIXTURE_DIR / "replay_vu14_period_plan.json"
VUSK1_PLAN = FIXTURE_DIR / "replay_vusk1_period_plan.json"
MIGRATION_DOC = Path("docs/migration/agrsich_replay_plan.md")


def test_explicit_period_diagnostics_bundle_summarizes_existing_plans() -> None:
    result = build_explicit_period_diagnostics_bundle([VU14_PLAN, VUSK1_PLAN])
    payload = result.to_dict()

    assert isinstance(result, ExplicitPeriodDiagnosticsBundleResult)
    assert payload["status"] == "ok"
    assert payload["mode"] == "explicit_period_diagnostics_bundle"
    assert payload["plan_count"] == 2
    assert payload["ok_plan_count"] == 2
    assert payload["warning_plan_count"] == 0
    assert payload["error_plan_count"] == 0
    assert payload["total_period_count"] == 8
    assert payload["global_periods"] == [1, 2, 3, 4, 101, 102, 103, 104]
    assert payload["legacy_target_count"] == 2
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert all(plan["execution_performed"] is False for plan in payload["plans"])


def test_explicit_period_diagnostics_bundle_propagates_plan_errors(tmp_path: Path) -> None:
    missing_plan = tmp_path / "missing_period_plan.json"

    result = build_explicit_period_diagnostics_bundle([VU14_PLAN, missing_plan])
    payload = result.to_dict()

    assert payload["status"] == "error"
    assert payload["plan_count"] == 2
    assert payload["ok_plan_count"] == 1
    assert payload["error_plan_count"] == 1
    assert payload["total_period_count"] == 4
    assert payload["issues"][0]["code"] == "explicit_period_diagnostics_failed"
    assert "missing_period_plan.json" in payload["issues"][0]["message"]
    assert not missing_plan.exists()


def test_explicit_period_diagnostics_bundle_rejects_empty_input() -> None:
    payload = build_explicit_period_diagnostics_bundle([]).to_dict()

    assert payload["status"] == "error"
    assert payload["plan_count"] == 0
    assert payload["issues"][0]["code"] == "explicit_period_diagnostics_bundle_empty"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_explicit_period_diagnostics_bundle_cli_prints_stable_json(capsys) -> None:
    exit_code = main([str(VU14_PLAN), str(VUSK1_PLAN)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "explicit_period_diagnostics_bundle"
    assert payload["plan_count"] == 2
    assert payload["total_period_count"] == 8
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_explicit_period_diagnostics_bundle_cli_returns_error_for_missing_plan(
    tmp_path: Path,
    capsys,
) -> None:
    missing_plan = tmp_path / "missing_period_plan.json"

    exit_code = main([str(missing_plan)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"
    assert payload["error_plan_count"] == 1
    assert not missing_plan.exists()


def test_explicit_period_diagnostics_bundle_is_documented() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "## Diagnose-Buendel fuer Periodenplaene" in doc
    assert "python -m ims.engine.explicit_period_diagnostics_bundle" in doc
    assert 'mode = "explicit_period_diagnostics_bundle"' in doc
    assert "startet keinen Runner" in doc
