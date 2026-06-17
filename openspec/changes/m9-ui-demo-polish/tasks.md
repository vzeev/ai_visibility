# Tasks

## Contract

- [x] Confirm M9 proposal, design, tasks, and spec are in place.
- [x] Create M9 OpenSpec proposal, design, tasks, and spec delta.

## Frontend

- [x] Add live dashboard overview for demo readiness.
- [x] Improve Config panel demo scanability.
- [x] Improve Visibility raw evidence detail.
- [x] Add Insights action for latest completed run extraction.
- [x] Tune responsive styling and copy.

## Verification

- [x] Run web typecheck/build.
- [x] Run relevant Python checks.
- [x] Run local service/demo seed path as needed.
- [ ] Browser-validate desktop and mobile dashboard flows.

## Documentation

- [x] Update README/OpenSpec/skeleton checks if needed.
- [x] Update task audit artifacts and final reconciliation.

## Blocked Verification

- Browser validation is blocked by the in-app browser runtime failing before tab creation with: `failed to write kernel assets: The system cannot find the path specified. (os error 3)`.
- Substitute verification was completed with Vite build, precommit, service tests, Docker Compose health checks, HTTP endpoint smoke checks, and demo e2e seed.
