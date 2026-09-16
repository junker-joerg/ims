import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ROADMAP = REPO_ROOT / "docs" / "plans" / "ims_2x_all_lines_management_lab_roadmap.md"
GUIDE = REPO_ROOT / "docs" / "handbook" / "management_seminar_guide.md"


def test_active_roadmap_covers_all_committed_product_directions() -> None:
    document = ROADMAP.read_text(encoding="utf-8")
    normalized = " ".join(document.split())

    for phrase in (
        "Kfz, Sach-Haftpflicht, Leben und Kranken",
        "Modellbilanz je Versicherer",
        "Solvency-II-Kapitalansicht",
        "DORA-bezogene operative Wirkungsketten",
        "nichttechnische, visuelle Bedienung",
        "CSV, JSON und XLSX",
    ):
        assert phrase in normalized

    assert "kein Compliance-Score" in normalized
    assert "kein Audit" in normalized
    assert "keine Rechtsberatung" in normalized
    assert "diagnostischer Legacy-Benchmark" in normalized
    assert "kein Zwang zur Reproduktion unbelegter alter Zufallsfolgen" in normalized


def test_active_roadmap_numbers_pr142_through_pr182_without_gaps() -> None:
    document = ROADMAP.read_text(encoding="utf-8")
    table_prs = [
        int(match)
        for match in re.findall(r"^\| PR(\d+) \|", document, flags=re.MULTILINE)
    ]

    assert table_prs == list(range(142, 183))
    assert "bedienbarer 100-Perioden-Lauf mit Ergebnis und Export | PR151 | 10" in document
    assert "vier Modellsegmente und konsolidierte Versichererbilanz | PR162 | 21" in document
    assert "erklaerbare Solvency-II-Kapitalansicht | PR170 | 29" in document
    assert "durchgaengige DORA-Wirkungskette | PR178 | 37" in document
    assert "kontrollierte Managementseminar-Reife | PR182 | 41" in document
    assert "PR154 umgesetzt, PR155 naechster Schritt" in document
    assert "PR143 hat die kanonische Fuenf-Perioden-Kette gebaut" in document
    assert "PR145 hat kontrollierten Serverstart" in document
    assert "PR146 hat den Pfad in der Workbench bedienbar gemacht" in document
    assert "PR147 hat fuer 10, 25, 50 und 100 Perioden" in document
    assert "technischer 100-Perioden-Lauf | PR149 | 8 | 0" in document
    assert "bedienbarer 100-Perioden-Lauf mit Ergebnis und Export | PR151 | 10 | 0" in document
    assert "kontrollierte Managementseminar-Reife | PR182 | 41 | 28" in document


def test_roadmap_defines_scope_estimate_and_validation_gates() -> None:
    document = ROADMAP.read_text(encoding="utf-8")

    assert "13.700-25.000 LoC" in document
    assert "Unsicherheit von etwa acht zusaetzlichen PRs" in document
    for gate in (
        "deterministische Wiederholung",
        "stabile Prefixe",
        "Bilanz-, Bestands-, Mengen- und Aggregatinvarianten",
        "Browserabnahme auf breitem und schmalem Viewport",
        "CSV-, JSON- und XLSX-Exporte",
    ):
        assert gate in document


def test_management_guide_is_nontechnical_honest_and_visual() -> None:
    document = GUIDE.read_text(encoding="utf-8")
    normalized = " ".join(document.split())

    assert "Handbuchschnitt: HB3e" in document
    assert "## Sieben Vorteile im Fuehrungskraefteseminar" in document
    assert "## Ein Seminar in 90 Minuten" in document
    assert "## Arbeitsblatt fuer eine Wirkungskette" in document
    assert "## Geeignete Seminarfaelle" in document
    assert "Noch nicht verfuegbar sind" in document
    assert "gefuehrter Aufbau der 100 Einzelkandidaten" in normalized
    assert "rechtliche DORA-Konformitaet" in normalized
    assert "/api/" not in document
    assert "DTO" not in document
    assert "pytest" not in document

    image_paths = re.findall(r"!\[[^]]*\]\((images/[^)]+)\)", document)
    assert len(image_paths) >= 5
    for relative_path in image_paths:
        assert (GUIDE.parent / relative_path).is_file(), relative_path


def test_handbook_and_strategy_indexes_link_active_roadmap() -> None:
    handbook_index = (REPO_ROOT / "docs" / "handbook" / "README.md").read_text(
        encoding="utf-8"
    )
    plans_index = (REPO_ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (REPO_ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "management_seminar_guide.md" in handbook_index
    assert ROADMAP.name in handbook_index
    assert ROADMAP.name in plans_index
    assert ROADMAP.name in strategy_index
