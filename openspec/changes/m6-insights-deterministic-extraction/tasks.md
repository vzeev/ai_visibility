# M6 Tasks

## Backend

- [x] Add insights-service database models, repository, and schemas for
      extraction runs, mentions, citations, and summaries.
- [x] Add deterministic extraction logic for brand/competitor mentions,
      citations/domains, and evidence-linked summary aggregation.
- [x] Add insights-service APIs to trigger extractions and query results.
- [x] Preserve extraction versioning and idempotent reruns against immutable raw
      responses.
- [x] Update contracts/skeleton checks as needed for the shipped M6 slice.

## Verification

- [x] Add unit tests for deterministic extraction behavior.
- [x] Add service tests for extraction APIs and evidence persistence.
- [x] Add Postgres-backed integration coverage for insights extraction.
- [x] Run unit, service, integration, pre-commit, and relevant aggregate checks.

## Documentation

- [x] Update README and OpenSpec with M6 status and usage notes.
