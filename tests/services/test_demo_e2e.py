from __future__ import annotations

import unittest
from typing import Any

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.config_service.app.db import models as config_models
from apps.insights_service.app.db import models as insights_models
from apps.visibility_service.app.db import models as visibility_models
from scripts.ai_visibility_tools.demo_e2e import (
    DEMO_BRAND_NAME,
    DEMO_PROVIDER_KEY,
    run_brandlight_demo_smoke,
    seed_brandlight_demo,
)


class DemoE2eTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = _create_sqlite_engine()
        config_models.Base.metadata.create_all(self.engine)
        visibility_models.Base.metadata.create_all(self.engine)
        insights_models.Base.metadata.create_all(self.engine)
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def tearDown(self) -> None:
        self.engine.dispose()

    def test_brandlight_seed_is_idempotent_for_config_entities(self) -> None:
        first = seed_brandlight_demo(self.session_factory)
        second = seed_brandlight_demo(self.session_factory)

        self.assertEqual(first.brand_id, second.brand_id)
        self.assertEqual(first.prompt_set_id, second.prompt_set_id)
        self.assertEqual(first.provider_id, second.provider_id)
        self.assertEqual(first.model_registry_id, second.model_registry_id)
        with self.session_factory() as session:
            brand_count = _count(
                session,
                select(func.count())
                .select_from(config_models.Brand)
                .where(config_models.Brand.name == DEMO_BRAND_NAME),
            )
            provider_count = _count(
                session,
                select(func.count())
                .select_from(config_models.Provider)
                .where(config_models.Provider.provider_key == DEMO_PROVIDER_KEY),
            )
            prompt_set_count = _count(
                session,
                select(func.count())
                .select_from(config_models.PromptSet)
                .where(config_models.PromptSet.name == "Brandlight interview demo prompts"),
            )
        self.assertEqual(1, brand_count)
        self.assertEqual(1, provider_count)
        self.assertEqual(1, prompt_set_count)

    def test_smoke_flow_processes_raw_responses_and_extracts_insights(self) -> None:
        result = run_brandlight_demo_smoke(self.session_factory)

        self.assertEqual(result.item_count, result.processed_count)
        self.assertEqual(0, result.failed_count)
        self.assertEqual(result.item_count, result.raw_response_count)
        self.assertEqual(result.raw_response_count, result.extraction_run_count)
        self.assertGreater(result.mention_count, 0)
        self.assertGreater(result.citation_count, 0)

        with self.session_factory() as session:
            raw_count = _count(
                session,
                select(func.count()).select_from(visibility_models.RawResponse),
            )
            summary_count = _count(
                session,
                select(func.count()).select_from(insights_models.VisibilitySummary),
            )
        self.assertEqual(result.raw_response_count, raw_count)
        self.assertEqual(1, summary_count)


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
    cursor.execute("ATTACH DATABASE ':memory:' AS insights")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _count(session: Session, statement: Any) -> int:
    return int(session.scalar(statement) or 0)
