"""Accepted AP5 hand cases and meaningful conservation/replay/contract regressions."""
from copy import deepcopy
from decimal import Decimal
from io import BytesIO
import json
import unittest

from openpyxl import load_workbook
from starlette.testclient import TestClient

from ims.api.market import create_market_app
from ims.market.presets import workshop_case
from ims.market.runner import FINANCIAL_FIELDS, actor_draws, calculate
from ims.market.transport import unpack_rows, wire_payload
from ims.strategies.modern_bridge import calculate as ap3_calculate
from ims.strategies.modern_presets import workshop_case as ap3_case


def row(result, side="baseline", p=6, sector="total"):
    return next(r for r in result["sides"][side]["market_rows"] if r["period"] == p and r["sector_id"] == sector)


class MarketTests(unittest.TestCase):
    def checked(self, source):
        result = calculate(source)
        self.assertTrue(result["valid"], result["issues"])
        return result

    def test_accepted_switch_hand_case_and_old_reserve_owner(self):
        result = self.checked(workshop_case("switch", 10))
        market = row(result)
        self.assertEqual([market[k] for k in ("closing_assets", "closing_liabilities", "closing_equity", "period_profit")], ["172.0000", "15.0000", "157.0000", "-23.0000"])
        actors = [r for r in result["sides"]["baseline"]["vu_rows"] if r["period"] == 6]
        self.assertEqual([(r["insurer_id"], r["insurance_expense"], r["old_claims_paid"], r["closing_liabilities"]) for r in actors], [(1, "0.0000", "5.0000", "15.0000"), (2, "40.0000", "0.0000", "0.0000")])
        decision = next(r for r in result["sides"]["baseline"]["customer_decisions"] if r["period"] == 6)
        self.assertEqual((decision["previous_insurer_id"], decision["insurer_id"], decision["premium_income"]), (1, 2, "20.0000"))

    def test_capacity_tie_break_risk_conservation_and_uninsured(self):
        source = workshop_case("capacity", 10)
        source["insurers"].reverse(); source["customer_groups"].reverse()
        result = self.checked(source)
        self.assertEqual(row(result)["closing_assets"], "315.0000")
        choices = [r for r in result["sides"]["baseline"]["customer_decisions"] if r["period"] == 6]
        self.assertEqual([r["insurer_id"] for r in choices], [1, 2, None])
        self.assertEqual(sum(Decimal(r["risk_loss"]) for r in choices), Decimal(20))
        self.assertEqual(sum(Decimal(r["uninsured_loss"]) for r in choices), Decimal(7))
        self.assertEqual(row(result, sector="motor")["weighted_price"], "2.0000")
        self.assertIsNone(row(result)["weighted_price"])

    def test_family_partition_peers_are_not_partition_and_carryover(self):
        result = self.checked(workshop_case("capacity", 10))
        side = result["sides"]["baseline"]
        for p in range(1, 11):
            total = row(result, p=p)
            for field in FINANCIAL_FIELDS:
                self.assertEqual(sum(Decimal(r[field]) for r in side["family_rows"] if r["period"] == p and r["sector_id"] == "total"), Decimal(total[field]))
            for aid in (1, 2, 3):
                r = next(r for r in side["vu_rows"] if r["period"] == p and r["insurer_id"] == aid)
                self.assertEqual(Decimal(r["closing_assets"]), Decimal(r["closing_liabilities"]) + Decimal(r["closing_equity"]))
                if p > 1:
                    previous = next(x for x in side["vu_rows"] if x["period"] == p - 1 and x["insurer_id"] == aid)
                    self.assertEqual(r["opening_assets"], previous["closing_assets"])
        peers = [r["closing_assets"] for r in side["peer_rows"] if r["period"] == 6 and r["sector_id"] == "total"]
        self.assertEqual(peers, ["215.0000", "212.0000"])

    def test_replay_and_financial_prefixes_all_four_sectors(self):
        long = self.checked(workshop_case("market", 10, 3))
        replay = self.checked(workshop_case("market", 10, 3))
        self.assertEqual(long["content_digest"], replay["content_digest"])
        short = self.checked(workshop_case("market", 5, 3))
        for side in ("baseline", "variant"):
            self.assertEqual(short["sides"][side]["market_rows"], [r for r in long["sides"][side]["market_rows"] if r["period"] <= 5])
            self.assertEqual(short["sides"][side]["customer_decisions"], [r for r in long["sides"][side]["customer_decisions"] if r["period"] <= 5])

    def test_measure_cost_lead_duration_and_no_future_information(self):
        result = self.checked(workshop_case("market", 25, 3))
        rows = [r for r in result["sides"]["variant"]["vu_rows"] if r["insurer_id"] == 1 and r["sector_id"] == "motor"]
        self.assertEqual(sum(Decimal(r["measure_cost"]) for r in rows), Decimal(3))
        self.assertEqual(rows[5]["measure_cost"], "3.0000")
        self.assertEqual([r["period"] for r in rows if r["active_measures"]], [8, 9, 10])
        self.assertEqual(rows[19]["family_id"], "motor_Preisantwort")
        self.assertEqual(rows[20]["family_id"], "motor_Zufall_I")
        self.assertTrue(all(r["information_period"] == r["period"] - 1 for r in rows))
        future = workshop_case("market", 25, 3)
        for c in future["customer_groups"]: c["risk_periods"][9]["loss"] = "500"
        changed = self.checked(future)
        before = [r for r in result["sides"]["variant"]["vu_rows"] if r["period"] < 10]
        after = [r for r in changed["sides"]["variant"]["vu_rows"] if r["period"] < 10]
        self.assertEqual(before, after)

    def test_actor_bound_draws_modern_id_41_and_optional_sectors(self):
        a = workshop_case("market", 10, 3)
        for actor in a["insurers"]:
            actor["sectors"] = {"motor": actor["sectors"]["motor"]}
        a["customer_groups"] = [g for g in a["customer_groups"] if g["sector_id"] == "motor"]
        for side in a["assignments"]: a["assignments"][side] = [g for g in a["assignments"][side] if g["sector_id"] == "motor"]
        a["insurers"][-1]["insurer_id"] = 41
        for g in a["customer_groups"]:
            if g["initial_insurer_id"] == 3: g["initial_insurer_id"] = 41
        for side in a["assignments"]:
            for g in a["assignments"][side]:
                if g["insurer_id"] == 3: g["insurer_id"] = 41
        a["peer_groups"] = []
        result = self.checked(a)
        self.assertTrue(any(r["insurer_id"] == 41 for r in result["sides"]["baseline"]["vu_rows"]))
        self.assertEqual(actor_draws(1, 1, 6), actor_draws(1, 1, 6))
        self.assertNotEqual(actor_draws(1, 1, 6), actor_draws(1, 41, 6))
        self.assertEqual(row(result, sector="life")["closing_assets"], "0.0000")
        self.assertIsNone(row(result, sector="life")["weighted_price"])

    def test_no_mutation_and_ap3_contract_regression(self):
        source = workshop_case("switch", 10); before = deepcopy(source)
        self.checked(source); self.assertEqual(source, before)
        old = ap3_calculate(ap3_case("price", 100))
        self.assertTrue(old["valid"])
        delta = Decimal(old["sides"]["variant"]["total_rows"][-1]["closing_equity"]) - Decimal(old["sides"]["baseline"]["total_rows"][-1]["closing_equity"])
        self.assertEqual(delta, Decimal(-28690))

    def test_threshold_uninsured_and_fractional_claim_rounding(self):
        source = workshop_case("switch", 10)
        source["damage_indicators"][5] = "0.9"
        source["customer_groups"][0]["insurance_threshold"] = "0.5"
        result = self.checked(source)
        decision = next(r for r in result["sides"]["baseline"]["customer_decisions"] if r["period"] == 6)
        self.assertIsNone(decision["insurer_id"])
        self.assertEqual(decision["uninsured_loss"], "40.0000")
        self.assertEqual(row(result)["insurance_expense"], "0.0000")
        source["damage_indicators"][5] = "0.1"
        source["customer_groups"][0]["risk_periods"][5].update(loss="0.0003", paid_share="0.5")
        result = self.checked(source)
        actor = next(r for r in result["sides"]["baseline"]["vu_rows"] if r["period"] == 6 and r["insurer_id"] == 2)
        self.assertEqual((actor["new_claims_paid"], actor["closing_liabilities"]), ("0.0002", "0.0001"))
        self.assertEqual(Decimal(actor["closing_assets"]), Decimal(actor["closing_liabilities"]) + Decimal(actor["closing_equity"]))

    def test_distinct_actuarial_sources_and_measure_channels_not_shared(self):
        source = workshop_case("market", 10, 3)
        opening = source["insurers"][1]["sectors"]["life"]["source"]["opening"]
        opening.update(opening_backing_assets="20000", opening_equity="19000")
        source["measures"]["variant"].append({"measure_id": "Lebensanpassung", "insurer_id": 1, "sector_id": "life", "decision_period": 6,
            "lead_periods": 0, "duration": 2, "cost": "4", "overrides": {"rate_per_period": "0.001"}})
        result = self.checked(source)
        records = result["sides"]["variant"]["vu_rows"]
        one = next(r for r in records if r["insurer_id"] == 1 and r["period"] == 1 and r["sector_id"] == "life")
        two = next(r for r in records if r["insurer_id"] == 2 and r["period"] == 1 and r["sector_id"] == "life")
        self.assertEqual((one["investment_income"], two["investment_income"]), ("5.0000", "10.0000"))
        six = next(r for r in records if r["insurer_id"] == 1 and r["period"] == 6 and r["sector_id"] == "life")
        self.assertEqual((six["parameters"]["rate_per_period"], six["measure_cost"]), ("0.001", "4.0000"))
        baseline_six = next(r for r in result["sides"]["baseline"]["vu_rows"] if r["insurer_id"] == 1 and r["period"] == 6 and r["sector_id"] == "life")
        self.assertEqual((baseline_six["parameters"]["rate_per_period"], baseline_six["measure_cost"]), ("0.0005", "0.0000"))

    def test_overlapping_measure_parameters_fail_atomically(self):
        source = workshop_case("market", 10, 3)
        source["measures"]["variant"].append({**deepcopy(source["measures"]["variant"][0]), "measure_id": "Doppelte_Aufnahme"})
        result = calculate(source)
        self.assertFalse(result["valid"]); self.assertEqual(result["sides"], {})
        self.assertIn("überlappende", result["issues"][0]["message"])

    def test_columnar_api_transport_is_lossless_for_null_and_missing_fields(self):
        result = self.checked(workshop_case("market", 10, 3))
        wire = wire_payload(result)
        decoded = {**wire, "sides": {side: {k: unpack_rows(v) for k, v in tables.items()} for side, tables in wire["sides"].items()}}
        decoded.pop("transport")
        self.assertEqual(decoded, result)

    def test_complete_41_vu_100_period_market_and_stable_existing_offers(self):
        forty = self.checked(workshop_case("market", 100, 40))
        forty_one = self.checked(workshop_case("market", 100, 41))
        self.assertEqual(len(forty_one["sides"]["variant"]["vu_rows"]), 41 * 4 * 100)
        for side in ("baseline", "variant"):
            offers40 = [(r["insurer_id"], r["period"], r["sector_id"], r.get("quoted_price"), r.get("draws")) for r in forty["sides"][side]["vu_rows"] if r["sector_id"] in ("motor", "property_liability")]
            offers41 = [(r["insurer_id"], r["period"], r["sector_id"], r.get("quoted_price"), r.get("draws")) for r in forty_one["sides"][side]["vu_rows"] if r["sector_id"] in ("motor", "property_liability") and r["insurer_id"] <= 40]
            self.assertEqual(offers40, offers41)
            for p in range(1, 101):
                total = row(forty_one, side=side, p=p)
                self.assertEqual(Decimal(total["closing_assets"]), Decimal(total["closing_liabilities"]) + Decimal(total["closing_equity"]))
                vu_sum = sum(Decimal(r["closing_equity"]) for r in forty_one["sides"][side]["vu_rows"] if r["period"] == p)
                self.assertEqual(vu_sum, Decimal(total["closing_equity"]))
            self.assertLess(len(json.dumps(wire_payload(forty_one), separators=(",", ":")).encode()), 48 * 1024 * 1024)

    def test_invalid_inputs_atomic_and_no_silent_limit_removal(self):
        mutators = [lambda d: d["insurers"].append(deepcopy(d["insurers"][0])),
                    lambda d: d["insurers"][0]["sectors"]["motor"].update(capacity=None),
                    lambda d: d["insurers"][0]["sectors"]["motor"]["opening"].update(assets="NaN"),
                    lambda d: d["assignments"]["baseline"].append(deepcopy(d["assignments"]["baseline"][0])),
                    lambda d: d["customer_groups"][0].update(initial_insurer_id=999),
                    lambda d: d["insurers"][0]["sectors"]["motor"]["periods"][0].update(old_claims_paid="21"),
                    lambda d: d["insurers"][1]["sectors"]["motor"]["opening"].update(assets="1", equity="1")]
        for change in mutators:
            source = workshop_case("switch", 10); change(source)
            result = calculate(source)
            self.assertFalse(result["valid"]); self.assertEqual(result["sides"], {}); self.assertIsNone(result["content_digest"])
        bad = workshop_case("market", 10, 3)
        bad["measures"]["variant"][0]["overrides"] = {"unknown": "2"}
        self.assertFalse(calculate(bad)["valid"])
        bad["measures"]["variant"][0]["overrides"] = {"capacity": "60"}
        bad["measures"]["variant"][0]["decision_period"] = 2
        self.assertFalse(calculate(bad)["valid"])
        bad = workshop_case("market", 10, 41)
        bad["insurers"].append({**deepcopy(bad["insurers"][-1]), "insurer_id": 42})
        self.assertFalse(calculate(bad)["valid"])


