from dataclasses import asdict, dataclass
from enum import StrEnum


STRATEGY_CATALOG_VERSION = "ims.strategy-catalog.v1"


class StrategyActorType(StrEnum):
    """Akteurstyp, dessen Verhalten die Strategie beschreibt."""

    INSURER = "insurer"
    POLICYHOLDER = "policyholder"


class StrategyImplementationStatus(StrEnum):
    """Technischer Stand des im Katalog referenzierten Rechenkerns."""

    PORTED_EXPLICIT_CORE = "ported_explicit_core"


class StrategyTestStatus(StrEnum):
    """Konservativer Mindeststand der vorhandenen Tests."""

    UNIT_TESTED = "unit_tested"
    UNIT_AND_REGRESSION_TESTED = "unit_and_regression_tested"


@dataclass(frozen=True, slots=True)
class StrategyFamilyDefinition:
    """Moderne Gruppierung historischer Regeln, ohne neue Fachsemantik."""

    family_id: str
    actor_type: StrategyActorType
    display_name: str
    description: str
    taxonomy_only: bool = True


@dataclass(frozen=True, slots=True)
class StrategyDefinition:
    """Read-only Herkunfts-, Implementierungs- und Testvertrag einer Regel."""

    strategy_id: str
    actor_type: StrategyActorType
    display_name: str
    family_id: str
    historical_action: str
    historical_rule_id: int
    historical_rule_class: int | None
    included_in_vdefmd6: bool
    source_file: str
    source_chapter: str
    implementation_status: StrategyImplementationStatus
    implementation_module: str
    implementation_entrypoint: str
    parameter_schema: str | None
    parameterized: bool
    parameter_capabilities: tuple[str, ...]
    test_status: StrategyTestStatus
    test_evidence: tuple[str, ...]
    notes: str = ""
    implementation_variant: str | None = None


STRATEGY_FAMILIES = (
    StrategyFamilyDefinition(
        family_id="vu.random",
        actor_type=StrategyActorType.INSURER,
        display_name="Zufallsbasierte Preis- und Werberegeln",
        description="Historische VU-Zufallsregeln mit expliziten Ziehungen.",
    ),
    StrategyFamilyDefinition(
        family_id="vu.experience_markup",
        actor_type=StrategyActorType.INSURER,
        display_name="Erfahrungsbasierte Mark-Up-Regeln",
        description="Reaktive VU-Regeln auf Reserve-, Wechsler- oder Marktanteilsbasis.",
    ),
    StrategyFamilyDefinition(
        family_id="vu.claims_oriented",
        actor_type=StrategyActorType.INSURER,
        display_name="Schadenorientierte Regel",
        description="VU-Regel auf Basis des erwarteten Schadens.",
    ),
    StrategyFamilyDefinition(
        family_id="vu.market_information",
        actor_type=StrategyActorType.INSURER,
        display_name="Markt- und Fremdinformationsregeln",
        description="VU-Regeln auf Basis aggregierter Marktinformationen.",
    ),
    StrategyFamilyDefinition(
        family_id="vu.free_definition",
        actor_type=StrategyActorType.INSURER,
        display_name="Frei definierbare Regel",
        description="Historische lineare VU-Regel ausserhalb der Vdefmd6-Gruppen.",
    ),
    StrategyFamilyDefinition(
        family_id="vn.random_and_compulsory",
        actor_type=StrategyActorType.POLICYHOLDER,
        display_name="Pflicht- und Zufallswahl",
        description="Historische VN-Regeln fuer Pflichtversicherung und Zufallsauswahl.",
    ),
    StrategyFamilyDefinition(
        family_id="vn.preference_and_experience",
        actor_type=StrategyActorType.POLICYHOLDER,
        display_name="Praeferenz und Erfahrung",
        description="VN-Wahl nach Werbung oder eigener Praemienhistorie.",
    ),
    StrategyFamilyDefinition(
        family_id="vn.market_search",
        actor_type=StrategyActorType.POLICYHOLDER,
        display_name="Marktsuche und Information",
        description="VN-Wahl aus Stichprobe oder vollstaendiger Marktinformation.",
    ),
)


_VU_UNIT_TEST = "tests/test_vu_rules.py"
_VN_UNIT_TEST = "tests/test_vn_insurance_rules.py"
_VU_MODULE = "ims.model.vu_rules"
_VN_MODULE = "ims.model.vn_insurance_rules"
_PORTED = StrategyImplementationStatus.PORTED_EXPLICIT_CORE
_UNIT = StrategyTestStatus.UNIT_TESTED
_REGRESSION = StrategyTestStatus.UNIT_AND_REGRESSION_TESTED


