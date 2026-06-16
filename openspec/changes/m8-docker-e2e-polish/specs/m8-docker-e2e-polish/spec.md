# M8 Docker E2E Polish Spec

## ADDED Requirements

### Requirement: Docker-backed demo smoke workflow

The repository SHALL provide a local command that proves the complete deterministic demo workflow against Postgres.

#### Scenario: Run deterministic Brandlight smoke flow

- GIVEN a migrated Postgres database
- WHEN the operator runs the M8 demo smoke command
- THEN the command seeds or reuses Brandlight config data
- AND creates a visibility run
- AND processes queued prompts through the fake provider
- AND persists raw responses
- AND runs insights extraction
- AND reports non-empty raw response and extracted mention counts.

### Requirement: Idempotent demo config seed

The demo seed SHALL be safe to run repeatedly without duplicating durable config entities identified by stable names.

#### Scenario: Re-run seed

- GIVEN Brandlight demo config has already been seeded
- WHEN the seed or smoke command runs again
- THEN existing brand, competitor, product, provider, model, prompt set, prompt, credential, and rate-limit records are reused or updated instead of duplicated.

### Requirement: Local API browser access

Backend services SHALL allow local Vite browser origins to call API endpoints during development/demo runs.

#### Scenario: Browser calls backend from Vite origin

- GIVEN the UI is served from `http://localhost:5173` or `http://127.0.0.1:5173`
- WHEN the browser calls config, visibility, or insights APIs
- THEN CORS settings permit the request under local demo defaults.
