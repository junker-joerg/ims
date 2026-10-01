"""Versioned, uncalibrated capital assumptions for the curated seminar only."""


def assumptions(period_count: int, case_id: str = "price") -> dict:
    stressed_assets = "5000" if case_id == "capital" else "1000"
    asset_loss = "500" if case_id == "capital" else "100"
    return {"schema_version": "ims.seminar-capital-assumptions.v1", "model_period": period_count,
        "reference_date": "2026-10-01", "assumption_note": f"Explizite unkalibrierte Seminarannahme: Kfz-Aktivastress {asset_loss} und Betriebsverlust 50; keine regulatorische Kalibrierung",
        "adjustments": {sector: {"asset_delta": "0", "liability_delta": "0"} for sector in ("motor", "property_liability", "life", "health")},
        "exposures": {key: {"amount": stressed_assets if key == "motor_assets" else "0", "rate": "0.1" if key == "motor_assets" else "0"} for key in ("motor_assets", "motor_claims", "property_claims", "life_liability", "health_benefit", "health_assets")},
        "factor_loadings": {key: "1" for key in ("asset_market_value", "non_life_claim_obligation", "life_obligation", "health_benefit_obligation", "counterparty_model_loss", "operational_model_loss")},
        "operational_loss": "50", "buffer_capacity": "0", "buffer_applied": "0", "max_loss": "200", "min_equity": "1000"}
