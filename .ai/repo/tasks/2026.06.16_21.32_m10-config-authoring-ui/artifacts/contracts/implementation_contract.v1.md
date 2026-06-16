# Implementation Contract v1 - M10 Config Authoring UI

## Objective

Turn the Config tab from a read-only dashboard into a safe authoring surface for demo-critical configuration that already exists in backend contracts: prompts, provider credentials, and provider/model rate limits.

## User Premise Check

- user_premise_check: accepted_with_scope_constraint
- basis: user request to implement M10, accepted architecture backlog, existing config-service POST APIs
- confidence: medium
- challenge_required: yes

M10 was not explicitly defined in the repository. The inferred next slice is accepted because it directly addresses the user's earlier configuration concerns and avoids new backend scope.

## In Scope

- Add typed API client methods for:
  - creating provider credentials with write-only token input
  - creating prompts
  - creating new prompt versions
  - creating rate-limit policies
  - creating models if needed by the rate-limit workflow
- Add Config tab forms for:
  - adding/rotating provider credentials without reading token values back
  - adding a prompt to a prompt set
  - adding a new version to an existing prompt
  - adding provider-level or model-level rate-limit policies
- Refresh Config tab data after successful writes.
- Show inline success/error states.
- Preserve redacted credential readback and do not log/store token values in frontend state beyond the form submission lifecycle.
- Update OpenSpec, README, skeleton checks, and task audit artifacts.

## Out Of Scope

- New backend endpoints unless an existing API contract blocks the UI.
- Credential testing against real providers.
- Real OpenAI model sync.
- Editing/deleting existing records.
- Auth/RBAC.
- Browser automation if the local Browser plugin remains blocked.

## Acceptance Criteria

1. Config tab can create a provider credential by selecting an existing provider, entering a label, and entering a token.
2. Credential list refreshes after creation and displays only redacted metadata from the backend.
3. Config tab can create a prompt under an existing prompt set.
4. Config tab can create a new active version for an existing prompt.
5. Config tab can create provider-level or model-level rate-limit policies.
6. Forms have loading, success, validation, and error states that do not overlap on mobile widths.
7. Existing read-only Config summary remains intact.
8. `poetry run web-check`, `npm run build`, `poetry run precommit`, and relevant service checks pass.

## Verification Method

- TypeScript typecheck through `poetry run web-check`.
- Vite production build through `npm run build`.
- Repo hooks through `poetry run precommit`.
- Service tests for existing config behavior through `poetry run test-service`.
- HTTP smoke or demo e2e if the local stack is available.

## Dependencies And Prerequisites

- Existing config-service POST APIs from M2.
- Existing React/Vite API client and Config tab from M7/M9.
- Existing Docker/demo data remains optional for static verification.

## Risks And Likely Failure Modes

- Credential token values could accidentally be rendered or retained after submission.
- Rate-limit form could conflict with existing provider/model policies.
- Config tab could become too dense for interview demo scanning.
- Browser validation may remain blocked by the local Browser plugin runtime issue.

## Evidence Ledger

| Claim | Claim type | Source or artifact | Verification status |
|---|---|---|---|
| Config-service already has POST endpoints for prompts, credentials, rate limits, and models. | repo_fact | `apps/config_service/app/api/routes.py` | verified |
| Provider credential responses are redacted metadata only. | repo_fact | `apps/config_service/app/schemas/http.py` | verified |
| User requested UI-configurable API tokens, prompts, and per-model rate limits earlier. | user_instruction | conversation context and architecture artifacts | verified |

## Approval Status And Version History

- v1: approved for implementation by user message "ok, now implement m10" on 2026-06-16.

