"""Record existing IMS calculations; no new simulation channel is implemented."""
from copy import deepcopy
from decimal import Decimal
import argparse
import json
from pathlib import Path
import platform
import subprocess

from ims.ict.presets import workshop_case
from ims.ict.simulation import calculate
from ims.strategies.modern_presets import workshop_case as market_case
from ims.strategies.modern_bridge import calculate as market_calculate


def probe() -> dict:
    cases = []
    for name, kind, shock in [
        ("outage", None, True), ("no_shock", None, False),
        ("restart", "restart", True), ("restart_no_shock", "restart", False),
        ("scalar_fallback", "fallback", True), ("scalar_fallback_no_shock", "fallback", False),
    ]:
        doc = workshop_case()
        if not shock:
            doc["events"] = []
        if kind:
            doc["strategies"] = [dict(strategy_id=kind, kind=kind,
                asset_id="platform" if kind == "restart" else "portal-1",
                start_hour="1188", through_hour="1224", effectiveness="0.5",
                cost_per_hour="1", assumption_note="Existing-contract probe, not a tested independent recovery capability.")]
        result = calculate(doc)
        assert result["valid"], result
        assert result == calculate(deepcopy(doc)), "Replay differs"
        summary = []
        for insurer in (1, 2):
            rows = [r for r in result["variant"]["balance_rows"] if r["insurer_id"] == insurer]
            services = [r for r in result["variant"]["service_rows"] if r["insurer_id"] == insurer]
            totals = {key: str(sum(Decimal(r[key]) for r in rows)) for key in ("strategy_cost", "operational_impact", "period_profit")}
            summary.append(dict(insurer_id=insurer, totals=totals, final_balance=rows[-1],
                selected_balances=[r for r in rows if r["period"] in (49,50,51,52,53)],
                selected_services=[r for r in services if r["period"] in (50,51,52,100)]))
        cases.append(dict(id=name, input=doc, input_digest=result["input_digest"],
            content_digest=result["content_digest"], replay_equal=True,
            timeline=result["timeline"], summaries=summary))
    source = market_case("price")
    market = market_calculate(source)
    assert market["valid"], market
    assert market == market_calculate(deepcopy(source))
    return dict(schema_version="ims.board-baseline-probe.v1", evidence_type="actual_existing_model_run",
        product_main_commit="81146aa8657e2d507cc51c921207e80895f78340",
        python=platform.python_version(), cases=cases,
        market=dict(case="AP3 price, 100 periods", input_digest=market["input_digest"],
            content_digest=market["content_digest"], replay_equal=True,
            closing_rows={side: rows["total_rows"][-1] for side, rows in market["sides"].items()}),
        limitations=["Two declared insurers; independent process queues", "Scalar fallback is not independent-provider verification",
            "Restart is declared event shortening, not tested recovery", "No cash ledger or customer/risk transfer in ICT",
            "Operational probes are not a fair three-insurer strategy comparison", "No proprietary software tested"])


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args=parser.parse_args()
    result=probe()
    result["runner_commit"]=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
    print(f"Recorded {len(result['cases'])} existing ICT runs and AP3 price replay: {args.out}")


if __name__ == "__main__":
    main()
