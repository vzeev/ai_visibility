# M8 Design

## Runtime Shape

The M8 smoke path should run as a local operator command against a configured Postgres database. It should reuse the same repositories and services used by the API/worker layers instead of creating separate fixture-only paths.

## Demo Data

Seed data should be deterministic and Brandlight-specific:

- Brandlight as the primary brand.
- A small competitor set.
- One or more products/use cases suitable for AI visibility prompts.
- A prompt set and prompts that produce predictable fake-provider responses.
- Fake provider/model configuration with local rate-limit settings.

Repeated runs should reuse existing config records by stable names and create fresh visibility runs only where runtime state is intentionally new.

## Smoke Flow

1. Ensure the target database is migrated.
2. Seed or reuse demo config data.
3. Create a visibility run from active config.
4. Run the fake-provider worker until the run has no queued items.
5. Run insights extraction for the persisted raw responses.
6. Verify counts for config records, queue items, raw responses, extraction runs, and extracted mentions.
7. Print a concise JSON or text summary for operator confidence.

## CORS and Service URLs

Backend services should default to local Vite origins:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

The defaults should be configurable through environment variables and kept suitable for a local demo rather than production.

## Verification

The smoke flow should be covered by automated tests at the orchestration/helper layer, plus Docker-backed integration execution when Docker is available.
