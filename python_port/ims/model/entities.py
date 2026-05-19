from dataclasses import dataclass, field


@dataclass(slots=True)
class BaseEntity:
    """
    Minimaler gemeinsamer Platzhalter fuer fachliche Entitaeten.

    In spaeteren PRs werden daraus konkretere Typen wie BAV, VU und VN
    abgeleitet oder separat modelliert.
    """

    entity_id: int
    active: bool = True


@dataclass(slots=True)
class BAVForeignInfoInsurer:
    """Kleiner Container fuer wenige VU-bezogene Fremdinformationen des BAV-Service."""

    dp: list[float] = field(default_factory=lambda: [0.0, 0.0])
    dw: list[float] = field(default_factory=lambda: [0.0, 0.0])
    pm: list[float] = field(default_factory=lambda: [0.0, 0.0])
    wm: list[float] = field(default_factory=lambda: [0.0, 0.0])
    mp: list[float] = field(default_factory=lambda: [0.0, 0.0])
    mw: list[float] = field(default_factory=lambda: [0.0, 0.0])


@dataclass(slots=True)
class BAVForeignInfoPolicyholder:
    """Kleiner Container fuer wenige VN-bezogene Fremdinformationen des BAV-Service."""

    dg: list[float] = field(default_factory=lambda: [0.0, 0.0])


@dataclass(slots=True)
class BAVActivityState:
    """
    Kleiner Aktivitaetscontainer fuer den erweiterten Frmdinf-Slice.

    Er haelt Vorperioden- und aktuelle Aktivitaetsmengen explizit getrennt, ohne bereits
    vollstaendige historische Aktivierungsschock- oder Regelvektoren zu modellieren.
    """

    active_insurer_ids_prev: list[int] = field(default_factory=list)
    active_policyholder_ids_prev: list[int] = field(default_factory=list)
    active_insurer_ids_current: list[int] = field(default_factory=list)
    active_policyholder_ids_current: list[int] = field(default_factory=list)
    active_insurer_count_prev: int = 0
    active_policyholder_count_prev: int = 0
    active_insurer_count_current: int = 0
    active_policyholder_count_current: int = 0


@dataclass(slots=True)
class BAVAggregateState:
    """Kleiner Aggregatzustand fuer den ersten substanziellen Agrsich-Slice."""

    active_insurer_ids_current: list[int] = field(default_factory=list)
    active_policyholder_ids_current: list[int] = field(default_factory=list)
    insurer_rule_counts: dict[int | None, int] = field(default_factory=dict)
    insurer_rule_class_counts: dict[int | None, int] = field(default_factory=dict)
    policyholder_rule_counts: dict[int | None, int] = field(default_factory=dict)
    policyholder_rule_class_counts: dict[int | None, int] = field(default_factory=dict)
    last_agrsich_period: int | None = None


@dataclass(slots=True)
class BAVServiceComputationMeta:
    """Metadaten zum kleinen, quellenkritischen Frmdinf-Portierschnitt."""

    used_previous_period_values: bool = False
    foreign_info_available: bool = False
    leader_insurer_id: int | None = None
    leader_insurer_ids: list[int | None] = field(default_factory=lambda: [None, None])


@dataclass(slots=True)
class BAVServiceState:
    """
    Servicezustand fuer den bislang portierten BAV-Servicekern.

    Dies bleibt bewusst eine kleine, strukturierte Abbildung fuer Fremdinformation,
    Aktivitaet, Aggregatideen und Berechnungsmetadaten und keine vollstaendige
    historische Vektorportierung.
    """

    insurer: BAVForeignInfoInsurer = field(default_factory=BAVForeignInfoInsurer)
    policyholder: BAVForeignInfoPolicyholder = field(default_factory=BAVForeignInfoPolicyholder)
    activity_state: BAVActivityState = field(default_factory=BAVActivityState)
    aggregate_state: BAVAggregateState = field(default_factory=BAVAggregateState)
    computation_meta: BAVServiceComputationMeta = field(default_factory=BAVServiceComputationMeta)


@dataclass(slots=True)
class BAV(BaseEntity):
    """Kleiner Zustandscontainer fuer eine BAV-nahe Entitaet."""

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
    Kleiner Zustandscontainer fuer einen Versicherer.

    Die *_prev-Felder, aktuellen Snapshots und Regelmarker bleiben bewusst klein und
    dienen nur den bislang portierten Frmdinf-/Agrsich-Slices. Fuer den validierten
    Versicherer-Agrsich-Export werden aktuelle Reserven jetzt sektorgetrennt gefuehrt.
    """

    name: str = ""
    premiums_prev: float = 0.0
    advertising_prev: float = 0.0
    reserves_prev: float = 0.0
    premiums_prev_sector: list[float] = field(default_factory=list)
    advertising_prev_sector: list[float] = field(default_factory=list)
    reserves_prev_sector: list[float] = field(default_factory=list)
    active_prev: bool = True
    rule_id: int | None = None
    rule_class: int | None = None
    premiums_current: float = 0.0
    advertising_current: float = 0.0
    premiums_current_sector: list[float] = field(default_factory=list)
    advertising_current_sector: list[float] = field(default_factory=list)
    reserves_current: list[float] = field(default_factory=lambda: [0.0, 0.0])
    policyholders_current: float = 0.0
    claims_count_current: list[int] = field(default_factory=lambda: [0, 0])
    claims_sum_current: list[float] = field(default_factory=lambda: [0.0, 0.0])


@dataclass(slots=True)
class Policyholder(BaseEntity):
    """
    Kleiner Zustandscontainer fuer einen Versicherungsnehmer.

    Auch hier bleiben Vorperiodenaktivitaet, aktuelle Snapshots und Regelmarker bewusst
    kleine, explizite Ausschnitte fuer die portierten BAV-Servicekerne.
    """

    name: str = ""
    insurer_id: int | None = None
    insured_prev: float = 0.0
    insured_prev_sector: list[float] = field(default_factory=list)
    active_prev: bool = True
    rule_id: int | None = None
    rule_class: int | None = None
    insured_current: float = 0.0
    chosen_insurer_current: int | None = None
    chosen_insurer_sector_current: list[int | None] = field(default_factory=lambda: [None, None])
    paid_premium_current: list[float] = field(default_factory=lambda: [0.0, 0.0])
    self_damage_current: list[float] = field(default_factory=lambda: [0.0, 0.0])
    claim_sum_current: list[float] = field(default_factory=lambda: [0.0, 0.0])
    end_wealth_sector_current: list[float] = field(default_factory=lambda: [0.0, 0.0])
    end_wealth_current: float = 0.0
