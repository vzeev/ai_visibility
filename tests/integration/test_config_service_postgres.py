from __future__ import annotations

import os
import unittest
from collections.abc import Iterator
from typing import Any, cast
from uuid import uuid4

from alembic.config import Config
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from apps.config_service.app.db.session import get_session
from apps.config_service.app.main import create_app
from apps.shared.runtime.env import bootstrap_repo_env
from tests.integration.db_helpers import db_reset_allowed, reset_postgres_schema

bootstrap_repo_env()
TEST_DATABASE_URL = os.environ.get("AI_VISIBILITY_TEST_DATABASE_URL")
RESET_ALLOWED = db_reset_allowed()


@unittest.skipUnless(
    TEST_DATABASE_URL and RESET_ALLOWED,
    "set AI_VISIBILITY_TEST_DATABASE_URL and AI_VISIBILITY_ALLOW_DB_RESET=true "
    "to run Postgres integration tests",
)
class ConfigServicePostgresIntegrationTests(unittest.TestCase):
    def test_alembic_backed_config_service_persists_brand(self) -> None:
        assert TEST_DATABASE_URL is not None
        original_database_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = TEST_DATABASE_URL
        try:
            reset_postgres_schema(TEST_DATABASE_URL)
            alembic_config = Config("alembic/alembic.ini")
            command.upgrade(alembic_config, "head")
            engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
            try:
                client: Any = _client_for_engine(engine)
                brand_name = f"Integration Brand {uuid4()}"
                response = cast(
                    Response,
                    client.post("/api/v1/brands", json={"name": brand_name}),
                )
                self.assertEqual(201, response.status_code)

                list_response = cast(Response, client.get("/api/v1/brands"))
                self.assertEqual(200, list_response.status_code)
                items = cast(list[dict[str, Any]], list_response.json())
                names = {item["name"] for item in items}
                self.assertIn(brand_name, names)
                client.close()
            finally:
                engine.dispose()
        finally:
            if original_database_url is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = original_database_url


def _client_for_engine(engine: Engine) -> TestClient:
    session_factory: sessionmaker[Session] = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    app = create_app()

    def override_session() -> Iterator[Session]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app)
