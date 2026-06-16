# M3 Visibility Queue And Raw Persistence

## Summary

Implement visibility-service queue behavior and raw response persistence after
M2 made configuration durable.

## Goals

- Create run batches from config snapshots.
- Expand runs into run items across active prompt versions and enabled models.
- Expose queue state for the UI.
- Support claiming, retry/fail recording, and raw completion.
- Persist raw responses idempotently.
- Search and paginate raw responses.

## Non-Goals

- No real provider network calls.
- No worker loop.
- No Redis/Celery.
- No insights extraction.
- No frontend wiring.

## Architecture References

- `docs/decisions/architecture.md`
- `contracts/database.sql`
- `contracts/openapi.yaml`
- `.ai/repo/tasks/2026.06.16_13.59_m3-visibility-queue-raw-persistence/artifacts/contracts/implementation_contract.v1.md`
