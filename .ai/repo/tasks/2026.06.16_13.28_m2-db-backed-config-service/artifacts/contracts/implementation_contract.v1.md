# Implementation Contract v1: M2 DB-Backed Config Service

## Objective

Replace config-service placeholder responses with DB-backed configuration APIs
for the config objects needed before visibility execution.

## User Premise Check

- user_premise_check: `accepted`
- basis: user approval to implement M2 after M2 was proposed as the next task.
- confidence: `high`
- challenge_required: `no`

## In Scope

- SQLAlchemy ORM models for M2 config tables.
- Config repository/service layer for:
  - brands
  - competitors
  - products
  - prompt sets
  - prompts and active prompt versions
  - providers
  - provider credentials as write-only token metadata
  - rate-limit policies
  - model registry entries
- FastAPI routes for the above.
- Pydantic request/response DTOs aligned to `contracts/openapi.yaml`.
- DB session dependency using the shared database URL.
- Service tests using an isolated test database setup.
- Integration test scaffold for Postgres/Alembic behavior, skipped unless an
  integration DB URL is provided.
- OpenSpec M2 change artifacts and README command/documentation updates when
  needed.

## Out Of Scope

- Real OpenAI calls.
- Visibility run creation from config snapshots.
- Full UI integration for config CRUD.
- Production-grade external secret vault.
- Auth/RBAC.
- Per-service DB login roles.

## Acceptance Criteria

- Config-service list/create endpoints persist and read from a database session.
- Provider credentials accept a token but return only redacted metadata.
- Prompt creation creates version 1 and prompt update creates the next active
  version without returning stale active text.
- Rate-limit policies support provider defaults and model overrides.
- Model registry entries can be created/listed and enabled for visibility.
- Service tests cover the main API behavior.
- Integration test path exists and is safe to skip when no Postgres test URL is
  configured.
- Existing quality scripts still pass.

## Verification Method

- `poetry run test-service`
- `poetry run test-integration`
- `poetry run precommit --files ...` over changed files
- `poetry run test-all` if runtime cost remains reasonable

## Dependencies And Prerequisites

- M1 schema and contracts exist.
- Poetry environment is installed.
- `PROCESSOR_ARCHITECTURE=AMD64` may be required for Poetry install on this
  Windows machine due local platform metadata behavior.

## Risks And Likely Failure Modes

- SQLAlchemy schema-qualified table names need special handling in SQLite tests.
- Token persistence must not leak token values through responses or reprs.
- Empty integration test suites must continue to behave as a clean skip.
- OpenAPI and database contracts can drift from route/DTO behavior if not
  updated alongside code.

## Evidence Ledger

- claim: M1 database contract already defines config tables.
  claim_type: `repo_fact`
  source_or_artifact: `contracts/database.sql`
  verification_status: `verified`
- claim: M1 OpenAPI already defines brands, prompts, credentials, and rate-limit
  endpoints.
  claim_type: `repo_fact`
  source_or_artifact: `contracts/openapi.yaml`
  verification_status: `verified`
- claim: M2 should be implemented before visibility execution.
  claim_type: `inference`
  source_or_artifact: architecture decision register and user approval.
  verification_status: `verified`

## Domain Boundary

Config-service records are durable configuration truth. Provider token values are
write-only inputs; read APIs return metadata and redacted fingerprints only.
Raw visibility evidence and derived insights remain out of scope for this slice.

## Approval Status

- approved_by_user: `yes`
- approval_message: "ok, now implement M2"
- version_history:
  - v1: initial M2 implementation contract.
