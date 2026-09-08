from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "plans" / "ims_2x_strategy_execution_connection_plan.md"


def test_pr123_plan_names_existing_anchors_and_missing_execution_state() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR123" in text
    assert "`VNInsuranceRuleSnapshot`" in text
    assert "acht vorhandenen VU-Snapshot-Sammlungen" in text
    assert "`run_loaded_explicit_period`" in text
    assert "`LoadedScenario`" in text
    assert "`SimulationContext`" in text
    assert "BAV-Zustand" in text
    assert "`vn_damage_settlement_snapshots`" in text
    assert "`vn_settlement_snapshots`" in text


def test_pr123_plan_keeps_browser_reports_out_of_runner_authority() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "unveraenderlichen\nEinperioden-Ausfuehrungskandidaten" in text
    assert "Browser-zu-Runner-Pfad" in text
    assert "nicht als\nautoritative Ausfuehrungsquelle akzeptiert" in text
    assert "bekanntes lokales Szenarioprofil" in text
    assert "Inhaltsdigest" in text
    assert "tiefen Kopie des Kandidaten" in text


def test_pr123_plan_preserves_atomicity_and_explicit_draw_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    for collection in (
        "vu_foreign_info_rule_snapshots",
        "vu_random_uniform_rule_snapshots",
        "vu_random_normal_rule_snapshots",
        "vu_reserve_markup_rule_snapshots",
        "vu_net_switcher_markup_rule_snapshots",
        "vu_expected_claim_rule_snapshots",
        "vu_market_share_markup_rule_snapshots",
        "vu_free_linear_rule_snapshots",
        "vn_insurance_rule_snapshots",
    ):
        assert f"`{collection}`" in text

    assert "vollstaendige explizite Draws ohne RNG- oder Loader-Fallback" in normalized
    assert "keine Teilkandidaten" in normalized
    assert "kein Carryover" in text
    assert "kein `output_dir`" in text
    assert "kein automatischer Legacy-Vergleich" in text


def test_pr123_plan_defers_execution_and_lists_follow_up_sequence() -> None:
    text = PLAN.read_text(encoding="utf-8")

    for pr_number in range(124, 133):
        assert f"PR{pr_number}" in text

    assert "vier kleine PRs" in text
    assert "keine Codeaenderung am Simulations- oder Regelkern" in text
    assert "keine Snapshot-, Szenario- oder Kandidatenpersistenz" in text
    assert "kein neuer API- oder UI-Startpfad" in text
    assert "keine Simulation und kein Schedulerstart" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text


def test_pr123_plan_is_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "ims_2x_strategy_execution_connection_plan.md" in plans_index
    assert "PR123 gemeinsamer Ausfuehrungsanschluss" in strategy_index
