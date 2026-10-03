"""Fresh, bounded AP7 market/process result with a complete portable source."""
from __future__ import annotations

from copy import deepcopy
from decimal import localcontext
import json

from ims.accounting.management_case import digest
from ims.market.runner import side_result
from ims.market.shock_contract import MAX_INPUT_BYTES, MAX_RESULT_BYTES, RESULT_VERSION, validate
from ims.market.shock_plan import ShockPlan
from ims.market.transport import wire_payload
from ims.strategies.modern_bridge import ContractError


def calculate(value: object) -> dict:
    try:
        if len(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")) > MAX_INPUT_BYTES:
            raise ContractError("$", "AP7-Eingang überschreitet 16 MiB; kein Teilergebnis")
        with localcontext() as context:
            context.prec = 64
            bundle, reference = validate(value)
            cache, sides = {}, {}
            for side in ("baseline", "variant"):
                plan = ShockPlan(bundle, side)
                sides[side] = {**side_result(bundle["model_input"], plan.model_side, cache, plan), **plan.tables()}
            for name in ("vu_rows", "customer_decisions", "ict_process_rows", "life_demand_rows", "cost_rows"):
                prefixes = [[row for row in sides[side][name] if row.get("period", 1000) <= 5] for side in ("baseline", "variant")]
                if prefixes[0] != prefixes[1]:
                    raise ContractError("$", "Gemeinsamer tatsächlicher Anfang P1–P5 verletzt")
            core = {"schema_version": RESULT_VERSION, "source_input": deepcopy(bundle["model_input"]),
                    "source_bundle": deepcopy(bundle["reference_bundle"]), "shock_bundle": deepcopy(bundle),
                    "reference": reference, "input_digest": digest(bundle), "period_count": bundle["model_input"]["period_count"],
                    "sides": sides, "comparison": bundle["comparison"],
                    "comparison_labels": {"baseline": "Derselbe Schock ohne Gegenmaßnahme", "variant": "Derselbe Schock mit Gegenmaßnahme"} if bundle["comparison"] == "shock_with_response" else {"baseline": "Kein Schock; beschlossene Vorsorge bleibt", "variant": "Schock; dieselbe beschlossene Vorsorge"},
                    "clock": {"period_hours": "24", "meaning": "Deklarierte Prozessstunden, keine Kalender-/Jahreskalibrierung"},
                    "limits": ["accepted_bafin_reference_workshop", "assumed_provider_and_product_profiles", "deterministic_bounded_life_demand", "claims_service_administration_only", "no_surrender", "no_cross_sector_funding", "no_dynamic_insolvency", "no_regulatory_capital"],
                    "historical_full_equality_claim": False, "regulatory_metrics": {"scr": None, "mcr": None, "coverage_ratio": None}}
            result = {**core, "valid": True, "issues": [], "content_digest": digest(core), "writes_performed": False, "partial_result_returned": False}
            if len(json.dumps(wire_payload(result), ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > MAX_RESULT_BYTES:
                raise ContractError("$", "Vollständiges AP7-Ergebnis überschreitet 64 MiB; kein Teilergebnis")
            return result
    except (ContractError, ValueError, TypeError, KeyError, StopIteration, ArithmeticError, RecursionError) as exc:
        return {"schema_version": RESULT_VERSION, "valid": False, "issues": [{"path": getattr(exc, "path", "$"), "code": "shock_contract_invalid", "message": str(exc) or "Unvollständiger AP7-Vertrag"}],
                "sides": {}, "content_digest": None, "partial_result_returned": False, "writes_performed": False}
