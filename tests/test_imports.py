def test_package_imports() -> None:
    import ims
    import ims.model
    import ims.engine
    import ims.io
    import ims.analysis

    assert ims is not None
    assert ims.model is not None
    assert ims.engine is not None
    assert ims.io is not None
    assert ims.analysis is not None


def test_core_placeholders_import() -> None:
    from ims.engine.context import SimulationContext
    from ims.engine.scheduler import Event, Scheduler
    from ims.io.scenario_loader import LoadedScenario, load_scenario
    from ims.model.entities import BAV, BaseEntity, Insurer, Policyholder

    ctx = SimulationContext()
    scheduler = Scheduler()
    entity = BaseEntity(entity_id=1)
    event = Event(0, 0, 0, "entity", 1, "noop")
    scenario = load_scenario("tests/fixtures/minimal_scenario.json")

    assert ctx.period == 0
    assert scheduler.empty() is True
    assert entity.entity_id == 1
    assert event.action == "noop"
    assert BAV is not None
    assert Insurer is not None
    assert Policyholder is not None
    assert isinstance(scenario, LoadedScenario)
