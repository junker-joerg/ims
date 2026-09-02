from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
from hashlib import sha256
import importlib
import json

from ims.model.vdefmd6_population import (
    VDEFMD6_INSURER_COUNT,
    VDEFMD6_POLICYHOLDER_COUNT,
    Vdefmd6InsurerDefinition,
    Vdefmd6PolicyholderDefinition,
    build_vdefmd6_population,
)
from ims.strategies.catalog import (
    STRATEGY_CATALOG_VERSION,
    STRATEGY_DEFINITIONS,
    StrategyActorType,
    get_strategy_definition,
    list_strategy_definitions,
)


STRATEGY_ASSIGNMENT_CONTRACT_VERSION = "ims.strategy-assignment-contract.v1"


@dataclass(frozen=True, slots=True)
class StrategySectorContract:
    """Heutige Sektorgrenze ohne vorweggenommene moderne Spartenlogik."""

    mode: str = "legacy_two_position_vector"
    position_count: int = 2
    position_keys: tuple[str, str] = ("legacy_sector_1", "legacy_sector_2")
    python_indices: tuple[int, int] = (0, 1)
    named_sectors_available: bool = False
    strategy_shared_across_positions: bool = True
    sector_specific_strategy_supported: bool = False
    additional_sectors_supported: bool = False


@dataclass(frozen=True, slots=True)
class StrategyAssignmentTargetDefinition:
    """Zulaessiger Akteurstyp und heutige Zuordnungsgranularitaet."""

    actor_type: StrategyActorType
    entity_type: str
    entity_id_field: str
    legacy_rule_id_field: str
    legacy_rule_class_field: str
    assignment_scope: str
    assignment_cardinality: str
    eligible_strategy_ids: tuple[str, ...]
    group_assignment_supported: bool = False
    scheduled_strategy_switch_supported: bool = False


@dataclass(frozen=True, slots=True)
class StrategyParameterFieldDefinition:
    """Lesende Beschreibung eines bereits vorhandenen Parameterfelds."""

    field_name: str
    display_name: str
    python_type: str
    value_shape: str = "legacy_two_sector_vector"
    required_by_existing_loader: bool = True
    existing_validation: str = "numeric_coercion_without_domain_bounds"


@dataclass(frozen=True, slots=True)
class StrategyParameterSchemaDefinition:
    """Vertrag eines vorhandenen Dataclass- und Mapping-Loaders."""

    schema_id: str
    actor_type: StrategyActorType
    module: str
    loader_entrypoint: str
    strategy_ids: tuple[str, ...]
    fields: tuple[StrategyParameterFieldDefinition, ...]
    editing_enabled: bool = False
    defaults_declared: bool = False
    new_domain_bounds_declared: bool = False


@dataclass(frozen=True, slots=True)
class StrategySourceAssignmentProfile:
    """Zusammenhaengende, quellgebundene Vdefmd6-Zuordnungsgruppe."""

    profile_id: str
    source_model: str
    actor_type: StrategyActorType
    target_id_start: int
    target_id_end: int
    target_count: int
    strategy_id: str
    historical_rule_id: int
    historical_rule_class: int
    activation_period: int
    active_through_run: int
    logical_time: int
    parameter_schema: str | None
    legacy_parameter_value_count: int
    legacy_parameter_fingerprint: str
    parameter_values_exposed: bool = False


def _field(
    field_name: str,
    display_name: str,
    *,
    python_type: str = "list[float]",
    existing_validation: str = "numeric_coercion_without_domain_bounds",
) -> StrategyParameterFieldDefinition:
    return StrategyParameterFieldDefinition(
        field_name=field_name,
        display_name=display_name,
        python_type=python_type,
        existing_validation=existing_validation,
    )


_RANDOM_UNIFORM_FIELDS = (
    _field("premium_factor_normal", "Praemienfaktor Normalfall"),
    _field("advertising_factor_normal", "Werbefaktor Normalfall"),
    _field("premium_factor_shock", "Praemienfaktor Aenderungsschock"),
    _field("advertising_factor_shock", "Werbefaktor Aenderungsschock"),
)

