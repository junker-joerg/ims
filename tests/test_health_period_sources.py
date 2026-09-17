import copy
import json
from pathlib import Path

import pytest

from ims.accounting.health_period_sources import (
    HEALTH_PERIOD_SOURCES_RESULT_VERSION,
    validate_health_period_sources,
)


FIXTURE = Path(__file__).parent / "fixtures" / "health_period_sources_v1.json"


def _input() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _codes(value: object) -> set[str]:
    result = validate_health_period_sources(value).to_dict()
    assert result["valid"] is False
    assert result["validated_period_count"] == 0
    assert "rows" not in result
    return {issue["code"] for issue in result["issues"]}


def test_three_period_sources_are_valid_stateless_and_variant_specific() -> None:
    scenario = _input()
    original = copy.deepcopy(scenario)
    result = validate_health_period_sources(scenario).to_dict()

    assert scenario == original
    assert result == validate_health_period_sources(scenario).to_dict()
    assert result["schema_version"] == HEALTH_PERIOD_SOURCES_RESULT_VERSION
    assert result["valid"] is True
    assert result["insurer_id"] == 1
    assert result["scenario_id"] == "seminar_health_01"
    assert result["variant_id"] == "baseline"
    assert result["validated_period_count"] == 3
    assert "rows" not in result
    for field in ("writes_performed", "runner_invoked", "simulation_performed", "historical_full_equality_claim"):
        assert result[field] is False

    scenario["variant_id"] = "higher_benefits"
    scenario["benefits"]["windows"][0]["amount_per_opening_policy"] = "2.60"
    variant = validate_health_period_sources(scenario).to_dict()
    assert variant["valid"] is True
    assert variant["variant_id"] == "higher_benefits"


def test_full_horizon_and_short_prefix_are_accepted_without_running_them() -> None:
    scenario = _input()
    scenario["period_count"] = 100
    for name in ("new_business", "exits"):
        scenario[name]["periods"] = [
            {"period": period, "count": 0} for period in range(1, 101)
        ]
    scenario["pricing"]["windows"] = [
        {"start_period": 1, "end_period": 100, "amount_per_opening_policy": "3.00"}
    ]
    scenario["benefits"]["windows"][0]["end_period"] = 100
    assert validate_health_period_sources(scenario).to_dict()["validated_period_count"] == 100

    scenario["period_count"] = 2
    for name in ("new_business", "exits"):
        scenario[name]["periods"] = scenario[name]["periods"][:2]
    for name in ("pricing", "benefits"):
        scenario[name]["windows"][0]["end_period"] = 2
    assert validate_health_period_sources(scenario).to_dict()["validated_period_count"] == 2


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("schema_version",), "ims.health-period-sources-input.v0", "contract_value_mismatch"),
        (("health_sector_contract_schema_version",), "ims.health-sector-contract.v1", "contract_value_mismatch"),
        (("source_kind",), "legacy", "contract_value_mismatch"),
        (("historical_mapping_status",), "mapped", "contract_value_mismatch"),
        (("sector_id",), "life", "contract_value_mismatch"),
        (("insurer_id",), True, "insurer_id_invalid"),
        (("insurer_id",), 26, "insurer_id_invalid"),
        (("scenario_id",), "bad name", "identifier_invalid"),
        (("variant_id",), "", "identifier_invalid"),
        (("period_count",), 101, "period_count_invalid"),
        (("opening_active_policies",), True, "count_invalid"),
        (("new_business", "actor_type"), "insurer", "actor_mismatch"),
        (("exits", "mode"), "automatic_switching", "source_mode_invalid"),
        (("pricing", "actor_type"), "exogenous", "actor_mismatch"),
        (("benefits", "actor_type"), "insurer", "actor_mismatch"),
        (("benefits", "mode"), "insurer_strategy", "source_mode_invalid"),
        (("new_business", "periods", 0, "count"), -1, "count_invalid"),
        (("new_business", "periods", 0, "period"), 2, "period_duplicate"),
        (("exits", "periods", 0, "count"), 11, "exits_exceed_opening"),
        (("pricing", "windows", 0, "amount_per_opening_policy"), 3.0, "decimal_string_required"),
        (("pricing", "windows", 0, "amount_per_opening_policy"), "-1", "negative_amount"),
        (("benefits", "windows", 0, "amount_per_opening_policy"), "1e2", "decimal_string_required"),
        (("benefits", "windows", 0, "end_period"), 0, "period_invalid"),
        (("pricing", "windows", 0, "start_period"), 3, "window_reversed"),
    ],
)
def test_contract_and_provenance_errors_are_atomic(path: tuple, value: object, code: str) -> None:
    scenario = _input()
    target = scenario
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    assert code in _codes(scenario)


def test_missing_unknown_and_uncovered_periods_are_rejected() -> None:
    scenario = _input()
    scenario["exits"]["periods"].pop()
    assert "period_coverage_invalid" in _codes(scenario)

    scenario = _input()
    scenario["pricing"]["windows"][0]["end_period"] = 1
    assert "window_coverage_invalid" in _codes(scenario)

    scenario = _input()
    scenario["pricing"]["windows"][1]["start_period"] = 2
    assert "window_overlap" in _codes(scenario)

    scenario = _input()
    scenario["benefits"]["windows"][0]["insurer_choice"] = True
    del scenario["pricing"]["actor_type"]
    assert "field_unknown" in _codes(scenario)
    assert "field_missing" in _codes(scenario)


def test_stock_moves_only_at_period_end_and_flow_limits_are_checked() -> None:
    scenario = _input()
    scenario["exits"]["periods"][1]["count"] = 12
    assert "exits_exceed_opening" in _codes(scenario)

    scenario = _input()
    scenario["opening_active_policies"] = 1_000_000_000
    scenario["new_business"]["periods"][0]["count"] = 2
    assert "closing_count_overflow" in _codes(scenario)

    scenario = _input()
    scenario["opening_active_policies"] = 1_000_000_000
    scenario["pricing"]["windows"][0]["amount_per_opening_policy"] = "1000"
    assert "flow_amount_overflow" in _codes(scenario)


def test_non_object_input_is_rejected() -> None:
    assert "object_required" in _codes([])
