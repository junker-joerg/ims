from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Protocol

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from ims.api.metadata_import import MetadataImportError
from ims.api.metadata import METADATA_SCHEMA_VERSION, metadata_capabilities
from ims.api.metadata_consistency import metadata_consistency_payload
from ims.api.metadata_repository import LazyWorkbenchMetadataRepository
from ims.api.core_validation_carryover_probe_contract import (
    core_validation_carryover_probe_api_contract_payload,
)
from ims.api.run_control_dry_run import dry_run_run_control_request, dry_run_run_control_request_payload
from ims.api.run_control_dry_run_contract import run_control_dry_run_contract_payload
from ims.api.run_control_execution_result_store import get_run_control_execution_result
from ims.api.run_control_execution_release import (
    build_default_execution_release_profiles,
    check_run_control_execution_release,
    parse_run_control_execution_release_payload,
)
from ims.api.run_control_preflight import preflight_run_control_from_repository
from ims.api.run_control_adapter_result_api_contract import run_control_adapter_result_api_contract_payload
from ims.api.run_control_adapter_start_contract import run_control_adapter_start_contract_payload
from ims.api.run_control_core_diagnostics_bridge import build_run_control_core_diagnostics_bridge
from ims.api.run_control_queue import (
    enqueue_run_control_request_object,
    get_run_control_queue_entry,
)
from ims.api.run_control_queue_action_plan import build_run_control_queue_action_plan
from ims.api.run_control_queue_overview import run_control_queue_detail_payload, run_control_queue_overview_payload
from ims.api.run_control_requests import run_control_request_contract_payload
from ims.engine.core_validation_overview import build_core_validation_overview

try:
    from fastapi import FastAPI
except ModuleNotFoundError:  # pragma: no cover - exercised implicitly when FastAPI is absent.
    FastAPI = None  # type: ignore[assignment]

APP_NAME = "IMS Workbench"
APP_VERSION = "0.1.0"


class MetadataRepositoryReader(Protocol):
    def list_scenarios(self) -> dict[str, object]:
        ...

    def get_scenario(self, scenario_id: str) -> dict[str, object] | None:
        ...

    def list_runs(self) -> dict[str, object]:
        ...

    def get_run(self, run_id: str) -> dict[str, object] | None:
        ...

    def metadata_source(self) -> dict[str, object]:
        ...


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _frontend_dist_dir() -> Path:
    configured = os.environ.get("IMS_FRONTEND_DIST")
    if configured:
        return Path(configured).expanduser().resolve()
    return _repo_root() / "frontend" / "dist"


def _metadata_db_path() -> Path | str:
    configured = os.environ.get("IMS_METADATA_DB")
    if configured:
        return Path(configured).expanduser().resolve()
    return ":memory:"


def _version_payload() -> dict[str, str]:
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "api": "ims.api",
    }


def _core_validation_overview_payload() -> dict[str, Any]:
    root = _repo_root()
    fixture_dir = root / "tests" / "fixtures"
    return build_core_validation_overview(
        legacy_fixture_path=fixture_dir / "legacy_validation_bundle.json",
        period_plan_paths=[
            fixture_dir / "replay_vu14_period_plan.json",
            fixture_dir / "replay_vusk1_period_plan.json",
        ],
    ).to_dict()


def _not_found_payload(resource: str, item_id: str) -> dict[str, object]:
    return {
        "error": {
            "code": "metadata_not_found",
            "resource": resource,
            "id": item_id,
            "message": f"{resource} metadata not found",
        }
    }


def _run_control_dry_run_error_payload(message: str) -> dict[str, object]:
    return {
        "status": "error",
        "mode": "run_control_dry_run",
        "message": message,
        "issues": [message],
        "writes_performed": False,
        "execution_performed": False,
    }


def _run_control_queue_error_payload(message: str, issues: list[str] | None = None) -> dict[str, object]:
    return {
        "status": "error",
        "mode": "run_control_queue_enqueue",
        "message": message,
        "issues": issues or [message],
        "writes_performed": False,
        "execution_performed": False,
    }