_LINEAR_FIELDS = (
    _field("premium_intercept_normal", "Praemienabschnitt Normalfall"),
    _field("premium_factor_normal", "Praemienfaktor Normalfall"),
    _field("advertising_intercept_normal", "Werbeabschnitt Normalfall"),
    _field("advertising_factor_normal", "Werbefaktor Normalfall"),
    _field("premium_intercept_shock", "Praemienabschnitt Aenderungsschock"),
    _field("premium_factor_shock", "Praemienfaktor Aenderungsschock"),
    _field("advertising_intercept_shock", "Werbeabschnitt Aenderungsschock"),
    _field("advertising_factor_shock", "Werbefaktor Aenderungsschock"),
)

_MARKUP_FIELDS = (
    _field("premium_below_normal", "Praemienfaktor unter Anspruch Normalfall"),
    _field("premium_above_normal", "Praemienfaktor ueber Anspruch Normalfall"),
    _field("advertising_below_normal", "Werbefaktor unter Anspruch Normalfall"),
    _field("advertising_above_normal", "Werbefaktor ueber Anspruch Normalfall"),
    _field("premium_below_shock", "Praemienfaktor unter Anspruch Aenderungsschock"),
    _field("premium_above_shock", "Praemienfaktor ueber Anspruch Aenderungsschock"),
    _field("advertising_below_shock", "Werbefaktor unter Anspruch Aenderungsschock"),
    _field("advertising_above_shock", "Werbefaktor ueber Anspruch Aenderungsschock"),
)

_VN_THRESHOLD_FIELDS = (
    _field("insurance_thresholds_normal", "Versicherungsschwelle Normalfall"),
    _field("insurance_thresholds_shock", "Versicherungsschwelle Aenderungsschock"),
)

_VN_SAMPLE_FIELDS = _VN_THRESHOLD_FIELDS + (
    _field(
        "sample_sizes_normal",
        "Stichprobengroesse Normalfall",
        python_type="list[int]",
        existing_validation="non_negative_integer_coercion",
    ),
    _field(
        "sample_sizes_shock",
        "Stichprobengroesse Aenderungsschock",
        python_type="list[int]",
        existing_validation="non_negative_integer_coercion",
    ),
)


