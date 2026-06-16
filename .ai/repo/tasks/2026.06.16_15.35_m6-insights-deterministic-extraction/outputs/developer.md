# Developer Output

## Scope Implemented

- Added deterministic extraction engine in
  `apps/insights_service/app/domain/extractor.py`.
- Added insights-service ORM projections, session wiring, and repository in
  `apps/insights_service/app/db/`.
- Replaced placeholder insights API with extraction and summary routes.
- Added unit, service, and Postgres integration tests.
- Updated OpenAPI, README, skeleton checks, and OpenSpec checklist.

## Key Decisions

- Reuse completed extraction runs for same raw response/version idempotency.
- Skip mention matches that fall inside URL spans so citations do not inflate
  mention counts.
- Keep cross-schema foreign keys out of ORM projections for SQLite service-test
  compatibility; Postgres constraints remain in Alembic.
- Keep M6 synchronous through API endpoints; scheduler/worker orchestration is
  future work.

## Checks Run

- `poetry run test-unit` passed with 17 tests.
- `poetry run test-service` passed with 14 tests.
- `poetry run test-integration` passed skip path with 4 skipped tests.
- Docker-backed `poetry run test-integration` passed with 4 tests.
- `poetry run precommit` passed.
- `poetry run test-all` passed.

## Blockers And Risks

- No blockers.
- Existing non-blocking warnings remain: FastAPI/Starlette TestClient deprecation
  and Alembic `path_separator` deprecation.

## Handoff

completed_work: M6 implementation and verification completed.
key_decisions: deterministic-only extraction, versioned idempotent runs,
evidence-linked summaries.
deviations_from_plan: none.
open_concerns: no real UI uses these APIs yet.
important_findings: URL spans must be excluded from mention matching.
recommended_next_actions: reviewer/security/QA closure, then M7 UI/API polish
planning.
verification_status: implemented and verified.
