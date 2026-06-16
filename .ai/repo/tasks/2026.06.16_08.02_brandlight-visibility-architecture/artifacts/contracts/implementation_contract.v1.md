# Implementation Contract v1

status: `draft_pending_user_approval`
owner_role: `developer`
approving_role: `user`

## Objective

After user approval, create the first implementation slice for the AI visibility demo foundation without yet building the full product workflow.

## User Premise Check

- user_premise_check: `partially_supported`
- basis: user instruction, Brandlight notes, Finfrax repo reference, OpenAI API docs
- confidence: `medium`
- challenge_required: `yes`

The requested service shape is coherent for demonstrating architecture and delivery. The only challenged premise is "all available models": the implementation should discover models dynamically and require explicit enablement before execution.

## In-Scope Work For This Slice

- Initialize OpenSpec skeleton and one active change package.
- Initialize contracts skeleton:
  - `contracts/openapi.yaml`
  - `contracts/database.sql`
  - `contracts/enums.md`
- Initialize root Poetry project and local Python tooling.
- Create Docker Compose baseline with Postgres and migration container.
- Create Alembic skeleton and initial migration for foundational schemas.
- Create Python package skeletons for:
  - `apps/config_service`
  - `apps/visibility_service`
  - `apps/insights_service`
  - `apps/worker`
  - `apps/shared`
- Create React/Vite workspace skeleton under `apps/web`.
- Add verification command wrappers and test directory structure for unit, service, and integration tests.
- Add docs decision file describing accepted architecture decisions for the repo.

## Out Of Scope And Non-Goals

- No OpenAI runtime calls in the first foundation slice.
- No real queue worker behavior unless explicitly included by user after approval.
- No production auth/RBAC.
- No Redis/Celery unless user chooses that over Postgres queue.
- No full UI workflow beyond skeleton unless user expands the slice.
- No hard-coded current OpenAI model list.
- No secrets committed to the repository.

## Acceptance Criteria

1. Repo contains OpenSpec, contracts, docs, backend app, frontend app, migration, Docker, and test skeletons matching the approved architecture.
2. `docker compose config` succeeds for the local stack.
3. Alembic can run against local Postgres in the Compose stack.
4. Python unit-test command exists and passes at least skeleton/import checks.
5. Web build/test command exists for the Vite workspace.
6. OpenSpec active change documents the foundation behavior and task list.
7. Contracts declare the initial API/schema/enums before service code depends on them.
8. `.env.example` documents required local environment variables without secrets.

## Verification Method

- Static file/layout check with a repo script.
- `poetry run test-unit` or equivalent.
- `docker compose config`.
- Migration smoke test against Compose Postgres.
- `npm run build` and `npm run test` inside `apps/web`.
- OpenSpec validation command if OpenSpec CLI is available; otherwise record manual/spec-file validation.

## Dependencies And Prerequisites

- User approval of architecture.
- User decision on Postgres queue vs Redis/Celery for MVP.
- User decision on whether first implementation slice is skeleton-only or includes config API behavior.
- Local Poetry, Docker, Node/npm availability.
- OpenAI API key is not required for this slice.

## Risks And Likely Failure Modes

- Over-scoping the first slice into real behavior before foundation is stable.
- Contracts drifting behind code if implementation begins before contract files are written.
- Docker Compose startup failures from premature healthcheck complexity.
- Frontend tooling drift if web dependencies are not pinned enough for repeatable builds.

## Evidence Ledger

| Claim | Claim type | Source or artifact | Verification status |
|---|---|---|---|
| Finfrax uses root Poetry, FastAPI services, Alembic, Compose, and Vite app structure. | repo_fact | `artifacts/spec/source_summary.md` | verified |
| Brandlight-inspired demo should preserve raw AI answers and expose derived insight lineage. | user_instruction/source_note | Brandlight notes summary | verified as source note |
| OpenAI models should be dynamically discovered rather than hard-coded. | external_fact | OpenAI `/v1/models` OpenAPI spec | verified |
| Responses API is appropriate for model response capture. | external_fact | OpenAI `/v1/responses` OpenAPI spec | verified |
| Structured Outputs can support schema-constrained extraction where supported. | external_fact | OpenAI structured outputs guide | verified |

## Open Questions Or Assumptions

- Assumption: first implementation slice should be foundation-first.
- Question: should the first slice include a working config API after skeleton setup?
- Question: should the MVP include Redis/Celery or stay with Postgres queue?
- Question: should auth/RBAC be explicitly excluded until after the interview demo works?

## Approval Status And Version History

- v1 created as architecture-stage draft.
- user approval: pending.
- evidence_readiness: ready for architecture review, not ready for implementation until user approves.

## Invariant Summary

- Config is source of truth for planned runs.
- Raw visibility responses are immutable evidence.
- Insights are derived, versioned, and recomputable.
- UI summaries must link back to raw evidence.

## Boundary Map

- `config-service`: config truth.
- `visibility-service`: raw collection evidence and queue state.
- `insights-service`: derived extraction and summary truth.
- `worker`: execution mechanism, not domain truth owner.
- `web`: presentation and workflow surface, not truth owner.

## Truth-Boundary Description

Raw OpenAI output becomes durable evidence only when the visibility worker stores the request/response record. Derived insights become usable product data only after extraction logic validates and versions them. No insight should overwrite or reinterpret raw evidence in place.

## Downstream-Client Compatibility Note

Initial API contracts must make raw IDs, extraction versions, and pagination/filter parameters stable enough for the UI and integration tests. Later scoring changes should add fields or new versions instead of silently changing existing meanings.
