"""Bounded API for the approved modern bridge and portable seminar sources."""

import json
from threading import BoundedSemaphore

from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from ims.api.guided_period_chain import workshop_input
from ims.api.management_case import exports
from ims.desktop.paths import resource_root
from ims.ict.presets import workshop_case as ict_case
from ims.strategies.modern_bridge import ContractError, calculate, contract_payload, exact
from ims.strategies.modern_presets import CASES, workshop_case
from ims.strategies.seminar_bundle import pack, unpack
from ims.strategies.seminar_capital import assumptions

MAX_INPUT_BYTES = 16 * 1024 * 1024


async def request_json(request) -> object:
    parts, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_INPUT_BYTES: raise ContractError("$", "Seminarquelle überschreitet 16 MiB")
        parts.append(chunk)
    def reject_constant(value): raise ValueError("Nichtendlicher JSON-Wert")
    try: return json.loads(b"".join(parts), parse_constant=reject_constant)
    except (ValueError, UnicodeDecodeError, RecursionError) as exc: raise ContractError("$", "Gültiges endliches JSON erforderlich") from exc


def failed(exc: ContractError) -> dict:
    return {"valid": False, "issues": [{"path": exc.path, "code": "seminar_contract_invalid", "message": str(exc)}], "content_digest": None,
        "sides": {}, "results": {}, "partial_result_returned": False, "writes_performed": False}


def create_seminar_app() -> Starlette:
    gate = BoundedSemaphore(1)
    headers = {"Cache-Control": "no-store"}

    async def curated(request):
        case_id = request.path_params["case_id"]
        path = resource_root() / "seminar_cases" / (case_id + ".json")
        if case_id not in CASES or not path.is_file():
            return JSONResponse(failed(ContractError("$", "Kuratierter Fall nicht verfügbar")), status_code=404, headers=headers)
        return FileResponse(path, media_type="application/json", filename=f"IMS-Seminar-{case_id}.json", headers=headers)

    async def preset(request):
        try:
            value = exact(await request_json(request), {"case_id", "period_count"}, "$")
            source = workshop_case(value["case_id"], value["period_count"])
            return JSONResponse({"valid": True, "source_input": source, "title": CASES[value["case_id"]], "capital_assumptions": assumptions(source["period_count"], source["case_id"]), "companion_sources": {"ict": ict_case(), "guided": workshop_input(1300, 0)}, "writes_performed": False}, headers=headers)
        except (ValueError, TypeError) as exc:
            return JSONResponse(failed(exc if isinstance(exc, ContractError) else ContractError("$", str(exc))), status_code=422, headers=headers)

    async def action(request):
        try: value = await request_json(request)
        except ContractError as exc: return JSONResponse(failed(exc), status_code=422, headers=headers)
        if not gate.acquire(blocking=False): return JSONResponse(failed(ContractError("$", "Eine Seminarprüfung läuft bereits")), status_code=409, headers=headers)
        def run():
            try:
                if request.url.path.endswith("/import-bundle"): return unpack(value)
                if request.url.path.endswith("/bundle.json"):
                    exact(value, {"sources", "title"}, "$")
                    bundle = pack(value["sources"], value["title"])
                    expected = '"' + bundle["expected_content_digests"]["modern"] + '"'
                    if request.headers.get("if-match") != expected: return (412, failed(ContractError("$", "Bündel benötigt denselben unveränderten Strategienachweis")))
                    return {"valid": True, "content_digest": bundle["bundle_digest"], "bundle": bundle}
                return calculate(value)
            except ContractError as exc: return failed(exc)
            finally: gate.release()
        result = await run_in_threadpool(run)
        if isinstance(result, tuple): return JSONResponse(result[1], status_code=result[0], headers=headers)
        if not result["valid"]: return JSONResponse(result, status_code=422, headers=headers)
        etag = '"' + result["content_digest"] + '"'
        reply_headers = {**headers, "ETag": etag}
        if request.url.path.endswith("/bundle.json"):
            return Response(json.dumps(result["bundle"], ensure_ascii=False, allow_nan=False).encode("utf-8"), media_type="application/json", headers={**reply_headers, "Content-Disposition": 'attachment; filename="IMS-Seminar-' + result["content_digest"][:12] + '.json"'})
        extension = request.path_params.get("extension")
        if not extension: return JSONResponse(result, headers=reply_headers)
        if extension not in ("json", "csv", "xlsx"): return JSONResponse(failed(ContractError("$", "Unbekanntes Format")), status_code=404, headers=headers)
        if request.headers.get("if-match") != etag: return JSONResponse(failed(ContractError("$", "Export benötigt denselben unveränderten Strategienachweis")), status_code=412, headers=headers)
        content, media = await run_in_threadpool(exports, result, extension)
        return Response(content, media_type=media, headers={**reply_headers, "Content-Disposition": f'attachment; filename="IMS-Strategie-{result["content_digest"][:12]}.{extension}"'})

    return Starlette(routes=[Route("/contract", lambda request: JSONResponse(contract_payload(), headers=headers)), Route("/workshop-case", preset, methods=["POST"]),
        Route("/calculate", action, methods=["POST"]), Route("/export.{extension}", action, methods=["POST"]), Route("/bundle.json", action, methods=["POST"]), Route("/import-bundle", action, methods=["POST"]),
        Route("/bundles/{case_id}.json", curated), Mount("/handbook", StaticFiles(directory=resource_root() / "docs" / "handbook"))])
