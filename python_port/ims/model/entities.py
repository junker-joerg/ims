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
class BAVActivityState:
    """
    Kleiner Aktivitätscontainer für den erweiterten Frmdinf-Slice.

    Er hält Vorperioden- und aktuelle Aktivitätsmengen explizit getrennt, ohne bereits
    vollständige historische Aktivierungsschock- oder Regelvektoren zu modellieren.
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
    """Kleiner Aggregatzustand für den ersten substanziellen Agrsich-Slice."""

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


@dataclass(slots=True)
class BAVServiceState:
    """
    Servicezustand für den bislang portierten BAV-Servicekern.

    Dies bleibt bewusst eine kleine, strukturierte Abbildung für Fremdinformation,
    Aktivität, Aggregatideen und Berechnungsmetadaten und keine vollständige
    historische Vektorportierung.
    """

    insurer: BAVForeignInfoInsurer = field(default_factory=BAVForeignInfoInsurer)
    policyholder: BAVForeignInfoPolicyholder = field(default_factory=BAVForeignInfoPolicyholder)
    activity_state: BAVActivityState = field(default_factory=BAVActivityState)
    aggregate_state: BAVAggregateState = field(default_factory=BAVAggregateState)
    computation_meta: BAVServiceComputationMeta = field(default_factory=BAVServiceComputationMeta)


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

    Die *_prev-Felder, aktuellen Snapshots und Regelmarker bleiben bewusst klein und
    dienen nur den bislang portierten Frmdinf-/Agrsich-Slices.
    """

    name: str = ""
    premiums_prev: float = 0.0
    advertising_prev: float = 0.0
    reserves_prev: float = 0.0
    active_prev: bool = True
    rule_id: int | None = None
    rule_class: int | None = None
    premiums_current: float = 0.0
    advertising_current: float = 0.0
    reserves_current: float = 0.0
    policyholders_current: float = 0.0
    claims_count_current: list[int] = field(default_factory=lambda: [0, 0])
    claims_sum_current: list[float] = field(default_factory=lambda: [0.0, 0.0])


@dataclass(slots=True)
class Policyholder(BaseEntity):
    """
    Kleiner Zustandscontainer für einen Versicherungsnehmer.

    Auch hier bleiben Vorperiodenaktivität, aktuelle Snapshots und Regelmarker bewusst
    kleine, explizite Ausschnitte für die portierten BAV-Servicekerne.
    """

    name: str = ""
    insurer_id: int | None = None
    insured_prev: float = 0.0
    active_prev: bool = True
    rule_id: int | None = None
    rule_class: int | None = None
    insured_current: float = 0.0
    chosen_insurer_current: int | None = None
    paid_premium_current: list[float] = field(default_factory=lambda: [0.0, 0.0])
    self_damage_current: list[float] = field(default_factory=lambda: [0.0, 0.0])
    claim_sum_current: list[float] = field(default_factory=lambda: [0.0, 0.0])
    end_wealth_current: float = 0.0
