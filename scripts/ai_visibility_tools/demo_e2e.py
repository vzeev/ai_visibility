from __future__ import annotations

import argparse
import asyncio
import json
import os
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from uuid import UUID

from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from apps.config_service.app.db import models as config_models
from apps.config_service.app.db.repository import ConfigRepository
from apps.insights_service.app.db.repository import InsightsRepository
from apps.insights_service.app.domain.extractor import DEFAULT_EXTRACTION_VERSION
from apps.shared.ai.provider import FakeAIProviderAdapter
from apps.shared.db.runtime import get_database_url
from apps.visibility_service.app.db.repository import VisibilityRepository
from apps.worker.app.visibility_worker import VisibilityWorker

DEMO_DATABASE_URL_ENV = "AI_VISIBILITY_DEMO_DATABASE_URL"
DEMO_BRAND_NAME = "Brandlight"
DEMO_PROMPT_SET_NAME = "Brandlight interview demo prompts"
DEMO_PROVIDER_KEY = "fake"
DEMO_MODEL_ID = "brandlight-fake-v1"
DEMO_FAKE_OUTPUT = (
    "Brandlight is a strong AI visibility platform for tracking how brands appear in AI "
    "answers. Profound and Peec AI are visible competitors. Source: "
    "https://www.brandlight.ai/."
)


@dataclass(frozen=True)
class DemoSeedResult:
    brand_id: UUID
    prompt_set_id: UUID
    provider_id: UUID
    model_registry_id: UUID
    rate_limit_policy_id: UUID
    prompt_count: int


@dataclass(frozen=True)
class DemoSmokeResult:
    brand_id: UUID
    prompt_set_id: UUID
    run_batch_id: UUID
    item_count: int
    processed_count: int
    failed_count: int
    raw_response_count: int
    extraction_run_count: int
    mention_count: int
    citation_count: int
    summary_id: UUID
    extraction_version: str

    def to_dict(self) -> dict[str, object]:
        values = asdict(self)
        return {
            key: str(value) if isinstance(value, UUID) else value for key, value in values.items()
        }


def database_url_from_env() -> str:
    return os.environ.get(DEMO_DATABASE_URL_ENV) or get_database_url()


def create_session_factory(database_url: str) -> tuple[Engine, sessionmaker[Session]]:
    engine = create_engine(database_url, pool_pre_ping=True)
    return engine, sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def upgrade_database(database_url: str) -> None:
    original_database_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = database_url
    try:
        command.upgrade(Config("alembic/alembic.ini"), "head")
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url


def seed_brandlight_demo(session_factory: sessionmaker[Session]) -> DemoSeedResult:
    with session_factory() as session:
        repository = ConfigRepository(session)
        brand = _get_or_create_brand(repository, session)
        _ensure_brand_alias(session, brand.id, "Brand Light")
        _get_or_create_competitor(repository, session, brand.id, "Profound")
        _get_or_create_competitor(repository, session, brand.id, "Peec AI")
        _get_or_create_product(repository, session, brand.id)
        prompt_set = _get_or_create_prompt_set(repository, session, brand.id)
        prompt_count = _ensure_demo_prompts(repository, session, prompt_set.id)
        provider = _get_or_create_provider(repository, session)
        _get_or_create_provider_credential(repository, session, provider.id)
        rate_limit = _get_or_create_rate_limit(repository, session, provider.id)
        model = _get_or_create_model(repository, session, provider.id, rate_limit.id)
        session.commit()
        return DemoSeedResult(
            brand_id=brand.id,
            prompt_set_id=prompt_set.id,
            provider_id=provider.id,
            model_registry_id=model.id,
            rate_limit_policy_id=rate_limit.id,
            prompt_count=prompt_count,
        )


