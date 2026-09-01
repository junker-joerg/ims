import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
HANDBOOK_ROOT = REPO_ROOT / "docs" / "handbook"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _pdf_page_count(path: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page(?!s)\b", path.read_bytes()))


def test_portable_installation_is_two_pages_and_user_facing() -> None:
    installation = _read(HANDBOOK_ROOT / "installation_test_package_windows.md")

    assert installation.count("## Seite ") == 2
    assert "install-workbench.cmd" in installation
    assert "start-workbench.cmd" in installation
    assert "Node.js, npm, Git und Administratorrechte" in installation
    assert "keine fachliche Produktionsfreigabe" in installation


def test_portable_user_guide_is_at_most_ten_pages_and_honest_about_scope() -> None:
    guide = _read(HANDBOOK_ROOT / "user_guide_test_package.md")

    assert guide.count("## Seite ") == 10
    assert "Die urspruengliche Idee" in guide
    assert "Was kann das Modell?" in guide
    assert "Was ist ein Schock?" in guide
    assert "Wo ist der Output?" in guide
    assert "keinen fachlichen Modelloutput" in guide
    assert "Aktivierungsschock" in guide
    assert "Aenderungsschock" in guide
    assert "Indirekter Schock" in guide
    assert "Prozessrealitaet" in guide
    assert "Kein Ergebnis der modernisierten Workbench" in guide
    assert guide.count("![") == 8
    for image_name in (
        "ims_market_cycle_diss_2026-09-01.png",
        "ims_shock_types_diss_2026-09-01.png",
        "diss_figure_5_8_market_share.png",
        "diss_figure_5_9_before_after.png",
        "diss_figure_5_10_aggregation.png",
        "windows_workbench_dashboard_hb3a_2026-09-01.png",
        "windows_workbench_scenarios_hb3a_2026-09-01.png",
        "windows_workbench_runs_hb3a_2026-09-01.png",
    ):
        assert image_name in guide
        assert (HANDBOOK_ROOT / "images" / image_name).is_file()


def test_portable_handbook_pdfs_have_the_documented_page_limits() -> None:
    installation_pdf = REPO_ROOT / "output" / "pdf" / "IMS-Installation-Windows.pdf"
    guide_pdf = REPO_ROOT / "output" / "pdf" / "IMS-Bedienungsanleitung.pdf"

    assert installation_pdf.read_bytes().startswith(b"%PDF")
    assert guide_pdf.read_bytes().startswith(b"%PDF")
    assert _pdf_page_count(installation_pdf) == 2
    assert _pdf_page_count(guide_pdf) == 10
    assert guide_pdf.read_bytes().count(b"/Subtype /Image") >= 8


def test_user_test_package_build_is_separate_from_simulation_and_pr102() -> None:
    build_script = _read(REPO_ROOT / "scripts" / "workbench" / "build-user-test-package.ps1")
    plan = _read(REPO_ROOT / "docs" / "plans" / "portable_user_test_package_plan.md")

    assert "workbench_bundle_build" in build_script
    assert "workbench_portable_staging" in build_script
    assert "IMS-Workbench-2026-Windows-Test.zip" in build_script
    assert "target_requires_node = $false" in build_script
    assert "simulation_performed = $false" in build_script
    assert "PR102 schliesst weiterhin den 6.300-Zeilen-Korpus" in plan
    assert "Keine Simulation, keine neue Fachlogik" in plan


def test_portable_web_requirements_match_the_package_contract() -> None:
    requirements = _read(REPO_ROOT / "python_port" / "requirements-web.txt").splitlines()
    project = _read(REPO_ROOT / "python_port" / "pyproject.toml")

    assert requirements == ["fastapi>=0.115", "uvicorn>=0.30"]
    assert 'web = [' in project
    for requirement in requirements:
        assert f'"{requirement}"' in project
