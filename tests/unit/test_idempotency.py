import unittest

from apps.shared.ai.idempotency import (
    build_raw_response_idempotency_key,
    build_run_item_idempotency_key,
)


class IdempotencyTests(unittest.TestCase):
    def test_run_item_idempotency_key_is_stable(self) -> None:
        first = build_run_item_idempotency_key(
            prompt_version_id="prompt-v1",
            provider_key="openai",
            model_id="gpt-5-main",
            sample_index=0,
            config_snapshot_hash="snapshot-1",
        )
        second = build_run_item_idempotency_key(
            prompt_version_id="prompt-v1",
            provider_key="openai",
            model_id="gpt-5-main",
            sample_index=0,
            config_snapshot_hash="snapshot-1",
        )

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("run-item:v1:sha256:"))

    def test_run_item_idempotency_key_changes_when_model_changes(self) -> None:
        first = build_run_item_idempotency_key(
            prompt_version_id="prompt-v1",
            provider_key="openai",
            model_id="gpt-5-main",
            sample_index=0,
            config_snapshot_hash="snapshot-1",
        )
        second = build_run_item_idempotency_key(
            prompt_version_id="prompt-v1",
            provider_key="openai",
            model_id="gpt-5-mini",
            sample_index=0,
            config_snapshot_hash="snapshot-1",
        )

        self.assertNotEqual(first, second)

    def test_raw_response_idempotency_key_is_stable_for_same_raw_payload(self) -> None:
        key = "run-item:v1:sha256:abc"
        first = build_raw_response_idempotency_key(
            run_item_idempotency_key=key,
            provider_key="openai",
            model_id="gpt-5-main",
            provider_response_id="resp-1",
            raw_response_json={"b": 2, "a": 1},
        )
        second = build_raw_response_idempotency_key(
            run_item_idempotency_key=key,
            provider_key="openai",
            model_id="gpt-5-main",
            provider_response_id="resp-1",
            raw_response_json={"a": 1, "b": 2},
        )

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("raw-response:v1:sha256:"))
