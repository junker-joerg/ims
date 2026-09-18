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
    assert "PR173 ist der naechste Schritt" in roadmap