def run_brandlight_demo_smoke(
    session_factory: sessionmaker[Session],
    *,
    sample_count: int = 1,
    max_attempts: int = 3,
    extraction_version: str = DEFAULT_EXTRACTION_VERSION,
) -> DemoSmokeResult:
    seed_result = seed_brandlight_demo(session_factory)
    with session_factory() as session:
        created_run = VisibilityRepository(session).create_run(
            brand_id=seed_result.brand_id,
            prompt_set_id=seed_result.prompt_set_id,
            sample_count=sample_count,
            max_attempts=max_attempts,
        )
        run_batch_id = created_run.batch.id
        item_count = created_run.item_count

    worker = VisibilityWorker(
        session_factory,
        adapters={DEMO_PROVIDER_KEY: FakeAIProviderAdapter({DEMO_MODEL_ID: DEMO_FAKE_OUTPUT})},
    )
    worker_results = asyncio.run(worker.process_batch(max_items=item_count + 1))
    processed_count = sum(1 for result in worker_results if result.status == "processed")
    failed_count = sum(1 for result in worker_results if result.status == "failed")

    with session_factory() as session:
        extraction_result = InsightsRepository(session).extract_run_batch(
            run_batch_id=run_batch_id,
            extraction_version=extraction_version,
        )
        mention_count = sum(len(record.mentions) for record in extraction_result.extraction_runs)
        citation_count = sum(len(record.citations) for record in extraction_result.extraction_runs)
        _validate_smoke_result(
            item_count=item_count,
            processed_count=processed_count,
            failed_count=failed_count,
            raw_response_count=extraction_result.raw_response_count,
            mention_count=mention_count,
        )
        return DemoSmokeResult(
            brand_id=seed_result.brand_id,
            prompt_set_id=seed_result.prompt_set_id,
            run_batch_id=run_batch_id,
            item_count=item_count,
            processed_count=processed_count,
            failed_count=failed_count,
            raw_response_count=extraction_result.raw_response_count,
            extraction_run_count=len(extraction_result.extraction_runs),
            mention_count=mention_count,
            citation_count=citation_count,
            summary_id=extraction_result.summary.id,
            extraction_version=extraction_version,
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Brandlight local demo smoke flow.")
    parser.add_argument("--database-url", default=database_url_from_env())
    parser.add_argument("--skip-migrations", action="store_true")
    parser.add_argument("--sample-count", type=int, default=1)
    parser.add_argument("--extraction-version", default=DEFAULT_EXTRACTION_VERSION)
    args = parser.parse_args(argv)

    if args.sample_count < 1:
        parser.error("--sample-count must be >= 1")

    if not args.skip_migrations:
        upgrade_database(str(args.database_url))

    engine, session_factory = create_session_factory(str(args.database_url))
    try:
        result = run_brandlight_demo_smoke(
            session_factory,
            sample_count=int(args.sample_count),
            extraction_version=str(args.extraction_version),
        )
    finally:
        engine.dispose()

    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


def _get_or_create_brand(
    repository: ConfigRepository,
    session: Session,
) -> config_models.Brand:
    brand = session.scalar(
        select(config_models.Brand).where(config_models.Brand.name == DEMO_BRAND_NAME)
    )
    if brand is None:
        return repository.create_brand(
            name=DEMO_BRAND_NAME,
            website_url="https://www.brandlight.ai/",
        )
    brand.website_url = "https://www.brandlight.ai/"
    session.commit()
    session.refresh(brand)
    return brand


def _ensure_brand_alias(session: Session, brand_id: UUID, alias: str) -> None:
    existing = session.scalar(
        select(config_models.BrandAlias)
        .where(config_models.BrandAlias.brand_id == brand_id)
        .where(config_models.BrandAlias.alias == alias)
    )
    if existing is None:
        session.add(config_models.BrandAlias(brand_id=brand_id, alias=alias))
        session.commit()


def _get_or_create_competitor(
    repository: ConfigRepository,
    session: Session,
    brand_id: UUID,
    name: str,
) -> config_models.Competitor:
    competitor = session.scalar(
        select(config_models.Competitor)
        .where(config_models.Competitor.brand_id == brand_id)
        .where(config_models.Competitor.name == name)
    )
    if competitor is None:
        return repository.create_competitor(
            brand_id=brand_id,
            name=name,
            website_url=None,
        )
    return competitor


def _get_or_create_product(
    repository: ConfigRepository,
    session: Session,
    brand_id: UUID,
) -> config_models.Product:
    product_name = "AI Visibility Platform"
    product = session.scalar(
        select(config_models.Product)
        .where(config_models.Product.brand_id == brand_id)
        .where(config_models.Product.name == product_name)
    )
    if product is None:
        return repository.create_product(
            brand_id=brand_id,
            name=product_name,
            description="Brandlight's platform for measuring brand visibility in AI answers.",
        )
    product.description = "Brandlight's platform for measuring brand visibility in AI answers."
    session.commit()
    session.refresh(product)
    return product


def _get_or_create_prompt_set(
    repository: ConfigRepository,
    session: Session,
    brand_id: UUID,
) -> config_models.PromptSet:
    prompt_set = session.scalar(
        select(config_models.PromptSet)
        .where(config_models.PromptSet.brand_id == brand_id)
        .where(config_models.PromptSet.name == DEMO_PROMPT_SET_NAME)
    )
    if prompt_set is None:
        return repository.create_prompt_set(
            brand_id=brand_id,
            name=DEMO_PROMPT_SET_NAME,
            description="Interview demo prompts for AI visibility evidence.",
            is_active=True,
        )
    prompt_set.description = "Interview demo prompts for AI visibility evidence."
    prompt_set.is_active = True
    session.commit()
    session.refresh(prompt_set)
    return prompt_set


def _ensure_demo_prompts(
    repository: ConfigRepository,
    session: Session,
    prompt_set_id: UUID,
) -> int:
    prompts = {
        "Category recommendation": (
            "commercial",
            "Which AI visibility platforms should a B2B marketing leader evaluate? "
            "Consider Brandlight, Profound, Peec AI, and cite https://www.brandlight.ai/.",
        ),
        "Competitor comparison": (
            "competitive",
            "Compare Brandlight with Profound and Peec AI for AI search visibility tracking. "
            "Mention whether Brandlight is visible and include https://www.brandlight.ai/.",
        ),
    }
    ensured_count = 0
    for name, (intent, prompt_text) in prompts.items():
        prompt = session.scalar(
            select(config_models.Prompt)
            .where(config_models.Prompt.prompt_set_id == prompt_set_id)
            .where(config_models.Prompt.name == name)
        )
        if prompt is None:
            repository.create_prompt(
                prompt_set_id=prompt_set_id,
                name=name,
                intent=intent,
                prompt_text=prompt_text,
            )
            ensured_count += 1
            continue
        prompt.intent = intent
        prompt.is_active = True
        session.commit()
        active_version = _active_prompt_version(session, prompt.id)
        if active_version is None or active_version.prompt_text != prompt_text:
            repository.create_prompt_version(prompt_id=prompt.id, prompt_text=prompt_text)
        ensured_count += 1
    return ensured_count


def _active_prompt_version(
    session: Session,
    prompt_id: UUID,
) -> config_models.PromptVersion | None:
    return session.scalar(
        select(config_models.PromptVersion)
        .where(config_models.PromptVersion.prompt_id == prompt_id)
        .where(config_models.PromptVersion.is_active.is_(True))
    )


def _get_or_create_provider(
    repository: ConfigRepository,
    session: Session,
) -> config_models.Provider:
    provider = session.scalar(
        select(config_models.Provider).where(
            config_models.Provider.provider_key == DEMO_PROVIDER_KEY
        )
    )
    if provider is None:
        return repository.create_provider(
            provider_key=DEMO_PROVIDER_KEY,
            display_name="Fake Provider",
            provider_kind="local",
            is_active=True,
        )
    provider.display_name = "Fake Provider"
    provider.provider_kind = "local"
    provider.is_active = True
    session.commit()
    session.refresh(provider)
    return provider


def _get_or_create_provider_credential(
    repository: ConfigRepository,
    session: Session,
    provider_id: UUID,
) -> config_models.ProviderCredential:
    label = "local fake provider token"
    credential = session.scalar(
        select(config_models.ProviderCredential)
        .where(config_models.ProviderCredential.provider_id == provider_id)
        .where(config_models.ProviderCredential.label == label)
    )
    if credential is None:
        demo_token = os.environ.get(
            "AI_VISIBILITY_DEMO_FAKE_TOKEN",
            f"fake-local-token-{provider_id.hex}",
        )
        return repository.create_provider_credential(
            provider_id=provider_id,
            label=label,
            token=demo_token,
        )
    return credential


def _get_or_create_rate_limit(
    repository: ConfigRepository,
    session: Session,
    provider_id: UUID,
) -> config_models.RateLimitPolicy:
    rate_limit = session.scalar(
        select(config_models.RateLimitPolicy)
        .where(config_models.RateLimitPolicy.provider_id == provider_id)
        .where(config_models.RateLimitPolicy.model_id == DEMO_MODEL_ID)
    )
    if rate_limit is None:
        return repository.create_rate_limit(
            provider_id=provider_id,
            model_id=DEMO_MODEL_ID,
            max_concurrent_requests=2,
            requests_per_minute=120,
            tokens_per_minute=None,
            min_delay_ms=0,
            max_retries=3,
            backoff_base_ms=100,
            backoff_max_ms=1_000,
        )
    rate_limit.max_concurrent_requests = 2
    rate_limit.requests_per_minute = 120
    rate_limit.tokens_per_minute = None
    rate_limit.min_delay_ms = 0
    rate_limit.max_retries = 3
    rate_limit.backoff_base_ms = 100
    rate_limit.backoff_max_ms = 1_000
    session.commit()
    session.refresh(rate_limit)
    return rate_limit


def _get_or_create_model(
    repository: ConfigRepository,
    session: Session,
    provider_id: UUID,
    rate_limit_policy_id: UUID,
) -> config_models.ModelRegistry:
    model = session.scalar(
        select(config_models.ModelRegistry)
        .where(config_models.ModelRegistry.provider_id == provider_id)
        .where(config_models.ModelRegistry.model_id == DEMO_MODEL_ID)
    )
    if model is None:
        return repository.create_model(
            provider_id=provider_id,
            model_id=DEMO_MODEL_ID,
            display_name="Brandlight Fake v1",
            owned_by="local",
            is_available=True,
            enabled_for_visibility=True,
            rate_limit_policy_id=rate_limit_policy_id,
            capability_json={"deterministic": True, "responses": True},
        )
    model.display_name = "Brandlight Fake v1"
    model.owned_by = "local"
    model.is_available = True
    model.enabled_for_visibility = True
    model.rate_limit_policy_id = rate_limit_policy_id
    model.capability_json = {"deterministic": True, "responses": True}
    session.commit()
    session.refresh(model)
    return model


def _validate_smoke_result(
    *,
    item_count: int,
    processed_count: int,
    failed_count: int,
    raw_response_count: int,
    mention_count: int,
) -> None:
    if item_count <= 0:
        raise RuntimeError("demo smoke created no visibility run items")
    if failed_count:
        raise RuntimeError(f"demo smoke worker failed {failed_count} item(s)")
    if processed_count < item_count:
        raise RuntimeError(
            f"demo smoke processed {processed_count} worker item(s), fewer than "
            f"{item_count} new demo visibility run items"
        )
    if raw_response_count != item_count:
        raise RuntimeError(
            f"demo smoke persisted {raw_response_count} raw responses for {item_count} items"
        )
    if mention_count <= 0:
        raise RuntimeError("demo smoke extraction produced no mentions")


if __name__ == "__main__":
    raise SystemExit(main())
