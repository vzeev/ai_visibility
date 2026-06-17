# M12 Demo E2E Validation Design

## Design Goals

- Validate the critical browser journey with deterministic API intercepts.
- Preserve real backend `demo-e2e` smoke tests for database/worker/integration
  confidence.
- Keep interview docs short enough to use live.
- Avoid implying production hardening that has not been implemented.

## Cypress Strategy

Cypress tests run against the Vite app and intercept backend API calls. This
proves the UI workflow, state rendering, selectors, and operator narrative
without requiring Docker, Postgres, or real OpenAI during browser tests.

The existing `poetry run demo-e2e` remains the backend integration smoke path.

## Demo Script Strategy

The root demo validation command should:

- point to the correct docs
- check that required files and scripts exist
- run existing deterministic smoke checks when explicitly requested
- keep real provider tokens out of output

## UI Polish Strategy

Only add polish that improves demo evidence:

- stable `data-cy` selectors
- compact run expansion/execution summary
- clear deterministic extraction labels
- raw response evidence remains central

