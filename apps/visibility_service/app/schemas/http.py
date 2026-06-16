from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class RunBatch(BaseModel):
    id: UUID
    status: str


class QueueState(BaseModel):
    pending: int = Field(ge=0)
    running: int = Field(ge=0)
    succeeded: int = Field(ge=0)
    failed: int = Field(ge=0)
    throttled: int = Field(ge=0)


class RawResponsePage(BaseModel):
    items: list[dict[str, object]]
    total: int
    query: str | None = None
    limit: int
    offset: int
