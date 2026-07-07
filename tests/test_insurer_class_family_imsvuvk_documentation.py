from pathlib import Path


DOC = Path("docs/migration/insurer_class_family_imsvuvk.md")
README = Path("docs/migration/README.md")


def test_insurer_class_family_imsvuvk_mapping_is_documented() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for class_id in range(1, 4):
        assert f"IMSVUVK{class_id}.DAT" in doc
        assert f"imsvuvk{class_id}.dat" in doc
        assert f"`rule_class = {class_id}`" in doc

    assert "`III`" in doc
    assert "insurer_class" in doc
    assert "WVEMOD1.ZIP" in doc
    assert "keine Simulation" in doc
    assert "keine neue Fachlogik" in doc
    assert "keine historische Vollgleichheit" in doc


def test_insurer_class_family_imsvuvk_document_is_listed() -> None:
    readme = README.read_text(encoding="utf-8")

    assert "insurer_class_family_imsvuvk.md" in readme
    assert "IMSVUVK1.DAT` bis `IMSVUVK3.DAT" in readme
