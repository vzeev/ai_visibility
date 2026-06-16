# M4 Implementation Contract V1

## Objective

Implement a bounded visibility worker that claims queued run items, calls the
provider-neutral fake AI adapter, and persists raw responses or provider errors
through the M3 visibility repository.

## User Premise Check

- user_premise_check: `accepted`
- basis: M3 implemented queue/raw persistence and the shared fake provider
  adapter already exists.
- confidence: `high`
- challenge_required: `no`

## In Scope

- Add a public visibility repository method that builds an `AIRequest` from a
  claimed run item and its immutable config snapshot.
- Add worker code that processes one item or a bounded batch.
- Use the provider-neutral `AIProviderAdapter` contract.
- Use the fake provider adapter as the default implementation.
- Persist successful responses through `record_raw_response`.
- Persist adapter errors through `record_model_error`.
- Add unit/service tests for success, bounded batch processing, and retryable
  provider failure.
- Add an opt-in Postgres integration test for worker persistence.
- Update OpenSpec, README, skeleton checks, and task audit artifacts.

## Out Of Scope

- Real OpenAI or other provider network calls.
- Provider token lookup/decryption.
- Production scheduler, daemon supervisor, or infinite loop.
- Rate-limit execution engine.
- Insights extraction.
- UI changes.

## Acceptance Criteria

1. A worker can claim one pending visibility item and turn it into an
   `AIRequest` without relying on private repository internals.
2. A fake-provider response creates exactly one raw response and marks the item
   succeeded through existing M3 idempotency rules.
3. A bounded batch processes at most the requested number of items and stops
   early when the queue is empty.
4. A retryable provider error records a model error and leaves the item
   retryable according to M3 retry rules.
5. Automated service tests and opt-in Postgres integration tests cover the
   worker path.

## Verification Method

- `poetry run test-service`
- `poetry run test-integration` with no DB URL to verify skip behavior.
- `poetry run test-integration` against `docker-compose.test.yml` Postgres.
- `poetry run precommit --files ...` for changed files.
- `poetry run test-all`

## Dependencies And Prerequisites

- M3 visibility repository and Alembic schema are present.
- Config snapshot contains prompt/model metadata for queued items.
- Automated tests use fake adapters only.

## Risks And Likely Failure Modes

- Detached SQLAlchemy instances after claim/commit could lose needed metadata.
  The worker must build requests through a repository method in the active
  session.
- Provider key values from config may not match the fake adapter key. The worker
  must default safely to fake behavior while preserving provider/model metadata
  in raw evidence.
- Retry status must reuse M3 rules instead of inventing separate worker states.

## Evidence Ledger

- claim: M3 repository already supports item claim, raw completion, and error
  recording.
  claim_type: `repo_fact`
  source_or_artifact: `apps/visibility_service/app/db/repository.py`
  verification_status: `verified`
- claim: fake provider adapter already implements the shared provider contract.
  claim_type: `repo_fact`
  source_or_artifact: `apps/shared/ai/provider.py`
  verification_status: `verified`

## Open Questions Or Assumptions

- Assumption: M4 should preserve configured provider keys in raw evidence while
  using the fake adapter for execution.

## Approval Status And Version History

- v1 approved for implementation by user request: "ok, implement m4".
