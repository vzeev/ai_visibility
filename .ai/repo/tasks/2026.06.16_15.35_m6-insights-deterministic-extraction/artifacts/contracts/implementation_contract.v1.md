# M6 Implementation Contract V1

## Objective

Implement deterministic insights extraction over stored raw visibility responses,
including versioned extraction runs, evidence-linked mention/citation rows, and
run-batch summaries.

## User Premise Check

- user_premise_check: `accepted`
- basis: accepted architecture, completed visibility collection milestones, and
  existing `insights.*` SQL contract.
- confidence: `high`
- challenge_required: `yes`; M6 creates derived truth, so lineage and
  recomputability are explicit acceptance criteria.

## In Scope

- Add insights-service ORM models, session wiring, repository, schemas, and API
  routes.
- Add deterministic extraction for brand aliases, brand names, competitor names,
  URLs, domains, sentiment labels, and aggregate summary counts.
- Make extraction idempotent per `(raw_response_id, extraction_version)`.
- Persist evidence JSON that references raw response IDs and text offsets.
- Build versioned run-batch summaries linked to raw responses and extraction
  runs.
- Add unit, service, and Postgres-backed integration tests.
- Update OpenSpec tasks, skeleton checks, README, and task audit artifacts.

## Out Of Scope

- React UI implementation.
- LLM-based or structured-output extraction.
- Background scheduler or long-running insights worker orchestration.
- Mutating `visibility.raw_responses` or rewriting historical raw evidence.
- Adding new database tables beyond the existing initial foundation schema unless
  validation proves a schema gap.

## Acceptance Criteria

1. A client can trigger extraction for a raw response and receive a completed
   extraction run containing deterministic mentions and citations.
2. A client can trigger extraction for a run batch and receive a versioned
   visibility summary for the batch.
3. Repeating extraction for the same raw response and version does not create a
   duplicate extraction run or duplicate derived rows.
4. Every mention and citation evidence payload includes the originating
   `raw_response_id` and offset/source metadata.
5. Summaries include raw response IDs, extraction run IDs, aggregate mention
   counts, citation counts, and model coverage.
6. Raw visibility records are read-only inputs throughout M6.

## Verification Method

- Unit tests for deterministic mention matching, citation parsing, sentiment,
  and summary aggregation.
- Service tests for extraction API behavior and idempotent reruns using SQLite
  attached schemas.
- Integration tests against the Alembic-managed Postgres test schema.
- `poetry run test-unit`
- `poetry run test-service`
- `poetry run test-integration`
- real Postgres `test-integration` when Docker is available.
- `poetry run precommit`
- `poetry run test-all`

## Dependencies And Prerequisites

- M3 raw response persistence and queue state.
- M4/M5 worker output path that creates raw responses.
- Initial foundation migration tables:
  `insights.extraction_runs`, `insights.extracted_mentions`,
  `insights.extracted_citations`, and `insights.visibility_summaries`.

## Risks And Likely Failure Modes

- Cross-schema SQLAlchemy mappings can break SQLite service tests if foreign keys
  are modeled too aggressively.
- Deterministic matching can overcount aliases without stable duplicate rules.
- Summary data can become misleading if it omits raw response/extraction run
  references.
- Idempotent reruns can accidentally duplicate child rows if existing completed
  runs are not reused.

## Evidence Ledger

- claim: Initial migration already defines required `insights.*` tables.
  claim_type: `repo_fact`
  source_or_artifact: `alembic/versions/20260616_0924_initial_foundation.py`
  verification_status: `verified`
- claim: Existing insights service is currently a skeleton route returning empty
  summaries.
  claim_type: `repo_fact`
  source_or_artifact: `apps/insights_service/app/api/routes.py`
  verification_status: `verified`
- claim: M6 should not include React UI work.
  claim_type: `user_instruction`
  source_or_artifact: `openspec/changes/m6-insights-deterministic-extraction/proposal.md`
  verification_status: `verified`

## Domain Boundary

- Raw visibility responses remain immutable evidence owned by the visibility
  service.
- Insights rows are derived, versioned state owned by the insights service.
- Derived rows must be explainable through evidence JSON and references to raw
  response IDs.

## Approval Status

- human_approval_to_implement: `approved`
- approval_source: user said `ok, implement m6`.

## Version History

- `v1`: initial M6 contract.
