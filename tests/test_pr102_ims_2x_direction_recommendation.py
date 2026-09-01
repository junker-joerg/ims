from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
STRATEGY_ROOT = REPO_ROOT / "docs" / "strategy"
RECOMMENDATION = STRATEGY_ROOT / "pr102_ims_2x_direction_recommendation.md"


def test_strategy_index_links_pr102_recommendation() -> None:
    index = (STRATEGY_ROOT / "README.md").read_text(encoding="utf-8")

    assert RECOMMENDATION.is_file()
    assert "pr102_ims_2x_direction_recommendation.md" in index
    assert "Grundlage fuer PR102" in index
    assert "noch keine aktive PR-Roadmap" in index


def test_recommendation_closes_legacy_equality_as_non_product_target() -> None:
    document = RECOMMENDATION.read_text(encoding="utf-8")
    normalized = " ".join(document.split())

    assert "15/15 Tabellen" in document
    assert "6.300/6.300" in document
    assert "`not_a_product_target`" in document
    assert "`accepted_diagnostic_benchmark`" in document
    assert "`modern_validation_program_required`" in document
    assert "`production_release_approved` bleibt in PR102 `false`" in normalized
    assert "Exakte historische Zufallsfolgen sind kein Produktziel" in normalized
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in normalized


def test_recommendation_defines_shared_ims_2x_product_modes() -> None:
    document = RECOMMENDATION.read_text(encoding="utf-8")

    for heading in (
        "### 1. Kalibrierte Marktrekonstruktion",
        "### 2. Regulationslabor als erstes Aushaengeschild",
        "### 3. Management-Simulation",
        "### 4. Forschungs- und Publikationsmodus",
        "## Warum keine vier getrennten Produkte",
    ):
        assert heading in document
    assert "IMS 2.x Insurance Market Simulation Lab" in document
    assert "allgemeines\nPlugin-Framework" in document
    assert "mindestens zwei reale Adapter" in document


def test_recommendation_makes_competence_and_ui_quality_visible() -> None:
    document = RECOMMENDATION.read_text(encoding="utf-8")
    normalized = " ".join(document.split())

    for phrase in (
        "versioniertes Run-Manifest",
        "sichtbare Datenprovenienz",
        "Sensitivitaetsbaender",
        "exportierbares Ergebnisdossier",
        "Baseline-gegen-Szenario-Vergleiche",
        "kuratierte Showcase-Szenarien",
    ):
        assert phrase in normalized
    assert "modernes wissenschaftliches Entscheidungswerkzeug" in normalized
    assert "Marketingseite ersetzt" in normalized


def test_recommendation_keeps_future_sequence_out_of_active_roadmap() -> None:
    document = RECOMMENDATION.read_text(encoding="utf-8")
    normalized = " ".join(document.split())

    assert "Kandidatenfolge, keine aktive PR-Roadmap" in normalized
    assert "Die Richtungsentscheidung ist erfolgt" in normalized
    assert "keine Aufnahme der Kandidatenfolge in die aktive Rest-PR-Planung" in normalized
    assert "keine Simulation oder Runnerausfuehrung" in normalized
    assert "keine Aenderung der Fachlogik" in normalized
