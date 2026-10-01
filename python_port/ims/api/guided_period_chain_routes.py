"""Shared API for the guided assembler; execution remains in run-control."""

import json
from pathlib import Path
from threading import BoundedSemaphore

from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ims.api.guided_period_chain import GuidedChainError, build, failed, store, workshop_input


def create_guided_chain_app(db_path: Path | str | None) -> Starlette:
    gate = BoundedSemaphore(1)
    headers = {"Cache-Control": "no-store"}

    async def parse(request: Request) -> object:
        chunks, size = [], 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > 16 * 1024 * 1024:
                raise GuidedChainError("payload_limit_exceeded", "Quellenvertrag überschreitet 16 MiB")
            chunks.append(chunk)
        try:
            return json.loads(b"".join(chunks))
        except (ValueError, UnicodeDecodeError) as exc:
            raise GuidedChainError("json_invalid", "Gültiges JSON erforderlich") from exc

    async def action(request: Request) -> JSONResponse:
        if not gate.acquire(blocking=False):
            return JSONResponse(failed(GuidedChainError("assembly_busy", "Eine Kettenprüfung läuft bereits")), status_code=409, headers=headers)
        try:
            value = await parse(request)
        except GuidedChainError as exc:
            gate.release()
            return JSONResponse(failed(exc), status_code=422, headers=headers)
        except BaseException:
            gate.release()
            raise

        def run() -> dict:
            try:
                kind = request.path_params["action"]
                if kind == "workshop-case":
                    if not isinstance(value, dict) or set(value) != {"seed", "run_index"}:
                        raise GuidedChainError("preset_request_invalid", "Seed und Laufindex ausdrücklich angeben")
                    return {"valid": True, "source_input": workshop_input(value["seed"], value["run_index"]), "writes_performed": False, "runner_invocation_performed": False}
                if kind == "build":
                    return build(value).result
                if kind == "store":
                    if db_path is None:
                        raise GuidedChainError("storage_not_configured", "Lokale SQLite-Ablage ist nicht konfiguriert")
                    return store(value, db_path=db_path)
                raise GuidedChainError("action_unknown", "Unbekannte Assistentenaktion")
            except GuidedChainError as exc:
                return failed(exc)
            finally:
                gate.release()

        result = await run_in_threadpool(run)
        response_headers = dict(headers)
        if result.get("content_digest"):
            response_headers["ETag"] = '"' + result["content_digest"] + '"'
        return JSONResponse(result, status_code=200 if result["valid"] else 422, headers=response_headers)

    return Starlette(routes=[Route("/{action}", action, methods=["POST"])])
