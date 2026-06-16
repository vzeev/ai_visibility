from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class RateLimitPolicy:
    provider_id: str
    model_id: str | None
    max_concurrent_requests: int
    requests_per_minute: int
    tokens_per_minute: int | None = None
    min_delay_ms: int = 0
    max_retries: int = 3
    backoff_base_ms: int = 1_000
    backoff_max_ms: int = 60_000

    def __post_init__(self) -> None:
        if self.max_concurrent_requests < 1:
            raise ValueError("max_concurrent_requests must be positive")
        if self.requests_per_minute < 1:
            raise ValueError("requests_per_minute must be positive")
        if self.tokens_per_minute is not None and self.tokens_per_minute < 1:
            raise ValueError("tokens_per_minute must be positive when set")
        if self.min_delay_ms < 0:
            raise ValueError("min_delay_ms must not be negative")
        if self.max_retries < 0:
            raise ValueError("max_retries must not be negative")


DEFAULT_POLICY = RateLimitPolicy(
    provider_id="default",
    model_id=None,
    max_concurrent_requests=1,
    requests_per_minute=20,
    tokens_per_minute=None,
    min_delay_ms=250,
)


def resolve_rate_limit(
    *,
    provider_id: str,
    model_id: str,
    policies: Iterable[RateLimitPolicy],
    default_policy: RateLimitPolicy = DEFAULT_POLICY,
) -> RateLimitPolicy:
    provider_fallback: RateLimitPolicy | None = None
    for policy in policies:
        if policy.provider_id != provider_id:
            continue
        if policy.model_id == model_id:
            return policy
        if policy.model_id is None:
            provider_fallback = policy
    if provider_fallback is not None:
        return provider_fallback
    return replace(default_policy, provider_id=provider_id)
