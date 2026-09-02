import importlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from ims.strategies.catalog import (
    STRATEGY_CATALOG_VERSION,
    STRATEGY_DEFINITIONS,
    STRATEGY_FAMILIES,
    StrategyActorType,
    get_strategy_definition,
    list_strategy_definitions,
    strategy_catalog_issues,
    strategy_catalog_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_strategy_catalog_covers_historical_vu_and_vn_actions() -> None:
    assert [item.historical_action for item in STRATEGY_DEFINITIONS] == [
        *(f"Vrvu{rule_id:02d}" for rule_id in range(1, 11)),
        *(f"Vrvn{rule_id:02d}" for rule_id in range(1, 7)),
    ]
    assert len(STRATEGY_FAMILIES) == 8
    assert strategy_catalog_issues() == ()


def test_strategy_catalog_keeps_vdefmd6_rule_classes_exact() -> None:
    vu = list_strategy_definitions(actor_type=StrategyActorType.INSURER)
    vn = list_strategy_definitions(actor_type="policyholder")

    assert [(item.historical_rule_id, item.historical_rule_class) for item in vu[:9]] == [
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 2),
        (5, 2),
        (6, 2),
        (7, 3),
        (8, 3),
        (9, 3),
    ]
    assert [(item.historical_rule_id, item.historical_rule_class) for item in vn] == [
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 2),
        (5, 3),
        (6, 3),
    ]

    free_rule = get_strategy_definition("vu.vrvu10")
    assert free_rule.historical_rule_class is None
    assert free_rule.included_in_vdefmd6 is False
    assert [
        get_strategy_definition(f"vu.vrvu{rule_id:02d}").implementation_variant
        for rule_id in range(7, 10)
    ] == ["dumping", "average", "attack"]


def test_strategy_catalog_references_existing_source_implementations_and_tests() -> None:
    source_by_file: dict[str, str] = {}
    for strategy in STRATEGY_DEFINITIONS:
        source = source_by_file.setdefault(
            strategy.source_file,
            (REPO_ROOT / strategy.source_file).read_text(encoding="latin-1"),
        )
        assert f"act {strategy.historical_action}" in source

        module = importlib.import_module(strategy.implementation_module)
        assert callable(getattr(module, strategy.implementation_entrypoint))
        if strategy.parameter_schema is not None:
            assert isinstance(getattr(module, strategy.parameter_schema), type)

        for evidence in strategy.test_evidence:
            assert (REPO_ROOT / evidence).is_file()


def test_strategy_catalog_filters_and_rejects_unknown_ids() -> None:
    assert [
        item.strategy_id
        for item in list_strategy_definitions(family_id="vn.market_search")
    ] == ["vn.vrvn05", "vn.vrvn06"]

    with pytest.raises(KeyError, match="Unbekannte Strategie-ID"):
        get_strategy_definition("vn.unknown")


def test_strategy_catalog_payload_is_stable_read_only_metadata() -> None:
    payload = strategy_catalog_payload()

    assert payload["schema_version"] == STRATEGY_CATALOG_VERSION
    assert payload["mode"] == "strategy_catalog_read_only"
    assert payload["scope"] == "read_only_strategy_metadata"
    assert payload["historical_full_equality_claim"] is False
    assert payload["selection_enabled"] is False
    assert payload["parameter_editing_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert len(payload["families"]) == 8
    assert len(payload["strategies"]) == 16
    assert json.loads(json.dumps(payload, sort_keys=True))["schema_version"] == STRATEGY_CATALOG_VERSION


def test_strategy_catalog_validation_reports_contract_breaks() -> None:
    duplicate = STRATEGY_DEFINITIONS + (STRATEGY_DEFINITIONS[0],)
    wrong_family = replace(
        STRATEGY_DEFINITIONS[0],
        family_id="vn.market_search",
    )

    assert "Doppelte Strategie-ID: vu.vrvu01" in strategy_catalog_issues(
        strategies=duplicate
    )
    assert "Akteurstyp passt nicht zur Familie: vu.vrvu01" in strategy_catalog_issues(
        strategies=(wrong_family,)
    )
