from __future__ import annotations

import asyncio
import json
import unittest
from typing import Any

import httpx

from apps.shared.ai.credentials import MissingProviderCredentialError, StaticCredentialResolver
from apps.shared.ai.openai_provider import OpenAIResponsesAdapter
from apps.shared.ai.provider import AIProviderError, AIRequest


class OpenAIProviderAdapterTests(unittest.TestCase):
    def test_responses_adapter_normalizes_successful_response(self) -> None:
        seen_payloads: list[dict[str, Any]] = []

        async def handler(request: httpx.Request) -> httpx.Response:
            seen_payloads.append(json.loads(request.content.decode("utf-8")))
            self.assertEqual("Bearer test-token", request.headers["Authorization"])
            return httpx.Response(
                200,
                json={
                    "id": "resp_123",
                    "model": "gpt-test",
                    "output": [
                        {
                            "type": "message",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": "Brandlight appears in AI answers.",
                                }
                            ],
                        }
                    ],
                    "usage": {"input_tokens": 10, "output_tokens": 7, "total_tokens": 17},
                },
            )

        response = asyncio.run(_complete_with_handler(handler))

        self.assertEqual("openai", response.provider_key)
        self.assertEqual("gpt-test", response.model_id)
        self.assertEqual("Brandlight appears in AI answers.", response.output_text)
        self.assertEqual("resp_123", response.provider_response_id)
        self.assertEqual(
            {"input_tokens": 10, "output_tokens": 7, "total_tokens": 17}, response.usage_json
        )
        self.assertEqual("gpt-test", seen_payloads[0]["model"])
        self.assertEqual("Which tools mention Brandlight?", seen_payloads[0]["input"])
        self.assertNotIn("test-token", json.dumps(response.raw_request_json))

    def test_rate_limit_response_is_retryable_provider_error(self) -> None:
        async def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(429, json={"error": {"message": "too many requests"}})

        with self.assertRaises(AIProviderError) as raised:
            asyncio.run(_complete_with_handler(handler))

        self.assertTrue(raised.exception.retryable)
        self.assertIn("OpenAI HTTP 429", str(raised.exception))

    def test_non_rate_limit_4xx_is_non_retryable_provider_error(self) -> None:
        async def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(400, json={"error": {"message": "bad request"}})

        with self.assertRaises(AIProviderError) as raised:
            asyncio.run(_complete_with_handler(handler))

        self.assertFalse(raised.exception.retryable)
        self.assertIn("OpenAI HTTP 400", str(raised.exception))

    def test_missing_runtime_credential_fails_closed(self) -> None:
        adapter = OpenAIResponsesAdapter(credential_resolver=MissingCredentialResolver())
        with self.assertRaises(AIProviderError) as raised:
            asyncio.run(adapter.complete(_request()))

        self.assertTrue(raised.exception.retryable)
        self.assertIn("runtime credential is not configured", str(raised.exception))


class MissingCredentialResolver:
    def resolve_token(self, provider_key: str) -> str:
        raise MissingProviderCredentialError(provider_key)


async def _complete_with_handler(
    handler: Any,
) -> Any:
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = OpenAIResponsesAdapter(
            credential_resolver=StaticCredentialResolver("test-token"),
            http_client=client,
        )
        return await adapter.complete(_request())


def _request() -> AIRequest:
    return AIRequest(
        provider_key="openai",
        model_id="gpt-test",
        prompt_text="Which tools mention Brandlight?",
        system_text="Answer concisely.",
        max_output_tokens=128,
        temperature=0.2,
        metadata={"run_item_id": "item-1"},
    )
