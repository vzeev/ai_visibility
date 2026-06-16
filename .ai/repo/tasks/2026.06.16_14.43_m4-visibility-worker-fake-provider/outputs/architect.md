# Architect Output

## Scope

Defined M4 as a bounded worker execution slice on top of M3 queue/raw
persistence.

## Premise Check

- user_premise_check: `accepted`
- basis: M3 queue persistence exists, fake provider adapter exists, and user
  approved M4 implementation.
- confidence: `high`

## Key Decisions

- Keep queue state transitions and raw idempotency in `VisibilityRepository`.
- Add `VisibilityRepository.build_ai_request` as the public request-construction
  seam for workers.
- Use `FakeAIProviderAdapter` as the default execution path.
- Preserve configured provider/model metadata in requests and raw evidence.
- Keep worker execution bounded by `max_items`; no daemon loop in M4.

## Verification Plan

- Service tests for success, batch bounds, and retryable error.
- Opt-in Postgres integration test for Alembic-backed worker persistence.
- Pre-commit and aggregate `test-all`.

## Handoff

completed_work: implementation contract created and approved.
key_decisions: fake-provider worker only; no real provider or scheduler.
deviations_from_plan: none.
open_concerns: later slices need real provider token/rate-limit handling.
recommended_next_actions: implement worker and verify with service plus
integration tests.
verification_status: contract-only, implemented later by developer.
