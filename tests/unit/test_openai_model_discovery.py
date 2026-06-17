from __future__ import annotations

import unittest

import httpx

from apps.shared.ai.credentials import StaticCredentialResolver
from apps.shared.ai.model_discovery import (
    ModelDiscoveryError,
    OpenAIModelDiscoveryClient,
)


class OpenAIModelDiscoveryClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_lists_openai_models_with_bearer_auth(self) -> None:
        seen_headers: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen_headers["authorization"] = request.headers["Authorization"]
            self.assertEqual("GET", request.method)
            self.assertEqual("https://api.openai.com/v1/models", str(request.url))
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        {
                            "id": "gpt-test-a",
                            "object": "model",
                            "created": 1,
                            "owned_by": "openai",
                        },
                        {
                            "id": "gpt-test-b",
                            "object": "model",
                            "created": 2,
                            "owned_by": "system",
                        },
                    ],
                },
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as http_client:
            client = OpenAIModelDiscoveryClient(
                credential_resolver=StaticCredentialResolver("sk-test"),
                http_client=http_client,
            )

            models = await client.list_models("openai")

        self.assertEqual("Bearer sk-test", seen_headers["authorization"])
        self.assertEqual(["gpt-test-a", "gpt-test-b"], [model.model_id for model in models])
        self.assertEqual("openai", models[0].owned_by)
        self.assertEqual("openai.models", models[0].capability_json["source"])

    async def test_missing_credential_fails_closed(self) -> None:
        client = OpenAIModelDiscoveryClient(
            credential_resolver=StaticCredentialResolver(""),
        )

        with self.assertRaises(ModelDiscoveryError) as error:
            await client.list_models("openai")

        self.assertTrue(error.exception.retryable)
        self.assertNotIn("sk-", str(error.exception))

    async def test_rate_limit_response_is_retryable(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                429,
                json={"error": {"message": "slow down"}},
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as http_client:
            client = OpenAIModelDiscoveryClient(
                credential_resolver=StaticCredentialResolver("sk-test"),
                http_client=http_client,
            )

            with self.assertRaises(ModelDiscoveryError) as error:
                await client.list_models("openai")

        self.assertTrue(error.exception.retryable)
        self.assertIn("HTTP 429", str(error.exception))
