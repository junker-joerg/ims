"""Bounded local common market API with fresh digest-guarded single-VU exports."""
import json
from threading import BoundedSemaphore

from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from ims.api.seminar import failed, request_json
from ims.market.contract import HORIZONS, INPUT_VERSION, MAX_COHORTS, MAX_VUS, RULE_PARAMETERS
from ims.market.export import single_vu_workbook
from ims.market.presets import CASES, workshop_case
from ims.market.runner import MAX_RESULT_BYTES, calculate
from ims.market.reference import BUNDLE_VERSION, build_bundle, reference_values, calculate as reference_calculate
from ims.desktop.paths import resource_root
from ims.market.transport import wire_payload
from ims.strategies.modern_bridge import ContractError, exact


def create_market_app() -> Starlette:
    gate = BoundedSemaphore(1)
    headers = {"Cache-Control": "no-store"}

    async def preset(request):
        try:
            value = exact(await request_json(request), {"case_id", "period_count", "vu_count"}, "$")
            source = workshop_case(value["case_id"], value["period_count"], value["vu_count"])
            return JSONResponse({"valid": True, "title": CASES[value["case_id"]], "source_input": source}, headers=headers)
        except (ValueError, TypeError) as exc:
            return JSONResponse(failed(exc if isinstance(exc, ContractError) else ContractError("$", str(exc))), status_code=422, headers=headers)

    async def reference_preset(request):
        try:
            value = exact(await request_json(request), {"period_count", "workshop", "overrides"}, "$")
            catalog = json.loads((resource_root() / "seminar_cases/bafin_2024_catalog.json").read_text(encoding="utf-8"))
            source = build_bundle(catalog, value["period_count"], value["workshop"], value["overrides"])
            return JSONResponse({"valid": True, "title": source["title"], "source_bundle": source,
                                 "source_input": source["model_input"],
                                 "reference": reference_values(catalog, source["overrides"], source["workshop"])}, headers=headers)
        except (ContractError, ValueError, TypeError, KeyError, ArithmeticError) as exc:
            return JSONResponse(failed(exc if isinstance(exc, ContractError) else ContractError("$", str(exc))), status_code=422, headers=headers)

    async def action(request):
        try:
            value = await request_json(request)
            exporting = request.url.path.endswith("/export.xlsx")
            if exporting:
                exact(value, {"source_input", "insurer_id"}, "$")
                if type(value["insurer_id"]) is not int:
                    raise ContractError("$.insurer_id", "Eindeutige Einzel-VU erforderlich")
            source = value["source_input"] if exporting else value
        except ContractError as exc:
            return JSONResponse(failed(exc), status_code=422, headers=headers)
        if not gate.acquire(blocking=False):
            return JSONResponse(failed(ContractError("$", "Eine gemeinsame Marktrechnung läuft bereits")), status_code=409, headers=headers)
        def work():
            try:
                result = reference_calculate(source) if isinstance(source, dict) and source.get("schema_version") == BUNDLE_VERSION else calculate(source)
                if not result["valid"]:
                    return JSONResponse(result, status_code=422, headers=headers)
                etag = '"' + result["content_digest"] + '"'
                reply = {**headers, "ETag": etag}
                if exporting or request.url.path.endswith("/source.json"):
                    if request.headers.get("if-match") != etag:
                        return JSONResponse(failed(ContractError("$", "Export benötigt denselben unveränderten Marktnachweis")), status_code=412, headers=headers)
                    if exporting:
                        if value["insurer_id"] not in {a["insurer_id"] for a in result["source_input"]["insurers"]}:
                            return JSONResponse(failed(ContractError("$.insurer_id", "VU gehört nicht zum Modellmarkt")), status_code=422, headers=headers)
                        content = single_vu_workbook(result, value["insurer_id"])
                        return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={**reply, "Content-Disposition": f'attachment; filename="IMS-VU{value["insurer_id"]}-{result["content_digest"][:12]}.xlsx"'})
                    return Response(json.dumps(source, ensure_ascii=False, allow_nan=False).encode("utf-8"), media_type="application/json", headers={**reply, "Content-Disposition": f'attachment; filename="IMS-Modellmarkt-{result["content_digest"][:12]}.json"'})
                return JSONResponse(wire_payload(result), headers=reply)
            finally:
                gate.release()
        return await run_in_threadpool(work)

    return Starlette(routes=[Route("/contract", lambda r: JSONResponse({"schema_version": INPUT_VERSION, "max_vus": MAX_VUS,
        "max_customer_groups": MAX_COHORTS, "horizons": HORIZONS, "rules": {k: sorted(v) for k, v in RULE_PARAMETERS.items()}, "max_result_bytes": MAX_RESULT_BYTES}, headers=headers)),
        Route("/workshop-case", preset, methods=["POST"]), Route("/reference-case", reference_preset, methods=["POST"]), Route("/calculate", action, methods=["POST"]),
        Route("/export.xlsx", action, methods=["POST"]), Route("/source.json", action, methods=["POST"])])
