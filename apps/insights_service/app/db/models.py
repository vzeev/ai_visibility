from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Numeric, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ConfigBrand(Base):
    __tablename__ = "brands"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    website_url: Mapped[str | None] = mapped_column(Text)


class ConfigBrandAlias(Base):
    __tablename__ = "brand_aliases"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    brand_id: Mapped[UUID] = mapped_column(nullable=False)
    alias: Mapped[str] = mapped_column(Text, nullable=False)


class ConfigCompetitor(Base):
    __tablename__ = "competitors"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    brand_id: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    website_url: Mapped[str | None] = mapped_column(Text)


class VisibilityRunBatch(Base):
    __tablename__ = "run_batches"
    __table_args__ = {"schema": "visibility"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    brand_id: Mapped[UUID] = mapped_column(nullable=False)
    prompt_set_id: Mapped[UUID] = mapped_column(nullable=False)
    config_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)


class VisibilityRunItem(Base):
    __tablename__ = "run_items"
    __table_args__ = {"schema": "visibility"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    run_batch_id: Mapped[UUID] = mapped_column(nullable=False)
    provider_id: Mapped[UUID] = mapped_column(nullable=False)
    model_registry_id: Mapped[UUID] = mapped_column(nullable=False)


class VisibilityRawResponse(Base):
    __tablename__ = "raw_responses"
    __table_args__ = {"schema": "visibility"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    run_item_id: Mapped[UUID] = mapped_column(nullable=False)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    provider_id: Mapped[UUID] = mapped_column(nullable=False)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    provider_response_id: Mapped[str | None] = mapped_column(Text)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[str] = mapped_column(Text, nullable=False)
    raw_request_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    raw_response_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    usage_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    latency_ms: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ExtractionRun(Base):
    __tablename__ = "extraction_runs"
    __table_args__ = {"schema": "insights"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    raw_response_id: Mapped[UUID] = mapped_column(nullable=False)
    extraction_version: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ExtractedMention(Base):
    __tablename__ = "extracted_mentions"
    __table_args__ = {"schema": "insights"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    extraction_run_id: Mapped[UUID] = mapped_column(nullable=False)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_name: Mapped[str] = mapped_column(Text, nullable=False)
    mention_text: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment_label: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class ExtractedCitation(Base):
    __tablename__ = "extracted_citations"
    __table_args__ = {"schema": "insights"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    extraction_run_id: Mapped[UUID] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(Text)
    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class VisibilitySummary(Base):
    __tablename__ = "visibility_summaries"
    __table_args__ = {"schema": "insights"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    brand_id: Mapped[UUID] = mapped_column(nullable=False)
    run_batch_id: Mapped[UUID] = mapped_column(nullable=False)
    extraction_version: Mapped[str] = mapped_column(Text, nullable=False)
    summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
