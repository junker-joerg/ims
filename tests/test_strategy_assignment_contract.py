import json
from dataclasses import replace

from ims.strategies import (
    STRATEGY_ASSIGNMENT_CONTRACT_VERSION,
    STRATEGY_ASSIGNMENT_TARGETS,
    STRATEGY_PARAMETER_SCHEMAS,
    StrategyActorType,
    build_vdefmd6_strategy_assignment_profiles,
    strategy_assignment_contract_issues,
    strategy_assignment_contract_payload,
)


def test_assignment_targets_cover_catalog_by_actor_without_group_or_schedule() -> None:
    insurer, policyholder = STRATEGY_ASSIGNMENT_TARGETS

    assert insurer.actor_type is StrategyActorType.INSURER
    assert insurer.eligible_strategy_ids == tuple(
        f"vu.vrvu{rule_id:02d}" for rule_id in range(1, 11)
    )
    assert policyholder.actor_type is StrategyActorType.POLICYHOLDER
    assert policyholder.eligible_strategy_ids == tuple(
        f"vn.vrvn{rule_id:02d}" for rule_id in range(1, 7)
    )
    assert all(
        target.assignment_scope == "individual_actor"
        and target.assignment_cardinality == "zero_or_one_catalog_strategy_per_actor"
        and not target.group_assignment_supported
        and not target.scheduled_strategy_switch_supported
        for target in STRATEGY_ASSIGNMENT_TARGETS
    )


def test_parameter_schemas_match_existing_parameterized_strategies() -> None:
    assert len(STRATEGY_PARAMETER_SCHEMAS) == 13
    assert sum(len(schema.strategy_ids) for schema in STRATEGY_PARAMETER_SCHEMAS) == 15
    assert all(
        not schema.editing_enabled
        and not schema.defaults_declared
        and not schema.new_domain_bounds_declared
        for schema in STRATEGY_PARAMETER_SCHEMAS
    )
    assert strategy_assignment_contract_issues() == ()

    sample_search = next(
        schema
        for schema in STRATEGY_PARAMETER_SCHEMAS
        if schema.schema_id == "VNSampleSearchInsuranceRuleParameters"
    )
    assert [(field.field_name, field.python_type) for field in sample_search.fields] == [
        ("insurance_thresholds_normal", "list[float]"),
        ("insurance_thresholds_shock", "list[float]"),
        ("sample_sizes_normal", "list[int]"),
        ("sample_sizes_shock", "list[int]"),
    ]
    assert sample_search.fields[-1].existing_validation == "non_negative_integer_coercion"
    assert all(
        field.value_shape == "legacy_two_sector_vector"
        for schema in STRATEGY_PARAMETER_SCHEMAS
        for field in schema.fields
    )


def test_vdefmd6_source_profiles_preserve_assignments_and_activation() -> None:
    profiles = build_vdefmd6_strategy_assignment_profiles()
    vu = [profile for profile in profiles if profile.actor_type is StrategyActorType.INSURER]
    vn = [profile for profile in profiles if profile.actor_type is StrategyActorType.POLICYHOLDER]

    assert [
        (profile.target_id_start, profile.target_id_end, profile.strategy_id)
        for profile in vu
    ] == [
        (1, 2, "vu.vrvu01"),
        (3, 4, "vu.vrvu02"),
        (5, 7, "vu.vrvu03"),
        (8, 10, "vu.vrvu04"),
        (11, 13, "vu.vrvu05"),
        (14, 14, "vu.vrvu06"),
        (15, 16, "vu.vrvu06"),
        (17, 19, "vu.vrvu07"),
        (20, 22, "vu.vrvu08"),
        (23, 25, "vu.vrvu09"),
    ]
    assert [
        (
            profile.target_id_start,
            profile.target_id_end,
            profile.strategy_id,
            profile.activation_period,
        )
        for profile in vn
    ] == [
        (1, 15, "vn.vrvn01", 1),
        (16, 30, "vn.vrvn02", 1),
        (31, 60, "vn.vrvn03", 1),
        (61, 90, "vn.vrvn04", 1),
        (91, 120, "vn.vrvn05", 1),
        (121, 150, "vn.vrvn06", 1),
        (151, 190, "vn.vrvn03", 50),
        (191, 200, "vn.vrvn02", 50),
    ]
    assert sum(profile.target_count for profile in vu) == 25
    assert sum(profile.target_count for profile in vn) == 200
    assert vu[5].legacy_parameter_fingerprint != vu[6].legacy_parameter_fingerprint
    assert not any(profile.strategy_id == "vu.vrvu10" for profile in profiles)
    assert next(profile for profile in vn if profile.strategy_id == "vn.vrvn01").parameter_schema is None
    assert all(not profile.parameter_values_exposed for profile in profiles)


