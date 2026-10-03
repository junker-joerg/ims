"""Declare new AP7 policies in the existing life guarantee/period-chain format."""
from __future__ import annotations

from decimal import Decimal

from ims.strategies.modern_bridge import money


def add_policies(source: dict, issues: list[dict], offers: dict[int, dict], insurer_id: int) -> dict:
    """Preserve every old policy/flow; only append explicitly issued new policies."""
    histories: list[dict] = []
    for item in issues:
        if item["insurer_id"] != insurer_id:
            continue
        offer = offers[insurer_id]
        histories.append({**item, "reserve": Decimal(offer["allocation"]), "offer": offer})
    for row in source["periods"]:
        period = row["period"]
        for history in histories:
            issue, offer = history["issue_period"], history["offer"]
            policy_id = history["policy_id"]
            if period == issue:
                row["new_business"].append({
                    "cohort_id": policy_id, "issue_term_periods": offer["term_periods"],
                    "guaranteed_rate_per_period": offer["guarantee_rate"], "new_business_policies": 1,
                    "new_business_premiums_collected": offer["premium"], "new_business_liability_allocation": offer["allocation"],
                    "policies": [{"policy_id": policy_id, "new_business_premiums_collected": offer["premium"],
                                  "new_business_liability_allocation": offer["allocation"]}],
                })
            elif issue < period <= issue + offer["term_periods"]:
                credit = Decimal(money(history["reserve"] * Decimal(offer["guarantee_rate"])))
                history["reserve"] += credit + Decimal(offer["renewal_allocation"])
                due = period == issue + offer["term_periods"]
                row["policy_flows"].append({
                    "policy_id": policy_id, "renewal_premiums_collected": offer["renewal_premium"],
                    "renewal_liability_allocation": offer["renewal_allocation"], "death_benefit_if_death": "0",
                    "maturity_benefit_if_due": money(history["reserve"]) if due else "0",
                })
    return source
