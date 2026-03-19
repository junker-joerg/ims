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

    entity_id: int
    active: bool = True


@dataclass(slots=True)
class BAV(BaseEntity):
    """Kleiner Zustandscontainer für eine BAV-nahe Entität."""

    name: str = ""
    last_update_period: int | None = None
    last_update_logtime: int | None = None
    last_active_insurer_count: int = 0
    last_active_policyholder_count: int = 0
    last_sample_token: float | None = None


@dataclass(slots=True)
class Insurer(BaseEntity):
    """Kleiner Zustandscontainer für einen Versicherer."""

    name: str = ""


@dataclass(slots=True)
class Policyholder(BaseEntity):
    """Kleiner Zustandscontainer für einen Versicherungsnehmer."""

    name: str = ""
    insurer_id: int | None = None
"""Placeholder module for future entity definitions.

This file reserves the import path for later PRs and intentionally omits
business fields and domain behavior.
"""
