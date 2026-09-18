import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ROADMAP = REPO_ROOT / "docs" / "plans" / "ims_2x_all_lines_management_lab_roadmap.md"
GUIDE = REPO_ROOT / "docs" / "handbook" / "management_seminar_guide.md"
WINDOWS_PLAN = REPO_ROOT / "docs" / "plans" / "ims_2x_windows_ready_to_run_packaging_plan.md"
LIFE_PLAN = REPO_ROOT / "docs" / "plans" / "ims_2x_life_workshop_expansion_plan.md"


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


def test_active_roadmap_numbers_pr142_through_pr192_without_gaps() -> None:
    document = ROADMAP.read_text(encoding="utf-8")
    table_prs = [
        int(match)
        for match in re.findall(r"^\| PR(\d+) \|", document, flags=re.MULTILINE)
    ]

    assert table_prs == list(range(142, 193))
    assert "bedienbarer 100-Perioden-Lauf mit Ergebnis und Export | PR151 | 10" in document
    assert "vier Modellsegmente und konsolidierte Versichererbilanz (API) | PR170 | 33" in document
    assert "Vier-Sparten-Bilanz im Browser | PR170a | 34" in document
    assert "erklaerbare Solvency-II-Kapitalansicht | PR178 | 42" in document
    assert "durchgaengige DORA-Wirkungskette | PR186 | 50" in document
    assert "kontrollierte Managementseminar-Reife | PR190 | 54" in document
    assert "PR170a Vier-Sparten-Gesamtbilanz im Browser umgesetzt, PR171 Solvency-II-Geltungsvertrag naechster Schritt" in document
    for label in ("PR169a", "PR169b", "PR169c", "PR169d", "PR170a"):
        assert f"| {label} |" in document
    assert "PR143 hat die kanonische Fuenf-Perioden-Kette gebaut" in document
    assert "PR145 hat kontrollierten Serverstart" in document
    assert "PR146 hat den Pfad in der Workbench bedienbar gemacht" in document
    assert "PR147 hat fuer 10, 25, 50 und 100 Perioden" in document
    assert "technischer 100-Perioden-Lauf | PR149 | 8 | 0" in document
    assert "bedienbarer 100-Perioden-Lauf mit Ergebnis und Export | PR151 | 10 | 0" in document
    assert "bedienbare Kranken-Simulation bis 100 Perioden | PR169d | 32 | 0" in document
    assert "kontrollierte Managementseminar-Reife | PR190 | 54 | 20" in document
    assert "Windows Ready-to-run ohne Zielrechner-Python | PR192 | 56 | 22" in document
    assert "Diese optionale Distributionsspur beginnt **erst nach PR190**" in document


def test_roadmap_defines_scope_estimate_and_validation_gates() -> None:
    document = ROADMAP.read_text(encoding="utf-8")

    assert "18.700-35.000 LoC" in document
    assert "Unsicherheit von etwa acht zusaetzlichen PRs" in document
    for gate in (
        "deterministische Wiederholung",
        "stabile Prefixe",
        "Bilanz-, Bestands-, Mengen- und Aggregatinvarianten",
        "Browserabnahme auf breitem und schmalem Viewport",
        "CSV-, JSON- und XLSX-Exporte",
    ):
        assert gate in document


def test_later_windows_ready_to_run_plan_keeps_pr171_next() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    plan = WINDOWS_PLAN.read_text(encoding="utf-8")

    assert "PR171 Solvency-II-Geltungsvertrag naechster Schritt" in roadmap
    assert "PR171 bleibt der" in plan
    for phrase in (
        "PR191", "PR192", "IMS-Workbench.exe", "One-folder",
        "ohne Zielrechner-Python", "127.0.0.1", "%LOCALAPPDATA%",
        "SmartScreen", "Linux oder iOS/Juno", "incomming/",
    ):
        assert phrase in plan
    assert "Dieser Plan baut noch kein Paket" in plan


def test_life_expansion_is_scheduled_before_health_and_four_sector_total() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    plan = LIFE_PLAN.read_text(encoding="utf-8")

    for phrase in (
        "Tod", "Neugeschaeft", "Kapitalbewegungen", "Policenwerte",
        "Ablaufleistung", "Mortalitaet", "Anlage", "PR165", "PR166",
        "PR167", "Baseline/Variante", "Rueckkauf/Bonus",
    ):
        assert phrase in plan
    assert roadmap.index("| PR160 | Lebensfluss-") < roadmap.index("| PR168 | Zustands-")
    assert roadmap.index("| PR167 | Gefuehrte Lebens-Workbench") < roadmap.index("| PR170 | Spartenuebergreifende Konsolidierung")
    assert "ims_2x_life_workshop_expansion_plan.md" in roadmap


def test_management_guide_is_nontechnical_honest_and_visual() -> None:
    document = GUIDE.read_text(encoding="utf-8")
    normalized = " ".join(document.split())

    assert "Handbuchschnitt: HB3h" in document
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