STRATEGY_PARAMETER_SCHEMAS = (
    StrategyParameterSchemaDefinition(
        "VURandomUniformRuleParameters",
        StrategyActorType.INSURER,
        "ims.model.vu_rules",
        "vu_random_uniform_rule_parameters_from_mapping",
        ("vu.vrvu01",),
        _RANDOM_UNIFORM_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VURandomNormalRuleParameters",
        StrategyActorType.INSURER,
        "ims.model.vu_rules",
        "vu_random_normal_rule_parameters_from_mapping",
        ("vu.vrvu02",),
        _LINEAR_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VUReserveMarkupRuleParameters",
        StrategyActorType.INSURER,
        "ims.model.vu_rules",
        "vu_reserve_markup_rule_parameters_from_mapping",
        ("vu.vrvu03",),
        _MARKUP_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VUNetSwitcherMarkupRuleParameters",
        StrategyActorType.INSURER,
        "ims.model.vu_rules",
        "vu_net_switcher_markup_rule_parameters_from_mapping",
        ("vu.vrvu04",),
        _MARKUP_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VUMarketShareMarkupRuleParameters",
        StrategyActorType.INSURER,
        "ims.model.vu_rules",
        "vu_market_share_markup_rule_parameters_from_mapping",
        ("vu.vrvu05",),
        _MARKUP_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VUExpectedClaimRuleParameters",
        StrategyActorType.INSURER,
        "ims.model.vu_rules",
        "vu_expected_claim_rule_parameters_from_mapping",
        ("vu.vrvu06",),
        _MARKUP_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VUForeignInfoRuleParameters",
        StrategyActorType.INSURER,
        "ims.model.vu_rules",
        "vu_foreign_info_rule_parameters_from_mapping",
        ("vu.vrvu07", "vu.vrvu08", "vu.vrvu09"),
        _LINEAR_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VUFreeLinearRuleParameters",
        StrategyActorType.INSURER,
        "ims.model.vu_rules",
        "vu_free_linear_rule_parameters_from_mapping",
        ("vu.vrvu10",),
        _LINEAR_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VNRandomInsuranceRuleParameters",
        StrategyActorType.POLICYHOLDER,
        "ims.model.vn_insurance_rules",
        "vn_random_insurance_rule_parameters_from_mapping",
        ("vn.vrvn02",),
        _VN_THRESHOLD_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VNPreferenceInsuranceRuleParameters",
        StrategyActorType.POLICYHOLDER,
        "ims.model.vn_insurance_rules",
        "vn_preference_insurance_rule_parameters_from_mapping",
        ("vn.vrvn03",),
        _VN_THRESHOLD_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VNSearchInsuranceRuleParameters",
        StrategyActorType.POLICYHOLDER,
        "ims.model.vn_insurance_rules",
        "vn_search_insurance_rule_parameters_from_mapping",
        ("vn.vrvn04",),
        _VN_THRESHOLD_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VNSampleSearchInsuranceRuleParameters",
        StrategyActorType.POLICYHOLDER,
        "ims.model.vn_insurance_rules",
        "vn_sample_search_insurance_rule_parameters_from_mapping",
        ("vn.vrvn05",),
        _VN_SAMPLE_FIELDS,
    ),
    StrategyParameterSchemaDefinition(
        "VNBestInfoInsuranceRuleParameters",
        StrategyActorType.POLICYHOLDER,
        "ims.model.vn_insurance_rules",
        "vn_best_info_insurance_rule_parameters_from_mapping",
        ("vn.vrvn06",),
        _VN_THRESHOLD_FIELDS,
    ),
)


STRATEGY_ASSIGNMENT_TARGETS = (
    StrategyAssignmentTargetDefinition(
        actor_type=StrategyActorType.INSURER,
        entity_type="ims.model.entities.Insurer",
        entity_id_field="entity_id",
        legacy_rule_id_field="rule_id",
        legacy_rule_class_field="rule_class",
        assignment_scope="individual_actor",
        assignment_cardinality="zero_or_one_catalog_strategy_per_actor",
        eligible_strategy_ids=tuple(
            strategy.strategy_id
            for strategy in list_strategy_definitions(actor_type=StrategyActorType.INSURER)
        ),
    ),
    StrategyAssignmentTargetDefinition(
        actor_type=StrategyActorType.POLICYHOLDER,
        entity_type="ims.model.entities.Policyholder",
        entity_id_field="entity_id",
        legacy_rule_id_field="rule_id",
        legacy_rule_class_field="rule_class",
        assignment_scope="individual_actor",
        assignment_cardinality="zero_or_one_catalog_strategy_per_actor",
        eligible_strategy_ids=tuple(
            strategy.strategy_id
            for strategy in list_strategy_definitions(actor_type=StrategyActorType.POLICYHOLDER)
        ),
    ),
)


_SourceDefinition = Vdefmd6InsurerDefinition | Vdefmd6PolicyholderDefinition


def _strategy_for_rule(
    actor_type: StrategyActorType,
    historical_rule_id: int,
) -> str:
    matches = tuple(
        strategy.strategy_id
        for strategy in list_strategy_definitions(actor_type=actor_type)
        if strategy.historical_rule_id == historical_rule_id
    )
    if len(matches) != 1:
        raise ValueError(
            f"Historische Regel {actor_type}/{historical_rule_id} ist nicht eindeutig katalogisiert"
        )
    return matches[0]


