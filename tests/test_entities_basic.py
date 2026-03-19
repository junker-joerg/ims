from ims.model.entities import BAV, BaseEntity, Insurer, Policyholder


def test_entities_can_be_instantiated_with_minimal_fields() -> None:
    base = BaseEntity(entity_id=1)
    bav = BAV(entity_id=10, name="Basis-BAV")
    insurer = Insurer(entity_id=20, name="Muster-VU")
    policyholder = Policyholder(entity_id=30, name="Muster-VN", insurer_id=20)

    assert base.active is True
    assert bav.name == "Basis-BAV"
    assert insurer.entity_id == 20
    assert policyholder.insurer_id == 20
