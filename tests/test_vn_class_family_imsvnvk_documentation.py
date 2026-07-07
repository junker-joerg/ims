from pathlib import Path


DOC = Path("docs/migration/vn_class_family_imsvnvk.md")
README = Path("docs/migration/README.md")


def test_vn_class_family_imsvnvk_mapping_is_documented() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for class_id in range(1, 4):
        assert f"IMSVNVK{class_id}.DAT" in doc
        assert f"imsvnvk{class_id}.dat" in doc
        assert f"`rule_class = {class_id}`" in doc

    assert "`III`" in doc
    assert "policyholder_class" in doc
    assert "WVEMOD1.ZIP" in doc
    assert "keine Simulation" in doc
    assert "keine neue Fachlogik" in doc
    assert "keine historische Vollgleichheit" in doc


def test_vn_class_family_imsvnvk_document_is_listed() -> None:
    readme = README.read_text(encoding="utf-8")

    assert "vn_class_family_imsvnvk.md" in readme
    assert "IMSVNVK1.DAT` bis `IMSVNVK3.DAT" in readme