def _parameter_fingerprint(values: tuple[float, ...]) -> str:
    encoded = json.dumps(list(values), separators=(",", ":"), ensure_ascii=True)
    return f"sha256:{sha256(encoded.encode('ascii')).hexdigest()}"


def _profile_signature(definition: _SourceDefinition) -> tuple[object, ...]:
    return (
        definition.action.rule_id,
        definition.rule_class,
        definition.activation.activation_period,
        definition.activation.active_through_run,
        definition.action.logical_time,
        definition.parameters,
    )


def _build_actor_profiles(
    actor_type: StrategyActorType,
    definitions: tuple[_SourceDefinition, ...],
) -> tuple[StrategySourceAssignmentProfile, ...]:
    ordered = tuple(sorted(definitions, key=lambda item: item.entity_id))
    groups: list[list[_SourceDefinition]] = []
    for definition in ordered:
        if (
            groups
            and definition.entity_id == groups[-1][-1].entity_id + 1
            and _profile_signature(definition) == _profile_signature(groups[-1][-1])
        ):
            groups[-1].append(definition)
        else:
            groups.append([definition])

    prefix = "vu" if actor_type is StrategyActorType.INSURER else "vn"
    profiles: list[StrategySourceAssignmentProfile] = []
    for group in groups:
        first = group[0]
        last = group[-1]
        strategy_id = _strategy_for_rule(actor_type, first.action.rule_id)
        strategy = get_strategy_definition(strategy_id)
        profiles.append(
            StrategySourceAssignmentProfile(
                profile_id=(
                    f"vdefmd6.{prefix}.{first.entity_id:03d}-{last.entity_id:03d}"
                ),
                source_model="Vdefmd6",
                actor_type=actor_type,
                target_id_start=first.entity_id,
                target_id_end=last.entity_id,
                target_count=len(group),
                strategy_id=strategy_id,
                historical_rule_id=first.action.rule_id,
                historical_rule_class=first.rule_class,
                activation_period=first.activation.activation_period,
                active_through_run=first.activation.active_through_run,
                logical_time=first.action.logical_time,
                parameter_schema=strategy.parameter_schema,
                legacy_parameter_value_count=len(first.parameters),
                legacy_parameter_fingerprint=_parameter_fingerprint(first.parameters),
            )
        )
    return tuple(profiles)


def build_vdefmd6_strategy_assignment_profiles() -> tuple[StrategySourceAssignmentProfile, ...]:
    """Leitet die belegten Gruppen ohne Regelaufruf aus dem Populationsvertrag ab."""

    population = build_vdefmd6_population()
    return _build_actor_profiles(
        StrategyActorType.INSURER,
        population.insurer_definitions,
    ) + _build_actor_profiles(
        StrategyActorType.POLICYHOLDER,
        population.policyholder_definitions,
    )


def _schema_by_id(
    schemas: tuple[StrategyParameterSchemaDefinition, ...],
) -> dict[str, StrategyParameterSchemaDefinition]:
    return {schema.schema_id: schema for schema in schemas}


