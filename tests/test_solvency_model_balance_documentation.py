from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_pr172_documents_explicit_bridge_and_no_regulatory_claim() -> None:
    plan = (ROOT / "docs/plans/ims_2x_pr172_solvency_model_balance.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "ims.four-sector-balance-result.v1", "model_own_funds_proxy",
        "Art. 75", "Art. 77", "Art. 88", "keine historische",
        "PR173", "scenario_declared", "solvency-model-balance",
    ):
        assert phrase in plan
    assert "PR172 | Solvenzmodellbilanz" in roadmap
    assert "PR174 ist der naechste Schritt" in roadmap


def test_pr173_documents_explicit_exposures_without_capital_claim() -> None:
    plan = (ROOT / "docs/plans/ims_2x_pr173_risk_drivers_and_shocks.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "ims.accounting.solvency_model_balance", "source_kind",
        "scenario_declared_non_overlapping_subposition", "amount_delta", "PR174",
        "kein SCR", "historische Vollgleichheit", "solvency-scenario-shocks",
    ):
        assert phrase in plan
    assert "PR173 | Risikotreiber" in roadmap
    assert "PR174 ist der naechste Schritt" in roadmap
