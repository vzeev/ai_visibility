from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.shared.ai.provider import AIResponse
from apps.visibility_service.app.db.repository import VisibilityRepository
from apps.visibility_service.app.db.session import get_session
from apps.visibility_service.app.schemas.http import (
    ClaimRunItemRequest,
    CompleteRunItemRequest,
    CreateRunRequest,
    FailRunItemRequest,
    QueueState,
    RawResponseItem,
    RawResponsePage,
    RunBatch,
    RunItem,
)

router = APIRouter()


def get_repository(session: Session = Depends(get_session)) -> VisibilityRepository:
    return VisibilityRepository(session)


@router.post("/runs", response_model=RunBatch, status_code=status.HTTP_202_ACCEPTED)
def create_run(
    payload: CreateRunRequest,
    repository: VisibilityRepository = Depends(get_repository),
) -> RunBatch:
    created = repository.create_run(
        brand_id=payload.brand_id,
        prompt_set_id=payload.prompt_set_id,
        sample_count=payload.sample_count,
        max_attempts=payload.max_attempts,
    )
    return RunBatch.model_validate(created.batch).model_copy(
        update={"item_count": created.item_count}
    )


@router.get("/runs", response_model=list[RunBatch])
def list_runs(repository: VisibilityRepository = Depends(get_repository)) -> list[RunBatch]:
    return [RunBatch.model_validate(run) for run in repository.list_runs()]


@router.get("/queue", response_model=QueueState)
def get_queue_state(repository: VisibilityRepository = Depends(get_repository)) -> QueueState:
    return QueueState(**repository.queue_state())


@router.post("/queue/claim", response_model=RunItem | None)
def claim_next_item(
    payload: ClaimRunItemRequest,
    repository: VisibilityRepository = Depends(get_repository),
) -> RunItem | None:
    item = repository.claim_next_item(lease_seconds=payload.lease_seconds)
    if item is None:
        return None
    return RunItem.model_validate(item)


@router.post("/queue/items/{run_item_id}/complete", response_model=RawResponseItem)
def complete_run_item(
    run_item_id: str,
    payload: CompleteRunItemRequest,
    repository: VisibilityRepository = Depends(get_repository),
) -> RawResponseItem:
    raw_response = repository.record_raw_response(
        run_item_id=_uuid(run_item_id),
        response=AIResponse(
            provider_key=payload.provider_key,
            model_id=payload.model_id,
            output_text=payload.output_text,
            raw_request_json=payload.raw_request_json,
            raw_response_json=payload.raw_response_json,
            usage_json=payload.usage_json,
            latency_ms=payload.latency_ms,
            provider_response_id=payload.provider_response_id,
        ),
    )
    return RawResponseItem.model_validate(raw_response)


@router.post("/queue/items/{run_item_id}/fail", response_model=RunItem)
def fail_run_item(
    run_item_id: str,
    payload: FailRunItemRequest,
    repository: VisibilityRepository = Depends(get_repository),
) -> RunItem:
    item = repository.record_model_error(
        run_item_id=_uuid(run_item_id),
        error_type=payload.error_type,
        error_message=payload.error_message,
        retryable=payload.retryable,
        retry_delay_seconds=payload.retry_delay_seconds,
    )
    return RunItem.model_validate(item)


@router.get("/raw-responses", response_model=RawResponsePage)
def list_raw_responses(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    repository: VisibilityRepository = Depends(get_repository),
) -> RawResponsePage:
    page = repository.list_raw_responses(q=q, limit=limit, offset=offset)
    return RawResponsePage(
        items=[RawResponseItem.model_validate(item) for item in page.items],
        total=page.total,
        query=q,
        limit=limit,
        offset=offset,
    )


@router.get("/raw-responses/{raw_response_id}", response_model=RawResponseItem)
def get_raw_response(
    raw_response_id: str,
    repository: VisibilityRepository = Depends(get_repository),
) -> RawResponseItem:
    return RawResponseItem.model_validate(repository.get_raw_response(_uuid(raw_response_id)))


def _uuid(value: str) -> UUID:
    return UUID(value)