STRATEGY_DEFINITIONS = (
    StrategyDefinition(
        "vu.vrvu01",
        StrategyActorType.INSURER,
        "Zufall I",
        "vu.random",
        "Vrvu01",
        1,
        1,
        True,
        "IMS.E",
        "3.3.1.1",
        _PORTED,
        _VU_MODULE,
        "apply_vu_random_uniform_rule",
        "VURandomUniformRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "explicit_uniform_draws"),
        _REGRESSION,
        (_VU_UNIT_TEST, "tests/test_tenth_fachlicher_vu_random_carryover_regression.py"),
    ),
    StrategyDefinition(
        "vu.vrvu02",
        StrategyActorType.INSURER,
        "Zufall II",
        "vu.random",
        "Vrvu02",
        2,
        1,
        True,
        "IMS.E",
        "3.3.1.1",
        _PORTED,
        _VU_MODULE,
        "apply_vu_random_normal_rule",
        "VURandomNormalRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "explicit_normal_draws"),
        _UNIT,
        (_VU_UNIT_TEST,),
    ),
    StrategyDefinition(
        "vu.vrvu03",
        StrategyActorType.INSURER,
        "Mark-Up I",
        "vu.experience_markup",
        "Vrvu03",
        3,
        2,
        True,
        "IMS.E",
        "3.3.1.2",
        _PORTED,
        _VU_MODULE,
        "apply_vu_reserve_markup_rule",
        "VUReserveMarkupRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "reserve_threshold"),
        _UNIT,
        (_VU_UNIT_TEST,),
    ),
    StrategyDefinition(
        "vu.vrvu04",
        StrategyActorType.INSURER,
        "Mark-Up II",
        "vu.experience_markup",
        "Vrvu04",
        4,
        2,
        True,
        "IMS.E",
        "3.3.1.2",
        _PORTED,
        _VU_MODULE,
        "apply_vu_net_switcher_markup_rule",
        "VUNetSwitcherMarkupRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "net_switcher_threshold"),
        _REGRESSION,
        (_VU_UNIT_TEST, "tests/test_third_fachlicher_vu_carryover_regression.py"),
    ),
    StrategyDefinition(
        "vu.vrvu05",
        StrategyActorType.INSURER,
        "Mark-Up III",
        "vu.experience_markup",
        "Vrvu05",
        5,
        2,
        True,
        "IMS.E",
        "3.3.1.2",
        _PORTED,
        _VU_MODULE,
        "apply_vu_market_share_markup_rule",
        "VUMarketShareMarkupRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "market_share_threshold"),
        _UNIT,
        (_VU_UNIT_TEST,),
    ),
    StrategyDefinition(
        "vu.vrvu06",
        StrategyActorType.INSURER,
        "Erwartungsschaden",
        "vu.claims_oriented",
        "Vrvu06",
        6,
        2,
        True,
        "IMS.E",
        "3.3.1.2",
        _PORTED,
        _VU_MODULE,
        "apply_vu_expected_claim_rule",
        "VUExpectedClaimRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "expected_claim"),
        _UNIT,
        (_VU_UNIT_TEST,),
    ),
    StrategyDefinition(
        "vu.vrvu07",
        StrategyActorType.INSURER,
        "Dumping",
        "vu.market_information",
        "Vrvu07",
        7,
        3,
        True,
        "IMS.E",
        "3.3.1.3",
        _PORTED,
        _VU_MODULE,
        "apply_vu_foreign_info_rule",
        "VUForeignInfoRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "market_foreign_information"),
        _UNIT,
        (_VU_UNIT_TEST,),
        "Dispatch-Variante dumping.",
        implementation_variant="dumping",
    ),
    StrategyDefinition(
        "vu.vrvu08",
        StrategyActorType.INSURER,
        "Durchschnitt",
        "vu.market_information",
        "Vrvu08",
        8,
        3,
        True,
        "IMS.E",
        "3.3.1.3",
        _PORTED,
        _VU_MODULE,
        "apply_vu_foreign_info_rule",
        "VUForeignInfoRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "market_foreign_information"),
        _REGRESSION,
        (_VU_UNIT_TEST, "tests/test_third_fachlicher_vu_carryover_regression.py"),
        "Dispatch-Variante average.",
        implementation_variant="average",
    ),
    StrategyDefinition(
        "vu.vrvu09",
        StrategyActorType.INSURER,
        "Angriff",
        "vu.market_information",
        "Vrvu09",
        9,
        3,
        True,
        "IMS.E",
        "3.3.1.3",
        _PORTED,
        _VU_MODULE,
        "apply_vu_foreign_info_rule",
        "VUForeignInfoRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "market_foreign_information"),
        _UNIT,
        (_VU_UNIT_TEST,),
        "Dispatch-Variante attack.",
        implementation_variant="attack",
    ),
    StrategyDefinition(
        "vu.vrvu10",
        StrategyActorType.INSURER,
        "Frei definierbar",
        "vu.free_definition",
        "Vrvu10",
        10,
        None,
        False,
        "IMS.E",
        "3.3.1.3",
        _PORTED,
        _VU_MODULE,
        "apply_vu_free_linear_rule",
        "VUFreeLinearRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "linear_price_and_advertising"),
        _UNIT,
        (_VU_UNIT_TEST,),
        "Historisch vorhanden, aber nicht Teil der Vdefmd6-Regelgruppen.",
    ),
    StrategyDefinition(
        "vn.vrvn01",
        StrategyActorType.POLICYHOLDER,
        "Zufall I / Pflichtversicherung",
        "vn.random_and_compulsory",
        "Vrvn01",
        1,
        1,
        True,
        "IMS.E",
        "3.3.2.1",
        _PORTED,
        _VN_MODULE,
        "apply_vn_compulsory_insurance_rule",
        None,
        False,
        ("two_sector", "explicit_insurer_choice_draws"),
        _REGRESSION,
        (_VN_UNIT_TEST, "tests/test_ninth_fachlicher_vn_damage_settlement_breadth.py"),
        "Die bestehende Portierung bildet die Pflichtversicherungsentscheidung explizit ab.",
    ),
    StrategyDefinition(
        "vn.vrvn02",
        StrategyActorType.POLICYHOLDER,
        "Zufall II",
        "vn.random_and_compulsory",
        "Vrvn02",
        2,
        1,
        True,
        "IMS.E",
        "3.3.2.1",
        _PORTED,
        _VN_MODULE,
        "apply_vn_random_insurance_rule",
        "VNRandomInsuranceRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "explicit_status_and_choice_draws"),
        _REGRESSION,
        (_VN_UNIT_TEST, "tests/test_eighth_fachlicher_vn_random_regression.py"),
    ),
    StrategyDefinition(
        "vn.vrvn03",
        StrategyActorType.POLICYHOLDER,
        "Praeferenz",
        "vn.preference_and_experience",
        "Vrvn03",
        3,
        2,
        True,
        "IMS.E",
        "3.3.2.2",
        _PORTED,
        _VN_MODULE,
        "apply_vn_preference_insurance_rule",
        "VNPreferenceInsuranceRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "advertising_preference"),
        _REGRESSION,
        (_VN_UNIT_TEST, "tests/test_seventh_fachlicher_vn_preference_regression.py"),
    ),
    StrategyDefinition(
        "vn.vrvn04",
        StrategyActorType.POLICYHOLDER,
        "Totale Erinnerung",
        "vn.preference_and_experience",
        "Vrvn04",
        4,
        2,
        True,
        "IMS.E",
        "3.3.2.2",
        _PORTED,
        _VN_MODULE,
        "apply_vn_search_insurance_rule",
        "VNSearchInsuranceRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "own_premium_history"),
        _REGRESSION,
        (_VN_UNIT_TEST, "tests/test_sixth_fachlicher_vn_search_history_regression.py"),
    ),
    StrategyDefinition(
        "vn.vrvn05",
        StrategyActorType.POLICYHOLDER,
        "Suche",
        "vn.market_search",
        "Vrvn05",
        5,
        3,
        True,
        "IMS.E",
        "3.3.2.3",
        _PORTED,
        _VN_MODULE,
        "apply_vn_sample_search_insurance_rule",
        "VNSampleSearchInsuranceRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "sample_size", "information_cost"),
        _REGRESSION,
        (_VN_UNIT_TEST, "tests/test_fifth_fachlicher_vn_sample_search_regression.py"),
    ),
    StrategyDefinition(
        "vn.vrvn06",
        StrategyActorType.POLICYHOLDER,
        "Beste Information",
        "vn.market_search",
        "Vrvn06",
        6,
        3,
        True,
        "IMS.E",
        "3.3.2.3",
        _PORTED,
        _VN_MODULE,
        "apply_vn_best_info_insurance_rule",
        "VNBestInfoInsuranceRuleParameters",
        True,
        ("two_sector", "normal_and_change_shock", "full_market_information", "information_cost"),
        _REGRESSION,
        (
            _VN_UNIT_TEST,
            "tests/test_second_fachlicher_vn_rule_snapshot_regression.py",
            "tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py",
        ),
    ),
)


