from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCUMENT = REPO_ROOT / "docs" / "migration" / "historical_horizon_contract.md"
MIGRATION_README = REPO_ROOT / "docs" / "migration" / "README.md"


def test_repeat_contract_documentation_fixes_scope_and_limits() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "Vertrag: `pr98-v1`" in document
    assert "15 Exportidentitaeten / 19 Referenzziele" in document
    assert "**Gesamt**" in document and "6.300" in document
    assert "maximal 100 Perioden" in normalized
    assert "(rl-1)*sl+period" in document
    assert "30 Laeufe mit jeweils 100 Perioden" in normalized
    assert "keine Reproduktion der historischen RNG-Folge" in normalized
    assert "modernen 300- und 500-Perioden-Runner" in normalized
    assert "keine historische Vollgleichheit" in normalized
    assert "keine fachliche Produktionsfreigabe" in normalized
    assert "PR99 hat `imsvnr03.dat` bis `imsvnr06.dat`" in normalized
    assert "PR100" in normalized


def test_repeat_contract_documentation_keeps_vusk1_as_one_level_iv_export() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "Aggregatstufe IV" in document
    assert "`selector_kind = all`" in document
    assert "`selector_value = SK1`" in document
    assert "keine unterschiedlichen Aggregate oder Aggregatebenen" in normalized
    assert "| `VUSK1L1.DAT` | 401-500 | 5 | 1-100" in document
    assert "vusk1l4_direct_04410ef" in document
    assert "versioned_fixture_regression_only" in document
    assert "weder eine gemeinsame historische" in normalized


def test_migration_index_lists_horizon_contract() -> None:
    readme = MIGRATION_README.read_text(encoding="utf-8")

    assert DOCUMENT.is_file()
    assert "historical_horizon_contract.md" in readme
    assert "PR-98-Korrekturvertrag" in readme
