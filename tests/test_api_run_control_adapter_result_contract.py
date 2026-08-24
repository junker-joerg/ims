import json
import os
import subprocess
import sys
from pathlib import Path

from ims.api.run_control_adapter_result_contract import (
    RunControlAdapterResultContract,
    build_run_control_adapter_result_contract,
    main,
    run_control_adapter_result_contract_payload,
    validate_run_control_adapter_result_payload,
)


def _summary_payload() -> dict[str, object]:
    return {
        "mode": "explicit_multi_period_execution_summary",
        "period_count": 2,
        "processed_local_periods": [1, 2],
        "processed_global_periods": [1, 2],
        "total_vu_rule_applications": 0,
        "total_vn_insurance_rule_applications": 0,
        "total_vn_settlement_applications": 0,
        "total_vn_damage_settlement_applications": 0,
        "carryover_count": 0,
        "vu_carryover_count": 0,
        "vn_carryover_count": 0,
        "written_file_count": 0,
        "legacy_comparison_performed": False,
        "legacy_comparison_matches": None,
        "legacy_report_written_file_count": 0,
        "writes_performed": False,
        "execution_performed": True,
        "automatic_historical_rule_selection_performed": False,
        "simulation_performed": False,
    }


def _adapter_result_payload() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "controlled_execution_adapter",
        "adapter_mode": "explicit_multi_period_fixture_adapter",
        "fixture_path": "tests/fixtures/replay_vn_policyholder_transition_plan.json",
        "fixture_kind": "explicit_vu_vn_period_plan_fixture",
        "explicit_execution_release": True,
        "requested_carry_forward_vu_state": False,
        "requested_carry_forward_vn_state": False,
        "summary": _summary_payload(),
        "contract": run_control_adapter_result_contract_payload(),
        "http_enabled": False,
        "ui_enabled": False,
        "queue_worker_enabled": False,
        "writes_enabled": False,
        "writes_performed": False,
        "execution_performed": True,
        "simulation_performed": False,
        "automatic_historical_rule_selection_performed": False,
        "historical_full_equality_claimed": False,
    }


def test_run_control_adapter_result_contract_reports_readonly_shape() -> None:
    payload = run_control_adapter_result_contract_payload()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_adapter_result_contract"
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["expected_result_mode"] == "controlled_execution_adapter"
    assert payload["expected_summary_mode"] == "explicit_multi_period_execution_summary"
    assert "summary" in payload["required_result_fields"]
    assert "simulation_performed" in payload["required_summary_fields"]
    assert "browser_upload" in payload["forbidden_fields"]
    assert "adapter_start_from_run_control" not in payload["forbidden_boundaries"]
    assert payload["precomputed_result_required"] is True
    assert payload["adapter_start_allowed"] is False
    assert payload["api_accepts_upload"] is False
    assert payload["http_enabled"] is False
    assert payload["ui_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["execution_performed"] is False
    assert isinstance(build_run_control_adapter_result_contract(), RunControlAdapterResultContract)


def test_run_control_adapter_result_contract_accepts_precomputed_payload() -> None:
    result = validate_run_control_adapter_result_payload(_adapter_result_payload()).to_dict()

    assert result["status"] == "ok"
    assert result["mode"] == "run_control_adapter_result_validation"
    assert result["result_accepted"] is True
    assert result["issues"] == []
    assert result["adapter_started"] is False
    assert result["writes_performed"] is False
    assert result["execution_performed"] is False
    assert result["simulation_performed"] is False


def test_run_control_adapter_result_contract_rejects_start_and_write_fields() -> None:
    payload = _adapter_result_payload()
    payload["browser_upload"] = "payload.json"
    payload["writes_performed"] = True
    payload["summary"]["writes_performed"] = True

    result = validate_run_control_adapter_result_payload(payload).to_dict()
    codes = {issue["code"] for issue in result["issues"]}

    assert result["status"] == "error"
    assert result["result_accepted"] is False
    assert "unknown_result_field" in codes
    assert "forbidden_result_field" in codes
    assert "writes_performed" in codes
    assert "summary_writes_performed" in codes


def test_run_control_adapter_result_contract_cli_prints_contract_without_writing(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    exit_code = main([])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "run_control_adapter_result_contract"
    assert payload["adapter_start_allowed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_adapter_result_contract_cli_checks_existing_json_without_writing(tmp_path, capsys):
    payload_path = tmp_path / "adapter_result.json"
    payload_path.write_text(json.dumps(_adapter_result_payload()), encoding="utf-8")

    exit_code = main(["check", str(payload_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "run_control_adapter_result_validation"
    assert payload["result_accepted"] is True
    assert {path.name for path in tmp_path.iterdir()} == {"adapter_result.json"}


def test_run_control_adapter_result_contract_module_entrypoint_rejects_bad_payload(tmp_path) -> None:
    payload = _adapter_result_payload()
    payload["simulation_performed"] = True
    payload_path = tmp_path / "adapter_result.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.run_control_adapter_result_contract",
            "check",
            str(payload_path),
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode == 1
    assert "simulation_performed" in completed.stdout
    assert completed.stderr == ""
