from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Protocol

from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from ims.api.metadata import METADATA_SCHEMA_VERSION, metadata_capabilities
from ims.api.metadata_repository import LazyWorkbenchMetadataRepository

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


def _metadata_source_payload(metadata_db_path: Path | str) -> dict[str, object]:
    configured = metadata_db_path != ":memory:"
    payload: dict[str, object] = {
        "schema_version": METADATA_SCHEMA_VERSION,
        "storage_kind": "sqlite" if configured else "memory",
        "configured": configured,
        "writes_enabled": False,
        "execution_enabled": False,
    }
    if configured:
        payload["path"] = str(metadata_db_path)
    return payload


def _version_payload() -> dict[str, str]:
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "api": "ims.api",
    }


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
    metadata_source = _metadata_source_payload(metadata_db_path)

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
        Route("/", lambda request: index_response()),
    ]
    if (dist_dir / "assets").is_dir():
        routes.append(Mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets"))
    return Starlette(routes=routes)


app = create_app()
