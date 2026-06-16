# Developer Output - M8 Docker E2E Polish

## Scope Implemented

- Added shared local CORS helper and wired config, visibility, and insights FastAPI apps through it.
- Corrected Docker Compose web environment variable names and passed CORS origins to backend containers.
- Added `scripts.ai_visibility_tools.demo_e2e` with deterministic Brandlight config seed, worker execution, insights extraction, and JSON smoke output.
- Added `poetry run demo-e2e`.
- Added a forward Alembic migration for `config.model_registry.created_at` and aligned `contracts/database.sql`.
- Added service tests for CORS and demo smoke/idempotent seeding.
- Made Postgres integration tests reset test schemas before Alembic upgrades so they remain repeatable after demo smoke runs.
- Updated README, `.env.example`, skeleton checks, OpenSpec tasks, and task artifacts.

## Premise Check

- user_premise_check: accepted
- basis: implementation contract and repository verification
- confidence: high
- challenge_required: no

## Commands Run

- `python -m unittest tests.services.test_demo_e2e tests.services.test_cors` failed because bare `python` resolved to a dependency-less Windows install manager; invalid repo environment.
- `c:\Users\vladi\.local\bin\poetry.exe run test-service` passed.
- `docker-compose -f docker-compose.yml config` passed.
- `docker-compose -f docker-compose.test.yml config` passed.
- `docker-compose -f docker-compose.test.yml up -d postgres-test` passed.
- `c:\Users\vladi\.local\bin\poetry.exe run test-integration` passed with `AI_VISIBILITY_TEST_DATABASE_URL`.
- `c:\Users\vladi\.local\bin\poetry.exe run demo-e2e --database-url postgresql+psycopg://ai_visibility:ai_visibility_local@localhost:55432/ai_visibility_test` passed.
- `.venv\Scripts\python.exe -m ruff check apps scripts tests alembic` passed.
- `.venv\Scripts\python.exe -m ruff format --check apps scripts tests alembic` initially required formatting; fixed with Ruff.
- `c:\Users\vladi\.local\bin\poetry.exe run check-skeleton` passed.
- `c:\Users\vladi\.local\bin\poetry.exe run precommit` passed after replacing hardcoded fake token handling.
- `c:\Users\vladi\.local\bin\poetry.exe run test-all` passed with `AI_VISIBILITY_TEST_DATABASE_URL`.
- `docker-compose -f docker-compose.test.yml down` passed.

## Notes

- `poetry run demo-e2e` warns that the newly added entry point is not installed as a script until `poetry install` is run; execution still succeeds.
- Smoke counts can be higher than the minimal two prompt/model items when the database already contains other enabled visibility models, because run creation intentionally expands across all enabled models.

## Handoff

completed_work: Implemented M8 Docker-backed smoke path, CORS, compose polish, schema fix, tests, docs, and OpenSpec task state.
key_decisions: Use fake provider for deterministic smoke; preserve global enabled-model expansion; reset integration test schemas for repeatability.
deviations_from_plan: Added schema migration after Docker smoke exposed `model_registry.created_at` mismatch.
open_concerns: The demo command entry point warning goes away after `poetry install`; no runtime blocker.
important_findings: Existing integration tests were not isolated from demo-seeded enabled models; fixed with test schema reset.
recommended_next_actions: Move to final review/security/QA and closure.
verification_status: verified.

