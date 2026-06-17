from __future__ import annotations

import os


def get_database_url() -> str:
    port = os.environ.get("POSTGRES_PORT", "55433")
    return os.environ.get(
        "DATABASE_URL",
        f"postgresql+psycopg://ai_visibility:ai_visibility_local@localhost:{port}/ai_visibility",
    )