def strategy_assignment_contract_issues(
    *,
    targets: tuple[StrategyAssignmentTargetDefinition, ...] = STRATEGY_ASSIGNMENT_TARGETS,
    schemas: tuple[StrategyParameterSchemaDefinition, ...] = STRATEGY_PARAMETER_SCHEMAS,
    profiles: tuple[StrategySourceAssignmentProfile, ...] | None = None,
) -> tuple[str, ...]:
    """Prueft Katalog-, Dataclass- und Vdefmd6-Bindung ohne Ausfuehrung."""

    issues: list[str] = []
    resolved_profiles = (
        profiles
        if profiles is not None
        else build_vdefmd6_strategy_assignment_profiles()
    )
    catalog_by_id = {
        strategy.strategy_id: strategy for strategy in STRATEGY_DEFINITIONS
    }

    targets_by_actor = {target.actor_type: target for target in targets}
    if len(targets_by_actor) != len(targets):
        issues.append("Doppelter Akteurstyp im Zuordnungsvertrag")
    for actor_type in StrategyActorType:
        target = targets_by_actor.get(actor_type)
        if target is None:
            issues.append(f"Fehlender Zuordnungstyp: {actor_type}")
            continue
        expected = tuple(
            strategy.strategy_id
            for strategy in list_strategy_definitions(actor_type=actor_type)
        )
        if target.eligible_strategy_ids != expected:
            issues.append(f"Katalogstrategien passen nicht zum Zuordnungstyp: {actor_type}")
        if target.group_assignment_supported or target.scheduled_strategy_switch_supported:
            issues.append(f"Nicht freigegebene Zuordnungsfunktion: {actor_type}")

    schemas_by_id = _schema_by_id(schemas)
    if len(schemas_by_id) != len(schemas):
        issues.append("Doppeltes Parameterschema")
    expected_schema_ids = {
        strategy.parameter_schema
        for strategy in STRATEGY_DEFINITIONS
        if strategy.parameter_schema is not None
    }
    if set(schemas_by_id) != expected_schema_ids:
        issues.append("Parameterschemata decken den Strategiekatalog nicht exakt ab")

    declared_parameterized_strategy_ids = tuple(
        strategy_id
        for schema in schemas
        for strategy_id in schema.strategy_ids
    )
    expected_parameterized_strategy_ids = tuple(
        strategy.strategy_id
        for strategy in STRATEGY_DEFINITIONS
        if strategy.parameter_schema is not None
    )
    if (
        len(set(declared_parameterized_strategy_ids))
        != len(declared_parameterized_strategy_ids)
        or set(declared_parameterized_strategy_ids)
        != set(expected_parameterized_strategy_ids)
    ):
        issues.append("Parametrisierte Strategien sind nicht exakt einmal zugeordnet")

    for schema in schemas:
        module = importlib.import_module(schema.module)
        parameter_type = getattr(module, schema.schema_id, None)
        if not isinstance(parameter_type, type) or not is_dataclass(parameter_type):
            issues.append(f"Parameterschema ist keine Dataclass: {schema.schema_id}")
            continue
        actual_fields = tuple((item.name, str(item.type)) for item in fields(parameter_type))
        declared_fields = tuple((item.field_name, item.python_type) for item in schema.fields)
        if actual_fields != declared_fields:
            issues.append(f"Parameterfelder weichen ab: {schema.schema_id}")
        if not callable(getattr(module, schema.loader_entrypoint, None)):
            issues.append(f"Parameterloader fehlt: {schema.loader_entrypoint}")
        for strategy_id in schema.strategy_ids:
            strategy = catalog_by_id.get(strategy_id)
            if strategy is None:
                issues.append(f"Unbekannte Strategie im Parameterschema: {strategy_id}")
                continue
            if strategy.actor_type is not schema.actor_type:
                issues.append(f"Akteurstyp des Parameterschemas weicht ab: {strategy_id}")
            if strategy.parameter_schema != schema.schema_id:
                issues.append(f"Strategie verweist auf anderes Parameterschema: {strategy_id}")
        if schema.editing_enabled or schema.defaults_declared or schema.new_domain_bounds_declared:
            issues.append(f"Nicht freigegebene Parameterfunktion: {schema.schema_id}")

    population = build_vdefmd6_population()
    source_definitions: dict[tuple[StrategyActorType, int], _SourceDefinition] = {
        **{
            (StrategyActorType.INSURER, item.entity_id): item
            for item in population.insurer_definitions
        },
        **{
            (StrategyActorType.POLICYHOLDER, item.entity_id): item
            for item in population.policyholder_definitions
        },
    }
    covered: set[tuple[StrategyActorType, int]] = set()
    seen_profile_ids: set[str] = set()
    for profile in resolved_profiles:
        if profile.profile_id in seen_profile_ids:
            issues.append(f"Doppeltes Quellprofil: {profile.profile_id}")
        seen_profile_ids.add(profile.profile_id)
        if profile.target_count != profile.target_id_end - profile.target_id_start + 1:
            issues.append(f"Ungueltige Zielspanne: {profile.profile_id}")
        strategy = catalog_by_id.get(profile.strategy_id)
        if strategy is None:
            issues.append(f"Unbekannte Strategie im Quellprofil: {profile.profile_id}")
        else:
            if strategy.actor_type is not profile.actor_type:
                issues.append(f"Akteurstyp des Quellprofils weicht ab: {profile.profile_id}")
            if strategy.parameter_schema != profile.parameter_schema:
                issues.append(f"Parameterschema des Quellprofils weicht ab: {profile.profile_id}")
        if profile.parameter_values_exposed:
            issues.append(f"Quellprofil legt Parameterwerte offen: {profile.profile_id}")
        for entity_id in range(profile.target_id_start, profile.target_id_end + 1):
            key = (profile.actor_type, entity_id)
            if key in covered:
                issues.append(f"Mehrfach zugeordnetes Quellsubjekt: {profile.actor_type}/{entity_id}")
                continue
            covered.add(key)
            definition = source_definitions.get(key)
            if definition is None:
                issues.append(f"Unbekanntes Quellsubjekt: {profile.actor_type}/{entity_id}")
                continue
            expected_strategy_id = _strategy_for_rule(
                profile.actor_type,
                definition.action.rule_id,
            )
            expected_values = (
                expected_strategy_id,
                definition.action.rule_id,
                definition.rule_class,
                definition.activation.activation_period,
                definition.activation.active_through_run,
                definition.action.logical_time,
                len(definition.parameters),
                _parameter_fingerprint(definition.parameters),
            )
            actual_values = (
                profile.strategy_id,
                profile.historical_rule_id,
                profile.historical_rule_class,
                profile.activation_period,
                profile.active_through_run,
                profile.logical_time,
                profile.legacy_parameter_value_count,
                profile.legacy_parameter_fingerprint,
            )
            if actual_values != expected_values:
                issues.append(f"Quellbindung weicht ab: {profile.actor_type}/{entity_id}")

    missing = set(source_definitions) - covered
    extra = covered - set(source_definitions)
    if missing:
        issues.append(f"Nicht zugeordnete Vdefmd6-Subjekte: {len(missing)}")
    if extra:
        issues.append(f"Zusaetzliche Vdefmd6-Subjekte: {len(extra)}")
    return tuple(issues)


