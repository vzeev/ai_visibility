from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InsightsDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ExtractionRequest(BaseModel):
    extraction_version: str = Field(default="deterministic-v1", min_length=1, max_length=100)


class ExtractedMention(InsightsDto):
    id: UUID
    extraction_run_id: UUID
    entity_type: str
    entity_name: str
    mention_text: str
    sentiment_label: str
    confidence: Decimal
    evidence_json: dict[str, Any]


class ExtractedCitation(InsightsDto):
    id: UUID
    extraction_run_id: UUID
    url: str
    domain: str
    title: str | None = None
    evidence_json: dict[str, Any]


class ExtractionRun(InsightsDto):
    id: UUID
    raw_response_id: UUID
    extraction_version: str
    status: str
    completed_at: datetime | None = None
    mentions: list[ExtractedMention]
    citations: list[ExtractedCitation]


class VisibilitySummary(InsightsDto):
    id: UUID
    brand_id: UUID
    run_batch_id: UUID
    extraction_version: str
    summary_json: dict[str, Any]


class BatchExtractionResponse(BaseModel):
    run_batch_id: UUID
    extraction_version: str
    raw_response_count: int
    extraction_run_count: int
    summary: VisibilitySummary
