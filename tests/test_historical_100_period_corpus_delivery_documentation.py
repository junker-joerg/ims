from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCUMENT = (
    REPO_ROOT
    / "docs"
    / "migration"
    / "historical_100_period_corpus_delivery.md"
)
MIGRATION_README = REPO_ROOT / "docs" / "migration" / "README.md"


def test_delivery_documentation_fixes_scope_counts_and_boundaries() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "Vertrag: `pr93-v1`" in document
    assert "2 von 15" in document
    assert "200 von 6.300" in document
    assert "13 Exporte und 6.100" in normalized
    assert "`imsvu014.dat`" in document
    assert "`imsvnsk1.dat`" in document
    assert document.count("`wvemod1_archive`") == 2
    assert "`all` und `SK1`" in normalized
    assert "488/1.400 Felder" in document
    assert "264/1.300 Felder" in document
    assert "keine neue Fachlogik" in document
    assert "keine Simulation" in document
    assert "keine historische Vollgleichheitsbehauptung" in document
    assert "keine Produktionsfreigabe" in document


def test_delivery_documentation_names_pr94_and_stable_prefix() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")
    readme = MIGRATION_README.read_text(encoding="utf-8")

    assert DOCUMENT.is_file()
    assert "historical_100_period_corpus_delivery.md" in readme
    assert "PR94 hat den kontrollierten Zustand" in normalized
    assert "Perioden 1-100" in normalized
    assert "exakt unveraendert" in normalized
