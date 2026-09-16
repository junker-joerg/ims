"""Lossless read-only view of the two historical damage-sector positions."""

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from math import isfinite

from ims.model.sector_taxonomy import LEGACY_SECTOR_POSITIONS, SECTOR_TAXONOMY_VERSION


LEGACY_DAMAGE_ADAPTER_VERSION = "ims.legacy-damage-adapter.v1"
LEGACY_DAMAGE_SECTOR_IDS = ("legacy.damage_1", "legacy.damage_2")


@dataclass(frozen=True, slots=True)
class LegacyDamageValue:
    legacy_sector_id: str
    python_vector_index: int
    value: int | float | None
    mapped_sector_id: None = None


def legacy_damage_sector_id(index: int) -> str:
    """Map an existing Python/export index to its neutral legacy identity."""

    if type(index) is not int or index not in range(len(LEGACY_DAMAGE_SECTOR_IDS)):
        raise ValueError("Historischer Schadenindex muss 0 oder 1 sein")
    return LEGACY_DAMAGE_SECTOR_IDS[index]


def adapt_legacy_damage_vector(
    values: Sequence[int | float | None],
) -> tuple[LegacyDamageValue, LegacyDamageValue]:
    """Annotate a two-position scalar vector without converting or changing values."""

    if not isinstance(values, (list, tuple)) or len(values) != 2:
        raise ValueError("Historischer Schadenvektor muss genau zwei Positionen haben")
    for value in values:
        if value is not None and type(value) not in (int, float):
            raise ValueError("Historischer Schadenvektor enthaelt keinen Skalar")
        if type(value) is float and not isfinite(value):
            raise ValueError("Historischer Schadenvektor enthaelt keinen endlichen Wert")
    return (
        LegacyDamageValue(legacy_damage_sector_id(0), 0, values[0]),
        LegacyDamageValue(legacy_damage_sector_id(1), 1, values[1]),
    )


def legacy_damage_adapter_contract_payload() -> dict[str, object]:
    """Describe proven positional mapping and the unresolved modern mapping."""

    return {
        "schema_version": LEGACY_DAMAGE_ADAPTER_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "mode": "legacy_damage_adapter_read_only",
        "historical_full_equality_claim": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "legacy_vector_length": len(LEGACY_DAMAGE_SECTOR_IDS),
        "modern_sector_mapping_status": "unresolved",
        "positions": [
            {
                **asdict(position),
                "legacy_sector_id": legacy_damage_sector_id(position.python_vector_index),
            }
            for position in LEGACY_SECTOR_POSITIONS
        ],
    }
