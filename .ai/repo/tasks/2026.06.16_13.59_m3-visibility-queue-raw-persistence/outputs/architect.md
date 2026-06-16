# Architect Output

stage: `architect`
status: `completed`

## Scope

M3 implements visibility-service queue and raw persistence behavior after M2
made configuration durable.

## Contract

- Implementation contract:
  `.ai/repo/tasks/2026.06.16_13.59_m3-visibility-queue-raw-persistence/artifacts/contracts/implementation_contract.v1.md`
- Active OpenSpec change:
  `openspec/changes/m3-visibility-queue-raw-persistence/`

## Key Decisions

- Visibility-service uses read-only config projection models for snapshots.
- Run creation captures immutable config snapshot JSON on the batch.
- Queue items are expanded from prompt versions, enabled models, and sample
  index.
- Raw completion consumes the provider-neutral `AIResponse` DTO shape.
- Duplicate raw completion returns the existing raw response for the run item.

## Verification Plan

- Service tests for run creation, queue claim, completion/idempotency, failure
  transitions, and raw search.
- Opt-in Postgres/Alembic integration test.
- Pre-commit and aggregate test commands.
