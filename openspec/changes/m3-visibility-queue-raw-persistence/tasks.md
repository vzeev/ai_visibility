# M3 Tasks

## Contracts

- [x] Extend OpenAPI for run creation, queue claim, item completion/failure, and
  raw response items.
- [x] Keep database contract aligned with implemented queue/raw behavior.

## Backend

- [x] Add visibility ORM models and read-only config projections.
- [x] Add visibility DB session dependency.
- [x] Add visibility repository.
- [x] Implement run creation from config snapshots.
- [x] Implement queue state and item claiming.
- [x] Implement item failure/retry/throttle transitions.
- [x] Implement raw response completion and idempotency.
- [x] Implement raw response search and pagination.

## Verification

- [x] Add visibility-service API tests.
- [x] Add opt-in Postgres/Alembic integration test.
- [x] Run service, integration, pre-commit, and aggregate checks.

## Documentation

- [x] Update README/OpenSpec/progress artifacts with M3 status and commands.
