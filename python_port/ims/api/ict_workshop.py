"""Shared Starlette routes mounted in both existing backend variants."""

import json
from threading import BoundedSemaphore

from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from ims.ict.contract import ContractError, Issue, contract_payload, digest, failure, validate
from ims.ict.exports import csv_export, workbook_export
from ims.ict.presets import workshop_case
from ims.ict.simulation import calculate


def create_ict_app() -> Starlette:
    gate = BoundedSemaphore(1)

    async def parse(request: Request) -> object:
        chunks: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > 256_000:
                raise ContractError([Issue("$", "body_limit_exceeded", "ICT-Eingabe ist zu groß")])
            chunks.append(chunk)
        try:
            return json.loads(b"".join(chunks))
        except (ValueError, UnicodeDecodeError) as exc:
            raise ContractError([Issue("$", "json_invalid", "Gültiges JSON erforderlich")]) from exc

    async def validation(request: Request) -> JSONResponse:
        try:
            value = validate(await parse(request))
        except ContractError as exc:
            return JSONResponse(failure(exc.issues), status_code=422, headers={"Cache-Control": "no-store"})
        return JSONResponse({"valid": True, "input_digest": digest(value), "issues": [], "writes_performed": False,
                             "ict_model_calculated": False}, headers={"Cache-Control": "no-store"})

    async def calculation(request: Request) -> Response:
        try:
            value = await parse(request)
        except ContractError as exc:
            return JSONResponse(failure(exc.issues), status_code=400, headers={"Cache-Control": "no-store"})
        if not gate.acquire(blocking=False):
            return JSONResponse(failure([Issue("$", "calculation_busy", "Eine ICT-Rechnung läuft bereits")]), status_code=409, headers={"Cache-Control": "no-store"})

        def run() -> dict:
            try:
                return calculate(value)
            finally:
                gate.release()

        result = await run_in_threadpool(run)
        if not result["valid"]:
            return JSONResponse(result, status_code=422, headers={"Cache-Control": "no-store"})
        etag = '"' + result["content_digest"] + '"'
        headers = {"ETag": etag, "Cache-Control": "no-store"}
        extension = request.path_params.get("extension")
        if not extension:
            return JSONResponse(result, headers=headers)
        if request.headers.get("if-match") != etag:
            return JSONResponse(failure([Issue("$", "digest_mismatch", "Export benötigt den unveränderten Ergebnisnachweis")]), status_code=412, headers={"Cache-Control": "no-store"})
        if extension not in ("json", "csv", "xlsx"):
            return Response(status_code=404)
        headers["Content-Disposition"] = f'attachment; filename="IMS-ICT-{result["content_digest"][:12]}.{extension}"'
        if extension == "json":
            return Response(json.dumps(result, sort_keys=True, ensure_ascii=False).encode(), media_type="application/json", headers=headers)
        if extension == "csv":
            return Response(csv_export(result), media_type="text/csv; charset=utf-8", headers=headers)
        return Response(workbook_export(result), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)

    return Starlette(routes=[
        Route("/contract", lambda request: JSONResponse(contract_payload())),
        Route("/workshop-case", lambda request: JSONResponse(workshop_case())),
        Route("/validate", validation, methods=["POST"]),
        Route("/calculate", calculation, methods=["POST"]),
        Route("/export.{extension}", calculation, methods=["POST"]),
    ])
