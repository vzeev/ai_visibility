from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.insights_service.app.db.repository import (
    BatchExtractionResult,
    ExtractionRunRecord,
    InsightsRepository,
    NotFoundError,
)
from apps.insights_service.app.db.session import get_session
from apps.insights_service.app.schemas.http import (
    BatchExtractionResponse,
    ExtractedCitation,
    ExtractedMention,
    ExtractionRequest,
    ExtractionRun,
    VisibilitySummary,
)

router = APIRouter()


def get_repository(session: Session = Depends(get_session)) -> InsightsRepository:
    return InsightsRepository(session)


@router.post(
    "/extractions/raw-responses/{raw_response_id}",
    response_model=ExtractionRun,
    status_code=status.HTTP_202_ACCEPTED,
)
def extract_raw_response(
    raw_response_id: UUID,
    payload: ExtractionRequest,
    repository: InsightsRepository = Depends(get_repository),
) -> ExtractionRun:
    try:
        record = repository.extract_raw_response(
            raw_response_id=raw_response_id,
            extraction_version=payload.extraction_version,
        )
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return _run_response(record)


@router.post(
    "/extractions/run-batches/{run_batch_id}",
    response_model=BatchExtractionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def extract_run_batch(
    run_batch_id: UUID,
    payload: ExtractionRequest,
    repository: InsightsRepository = Depends(get_repository),
) -> BatchExtractionResponse:
    try:
        result = repository.extract_run_batch(
            run_batch_id=run_batch_id,
            extraction_version=payload.extraction_version,
        )
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return _batch_response(result)


@router.get("/extraction-runs/{extraction_run_id}", response_model=ExtractionRun)
def get_extraction_run(
    extraction_run_id: UUID,
    repository: InsightsRepository = Depends(get_repository),
) -> ExtractionRun:
    try:
        return _run_response(repository.get_extraction_run(extraction_run_id))
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/summaries", response_model=list[VisibilitySummary])
def list_summaries(
    brand_id: UUID | None = None,
    run_batch_id: UUID | None = None,
    extraction_version: str | None = None,
    repository: InsightsRepository = Depends(get_repository),
) -> list[VisibilitySummary]:
    return [
        VisibilitySummary.model_validate(summary)
        for summary in repository.list_summaries(
            brand_id=brand_id,
            run_batch_id=run_batch_id,
            extraction_version=extraction_version,
        )
    ]


def _run_response(record: ExtractionRunRecord) -> ExtractionRun:
    return ExtractionRun(
        id=record.run.id,
        raw_response_id=record.run.raw_response_id,
        extraction_version=record.run.extraction_version,
        status=record.run.status,
        completed_at=record.run.completed_at,
        mentions=[ExtractedMention.model_validate(mention) for mention in record.mentions],
        citations=[ExtractedCitation.model_validate(citation) for citation in record.citations],
    )


def _batch_response(result: BatchExtractionResult) -> BatchExtractionResponse:
    return BatchExtractionResponse(
        run_batch_id=result.run_batch_id,
        extraction_version=result.extraction_version,
        raw_response_count=result.raw_response_count,
        extraction_run_count=len(result.extraction_runs),
        summary=VisibilitySummary.model_validate(result.summary),
    )
