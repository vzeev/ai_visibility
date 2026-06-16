from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, SecretStr


class Brand(BaseModel):
    id: UUID
    name: str
    website_url: str | None = None


class CreateBrandRequest(BaseModel):
    name: str
    website_url: str | None = None


class PromptVersion(BaseModel):
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
    name: str
    intent: str
    prompt_text: str


class CreateProviderCredentialRequest(BaseModel):
    provider_id: UUID
    label: str
    token: SecretStr = Field(json_schema_extra={"writeOnly": True})


class ProviderCredential(BaseModel):
    id: UUID
    provider_id: UUID
    label: str
    status: str
    redacted_fingerprint: str
    last_tested_at: datetime | None = None


class RateLimitPolicyResponse(BaseModel):
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
