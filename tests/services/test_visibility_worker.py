from __future__ import annotations

import asyncio
import unittest
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.shared.ai.provider import AIProviderError, AIRequest, AIResponse, FakeAIProviderAdapter
from apps.shared.ai.rate_limits import RateLimitDecision, RateLimitPolicy
from apps.visibility_service.app.db import models
from apps.visibility_service.app.db.repository import VisibilityRepository
from apps.worker.app.visibility_worker import VisibilityWorker


class VisibilityWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = _create_sqlite_engine()
        models.Base.metadata.create_all(self.engine)
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )
        self.config_ids = _seed_config(self.session_factory)

    def tearDown(self) -> None:
        self.engine.dispose()

    def test_process_one_persists_fake_raw_response(self) -> None:
        self._create_run(sample_count=1, max_attempts=3)
        worker = VisibilityWorker(
            self.session_factory,
            adapters={"openai": FakeAIProviderAdapter({"gpt-test": "Brandlight is visible."})},
        )

        result = asyncio.run(worker.process_one())

        self.assertEqual("processed", result.status)
        self.assertIsNotNone(result.raw_response_id)
        with self.session_factory() as session:
            raw_responses = list(session.scalars(select(models.RawResponse)))
            queue = VisibilityRepository(session).queue_state()
        self.assertEqual(1, len(raw_responses))
        self.assertEqual("Brandlight is visible.", raw_responses[0].output_text)
        self.assertEqual("openai", raw_responses[0].raw_request_json["provider"])
        self.assertEqual(1, queue["succeeded"])

    def test_process_batch_respects_max_items(self) -> None:
        self._create_run(sample_count=3, max_attempts=3)
        worker = VisibilityWorker(self.session_factory)

        results = asyncio.run(worker.process_batch(max_items=2))

        self.assertEqual(["processed", "processed"], [result.status for result in results])
        with self.session_factory() as session:
            queue = VisibilityRepository(session).queue_state()
        self.assertEqual(2, queue["succeeded"])
        self.assertEqual(1, queue["pending"])

    def test_retryable_provider_error_is_recorded_for_retry(self) -> None:
        self._create_run(sample_count=1, max_attempts=2)
        worker = VisibilityWorker(
            self.session_factory,
            adapters={"openai": RetryableFailingAdapter()},
            retry_delay_seconds=0,
        )

        result = asyncio.run(worker.process_one())

        self.assertEqual("failed", result.status)
        self.assertEqual("rate limited", result.error_message)
        with self.session_factory() as session:
            errors = list(session.scalars(select(models.ModelError)))
            raw_responses = list(session.scalars(select(models.RawResponse)))
            queue = VisibilityRepository(session).queue_state()
        self.assertEqual(1, len(errors))
        self.assertTrue(errors[0].retryable)
        self.assertEqual("provider_error", errors[0].error_type)
        self.assertEqual(0, len(raw_responses))
        self.assertEqual(1, queue["pending"])

    def test_rate_limit_gate_throttles_from_configured_policy(self) -> None:
        self._attach_rate_limit(min_delay_ms=5_000)
        self._create_run(sample_count=1, max_attempts=2)
        gate = DenyRateLimitGate()
        worker = VisibilityWorker(self.session_factory, rate_limit_gate=gate)

        result = asyncio.run(worker.process_one())

        self.assertEqual("failed", result.status)
        self.assertEqual(
            "provider/model rate limit is not currently eligible", result.error_message
        )
        self.assertIsNotNone(gate.checked_policy)
        assert gate.checked_policy is not None
        self.assertEqual(5_000, gate.checked_policy.min_delay_ms)
        self.assertFalse(gate.recorded_execution)
        with self.session_factory() as session:
            errors = list(session.scalars(select(models.ModelError)))
            raw_responses = list(session.scalars(select(models.RawResponse)))
            queue = VisibilityRepository(session).queue_state()
        self.assertEqual(1, len(errors))
        self.assertEqual("rate_limit", errors[0].error_type)
        self.assertEqual(0, len(raw_responses))
        self.assertEqual(1, queue["throttled"])

    def _create_run(self, *, sample_count: int, max_attempts: int) -> None:
        with self.session_factory() as session:
            VisibilityRepository(session).create_run(
                brand_id=self.config_ids["brand_id"],
                prompt_set_id=self.config_ids["prompt_set_id"],
                sample_count=sample_count,
                max_attempts=max_attempts,
            )

    def _attach_rate_limit(self, *, min_delay_ms: int) -> None:
        policy_id = uuid4()
        now = datetime.now(UTC)
        with self.session_factory() as session:
            session.add(
                models.ConfigRateLimitPolicy(
                    id=policy_id,
                    provider_id=self.config_ids["provider_id"],
                    model_id="gpt-test",
                    max_concurrent_requests=1,
                    requests_per_minute=20,
                    tokens_per_minute=None,
                    min_delay_ms=min_delay_ms,
                    max_retries=2,
                    backoff_base_ms=100,
                    backoff_max_ms=1_000,
                    created_at=now,
                    updated_at=now,
                )
            )
            model = session.get(models.ConfigModelRegistry, self.config_ids["model_registry_id"])
            assert model is not None
            model.rate_limit_policy_id = policy_id
            session.commit()


class RetryableFailingAdapter:
    provider_key = "openai"

    async def complete(self, request: AIRequest) -> AIResponse:
        raise AIProviderError(
            provider_key=request.provider_key,
            model_id=request.model_id,
            message="rate limited",
            retryable=True,
        )


class DenyRateLimitGate:
    def __init__(self) -> None:
        self.checked_policy: RateLimitPolicy | None = None
        self.recorded_execution = False

    def check(
        self,
        *,
        provider_key: str,
        model_id: str,
        policy: RateLimitPolicy,
    ) -> RateLimitDecision:
        self.checked_policy = policy
        return RateLimitDecision(allowed=False, retry_after_seconds=7)

    def record_execution(
        self,
        *,
        provider_key: str,
        model_id: str,
        policy: RateLimitPolicy,
    ) -> None:
        self.recorded_execution = True


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
