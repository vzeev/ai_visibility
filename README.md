# AI Visibility Demo

AI Visibility Demo is a local interview-ready product skeleton for exploring how
brands appear in AI-generated answers.

The project is intentionally contract-first:

- `docs/decisions/architecture.md` records accepted architecture decisions.
- `contracts/` records API, database, and enum contracts.
- `openspec/` records proposed and accepted behavior specs.
- `apps/` contains backend services, worker code, shared helpers, and the web UI.

## Target Local Shape

```text
React/Vite UI
  -> config-service
  -> visibility-service
  -> insights-service

visibility-worker / insights-worker
  -> provider-neutral AI adapter
  -> Postgres
```

## Commands

```bash
poetry install
pre-commit install
poetry run precommit
poetry run doctor
poetry run fix
poetry run test-all
poetry run test-unit
poetry run test-service
poetry run test-integration
poetry run check-skeleton
poetry run web-check
docker compose config
cd apps/web
npm install
npm run build
npm run test
```

When project dependencies are not installed yet, the foundation helper tests can
also run with `python -m unittest discover tests`.

`poetry run test-servcie` is available as a compatibility alias for
`poetry run test-service`.

The first foundation slice uses fake AI adapters for tests. Real provider calls
are added only behind the provider-neutral adapter boundary and must not be used
by automated tests.

## Pre-Commit

The hook setup mirrors the Finfrax baseline where it fits this repo:

- standard whitespace, merge-conflict, and large-file guards
- Ruff fix and format
- Bandit over `apps`, `scripts`, and `alembic`
- Pyright with the root `pyproject.toml`
- local skeleton, Python test, and web type-check hooks

## Design Decisions

Start with [docs/decisions/architecture.md](docs/decisions/architecture.md).

Current accepted highlights:

- Prompts are UI-configurable, versioned DB records.
- Provider API tokens are UI-configurable but write-only/redacted on read.
- Rate limits are configurable per provider/model.
- All AI APIs use the same internal adapter contract.
- Raw visibility data is idempotent and immutable evidence.
- The UI should visually align with the official Brandlight site
  (`https://www.brandlight.ai/`) without copying proprietary assets.
