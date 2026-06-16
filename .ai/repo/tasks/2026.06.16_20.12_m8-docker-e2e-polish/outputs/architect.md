# Architect Output - M8 Docker E2E Polish

## Scope

Reviewed M8 contract, OpenSpec package, Docker Compose, service app entrypoints, repository APIs, worker flow, insights extraction flow, tests, README, and skeleton checks.

## Premise Check

- user_premise_check: accepted
- basis: repository_evidence and user-approved milestone sequence
- confidence: high
- challenge_required: no

## Implementation Plan

1. Add a small shared CORS helper used by config, visibility, and insights FastAPI apps.
2. Fix Docker Compose web env names to match `apps/web/src/lib/api.ts` and pass local CORS origins to backend services.
3. Add `scripts.ai_visibility_tools.demo_e2e` with:
   - idempotent Brandlight config seeding,
   - a `run_brandlight_demo_smoke` orchestration function,
   - an operator CLI that can run Alembic migrations and print a JSON summary.
4. Add `demo-e2e` Poetry script.
5. Add service tests for CORS and the demo orchestration on SQLite schemas, and preserve Docker-backed integration execution through existing integration harness.
6. Update README, skeleton checks, OpenSpec tasks, and role audit artifacts.

## Test Strategy

- Service tests:
  - CORS local Vite preflight across all backend apps.
  - Demo seed idempotency and smoke orchestration against in-memory SQLite attached schemas.
- Integration:
  - Existing Docker-backed `poetry run test-integration`.
  - New `poetry run demo-e2e --skip-migrations` or migrated execution against Postgres when Docker is available.
- Static/full checks:
  - `poetry run precommit`
  - `poetry run test-all`
  - `docker compose config`

## Risks

- SQLite service tests can mask Postgres-specific Alembic issues, so Docker-backed integration remains required.
- CORS should stay local-demo scoped and configurable rather than broad production policy.
- Demo config should be reused/updated, while visibility runs remain intentionally new runtime evidence.

## Handoff

completed_work: Derived implementation plan from OpenSpec and code inspection.
key_decisions: Use real repositories and worker/insights classes; add shared CORS helper; keep real OpenAI out of M8 smoke.
deviations_from_plan: none.
open_concerns: Docker runtime availability must be verified later.
important_findings: Compose web env names are stale relative to Vite config variable names.
recommended_next_actions: Implement shared CORS, demo smoke module, tests, docs, and verification.
verification_status: planned, not yet executed.

