from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class ConfigDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Brand(ConfigDto):
    id: UUID
    name: str
    website_url: str | None = None


class CreateBrandRequest(BaseModel):
    name: str = Field(min_length=1)
    website_url: str | None = None


class Competitor(ConfigDto):
    id: UUID
    brand_id: UUID
    name: str
    website_url: str | None = None


class CreateCompetitorRequest(BaseModel):
    name: str = Field(min_length=1)
    website_url: str | None = None


class Product(ConfigDto):
    id: UUID
    brand_id: UUID
    name: str
    description: str


class CreateProductRequest(BaseModel):
    name: str = Field(min_length=1)
    description: str = ""


class PromptSet(ConfigDto):
    id: UUID
    brand_id: UUID
    name: str
    description: str
    is_active: bool


class CreatePromptSetRequest(BaseModel):
    brand_id: UUID
    name: str = Field(min_length=1)
    description: str = ""
    is_active: bool = True


class PromptVersion(ConfigDto):
    id: UUID
    version: int
    prompt_text: str


class Prompt(BaseModel):
    id: UUID
    prompt_set_id: UUID
    name: str
    intent: str
    active_version: PromptVersion


class CreatePromptRequest(BaseModel):
    prompt_set_id: UUID
    name: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    prompt_text: str = Field(min_length=1)


class CreatePromptVersionRequest(BaseModel):
    prompt_text: str = Field(min_length=1)


class Provider(ConfigDto):
    id: UUID
    provider_key: str
    display_name: str
    provider_kind: str
    is_active: bool


class CreateProviderRequest(BaseModel):
    provider_key: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    provider_kind: str = Field(min_length=1)
    is_active: bool = True


class CreateProviderCredentialRequest(BaseModel):
    provider_id: UUID
    label: str = Field(min_length=1)
    token: SecretStr = Field(json_schema_extra={"writeOnly": True})


class ProviderCredential(ConfigDto):
    id: UUID
    provider_id: UUID
    label: str
    status: str
    redacted_fingerprint: str
    last_tested_at: datetime | None = None


class CreateRateLimitPolicyRequest(BaseModel):
    provider_id: UUID
    model_id: str | None = None
    max_concurrent_requests: int = Field(ge=1)
    requests_per_minute: int = Field(ge=1)
    tokens_per_minute: int | None = Field(default=None, ge=1)
    min_delay_ms: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0)
    backoff_base_ms: int = Field(default=1_000, ge=0)
    backoff_max_ms: int = Field(default=60_000, ge=0)


class RateLimitPolicyResponse(ConfigDto):
    id: UUID | None = None
    provider_id: UUID
    model_id: str | None = None
    max_concurrent_requests: int
    requests_per_minute: int
    tokens_per_minute: int | None = None
    min_delay_ms: int = 0
    max_retries: int = 3
    backoff_base_ms: int = 1_000
    backoff_max_ms: int = 60_000


class ModelRegistry(ConfigDto):
    id: UUID
    provider_id: UUID
    model_id: str
    display_name: str
    owned_by: str | None = None
    is_available: bool
    enabled_for_visibility: bool
    rate_limit_policy_id: UUID | None = None
    capability_json: dict[str, Any]


class CreateModelRegistryRequest(BaseModel):
    provider_id: UUID
    model_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    owned_by: str | None = None
    is_available: bool = True
    enabled_for_visibility: bool = False
    rate_limit_policy_id: UUID | None = None
    capability_json: dict[str, Any] = Field(default_factory=dict)


class UpdateModelVisibilityRequest(BaseModel):
    enabled_for_visibility: bool


class ModelSyncResponse(BaseModel):
    provider_id: UUID
    provider_key: str
    discovered_count: int
    created_count: int
    updated_count: int
    unavailable_count: int
    models: list[ModelRegistry]
