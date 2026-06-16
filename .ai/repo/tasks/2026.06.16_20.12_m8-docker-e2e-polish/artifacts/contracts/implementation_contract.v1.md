# Implementation Contract v1 - M8 Docker E2E Polish

## Objective

Provide a reproducible Docker-backed demo path proving the complete Brandlight AI visibility loop:
configuration setup, visibility run creation, fake-provider worker execution, raw response persistence, insights extraction, and API/UI-readable results.

## User Premise Check

- user_premise_check: accepted
- basis: user_instruction plus completed M1-M7 milestones
- confidence: high
- challenge_required: no

## In Scope

- Add a deterministic Brandlight demo seed path for config data and prompts.
- Add an end-to-end smoke command that can run against a Postgres database and exercise config, visibility, worker, and insights layers.
- Polish Docker/local service wiring needed for that flow, including service URLs and CORS defaults for the Vite UI.
- Add or update scripts in `pyproject.toml` for the M8 smoke workflow.
- Add focused tests for the smoke workflow and any runtime wiring introduced by this slice.
- Update README, OpenSpec tasks/specs, skeleton checks, and task audit artifacts.

## Out of Scope

- Real OpenAI API calls in the smoke path; the M8 proof must be deterministic and cost-free through the fake provider.
- Production-grade orchestration, retry queues, or distributed workers beyond the current database queue.
- Authentication/RBAC.
- New UI design beyond ensuring existing UI can read the Docker/local API path.

## Acceptance Criteria

1. A single repo command can seed demo Brandlight config, create a visibility run, process fake-provider responses, run insights extraction, and verify non-empty raw and insights outputs.
2. The smoke path is idempotent enough for repeated local runs without duplicate durable config records or raw response conflicts.
3. Docker Compose service definitions expose config, visibility, insights, worker, Postgres, and web in a coherent local network.
4. Browser clients on Vite local origins can call backend services through configured CORS defaults.
5. Automated tests cover the new smoke/demo path or its core orchestration logic.
6. README/OpenSpec document how to start the stack and run the smoke workflow.

## Verification Method

- Unit/service tests for new orchestration helpers and CORS behavior.
- Docker-backed integration test or smoke script against Postgres.
- `poetry run precommit`
- `poetry run test-all`
- Docker Compose config validation.
- Browser runtime validation if a UI behavior change is material and the browser tool is available; otherwise record the tool blocker.

## Dependencies and Prerequisites

- Existing M1-M7 code, migrations, and tests are available.
- Docker Desktop/Postgres are available for full integration verification.
- Fake provider remains the default deterministic worker path.

## Risks and Likely Failure Modes

- Port collisions with local services on 8001-8003 or 5173.
- Docker startup timing can make smoke checks flaky without explicit readiness handling.
- CORS could accidentally become too broad if defaults are not scoped to local demo origins.
- Idempotency must avoid duplicate config rows while preserving raw response uniqueness constraints.

## Evidence Ledger

| Claim | Claim Type | Source Or Artifact | Verification Status |
| --- | --- | --- | --- |
| M8 should prove config-to-insights flow end to end. | user_instruction | user request and next-step summary | verified |
| OpenSpec is the repo durable feature source. | repo_fact | `.ai/system/development/flows/openspec-feature-implementation.md`, `openspec/` | verified |
| Fake provider should be used for deterministic smoke verification. | repo_fact | M4/M5 worker milestones and contract | partially_verified pending code inspection |

## Open Questions or Assumptions

- The smoke command may run against either `AI_VISIBILITY_DATABASE_URL` or `AI_VISIBILITY_TEST_DATABASE_URL`; implementation should make this explicit and safe for local/demo use.
- The final stack may still require the operator to start Docker Compose before running the smoke command.

## Approval Status and Version History

- v1: approved for implementation by user message "ok, implement m8" on 2026-06-16.

