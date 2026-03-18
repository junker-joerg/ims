from dataclasses import dataclass


@dataclass(slots=True)
class BaseEntity:
    """
    Minimaler gemeinsamer Platzhalter für fachliche Entitäten.

    In späteren PRs werden daraus konkretere Typen wie BAV, VU und VN
    abgeleitet oder separat modelliert.
    """
    entity_id: int
    active: bool = True
"""Analysis package placeholders for the IMS Python port."""
