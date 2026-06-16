# Implementation Contract v1: M3 Visibility Queue And Raw Persistence

## Objective

Implement visibility-service as the owner of run batches, queue state, raw model
responses, retry/error recording, idempotent raw writes, and raw-response
search/pagination.

## User Premise Check

- user_premise_check: `accepted`
- basis: user approval to implement M3 after M3 was proposed as the next step.
- confidence: `high`
- challenge_required: `no`

## In Scope

- SQLAlchemy visibility ORM models for run batches, run items, raw responses,
  and model errors.
- Read-only config projections inside visibility-service for snapshot creation.
- Visibility repository/session layer.
- Run creation from `brand_id`, `prompt_set_id`, `sample_count`, and
  `max_attempts`.
- Immutable config snapshot captured on each run batch.
- Run item expansion for active prompt versions times enabled visibility models.
- Queue state counts.
- Queue item claiming with leases and attempt counts.
- Run item failure recording with retry/throttle/fail state transitions.
- Raw response persistence using the provider-neutral `AIResponse` DTO.
- Raw response idempotency using existing deterministic helpers.
- Raw response list/search/pagination API.
- Service tests and opt-in Postgres/Alembic integration tests.

## Out Of Scope

- Real OpenAI or provider network calls.
- Worker process loop.
- Redis/Celery.
- Insights extraction.
- React UI wiring to the queue/raw APIs.
- Production auth/RBAC.

## Acceptance Criteria

- Creating a run snapshots config and creates one run item for each active prompt
  version, enabled model, and sample index.
- Queue state reflects pending/running/succeeded/failed/throttled item counts.
- Claiming an item moves it to running and increments attempt count.
- Completing an item persists a raw response and marks the item succeeded.
- Repeating the same completion returns the existing raw response instead of
  creating a duplicate.
- Retryable failure before max attempts returns the item to pending or throttled.
- Exhausted or non-retryable failure marks the item failed and records an error.
- Raw responses can be searched and paginated.
- Service and integration tests verify the behavior.

## Verification Method

- `poetry run test-service`
- `poetry run test-integration`
- Real Postgres integration through `docker-compose.test.yml` when available.
- `poetry run precommit --files ...` over changed M3 files.
- `poetry run test-all`

## Risks And Likely Failure Modes

- SQLite service tests need attached `config` and `visibility` schemas.
- Raw response idempotency must not accidentally depend on mutable run state.
- Config snapshot creation must not import config-service internals.
- Postgres integration must not leave Docker containers running.

## Evidence Ledger

- claim: M2 config-service persists config needed by M3 snapshots.
  claim_type: `repo_fact`
  source_or_artifact: `apps/config_service/app/db/**`
  verification_status: `verified`
- claim: M1 database contract already defines visibility queue and raw response
  tables.
  claim_type: `repo_fact`
  source_or_artifact: `contracts/database.sql`
  verification_status: `verified`
- claim: Raw idempotency helpers already exist.
  claim_type: `repo_fact`
  source_or_artifact: `apps/shared/ai/idempotency.py`
  verification_status: `verified`

## Domain Boundary

Run batches capture immutable config snapshots. Raw responses are external model
evidence and must remain separate from derived insight truth. Duplicate raw
completion attempts must return existing evidence or fail cleanly without
creating conflicting raw records.

## Approval Status

- approved_by_user: `yes`
- approval_message: "ok, implement m3"
- version_history:
  - v1: initial M3 implementation contract.
