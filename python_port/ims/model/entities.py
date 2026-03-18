"""Conservative entity containers for the early IMS Python port.

These dataclasses only capture minimal identifying state needed for early
scenario loading. More detailed business attributes are intentionally deferred.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class BAV:
    """Minimal placeholder for a BAV-like aggregate or contract container."""

    identifier: str
    name: str
    # TODO: clarify which historical BAV fields are required for the first rule port.


@dataclass(slots=True)
class Insurer:
    """Minimal insurer container for scenario wiring."""

    identifier: str
    name: str
    # TODO: add only validated technical fields once legacy structures are mapped.


@dataclass(slots=True)
class Policyholder:
    """Minimal policyholder container with optional references.

    Optional references are included only to support lightweight scenario-based
    wiring between entities without introducing business rules.
    """

    identifier: str
    name: str
    insurer_id: str | None = None
    bav_id: str | None = None
    # TODO: defer products, contributions and market-specific fields.
