import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCUMENT = REPO_ROOT / "docs" / "migration" / "historical_reference_archive_coherence.md"


def test_coherence_document_fixes_pr89_result() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")

    assert "Vertrag: `pr89-v1`" in document
    assert "19 Referenzziele und 92" in document
    assert "13 Ziele sind `exact_archive_member`" in document
    assert "5 Ziele sind `exact_window_slice`" in document
    assert "`VUSK1L4.DAT` ist als einziges Ziel `same_name_divergent`" in document
    assert "Kein Ziel ist `unresolved`" in document


def test_coherence_document_records_all_reference_hashes() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    target_rows = [
        line
        for line in document.splitlines()
        if line.startswith("| `") and re.search(r"`[0-9a-f]{64}`", line)
    ]

    assert len(target_rows) == 19
    assert all(re.search(r"`[0-9a-f]{64}`", row) for row in target_rows)
    assert "`37189ca9058a0817f4623767a5758ccd2d870d1518f2f443a941d33c91929c88`" in document
    assert "`79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9`" in document


def test_coherence_document_keeps_sk1_and_run_boundaries_conservative() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "Zeitfenster derselben Exportidentitaet `IMSVUSK1.DAT`" in normalized
    assert "`SK1/all`-Aggregats" in document
    assert "Aggregatstufe IV" in document
    assert "keinem der sieben bekannten" in normalized
    assert "nicht als neue Aggregatebene" in normalized
    assert "kein Nachweis eines gemeinsamen historischen" in normalized
    assert "startet keine Ausfuehrung oder" in normalized
    assert "PR 90" in document
