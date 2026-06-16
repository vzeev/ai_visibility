# M3 Design

## Runtime Shape

```text
visibility-service HTTP routes
  -> Pydantic DTOs
  -> VisibilityRepository
  -> SQLAlchemy session
  -> config.* read-only snapshot projection
  -> visibility.* queue and raw tables
```

## Key Decisions

- Visibility-service owns run batches, run items, raw responses, and model
  errors.
- Config-service remains config truth owner. Visibility-service uses read-only
  projection models for snapshot reads instead of importing config-service
  internals.
- Run creation snapshots active prompt versions and enabled models at the time
  the run is created.
- Run item idempotency keys use the existing deterministic helper and a snapshot
  hash.
- Raw response writes use the provider-neutral `AIResponse` DTO.
- Duplicate completion with the same raw response returns the existing raw row.
- Integration tests are opt-in through `AI_VISIBILITY_TEST_DATABASE_URL`.

## Verification

- Service tests use SQLite with attached `config` and `visibility` schemas.
- Integration tests use Alembic-backed Postgres when the test DB URL is set.
- Pre-commit verifies formatting, typing, Bandit, skeleton, and unit/service
  suites.
