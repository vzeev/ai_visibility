from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.config_service.app.db import models
from apps.config_service.app.services.secrets import build_local_secret_ref
from apps.shared.ai.model_discovery import DiscoveredModel
from apps.shared.ai.secrets import redacted_fingerprint


class ConfigRepositoryError(Exception):
    pass


class NotFoundError(ConfigRepositoryError):
    pass


class ConflictError(ConfigRepositoryError):
    pass


@dataclass(frozen=True)
class PromptRecord:
    prompt: models.Prompt
    active_version: models.PromptVersion


@dataclass(frozen=True)
class ModelSyncResult:
    created_count: int
    updated_count: int
    unavailable_count: int
    models: list[models.ModelRegistry]


class ConfigRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_brands(self) -> list[models.Brand]:
        return self._list(select(models.Brand).order_by(models.Brand.name))

    def create_brand(self, *, name: str, website_url: str | None) -> models.Brand:
        brand = models.Brand(name=name, website_url=website_url)
        return self._add_one(brand, conflict_message=f"brand already exists: {name}")

    def list_competitors(self, brand_id: UUID) -> list[models.Competitor]:
        self._require_brand(brand_id)
        return self._list(
            select(models.Competitor)
            .where(models.Competitor.brand_id == brand_id)
            .order_by(models.Competitor.name)
        )

    def create_competitor(
        self,
        *,
        brand_id: UUID,
        name: str,
        website_url: str | None,
    ) -> models.Competitor:
        self._require_brand(brand_id)
        competitor = models.Competitor(brand_id=brand_id, name=name, website_url=website_url)
        return self._add_one(
            competitor,
            conflict_message=f"competitor already exists for brand: {name}",
        )

    def list_products(self, brand_id: UUID) -> list[models.Product]:
        self._require_brand(brand_id)
        return self._list(
            select(models.Product)
            .where(models.Product.brand_id == brand_id)
            .order_by(models.Product.name)
        )

    def create_product(
        self,
        *,
        brand_id: UUID,
        name: str,
        description: str,
    ) -> models.Product:
        self._require_brand(brand_id)
        product = models.Product(brand_id=brand_id, name=name, description=description)
        return self._add_one(product, conflict_message=f"product already exists for brand: {name}")

    def list_prompt_sets(self, brand_id: UUID | None = None) -> list[models.PromptSet]:
        statement = select(models.PromptSet).order_by(models.PromptSet.name)
        if brand_id is not None:
            self._require_brand(brand_id)
            statement = statement.where(models.PromptSet.brand_id == brand_id)
        return self._list(statement)

    def create_prompt_set(
        self,
        *,
        brand_id: UUID,
        name: str,
        description: str,
        is_active: bool,
    ) -> models.PromptSet:
        self._require_brand(brand_id)
        prompt_set = models.PromptSet(
            brand_id=brand_id,
            name=name,
            description=description,
            is_active=is_active,
        )
        return self._add_one(
            prompt_set,
            conflict_message=f"prompt set already exists for brand: {name}",
        )

    def list_prompts(self, prompt_set_id: UUID | None = None) -> list[PromptRecord]:
        statement = select(models.Prompt).order_by(models.Prompt.name)
        if prompt_set_id is not None:
            self._require_prompt_set(prompt_set_id)
            statement = statement.where(models.Prompt.prompt_set_id == prompt_set_id)
        return [self._prompt_record(prompt) for prompt in self._list(statement)]

    def create_prompt(
        self,
        *,
        prompt_set_id: UUID,
        name: str,
        intent: str,
        prompt_text: str,
    ) -> PromptRecord:
        self._require_prompt_set(prompt_set_id)
        prompt = models.Prompt(prompt_set_id=prompt_set_id, name=name, intent=intent)
        self._session.add(prompt)
        try:
            self._session.flush()
            version = models.PromptVersion(
                prompt_id=prompt.id,
                version=1,
                prompt_text=prompt_text,
                is_active=True,
            )
            self._session.add(version)
            self._session.commit()
            self._session.refresh(prompt)
            self._session.refresh(version)
        except IntegrityError as error:
            self._session.rollback()
            raise ConflictError(f"prompt already exists in prompt set: {name}") from error
        return PromptRecord(prompt=prompt, active_version=version)

    def create_prompt_version(self, *, prompt_id: UUID, prompt_text: str) -> PromptRecord:
        prompt = self._require_prompt(prompt_id)
        versions = self._list(
            select(models.PromptVersion)
            .where(models.PromptVersion.prompt_id == prompt_id)
            .order_by(desc(models.PromptVersion.version))
        )
        next_version = versions[0].version + 1 if versions else 1
        for version in versions:
            version.is_active = False
        active_version = models.PromptVersion(
            prompt_id=prompt.id,
            version=next_version,
            prompt_text=prompt_text,
            is_active=True,
        )
        self._session.add(active_version)
        self._commit()
        self._session.refresh(prompt)
        self._session.refresh(active_version)
        return PromptRecord(prompt=prompt, active_version=active_version)

    def list_providers(self) -> list[models.Provider]:
        return self._list(select(models.Provider).order_by(models.Provider.provider_key))

    def get_provider(self, provider_id: UUID) -> models.Provider:
        return self._require_provider(provider_id)

    def create_provider(
        self,
        *,
        provider_key: str,
        display_name: str,
        provider_kind: str,
        is_active: bool,
    ) -> models.Provider:
        provider = models.Provider(
            provider_key=provider_key,
            display_name=display_name,
            provider_kind=provider_kind,
            is_active=is_active,
        )
        return self._add_one(
            provider,
            conflict_message=f"provider already exists: {provider_key}",
        )

    def list_provider_credentials(self) -> list[models.ProviderCredential]:
        return self._list(
            select(models.ProviderCredential).order_by(models.ProviderCredential.label)
        )

    def create_provider_credential(
        self,
        *,
        provider_id: UUID,
        label: str,
        token: str,
    ) -> models.ProviderCredential:
        self._require_provider(provider_id)
        credential = models.ProviderCredential(
            provider_id=provider_id,
            label=label,
            status="active",
            secret_ref=build_local_secret_ref(token),
            redacted_fingerprint=redacted_fingerprint(token),
            last_tested_at=None,
        )
        return self._add_one(
            credential,
            conflict_message=f"provider credential already exists: {label}",
        )

    def list_rate_limits(self) -> list[models.RateLimitPolicy]:
        return self._list(
            select(models.RateLimitPolicy).order_by(
                models.RateLimitPolicy.provider_id,
                models.RateLimitPolicy.model_id,
            )
        )

    def create_rate_limit(
        self,
        *,
        provider_id: UUID,
        model_id: str | None,
        max_concurrent_requests: int,
        requests_per_minute: int,
        tokens_per_minute: int | None,
        min_delay_ms: int,
        max_retries: int,
        backoff_base_ms: int,
        backoff_max_ms: int,
    ) -> models.RateLimitPolicy:
        self._require_provider(provider_id)
        if self._rate_limit_exists(provider_id=provider_id, model_id=model_id):
            raise ConflictError("rate-limit policy already exists for provider/model")
        policy = models.RateLimitPolicy(
            provider_id=provider_id,
            model_id=model_id,
            max_concurrent_requests=max_concurrent_requests,
            requests_per_minute=requests_per_minute,
            tokens_per_minute=tokens_per_minute,
            min_delay_ms=min_delay_ms,
            max_retries=max_retries,
            backoff_base_ms=backoff_base_ms,
            backoff_max_ms=backoff_max_ms,
        )
        return self._add_one(
            policy,
            conflict_message="rate-limit policy already exists for provider/model",
        )

    def list_models(self, provider_id: UUID | None = None) -> list[models.ModelRegistry]:
        statement = select(models.ModelRegistry).order_by(models.ModelRegistry.model_id)
        if provider_id is not None:
            self._require_provider(provider_id)
            statement = statement.where(models.ModelRegistry.provider_id == provider_id)
        return self._list(statement)

    def create_model(
        self,
        *,
        provider_id: UUID,
        model_id: str,
        display_name: str,
        owned_by: str | None,
        is_available: bool,
        enabled_for_visibility: bool,
        rate_limit_policy_id: UUID | None,
        capability_json: dict[str, Any],
    ) -> models.ModelRegistry:
        self._require_provider(provider_id)
        if rate_limit_policy_id is not None:
            self._require_rate_limit(rate_limit_policy_id)
        model = models.ModelRegistry(
            provider_id=provider_id,
            model_id=model_id,
            display_name=display_name,
            owned_by=owned_by,
            is_available=is_available,
            enabled_for_visibility=enabled_for_visibility,
            rate_limit_policy_id=rate_limit_policy_id,
            capability_json=capability_json,
        )
        return self._add_one(model, conflict_message=f"model already exists: {model_id}")

    def sync_models(
        self,
        *,
        provider_id: UUID,
        discovered_models: list[DiscoveredModel],
    ) -> ModelSyncResult:
        self._require_provider(provider_id)
        existing_models = self._list(
            select(models.ModelRegistry).where(models.ModelRegistry.provider_id == provider_id)
        )
        existing_by_model_id = {model.model_id: model for model in existing_models}
        discovered_by_model_id = {model.model_id: model for model in discovered_models}

        created_count = 0
        updated_count = 0
        unavailable_count = 0

        for discovered in discovered_by_model_id.values():
            existing = existing_by_model_id.get(discovered.model_id)
            if existing is None:
                self._session.add(
                    models.ModelRegistry(
                        provider_id=provider_id,
                        model_id=discovered.model_id,
                        display_name=discovered.display_name,
                        owned_by=discovered.owned_by,
                        is_available=True,
                        enabled_for_visibility=False,
                        rate_limit_policy_id=None,
                        capability_json=discovered.capability_json,
                    )
                )
                created_count += 1
                continue

            existing.display_name = discovered.display_name
            existing.owned_by = discovered.owned_by
            existing.is_available = True
            existing.capability_json = discovered.capability_json
            updated_count += 1

        for existing in existing_models:
            if existing.model_id not in discovered_by_model_id and existing.is_available:
                existing.is_available = False
                unavailable_count += 1

        self._commit()
        return ModelSyncResult(
            created_count=created_count,
            updated_count=updated_count,
            unavailable_count=unavailable_count,
            models=self.list_models(provider_id),
        )

    def _require_brand(self, brand_id: UUID) -> models.Brand:
        return self._require(models.Brand, brand_id, "brand not found")

    def _require_prompt_set(self, prompt_set_id: UUID) -> models.PromptSet:
        return self._require(models.PromptSet, prompt_set_id, "prompt set not found")

    def _require_prompt(self, prompt_id: UUID) -> models.Prompt:
        return self._require(models.Prompt, prompt_id, "prompt not found")

    def _require_provider(self, provider_id: UUID) -> models.Provider:
        return self._require(models.Provider, provider_id, "provider not found")

    def _require_rate_limit(self, rate_limit_policy_id: UUID) -> models.RateLimitPolicy:
        return self._require(models.RateLimitPolicy, rate_limit_policy_id, "rate limit not found")

    def _prompt_record(self, prompt: models.Prompt) -> PromptRecord:
        active_version = self._session.scalar(
            select(models.PromptVersion)
            .where(models.PromptVersion.prompt_id == prompt.id)
            .where(models.PromptVersion.is_active.is_(True))
        )
        if active_version is None:
            raise NotFoundError(f"active prompt version not found for prompt: {prompt.id}")
        return PromptRecord(prompt=prompt, active_version=active_version)

    def _rate_limit_exists(self, *, provider_id: UUID, model_id: str | None) -> bool:
        statement = select(models.RateLimitPolicy).where(
            models.RateLimitPolicy.provider_id == provider_id
        )
        if model_id is None:
            statement = statement.where(models.RateLimitPolicy.model_id.is_(None))
        else:
            statement = statement.where(models.RateLimitPolicy.model_id == model_id)
        return self._session.scalar(statement) is not None

    def _require[T](self, model: type[T], item_id: UUID, message: str) -> T:
        item = self._session.get(model, item_id)
        if item is None:
            raise NotFoundError(message)
        return item

    def _add_one[T](self, item: T, *, conflict_message: str) -> T:
        self._session.add(item)
        try:
            self._session.commit()
            self._session.refresh(item)
        except IntegrityError as error:
            self._session.rollback()
            raise ConflictError(conflict_message) from error
        return item

    def _commit(self) -> None:
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise ConflictError("config write violates a uniqueness constraint") from error

    def _list[T](self, statement: Select[tuple[T]]) -> list[T]:
        return list(self._session.execute(statement).scalars().all())
