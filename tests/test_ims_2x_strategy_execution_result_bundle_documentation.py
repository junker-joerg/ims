from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs/plans/ims_2x_pr150_result_bundle_plan.md"
MAPPING = ROOT / "docs/migration/ims_2x_strategy_execution_result_bundle.md"


def test_pr150_names_historical_boundary_formats_and_persistence_gap():
    content = " ".join((PLAN.read_text(encoding="utf-8") + " " +
                        MAPPING.read_text(encoding="utf-8")).split())
    for phrase in (
        "ESS.C:71-75", "IMSDATA.C:14", "100 Perioden", "kennzahlen.csv",
        "kennzahlen.xlsx", "ergebnis.json", "Prefix", "fluechtig",
        "keine neue", "historische", "PR151", "incomming/",
    ):
        assert phrase in content
    for index, name in (("docs/plans/README.md", PLAN.name),
                        ("docs/migration/README.md", MAPPING.name)):
        assert name in (ROOT / index).read_text(encoding="utf-8")
