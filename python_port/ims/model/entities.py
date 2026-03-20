from dataclasses import dataclass, field


@dataclass(slots=True)
class BaseEntity:
    """
    Minimaler gemeinsamer Platzhalter für fachliche Entitäten.

    In späteren PRs werden daraus konkretere Typen wie BAV, VU und VN
    abgeleitet oder separat modelliert.
    """

    entity_id: int
    active: bool = True


@dataclass(slots=True)
class BAVForeignInfoInsurer:
    """Kleiner Container für wenige VU-bezogene Fremdinformationen des BAV-Service."""

    dp: float = 0.0
    dw: float = 0.0
    pm: float = 0.0
    wm: float = 0.0
    mp: float = 0.0
    mw: float = 0.0


@dataclass(slots=True)
class BAVForeignInfoPolicyholder:
    """Kleiner Container für wenige VN-bezogene Fremdinformationen des BAV-Service."""

    dg: float = 0.0


@dataclass(slots=True)
class BAVServiceState:
    """
    Kleiner Servicezustand für den ersten historischen BAV-Slice.

    Dies ist bewusst keine vollständige Portierung historischer Vektorstrukturen,
    sondern nur ein enger Datencontainer für wenige Fremdinformationswerte.
    """

    insurer: BAVForeignInfoInsurer = field(default_factory=BAVForeignInfoInsurer)
    policyholder: BAVForeignInfoPolicyholder = field(default_factory=BAVForeignInfoPolicyholder)


@dataclass(slots=True)
class BAV(BaseEntity):
    """Kleiner Zustandscontainer für eine BAV-nahe Entität."""

    name: str = ""
    last_update_period: int | None = None
    last_update_logtime: int | None = None
    last_active_insurer_count: int = 0
    last_active_policyholder_count: int = 0
    last_sample_token: float | None = None
    service_state: BAVServiceState = field(default_factory=BAVServiceState)


@dataclass(slots=True)
class Insurer(BaseEntity):
    """
    Kleiner Zustandscontainer für einen Versicherer.

    Die *_prev-Felder sind bewusst nur kleine Vorperioden-Snapshots für den
    ersten BAV-Service-Slice und keine vollständige historische Vektorportierung.
    """

    name: str = ""
    premiums_prev: float = 0.0
    advertising_prev: float = 0.0
    reserves_prev: float = 0.0


@dataclass(slots=True)
class Policyholder(BaseEntity):
    """
    Kleiner Zustandscontainer für einen Versicherungsnehmer.

    Das Vorperiodenfeld ist bewusst nur ein kleiner Snapshot für den ersten
    BAV-Service-Slice.
    """

    name: str = ""
    insurer_id: int | None = None
    insured_prev: float = 0.0
