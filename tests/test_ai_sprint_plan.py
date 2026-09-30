"""Delivery-plan gates: omitted work and premature starts must fail."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "ims_sprint_plan", ROOT / "scripts/planning/ims_sprint_plan.py"
)
sprint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sprint)


class SprintPlanTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads(sprint.DEFAULT_PLAN.read_text(encoding="utf-8"))
        # Test progression independently of future changes to the live status.
        for package in self.plan["packages"]:
            package["status"] = "planned"
            package["completion_evidence"] = []

    def done(self, index):
        package = self.plan["packages"][index]
        package["status"] = "done"
        package["completion_evidence"] = ["Test fixture: verified acceptance record."]

    def test_live_manifest_is_valid(self):
        sprint.validate(json.loads(sprint.DEFAULT_PLAN.read_text(encoding="utf-8")))

    def test_auto_respects_progression(self):
        self.assertEqual(sprint.select_package(sprint.validate(self.plan), "auto")["id"], "AP1")
        self.done(0)
        self.assertEqual(sprint.select_package(sprint.validate(self.plan), "auto")["id"], "AP2")
        self.done(1)
        self.assertEqual(sprint.select_package(sprint.validate(self.plan), "auto")["id"], "AP3")
        self.done(2)
        self.assertIsNone(sprint.select_package(sprint.validate(self.plan), "auto"))

    def test_no_old_requirement_can_disappear_or_be_counted_twice(self):
        for mutation, message in [
            (lambda p: p["packages"][2]["old_plan_ids"].pop(), "unvollständig"),
            (lambda p: p["packages"][2]["old_plan_ids"].append("PR191"), "Doppelte"),
            (lambda p: p["packages"][2]["old_plan_ids"].append("PR999"), "unvollständig"),
        ]:
            with self.subTest(message=message):
                plan = copy.deepcopy(self.plan)
                mutation(plan)
                with self.assertRaisesRegex(sprint.PlanError, message):
                    sprint.validate(plan)

    def test_packaging_cannot_be_silently_moved_back_to_domain_work(self):
        self.plan["packages"][0]["old_plan_ids"].remove("PR191")
        self.plan["packages"][2]["old_plan_ids"].append("PR191")
        with self.assertRaisesRegex(sprint.PlanError, "Windows-Schritte"):
            sprint.validate(self.plan)

    def test_dependency_cycles_and_unknown_dependencies_fail(self):
        self.plan["packages"][0]["depends_on"] = ["AP3"]
        with self.assertRaisesRegex(sprint.PlanError, "Zyklische"):
            sprint.validate(self.plan)
        self.plan["packages"][0]["depends_on"] = ["AP9"]
        with self.assertRaisesRegex(sprint.PlanError, "unbekannte"):
            sprint.validate(self.plan)

    def test_done_requires_evidence_and_completed_dependencies(self):
        self.plan["packages"][1]["status"] = "done"
        with self.assertRaisesRegex(sprint.PlanError, "completion_evidence"):
            sprint.validate(self.plan)
        self.done(1)
        with self.assertRaisesRegex(sprint.PlanError, "unerledigte Abhängigkeiten"):
            sprint.validate(self.plan)

    def test_explicit_selection_cannot_skip_gates(self):
        for selection in ["AP2", "AP3"]:
            with self.subTest(selection=selection):
                with self.assertRaisesRegex(sprint.PlanError, "offene Abhängigkeiten"):
                    sprint.select_package(self.plan, selection)

    def test_blocked_package_does_not_create_work(self):
        self.plan["packages"][0]["status"] = "blocked"
        sprint.validate(self.plan)
        self.assertIsNone(sprint.select_package(self.plan, "auto"))
        with self.assertRaisesRegex(sprint.PlanError, "blockiert"):
            sprint.select_package(self.plan, "AP1")

    def test_sources_must_exist_inside_repo(self):
        for path in ["../outside.md", "/etc/passwd", "docs/does-not-exist.md"]:
            with self.subTest(path=path):
                self.plan["packages"][0]["source_files"] = [path]
                with self.assertRaises(sprint.PlanError):
                    sprint.validate(self.plan)

    def test_cli_writes_handoff_and_clears_stale_output_on_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            manifest = folder / "plan.json"
            manifest.write_text(json.dumps(self.plan), encoding="utf-8")
            output = folder / "output"
            args = ["--plan", str(manifest), "--out", str(output),
                    "--commit", self.plan["baseline_commit"]]
            self.assertEqual(sprint.main(args), 0)
            order = (output / "codex-work-order.md").read_text(encoding="utf-8")
            self.assertIn("AP1", order)
            self.assertIn("Planungs-PR angenommen?", order)
            self.assertIn("Clean-VM-Nachweis", order)
            self.assertEqual(sprint.main(args + ["--package", "AP3"]), 1)
            self.assertFalse((output / "codex-work-order.md").exists())
            self.assertFalse((output / "plan-report.md").exists())

    def test_cli_handles_all_done_without_a_new_order(self):
        for index in range(3):
            self.done(index)
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            manifest = folder / "plan.json"
            manifest.write_text(json.dumps(self.plan), encoding="utf-8")
            self.assertEqual(sprint.main([
                "--plan", str(manifest), "--out", str(folder / "output"),
                "--commit", self.plan["baseline_commit"],
            ]), 0)
            self.assertFalse((folder / "output/codex-work-order.md").exists())
            self.assertIn("Kein Paket", (folder / "output/plan-report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
