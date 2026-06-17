# Technical Implementation Demo

This document is the implementation-process companion to the architecture demo.

## Contract-First Layers

- `contracts/openapi.yaml` describes service API shape.
- `contracts/database.sql` describes database schema intent.
- `contracts/enums.md` records shared status values.
- `openspec/changes/**` records behavior changes before implementation.
- Alembic owns executable schema migrations.

## OpenSpec Usage

OpenSpec is used as durable feature truth. Each milestone has a change package
with proposal, design, tasks, and spec delta.

Good examples to show:

- `openspec/changes/m5-openai-runtime-readiness`
- `openspec/changes/m6-insights-deterministic-extraction`
- `openspec/changes/m10-config-authoring-ui`
- `openspec/changes/m11-openai-model-sync`
- `openspec/changes/m12-demo-e2e-validation`

Talking point:

> OpenSpec keeps intended behavior explicit before implementation and gives
> review, QA, docs, and code the same source of truth.

## Local Runtime

- Poetry manages Python dependencies and command wrappers.
- Docker Compose runs Postgres, services, worker, and web.
- `.env` is the local runtime configuration source.
- Provider secrets stay out of Compose source and are not printed by demo
  scripts.

## Testing Layers

- Unit tests cover pure domain and adapter logic.
- Service tests cover FastAPI/repository behavior with deterministic fakes.
- Integration tests cover Postgres-backed behavior when explicitly enabled.
- Cypress E2E validates the browser demo journey with deterministic API
  intercepts.

## Main Commands

```bash
poetry run dev
poetry run demo-e2e --skip-migrations
poetry run demo-check
poetry run web-check
poetry run web-e2e
```

For direct web commands:

```bash
cd apps/web
npm run build
npm run cy:run
```
