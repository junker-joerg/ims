"""Basic tests for early IMS entity containers."""

from ims.model.entities import BAV, Insurer, Policyholder


def test_entities_expose_only_minimal_identifying_state() -> None:
    bav = BAV(identifier="bav-1", name="Basis-BAV")
    insurer = Insurer(identifier="ins-1", name="MusterVersicherer")
    policyholder = Policyholder(
        identifier="ph-1",
        name="Erika Beispiel",
        insurer_id="ins-1",
        bav_id="bav-1",
    )

    assert bav.identifier == "bav-1"
    assert insurer.name == "MusterVersicherer"
    assert policyholder.insurer_id == "ins-1"
    assert policyholder.bav_id == "bav-1"
