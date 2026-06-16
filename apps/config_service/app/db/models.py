from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
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


class Brand(Base, TimestampMixin):
    __tablename__ = "brands"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    website_url: Mapped[str | None] = mapped_column(Text)


class BrandAlias(Base):
    __tablename__ = "brand_aliases"
    __table_args__ = (
        UniqueConstraint("brand_id", "alias"),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("config.brands.id"), nullable=False)
    alias: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Competitor(Base):
    __tablename__ = "competitors"
    __table_args__ = (
        UniqueConstraint("brand_id", "name"),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("config.brands.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    website_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("brand_id", "name"),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("config.brands.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class PromptSet(Base, TimestampMixin):
    __tablename__ = "prompt_sets"
    __table_args__ = (
        UniqueConstraint("brand_id", "name"),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("config.brands.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Prompt(Base, TimestampMixin):
    __tablename__ = "prompts"
    __table_args__ = (
        UniqueConstraint("prompt_set_id", "name"),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    prompt_set_id: Mapped[UUID] = mapped_column(ForeignKey("config.prompt_sets.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (
        UniqueConstraint("prompt_id", "version"),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("config.prompts.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Provider(Base):
    __tablename__ = "providers"
    __table_args__ = {"schema": "config"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    provider_kind: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class ProviderCredential(Base, TimestampMixin):
    __tablename__ = "provider_credentials"
    __table_args__ = (
        UniqueConstraint("provider_id", "label"),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider_id: Mapped[UUID] = mapped_column(ForeignKey("config.providers.id"), nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    secret_ref: Mapped[str | None] = mapped_column(Text)
    redacted_fingerprint: Mapped[str] = mapped_column(Text, nullable=False)
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RateLimitPolicy(Base, TimestampMixin):
    __tablename__ = "rate_limit_policies"
    __table_args__ = (
        UniqueConstraint("provider_id", "model_id"),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider_id: Mapped[UUID] = mapped_column(ForeignKey("config.providers.id"), nullable=False)
    model_id: Mapped[str | None] = mapped_column(Text)
    max_concurrent_requests: Mapped[int] = mapped_column(Integer, nullable=False)
    requests_per_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_per_minute: Mapped[int | None] = mapped_column(Integer)
    min_delay_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    backoff_base_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=1_000)
    backoff_max_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=60_000)


class ModelRegistry(Base, TimestampMixin):
    __tablename__ = "model_registry"
    __table_args__ = (
        UniqueConstraint("provider_id", "model_id"),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider_id: Mapped[UUID] = mapped_column(ForeignKey("config.providers.id"), nullable=False)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    owned_by: Mapped[str | None] = mapped_column(Text)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enabled_for_visibility: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rate_limit_policy_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("config.rate_limit_policies.id")
    )
    capability_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
