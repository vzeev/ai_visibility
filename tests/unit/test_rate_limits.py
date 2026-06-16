import unittest

from apps.shared.ai.rate_limits import RateLimitPolicy, resolve_rate_limit


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
