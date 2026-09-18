from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_pr171_documents_model_limit_sources_and_next_step() -> None:
    plan = (ROOT / "docs/plans/ims_2x_pr171_solvency_scope_contract.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "ims.four-sector-balance-result.v1", "Modell-Eigenkapital",
        "Best Estimate", "Risikomarge", "SCR", "MCR", "2027",
        "PR172", "keine historische", "GET /api/model/solvency-scope-contract",
    ):
        assert phrase in plan
    assert "PR171 | Scope-" in roadmap
    assert "PR172 ist der naechste Schritt" in roadmap
