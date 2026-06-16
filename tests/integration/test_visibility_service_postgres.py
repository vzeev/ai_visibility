from __future__ import annotations

import os
import unittest
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

from alembic.config import Config
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from apps.visibility_service.app.db import models
from apps.visibility_service.app.db.session import get_session
from apps.visibility_service.app.main import create_app

TEST_DATABASE_URL = os.environ.get("AI_VISIBILITY_TEST_DATABASE_URL")


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "set AI_VISIBILITY_TEST_DATABASE_URL to run Postgres integration tests",
)
class VisibilityServicePostgresIntegrationTests(unittest.TestCase):
    def test_alembic_backed_visibility_run_creation(self) -> None:
        assert TEST_DATABASE_URL is not None
        original_database_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = TEST_DATABASE_URL
        try:
            alembic_config = Config("alembic/alembic.ini")
            command.upgrade(alembic_config, "head")
            engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
            try:
                session_factory: sessionmaker[Session] = sessionmaker(
                    bind=engine,
                    autoflush=False,
                    expire_on_commit=False,
                )
                config_ids = _seed_config(session_factory)
                client: Any = _client_for_engine(engine)
                response = cast(
                    Response,
                    client.post(
                        "/api/v1/runs",
                        json={
                            "brand_id": str(config_ids["brand_id"]),
                            "prompt_set_id": str(config_ids["prompt_set_id"]),
                            "sample_count": 1,
                            "max_attempts": 3,
                        },
                    ),
                )
                self.assertEqual(202, response.status_code)
                payload = cast(dict[str, Any], response.json())
                self.assertEqual(1, payload["item_count"])
                client.close()
            finally:
                engine.dispose()
        finally:
            if original_database_url is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = original_database_url


def _seed_config(session_factory: sessionmaker[Session]) -> dict[str, Any]:
    now = datetime.now(UTC)
    ids = {
        "brand_id": uuid4(),
        "prompt_set_id": uuid4(),
        "prompt_id": uuid4(),
        "prompt_version_id": uuid4(),
        "provider_id": uuid4(),
        "model_registry_id": uuid4(),
    }
    with session_factory() as session:
        session.add(
            models.ConfigBrand(
                id=ids["brand_id"],
                name=f"Integration Brand {uuid4()}",
                website_url="https://www.brandlight.ai/",
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            models.ConfigProvider(
                id=ids["provider_id"],
                provider_key=f"openai-{uuid4()}",
                display_name="OpenAI",
                provider_kind="llm",
                is_active=True,
                created_at=now,
            )
        )
        session.flush()
        session.add(
            models.ConfigPromptSet(
                id=ids["prompt_set_id"],
                brand_id=ids["brand_id"],
                name=f"Integration Prompt Set {uuid4()}",
                description="integration",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            models.ConfigModelRegistry(
                id=ids["model_registry_id"],
                provider_id=ids["provider_id"],
                model_id=f"gpt-test-{uuid4()}",
                display_name="GPT Test",
                owned_by="openai",
                is_available=True,
                enabled_for_visibility=True,
                rate_limit_policy_id=None,
                capability_json={"responses": True},
                discovered_at=now,
                updated_at=now,
            )
        )
        session.flush()
        session.add(
            models.ConfigPrompt(
                id=ids["prompt_id"],
                prompt_set_id=ids["prompt_set_id"],
                name=f"Integration Prompt {uuid4()}",
                intent="commercial",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )
        session.flush()
        session.add(
            models.ConfigPromptVersion(
                id=ids["prompt_version_id"],
                prompt_id=ids["prompt_id"],
                version=1,
                prompt_text="Which AI visibility platforms should I evaluate?",
                is_active=True,
                created_at=now,
            )
        )
        session.commit()
    return ids


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