def _run_control_queue_action_plan_unavailable_payload(
    metadata_source: dict[str, object],
    message: str,
    *,
    status: str = "warning",
) -> dict[str, object]:
    return {
        "status": status,
        "mode": "run_control_queue_action_plan",
        "schema_version": METADATA_SCHEMA_VERSION,
        "metadata_source": dict(metadata_source),
        "queue_count": 0,
        "actions": [],
        "issues": [
            {
                "code": "run_control_queue_action_plan_unavailable",
                "severity": status,
                "message": message,
                "queue_ids": [],
            }
        ],
        "writes_performed": False,
        "execution_performed": False,
    }


def _run_control_execution_result_error_payload(
    metadata_source: dict[str, object],
    message: str,
) -> dict[str, object]:
    return {
        "status": "error",
        "mode": "run_control_execution_result_store_show",
        "schema_version": METADATA_SCHEMA_VERSION,
        "metadata_source": dict(metadata_source),
        "message": message,
        "issues": [message],
        "writes_performed": False,
        "execution_performed": False,
        "adapter_started": False,
        "simulation_performed": False,
    }


def _run_control_execution_release_error_payload(message: str) -> dict[str, object]:
    return {
        "status": "error",
        "mode": "run_control_execution_release_check",
        "message": message,
        "issues": [message],
        "release_ready": False,
        "adapter_start_allowed": False,
        "adapter_started": False,
        "result_persisted": False,
        "writes_performed": False,
        "execution_performed": False,
        "simulation_performed": False,
        "automatic_historical_rule_selection_performed": False,
        "historical_full_equality_claimed": False,
    }


