# QA Output

stage: `qa`
status: `approved`

## Acceptance Mapping

- Run creation from config snapshot: covered by visibility service tests and
  Postgres integration.
- Queue state and claiming: covered by service tests.
- Idempotent raw persistence: covered by repeated completion test.
- Retry/failure recording: covered by retryable rate-limit failure test.
- Raw search and pagination: covered by raw response search test.

## Verification Evidence

- `poetry run test-service`: pass, 8 tests.
- `poetry run test-integration`: pass as skip without DB URL.
- Real Postgres integration: pass, 2 tests total with M2/M3 integration suite.
- `poetry run precommit --files ...`: pass.
- `poetry run test-all`: pass.

## Residual Notes

- UI/browser validation was not run because M3 is backend/API behavior only.
- Starlette TestClient deprecation warnings are non-blocking.
