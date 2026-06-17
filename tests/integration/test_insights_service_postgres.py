from __future__ import annotations

import os
import unittest
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from apps.config_service.app.db import models as config_models
from apps.insights_service.app.db import models as insights_models
from apps.insights_service.app.db.repository import InsightsRepository
from apps.shared.runtime.env import bootstrap_repo_env
from apps.visibility_service.app.db import models as visibility_models
from tests.integration.db_helpers import db_reset_allowed, reset_postgres_schema

bootstrap_repo_env()
TEST_DATABASE_URL = os.environ.get("AI_VISIBILITY_TEST_DATABASE_URL")
RESET_ALLOWED = db_reset_allowed()


@unittest.skipUnless(
    TEST_DATABASE_URL and RESET_ALLOWED,
    "set AI_VISIBILITY_TEST_DATABASE_URL and AI_VISIBILITY_ALLOW_DB_RESET=true "
    "to run Postgres integration tests",
)
class InsightsServicePostgresIntegrationTests(unittest.TestCase):
    def test_extracts_summary_with_alembic_schema(self) -> None:
        assert TEST_DATABASE_URL is not None
        original_database_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = TEST_DATABASE_URL
        try:
            reset_postgres_schema(TEST_DATABASE_URL)
            alembic_config = Config("alembic/alembic.ini")
            command.upgrade(alembic_config, "head")
            engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
            try:
                session_factory: sessionmaker[Session] = sessionmaker(
                    bind=engine,
                    autoflush=False,
                    expire_on_commit=False,
                )
                ids = _seed_visibility_data(session_factory)

                with session_factory() as session:
                    result = InsightsRepository(session).extract_run_batch(
                        run_batch_id=ids["run_batch_id"],
                        extraction_version="deterministic-v1",
                    )

                    self.assertEqual(1, result.raw_response_count)
                    self.assertEqual(1, result.summary.summary_json["brand_mentions"])
                    self.assertEqual(1, result.summary.summary_json["competitor_mentions"])
                    self.assertEqual(1, result.summary.summary_json["citation_count"])
                    self.assertEqual(
                        [str(ids["raw_response_id"])],
                        result.summary.summary_json["raw_response_ids"],
                    )
                    mention_count = session.scalar(
                        select(func.count()).select_from(insights_models.ExtractedMention)
                    )
                    self.assertEqual(2, mention_count)
            finally:
                engine.dispose()
        finally:
            if original_database_url is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = original_database_url


def _seed_visibility_data(session_factory: sessionmaker[Session]) -> dict[str, Any]:
    now = datetime.now(UTC)
    ids = {
        "brand_id": uuid4(),
        "alias_id": uuid4(),
        "competitor_id": uuid4(),
        "prompt_set_id": uuid4(),
        "prompt_id": uuid4(),
        "prompt_version_id": uuid4(),
        "provider_id": uuid4(),
        "model_registry_id": uuid4(),
        "run_batch_id": uuid4(),
        "run_item_id": uuid4(),
        "raw_response_id": uuid4(),
    }
    with session_factory() as session:
        session.add_all(
            [
                config_models.Brand(
                    id=ids["brand_id"],
                    name=f"Brandlight Integration {uuid4()}",
                    website_url="https://www.brandlight.ai/",
                ),
                config_models.BrandAlias(
                    id=ids["alias_id"],
                    brand_id=ids["brand_id"],
                    alias="Brandlight",
                ),
                config_models.Competitor(
                    id=ids["competitor_id"],
                    brand_id=ids["brand_id"],
                    name=f"AcmeRank {uuid4()}",
                    website_url="https://example.com/",
                ),
                visibility_models.ConfigPromptSet(
                    id=ids["prompt_set_id"],
                    brand_id=ids["brand_id"],
                    name=f"Insights Integration Prompt Set {uuid4()}",
                    description="integration",
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                ),
                visibility_models.ConfigProvider(
                    id=ids["provider_id"],
                    provider_key=f"openai-{uuid4()}",
                    display_name="OpenAI",
                    provider_kind="llm",
                    is_active=True,
                    created_at=now,
                ),
            ]
        )
        session.flush()
        session.add_all(
            [
                visibility_models.ConfigPrompt(
                    id=ids["prompt_id"],
                    prompt_set_id=ids["prompt_set_id"],
                    name=f"Insights Integration Prompt {uuid4()}",
                    intent="commercial",
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                ),
                visibility_models.ConfigModelRegistry(
                    id=ids["model_registry_id"],
                    provider_id=ids["provider_id"],
                    model_id=f"gpt-test-{uuid4()}",
                    display_name="GPT Test",
                    owned_by="openai",
                    is_available=True,
                    enabled_for_visibility=False,
                    rate_limit_policy_id=None,
                    capability_json={"responses": True},
                    discovered_at=now,
                    updated_at=now,
                ),
            ]
        )
        session.flush()
        session.add(
            visibility_models.ConfigPromptVersion(
                id=ids["prompt_version_id"],
                prompt_id=ids["prompt_id"],
                version=1,
                prompt_text="Which AI visibility platforms should I evaluate?",
                is_active=True,
                created_at=now,
            )
        )
        session.flush()
        session.add(
            visibility_models.RunBatch(
                id=ids["run_batch_id"],
                brand_id=ids["brand_id"],
                prompt_set_id=ids["prompt_set_id"],
                config_snapshot_json={},
                status="succeeded",
                started_at=now,
                completed_at=now,
            )
        )
        session.flush()
        session.add(
            visibility_models.RunItem(
                id=ids["run_item_id"],
                run_batch_id=ids["run_batch_id"],
                prompt_version_id=ids["prompt_version_id"],
                provider_id=ids["provider_id"],
                model_registry_id=ids["model_registry_id"],
                sample_index=0,
                idempotency_key=f"run-item:{ids['run_item_id']}",
                status="succeeded",
                attempt_count=1,
                max_attempts=3,
                lease_expires_at=None,
                next_attempt_at=now,
                last_error=None,
            )
        )
        session.flush()
        competitor = session.get(config_models.Competitor, ids["competitor_id"])
        assert competitor is not None
        session.add(
            visibility_models.RawResponse(
                id=ids["raw_response_id"],
                run_item_id=ids["run_item_id"],
                idempotency_key=f"raw:{ids['raw_response_id']}",
                provider_id=ids["provider_id"],
                model_id="gpt-test",
                provider_response_id="response-test",
                prompt_text="Which platforms should I evaluate?",
                output_text=(
                    f"Brandlight is a strong option. "
                    f"{competitor.name} "
                    f"is not recommended. See https://www.brandlight.ai/docs."
                ),
                raw_request_json={"prompt": "Which platforms should I evaluate?"},
                raw_response_json={"id": "response-test"},
                usage_json={},
                latency_ms=10,
                status="succeeded",
            )
        )
        session.commit()
    return ids


if __name__ == "__main__":
    unittest.main()
