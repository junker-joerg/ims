from pathlib import Path


DOC = Path("docs/migration/vn_rule_family_imsvnr.md")
README = Path("docs/migration/README.md")


def test_vn_rule_family_imsvnr_mapping_is_documented() -> None:
    doc = DOC.read_text(encoding="utf-8")

    for rule_id in range(1, 7):
        suffix = f"{rule_id:02d}"
        assert f"IMSVNR{suffix}.DAT" in doc
        assert f"Vrvn{suffix}" in doc
        assert f"imsvnr{suffix}.dat" in doc
        assert f"`rule = {rule_id}`" in doc

    assert "`II`" in doc
    assert "policyholder_rule" in doc
    assert "keine historische Vollgleichheitsbehauptung" in doc
    assert "keine neue VN-Regelentscheidung" in doc
    assert "keine Simulation" in doc


def test_vn_rule_family_imsvnr_document_is_listed() -> None:
    readme = README.read_text(encoding="utf-8")

    assert "vn_rule_family_imsvnr.md" in readme
    assert "IMSVNR01.DAT` bis `IMSVNR06.DAT" in readme
