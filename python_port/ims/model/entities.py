"""Technical placeholder for future IMS model entities.

This module establishes an importable location for later entity definitions
without introducing any migrated domain logic.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class EntityPlaceholder:
    """Minimal placeholder type for future entity definitions."""

    identifier: str = "placeholder"
