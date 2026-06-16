from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.config_service.app.db.repository import ConfigRepository, PromptRecord
from apps.config_service.app.db.session import get_session
from apps.config_service.app.schemas.http import (
    Brand,
    Competitor,
    CreateBrandRequest,
    CreateCompetitorRequest,
    CreateModelRegistryRequest,
    CreateProductRequest,
    CreatePromptRequest,
    CreatePromptSetRequest,
    CreatePromptVersionRequest,
    CreateProviderCredentialRequest,
    CreateProviderRequest,
    CreateRateLimitPolicyRequest,
    ModelRegistry,
    Product,
    Prompt,
    PromptSet,
    PromptVersion,
    Provider,
    ProviderCredential,
    RateLimitPolicyResponse,
)

router = APIRouter()


def get_repository(session: Session = Depends(get_session)) -> ConfigRepository:
    return ConfigRepository(session)


@router.get("/brands", response_model=list[Brand])
def list_brands(repository: ConfigRepository = Depends(get_repository)) -> list[Brand]:
    return [Brand.model_validate(brand) for brand in repository.list_brands()]


@router.post("/brands", response_model=Brand, status_code=status.HTTP_201_CREATED)
def create_brand(
    payload: CreateBrandRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> Brand:
    brand = repository.create_brand(name=payload.name, website_url=payload.website_url)
    return Brand.model_validate(brand)


@router.get("/brands/{brand_id}/competitors", response_model=list[Competitor])
def list_competitors(
    brand_id: UUID,
    repository: ConfigRepository = Depends(get_repository),
) -> list[Competitor]:
    return [
        Competitor.model_validate(competitor)
        for competitor in repository.list_competitors(brand_id)
    ]


@router.post(
    "/brands/{brand_id}/competitors",
    response_model=Competitor,
    status_code=status.HTTP_201_CREATED,
)
def create_competitor(
    brand_id: UUID,
    payload: CreateCompetitorRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> Competitor:
    competitor = repository.create_competitor(
        brand_id=brand_id,
        name=payload.name,
        website_url=payload.website_url,
    )
    return Competitor.model_validate(competitor)


@router.get("/brands/{brand_id}/products", response_model=list[Product])
def list_products(
    brand_id: UUID,
    repository: ConfigRepository = Depends(get_repository),
) -> list[Product]:
    return [Product.model_validate(product) for product in repository.list_products(brand_id)]


@router.post(
    "/brands/{brand_id}/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    brand_id: UUID,
    payload: CreateProductRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> Product:
    product = repository.create_product(
        brand_id=brand_id,
        name=payload.name,
        description=payload.description,
    )
    return Product.model_validate(product)


@router.get("/prompt-sets", response_model=list[PromptSet])
def list_prompt_sets(
    brand_id: UUID | None = None,
    repository: ConfigRepository = Depends(get_repository),
) -> list[PromptSet]:
    return [
        PromptSet.model_validate(prompt_set) for prompt_set in repository.list_prompt_sets(brand_id)
    ]


@router.post("/prompt-sets", response_model=PromptSet, status_code=status.HTTP_201_CREATED)
def create_prompt_set(
    payload: CreatePromptSetRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> PromptSet:
    prompt_set = repository.create_prompt_set(
        brand_id=payload.brand_id,
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    return PromptSet.model_validate(prompt_set)


@router.get("/prompts", response_model=list[Prompt])
def list_prompts(
    prompt_set_id: UUID | None = None,
    repository: ConfigRepository = Depends(get_repository),
) -> list[Prompt]:
    return [_prompt_response(record) for record in repository.list_prompts(prompt_set_id)]


@router.post("/prompts", response_model=Prompt, status_code=status.HTTP_201_CREATED)
def create_prompt(
    payload: CreatePromptRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> Prompt:
    record = repository.create_prompt(
        prompt_set_id=payload.prompt_set_id,
        name=payload.name,
        intent=payload.intent,
        prompt_text=payload.prompt_text,
    )
    return _prompt_response(record)


@router.post(
    "/prompts/{prompt_id}/versions",
    response_model=Prompt,
    status_code=status.HTTP_201_CREATED,
)
def create_prompt_version(
    prompt_id: UUID,
    payload: CreatePromptVersionRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> Prompt:
    return _prompt_response(
        repository.create_prompt_version(prompt_id=prompt_id, prompt_text=payload.prompt_text)
    )


@router.get("/providers", response_model=list[Provider])
def list_providers(repository: ConfigRepository = Depends(get_repository)) -> list[Provider]:
    return [Provider.model_validate(provider) for provider in repository.list_providers()]


@router.post("/providers", response_model=Provider, status_code=status.HTTP_201_CREATED)
def create_provider(
    payload: CreateProviderRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> Provider:
    provider = repository.create_provider(
        provider_key=payload.provider_key,
        display_name=payload.display_name,
        provider_kind=payload.provider_kind,
        is_active=payload.is_active,
    )
    return Provider.model_validate(provider)


@router.get("/provider-credentials", response_model=list[ProviderCredential])
def list_provider_credentials(
    repository: ConfigRepository = Depends(get_repository),
) -> list[ProviderCredential]:
    return [
        ProviderCredential.model_validate(credential)
        for credential in repository.list_provider_credentials()
    ]


@router.post(
    "/provider-credentials",
    response_model=ProviderCredential,
    status_code=status.HTTP_201_CREATED,
)
def create_provider_credential(
    payload: CreateProviderCredentialRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> ProviderCredential:
    credential = repository.create_provider_credential(
        provider_id=payload.provider_id,
        label=payload.label,
        token=payload.token.get_secret_value(),
    )
    return ProviderCredential.model_validate(credential)


@router.get("/rate-limits", response_model=list[RateLimitPolicyResponse])
def list_rate_limits(
    repository: ConfigRepository = Depends(get_repository),
) -> list[RateLimitPolicyResponse]:
    return [
        RateLimitPolicyResponse.model_validate(policy) for policy in repository.list_rate_limits()
    ]


@router.post(
    "/rate-limits",
    response_model=RateLimitPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rate_limit(
    payload: CreateRateLimitPolicyRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> RateLimitPolicyResponse:
    policy = repository.create_rate_limit(
        provider_id=payload.provider_id,
        model_id=payload.model_id,
        max_concurrent_requests=payload.max_concurrent_requests,
        requests_per_minute=payload.requests_per_minute,
        tokens_per_minute=payload.tokens_per_minute,
        min_delay_ms=payload.min_delay_ms,
        max_retries=payload.max_retries,
        backoff_base_ms=payload.backoff_base_ms,
        backoff_max_ms=payload.backoff_max_ms,
    )
    return RateLimitPolicyResponse.model_validate(policy)


@router.get("/models", response_model=list[ModelRegistry])
def list_models(
    provider_id: UUID | None = None,
    repository: ConfigRepository = Depends(get_repository),
) -> list[ModelRegistry]:
    return [ModelRegistry.model_validate(model) for model in repository.list_models(provider_id)]


@router.post("/models", response_model=ModelRegistry, status_code=status.HTTP_201_CREATED)
def create_model(
    payload: CreateModelRegistryRequest,
    repository: ConfigRepository = Depends(get_repository),
) -> ModelRegistry:
    model = repository.create_model(
        provider_id=payload.provider_id,
        model_id=payload.model_id,
        display_name=payload.display_name,
        owned_by=payload.owned_by,
        is_available=payload.is_available,
        enabled_for_visibility=payload.enabled_for_visibility,
        rate_limit_policy_id=payload.rate_limit_policy_id,
        capability_json=payload.capability_json,
    )
    return ModelRegistry.model_validate(model)


def _prompt_response(record: PromptRecord) -> Prompt:
    return Prompt(
        id=record.prompt.id,
        prompt_set_id=record.prompt.prompt_set_id,
        name=record.prompt.name,
        intent=record.prompt.intent,
        active_version=PromptVersion.model_validate(record.active_version),
    )
