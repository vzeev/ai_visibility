# M12 Implementation Contract V1

status: `approved_by_user_request`
owner_role: `developer`
approving_role: `user`

## Objective

Add a repeatable demo validation layer around the existing Brandlight AI
visibility app: Cypress end-to-end tests, demo walkthrough scripts/docs, and
small UI/API polish needed to make the interview flow coherent.

## User Premise Check

- user_premise_check: `partially_supported`
- basis: user instruction plus repo state from M1-M11
- confidence: `high`
- challenge_required: `yes`

The repo already implements most of the demo workflow. The main remaining work
is validation and guided walkthrough. The request phrase "everything left" is
too broad if interpreted as production hardening or AI-assisted insight
extraction; this M12 slice is bounded to demo-readiness gaps with direct
verification.

## In-Scope Work For This Slice

- Create `openspec/changes/m12-demo-e2e-validation/` with proposal, design,
  tasks, and spec delta.
- Add Cypress to the React workspace.
- Add Cypress tests that validate the interview demo journey with deterministic
  API fixtures.
- Add root command wrappers for Cypress/demo validation.
- Add demo walkthrough docs based on the owner plan and the assistant proposal.
- Add a scriptable demo guide/check command that tells the operator what to run
  and verifies repo-local demo prerequisites where possible.
- Add small UI observability improvements needed by the demo:
  - stable selectors for E2E validation
  - run expansion visibility
  - model/result comparison summary where data is already available
  - clear deterministic vs AI-assisted insight wording
- Update README and skeleton checks.

## Out Of Scope And Non-Goals

- No production auth/RBAC.
- No deployment pipeline.
- No new secret-storage backend.
- No real external OpenAI calls in Cypress or automated tests.
- No claim that UI-entered credentials drive runtime OpenAI calls unless the
  runtime resolver is changed in this slice.
- No full AI-assisted insights implementation unless it can be done safely
  without changing the raw/derived truth boundary or adding untestable network
  behavior.

## Acceptance Criteria

1. OpenSpec M12 artifacts exist and describe the demo E2E behavior.
2. `apps/web` has Cypress configuration, scripts, fixtures or intercepts, and at
   least one E2E spec covering Overview, Config, Queue, Visibility, and Insights.
3. Root Poetry scripts expose demo validation and Cypress execution commands.
4. Demo walkthrough docs exist under `docs/demo/`.
5. UI exposes enough stable labels/selectors for Cypress and manual interview
   narration.
6. Queue/visibility/insights screens expose the main demo evidence points without
   requiring code inspection.
7. Automated checks pass or any unavailable browser/runtime dependency is
   recorded with a precise blocker.

## Verification Method

- `poetry run check-skeleton`
- `poetry run web-check`
- `npm run build` in `apps/web`
- `npm run cy:run` or the root wrapper when Cypress binary is available
- targeted Python unit/service tests for new demo script behavior

## Dependencies And Prerequisites

- Node/npm available.
- Cypress install may require network access if not already in `node_modules`.
- Docker/browser runtime may be unavailable in the sandbox; record blockers if
  the binary cannot run.

## Risks And Likely Failure Modes

- Cypress dependency download may fail or be slow in restricted network.
- E2E tests can become brittle if selectors use incidental text.
- Demo scripts can over-promise runtime OpenAI behavior; docs must be explicit.
- Full precommit may be slow because prior runs hung in this environment.

## Evidence Ledger

| Claim | Claim type | Source or artifact | Verification status |
|---|---|---|---|
| Existing UI has Overview, Config, Queue, Visibility, and Insights tabs. | repo_fact | `apps/web/src/**` | verified |
| Existing demo smoke script seeds config, processes fake worker output, and extracts deterministic insights. | repo_fact | `scripts/ai_visibility_tools/demo_e2e.py` | verified |
| Cypress is not yet configured in `apps/web/package.json`. | repo_fact | `apps/web/package.json` | verified |
| The interview demo needs a main flow doc and stronger visibility/insights narrative. | user_instruction | current user plan and demo note request | verified |

## Open Questions Or Assumptions

- Assumption: M12 should not block on real external OpenAI calls.
- Assumption: AI-assisted insights remain a clearly labeled future or optional
  path unless implemented with deterministic test doubles.

