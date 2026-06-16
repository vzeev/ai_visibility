import unittest

from apps.shared.ai.rate_limits import (
    InMemoryRateLimitGate,
    RateLimitPolicy,
    rate_limit_policy_from_mapping,
    resolve_rate_limit,
)


class RateLimitTests(unittest.TestCase):
    def test_resolve_rate_limit_prefers_model_specific_policy(self) -> None:
        fallback = RateLimitPolicy(
            provider_id="openai",
            model_id=None,
            max_concurrent_requests=1,
            requests_per_minute=20,
        )
        model_specific = RateLimitPolicy(
            provider_id="openai",
            model_id="gpt-5-main",
            max_concurrent_requests=2,
            requests_per_minute=40,
        )

        result = resolve_rate_limit(
            provider_id="openai",
            model_id="gpt-5-main",
            policies=[fallback, model_specific],
        )

        self.assertEqual(result, model_specific)

    def test_resolve_rate_limit_uses_provider_fallback(self) -> None:
        fallback = RateLimitPolicy(
            provider_id="openai",
            model_id=None,
            max_concurrent_requests=1,
            requests_per_minute=20,
        )

        result = resolve_rate_limit(
            provider_id="openai",
            model_id="gpt-5-mini",
            policies=[fallback],
        )

        self.assertEqual(result, fallback)

    def test_rate_limit_policy_rejects_invalid_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "requests_per_minute"):
            RateLimitPolicy(
                provider_id="openai",
                model_id="gpt-5-main",
                max_concurrent_requests=1,
                requests_per_minute=0,
            )

    def test_in_memory_gate_blocks_until_min_delay_elapses(self) -> None:
        current_time = 100.0
        gate = InMemoryRateLimitGate(clock=lambda: current_time)
        policy = RateLimitPolicy(
            provider_id="openai",
            model_id="gpt-5-main",
            max_concurrent_requests=1,
            requests_per_minute=20,
            min_delay_ms=2_000,
        )

        self.assertTrue(
            gate.check(provider_key="openai", model_id="gpt-5-main", policy=policy).allowed
        )
        gate.record_execution(provider_key="openai", model_id="gpt-5-main", policy=policy)
        blocked = gate.check(provider_key="openai", model_id="gpt-5-main", policy=policy)
        self.assertFalse(blocked.allowed)
        self.assertEqual(2, blocked.retry_after_seconds)

    def test_rate_limit_policy_from_mapping_uses_snapshot_values(self) -> None:
        policy = rate_limit_policy_from_mapping(
            {
                "provider_id": "provider-1",
                "model_id": "gpt-test",
                "max_concurrent_requests": 2,
                "requests_per_minute": 30,
                "tokens_per_minute": 1_000,
                "min_delay_ms": 500,
                "max_retries": 4,
                "backoff_base_ms": 250,
                "backoff_max_ms": 5_000,
            },
            provider_id="openai",
            model_id="gpt-test",
        )

        self.assertEqual("provider-1", policy.provider_id)
        self.assertEqual("gpt-test", policy.model_id)
        self.assertEqual(2, policy.max_concurrent_requests)
        self.assertEqual(500, policy.min_delay_ms)
