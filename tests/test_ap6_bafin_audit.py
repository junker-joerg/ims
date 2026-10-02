"""Independent arithmetic and failure cases for the AP6 research audit."""
from __future__ import annotations

from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ap6_audit", ROOT / "scripts/planning/audit_ap6_bafin_workbook.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def row(group: str, value: object, number: int, sector: str = "Leben") -> dict:
    amount, lower, upper, status = audit.premium(value, Decimal(1))
    return {"group_assertion": group, "workbook_row": number, "source_sector": sector,
            "premium_million_eur": amount, "lower_million_eur": lower, "upper_million_eur": upper}


class BafinAuditTests(unittest.TestCase):
    def test_source_dash_zero_and_unknown_are_distinct(self):
        self.assertEqual(audit.premium("-", Decimal(1)), (Decimal(0), Decimal(0), Decimal(0), "source_exact_zero"))
        self.assertEqual(audit.premium(0, Decimal(1)), (Decimal(0), Decimal(0), Decimal(1), "source_below_unit"))
        for value in (None, "", "***", "0", "–", True, float("nan"), float("inf"), -1):
            self.assertEqual(audit.premium(value, Decimal(1)), (None, None, None, "unknown"))

    def test_thousand_to_million_conversion_retains_precision(self):
        self.assertEqual(audit.premium(660204, Decimal("0.001")),
                         (Decimal("660.204"), Decimal("660.203"), Decimal("660.205"), "source_rounded"))

    def test_hand_case_group_addition_keeps_unknown_and_empty_sector(self):
        group = audit.aggregate([row("A", 70, 1), row("A", 30, 2), row("A", "***", 3)])[0]
        self.assertEqual(group["total"], Decimal(100))
        self.assertEqual(group["unknown_count"], 1)
        self.assertIsNone(group["upper"])
        self.assertEqual(group["sector_entity_count"]["Kranken"], 0)
        self.assertFalse(group["group_membership_verified"])

    def test_boundary_checks_all_candidates_not_only_rank_41(self):
        ranking = audit.aggregate([row("A", 100, 1), row("B", 99, 2), row("C", "***", 3)])
        result = audit.boundary(ranking, count=1)
        self.assertFalse(result["separated_within_workbook_assignments_and_source_units"])
        self.assertIsNone(result["maximum_other_upper_million_eur"])

    def test_source_rounding_can_prevent_an_apparent_boundary(self):
        result = audit.boundary(audit.aggregate([row("A", 100, 1), row("B", 99, 2)]), count=1)
        self.assertEqual(result["gap_million_eur"], Decimal(1))
        self.assertFalse(result["separated_within_workbook_assignments_and_source_units"])

    def test_separated_source_boundary_is_not_german_selection(self):
        result = audit.boundary(audit.aggregate([row("A", 100, 1), row("B", 90, 2)]), count=1)
        self.assertTrue(result["separated_within_workbook_assignments_and_source_units"])
        self.assertFalse(result["german_market_boundary_verified"])

    def test_equal_displayed_values_have_reproducible_order_but_no_verified_boundary(self):
        rows = [row("B", 100, 1), row("A", 100, 2)]
        self.assertEqual(audit.aggregate(rows), audit.aggregate(list(reversed(rows))))
        self.assertEqual(audit.aggregate(rows)[0]["group_assertion"], "A")
        self.assertFalse(audit.boundary(audit.aggregate(rows), count=1)["separated_within_workbook_assignments_and_source_units"])

    def test_top40_only_is_not_a_complete_ranking(self):
        with self.assertRaises(ValueError):
            audit.boundary(audit.aggregate([row("A", 100, 1)]), count=1)

    def test_modified_primary_file_is_rejected_before_parsing(self):
        register = json.loads(audit.SOURCE_REGISTER.read_text(encoding="utf-8"))
        source = next(s for s in register["sources"] if s["id"] == "AP6-S02")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbook = root / "input.xlsx"
            workbook.write_bytes(b"not loaded")
            primary = root / Path(source["local_download"]).name
            primary.write_bytes(b"modified source")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                audit.audit(workbook, root)

    def test_committed_reference_is_consistent_without_claiming_acceptance(self):
        result = json.loads((ROOT / "docs/research/ims_ap6_top40_2024_audit.json").read_text(encoding="utf-8"))
        rows = result["entities"]
        self.assertEqual(len(rows), 326)
        self.assertEqual(len({(r["source_sheet"], r["source_cell"]) for r in rows}), 326)
        self.assertEqual(len(result["groups_by_available_earned_amount"]), 145)
        self.assertEqual(result["audit"]["formulas_checked"], 663)
        self.assertEqual(result["audit"]["errors"], [])
        group_rows = {r["workbook_row"]: r for r in rows}
        groups = result["groups_by_available_earned_amount"]
        for group in groups:
            expected = sum((Decimal(group_rows[i]["premium_million_eur"]) for i in group["entity_rows"]
                            if group_rows[i]["premium_million_eur"] is not None), Decimal(0))
            self.assertEqual(Decimal(group["total"]), expected)
        selected = {i for group in groups[:40] for i in group["entity_rows"]}
        self.assertEqual(len(selected), 206)
        total = sum((Decimal(r["premium_million_eur"]) for r in rows if r["workbook_row"] in selected), Decimal(0))
        self.assertEqual(total, Decimal("254270.039"))
        self.assertEqual(Decimal(result["displayed_top40_totals"]["C"]), total)
        self.assertEqual((groups[39]["group_assertion"], groups[40]["group_assertion"]), ("Münchener Verein", "Itzehoer"))
        zeros = [r for r in rows if r["value_status"] == "source_exact_zero"]
        self.assertEqual([r["workbook_row"] for r in zeros], [84, 329, 330])
        self.assertTrue(result["boundary"]["separated_within_workbook_assignments_and_source_units"])
        self.assertFalse(result["boundary"]["german_market_boundary_verified"])
        self.assertFalse(result["ap6_gate"]["selection_verified"])
        self.assertFalse(result["ap6_gate"]["demo_activation_allowed"])


if __name__ == "__main__":
    unittest.main()
