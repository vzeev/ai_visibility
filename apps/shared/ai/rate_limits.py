from __future__ import annotations

import math
import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, replace
from typing import Protocol


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
        if self.backoff_base_ms < 0:
            raise ValueError("backoff_base_ms must not be negative")
        if self.backoff_max_ms < 0:
            raise ValueError("backoff_max_ms must not be negative")


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int = 0


class RateLimitGate(Protocol):
    def check(
        self,
        *,
        provider_key: str,
        model_id: str,
        policy: RateLimitPolicy,
    ) -> RateLimitDecision: ...

    def record_execution(
        self,
        *,
        provider_key: str,
        model_id: str,
        policy: RateLimitPolicy,
    ) -> None: ...


DEFAULT_POLICY = RateLimitPolicy(
    provider_id="default",
    model_id=None,
    max_concurrent_requests=1,
    requests_per_minute=20,
    tokens_per_minute=None,
    min_delay_ms=0,
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


class InMemoryRateLimitGate:
    def __init__(self, *, clock: Callable[[], float] | None = None) -> None:
        self._clock = clock or time.monotonic
        self._last_execution_at: dict[tuple[str, str], float] = {}

    def check(
        self,
        *,
        provider_key: str,
        model_id: str,
        policy: RateLimitPolicy,
    ) -> RateLimitDecision:
        if policy.min_delay_ms <= 0:
            return RateLimitDecision(allowed=True)
        key = (provider_key, model_id)
        last_execution_at = self._last_execution_at.get(key)
        if last_execution_at is None:
            return RateLimitDecision(allowed=True)
        seconds_between_calls = policy.min_delay_ms / 1000
        next_allowed_at = last_execution_at + seconds_between_calls
        now = self._clock()
        if now >= next_allowed_at:
            return RateLimitDecision(allowed=True)
        retry_after = max(1, math.ceil(next_allowed_at - now))
        return RateLimitDecision(allowed=False, retry_after_seconds=retry_after)

    def record_execution(
        self,
        *,
        provider_key: str,
        model_id: str,
        policy: RateLimitPolicy,
    ) -> None:
        if policy.min_delay_ms > 0:
            self._last_execution_at[(provider_key, model_id)] = self._clock()


def rate_limit_policy_from_mapping(
    value: Mapping[str, object] | None,
    *,
    provider_id: str,
    model_id: str,
) -> RateLimitPolicy:
    if value is None:
        return replace(DEFAULT_POLICY, provider_id=provider_id, model_id=model_id)
    return RateLimitPolicy(
        provider_id=str(value.get("provider_id") or provider_id),
        model_id=_optional_string(value.get("model_id"), default=model_id),
        max_concurrent_requests=_int_value(value, "max_concurrent_requests", 1),
        requests_per_minute=_int_value(value, "requests_per_minute", 20),
        tokens_per_minute=_optional_int(value.get("tokens_per_minute")),
        min_delay_ms=_int_value(value, "min_delay_ms", 0),
        max_retries=_int_value(value, "max_retries", 3),
        backoff_base_ms=_int_value(value, "backoff_base_ms", 1_000),
        backoff_max_ms=_int_value(value, "backoff_max_ms", 60_000),
    )


def _int_value(value: Mapping[str, object], key: str, default: int) -> int:
    candidate = value.get(key)
    if isinstance(candidate, int):
        return candidate
    return default


def _optional_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    return None


def _optional_string(value: object, *, default: str) -> str | None:
    if isinstance(value, str):
        return value
    return default
