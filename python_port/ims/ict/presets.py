"""Uncalibrated, fully declared workshop inputs; never historical defaults."""

from ims.ict.contract import INPUT_VERSION, PROCESSES


def workshop_case() -> dict:
    note = "Explizite unkalibrierte Workshop-Annahme; unabhängige Prozesswarteschlangen, keine historische Zuordnung."
    return {
        "schema_version": INPUT_VERSION, "scenario_id": "ict-shared-provider-workshop", "variant_id": "outage",
        "source_kind": "declared_workshop_not_historical_or_regulatory", "assumption_note": note,
        "period_hours": "24", "period_count": 100,
        "providers": [{"provider_id": key, "assumption_note": note} for key in ("shared-provider", "local-operator")],
        "assets": [
            {"asset_id": "platform", "provider_id": "shared-provider", "depends_on": [], "assumption_note": note},
            *[{"asset_id": f"portal-{i}", "provider_id": "local-operator", "depends_on": ["platform"], "assumption_note": note} for i in (1, 2)],
        ],
        "services": [
            {"service_id": f"vu-{i}-{process}", "insurer_id": i, "process": process, "asset_ids": [f"portal-{i}"],
             "demand_per_hour": "10", "capacity_per_hour": "12", "unit_margin": "2" if process == "sales" else "1" if process == "underwriting" else "0",
             "backlog_cost_per_unit_period": "0.02", "rework_cost_per_unit": "0.25", "opening_backlog": "0", "assumption_note": note}
            for i in (1, 2) for process in PROCESSES
        ],
        "insurers": [{"insurer_id": i, "opening_assets": "10000", "opening_liabilities": "3000",
                      "baseline_profit_per_period": "100", "max_loss_per_period": "300", "min_equity": "6000", "assumption_note": note} for i in (1, 2)],
        "events": [{"event_id": "shared-outage", "kind": "provider_outage", "target_id": "shared-provider",
                    "start_hour": "1176", "duration_hours": "48", "capacity_loss_fraction": "1", "rework_fraction": "0", "assumption_note": note}],
        "strategies": [],
    }
