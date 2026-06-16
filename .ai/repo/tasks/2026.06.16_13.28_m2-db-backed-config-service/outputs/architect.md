# Architect Output

stage: `architect`
status: `completed`

## Scope

M2 implements DB-backed config-service behavior against existing M1 schema
truth. The slice intentionally stops before visibility run creation, real
provider calls, UI CRUD screens, auth/RBAC, and a production secret vault.

## Contract

- Implementation contract:
  `.ai/repo/tasks/2026.06.16_13.28_m2-db-backed-config-service/artifacts/contracts/implementation_contract.v1.md`
- Active OpenSpec change:
  `openspec/changes/m2-db-backed-config-service/`

## Key Decisions

- ORM models mirror `contracts/database.sql`; Alembic remains DDL owner.
- Route handlers are thin and delegate to `ConfigRepository`.
- Prompt text changes create new active prompt versions.
- Credential tokens are write-only request inputs; responses expose only
  metadata and redacted fingerprints.
- Postgres integration is opt-in through `AI_VISIBILITY_TEST_DATABASE_URL`.

## Verification Plan

- Service tests for HTTP and persistence behavior.
- Opt-in Postgres/Alembic integration test.
- Pre-commit stack and aggregate test command.
