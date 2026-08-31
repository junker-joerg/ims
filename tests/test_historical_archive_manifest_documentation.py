import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCUMENT = REPO_ROOT / "docs" / "migration" / "historical_archive_manifest.md"


def test_archive_manifest_document_fixes_observed_archive_inventory() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")

    assert "Vertrag: `pr88-v1`" in document
    assert "165 Dateieintraege" in document
    assert "64 Archiveintraege" in document
    assert "drei von sieben" not in document
    assert "drei vollstaendige" not in document
    assert "WVEMOD1.ZIP" in document
    assert "WVEMOD2.ZIP" in document
    assert "WVEMOD3.ZIP" in document
    assert "1.506.069" in document
    assert "IMSREPOR.DAT" in document


def test_archive_manifest_document_records_all_archive_hashes_and_core_rows() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")

    for archive_hash in (
        "ade1f91a4b6cf7b26df38ce82f45c07b3fad1d64738f20ec7ab09bc64a28ddb0",
        "61fe4268ceebb6f3af1288b51aac360744bc121fa48335f0f79ee6b09239f5b8",
        "5839ddea724949e9e1065a4d9f1ac3f27e97c2ed444d819f466f3cd4ee97f190",
        "a5caa7ca12fdece28991e7cf32b5768cdaed3a0cbf31a759506b05ab0fc05634",
        "444c0bddf7a0dcee21e963167c36da56ed9b0a33172487914adf51e2a91206d9",
        "d17f399139ced0c85db424aac46b585ee40f2d98eb84da43b3d5790d445c3eae",
        "86a07aace01c47751a3320de580bbb66714ae6d28a74bafce876e14b6470f47b",
    ):
        assert archive_hash in document

    core_rows = [
        line
        for line in document.splitlines()
        if line.startswith("| `") and "IMSV" in line and "IMSREPOR" not in line
    ]
    assert len(core_rows) == 64
    assert all(re.search(r"`[0-9a-f]{64}`", row) for row in core_rows)
    assert all("| yes |" not in row for row in core_rows)


def test_archive_manifest_document_keeps_provenance_claims_blocked() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")

    assert "extrahiert keine Datei" in document
    assert "bleiben unversioniert" in document
    assert "keine Archive demselben" in document
    assert "weder historische Vollgleichheit noch eine" in document
    assert "PR 89" in document
    assert "VUSK1L1-5" in document
    assert "desselben `SK1/all`-Aggregats auf Stufe IV" in document
