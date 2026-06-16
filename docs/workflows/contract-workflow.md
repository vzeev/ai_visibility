# Contract Workflow

## Rule

Implementation follows contracts. Contracts do not follow implementation.

Before adding or changing behavior that requires an endpoint, database object,
API field, enum, or generated model:

1. Update `contracts/openapi.yaml`, `contracts/database.sql`, or
   `contracts/enums.md`.
2. Update or add the active OpenSpec change under `openspec/changes/`.
3. Implement code from the contract.
4. Add verification for the contract boundary.

## Forbidden Shortcuts

- Do not invent DB fields in service code.
- Do not invent endpoints in service code.
- Do not store prompts as hard-coded source constants.
- Do not expose provider token values through read APIs.
- Do not let provider-specific SDK shapes leak into scheduling logic.
- Do not create raw response rows without deterministic idempotency keys.