def create_app(
    frontend_dist: Path | None = None,
    metadata_repository: MetadataRepositoryReader | None = None,
) -> Any:
    dist_dir = frontend_dist or _frontend_dist_dir()
    metadata_db_path = _metadata_db_path()
    repository = metadata_repository or LazyWorkbenchMetadataRepository(metadata_db_path)
    metadata_source = repository.metadata_source()
    if metadata_repository is not None:
        metadata_source = {**metadata_source, "injected": True}

    def health_payload() -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "ims-workbench-api",
            "version": APP_VERSION,
            "frontend_available": (dist_dir / "index.html").is_file(),
        }

    def index_response() -> FileResponse | JSONResponse:
        index_file = dist_dir / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)
        return JSONResponse(
            {
                "message": "IMS Workbench frontend has not been built yet.",
                "next_step": "Run npm.cmd install --prefix frontend and npm.cmd run build --prefix frontend.",
            },
            status_code=503,
        )

    def scenario_detail_response(scenario_id: str) -> JSONResponse:
        scenario = repository.get_scenario(scenario_id)
        if scenario is None:
            return JSONResponse(_not_found_payload("scenario", scenario_id), status_code=404)
        return JSONResponse(scenario)

    def run_detail_response(run_id: str) -> JSONResponse:
        run = repository.get_run(run_id)
        if run is None:
            return JSONResponse(_not_found_payload("run", run_id), status_code=404)
        return JSONResponse(run)

    def consistency_payload() -> dict[str, object]:
        return metadata_consistency_payload(
            repository.list_scenarios(),
            repository.list_runs(),
            metadata_capabilities(),
        )

    def queue_overview_payload() -> dict[str, object]:
        return run_control_queue_overview_payload(metadata_source)

    def queue_detail_response(queue_id: str) -> JSONResponse:
        detail = run_control_queue_detail_payload(metadata_source, queue_id)
        if detail is None:
            return JSONResponse(_not_found_payload("run_control_queue", queue_id), status_code=404)
        return JSONResponse(detail)

    def queue_action_plan_payload(queue_id: str | None = None) -> dict[str, object]:
        if metadata_source.get("storage_kind") != "sqlite" or not metadata_source.get("path"):
            return _run_control_queue_action_plan_unavailable_payload(
                metadata_source,
                "run control queue action plan requires an explicit SQLite metadata source",
            )
        try:
            return build_run_control_queue_action_plan(
                Path(str(metadata_source["path"])),
                queue_id=queue_id,
            ).to_dict()
        except MetadataImportError as exc:
            return _run_control_queue_action_plan_unavailable_payload(
                metadata_source,
                str(exc),
                status="error",
            )

    def queue_action_plan_response(request: Request) -> JSONResponse:
        queue_id = request.query_params.get("queue_id")
        return JSONResponse(queue_action_plan_payload(queue_id if queue_id else None))

    def run_control_core_diagnostics_bridge_payload(queue_id: str | None = None) -> dict[str, object]:
        return build_run_control_core_diagnostics_bridge(
            queue_action_plan_payload(queue_id),
            _core_validation_overview_payload(),
        ).to_dict()

    def run_control_core_diagnostics_bridge_response(request: Request) -> JSONResponse:
        queue_id = request.query_params.get("queue_id")
        return JSONResponse(run_control_core_diagnostics_bridge_payload(queue_id if queue_id else None))

    def execution_result_response(queue_id: str) -> JSONResponse:
        if metadata_source.get("storage_kind") != "sqlite" or not metadata_source.get("path"):
            return JSONResponse(
                _run_control_execution_result_error_payload(
                    metadata_source,
                    "run control execution result requires an explicit SQLite metadata source",
                ),
                status_code=404,
            )
        try:
            result = get_run_control_execution_result(
                queue_id,
                db_path=Path(str(metadata_source["path"])),
            ).to_dict()
        except MetadataImportError as exc:
            message = str(exc)
            if "no such table: run_control_execution_results" in message:
                message = f"run control execution result not found: {queue_id}"
            return JSONResponse(
                _run_control_execution_result_error_payload(metadata_source, message),
                status_code=404,
            )
        return JSONResponse(result)

    def preflight_payload(run_id: str) -> dict[str, object]:
        return preflight_run_control_from_repository(run_id, repository).to_dict()

    async def dry_run_response(request: Request) -> JSONResponse:
        try:
            payload = await request.json()
        except ValueError:
            return JSONResponse(
                _run_control_dry_run_error_payload("run control dry-run JSON is invalid"),
                status_code=400,
            )
        try:
            return JSONResponse(dry_run_run_control_request_payload(payload, repository))
        except MetadataImportError as exc:
            return JSONResponse(_run_control_dry_run_error_payload(str(exc)), status_code=400)

    async def queue_enqueue_response(request: Request) -> JSONResponse:
        if metadata_source.get("storage_kind") != "sqlite" or not metadata_source.get("path"):
            return JSONResponse(
                _run_control_queue_error_payload(
                    "run control queue enqueue requires an explicit SQLite metadata source"
                ),
                status_code=400,
            )
        try:
            payload = await request.json()
        except ValueError:
            return JSONResponse(
                _run_control_queue_error_payload("run control queue enqueue JSON is invalid"),
                status_code=400,
            )
        try:
            dry_run = dry_run_run_control_request(payload, repository)
            if dry_run.issues:
                return JSONResponse(
                    _run_control_queue_error_payload(
                        "run control queue enqueue requires a passing dry-run",
                        list(dry_run.issues),
                    ),
                    status_code=400,
                )
            result = enqueue_run_control_request_object(
                dry_run.request,
                db_path=Path(str(metadata_source["path"])),
            ).to_dict()
        except MetadataImportError as exc:
            return JSONResponse(_run_control_queue_error_payload(str(exc)), status_code=400)
        result["dry_run"] = dry_run.to_dict()
        result["execution_enabled"] = False
        return JSONResponse(result, status_code=201)

    async def execution_release_check_response(request: Request) -> JSONResponse:
        if metadata_source.get("storage_kind") != "sqlite" or not metadata_source.get("path"):
            return JSONResponse(
                _run_control_execution_release_error_payload(
                    "run control execution release check requires an explicit SQLite metadata source"
                ),
                status_code=400,
            )
        try:
            payload = await request.json()
        except ValueError:
            return JSONResponse(
                _run_control_execution_release_error_payload(
                    "run control execution release JSON is invalid"
                ),
                status_code=400,
            )
        try:
            release_request = parse_run_control_execution_release_payload(payload)
            db_path = Path(str(metadata_source["path"]))
            try:
                queue_entry = get_run_control_queue_entry(
                    release_request.queue_id,
                    db_path=db_path,
                ).entry
            except MetadataImportError:
                queue_entry = None
            preflight = preflight_run_control_from_repository(release_request.run_id, repository)
            result = check_run_control_execution_release(
                release_request,
                queue_entry=queue_entry,
                preflight=preflight,
                profiles=build_default_execution_release_profiles(_repo_root()),
                trusted_fixture_root=_repo_root() / "tests" / "fixtures",
            )
        except MetadataImportError as exc:
            return JSONResponse(
                _run_control_execution_release_error_payload(str(exc)),
                status_code=400,
            )
        return JSONResponse(result.to_dict(), status_code=200 if result.release_ready else 409)

    if FastAPI is not None:
        app = FastAPI(
            title=APP_NAME,
            version=APP_VERSION,
            description="Lokale Backend-Shell fuer die IMS Workbench.",
        )

        @app.get("/api/health")
        def health() -> dict[str, Any]:
            return health_payload()

        @app.get("/api/version")
        def version() -> dict[str, str]:
            return _version_payload()

        @app.get("/api/scenarios")
        def scenarios() -> dict[str, object]:
            return repository.list_scenarios()

        @app.get("/api/scenarios/{scenario_id}", response_model=None)
        def scenario_detail(scenario_id: str) -> dict[str, object] | JSONResponse:
            scenario = repository.get_scenario(scenario_id)
            if scenario is None:
                return JSONResponse(_not_found_payload("scenario", scenario_id), status_code=404)
            return scenario

        @app.get("/api/runs")
        def runs() -> dict[str, object]:
            return repository.list_runs()

        @app.get("/api/runs/{run_id}", response_model=None)
        def run_detail(run_id: str) -> dict[str, object] | JSONResponse:
            run = repository.get_run(run_id)
            if run is None:
                return JSONResponse(_not_found_payload("run", run_id), status_code=404)
            return run

        @app.get("/api/metadata/capabilities")
        def capabilities() -> dict[str, object]:
            return metadata_capabilities()

        @app.get("/api/metadata/source")
        def source() -> dict[str, object]:
            return metadata_source

        @app.get("/api/metadata/consistency")
        def consistency() -> dict[str, object]:
            return consistency_payload()

        @app.get("/api/core-validation/overview")
        def core_validation_overview() -> dict[str, object]:
            return _core_validation_overview_payload()

        @app.get("/api/core-validation/carryover-probe-contract")
        def core_validation_carryover_probe_contract() -> dict[str, object]:
            return core_validation_carryover_probe_api_contract_payload()

        @app.get("/api/run-control/queue")
        def run_control_queue() -> dict[str, object]:
            return queue_overview_payload()

        @app.post("/api/run-control/queue", response_model=None)
        async def run_control_queue_enqueue(request: Request) -> JSONResponse:
            return await queue_enqueue_response(request)

        @app.get("/api/run-control/queue/action-plan")
        def run_control_queue_action_plan(queue_id: str | None = None) -> dict[str, object]:
            return queue_action_plan_payload(queue_id)

        @app.get("/api/run-control/core-diagnostics-bridge")
        def run_control_core_diagnostics_bridge(queue_id: str | None = None) -> dict[str, object]:
            return run_control_core_diagnostics_bridge_payload(queue_id)

        @app.get("/api/run-control/execution-result/{queue_id}", response_model=None)
        def run_control_execution_result(queue_id: str) -> dict[str, object] | JSONResponse:
            return execution_result_response(queue_id)

        @app.get("/api/run-control/request-contract")
        def run_control_request_contract() -> dict[str, object]:
            return run_control_request_contract_payload()

        @app.get("/api/run-control/dry-run-contract")
        def run_control_dry_run_contract() -> dict[str, object]:
            return run_control_dry_run_contract_payload()

        @app.get("/api/run-control/adapter-result-contract")
        def run_control_adapter_result_contract() -> dict[str, object]:
            return run_control_adapter_result_api_contract_payload()

        @app.get("/api/run-control/adapter-start-contract")
        def run_control_adapter_start_contract() -> dict[str, object]:
            return run_control_adapter_start_contract_payload()

        @app.post("/api/run-control/adapter-release-check", response_model=None)
        async def run_control_adapter_release_check(request: Request) -> JSONResponse:
            return await execution_release_check_response(request)

        @app.post("/api/run-control/dry-run", response_model=None)
        async def run_control_dry_run(request: Request) -> JSONResponse:
            return await dry_run_response(request)

        @app.get("/api/run-control/preflight/{run_id}")
        def run_control_preflight(run_id: str) -> dict[str, object]:
            return preflight_payload(run_id)

        @app.get("/api/run-control/queue/{queue_id}", response_model=None)
        def run_control_queue_detail(queue_id: str) -> dict[str, object] | JSONResponse:
            detail = run_control_queue_detail_payload(metadata_source, queue_id)
            if detail is None:
                return JSONResponse(_not_found_payload("run_control_queue", queue_id), status_code=404)
            return detail

        if (dist_dir / "assets").is_dir():
            app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

        @app.get("/")
        def index() -> FileResponse | JSONResponse:
            return index_response()

        return app

    routes: list[Any] = [
        Route("/api/health", lambda request: JSONResponse(health_payload())),
        Route("/api/version", lambda request: JSONResponse(_version_payload())),
        Route("/api/scenarios", lambda request: JSONResponse(repository.list_scenarios())),
        Route(
            "/api/scenarios/{scenario_id}",
            lambda request: scenario_detail_response(request.path_params["scenario_id"]),
        ),
        Route("/api/runs", lambda request: JSONResponse(repository.list_runs())),
        Route(
            "/api/runs/{run_id}",
            lambda request: run_detail_response(request.path_params["run_id"]),
        ),
        Route("/api/metadata/capabilities", lambda request: JSONResponse(metadata_capabilities())),
        Route("/api/metadata/source", lambda request: JSONResponse(metadata_source)),
        Route("/api/metadata/consistency", lambda request: JSONResponse(consistency_payload())),
        Route("/api/core-validation/overview", lambda request: JSONResponse(_core_validation_overview_payload())),
        Route(
            "/api/core-validation/carryover-probe-contract",
            lambda request: JSONResponse(core_validation_carryover_probe_api_contract_payload()),
        ),
        Route("/api/run-control/queue", lambda request: JSONResponse(queue_overview_payload())),
        Route("/api/run-control/queue", queue_enqueue_response, methods=["POST"]),
        Route("/api/run-control/queue/action-plan", queue_action_plan_response),
        Route("/api/run-control/core-diagnostics-bridge", run_control_core_diagnostics_bridge_response),
        Route(
            "/api/run-control/execution-result/{queue_id}",
            lambda request: execution_result_response(request.path_params["queue_id"]),
        ),
        Route("/api/run-control/request-contract", lambda request: JSONResponse(run_control_request_contract_payload())),
        Route("/api/run-control/dry-run-contract", lambda request: JSONResponse(run_control_dry_run_contract_payload())),
        Route(
            "/api/run-control/adapter-result-contract",
            lambda request: JSONResponse(run_control_adapter_result_api_contract_payload()),
        ),
        Route(
            "/api/run-control/adapter-start-contract",
            lambda request: JSONResponse(run_control_adapter_start_contract_payload()),
        ),
        Route(
            "/api/run-control/adapter-release-check",
            execution_release_check_response,
            methods=["POST"],
        ),
        Route("/api/run-control/dry-run", dry_run_response, methods=["POST"]),
        Route(
            "/api/run-control/preflight/{run_id}",
            lambda request: JSONResponse(preflight_payload(request.path_params["run_id"])),
        ),
        Route(
            "/api/run-control/queue/{queue_id}",
            lambda request: queue_detail_response(request.path_params["queue_id"]),
        ),
        Route("/", lambda request: index_response()),
    ]
    if (dist_dir / "assets").is_dir():
        routes.append(Mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets"))
    return Starlette(routes=routes)


app = create_app()
