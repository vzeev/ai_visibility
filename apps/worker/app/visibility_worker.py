from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from apps.shared.ai.provider import AIProviderAdapter, AIProviderError, FakeAIProviderAdapter
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
        lease_seconds: int = 300,
        retry_delay_seconds: int = 0,
    ) -> None:
        self._session_factory = session_factory
        self._fallback_adapter: AIProviderAdapter = FakeAIProviderAdapter()
        self._adapters: dict[str, AIProviderAdapter] = dict(adapters or {})
        self._adapters.setdefault(self._fallback_adapter.provider_key, self._fallback_adapter)
        self._lease_seconds = lease_seconds
        self._retry_delay_seconds = retry_delay_seconds

    async def process_one(self) -> WorkerProcessResult:
        with self._session_factory() as session:
            repository = VisibilityRepository(session)
            item = repository.claim_next_item(lease_seconds=self._lease_seconds)
            if item is None:
                return WorkerProcessResult(status="idle")

            request = repository.build_ai_request(item)
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
