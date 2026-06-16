from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, cast
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from apps.shared.ai.openai_provider import OpenAIResponsesAdapter
from apps.shared.ai.provider import (
    AIProviderAdapter,
    AIProviderError,
    AIRequest,
    FakeAIProviderAdapter,
)
from apps.shared.ai.rate_limits import (
    InMemoryRateLimitGate,
    RateLimitGate,
    RateLimitPolicy,
    rate_limit_policy_from_mapping,
)
from apps.visibility_service.app.db.repository import VisibilityRepository

WorkerStatus = Literal["processed", "idle", "failed"]


@dataclass(frozen=True)
class WorkerProcessResult:
    status: WorkerStatus
    run_item_id: UUID | None = None
    raw_response_id: UUID | None = None
    error_message: str | None = None


class VisibilityWorker:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        adapters: Mapping[str, AIProviderAdapter] | None = None,
        rate_limit_gate: RateLimitGate | None = None,
        lease_seconds: int = 300,
        retry_delay_seconds: int = 0,
    ) -> None:
        self._session_factory = session_factory
        self._fallback_adapter: AIProviderAdapter = FakeAIProviderAdapter()
        self._adapters: dict[str, AIProviderAdapter] = dict(adapters or {})
        self._adapters.setdefault(self._fallback_adapter.provider_key, self._fallback_adapter)
        self._rate_limit_gate = rate_limit_gate or InMemoryRateLimitGate()
        self._lease_seconds = lease_seconds
        self._retry_delay_seconds = retry_delay_seconds

    @classmethod
    def with_openai_enabled(cls, session_factory: sessionmaker[Session]) -> VisibilityWorker:
        return cls(session_factory, adapters={"openai": OpenAIResponsesAdapter()})

    async def process_one(self) -> WorkerProcessResult:
        with self._session_factory() as session:
            repository = VisibilityRepository(session)
            item = repository.claim_next_item(lease_seconds=self._lease_seconds)
            if item is None:
                return WorkerProcessResult(status="idle")

            request = repository.build_ai_request(item)
            rate_limit_policy = _rate_limit_policy_from_request(request)
            decision = self._rate_limit_gate.check(
                provider_key=request.provider_key,
                model_id=request.model_id,
                policy=rate_limit_policy,
            )
            if not decision.allowed:
                throttled_item = repository.record_model_error(
                    run_item_id=item.id,
                    error_type="rate_limit",
                    error_message="provider/model rate limit is not currently eligible",
                    retryable=True,
                    retry_delay_seconds=decision.retry_after_seconds,
                )
                return WorkerProcessResult(
                    status="failed",
                    run_item_id=throttled_item.id,
                    error_message="provider/model rate limit is not currently eligible",
                )

            adapter = self._adapters.get(request.provider_key, self._fallback_adapter)
            try:
                response = await adapter.complete(request)
            except AIProviderError as error:
                failed_item = repository.record_model_error(
                    run_item_id=item.id,
                    error_type="provider_error",
                    error_message=str(error),
                    retryable=error.retryable,
                    retry_delay_seconds=self._retry_delay_seconds,
                )
                return WorkerProcessResult(
                    status="failed",
                    run_item_id=failed_item.id,
                    error_message=str(error),
                )
            except Exception as error:
                failed_item = repository.record_model_error(
                    run_item_id=item.id,
                    error_type="worker_error",
                    error_message=str(error),
                    retryable=False,
                    retry_delay_seconds=0,
                )
                return WorkerProcessResult(
                    status="failed",
                    run_item_id=failed_item.id,
                    error_message=str(error),
                )

            raw_response = repository.record_raw_response(run_item_id=item.id, response=response)
            self._rate_limit_gate.record_execution(
                provider_key=request.provider_key,
                model_id=request.model_id,
                policy=rate_limit_policy,
            )
            return WorkerProcessResult(
                status="processed",
                run_item_id=item.id,
                raw_response_id=raw_response.id,
            )

    async def process_batch(self, *, max_items: int) -> list[WorkerProcessResult]:
        if max_items < 1:
            return []

        results: list[WorkerProcessResult] = []
        for _ in range(max_items):
            result = await self.process_one()
            results.append(result)
            if result.status == "idle":
                break
        return results


def _rate_limit_policy_from_request(request: AIRequest) -> RateLimitPolicy:
    rate_limit_policy = request.metadata.get("rate_limit_policy")
    policy_mapping: Mapping[str, object] | None = None
    if isinstance(rate_limit_policy, Mapping):
        mapping = cast(Mapping[object, object], rate_limit_policy)
        policy_mapping = {str(key): value for key, value in mapping.items()}
    return rate_limit_policy_from_mapping(
        policy_mapping,
        provider_id=request.provider_key,
        model_id=request.model_id,
    )
