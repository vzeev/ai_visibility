import asyncio
import unittest

from apps.shared.ai.provider import AIRequest, FakeAIProviderAdapter


class ProviderAdapterTests(unittest.TestCase):
    def test_fake_provider_adapter_returns_normalized_response(self) -> None:
        adapter = FakeAIProviderAdapter({"gpt-5-main": "Brandlight is visible."})
        response = asyncio.run(
            adapter.complete(
                AIRequest(
                    provider_key="fake",
                    model_id="gpt-5-main",
                    prompt_text="Where does Brandlight appear?",
                )
            )
        )

        self.assertEqual(response.provider_key, "fake")
        self.assertEqual(response.model_id, "gpt-5-main")
        self.assertEqual(response.output_text, "Brandlight is visible.")
        self.assertEqual(response.raw_request_json["model"], "gpt-5-main")
        self.assertEqual(response.raw_response_json["id"], "fake-gpt-5-main")
