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
    assert "PR178a ist" in roadmap


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
    assert "PR178a ist" in roadmap


def test_pr174_documents_explicit_model_stress_without_scr_claim() -> None:
    plan = (ROOT / "docs/plans/ims_2x_pr174_model_risk_modules.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "ims.accounting.solvency_scenario_shocks",
        "scenario_declared_not_regulatory", "ROUND_HALF_UP", "PR175",
        "keine historische Vollgleichheit", "solvency-risk-modules",
    ):
        assert phrase in plan
    assert "PR174 | Ausgewaehlte Markt-" in roadmap
    assert "PR178a ist" in roadmap


def test_pr175_documents_model_aggregation_without_capital_claim() -> None:
    plan = (ROOT / "docs/plans/ims_2x_pr175_model_risk_aggregation.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "ims.accounting.solvency_risk_modules",
        "counterparty_model_loss", "operational_model_loss", "positiv semidefinit",
        "ROUND_HALF_UP", "keine Solvency-II-Kapitalanforderung",
        "PR176", "Keine historische Vollgleichheit", "solvency-risk-aggregation",
    ):
        assert phrase in plan
    assert "PR175 | Gegenpartei-, operationelles Risiko" in roadmap
    assert "PR178a ist" in roadmap


def test_pr176_documents_model_limits_and_blocked_regulatory_values() -> None:
    plan = (ROOT / "docs/plans/ims_2x_pr176_capital_readiness_and_management_limits.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "ims.accounting.solvency_model_balance",
        "ims.accounting.solvency_risk_aggregation", "Art. 101", "Art. 103",
        "Art. 129", "30.01.2027", "blocked_missing_regulatory_basis",
        "keine aufsichtsrechtliche", "Keine historische Vollgleichheit",
        "solvency-capital-readiness", "PR177",
    ):
        assert phrase in plan
    assert "PR176 | SCR, MCR, Bedeckungsquote" in roadmap
    assert "PR178a ist" in roadmap


def test_pr177_documents_fixed_model_cases_without_regulatory_release() -> None:
    plan = (ROOT / "docs/plans/ims_2x_pr177_capital_validation_cases.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "319.0000", "401.5750", "-82.4000",
        "Quellen-Digests", "Solvency-II", "null", "Keine Simulation",
        "keine historische", "PR178 Kapitalansicht und Export folgt",
    ):
        assert phrase in plan
    assert "PR177 | Feste Faelle, Sensitivitaeten und Invarianten | umgesetzt" in roadmap
    assert "PR178a ist" in roadmap


def test_pr178_documents_browser_export_and_capital_gate() -> None:
    plan = (ROOT / "docs/plans/ims_2x_pr178_capital_workbench_and_export.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "Vier-Sparten-Gesamtbilanz", "Quellen-Digests", "XLSX",
        "JSON", "SCR", "MCR", "keine historische", "PR178a",
    ):
        assert phrase in plan
    assert "PR178 | Kapitalansicht und Export | umgesetzt" in roadmap
    for width in ("wide", "narrow"):
        screenshot = ROOT / f"docs/handbook/images/windows_capital_pr178_{width}_2026-09-18.png"
        assert screenshot.is_file() and screenshot.stat().st_size > 10_000
