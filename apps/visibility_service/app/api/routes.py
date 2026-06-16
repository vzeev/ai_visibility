from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, status

from apps.visibility_service.app.schemas.http import (
    QueueState,
    RawResponsePage,
    RunBatch,
)

router = APIRouter()


@router.post("/runs", response_model=RunBatch, status_code=status.HTTP_202_ACCEPTED)
def create_run() -> RunBatch:
    return RunBatch(id=uuid4(), status="queued")


@router.get("/runs", response_model=list[RunBatch])
def list_runs() -> list[RunBatch]:
    return []


@router.get("/queue", response_model=QueueState)
def get_queue_state() -> QueueState:
    return QueueState(pending=0, running=0, succeeded=0, failed=0, throttled=0)


@router.get("/raw-responses", response_model=RawResponsePage)
def list_raw_responses(q: str | None = None, limit: int = 50, offset: int = 0) -> RawResponsePage:
    return RawResponsePage(items=[], total=0, query=q, limit=limit, offset=offset)
