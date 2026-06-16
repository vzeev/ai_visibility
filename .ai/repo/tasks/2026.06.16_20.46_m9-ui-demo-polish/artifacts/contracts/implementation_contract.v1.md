# Implementation Contract v1 - M9 UI Demo Polish

## Objective

Polish the existing React/Vite dashboard so a local Brandlight demo clearly shows pipeline readiness, raw evidence, and extracted insights, with a browser-validated click path.

## User Premise Check

- user_premise_check: accepted
- basis: user request, completed M8 Docker smoke path, current UI inspection
- confidence: high
- challenge_required: no

## In Scope

- Add a live demo overview to the dashboard shell showing config, queue, raw evidence, and insight readiness.
- Improve the tab panels so the Brandlight demo data is easier to scan without changing the backend architecture.
- Add a UI action to trigger deterministic insights extraction for the latest completed visibility run using existing backend endpoint.
- Improve raw-evidence detail presentation for idempotency/source-of-truth demo value.
- Add CSS polish and responsive checks while staying consistent with the current Brandlight-inspired visual style.
- Update OpenSpec, README/skeleton checks if needed, and task audit artifacts.

## Out of Scope

- Real provider calls from the UI.
- Authentication/RBAC.
- New backend endpoints unless an existing contract blocks the UI workflow.
- Replacing the current tabbed dashboard structure.
- Production deployment packaging.

## Acceptance Criteria

1. The dashboard first screen shows a live demo summary across config, queue/raw data, and insights.
2. Config tab makes the active Brandlight demo setup scannable.
3. Visibility tab surfaces raw-response idempotency/source evidence clearly.
4. Insights tab can run deterministic extraction for the latest succeeded run and refresh summaries.
5. UI remains responsive and avoids overlapping text at desktop and mobile widths.
6. `npm run test`, `npm run build`, `poetry run web-check`, and relevant Python checks pass.
7. Browser validation covers initial dashboard, tab switching, raw search/detail, insights action, and mobile layout, unless tool/runtime failure is recorded.

## Verification Method

- TypeScript/web checks.
- Python skeleton/precommit checks as applicable.
- Local services plus seeded demo data.
- Browser validation via in-app browser screenshots/DOM checks.

## Dependencies and Prerequisites

- M8 demo smoke path exists and can seed a local database.
- Backend services are reachable at Vite default local URLs.

## Risks and Likely Failure Modes

- UI action to extract latest run may fail when no succeeded run has raw responses.
- Browser validation may be blocked by the prior browser-plugin asset-write issue.
- Overloading the dashboard with explanation would make it feel less like a product; UI copy must stay data/status focused.

## Approval Status and Version History

- v1: approved for implementation by user message "ok. implement m9" on 2026-06-16.

