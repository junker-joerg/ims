import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.core_validation_carryover_probe_contract import (
    CoreValidationCarryoverProbeApiContract,
    build_core_validation_carryover_probe_api_contract,
    core_validation_carryover_probe_api_contract_payload,
    main,
)


def test_core_validation_carryover_probe_api_contract_reports_stable_boundaries() -> None:
    payload = build_core_validation_carryover_probe_api_contract().to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "core_validation_carryover_probe_api_contract"
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["endpoint"] == "/api/core-validation/carryover-probe-contract"
    assert payload["expected_probe_mode"] == "explicit_transition_carryover_probe"
    assert payload["expected_contract_mode"] == "explicit_transition_carryover_probe_contract"
    assert payload["precomputed_probe_required"] is True
    assert payload["api_accepts_probe_payload"] is False
    assert payload["api_starts_probe"] is False
    assert payload["http_enabled"] is True
    assert payload["ui_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False


def test_core_validation_carryover_probe_api_contract_lists_payload_shape() -> None:
    payload = core_validation_carryover_probe_api_contract_payload()

    assert payload["expected_inputs"] == ["precomputed_explicit_transition_carryover_probe_payload"]
    assert payload["required_preconditions"] == [
        "carryover_probe_payload_precomputed_outside_api",
        "core_validation_overview_contract_visible",
        "execution_enabled_false",
        "writes_enabled_false",
    ]
    assert payload["accepted_payload_fields"] == [
        "status",
        "mode",
        "plan_path",
        "transition_count",
        "vu_carryover_requested",
        "vn_carryover_requested",
        "in_memory_carryover_performed",
        "transitions",
        "issues",
        "writes_performed",
        "execution_performed",
        "simulation_performed",
        "automatic_historical_rule_selection_performed",
    ]
    assert "diagnostic_candidate_ids_match" in payload["transition_fields"]
    assert "vu_carryover_executed" in payload["carryover_request_fields"]
    assert "carried_policyholder_state" in payload["carried_entity_fields"]
    assert payload["boundary_fields"] == [
        "writes_performed",
        "execution_performed",
        "simulation_performed",
        "automatic_historical_rule_selection_performed",
    ]
    assert "probe_execution_from_api" in payload["forbidden_boundaries"]
    assert "historical_full_equality_claim" in payload["forbidden_boundaries"]


def test_core_validation_carryover_probe_contract_cli_prints_json_without_writing(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    exit_code = main([])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "core_validation_carryover_probe_api_contract"
    assert payload["api_starts_probe"] is False
    assert payload["writes_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()
    assert CoreValidationCarryoverProbeApiContract is not None


def test_core_validation_carryover_probe_contract_rejects_arguments(capsys):
    with pytest.raises(SystemExit):
        main(["--plan", "tests/fixtures/replay_vn_policyholder_transition_plan.json"])

    assert capsys.readouterr().out == ""


def test_core_validation_carryover_probe_contract_module_entrypoint_rejects_arguments():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.core_validation_carryover_probe_contract",
            "--apply-vn",
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "does not accept arguments" in completed.stderr
    assert completed.stdout == ""
