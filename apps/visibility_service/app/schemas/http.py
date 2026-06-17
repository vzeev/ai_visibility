from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VisibilityDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CreateRunRequest(BaseModel):
    brand_id: UUID
    prompt_set_id: UUID
    sample_count: int = Field(default=1, ge=1, le=10)
    max_attempts: int = Field(default=3, ge=1, le=10)


class RunBatch(VisibilityDto):
    id: UUID
    brand_id: UUID
    prompt_set_id: UUID
    status: str
    created_at: datetime
    item_count: int | None = None


class QueueState(BaseModel):
    pending: int = Field(ge=0)
    running: int = Field(ge=0)
    succeeded: int = Field(ge=0)
    failed: int = Field(ge=0)
    throttled: int = Field(ge=0)


class ClaimRunItemRequest(BaseModel):
    lease_seconds: int = Field(default=300, ge=1, le=3600)


class RunItem(VisibilityDto):
    id: UUID
    run_batch_id: UUID
    prompt_version_id: UUID
    provider_id: UUID
    model_registry_id: UUID
    sample_index: int
    idempotency_key: str
    status: str
    attempt_count: int
    max_attempts: int
    last_error: str | None = None


class CompleteRunItemRequest(BaseModel):
    provider_key: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    output_text: str = Field(min_length=1)
    raw_request_json: dict[str, Any]
    raw_response_json: dict[str, Any]
    usage_json: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int = Field(ge=0)
    provider_response_id: str | None = None


class FailRunItemRequest(BaseModel):
    error_type: str = Field(min_length=1)
    error_message: str = Field(min_length=1)
    retryable: bool
    retry_delay_seconds: int = Field(default=0, ge=0, le=3600)


class RawResponseItem(VisibilityDto):
    id: UUID
    run_item_id: UUID
    idempotency_key: str
    provider_id: UUID
    model_id: str
    provider_response_id: str | None = None
    prompt_text: str
    output_text: str
    raw_request_json: dict[str, Any]
    raw_response_json: dict[str, Any]
    usage_json: dict[str, Any]
    latency_ms: int
    status: str


class RawResponsePage(BaseModel):
    items: list[RawResponseItem]
    total: int
    query: str | None = None
    limit: int
    offset: int
