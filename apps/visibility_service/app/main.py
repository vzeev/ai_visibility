from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from apps.shared.http.cors import add_cors_middleware
from apps.shared.runtime.env import bootstrap_repo_env
from apps.visibility_service.app.api.routes import router
from apps.visibility_service.app.db.repository import ConflictError, NotFoundError

bootstrap_repo_env()

SERVICE_NAME = "visibility-service"


def healthz() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "ok"}


def readyz() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "ok"}


def create_app() -> FastAPI:
    app = FastAPI(title="AI Visibility Service", version="0.1.0")
    add_cors_middleware(app)
    app.add_api_route("/healthz", healthz, methods=["GET"])
    app.add_api_route("/readyz", readyz, methods=["GET"])
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(ConflictError, conflict_handler)
    app.include_router(router, prefix="/api/v1")
    return app


def not_found_handler(_request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


def conflict_handler(_request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


app = create_app()
