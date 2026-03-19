"""Foundational context objects for the IMS Python port."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class InventoryContext:
    """Minimal shared runtime context placeholder.

    The scaffold intentionally stores only generic metadata so package
    boundaries can be exercised before domain logic is migrated.
    """

    name: str = "ims"
    metadata: dict[str, Any] = field(default_factory=dict)
