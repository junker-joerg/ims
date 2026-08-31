import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCUMENT = REPO_ROOT / "docs" / "migration" / "historical_reference_layer_contract.md"


def test_layer_contract_document_fixes_pr91_decision() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "Vertrag: `pr91-v1`" in document
    assert "19 von 19 Zielen und vier getrennte Referenzschichten" in normalized
    assert "18 Ziele sind `archive_family_only`" in document
    assert "kein Ziel ist `same_run_proven`" in document
    assert "der Gesamtkorpus ist `mixed_reference_layers`" in document
    assert "`go_separate_reference_tests`" in document
    assert "`full_window_phase_allowed = true`" in document
    assert "LF- und" in document and "CRLF-Checkout-Varianten" in document
    assert "Windows- und LF-Checkouts identisch" in normalized


def test_layer_contract_document_records_all_target_hashes() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    target_rows = [
        line
        for line in document.splitlines()
        if line.startswith("| `")
        and re.match(r"\| `(VU|IMSV)", line)
        and re.search(r"`[0-9a-f]{64}`", line)
    ]

    assert len(target_rows) == 19
    assert all(re.search(r"`[0-9a-f]{64}`", row) for row in target_rows)
    assert "`zins000_archive`" in document
    assert "`wvemod1_archive`" in document
    assert "`wvemod2_archive`" in document
    assert "`vusk1l4_direct_04410ef`" in document


def test_layer_contract_document_keeps_vusk1_and_claim_boundaries() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "Zeitfenster derselben Exportidentitaet" in normalized
    assert "desselben `SK1/all`-Aggregats" in document
    assert "derselben Aggregatstufe IV" in normalized
    assert "`4ec1473063895eb5bad6e4bf5d9cc5f1856f94166070a8d28ad07356815357b7`" in document
    assert "stabile versionierte Fixture-Regression" in normalized
    assert "keine koharente historische 500-Perioden-Reihe" in normalized
    assert "keine gemeinsame historische Archivquelle" in normalized
    assert "Noch wird kein 300-/500-Vollvergleich ausgefuehrt" in normalized
