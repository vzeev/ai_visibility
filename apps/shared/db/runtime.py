from __future__ import annotations

import os


def get_database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://ai_visibility:ai_visibility_local@localhost:5432/ai_visibility",
    )
