from __future__ import annotations

import os
from urllib.parse import urlsplit

from sqlalchemy import create_engine, text

ALLOW_DB_RESET_ENV = "AI_VISIBILITY_ALLOW_DB_RESET"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def db_reset_allowed() -> bool:
    return os.environ.get(ALLOW_DB_RESET_ENV, "").lower() in {"1", "true", "yes"}


def assert_safe_reset_database_url(database_url: str) -> None:
    parsed = urlsplit(database_url)
    hostname = parsed.hostname or ""
    database_name = parsed.path.removeprefix("/")
    if not db_reset_allowed():
        raise RuntimeError(f"set {ALLOW_DB_RESET_ENV}=true before resetting test schemas")
    if not parsed.scheme.startswith("postgresql"):
        raise RuntimeError("database reset is only allowed for PostgreSQL URLs")
    if hostname not in LOCAL_HOSTS:
        raise RuntimeError("database reset is only allowed for local PostgreSQL hosts")
    if "test" not in database_name.lower():
        raise RuntimeError("database reset is only allowed for databases named as test databases")


def reset_postgres_schema(database_url: str) -> None:
    assert_safe_reset_database_url(database_url)
    engine = create_engine(database_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.execute(text("DROP SCHEMA IF EXISTS insights CASCADE"))
            connection.execute(text("DROP SCHEMA IF EXISTS visibility CASCADE"))
            connection.execute(text("DROP SCHEMA IF EXISTS config CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    finally:
        engine.dispose()
