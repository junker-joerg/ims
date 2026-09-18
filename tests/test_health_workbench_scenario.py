import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ims.accounting.health_period_chain import run_health_period_chain


ROOT = Path(__file__).resolve().parent.parent
HORIZONS = (1, 2, 5, 10, 25, 50, 100)


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js fuer Workbench-Vertragstest erforderlich")
def test_workbench_inputs_are_valid_and_keep_exact_horizon_prefixes() -> None:
    script = """
import { buildHealthInput, defaultHealthDraft, HEALTH_HORIZONS } from './frontend/src/healthScenario.ts';
process.stdout.write(JSON.stringify(HEALTH_HORIZONS.map(periodCount => {
  const draft = { ...defaultHealthDraft(), periodCount };
  return {
    periodCount,
    baseline: buildHealthInput(draft, 'baseline'),
    variant: buildHealthInput(draft, 'variant')
  };
})));
"""
    completed = subprocess.run(
        ["node", "--experimental-strip-types", "--input-type=module", "-e", script],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    cases = json.loads(completed.stdout)
    assert tuple(case["periodCount"] for case in cases) == HORIZONS
    reports = {}
    for case in cases:
        count = case["periodCount"]
        for side in ("baseline", "variant"):
            value = case[side]
            assert value["sources"]["scenario_id"] == "seminar_health_01"
            assert value["sources"]["variant_id"] == side
            assert len(value["sources"]["new_business"]["periods"]) == count
            assert len(value["sources"]["exits"]["periods"]) == count
            report = run_health_period_chain(value).to_dict()
            assert report["valid"] is True, report["issues"]
            assert report["calculated_period_count"] == count
            reports[(side, count)] = report["rows"]

    for count in HORIZONS:
        for side in ("baseline", "variant"):
            assert reports[(side, count)] == reports[(side, 100)][:count]
    assert reports[("baseline", 100)][:5] == reports[("variant", 100)][:5]
    assert reports[("baseline", 100)][5]["closing_cash"] == "1552.0000"
    assert reports[("variant", 100)][5]["closing_cash"] == "1492.0000"
    assert reports[("baseline", 100)][5]["closing_equity"] != reports[("variant", 100)][5]["closing_equity"]
    assert reports[("baseline", 100)][-1]["closing_active_policies"] == 100


def test_workbench_entry_and_export_controls_are_bound_to_health_api() -> None:
    component = (ROOT / "frontend/src/HealthWorkbench.tsx").read_text(encoding="utf-8")
    app = (ROOT / "frontend/src/main.tsx").read_text(encoding="utf-8")
    for marker in (
        'data-testid="health-workbench"', 'data-testid="health-results"',
        '"/api/accounting/health-period-chain"',
        'explicit_storage_release: true', '"If-Match"',
        'format === "xlsx"', 'health-history-list', 'historyReady',
        'stored_result_verified',
    ):
        assert marker in component
    assert 'href="#health"' in app
    assert "<HealthWorkbench onReady={setHealthReady} />" in app
