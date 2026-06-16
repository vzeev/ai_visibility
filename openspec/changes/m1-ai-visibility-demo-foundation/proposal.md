# M1 AI Visibility Demo Foundation

## Summary

Create the contract-first local foundation for the AI Visibility Demo.

## Goals

- Initialize OpenSpec and contract mirrors.
- Initialize Python/FastAPI service skeletons and shared package boundaries.
- Initialize Postgres, Alembic, and Docker Compose baseline.
- Initialize React/Vite UI skeleton with Brandlight-aligned design tokens.
- Define provider-neutral AI adapter contracts.
- Define config-owned prompts, provider credentials, model registry, rate limits,
  run items, raw responses, and insights schemas.

## Non-Goals

- No real OpenAI calls in this foundation slice.
- No production auth/RBAC.
- No Redis/Celery until the Postgres queue baseline is proven insufficient.
- No full dashboard implementation beyond the first UI shell.

## Architecture References

- `docs/decisions/architecture.md`
- `contracts/openapi.yaml`
- `contracts/database.sql`
- `contracts/enums.md`
