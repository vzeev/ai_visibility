from __future__ import annotations

from fastapi import APIRouter

from apps.insights_service.app.schemas.http import VisibilitySummary

router = APIRouter()


@router.get("/summaries", response_model=list[VisibilitySummary])
def list_summaries() -> list[VisibilitySummary]:
    return []
