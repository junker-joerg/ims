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
    from ims.engine.scheduler import Scheduler
    from ims.model.entities import BaseEntity

    ctx = SimulationContext()
    scheduler = Scheduler()
    entity = BaseEntity(entity_id=1)

    assert ctx.period == 0
    assert scheduler.empty() is True
    assert entity.entity_id == 1
