from __future__ import annotations

from sqlalchemy import create_engine, text


def reset_postgres_schema(database_url: str) -> None:
    engine = create_engine(database_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.execute(text("DROP SCHEMA IF EXISTS insights CASCADE"))
            connection.execute(text("DROP SCHEMA IF EXISTS visibility CASCADE"))
            connection.execute(text("DROP SCHEMA IF EXISTS config CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    finally:
        engine.dispose()
