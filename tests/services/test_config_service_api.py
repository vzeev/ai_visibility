from __future__ import annotations

import unittest
from collections.abc import Iterator
from typing import Any, cast

from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.config_service.app.api.routes import get_model_discovery_client
from apps.config_service.app.db import models
from apps.config_service.app.db.session import get_session
from apps.config_service.app.main import create_app
from apps.shared.ai.model_discovery import DiscoveredModel


class ConfigServiceApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = _create_sqlite_engine()
        models.Base.metadata.create_all(self.engine)
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )
        self.app = create_app()

        def override_session() -> Iterator[Session]:
            with self.session_factory() as session:
                yield session

        self.app.dependency_overrides[get_session] = override_session
        self.client: Any = TestClient(self.app)

    def tearDown(self) -> None:
        self.client.close()
        self.app.dependency_overrides.clear()
        self.engine.dispose()

    def test_brand_competitor_and_product_are_persisted(self) -> None:
        brand = self._create_brand("Brandlight")

        duplicate = self._post(
            "/api/v1/brands",
            json={"name": "Brandlight"},
        )
        self.assertEqual(409, duplicate.status_code)

        competitor_response = self._post(
            f"/api/v1/brands/{brand['id']}/competitors",
            json={"name": "Profound", "website_url": "https://example.com"},
        )
        self.assertEqual(201, competitor_response.status_code)

        product_response = self._post(
            f"/api/v1/brands/{brand['id']}/products",
            json={"name": "Visibility Command Center", "description": "AI visibility"},
        )
        self.assertEqual(201, product_response.status_code)

        brands = self._get("/api/v1/brands")
        competitors = self._get(f"/api/v1/brands/{brand['id']}/competitors")
        products = self._get(f"/api/v1/brands/{brand['id']}/products")

        self.assertEqual("Brandlight", _list_payload(brands)[0]["name"])
        self.assertEqual("Profound", _list_payload(competitors)[0]["name"])
        self.assertEqual("Visibility Command Center", _list_payload(products)[0]["name"])

    def test_prompt_updates_create_active_versions(self) -> None:
        brand = self._create_brand("Prompt Brand")
        prompt_set = self._create_prompt_set(brand["id"], "Default prompts")

        prompt_response = self._post(
            "/api/v1/prompts",
            json={
                "prompt_set_id": prompt_set["id"],
                "name": "Buyer question",
                "intent": "commercial",
                "prompt_text": "Which AI visibility platforms should I evaluate?",
            },
        )
        self.assertEqual(201, prompt_response.status_code)
        prompt = _dict_payload(prompt_response)
        self.assertEqual(1, prompt["active_version"]["version"])

        version_response = self._post(
            f"/api/v1/prompts/{prompt['id']}/versions",
            json={"prompt_text": "Which enterprise AI visibility platforms should I evaluate?"},
        )
        self.assertEqual(201, version_response.status_code)
        updated_prompt = _dict_payload(version_response)
        self.assertEqual(2, updated_prompt["active_version"]["version"])
        self.assertIn("enterprise", updated_prompt["active_version"]["prompt_text"])

        prompts = self._get(
            "/api/v1/prompts",
            params={"prompt_set_id": prompt_set["id"]},
        )
        self.assertEqual(200, prompts.status_code)
        self.assertEqual(2, _list_payload(prompts)[0]["active_version"]["version"])

    def test_provider_credentials_are_write_only(self) -> None:
        provider = self._create_provider("openai")
        token = "sk-test-secret-value"

        credential_response = self._post(
            "/api/v1/provider-credentials",
            json={"provider_id": provider["id"], "label": "local dev", "token": token},
        )
        self.assertEqual(201, credential_response.status_code)
        credential = _dict_payload(credential_response)
        self.assertNotIn(token, credential_response.text)
        self.assertTrue(credential["redacted_fingerprint"].startswith("sha256:"))

        credentials_response = self._get("/api/v1/provider-credentials")
        self.assertEqual(200, credentials_response.status_code)
        self.assertNotIn(token, credentials_response.text)

        with self.session_factory() as session:
            stored = session.scalar(select(models.ProviderCredential))
            self.assertIsNotNone(stored)
            if stored is not None:
                self.assertNotEqual(token, stored.secret_ref)
                self.assertTrue((stored.secret_ref or "").startswith("local-sha256:"))

    def test_rate_limits_and_models_are_persisted(self) -> None:
        provider = self._create_provider("openai-models")

        rate_limit_response = self._post(
            "/api/v1/rate-limits",
            json={
                "provider_id": provider["id"],
                "model_id": None,
                "max_concurrent_requests": 2,
                "requests_per_minute": 40,
                "tokens_per_minute": 10000,
                "min_delay_ms": 100,
                "max_retries": 4,
                "backoff_base_ms": 500,
                "backoff_max_ms": 30000,
            },
        )
        self.assertEqual(201, rate_limit_response.status_code)
        rate_limit = _dict_payload(rate_limit_response)

        model_response = self._post(
            "/api/v1/models",
            json={
                "provider_id": provider["id"],
                "model_id": "gpt-test",
                "display_name": "GPT Test",
                "owned_by": "openai",
                "is_available": True,
                "enabled_for_visibility": True,
                "rate_limit_policy_id": rate_limit["id"],
                "capability_json": {"responses": True},
            },
        )
        self.assertEqual(201, model_response.status_code)

        models_response = self._get("/api/v1/models", params={"provider_id": provider["id"]})
        self.assertEqual(200, models_response.status_code)
        models_payload = _list_payload(models_response)
        self.assertEqual("gpt-test", models_payload[0]["model_id"])
        self.assertTrue(models_payload[0]["enabled_for_visibility"])
        self.assertEqual({"responses": True}, models_payload[0]["capability_json"])

    def test_model_visibility_can_be_enabled_and_disabled(self) -> None:
        provider = self._create_provider("openai-visibility")
        model_response = self._post(
            "/api/v1/models",
            json={
                "provider_id": provider["id"],
                "model_id": "gpt-visible",
                "display_name": "GPT Visible",
                "owned_by": "openai",
                "is_available": True,
                "enabled_for_visibility": False,
                "capability_json": {"responses": True},
            },
        )
        self.assertEqual(201, model_response.status_code)
        model = _dict_payload(model_response)

        enabled_response = self._patch(
            f"/api/v1/models/{model['id']}/visibility",
            json={"enabled_for_visibility": True},
        )
        self.assertEqual(200, enabled_response.status_code)
        self.assertTrue(_dict_payload(enabled_response)["enabled_for_visibility"])

        disabled_response = self._patch(
            f"/api/v1/models/{model['id']}/visibility",
            json={"enabled_for_visibility": False},
        )
        self.assertEqual(200, disabled_response.status_code)
        self.assertFalse(_dict_payload(disabled_response)["enabled_for_visibility"])

    def test_unavailable_model_cannot_be_enabled_for_visibility(self) -> None:
        provider = self._create_provider("openai-unavailable")
        model_response = self._post(
            "/api/v1/models",
            json={
                "provider_id": provider["id"],
                "model_id": "gpt-stale",
                "display_name": "GPT Stale",
                "owned_by": "openai",
                "is_available": False,
                "enabled_for_visibility": False,
                "capability_json": {},
            },
        )
        self.assertEqual(201, model_response.status_code)
        model = _dict_payload(model_response)

        enabled_response = self._patch(
            f"/api/v1/models/{model['id']}/visibility",
            json={"enabled_for_visibility": True},
        )
        self.assertEqual(409, enabled_response.status_code)

    def test_model_sync_preserves_local_settings_and_marks_unavailable(self) -> None:
        provider = self._create_provider("openai")
        rate_limit_response = self._post(
            "/api/v1/rate-limits",
            json={
                "provider_id": provider["id"],
                "model_id": "gpt-existing",
                "max_concurrent_requests": 1,
                "requests_per_minute": 10,
            },
        )
        self.assertEqual(201, rate_limit_response.status_code)
        rate_limit = _dict_payload(rate_limit_response)
        existing_response = self._post(
            "/api/v1/models",
            json={
                "provider_id": provider["id"],
                "model_id": "gpt-existing",
                "display_name": "Old display name",
                "owned_by": "old-owner",
                "is_available": True,
                "enabled_for_visibility": True,
                "rate_limit_policy_id": rate_limit["id"],
                "capability_json": {"old": True},
            },
        )
        self.assertEqual(201, existing_response.status_code)
        stale_response = self._post(
            "/api/v1/models",
            json={
                "provider_id": provider["id"],
                "model_id": "gpt-stale",
                "display_name": "Stale",
                "is_available": True,
                "enabled_for_visibility": True,
                "capability_json": {},
            },
        )
        self.assertEqual(201, stale_response.status_code)

        fake_discovery = _FakeModelDiscoveryClient(
            [
                DiscoveredModel(
                    model_id="gpt-existing",
                    display_name="gpt-existing",
                    owned_by="openai",
                    capability_json={"source": "test"},
                ),
                DiscoveredModel(
                    model_id="gpt-new",
                    display_name="gpt-new",
                    owned_by="openai",
                    capability_json={"source": "test"},
                ),
            ]
        )
        self.app.dependency_overrides[get_model_discovery_client] = lambda: fake_discovery

        sync_response = self._post(f"/api/v1/providers/{provider['id']}/models/sync", json={})

        self.assertEqual(200, sync_response.status_code)
        payload = _dict_payload(sync_response)
        self.assertEqual("openai", fake_discovery.provider_key)
        self.assertEqual(2, payload["discovered_count"])
        self.assertEqual(1, payload["created_count"])
        self.assertEqual(1, payload["updated_count"])
        self.assertEqual(1, payload["unavailable_count"])
        by_model_id = {model["model_id"]: model for model in payload["models"]}
        self.assertTrue(by_model_id["gpt-existing"]["enabled_for_visibility"])
        self.assertEqual(rate_limit["id"], by_model_id["gpt-existing"]["rate_limit_policy_id"])
        self.assertEqual("openai", by_model_id["gpt-existing"]["owned_by"])
        self.assertFalse(by_model_id["gpt-new"]["enabled_for_visibility"])
        self.assertTrue(by_model_id["gpt-new"]["is_available"])
        self.assertFalse(by_model_id["gpt-stale"]["is_available"])

    def _create_brand(self, name: str) -> dict[str, Any]:
        response = self._post(
            "/api/v1/brands",
            json={"name": name, "website_url": "https://brandlight.ai"},
        )
        self.assertEqual(201, response.status_code)
        return _dict_payload(response)

    def _create_prompt_set(self, brand_id: str, name: str) -> dict[str, Any]:
        response = self._post(
            "/api/v1/prompt-sets",
            json={"brand_id": brand_id, "name": name, "description": "core"},
        )
        self.assertEqual(201, response.status_code)
        return _dict_payload(response)

    def _create_provider(self, provider_key: str) -> dict[str, Any]:
        response = self._post(
            "/api/v1/providers",
            json={
                "provider_key": provider_key,
                "display_name": provider_key.title(),
                "provider_kind": "llm",
            },
        )
        self.assertEqual(201, response.status_code)
        return _dict_payload(response)

    def _post(self, url: str, *, json: dict[str, Any]) -> Response:
        return cast(Response, self.client.post(url, json=json))

    def _patch(self, url: str, *, json: dict[str, Any]) -> Response:
        return cast(Response, self.client.patch(url, json=json))

    def _get(self, url: str, *, params: dict[str, Any] | None = None) -> Response:
        return cast(Response, self.client.get(url, params=params))


def _create_sqlite_engine() -> Engine:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    event.listen(engine, "connect", _attach_config_schema)

    return engine


def _attach_config_schema(dbapi_connection: Any, _connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("ATTACH DATABASE ':memory:' AS config")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _dict_payload(response: Response) -> dict[str, Any]:
    return cast(dict[str, Any], response.json())


def _list_payload(response: Response) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], response.json())


class _FakeModelDiscoveryClient:
    def __init__(self, models: list[DiscoveredModel]) -> None:
        self._models = models
        self.provider_key: str | None = None

    async def list_models(self, provider_key: str) -> list[DiscoveredModel]:
        self.provider_key = provider_key
        return self._models
