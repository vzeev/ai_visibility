# Implementation Contract v1 - M11 OpenAI Model Sync

## Objective

Add a safe, testable OpenAI model registry synchronization path so config-service can discover currently available OpenAI models and upsert them into `config.model_registry`.

## User Premise Check

- user_premise_check: accepted_with_scope_constraint
- basis: user request to implement M11, M10 reconciliation gap, architecture delivery plan
- confidence: medium
- challenge_required: yes

M11 was not explicitly predeclared in OpenSpec. The inferred slice is provider model sync because M10 left "Provider model sync" unimplemented, and the architecture says OpenAI model availability changes and the registry must be dynamic.

## In Scope

- Add provider-neutral model discovery DTO/protocol and an OpenAI implementation using `GET /v1/models`.
- Add config repository upsert logic that:
  - creates newly discovered models as available but disabled for visibility by default
  - updates existing discovered model metadata while preserving `enabled_for_visibility` and rate-limit links
  - marks previously known provider models unavailable when missing from the latest discovery response
- Add `POST /api/v1/providers/{provider_id}/models/sync`.
- Add Config tab API/client support and a sync action for OpenAI providers.
- Update OpenAPI, OpenSpec, README, skeleton checks, tests, and task artifacts.

## Out Of Scope

- Calling OpenAI in automated tests.
- Enabling all discovered models automatically.
- Model capability inference beyond storing safe provider metadata.
- Credential testing UI.
- Edit/delete model management.
- Auth/RBAC.

## Acceptance Criteria

1. The OpenAI model discovery client sends `GET /v1/models` with bearer auth and parses `id`, `owned_by`, and metadata into normalized discovered-model records.
2. Missing OpenAI credentials fail closed without logging or returning token values.
3. `POST /api/v1/providers/{provider_id}/models/sync` discovers models for OpenAI providers and returns sync counts plus redacted model registry records.
4. New discovered models are `is_available=true` and `enabled_for_visibility=false` by default.
5. Existing discovered models preserve `enabled_for_visibility` and `rate_limit_policy_id`.
6. Previously known provider models absent from the latest discovery response are marked `is_available=false`.
7. Config tab can trigger OpenAI model sync and refresh the model list.
8. Relevant unit/service/frontend checks and `poetry run precommit` pass.

## Verification Method

- Unit tests for OpenAI model discovery using `httpx.MockTransport`.
- Service tests for sync endpoint using a fake discovery client and SQLite-backed config schema.
- Frontend typecheck/build via existing web checks.
- Contract/skeleton validation through `poetry run check-skeleton`.
- Repo hooks through `poetry run precommit`.

## Dependencies And Prerequisites

- Existing provider registry and model registry tables from M2.
- Existing OpenAI credential resolver and `.env` bootstrap from M5 follow-up.
- Official OpenAI OpenAPI documents `GET /v1/models` as listing currently available models with owner/availability metadata.

## Risks And Likely Failure Modes

- Accidentally enabling every discovered model could make demos costly or noisy.
- Model sync must not leak `OPENAI_API_KEY`.
- Dynamic model lists can include non-chat or deprecated models; sync stores availability only and leaves operator enablement explicit.
- Docker worker `.env` mount remains a local-demo compromise, not production secret handling.

## Evidence Ledger

| Claim | Claim type | Source or artifact | Verification status |
|---|---|---|---|
| OpenAI exposes `GET /v1/models` to list currently available models. | external_fact | OpenAI OpenAPI spec for `/models` via docs MCP | verified |
| M10 left provider model sync out of scope. | repo_fact | `.ai/repo/tasks/2026.06.16_21.32_m10-config-authoring-ui/artifacts/reconciliation/final_reconciliation.md` | verified |
| Config-service already stores model registry records. | repo_fact | `apps/config_service/app/db/models.py` and `contracts/database.sql` | verified |

## Approval Status And Version History

- v1: approved by user message "now implement m11" on 2026-06-17.

