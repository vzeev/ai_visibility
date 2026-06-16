from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Select, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.insights_service.app.db import models
from apps.insights_service.app.domain.extractor import (
    DEFAULT_EXTRACTION_VERSION,
    DeterministicInsightExtractor,
    EntityAliases,
)

COMPLETED = "completed"
RUNNING = "running"


class InsightsRepositoryError(Exception):
    pass


class NotFoundError(InsightsRepositoryError):
    pass


class ConflictError(InsightsRepositoryError):
    pass


@dataclass(frozen=True)
class ExtractionRunRecord:
    run: models.ExtractionRun
    mentions: list[models.ExtractedMention]
    citations: list[models.ExtractedCitation]


@dataclass(frozen=True)
class BatchExtractionResult:
    run_batch_id: UUID
    extraction_version: str
    raw_response_count: int
    extraction_runs: list[ExtractionRunRecord]
    summary: models.VisibilitySummary


class InsightsRepository:
    def __init__(
        self,
        session: Session,
        extractor: DeterministicInsightExtractor | None = None,
    ) -> None:
        self._session = session
        self._extractor = extractor or DeterministicInsightExtractor()

    def extract_raw_response(
        self,
        *,
        raw_response_id: UUID,
        extraction_version: str = DEFAULT_EXTRACTION_VERSION,
    ) -> ExtractionRunRecord:
        raw_response = self._require_raw_response(raw_response_id)
        run_item = self._require_run_item(raw_response.run_item_id)
        run_batch = self._require_run_batch(run_item.run_batch_id)
        existing = self._existing_extraction_run(raw_response.id, extraction_version)
        if existing is not None and existing.status == COMPLETED:
            return self._record(existing)

        run = existing or models.ExtractionRun(
            raw_response_id=raw_response.id,
            extraction_version=extraction_version,
            status=RUNNING,
            completed_at=None,
        )
        if existing is None:
            self._session.add(run)
            self._session.flush()
        else:
            self._delete_derived_rows(run.id)
            run.status = RUNNING
            run.completed_at = None

        entities = self._entities_for_brand(run_batch.brand_id)
        result = self._extractor.extract(output_text=raw_response.output_text, entities=entities)
        for mention in result.mentions:
            self._session.add(
                models.ExtractedMention(
                    extraction_run_id=run.id,
                    entity_type=mention.entity_type,
                    entity_name=mention.entity_name,
                    mention_text=mention.mention_text,
                    sentiment_label=mention.sentiment_label,
                    confidence=Decimal(str(mention.confidence)),
                    evidence_json={
                        "raw_response_id": str(raw_response.id),
                        "source": "output_text",
                        "start_index": mention.start_index,
                        "end_index": mention.end_index,
                        "snippet": mention.snippet,
                    },
                )
            )
        for citation in result.citations:
            self._session.add(
                models.ExtractedCitation(
                    extraction_run_id=run.id,
                    url=citation.url,
                    domain=citation.domain,
                    title=None,
                    evidence_json={
                        "raw_response_id": str(raw_response.id),
                        "source": "output_text",
                        "start_index": citation.start_index,
                        "end_index": citation.end_index,
                        "snippet": citation.snippet,
                    },
                )
            )
        run.status = COMPLETED
        run.completed_at = _utc_now()
        self._commit()
        self._session.refresh(run)
        return self._record(run)

    def extract_run_batch(
        self,
        *,
        run_batch_id: UUID,
        extraction_version: str = DEFAULT_EXTRACTION_VERSION,
    ) -> BatchExtractionResult:
        run_batch = self._require_run_batch(run_batch_id)
        raw_responses = self._raw_responses_for_batch(run_batch.id)
        records = [
            self.extract_raw_response(
                raw_response_id=raw_response.id,
                extraction_version=extraction_version,
            )
            for raw_response in raw_responses
        ]
        summary_json = self._summary_json(
            run_batch=run_batch,
            raw_responses=raw_responses,
            records=records,
            extraction_version=extraction_version,
        )
        summary = self._existing_summary(
            brand_id=run_batch.brand_id,
            run_batch_id=run_batch.id,
            extraction_version=extraction_version,
        )
        if summary is None:
            summary = models.VisibilitySummary(
                brand_id=run_batch.brand_id,
                run_batch_id=run_batch.id,
                extraction_version=extraction_version,
                summary_json=summary_json,
            )
            self._session.add(summary)
        else:
            summary.summary_json = summary_json
        self._commit()
        self._session.refresh(summary)
        return BatchExtractionResult(
            run_batch_id=run_batch.id,
            extraction_version=extraction_version,
            raw_response_count=len(raw_responses),
            extraction_runs=records,
            summary=summary,
        )

    def get_extraction_run(self, extraction_run_id: UUID) -> ExtractionRunRecord:
        run = self._session.get(models.ExtractionRun, extraction_run_id)
        if run is None:
            raise NotFoundError("extraction run not found")
        return self._record(run)

    def list_summaries(
        self,
        *,
        brand_id: UUID | None = None,
        run_batch_id: UUID | None = None,
        extraction_version: str | None = None,
    ) -> list[models.VisibilitySummary]:
        statement = select(models.VisibilitySummary).order_by(
            models.VisibilitySummary.created_at.desc()
        )
        if brand_id is not None:
            statement = statement.where(models.VisibilitySummary.brand_id == brand_id)
        if run_batch_id is not None:
            statement = statement.where(models.VisibilitySummary.run_batch_id == run_batch_id)
        if extraction_version is not None:
            statement = statement.where(
                models.VisibilitySummary.extraction_version == extraction_version
            )
        return self._list(statement)

    def _record(self, run: models.ExtractionRun) -> ExtractionRunRecord:
        mentions = self._list(
            select(models.ExtractedMention)
            .where(models.ExtractedMention.extraction_run_id == run.id)
            .order_by(models.ExtractedMention.entity_type, models.ExtractedMention.entity_name)
        )
        citations = self._list(
            select(models.ExtractedCitation)
            .where(models.ExtractedCitation.extraction_run_id == run.id)
            .order_by(models.ExtractedCitation.domain, models.ExtractedCitation.url)
        )
        return ExtractionRunRecord(run=run, mentions=mentions, citations=citations)

    def _entities_for_brand(self, brand_id: UUID) -> tuple[EntityAliases, ...]:
        brand = self._session.get(models.ConfigBrand, brand_id)
        if brand is None:
            raise NotFoundError("brand not found for run batch")
        aliases = [
            alias.alias
            for alias in self._list(
                select(models.ConfigBrandAlias)
                .where(models.ConfigBrandAlias.brand_id == brand.id)
                .order_by(models.ConfigBrandAlias.alias)
            )
        ]
        competitors = self._list(
            select(models.ConfigCompetitor)
            .where(models.ConfigCompetitor.brand_id == brand.id)
            .order_by(models.ConfigCompetitor.name)
        )
        entities = [
            EntityAliases(
                entity_type="brand",
                entity_name=brand.name,
                aliases=tuple([brand.name, *aliases]),
            )
        ]
        entities.extend(
            EntityAliases(
                entity_type="competitor",
                entity_name=competitor.name,
                aliases=(competitor.name,),
            )
            for competitor in competitors
        )
        return tuple(entities)

    def _summary_json(
        self,
        *,
        run_batch: models.VisibilityRunBatch,
        raw_responses: list[models.VisibilityRawResponse],
        records: list[ExtractionRunRecord],
        extraction_version: str,
    ) -> dict[str, Any]:
        mentions = [mention for record in records for mention in record.mentions]
        citations = [citation for record in records for citation in record.citations]
        entity_counts: dict[str, dict[str, int]] = {"brand": {}, "competitor": {}}
        for mention in mentions:
            entity_counts.setdefault(mention.entity_type, {})
            entity_counts[mention.entity_type][mention.entity_name] = (
                entity_counts[mention.entity_type].get(mention.entity_name, 0) + 1
            )
        domain_counts = Counter(citation.domain for citation in citations)
        return {
            "brand_id": str(run_batch.brand_id),
            "run_batch_id": str(run_batch.id),
            "extraction_version": extraction_version,
            "raw_response_ids": [str(raw_response.id) for raw_response in raw_responses],
            "extraction_run_ids": [str(record.run.id) for record in records],
            "raw_response_count": len(raw_responses),
            "brand_mentions": sum(entity_counts.get("brand", {}).values()),
            "competitor_mentions": sum(entity_counts.get("competitor", {}).values()),
            "citation_count": len(citations),
            "entity_mentions": entity_counts,
            "citation_domains": dict(sorted(domain_counts.items())),
            "models": sorted({raw_response.model_id for raw_response in raw_responses}),
            "generated_at": _utc_now().isoformat(),
        }

    def _existing_extraction_run(
        self,
        raw_response_id: UUID,
        extraction_version: str,
    ) -> models.ExtractionRun | None:
        return self._session.scalar(
            select(models.ExtractionRun)
            .where(models.ExtractionRun.raw_response_id == raw_response_id)
            .where(models.ExtractionRun.extraction_version == extraction_version)
        )

    def _existing_summary(
        self,
        *,
        brand_id: UUID,
        run_batch_id: UUID,
        extraction_version: str,
    ) -> models.VisibilitySummary | None:
        return self._session.scalar(
            select(models.VisibilitySummary)
            .where(models.VisibilitySummary.brand_id == brand_id)
            .where(models.VisibilitySummary.run_batch_id == run_batch_id)
            .where(models.VisibilitySummary.extraction_version == extraction_version)
        )

    def _delete_derived_rows(self, extraction_run_id: UUID) -> None:
        self._session.execute(
            delete(models.ExtractedMention).where(
                models.ExtractedMention.extraction_run_id == extraction_run_id
            )
        )
        self._session.execute(
            delete(models.ExtractedCitation).where(
                models.ExtractedCitation.extraction_run_id == extraction_run_id
            )
        )

    def _raw_responses_for_batch(
        self,
        run_batch_id: UUID,
    ) -> list[models.VisibilityRawResponse]:
        return self._list(
            select(models.VisibilityRawResponse)
            .join(
                models.VisibilityRunItem,
                models.VisibilityRawResponse.run_item_id == models.VisibilityRunItem.id,
            )
            .where(models.VisibilityRunItem.run_batch_id == run_batch_id)
            .order_by(models.VisibilityRawResponse.created_at, models.VisibilityRawResponse.id)
        )

    def _require_raw_response(self, raw_response_id: UUID) -> models.VisibilityRawResponse:
        item = self._session.get(models.VisibilityRawResponse, raw_response_id)
        if item is None:
            raise NotFoundError("raw response not found")
        return item

    def _require_run_item(self, run_item_id: UUID) -> models.VisibilityRunItem:
        item = self._session.get(models.VisibilityRunItem, run_item_id)
        if item is None:
            raise NotFoundError("run item not found")
        return item

    def _require_run_batch(self, run_batch_id: UUID) -> models.VisibilityRunBatch:
        item = self._session.get(models.VisibilityRunBatch, run_batch_id)
        if item is None:
            raise NotFoundError("run batch not found")
        return item

    def _commit(self) -> None:
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise ConflictError("insights write violates a uniqueness constraint") from error

    def _list[T](self, statement: Select[tuple[T]]) -> list[T]:
        return list(self._session.execute(statement).scalars().all())


def _utc_now() -> datetime:
    return datetime.now(UTC)
