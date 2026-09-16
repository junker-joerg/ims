"""Read-only sector identities; no binding to the historical two-slot model."""

from dataclasses import asdict, dataclass
from enum import StrEnum


SECTOR_TAXONOMY_VERSION = "ims.sector-taxonomy.v1"


class SectorModelFamily(StrEnum):
    NON_LIFE = "non_life"
    LIFE = "life"
    HEALTH = "health"


@dataclass(frozen=True, slots=True)
class SectorDefinition:
    sector_id: str
    display_name: str
    model_family: SectorModelFamily
    modelling_status: str = "taxonomy_only"


@dataclass(frozen=True, slots=True)
class LegacySectorPosition:
    python_vector_index: int
    historical_vu_field: str
    historical_vn_field: str
    mapped_sector_id: None = None


SECTOR_DEFINITIONS = (
    SectorDefinition("motor", "Kfz", SectorModelFamily.NON_LIFE),
    SectorDefinition("property_liability", "Sach-Haftpflicht", SectorModelFamily.NON_LIFE),
    SectorDefinition("life", "Leben", SectorModelFamily.LIFE),
    SectorDefinition("health", "Kranken", SectorModelFamily.HEALTH),
)

LEGACY_SECTOR_POSITIONS = (
    LegacySectorPosition(0, "classVU.Sp[1]", "classVN.Rk[1]"),
    LegacySectorPosition(1, "classVU.Sp[2]", "classVN.Rk[2]"),
)


def sector_taxonomy_payload() -> dict[str, object]:
    """Return versioned identities without changing any simulation state."""

    return {
        "schema_version": SECTOR_TAXONOMY_VERSION,
        "mode": "sector_taxonomy_read_only",
        "scope": "planned_model_sectors",
        "historical_full_equality_claim": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "sectors": [asdict(sector) for sector in SECTOR_DEFINITIONS],
        "legacy_vector": {
            "mapping_status": "unresolved",
            "positions": [asdict(position) for position in LEGACY_SECTOR_POSITIONS],
        },
        "extension_contract": {
            "identity_key": "sector_id",
            "legacy_positions_are_sector_ids": False,
            "legacy_state_unchanged": True,
            "explicit_adapter_required": True,
            "new_sector_state_available": False,
            "per_sector_strategy_assignment_available": False,
            "per_sector_balance_available": False,
        },
    }
