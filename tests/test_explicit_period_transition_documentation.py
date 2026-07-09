from pathlib import Path


DOC = Path("docs/migration/explicit_period_transition_diagnostics.md")
README = Path("docs/migration/README.md")


def test_explicit_period_transition_diagnostics_is_documented() -> None:
    doc = DOC.read_text(encoding="utf-8")

    assert "Explizite Periodenuebergangsdiagnose" in doc
    assert "python -m ims.engine.explicit_period_transition_diagnostics" in doc
    assert 'mode = "explicit_period_transition_diagnostics"' in doc
    assert "transition_count" in doc
    assert "from_global_period" in doc
    assert "to_global_period" in doc
    assert "writes_performed = false" in doc
    assert "execution_performed = false" in doc
    assert "simulation_performed = false" in doc
    assert "automatic_historical_rule_selection_performed = false" in doc
    assert "VU14L1.DAT" in doc
    assert "VUSK1L4.DAT" in doc
    assert "replay_vn_policyholder_transition_plan.json" in doc
    assert "VN-Policyholder `21`" in doc
    assert "vn_carryover_planned = true" in doc
    assert "explicit_period_transition_no_policyholders" in doc
    assert "gezielt fuer eine minimale VN-Subjektmenge auf" in doc
    assert "kein Runner-Start" in doc
    assert "keine Simulation" in doc
    assert "keine neue Fachlogik" in doc
    assert "keine historische Vollgleichheitsbehauptung" in doc


def test_explicit_period_transition_diagnostics_document_is_listed() -> None:
    readme = README.read_text(encoding="utf-8")

    assert "explicit_period_transition_diagnostics.md" in readme
    assert "rein lesende Uebergangsdiagnose" in readme
