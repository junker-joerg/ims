from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCUMENT = REPO_ROOT / "docs" / "migration" / "historical_horizon_contract.md"
MIGRATION_README = REPO_ROOT / "docs" / "migration" / "README.md"


def test_horizon_contract_documentation_fixes_scope_and_limits() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "Vertrag: `pr92-v1`" in document
    assert "15 Exportidentitaeten / 19 Referenzziele" in document
    assert "| Gesamt |" in document and "6.300" in document
    assert "Ein 300er-Snapshot muss" in document
    assert "Ein 500er-Snapshot muss" in normalized
    assert "exakte Gleichheit" in document
    assert "ohne Toleranz" in document
    assert "keinen 300-/500-Periodenlauf" in normalized
    assert "keine neue Fachlogik" in normalized
    assert "keine historische Vollgleichheit" in normalized
    assert "keine fachliche Produktionsfreigabe" in normalized
    assert "PR93 hat `imsvu014.dat` und `imsvnsk1.dat`" in normalized


def test_horizon_contract_documentation_keeps_vusk1_as_one_level_iv_export() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "Aggregatstufe IV" in document
    assert "`selector_kind = all`" in document
    assert "`selector_value = SK1`" in document
    assert "keine unterschiedlichen Aggregate oder Aggregatebenen" in normalized
    assert "vusk1l4_direct_04410ef" in document
    assert "versioned_fixture_regression_only" in document
    assert "weder eine gemeinsame historische" in normalized


def test_migration_index_lists_horizon_contract() -> None:
    readme = MIGRATION_README.read_text(encoding="utf-8")

    assert DOCUMENT.is_file()
    assert "historical_horizon_contract.md" in readme
    assert "PR-92-Vertrag" in readme
