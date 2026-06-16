# M7 Implementation Contract V1

## Objective

Replace the static React/Vite dashboard with an API-backed local dashboard for
Config, Queue, Visibility, and Insights.

## User Premise Check

- user_premise_check: `accepted`
- basis: completed backend milestones and architecture roadmap Phase 4.
- confidence: `high`
- challenge_required: `yes`; the UI must be genuinely useful and Brandlight-like
  without copying proprietary assets or pretending unavailable APIs succeeded.

## In Scope

- Add a typed `fetch` API client with Vite-configurable service base URLs.
- Implement API-backed Config, Queue, Visibility, and Insights tabs.
- Add loading, empty, error, refresh, search, pagination, and detail states.
- Add a small run-creation flow from selected brand/prompt set in Queue.
- Preserve responsive enterprise-dashboard styling aligned with Brandlight's
  public site direction.
- Update README, OpenSpec, and skeleton checks.

## Out Of Scope

- Authentication, authorization, and production deployment hardening.
- New backend worker or extraction behavior.
- Proprietary Brandlight images/assets.
- Large new frontend dependency or state-management library.

## Acceptance Criteria

1. The UI compiles and builds with TypeScript.
2. All four tabs fetch real local service APIs and render returned data.
3. Each tab has clear loading, empty, error, and refresh states.
4. Visibility tab supports query search, pagination, and raw response detail.
5. Insights tab shows summary counts, entity/domain breakdowns, and extraction
   run detail when available.
6. Queue tab shows queue counts and can submit `POST /api/v1/runs`.
7. The UI remains usable when backend APIs are unavailable.
8. Browser validation shows a nonblank, responsive, non-overlapping dashboard.

## Verification Method

- `npm run test` in `apps/web`
- `npm run build` in `apps/web`
- `poetry run precommit`
- `poetry run test-all`
- local dev server plus browser screenshot checks at desktop and mobile widths

## Dependencies And Prerequisites

- Config-service M2 APIs.
- Visibility-service M3 APIs.
- Insights-service M6 APIs.
- Vite React app from M1.

## Risks And Likely Failure Modes

- Services may not be running during UI use; error states must be first-class.
- Current APIs are read-heavy and local-only; UI forms should avoid implying
  full production editing support.
- TypeScript DTO drift can break frontend if backend schemas change.
- Browser validation can generate `tsconfig.tsbuildinfo`; cleanup is required.

## Evidence Ledger

- claim: frontend currently uses static mock data.
  claim_type: `repo_fact`
  source_or_artifact: `apps/web/src/features/*`
  verification_status: `verified`
- claim: backend services expose required API endpoints.
  claim_type: `repo_fact`
  source_or_artifact: `apps/*_service/app/api/routes.py`
  verification_status: `verified`
- claim: UI should mimic public Brandlight direction without copied assets.
  claim_type: `user_instruction`
  source_or_artifact: user request and `https://www.brandlight.ai/`
  verification_status: `verified`

## Approval Status

- human_approval_to_implement: `approved`
- approval_source: user said `ok, implement m7`.

## Version History

- `v1`: initial M7 UI API dashboard contract.
