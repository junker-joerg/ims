from pathlib import Path


DOC = Path("docs/migration/parameter_output_vu014pr1.md")
README = Path("docs/migration/README.md")


def test_parameter_output_vu014pr1_inventory_is_documented() -> None:
    doc = DOC.read_text(encoding="utf-8")

    assert "VU014PR1.DAT" in doc
    assert "parameter_output" in doc
    assert "Pr1L1" in doc
    assert "Pr1l2" in doc
    assert "Pr1L5" in doc
    assert "3737" in doc
    assert "af8e58e6548582fde3d02c0f037bb1c89c71402649b1ab1f342a11dc9d78fecd" in doc
    assert "1-100" in doc
    assert "keine Simulation" in doc
    assert "keine neue Fachlogik" in doc
    assert "keine historische Vollgleichheitsbehauptung" in doc
    assert "Keine Uebernahme in `tests/references/legacy_agrsich/`" in doc
    assert "Keine Erweiterung von `tests/fixtures/legacy_validation_bundle.json`" in doc
    assert "Feldmapping bleibt offen" in doc


def test_parameter_output_vu014pr1_field_mapping_limits_are_documented() -> None:
    doc = DOC.read_text(encoding="utf-8")

    assert "IMSDATA.C" in doc
    assert "IMS.E" in doc
    assert "Pr[SIMLAENGE+1]" in doc
    assert "Pv[16]" in doc
    assert "VU[j].DatenVU->Sp[1].l.Pr[1]" in doc
    assert "VU14P1.DAT" in doc
    assert "VU14P2.DAT" in doc
    assert "IMSVU014.DAT" in doc
    assert "keine zweite `VU014PR1.DAT`-Variante" in doc


def test_parameter_output_vu014pr1_document_is_listed() -> None:
    readme = README.read_text(encoding="utf-8")

    assert "parameter_output_vu014pr1.md" in readme
    assert "VU014PR1.DAT" in readme
