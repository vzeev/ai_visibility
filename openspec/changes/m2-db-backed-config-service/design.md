# M2 Design

## Runtime Shape

```text
config-service HTTP routes
  -> Pydantic DTOs
  -> ConfigRepository
  -> SQLAlchemy session
  -> config.* Postgres tables
```

## Key Decisions

- Alembic and `contracts/database.sql` remain schema truth.
- SQLAlchemy ORM models mirror the existing config schema.
- API route handlers stay thin and delegate persistence to a repository.
- Prompt text updates create a new `config.prompt_versions` row and mark earlier
  versions inactive.
- Provider tokens are write-only request inputs. The service stores a stable
  local secret reference and redacted fingerprint, and responses never include
  the token.
- Integration tests are opt-in through a Postgres test database URL so local
  unit/service verification stays fast.

## Verification

- FastAPI service tests exercise DB-backed behavior through HTTP.
- Unit/service tests use isolated SQLAlchemy database setup.
- Integration tests verify migration-backed Postgres behavior when
  `AI_VISIBILITY_TEST_DATABASE_URL` is set.
