from pathlib import Path

import pytest

from ims.model.legacy_export_identity import (
    build_legacy_export_identity,
    canonicalize_legacy_export_selector,
)


MIGRATION_DOC = Path("docs/migration/level_iv_selector_canonicalization.md")


@pytest.mark.parametrize("selector_value", ["all", "SK1"])
def test_level_iv_all_selector_uses_historical_sk1_identity(selector_value: str) -> None:
    assert canonicalize_legacy_export_selector("IV", "all", selector_value) == "SK1"
    assert build_legacy_export_identity(
        "imsvusk1.dat",
        "insurer",
        "IV",
        "all",
        selector_value,
    ) == ("imsvusk1.dat", "insurer", "IV", "all", "SK1")


@pytest.mark.parametrize(
    ("level", "selector_kind", "selector_value"),
    [
        ("III", "all", "all"),
        ("IV", "rule", "all"),
        ("IV", "all", "ALL"),
        ("IV", "all", "sk1"),
        ("IV", "all", 1),
        ("iv", "all", "all"),
    ],
)
def test_level_iv_selector_canonicalization_keeps_other_identities_strict(
    level: str,
    selector_kind: str,
    selector_value: int | str,
) -> None:
    assert canonicalize_legacy_export_selector(level, selector_kind, selector_value) == selector_value


def test_level_iv_selector_documentation_keeps_scope_conservative() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "Technische Level-IV-Selektorkanonisierung" in doc
    assert "nur fuer die Exportidentitaet" in doc
    assert "kanonisiert ausschliesslich diese beiden Werte" in doc
    assert "rohe Laufzeittabelle behaelt `selector_value = \"all\"`" in doc
    assert "Andere Stufen, Selektorarten, Werte und Schreibweisen bleiben verschieden" in doc
    assert "VUSK1L1.DAT` bis `VUSK1L5.DAT" in doc
    assert "Zeitfenster desselben `SK1`-/`all`-Aggregats" in doc
    assert "keine historische Vollgleichheit" in doc
    assert "keine Vollsimulation gestartet" in doc
    assert "PR 62" in doc and "Run-Control-Freigabecheck" in doc
    assert "PR 63" in doc and "Backend-Start-/Status" in doc
