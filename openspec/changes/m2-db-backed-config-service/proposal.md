# M2 DB-Backed Config Service

## Summary

Implement config-service as the durable source of truth for brands, products,
competitors, prompt configuration, providers, provider credentials, model
registry entries, and rate-limit policies.

## Goals

- Persist config-service API writes in Postgres-backed tables.
- Return config-service API reads from database state.
- Keep provider token values write-only and return only redacted credential
  metadata.
- Version prompts so updates create auditable prompt versions.
- Provide rate-limit and model-registry APIs needed by the visibility queue in a
  later slice.
- Add service and integration verification paths.

## Non-Goals

- No real OpenAI or provider API calls.
- No visibility queue execution.
- No React config CRUD implementation.
- No production external secret vault.
- No auth/RBAC.

## Architecture References

- `docs/decisions/architecture.md`
- `contracts/database.sql`
- `contracts/openapi.yaml`
- `.ai/repo/tasks/2026.06.16_13.28_m2-db-backed-config-service/artifacts/contracts/implementation_contract.v1.md`
