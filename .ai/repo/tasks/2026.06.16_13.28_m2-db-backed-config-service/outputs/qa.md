# QA Output

stage: `qa`
status: `approved`

## Acceptance Mapping

- DB-backed config CRUD: covered by service API tests for brand, competitor,
  product, provider, rate-limit, and model registry persistence.
- Prompt versioning: covered by service API test that creates version 1 and then
  creates active version 2.
- Write-only credentials: covered by service API test that checks create/list
  response bodies do not contain the token.
- Integration path: covered by opt-in Postgres/Alembic integration test.

## Verification Evidence

- `poetry run test-service`: pass, 6 tests.
- `poetry run test-integration`: pass as skip without DB URL.
- Real Postgres integration with Docker Compose: pass, 1 test.
- `poetry run precommit --files ...`: pass.
- `poetry run test-all`: pass.

## Residual Notes

- Browser/UI validation was not run because M2 is backend/API persistence only.
- The Starlette TestClient deprecation warning is non-blocking.
