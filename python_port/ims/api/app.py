from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Protocol

from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from ims.api.metadata import metadata_capabilities
from ims.api.metadata_consistency import metadata_consistency_payload
from ims.api.metadata_repository import LazyWorkbenchMetadataRepository
from ims.api.run_control_dry_run_contract import run_control_dry_run_contract_payload
from ims.api.run_control_preflight import preflight_run_control_from_repository
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

    def preflight_payload(run_id: str) -> dict[str, object]:
        return preflight_run_control_from_repository(run_id, repository).to_dict()

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

        @app.get("/api/run-control/queue")
        def run_control_queue() -> dict[str, object]:
            return queue_overview_payload()

        @app.get("/api/run-control/request-contract")
        def run_control_request_contract() -> dict[str, object]:
            return run_control_request_contract_payload()

        @app.get("/api/run-control/dry-run-contract")
        def run_control_dry_run_contract() -> dict[str, object]:
            return run_control_dry_run_contract_payload()

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
        Route("/api/run-control/queue", lambda request: JSONResponse(queue_overview_payload())),
        Route("/api/run-control/request-contract", lambda request: JSONResponse(run_control_request_contract_payload())),
        Route("/api/run-control/dry-run-contract", lambda request: JSONResponse(run_control_dry_run_contract_payload())),
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
