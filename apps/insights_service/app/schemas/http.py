from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class VisibilitySummary(BaseModel):
    id: UUID
    summary_json: dict[str, object]