def strategy_assignment_contract_payload() -> dict[str, object]:
    """Liefert den versionierten, rein lesenden Zuordnungsvertrag."""

    profiles = build_vdefmd6_strategy_assignment_profiles()
    return {
        "schema_version": STRATEGY_ASSIGNMENT_CONTRACT_VERSION,
        "catalog_schema_version": STRATEGY_CATALOG_VERSION,
        "mode": "strategy_assignment_contract_read_only",
        "scope": "eligibility_parameter_shapes_and_vdefmd6_source_profiles",
        "selection_enabled": False,
        "assignment_editing_enabled": False,
        "parameter_editing_enabled": False,
        "group_assignment_enabled": False,
        "sector_specific_strategy_enabled": False,
        "scheduled_strategy_switch_enabled": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_full_equality_claim": False,
        "sector_contract": asdict(StrategySectorContract()),
        "assignment_targets": [asdict(target) for target in STRATEGY_ASSIGNMENT_TARGETS],
        "parameter_schemas": [asdict(schema) for schema in STRATEGY_PARAMETER_SCHEMAS],
        "source_profiles": [asdict(profile) for profile in profiles],
        "source_summary": {
            "model": "Vdefmd6",
            "profile_count": len(profiles),
            "insurer_count": VDEFMD6_INSURER_COUNT,
            "policyholder_count": VDEFMD6_POLICYHOLDER_COUNT,
            "parameter_values_exposed": False,
        },
    }
