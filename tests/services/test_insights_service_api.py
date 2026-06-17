from __future__ import annotations

import unittest
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.insights_service.app.db import models
from apps.insights_service.app.db.session import get_session
from apps.insights_service.app.main import create_app


class InsightsServiceApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = _create_sqlite_engine()
        models.Base.metadata.create_all(self.engine)
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )
        self.ids = _seed_visibility_data(self.session_factory)
        app = create_app()

        def override_session() -> Iterator[Session]:
            with self.session_factory() as session:
                yield session

        app.dependency_overrides[get_session] = override_session
        self.client: Any = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        self.engine.dispose()

    def test_raw_response_extraction_is_idempotent_and_evidence_linked(self) -> None:
        first = _dict_payload(
            self._post(
                f"/api/v1/extractions/raw-responses/{self.ids['raw_response_id']}",
                json={"extraction_version": "deterministic-v1"},
            )
        )
        second = _dict_payload(
            self._post(
                f"/api/v1/extractions/raw-responses/{self.ids['raw_response_id']}",
                json={"extraction_version": "deterministic-v1"},
            )
        )

        self.assertEqual(first["id"], second["id"])
        self.assertEqual("completed", first["status"])
        self.assertEqual(2, len(first["mentions"]))
        self.assertEqual(1, len(first["citations"]))
        self.assertEqual(
            str(self.ids["raw_response_id"]),
            first["mentions"][0]["evidence_json"]["raw_response_id"],
        )
        self.assertEqual(
            str(self.ids["raw_response_id"]),
            first["citations"][0]["evidence_json"]["raw_response_id"],
        )

        with self.session_factory() as session:
            mention_count = session.scalar(
                select(func.count()).select_from(models.ExtractedMention)
            )
            citation_count = session.scalar(
                select(func.count()).select_from(models.ExtractedCitation)
            )
            extraction_count = session.scalar(
                select(func.count()).select_from(models.ExtractionRun)
            )
        self.assertEqual(2, mention_count)
        self.assertEqual(1, citation_count)
        self.assertEqual(1, extraction_count)

    def test_batch_extraction_creates_filterable_summary(self) -> None:
        result = _dict_payload(
            self._post(
                f"/api/v1/extractions/run-batches/{self.ids['run_batch_id']}",
                json={"extraction_version": "deterministic-v1"},
            )
        )

        self.assertEqual(str(self.ids["run_batch_id"]), result["run_batch_id"])
        self.assertEqual(1, result["raw_response_count"])
        summary = result["summary"]
        self.assertEqual("deterministic-v1", summary["extraction_version"])
        self.assertIsInstance(summary["created_at"], str)
        self.assertEqual(
            [str(self.ids["raw_response_id"])], summary["summary_json"]["raw_response_ids"]
        )
        self.assertEqual(1, summary["summary_json"]["brand_mentions"])
        self.assertEqual(1, summary["summary_json"]["competitor_mentions"])
        self.assertEqual(1, summary["summary_json"]["citation_count"])

        summaries = _list_payload(
            self._get(
                "/api/v1/summaries",
                params={
                    "run_batch_id": str(self.ids["run_batch_id"]),
                    "extraction_version": "deterministic-v1",
                },
            )
        )
        self.assertEqual(1, len(summaries))
        self.assertEqual(summary["id"], summaries[0]["id"])

    def _post(self, url: str, *, json: dict[str, Any]) -> Response:
        return cast(Response, self.client.post(url, json=json))

    def _get(self, url: str, *, params: dict[str, Any] | None = None) -> Response:
        return cast(Response, self.client.get(url, params=params))


def _seed_visibility_data(session_factory: sessionmaker[Session]) -> dict[str, Any]:
    now = datetime.now(UTC)
    ids = {
        "brand_id": uuid4(),
        "alias_id": uuid4(),
        "competitor_id": uuid4(),
        "run_batch_id": uuid4(),
        "run_item_id": uuid4(),
        "raw_response_id": uuid4(),
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
                ),
                models.ConfigBrandAlias(
                    id=ids["alias_id"],
                    brand_id=ids["brand_id"],
                    alias="Brand Light",
                ),
                models.ConfigCompetitor(
                    id=ids["competitor_id"],
                    brand_id=ids["brand_id"],
                    name="AcmeRank",
                    website_url="https://example.com/",
                ),
                models.VisibilityRunBatch(
                    id=ids["run_batch_id"],
                    brand_id=ids["brand_id"],
                    prompt_set_id=uuid4(),
                    config_snapshot_json={},
                    status="succeeded",
                ),
                models.VisibilityRunItem(
                    id=ids["run_item_id"],
                    run_batch_id=ids["run_batch_id"],
                    provider_id=ids["provider_id"],
                    model_registry_id=ids["model_registry_id"],
                ),
                models.VisibilityRawResponse(
                    id=ids["raw_response_id"],
                    run_item_id=ids["run_item_id"],
                    idempotency_key=f"raw:{ids['raw_response_id']}",
                    provider_id=ids["provider_id"],
                    model_id="gpt-test",
                    provider_response_id="response-test",
                    prompt_text="Which platforms should I evaluate?",
                    output_text=(
                        "Brandlight is a strong option. "
                        "AcmeRank is not recommended. "
                        "See https://www.brandlight.ai/docs."
                    ),
                    raw_request_json={"prompt": "Which platforms should I evaluate?"},
                    raw_response_json={"id": "response-test"},
                    usage_json={},
                    latency_ms=10,
                    status="succeeded",
                    created_at=now,
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
    cursor.execute("ATTACH DATABASE ':memory:' AS insights")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _dict_payload(response: Response) -> dict[str, Any]:
    return cast(dict[str, Any], response.json())


def _list_payload(response: Response) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], response.json())


if __name__ == "__main__":
    unittest.main()
