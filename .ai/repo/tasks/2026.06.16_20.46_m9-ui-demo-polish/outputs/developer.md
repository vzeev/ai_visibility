# Developer Output - M9 UI Demo Polish

## Changed App Files

- `apps/web/src/features/overview/DemoOverview.tsx`
- `apps/web/src/app/App.tsx`
- `apps/web/src/features/config/ConfigPanel.tsx`
- `apps/web/src/features/visibility/VisibilityPanel.tsx`
- `apps/web/src/features/insights/InsightsPanel.tsx`
- `apps/web/src/lib/api.ts`
- `apps/web/src/styles/global.css`

## Implementation Notes

- Added a live overview band above the tabs.
- Added Config readiness strip and active setup emphasis.
- Added raw response drilldown fields for idempotency/source evidence.
- Added Insights "Analyze latest run" action with inline success/error state.
- Added API client support for `POST /api/v1/extractions/run-batches/{id}`.
- Added responsive CSS for the overview and analysis panels.

## Verification

All non-browser gates passed. The in-app browser could not start due the environment-side asset-write failure.

