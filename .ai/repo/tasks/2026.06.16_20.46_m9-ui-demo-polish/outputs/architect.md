# Architect Output - M9 UI Demo Polish

## Decision

Keep the existing tabbed operational dashboard and add a compact live overview instead of replacing the shell. This preserves the current architecture while making the demo story visible immediately.

## Implemented Design

- Dashboard overview aggregates config, queue/run, raw evidence, and insights state through existing service APIs.
- Insights UI reuses the existing batch extraction endpoint; no backend endpoint expansion was required.
- Raw evidence remains source-of-truth oriented by exposing response IDs, run item IDs, idempotency keys, request JSON, and response JSON.
- Styling stays within the existing restrained Brandlight-inspired UI language.

## Residual Risk

Browser viewport validation could not run due the local in-app browser runtime failure. Responsive behavior was handled in CSS and covered by static/build checks, but it still needs human/browser inspection.

