from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

try:
    from fastapi import FastAPI
except ModuleNotFoundError:  # pragma: no cover - exercised implicitly when FastAPI is absent.
    FastAPI = None  # type: ignore[assignment]

APP_NAME = "IMS Workbench"
APP_VERSION = "0.1.0"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _frontend_dist_dir() -> Path:
    configured = os.environ.get("IMS_FRONTEND_DIST")
    if configured:
        return Path(configured).expanduser().resolve()
    return _repo_root() / "frontend" / "dist"


def _version_payload() -> dict[str, str]:
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "api": "ims.api",
    }


def create_app(frontend_dist: Path | None = None) -> Any:
    dist_dir = frontend_dist or _frontend_dist_dir()

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

        if (dist_dir / "assets").is_dir():
            app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

        @app.get("/")
        def index() -> FileResponse | JSONResponse:
            return index_response()

        return app

    routes: list[Any] = [
        Route("/api/health", lambda request: JSONResponse(health_payload())),
        Route("/api/version", lambda request: JSONResponse(_version_payload())),
        Route("/", lambda request: index_response()),
    ]
    if (dist_dir / "assets").is_dir():
        routes.append(Mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets"))
    return Starlette(routes=routes)


app = create_app()
