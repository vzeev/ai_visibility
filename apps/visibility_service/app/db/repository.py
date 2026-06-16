from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.shared.ai.idempotency import (
    build_raw_response_idempotency_key,
    build_run_item_idempotency_key,
    digest_payload,
)
from apps.shared.ai.provider import AIRequest, AIResponse
from apps.visibility_service.app.db import models

PENDING = "pending"
RUNNING = "running"
SUCCEEDED = "succeeded"
FAILED = "failed"
THROTTLED = "throttled"
QUEUED = "queued"


class VisibilityRepositoryError(Exception):
    pass


class NotFoundError(VisibilityRepositoryError):
    pass


class ConflictError(VisibilityRepositoryError):
    pass


@dataclass(frozen=True)
class CreatedRun:
    batch: models.RunBatch
    item_count: int


@dataclass(frozen=True)
class RawResponsePage:
    items: list[models.RawResponse]
    total: int


class VisibilityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_run(
        self,
        *,
        brand_id: UUID,
        prompt_set_id: UUID,
        sample_count: int,
        max_attempts: int,
    ) -> CreatedRun:
        snapshot = self._build_config_snapshot(brand_id=brand_id, prompt_set_id=prompt_set_id)
        batch = models.RunBatch(
            brand_id=brand_id,
            prompt_set_id=prompt_set_id,
            config_snapshot_json=snapshot,
            status=QUEUED,
            started_at=None,
            completed_at=None,
        )
        self._session.add(batch)
        self._session.flush()

        snapshot_hash = digest_payload(
            "config-snapshot:v1",
            {"run_batch_id": str(batch.id), "config_snapshot": snapshot},
        )
        item_count = 0
        for prompt in _snapshot_list(snapshot, "prompts"):
            for model in _snapshot_list(snapshot, "models"):
                for sample_index in range(sample_count):
                    item = models.RunItem(
                        run_batch_id=batch.id,
                        prompt_version_id=UUID(str(prompt["prompt_version_id"])),
                        provider_id=UUID(str(model["provider_id"])),
                        model_registry_id=UUID(str(model["model_registry_id"])),
                        sample_index=sample_index,
                        idempotency_key=build_run_item_idempotency_key(
                            prompt_version_id=str(prompt["prompt_version_id"]),
                            provider_key=str(model["provider_key"]),
                            model_id=str(model["model_id"]),
                            sample_index=sample_index,
                            config_snapshot_hash=snapshot_hash,
                        ),
                        status=PENDING,
                        attempt_count=0,
                        max_attempts=max_attempts,
                        next_attempt_at=_utc_now(),
                    )
                    self._session.add(item)
                    item_count += 1
        self._commit()
        self._session.refresh(batch)
        return CreatedRun(batch=batch, item_count=item_count)

    def list_runs(self) -> list[models.RunBatch]:
        return self._list(select(models.RunBatch).order_by(models.RunBatch.created_at.desc()))

    def queue_state(self) -> dict[str, int]:
        counts = {PENDING: 0, RUNNING: 0, SUCCEEDED: 0, FAILED: 0, THROTTLED: 0}
        rows = self._session.execute(
            select(models.RunItem.status, func.count()).group_by(models.RunItem.status)
        ).all()
        for status, count in rows:
            counts[str(status)] = int(count)
        return counts

    def claim_next_item(self, *, lease_seconds: int) -> models.RunItem | None:
        now = _utc_now()
        item = self._session.scalar(
            select(models.RunItem)
            .where(models.RunItem.status.in_((PENDING, THROTTLED)))
            .where(models.RunItem.next_attempt_at <= now)
            .order_by(models.RunItem.created_at, models.RunItem.id)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if item is None:
            return None
        item.status = RUNNING
        item.attempt_count += 1
        item.lease_expires_at = now + timedelta(seconds=lease_seconds)
        batch = self._require_batch(item.run_batch_id)
        batch.status = RUNNING
        if batch.started_at is None:
            batch.started_at = now
        self._commit()
        self._session.refresh(item)
        return item

    def record_model_error(
        self,
        *,
        run_item_id: UUID,
        error_type: str,
        error_message: str,
        retryable: bool,
        retry_delay_seconds: int,
    ) -> models.RunItem:
        item = self._require_item(run_item_id)
        metadata = self._item_metadata(item)
        model_error = models.ModelError(
            run_item_id=item.id,
            provider_id=item.provider_id,
            model_id=str(metadata["model_id"]),
            error_type=error_type,
            error_message=error_message,
            retryable=retryable,
        )
        self._session.add(model_error)
        item.last_error = error_message
        item.lease_expires_at = None
        if retryable and item.attempt_count < item.max_attempts:
            item.status = THROTTLED if error_type == "rate_limit" else PENDING
            item.next_attempt_at = _utc_now() + timedelta(seconds=retry_delay_seconds)
        else:
            item.status = FAILED
        self._refresh_batch_status(item.run_batch_id)
        self._commit()
        self._session.refresh(item)
        return item

    def record_raw_response(self, *, run_item_id: UUID, response: AIResponse) -> models.RawResponse:
        item = self._require_item(run_item_id)
        existing_for_item = self._session.scalar(
            select(models.RawResponse).where(models.RawResponse.run_item_id == run_item_id)
        )
        if existing_for_item is not None:
            item.status = SUCCEEDED
            item.lease_expires_at = None
            self._refresh_batch_status(item.run_batch_id)
            self._commit()
            return existing_for_item

        metadata = self._item_metadata(item)
        raw_response_json = dict(response.raw_response_json)
        raw_response = models.RawResponse(
            run_item_id=item.id,
            idempotency_key=build_raw_response_idempotency_key(
                run_item_idempotency_key=item.idempotency_key,
                provider_key=response.provider_key,
                model_id=response.model_id,
                provider_response_id=response.provider_response_id,
                raw_response_json=raw_response_json,
            ),
            provider_id=item.provider_id,
            model_id=response.model_id,
            provider_response_id=response.provider_response_id,
            prompt_text=str(metadata["prompt_text"]),
            output_text=response.output_text,
            raw_request_json=dict(response.raw_request_json),
            raw_response_json=raw_response_json,
            usage_json=dict(response.usage_json),
            latency_ms=response.latency_ms,
            status=SUCCEEDED,
        )
        self._session.add(raw_response)
        item.status = SUCCEEDED
        item.lease_expires_at = None
        item.last_error = None
        self._refresh_batch_status(item.run_batch_id)
        try:
            self._session.commit()
            self._session.refresh(raw_response)
        except IntegrityError:
            self._session.rollback()
            existing = self._session.scalar(
                select(models.RawResponse).where(
                    models.RawResponse.idempotency_key == raw_response.idempotency_key
                )
            )
            if existing is None:
                raise
            return existing
        return raw_response

    def build_ai_request(self, item: models.RunItem) -> AIRequest:
        metadata = self._item_metadata(item)
        request_metadata: dict[str, object] = {
            "run_batch_id": str(item.run_batch_id),
            "run_item_id": str(item.id),
            "sample_index": item.sample_index,
            "idempotency_key": item.idempotency_key,
            "attempt_count": item.attempt_count,
        }
        rate_limit_policy = metadata.get("rate_limit_policy")
        if isinstance(rate_limit_policy, Mapping):
            rate_limit_mapping = cast(Mapping[object, object], rate_limit_policy)
            request_metadata["rate_limit_policy"] = {
                str(key): value for key, value in rate_limit_mapping.items()
            }
        return AIRequest(
            provider_key=str(metadata["provider_key"]),
            model_id=str(metadata["model_id"]),
            prompt_text=str(metadata["prompt_text"]),
            metadata=request_metadata,
        )

    def list_raw_responses(self, *, q: str | None, limit: int, offset: int) -> RawResponsePage:
        search_condition = None
        if q:
            pattern = f"%{q}%"
            search_condition = or_(
                models.RawResponse.output_text.ilike(pattern),
                models.RawResponse.prompt_text.ilike(pattern),
                models.RawResponse.model_id.ilike(pattern),
            )
        count_statement = select(func.count()).select_from(models.RawResponse)
        item_statement = (
            select(models.RawResponse)
            .order_by(models.RawResponse.created_at.desc(), models.RawResponse.id)
            .limit(limit)
            .offset(offset)
        )
        if search_condition is not None:
            count_statement = count_statement.where(search_condition)
            item_statement = item_statement.where(search_condition)
        total = int(self._session.scalar(count_statement) or 0)
        return RawResponsePage(items=self._list(item_statement), total=total)

    def _build_config_snapshot(self, *, brand_id: UUID, prompt_set_id: UUID) -> dict[str, object]:
        brand = self._require(models.ConfigBrand, brand_id, "brand not found")
        prompt_set = self._require(models.ConfigPromptSet, prompt_set_id, "prompt set not found")
        if prompt_set.brand_id != brand.id:
            raise ConflictError("prompt set does not belong to brand")
        if not prompt_set.is_active:
            raise ConflictError("prompt set is not active")

        prompts = self._active_prompt_records(prompt_set_id)
        if not prompts:
            raise ConflictError("prompt set has no active prompt versions")
        models_for_run = self._enabled_models()
        if not models_for_run:
            raise ConflictError("no enabled visibility models are configured")

        return {
            "brand": {
                "id": str(brand.id),
                "name": brand.name,
                "website_url": brand.website_url,
            },
            "prompt_set": {
                "id": str(prompt_set.id),
                "name": prompt_set.name,
                "description": prompt_set.description,
            },
            "prompts": prompts,
            "models": models_for_run,
            "created_at": _utc_now().isoformat(),
        }

    def _active_prompt_records(self, prompt_set_id: UUID) -> list[dict[str, object]]:
        prompts = self._list(
            select(models.ConfigPrompt)
            .where(models.ConfigPrompt.prompt_set_id == prompt_set_id)
            .where(models.ConfigPrompt.is_active.is_(True))
            .order_by(models.ConfigPrompt.name)
        )
        records: list[dict[str, object]] = []
        for prompt in prompts:
            active_version = self._session.scalar(
                select(models.ConfigPromptVersion)
                .where(models.ConfigPromptVersion.prompt_id == prompt.id)
                .where(models.ConfigPromptVersion.is_active.is_(True))
            )
            if active_version is None:
                continue
            records.append(
                {
                    "prompt_id": str(prompt.id),
                    "prompt_version_id": str(active_version.id),
                    "version": active_version.version,
                    "name": prompt.name,
                    "intent": prompt.intent,
                    "prompt_text": active_version.prompt_text,
                }
            )
        return records

    def _enabled_models(self) -> list[dict[str, object]]:
        model_rows = self._list(
            select(models.ConfigModelRegistry)
            .where(models.ConfigModelRegistry.enabled_for_visibility.is_(True))
            .where(models.ConfigModelRegistry.is_available.is_(True))
            .order_by(models.ConfigModelRegistry.model_id)
        )
        records: list[dict[str, object]] = []
        for model in model_rows:
            provider = self._session.get(models.ConfigProvider, model.provider_id)
            if provider is None or not provider.is_active:
                continue
            records.append(
                {
                    "model_registry_id": str(model.id),
                    "provider_id": str(provider.id),
                    "provider_key": provider.provider_key,
                    "model_id": model.model_id,
                    "display_name": model.display_name,
                    "owned_by": model.owned_by,
                    "capability_json": model.capability_json,
                    "rate_limit_policy": self._rate_limit_record(model),
                }
            )
        return records

    def _rate_limit_record(
        self,
        model: models.ConfigModelRegistry,
    ) -> dict[str, object] | None:
        policy = None
        if model.rate_limit_policy_id is not None:
            policy = self._session.get(models.ConfigRateLimitPolicy, model.rate_limit_policy_id)
        if policy is None:
            policy = self._session.scalar(
                select(models.ConfigRateLimitPolicy)
                .where(models.ConfigRateLimitPolicy.provider_id == model.provider_id)
                .where(models.ConfigRateLimitPolicy.model_id == model.model_id)
            )
        if policy is None:
            policy = self._session.scalar(
                select(models.ConfigRateLimitPolicy)
                .where(models.ConfigRateLimitPolicy.provider_id == model.provider_id)
                .where(models.ConfigRateLimitPolicy.model_id.is_(None))
            )
        if policy is None:
            return None
        return {
            "id": str(policy.id),
            "provider_id": str(policy.provider_id),
            "model_id": policy.model_id,
            "max_concurrent_requests": policy.max_concurrent_requests,
            "requests_per_minute": policy.requests_per_minute,
            "tokens_per_minute": policy.tokens_per_minute,
            "min_delay_ms": policy.min_delay_ms,
            "max_retries": policy.max_retries,
            "backoff_base_ms": policy.backoff_base_ms,
            "backoff_max_ms": policy.backoff_max_ms,
        }

    def _item_metadata(self, item: models.RunItem) -> dict[str, object]:
        batch = self._require_batch(item.run_batch_id)
        snapshot = batch.config_snapshot_json
        prompt_text = ""
        model_id = ""
        provider_key = ""
        rate_limit_policy: dict[str, object] | None = None
        for prompt in _snapshot_list(snapshot, "prompts"):
            if str(prompt["prompt_version_id"]) == str(item.prompt_version_id):
                prompt_text = str(prompt["prompt_text"])
                break
        for model in _snapshot_list(snapshot, "models"):
            if str(model["model_registry_id"]) == str(item.model_registry_id):
                model_id = str(model["model_id"])
                provider_key = str(model["provider_key"])
                policy = model.get("rate_limit_policy")
                if isinstance(policy, dict):
                    rate_limit_policy = cast(dict[str, object], policy)
                break
        if not prompt_text or not model_id or not provider_key:
            raise NotFoundError("run item metadata missing from config snapshot")
        return {
            "prompt_text": prompt_text,
            "model_id": model_id,
            "provider_key": provider_key,
            "rate_limit_policy": rate_limit_policy,
        }

    def _refresh_batch_status(self, run_batch_id: UUID) -> None:
        batch = self._require_batch(run_batch_id)
        statuses = [
            item.status
            for item in self._list(
                select(models.RunItem).where(models.RunItem.run_batch_id == run_batch_id)
            )
        ]
        if statuses and all(status == SUCCEEDED for status in statuses):
            batch.status = SUCCEEDED
            batch.completed_at = _utc_now()
        elif statuses and all(status in (SUCCEEDED, FAILED) for status in statuses):
            batch.status = FAILED
            batch.completed_at = _utc_now()
        elif any(status == RUNNING for status in statuses):
            batch.status = RUNNING
        elif any(status in (PENDING, THROTTLED) for status in statuses):
            batch.status = QUEUED

    def _require_batch(self, run_batch_id: UUID) -> models.RunBatch:
        return self._require(models.RunBatch, run_batch_id, "run batch not found")

    def _require_item(self, run_item_id: UUID) -> models.RunItem:
        return self._require(models.RunItem, run_item_id, "run item not found")

    def _require[T](self, model: type[T], item_id: UUID, message: str) -> T:
        item = self._session.get(model, item_id)
        if item is None:
            raise NotFoundError(message)
        return item

    def _commit(self) -> None:
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise ConflictError("visibility write violates a uniqueness constraint") from error

    def _list[T](self, statement: Select[tuple[T]]) -> list[T]:
        return list(self._session.execute(statement).scalars().all())


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _snapshot_list(snapshot: Mapping[str, object], key: str) -> list[dict[str, object]]:
    return cast(list[dict[str, object]], snapshot[key])
