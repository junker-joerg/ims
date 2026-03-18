"""Minimal entity definitions for the IMS Python port."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class InventoryEntity:
    """Generic entity placeholder used by the initial scaffold."""

    identifier: str
    attributes: dict[str, Any] = field(default_factory=dict)
