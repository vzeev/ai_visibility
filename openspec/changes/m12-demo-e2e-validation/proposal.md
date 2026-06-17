# M12 Demo E2E Validation Proposal

## Why

The application has the main demo capabilities, but the interview needs a
repeatable walkthrough and browser-level validation. M12 adds Cypress E2E tests,
demo scripts, and concise demo docs so the system can be shown confidently.

## What Changes

- Add Cypress to the web workspace.
- Add deterministic browser E2E coverage for Overview, Config, Queue,
  Visibility, and Insights.
- Add root scripts for Cypress and guided demo validation.
- Add `docs/demo/` walkthrough documentation.
- Improve UI observability for queue expansion, raw evidence, and insight
  evidence.

## Impact

- Gives the demo a repeatable validation path.
- Keeps E2E tests independent of real OpenAI calls.
- Makes the interview story easier to present without code browsing.

