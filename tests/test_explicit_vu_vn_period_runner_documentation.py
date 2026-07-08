from pathlib import Path


DOC = Path("docs/migration/explicit_vu_vn_period_runner.md")
README = Path("docs/migration/README.md")


def test_explicit_vu_vn_period_runner_execution_summary_is_documented() -> None:
    doc = DOC.read_text(encoding="utf-8")

    assert "build_explicit_multi_period_execution_summary" in doc
    assert "lokale und globale Periodenachsen" in doc
    assert "VU-/VN-Anwendungszaehlungen" in doc
    assert "Carryover-Zaehler" in doc
    assert "Legacy-Vergleichsstatus" in doc
    assert "keine fachliche Nachberechnung" in doc
    assert "keine automatische" in doc
    assert "keine Vollsimulation" in doc


def test_explicit_vu_vn_period_runner_document_is_listed() -> None:
    readme = README.read_text(encoding="utf-8")

    assert "explicit_vu_vn_period_runner.md" in readme
    assert "gemeinsame explizite Periodenstrecke" in readme
