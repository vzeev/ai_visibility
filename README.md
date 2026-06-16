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

## M2 Config Service

Config-service now persists its core configuration APIs through SQLAlchemy
sessions backed by the `config.*` tables:

- brands, competitors, and products
- prompt sets, prompts, and prompt versions
- providers and write-only provider credential metadata
- provider/model rate-limit policies
- model registry entries and `enabled_for_visibility`

Provider token values are accepted only as write-only request fields. Responses
return redacted fingerprints and metadata, not saved token values.

Postgres integration verification is opt-in:

```bash
docker compose -f docker-compose.test.yml up -d postgres-test
$env:AI_VISIBILITY_TEST_DATABASE_URL="postgresql+psycopg://ai_visibility:ai_visibility_local@localhost:55432/ai_visibility_test"
poetry run test-integration
docker compose -f docker-compose.test.yml down
```

## M3 Visibility Queue And Raw Persistence

Visibility-service now owns the first real queue and raw-evidence path:

- `POST /api/v1/runs` creates a run batch from a config snapshot.
- Run creation expands active prompt versions across enabled visibility models
  and requested sample count.
- `GET /api/v1/queue` returns pending, running, succeeded, failed, and
  throttled counts.
- `POST /api/v1/queue/claim` claims the next pending/throttled item and sets a
  lease.
- `POST /api/v1/queue/items/{run_item_id}/complete` persists a raw response
  through the provider-neutral response DTO shape.
- `POST /api/v1/queue/items/{run_item_id}/fail` records model errors and applies
  retry/throttle/fail transitions.
- `GET /api/v1/raw-responses` supports text search plus limit/offset
  pagination.

Raw response completion is idempotent per run item: replaying the same
completion returns the existing raw evidence row instead of creating a duplicate.

## M4 Visibility Worker Fake Provider

The worker now executes the first bounded queue-processing path:

- `VisibilityRepository.build_ai_request` constructs provider-neutral requests
  from the run item's immutable config snapshot.
- `VisibilityWorker.process_one` claims one item, calls an `AIProviderAdapter`,
  and stores raw evidence through the existing M3 repository path.
- `VisibilityWorker.process_batch(max_items=...)` processes a bounded number of
  items and stops early when the queue is empty.
- The default execution path uses `FakeAIProviderAdapter`; real provider network
  calls remain out of scope for automated tests.
- Retryable adapter failures are recorded as model errors and reuse the M3 queue
  retry/failure state transitions.

Run the worker locally with:

```bash
poetry run python -m apps.worker.app.main
```

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
