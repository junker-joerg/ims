from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCUMENT = REPO_ROOT / "docs" / "migration" / "historical_archive_run_metadata.md"


def test_run_metadata_document_fixes_pr90_archive_result() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "Vertrag: `pr90-v1`" in document
    assert "165 Eintraege" in document
    assert "164 `IMSV*.DAT`-Ausgaben" in document
    assert "Genau ein weiterer Eintrag" in normalized
    assert "Separate Modell-, Definitions- oder Parameterdateien" in normalized
    assert document.count("`metadata_absent`") == 6


def test_run_metadata_document_records_direct_report_facts() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "`03c3ce742cfea6c5eef27f1434924b5969093a83e2401166ed5ffce181d2e133`" in document
    assert "`5616`" in document
    assert "25 VU, 199.200 Bytes" in document
    assert "200 VN, 1.923.200 Bytes" in document
    assert "dreimal zusammenhaengend `1-100`" in document
    assert "nicht als ein fortlaufender 300-Perioden-Horizont" in normalized
    assert "neutral als drei beobachtete Sequenzen" in normalized


def test_run_metadata_document_keeps_archive_and_claim_boundaries() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    normalized = document.replace("\n", " ")

    assert "gehoert ausschliesslich zu `VDEFMD5A.ZIP`" in normalized
    assert "duerfen daher nicht als Laufmetadaten dieser Referenzen" in normalized
    assert "belegt weder einen gemeinsamen historischen Lauf" in normalized
    assert "keine Klasse `same_run_proven`" in normalized
    assert "Das Legacy-Bundle wird erst nach einem getrennten" in normalized
    assert "keine Simulation gestartet" in document
