from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_CORS_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")
CORS_ORIGINS_ENV = "AI_VISIBILITY_CORS_ORIGINS"


def configured_cors_origins() -> list[str]:
    raw_origins = os.environ.get(CORS_ORIGINS_ENV)
    if raw_origins is None:
        return list(DEFAULT_CORS_ORIGINS)
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def add_cors_middleware(app: FastAPI) -> None:
    origins = configured_cors_origins()
    if not origins:
        return
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
