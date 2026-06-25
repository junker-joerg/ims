import json
from pathlib import Path

from ims.engine.explicit_period_diagnostics import diagnose_explicit_period_plan, main


REPO_ROOT = Path(__file__).resolve().parent.parent
VU14_PLAN = REPO_ROOT / "tests" / "fixtures" / "replay_vu14_period_plan.json"


def _minimal_plan() -> dict:
    return {
        "metadata": {"purpose": "diagnostic test"},
        "base_snapshot": {
            "context": {"period": 0, "max_periods": 12, "run_index": 0, "rng_seed": 0},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 11, "name": "VU-11", "rule_id": 1, "rule_class": 1}],
            "policyholders": [{"entity_id": 21, "name": "VN-21", "rule_id": 5, "rule_class": 1}],
        },
        "period_updates": [
            {
                "context": {"period": 2, "max_periods": 12, "run_index": 1, "rng_seed": 1202},
                "insurers": [{"entity_id": 11, "name": "VU-11A"}],
                "policyholders": [],
                "vn_insurance_rule_snapshots": [{"policyholder_id": 21, "rule_kind": "compulsory"}],
            }
        ],
    }


def _minimal_plan_with_legacy_reference() -> dict:
    data = _minimal_plan()
    data["legacy_targets"] = [
        {
            "legacy_path": "tests/references/legacy_agrsich/IMSVNR05.DAT",
            "export_filename": "imsvnr05.dat",
            "subject_type": "policyholder",
        }
    ]
    return data


def test_explicit_period_diagnostics_reports_fixture_without_execution() -> None:
    result = diagnose_explicit_period_plan(VU14_PLAN)
    payload = result.to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "explicit_period_diagnostics"
    assert payload["period_count"] == 4
    assert payload["global_periods"] == [1, 2, 3, 4]
    assert payload["legacy_targets"][0]["kind"] == "legacy_window"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert all(period["execution_performed"] is False for period in payload["periods"])


def test_explicit_period_diagnostics_reports_rule_boundaries(tmp_path: Path) -> None:
    plan_path = tmp_path / "period_plan.json"
    plan_path.write_text(json.dumps(_minimal_plan()), encoding="utf-8")

    payload = diagnose_explicit_period_plan(plan_path).to_dict()

    assert payload["status"] == "warning"
    assert payload["global_periods"] == [14]
    assert payload["snapshot_families"] == ["vn_insurance_rule_snapshots"]
    assert payload["periods"][0]["insurer_update_count"] == 1
    assert payload["periods"][0]["vn_insurance_rule_application_count"] == 1
    assert payload["issues"][0]["code"] == "explicit_period_no_legacy_reference"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_explicit_period_diagnostics_rejects_duplicate_global_periods(tmp_path: Path) -> None:
    data = _minimal_plan()
    data["period_updates"].append(
        {
            "context": {"period": 2, "max_periods": 12, "run_index": 1, "rng_seed": 1203},
            "insurers": [],
            "policyholders": [],
        }
    )
    plan_path = tmp_path / "duplicate_period_plan.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    payload = diagnose_explicit_period_plan(plan_path).to_dict()

    assert payload["status"] == "error"
    assert payload["issues"][0]["code"] == "explicit_period_duplicate_global_period"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_explicit_period_diagnostics_rejects_invalid_vn_rule_kind_before_counts(tmp_path: Path) -> None:
    data = _minimal_plan_with_legacy_reference()
    data["period_updates"][0]["vn_insurance_rule_snapshots"][0]["rule_kind"] = "unsupported"
    plan_path = tmp_path / "invalid_rule_kind_period_plan.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    payload = diagnose_explicit_period_plan(plan_path).to_dict()

    assert payload["status"] == "error"
    assert payload["period_count"] == 0
    assert payload["periods"] == []
    assert payload["issues"][0]["code"] == "explicit_period_snapshot_invalid"
    assert "unsupported VN insurance rule kind" in payload["issues"][0]["message"]
    assert payload["issues"][0]["period"] == 2
    assert payload["issues"][0]["global_period"] == 14
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_explicit_period_diagnostics_rejects_unknown_snapshot_policyholder_before_counts(tmp_path: Path) -> None:
    data = _minimal_plan_with_legacy_reference()
    data["period_updates"][0]["vn_insurance_rule_snapshots"][0]["policyholder_id"] = 999
    plan_path = tmp_path / "unknown_policyholder_period_plan.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    payload = diagnose_explicit_period_plan(plan_path).to_dict()

    assert payload["status"] == "error"
    assert payload["period_count"] == 0
    assert payload["periods"] == []
    assert payload["issues"][0]["code"] == "explicit_period_snapshot_invalid"
    assert "VN insurance rule snapshots reference unknown policyholders: 999" in payload["issues"][0]["message"]
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_explicit_period_diagnostics_cli_returns_stable_json(capsys) -> None:
    exit_code = main([str(VU14_PLAN)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "explicit_period_diagnostics"
    assert payload["status"] == "ok"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_explicit_period_diagnostics_cli_reports_errors_as_json(tmp_path: Path, capsys) -> None:
    missing_path = tmp_path / "missing_period_plan.json"

    exit_code = main([str(missing_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"
    assert payload["issues"][0]["code"] == "explicit_period_diagnostics_failed"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not missing_path.exists()
