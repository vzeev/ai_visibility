from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, status

from apps.config_service.app.schemas.http import (
    Brand,
    CreateBrandRequest,
    CreatePromptRequest,
    CreateProviderCredentialRequest,
    Prompt,
    PromptVersion,
    ProviderCredential,
    RateLimitPolicyResponse,
)
from apps.shared.ai.secrets import redacted_fingerprint

router = APIRouter()


@router.get("/brands", response_model=list[Brand])
def list_brands() -> list[Brand]:
    return []


@router.post("/brands", response_model=Brand, status_code=status.HTTP_201_CREATED)
def create_brand(payload: CreateBrandRequest) -> Brand:
    return Brand(id=uuid4(), name=payload.name, website_url=payload.website_url)


@router.get("/prompts", response_model=list[Prompt])
def list_prompts() -> list[Prompt]:
    return []


@router.post("/prompts", response_model=Prompt, status_code=status.HTTP_201_CREATED)
def create_prompt(payload: CreatePromptRequest) -> Prompt:
    prompt_id = uuid4()
    return Prompt(
        id=prompt_id,
        prompt_set_id=payload.prompt_set_id,
        name=payload.name,
        intent=payload.intent,
        active_version=PromptVersion(id=uuid4(), version=1, prompt_text=payload.prompt_text),
    )


@router.post(
    "/provider-credentials",
    response_model=ProviderCredential,
    status_code=status.HTTP_201_CREATED,
)
def create_provider_credential(payload: CreateProviderCredentialRequest) -> ProviderCredential:
    return ProviderCredential(
        id=uuid4(),
        provider_id=payload.provider_id,
        label=payload.label,
        status="active",
        redacted_fingerprint=redacted_fingerprint(payload.token.get_secret_value()),
        last_tested_at=None,
    )


@router.get("/rate-limits", response_model=list[RateLimitPolicyResponse])
def list_rate_limits() -> list[RateLimitPolicyResponse]:
    return []


@router.post(
    "/rate-limits",
    response_model=RateLimitPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rate_limit(payload: RateLimitPolicyResponse) -> RateLimitPolicyResponse:
    return payload
