from __future__ import annotations

import unittest
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.visibility_service.app.db import models
from apps.visibility_service.app.db.session import get_session
from apps.visibility_service.app.main import create_app


class VisibilityServiceApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = _create_sqlite_engine()
        models.Base.metadata.create_all(self.engine)
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )
        self.config_ids = _seed_config(self.session_factory)
        app = create_app()

        def override_session() -> Iterator[Session]:
            with self.session_factory() as session:
                yield session

        app.dependency_overrides[get_session] = override_session
        self.client: Any = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        self.engine.dispose()

    def test_run_creation_claim_completion_and_raw_idempotency(self) -> None:
        run = self._create_run(sample_count=2, max_attempts=3)
        self.assertEqual("queued", run["status"])
        self.assertEqual(2, run["item_count"])
        self.assertIsInstance(run["created_at"], str)

        queue = _dict_payload(self._get("/api/v1/queue"))
        self.assertEqual(2, queue["pending"])

        claimed = _dict_payload(self._post("/api/v1/queue/claim", json={"lease_seconds": 60}))
        self.assertEqual("running", claimed["status"])
        self.assertEqual(1, claimed["attempt_count"])

        completion_payload = {
            "provider_key": "openai",
            "model_id": "gpt-test",
            "output_text": "Brandlight is visible in AI search answers.",
            "raw_request_json": {"prompt": "Where is Brandlight visible?"},
            "raw_response_json": {
                "id": "response-1",
                "output_text": "Brandlight is visible in AI search answers.",
            },
            "usage_json": {"input_tokens": 10, "output_tokens": 12},
            "latency_ms": 50,
            "provider_response_id": "response-1",
        }
        first_raw = _dict_payload(
            self._post(
                f"/api/v1/queue/items/{claimed['id']}/complete",
                json=completion_payload,
            )
        )
        second_raw = _dict_payload(
            self._post(
                f"/api/v1/queue/items/{claimed['id']}/complete",
                json=completion_payload,
            )
        )
        self.assertEqual(first_raw["id"], second_raw["id"])

        page = _dict_payload(
            self._get("/api/v1/raw-responses", params={"q": "Brandlight", "limit": 10, "offset": 0})
        )
        self.assertEqual(1, page["total"])
        self.assertEqual("gpt-test", page["items"][0]["model_id"])
        self.assertIn("Brandlight", page["items"][0]["output_text"])

        direct_raw = _dict_payload(self._get(f"/api/v1/raw-responses/{first_raw['id']}"))
        self.assertEqual(first_raw["id"], direct_raw["id"])
        self.assertEqual("response-1", direct_raw["provider_response_id"])

        queue_after = _dict_payload(self._get("/api/v1/queue"))
        self.assertEqual(1, queue_after["succeeded"])
        self.assertEqual(1, queue_after["pending"])

    def test_retryable_failures_eventually_fail_after_max_attempts(self) -> None:
        self._create_run(sample_count=1, max_attempts=2)

        first_claim = _dict_payload(self._post("/api/v1/queue/claim", json={"lease_seconds": 60}))
        first_failure = _dict_payload(
            self._post(
                f"/api/v1/queue/items/{first_claim['id']}/fail",
                json={
                    "error_type": "rate_limit",
                    "error_message": "provider throttled",
                    "retryable": True,
                    "retry_delay_seconds": 0,
                },
            )
        )
        self.assertEqual("throttled", first_failure["status"])

        second_claim = _dict_payload(self._post("/api/v1/queue/claim", json={"lease_seconds": 60}))
        self.assertEqual(2, second_claim["attempt_count"])
        second_failure = _dict_payload(
            self._post(
                f"/api/v1/queue/items/{second_claim['id']}/fail",
                json={
                    "error_type": "rate_limit",
                    "error_message": "provider throttled again",
                    "retryable": True,
                    "retry_delay_seconds": 0,
                },
            )
        )
        self.assertEqual("failed", second_failure["status"])

        queue = _dict_payload(self._get("/api/v1/queue"))
        self.assertEqual(1, queue["failed"])

    def _create_run(self, *, sample_count: int, max_attempts: int) -> dict[str, Any]:
        response = self._post(
            "/api/v1/runs",
            json={
                "brand_id": str(self.config_ids["brand_id"]),
                "prompt_set_id": str(self.config_ids["prompt_set_id"]),
                "sample_count": sample_count,
                "max_attempts": max_attempts,
            },
        )
        self.assertEqual(202, response.status_code)
        return _dict_payload(response)

    def _post(self, url: str, *, json: dict[str, Any]) -> Response:
        return cast(Response, self.client.post(url, json=json))

    def _get(self, url: str, *, params: dict[str, Any] | None = None) -> Response:
        return cast(Response, self.client.get(url, params=params))


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
        session.add_all(
            [
                models.ConfigBrand(
                    id=ids["brand_id"],
                    name="Brandlight",
                    website_url="https://www.brandlight.ai/",
                    created_at=now,
                    updated_at=now,
                ),
                models.ConfigPromptSet(
                    id=ids["prompt_set_id"],
                    brand_id=ids["brand_id"],
                    name="Core prompts",
                    description="Core AI visibility questions",
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                ),
                models.ConfigPrompt(
                    id=ids["prompt_id"],
                    prompt_set_id=ids["prompt_set_id"],
                    name="Category visibility",
                    intent="commercial",
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                ),
                models.ConfigPromptVersion(
                    id=ids["prompt_version_id"],
                    prompt_id=ids["prompt_id"],
                    version=1,
                    prompt_text="Which AI visibility platforms should I evaluate?",
                    is_active=True,
                    created_at=now,
                ),
                models.ConfigProvider(
                    id=ids["provider_id"],
                    provider_key="openai",
                    display_name="OpenAI",
                    provider_kind="llm",
                    is_active=True,
                    created_at=now,
                ),
                models.ConfigModelRegistry(
                    id=ids["model_registry_id"],
                    provider_id=ids["provider_id"],
                    model_id="gpt-test",
                    display_name="GPT Test",
                    owned_by="openai",
                    is_available=True,
                    enabled_for_visibility=True,
                    rate_limit_policy_id=None,
                    capability_json={"responses": True},
                    discovered_at=now,
                    updated_at=now,
                ),
            ]
        )
        session.commit()
    return ids


def _create_sqlite_engine() -> Engine:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine, "connect", _attach_schemas)
    return engine


def _attach_schemas(dbapi_connection: Any, _connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("ATTACH DATABASE ':memory:' AS config")
    cursor.execute("ATTACH DATABASE ':memory:' AS visibility")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _dict_payload(response: Response) -> dict[str, Any]:
    return cast(dict[str, Any], response.json())
