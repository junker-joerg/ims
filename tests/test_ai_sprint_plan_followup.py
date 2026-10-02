"""Follow-up provenance, coverage and authorization boundaries."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT / f"scripts/planning/{name}.py")
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
sprint=module("ims_sprint_plan")
followup=module("ims_followup_plan")
BOARD=ROOT/"docs/plans/ims_board_strategy_plan.json"
MARKET=ROOT/"docs/plans/ims_explainable_market_plan.json"


class FollowupPlanTests(unittest.TestCase):
    def setUp(self):
        self.plan=followup.read_json(BOARD)
        self.sha=followup.resolve_ref(ROOT,"origin/main")
        # Exercise states independently of later package merges. These are
        # explicit test fixtures, never real human authorization records.
        self.market=followup.read_json(MARKET)
        for p in self.market["packages"]:
            p.update(status="planned",completion_evidence=[])
            for field in ("technically_complete","merged_to_main"):
                if field in p: p[field]=False
        self.plan.update(status="proposed",approval=None)
        for p in self.plan["packages"]:
            p.update(status="proposed",plan_status="proposed",technically_complete=False,
                implementation_authorized=False,merged_to_main=False,completion_evidence=[],merge_evidence=[])
        self.read_original=followup.read_json
        def read_fixture(path):
            if Path(path).resolve()==MARKET: return copy.deepcopy(self.market)
            return self.read_original(path)
        def main_fixture(root,sha,path):
            if path=="docs/plans/ims_explainable_market_plan.json": return copy.deepcopy(self.market)
            if path=="docs/plans/ims_board_strategy_plan.json": return copy.deepcopy(self.plan)
            return self.read_original(ROOT/path)
        read_patch=patch.object(followup,"read_json",side_effect=read_fixture)
        main_patch=patch.object(followup,"read_at_ref",side_effect=main_fixture)
        read_patch.start(); main_patch.start()
        self.addCleanup(read_patch.stop); self.addCleanup(main_patch.stop)

    def portfolio(self,plan=None):
        return followup.load_portfolio(plan or self.plan,BOARD,ROOT,sprint.validate)

    def receipt(self,folder,pid="AP4"):
        path=folder/"authorization.json"
        path.write_text(json.dumps(dict(schema_version="ims.execution-authorization.v1", package=pid,
            scope="implementation",plan_commit=self.sha,authorized_by="Human test fixture",
            authorized_at="2026-10-02T12:00:00+02:00",user_request="Test fixture: authorize exactly this implementation package.")),encoding="utf-8")
        return path

    def test_live_portfolio_and_source_matrix(self):
        portfolio=self.portfolio()
        self.assertEqual(len(portfolio["packages"]),14)
        self.assertEqual(len(self.plan["requirements"]),65)
        self.assertEqual(portfolio["by_id"]["AP10"]["depends_on"],["AP7"])
        self.assertEqual(portfolio["by_id"]["AP13"]["depends_on"],["AP10","AP11"])

    def test_accepted_market_only_is_supported(self):
        p=followup.load_portfolio(followup.read_json(MARKET),MARKET,ROOT,sprint.validate)
        self.assertEqual(len(p["packages"]),9)
        self.assertEqual(followup.select(p,"auto","preview",ROOT,self.sha,None)["id"],"AP4")

    def test_auto_preview_prefers_accepted_package(self):
        p=self.portfolio()
        self.assertEqual(followup.select(p,"auto","preview",ROOT,self.sha,None)["id"],"AP4")
        order=followup.render_order(p,p["by_id"]["AP10"],"preview",self.sha,self.sha,ROOT,None)
        for text in ("VORSCHAU", "NICHT ZUR UMSETZUNG", "Entscheidungsnutzen", "Abnahmen", "REF-01", "AP7", "Fortsetzen"):
            self.assertIn(text,order)

    def test_no_missing_duplicate_or_unknown_requirement(self):
        for mutation in (lambda p:p["requirements"].pop(), lambda p:p["requirements"].append(copy.deepcopy(p["requirements"][0])), lambda p:p["requirements"][0].update(id="AP10-R99")):
            p=copy.deepcopy(self.plan); mutation(p)
            with self.assertRaises(followup.FollowupError): self.portfolio(p)

    def test_requirement_cannot_disappear_from_target_package(self):
        self.plan["packages"][0]["requirement_ids"].pop()
        with self.assertRaisesRegex(followup.FollowupError,"Anforderungszuordnung"):
            self.portfolio()

    def test_disposition_requires_reason_and_acceptance_impact(self):
        for key in ("reason","acceptance_impact","original_assignment"):
            p=copy.deepcopy(self.plan); p["requirements"][0][key]=""
            with self.assertRaises(followup.FollowupError): self.portfolio(p)

    def test_deferred_requirements_stay_in_backlog(self):
        self.plan["backlog"].pop()
        with self.assertRaisesRegex(followup.FollowupError,"Backlog"):
            self.portfolio()

    def test_deferred_package_and_plan_cannot_generate_order(self):
        self.plan["packages"][0].update(status="deferred",plan_status="deferred")
        p=self.portfolio()
        for mode in ("preview","authorized"):
            with self.assertRaisesRegex(followup.FollowupError,"zurückgestellt"):
                followup.select(p,"AP10",mode,ROOT,self.sha,None)
        market=followup.read_json(MARKET); market["status"]="deferred"
        p=followup.load_portfolio(market,MARKET,ROOT,sprint.validate)
        self.assertIsNone(followup.select(p,"auto","preview",ROOT,self.sha,None))

    def test_proposal_cannot_be_authorized_even_with_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt=self.receipt(Path(temporary),"AP10")
            with self.assertRaisesRegex(followup.FollowupError,"Vorschlag"):
                followup.select(self.portfolio(),"AP10","authorized",ROOT,self.sha,receipt)

    def test_proposed_done_or_fake_authorized_status_rejected(self):
        for change in (dict(implementation_authorized=True),dict(status="done",technically_complete=True,completion_evidence=["fake"]),dict(completion_evidence=["fake"])):
            p=copy.deepcopy(self.plan); p["packages"][0].update(change)
            with self.assertRaises(followup.FollowupError): self.portfolio(p)

    def test_accepted_status_requires_plan_approval_evidence(self):
        self.plan["status"]="accepted"
        with self.assertRaisesRegex(followup.FollowupError,"Planannahmebeleg"):
            self.portfolio()

    def test_cycles_duplicate_ids_and_unknown_dependencies_rejected(self):
        for change in (dict(depends_on=["AP14"]),dict(depends_on=["AP99"]),dict(depends_on=["AP7","AP7"]),dict(id="AP11")):
            p=copy.deepcopy(self.plan); p["packages"][0].update(change)
            with self.assertRaises(followup.FollowupError): self.portfolio(p)

    def test_invalid_source_path_or_unknown_source_id(self):
        for path in ("../escape.md", "C:/Windows/test.md", "docs/missing.md"):
            p=copy.deepcopy(self.plan); p["packages"][0]["source_files"]=[path]
            with self.assertRaises(followup.FollowupError): self.portfolio(p)
        self.plan["packages"][0]["source_ids"]=["S999"]
        with self.assertRaisesRegex(followup.FollowupError,"Quellen-ID"):
            self.portfolio()

    def test_accepted_ap4_needs_explicit_implementation_receipt(self):
        with self.assertRaisesRegex(followup.FollowupError,"Umsetzungsfreigabe"):
            followup.select(self.portfolio(),"AP4","authorized",ROOT,self.sha,None)

    def test_valid_accepted_scope_with_main_dependencies_and_fixture_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt=self.receipt(Path(temporary))
            p=self.portfolio()
            selected=followup.select(p,"auto","authorized",ROOT,self.sha,receipt)
            self.assertEqual(selected["id"],"AP4")
            order=followup.render_order(p,selected,"authorized",self.sha,self.sha,ROOT,receipt)
            self.assertIn("FREIGEGEBENER ARBEITSAUFTRAG",order)
            self.assertIn("kein automatischer Start",order)

    def test_wrong_package_scope_stale_commit_and_missing_human_receipt_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt=self.receipt(Path(temporary)); original=followup.read_json(receipt)
            for key,value in [("package","AP5"),("scope","plan"),("plan_commit","0"*40),("authorized_by",""),("authorized_at","2026-10-02"),("user_request","")]:
                changed={**original,key:value}; receipt.write_text(json.dumps(changed),encoding="utf-8")
                with self.subTest(key=key), self.assertRaises(followup.FollowupError):
                    followup.select(self.portfolio(),"AP4","authorized",ROOT,self.sha,receipt)

    def test_local_accepted_board_without_main_acceptance_is_rejected(self):
        self.plan["status"]="accepted"; self.plan["approval"]={"user_request":"Test plan acceptance"}
        self.plan["packages"][0].update(plan_status="accepted",status="planned")
        with patch.object(followup,"read_at_ref",return_value=followup.read_json(BOARD)):
            with self.assertRaisesRegex(followup.FollowupError,"Planannahme fehlt"):
                followup.authorize(self.portfolio(),self.portfolio()["by_id"]["AP10"],ROOT,self.sha,None)

    def test_done_in_branch_not_in_main_is_not_completed_dependency(self):
        p=self.portfolio()["by_id"]["AP4"]
        p.update(status="done",technically_complete=True,completion_evidence=["branch only"])
        self.assertFalse(followup.main_done(p,ROOT,self.sha))

    def test_done_without_completion_or_fake_merge_is_rejected(self):
        p=self.portfolio()
        market=followup.read_json(MARKET)
        market["packages"][0]["status"]="done"
        with self.assertRaisesRegex(followup.FollowupError,"Abschlussbelege"):
            followup.load_portfolio(market,MARKET,ROOT,sprint.validate)
        self.plan["packages"][0].update(merged_to_main=True,merge_evidence=["fake"])
        with self.assertRaisesRegex(followup.FollowupError,"Merge"):
            self.portfolio()

    def test_unmerged_transitive_dependency_blocks_authorized_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt=self.receipt(Path(temporary))
            with patch.object(followup,"main_done",return_value=False):
                with self.assertRaisesRegex(followup.FollowupError,"main-Belege"):
                    followup.select(self.portfolio(),"AP4","authorized",ROOT,self.sha,receipt)

    def test_changed_scope_cannot_use_old_main_approval(self):
        p=self.portfolio(); p["by_id"]["AP4"]["_raw"]=copy.deepcopy(p["by_id"]["AP4"]["_raw"])
        p["by_id"]["AP4"]["_raw"]["deliverables"].append("unapproved expansion")
        with self.assertRaisesRegex(followup.FollowupError,"Arbeitsumfang"):
            followup.authorize(p,p["by_id"]["AP4"],ROOT,self.sha,None)

    def test_cli_preview_and_failure_clear_stale_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder=Path(temporary)
            args=["--plan",str(BOARD),"--package","AP10","--out",str(folder)]
            self.assertEqual(sprint.main(args),0)
            self.assertIn("VORSCHAU",(folder/"codex-work-order.md").read_text(encoding="utf-8"))
            self.assertEqual(sprint.main(args+["--mode","authorized"]),1)
            self.assertFalse((folder/"codex-work-order.md").exists())
            self.assertFalse((folder/"plan-report.md").exists())

    def test_ap1_to_ap3_keep_separate_compatible_mode(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(sprint.main(["--out",temporary]),0)
            self.assertEqual(sprint.main(["--out",temporary,"--mode","authorized"]),1)

    def test_main_reference_and_checkout_commit_cannot_be_spoofed(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(sprint.main(["--plan",str(BOARD),"--out",temporary,"--commit","0"*40]),1)


if __name__ == "__main__":
    unittest.main()
