from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ConfigBrand(Base):
    __tablename__ = "brands"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    website_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ConfigPromptSet(Base):
    __tablename__ = "prompt_sets"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    brand_id: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ConfigPrompt(Base):
    __tablename__ = "prompts"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    prompt_set_id: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ConfigPromptVersion(Base):
    __tablename__ = "prompt_versions"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    prompt_id: Mapped[UUID] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ConfigProvider(Base):
    __tablename__ = "providers"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    provider_key: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    provider_kind: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ConfigModelRegistry(Base):
    __tablename__ = "model_registry"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    provider_id: Mapped[UUID] = mapped_column(nullable=False)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    owned_by: Mapped[str | None] = mapped_column(Text)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    enabled_for_visibility: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rate_limit_policy_id: Mapped[UUID | None] = mapped_column()
    capability_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class RunBatch(Base):
    __tablename__ = "run_batches"
    __table_args__ = {"schema": "visibility"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    brand_id: Mapped[UUID] = mapped_column(nullable=False)
    prompt_set_id: Mapped[UUID] = mapped_column(nullable=False)
    config_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RunItem(Base):
    __tablename__ = "run_items"
    __table_args__ = {"schema": "visibility"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    run_batch_id: Mapped[UUID] = mapped_column(
        ForeignKey("visibility.run_batches.id"),
        nullable=False,
    )
    prompt_version_id: Mapped[UUID] = mapped_column(nullable=False)
    provider_id: Mapped[UUID] = mapped_column(nullable=False)
    model_registry_id: Mapped[UUID] = mapped_column(nullable=False)
    sample_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class RawResponse(Base):
    __tablename__ = "raw_responses"
    __table_args__ = {"schema": "visibility"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    run_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("visibility.run_items.id"),
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    provider_id: Mapped[UUID] = mapped_column(nullable=False)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    provider_response_id: Mapped[str | None] = mapped_column(Text)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[str] = mapped_column(Text, nullable=False)
    raw_request_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    raw_response_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    usage_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class ModelError(Base):
    __tablename__ = "model_errors"
    __table_args__ = {"schema": "visibility"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    run_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("visibility.run_items.id"),
        nullable=False,
    )
    provider_id: Mapped[UUID] = mapped_column(nullable=False)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    error_type: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    retryable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