def test_assignment_payload_keeps_sector_and_execution_boundaries_closed() -> None:
    payload = strategy_assignment_contract_payload()

    assert payload["schema_version"] == STRATEGY_ASSIGNMENT_CONTRACT_VERSION
    assert payload["catalog_schema_version"] == "ims.strategy-catalog.v1"
    assert payload["mode"] == "strategy_assignment_contract_read_only"
    assert payload["source_summary"] == {
        "model": "Vdefmd6",
        "profile_count": 18,
        "insurer_count": 25,
        "policyholder_count": 200,
        "parameter_values_exposed": False,
    }
    assert payload["sector_contract"] == {
        "mode": "legacy_two_position_vector",
        "position_count": 2,
        "position_keys": ("legacy_sector_1", "legacy_sector_2"),
        "python_indices": (0, 1),
        "named_sectors_available": False,
        "strategy_shared_across_positions": True,
        "sector_specific_strategy_supported": False,
        "additional_sectors_supported": False,
    }
    assert all(
        payload[key] is False
        for key in (
            "selection_enabled",
            "assignment_editing_enabled",
            "parameter_editing_enabled",
            "group_assignment_enabled",
            "sector_specific_strategy_enabled",
            "scheduled_strategy_switch_enabled",
            "writes_enabled",
            "execution_enabled",
            "simulation_performed",
            "historical_full_equality_claim",
        )
    )
    serialized = json.loads(json.dumps(payload, sort_keys=True))
    assert serialized["sector_contract"]["position_keys"] == [
        "legacy_sector_1",
        "legacy_sector_2",
    ]
    assert all(
        "parameters" not in profile and "parameter_values" not in profile
        for profile in serialized["source_profiles"]
    )


def test_assignment_validation_reports_target_schema_and_profile_drift() -> None:
    wrong_target = replace(
        STRATEGY_ASSIGNMENT_TARGETS[0],
        eligible_strategy_ids=STRATEGY_ASSIGNMENT_TARGETS[0].eligible_strategy_ids[:-1],
    )
    wrong_schema = replace(
        STRATEGY_PARAMETER_SCHEMAS[0],
        fields=STRATEGY_PARAMETER_SCHEMAS[0].fields[:-1],
    )
    missing_strategy_schema = replace(
        STRATEGY_PARAMETER_SCHEMAS[0],
        strategy_ids=(),
    )
    profiles = build_vdefmd6_strategy_assignment_profiles()
    unknown_profile = replace(profiles[0], strategy_id="vu.unknown")

    assert "Katalogstrategien passen nicht zum Zuordnungstyp: insurer" in (
        strategy_assignment_contract_issues(
            targets=(wrong_target, STRATEGY_ASSIGNMENT_TARGETS[1])
        )
    )
    assert "Parameterfelder weichen ab: VURandomUniformRuleParameters" in (
        strategy_assignment_contract_issues(
            schemas=(wrong_schema,) + STRATEGY_PARAMETER_SCHEMAS[1:]
        )
    )
    assert "Parametrisierte Strategien sind nicht exakt einmal zugeordnet" in (
        strategy_assignment_contract_issues(
            schemas=(missing_strategy_schema,) + STRATEGY_PARAMETER_SCHEMAS[1:]
        )
    )
    assert "Doppeltes Quellprofil: vdefmd6.vu.001-002" in (
        strategy_assignment_contract_issues(profiles=profiles + (profiles[0],))
    )
    assert "Unbekannte Strategie im Quellprofil: vdefmd6.vu.001-002" in (
        strategy_assignment_contract_issues(
            profiles=(unknown_profile,) + profiles[1:]
        )
    )
    assert "Nicht zugeordnete Vdefmd6-Subjekte: 225" in (
        strategy_assignment_contract_issues(profiles=())
    )