def list_strategy_definitions(
    *,
    actor_type: StrategyActorType | str | None = None,
    family_id: str | None = None,
) -> tuple[StrategyDefinition, ...]:
    """Liefert Katalogeintraege in stabiler historischer Reihenfolge."""

    resolved_actor = StrategyActorType(actor_type) if actor_type is not None else None
    return tuple(
        strategy
        for strategy in STRATEGY_DEFINITIONS
        if (resolved_actor is None or strategy.actor_type is resolved_actor)
        and (family_id is None or strategy.family_id == family_id)
    )


def get_strategy_definition(strategy_id: str) -> StrategyDefinition:
    """Liefert genau einen Katalogeintrag oder meldet eine unbekannte ID."""

    for strategy in STRATEGY_DEFINITIONS:
        if strategy.strategy_id == strategy_id:
            return strategy
    raise KeyError(f"Unbekannte Strategie-ID: {strategy_id}")


def strategy_catalog_issues(
    families: tuple[StrategyFamilyDefinition, ...] = STRATEGY_FAMILIES,
    strategies: tuple[StrategyDefinition, ...] = STRATEGY_DEFINITIONS,
) -> tuple[str, ...]:
    """Prueft den internen Katalogvertrag ohne Datei-I/O oder Regelaufruf."""

    issues: list[str] = []
    family_by_id: dict[str, StrategyFamilyDefinition] = {}
    for family in families:
        if family.family_id in family_by_id:
            issues.append(f"Doppelte Familie: {family.family_id}")
        family_by_id[family.family_id] = family
        if not family.taxonomy_only:
            issues.append(f"Familie ist nicht als reine Taxonomie markiert: {family.family_id}")

    seen_strategy_ids: set[str] = set()
    seen_actions: set[tuple[StrategyActorType, str]] = set()
    for strategy in strategies:
        if strategy.strategy_id in seen_strategy_ids:
            issues.append(f"Doppelte Strategie-ID: {strategy.strategy_id}")
        seen_strategy_ids.add(strategy.strategy_id)

        action_key = (strategy.actor_type, strategy.historical_action)
        if action_key in seen_actions:
            issues.append(f"Doppelte historische Aktion: {strategy.historical_action}")
        seen_actions.add(action_key)

        family = family_by_id.get(strategy.family_id)
        if family is None:
            issues.append(f"Unbekannte Familie fuer {strategy.strategy_id}: {strategy.family_id}")
        elif family.actor_type is not strategy.actor_type:
            issues.append(f"Akteurstyp passt nicht zur Familie: {strategy.strategy_id}")

        if strategy.included_in_vdefmd6 and strategy.historical_rule_class is None:
            issues.append(f"Vdefmd6-Regel ohne Regelklasse: {strategy.strategy_id}")
        if not strategy.parameterized and strategy.parameter_schema is not None:
            issues.append(f"Nicht parametrisierte Regel mit Parameterschema: {strategy.strategy_id}")
        if strategy.parameterized and strategy.parameter_schema is None:
            issues.append(f"Parametrisierte Regel ohne Parameterschema: {strategy.strategy_id}")
        if not strategy.test_evidence:
            issues.append(f"Regel ohne Testnachweis: {strategy.strategy_id}")

        is_foreign_info = strategy.implementation_entrypoint == "apply_vu_foreign_info_rule"
        if is_foreign_info and strategy.implementation_variant not in {"dumping", "average", "attack"}:
            issues.append(f"Fremdinformationsregel ohne gueltige Variante: {strategy.strategy_id}")
        if not is_foreign_info and strategy.implementation_variant is not None:
            issues.append(f"Unerwartete Implementierungsvariante: {strategy.strategy_id}")

    used_family_ids = {strategy.family_id for strategy in strategies}
    for family in families:
        if family.family_id not in used_family_ids:
            issues.append(f"Leere Familie: {family.family_id}")
    return tuple(issues)


def strategy_catalog_payload() -> dict[str, object]:
    """Erzeugt den serialisierbaren Vertrag fuer die API-/UI-Nutzung."""

    return {
        "schema_version": STRATEGY_CATALOG_VERSION,
        "mode": "strategy_catalog_read_only",
        "scope": "read_only_strategy_metadata",
        "historical_full_equality_claim": False,
        "selection_enabled": False,
        "parameter_editing_enabled": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "families": [asdict(family) for family in STRATEGY_FAMILIES],
        "strategies": [asdict(strategy) for strategy in STRATEGY_DEFINITIONS],
    }