class MarketApiTests(unittest.TestCase):
    def test_market_is_mounted_in_real_desktop_api(self):
        from ims.api.app import create_app
        with TestClient(create_app()) as client:
            self.assertEqual(client.get("/api/market/contract").json()["max_vus"], 41)
            source = client.post("/api/market/workshop-case", json={"case_id": "switch", "period_count": 10, "vu_count": 2}).json()["source_input"]
            self.assertEqual(client.post("/api/market/calculate", json=source).status_code, 200)

    def test_fresh_calculation_portable_source_and_single_vu_excel_identity(self):
        with TestClient(create_market_app()) as client:
            source = client.post("/workshop-case", json={"case_id": "switch", "period_count": 10, "vu_count": 2}).json()["source_input"]
            reply = client.post("/calculate", json=source)
            self.assertEqual(reply.status_code, 200)
            result, etag = reply.json(), reply.headers["etag"]
            exported = client.post("/export.xlsx", json={"source_input": source, "insurer_id": 2}, headers={"If-Match": etag})
            self.assertEqual(exported.status_code, 200)
            self.assertEqual(exported.headers["etag"], etag)
            book = load_workbook(BytesIO(exported.content), read_only=True)
            records = list(book["Baseline"].values)
            fields = records[0]
            selected = [dict(zip(fields, r)) for r in records[1:]]
            self.assertEqual({r["insurer_id"] for r in selected}, {"2"})
            self.assertEqual(next(r for r in selected if r["period"] == "6")["closing_assets"], "79.0000")
            portable = client.post("/source.json", json=source, headers={"If-Match": etag})
            self.assertEqual(client.post("/calculate", json=portable.json()).headers["etag"], etag)
            source["seed"] += 1
            self.assertEqual(client.post("/export.xlsx", json={"source_input": source, "insurer_id": 2}, headers={"If-Match": etag}).status_code, 412)

    def test_invalid_export_id_nonfinite_json_and_atomic_errors(self):
        with TestClient(create_market_app()) as client:
            self.assertEqual(client.post("/calculate", content=b'{"seed":NaN}').status_code, 422)
            source = workshop_case("capacity", 10)
            result = client.post("/calculate", json=source)
            self.assertEqual(client.post("/export.xlsx", json={"source_input": source, "insurer_id": 99}, headers={"If-Match": result.headers["etag"]}).status_code, 422)
            self.assertEqual(client.post("/export.xlsx", json={"source_input": source, "insurer_id": True}).status_code, 422)
