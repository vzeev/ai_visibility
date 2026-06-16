# M6 Insights Deterministic Extraction

## Summary

Implement the first real insights-service backend slice so stored raw visibility
responses can be deterministically converted into versioned, evidence-linked
derived records.

## Goals

- Persist `insights.extraction_runs`, `insights.extracted_mentions`,
  `insights.extracted_citations`, and `insights.visibility_summaries` through
  the insights service.
- Add deterministic extraction for brand mentions, competitor mentions,
  citations/domains, and summary counts from existing raw responses.
- Version every extraction result and keep all derived records traceable back to
  immutable `visibility.raw_responses` rows.
- Expose backend APIs to trigger extraction and read extraction results without
  adding any React UI work.

## Non-Goals

- No React/Vite UI implementation for the Insights tab.
- No LLM-based or structured-output extraction in this milestone.
- No mutation of raw visibility data.
- No scheduler or long-running insights worker orchestration beyond the bounded
  backend slice needed to process extractions.

## Architecture References

- `.ai/repo/tasks/2026.06.16_08.02_brandlight-visibility-architecture/artifacts/spec/architecture_proposal.md`
- `apps/visibility_service/app/db/models.py`
- `apps/visibility_service/app/db/repository.py`
- `contracts/database.sql`
- `contracts/openapi.yaml`
