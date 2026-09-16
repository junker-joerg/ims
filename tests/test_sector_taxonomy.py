import json
from dataclasses import FrozenInstanceError

import pytest

from ims.model.sector_taxonomy import (
    LEGACY_SECTOR_POSITIONS,
    SECTOR_DEFINITIONS,
    SECTOR_TAXONOMY_VERSION,
    SectorModelFamily,
    sector_taxonomy_payload,
)


def test_taxonomy_has_four_distinct_planned_model_sectors() -> None:
    assert [(sector.sector_id, sector.display_name, sector.model_family) for sector in SECTOR_DEFINITIONS] == [
        ("motor", "Kfz", SectorModelFamily.NON_LIFE),
        ("property_liability", "Sach-Haftpflicht", SectorModelFamily.NON_LIFE),
        ("life", "Leben", SectorModelFamily.LIFE),
        ("health", "Kranken", SectorModelFamily.HEALTH),
    ]
    assert all(sector.modelling_status == "taxonomy_only" for sector in SECTOR_DEFINITIONS)
    assert len({sector.sector_id for sector in SECTOR_DEFINITIONS}) == 4


def test_historical_positions_remain_unmapped_and_separate() -> None:
    assert [(position.python_vector_index, position.historical_vu_field, position.historical_vn_field) for position in LEGACY_SECTOR_POSITIONS] == [
        (0, "classVU.Sp[1]", "classVN.Rk[1]"),
        (1, "classVU.Sp[2]", "classVN.Rk[2]"),
    ]
    assert all(position.mapped_sector_id is None for position in LEGACY_SECTOR_POSITIONS)
    with pytest.raises(FrozenInstanceError):
        LEGACY_SECTOR_POSITIONS[0].mapped_sector_id = "motor"  # type: ignore[misc]


def test_taxonomy_payload_is_serializable_and_excludes_implicit_adapter() -> None:
    payload = json.loads(json.dumps(sector_taxonomy_payload(), sort_keys=True))

    assert payload["schema_version"] == SECTOR_TAXONOMY_VERSION
    assert payload["mode"] == "sector_taxonomy_read_only"
    assert payload["historical_full_equality_claim"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["legacy_vector"]["mapping_status"] == "unresolved"
    assert [item["mapped_sector_id"] for item in payload["legacy_vector"]["positions"]] == [None, None]
    assert payload["extension_contract"]["explicit_adapter_required"] is True
    assert payload["extension_contract"]["new_sector_state_available"] is False
