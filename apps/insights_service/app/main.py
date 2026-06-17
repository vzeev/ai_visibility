from __future__ import annotations

from fastapi import FastAPI

from apps.insights_service.app.api.routes import router
from apps.shared.http.cors import add_cors_middleware
from apps.shared.runtime.env import bootstrap_repo_env

bootstrap_repo_env()

SERVICE_NAME = "insights-service"


def healthz() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "ok"}


def readyz() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "ok"}


def create_app() -> FastAPI:
    app = FastAPI(title="AI Visibility Insights Service", version="0.1.0")
    add_cors_middleware(app)
    app.add_api_route("/healthz", healthz, methods=["GET"])
    app.add_api_route("/readyz", readyz, methods=["GET"])
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
