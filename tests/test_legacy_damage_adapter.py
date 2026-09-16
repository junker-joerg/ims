import json
from dataclasses import FrozenInstanceError, asdict

import pytest

from ims.model.entities import Insurer, Policyholder
from ims.model.legacy_damage_adapter import (
    LEGACY_DAMAGE_ADAPTER_VERSION,
    adapt_legacy_damage_vector,
    legacy_damage_adapter_contract_payload,
    legacy_damage_sector_id,
)


def test_legacy_positions_map_c_one_two_to_python_zero_one_only() -> None:
    payload = json.loads(json.dumps(legacy_damage_adapter_contract_payload()))

    assert payload["schema_version"] == LEGACY_DAMAGE_ADAPTER_VERSION
    assert payload["sector_taxonomy_schema_version"] == "ims.sector-taxonomy.v1"
    assert payload["legacy_vector_length"] == 2
    assert payload["modern_sector_mapping_status"] == "unresolved"
    assert payload["historical_full_equality_claim"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert [
        (
            item["legacy_sector_id"],
            item["python_vector_index"],
            item["historical_vu_field"],
            item["historical_vn_field"],
            item["mapped_sector_id"],
        )
        for item in payload["positions"]
    ] == [
        ("legacy.damage_1", 0, "classVU.Sp[1]", "classVN.Rk[1]", None),
        ("legacy.damage_2", 1, "classVU.Sp[2]", "classVN.Rk[2]", None),
    ]


def test_adapter_preserves_value_type_order_and_actor_state() -> None:
    insurer = Insurer(entity_id=11, premiums_current_sector=[10.25, -0.0])
    policyholder = Policyholder(
        entity_id=7,
        chosen_insurer_sector_current=[None, 11],
    )
    insurer_before = json.dumps(asdict(insurer), sort_keys=True)
    policyholder_before = json.dumps(asdict(policyholder), sort_keys=True)

    vu_values = adapt_legacy_damage_vector(insurer.premiums_current_sector)
    vn_values = adapt_legacy_damage_vector(policyholder.chosen_insurer_sector_current)

    assert [(item.legacy_sector_id, item.python_vector_index, item.value) for item in vu_values] == [
        ("legacy.damage_1", 0, 10.25),
        ("legacy.damage_2", 1, -0.0),
    ]
    assert [item.value for item in vn_values] == [None, 11]
    assert type(vn_values[1].value) is int
    assert all(item.mapped_sector_id is None for item in (*vu_values, *vn_values))
    assert json.dumps(asdict(insurer), sort_keys=True) == insurer_before
    assert json.dumps(asdict(policyholder), sort_keys=True) == policyholder_before
    with pytest.raises(FrozenInstanceError):
        vu_values[0].value = 99.0  # type: ignore[misc]


@pytest.mark.parametrize("index", [-1, 2, True, 0.0, "0"])
def test_legacy_sector_id_rejects_wrong_index(index: object) -> None:
    with pytest.raises(ValueError, match="0 oder 1"):
        legacy_damage_sector_id(index)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "values",
    [[], [1], [1, 2, 3], "12", [True, 1], ["1", 2], [float("nan"), 2], [1, float("inf")]],
)
def test_adapter_rejects_incompatible_vectors(values: object) -> None:
    with pytest.raises(ValueError, match="Historischer Schadenvektor"):
        adapt_legacy_damage_vector(values)  # type: ignore[arg-type]
