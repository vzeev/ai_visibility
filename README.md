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
poetry run demo-e2e
poetry run web-check
docker compose config
cd apps/web
npm install
npm run build
npm run test
```

When project dependencies are not installed yet, the foundation helper tests can
also run with `python -m unittest discover tests`.

Local Python entry points load the repository root `.env` file automatically.
`.env.example` documents the supported keys and safe local defaults.

Create `.env` from `.env.example` before running local services or the Docker
worker. Keep provider tokens only in `.env`.

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

Set `AI_VISIBILITY_TEST_DATABASE_URL` and `AI_VISIBILITY_ALLOW_DB_RESET=true` in
`.env`, then run:

```bash
docker compose -f docker-compose.test.yml up -d postgres-test
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

## M5 OpenAI Runtime Readiness

Real OpenAI execution is now available behind the same provider-neutral adapter
interface used by the fake provider:

- `OpenAIResponsesAdapter` maps `AIRequest` to `POST /v1/responses` and
  normalizes response IDs, output text, usage, latency, and raw JSON into
  `AIResponse`.
- Runtime tokens are resolved through `EnvironmentCredentialResolver`; missing
  tokens fail closed as retryable provider errors.
- Raw request JSON never includes authorization headers or token values.
- Worker execution checks the configured provider/model rate-limit policy from
  the run snapshot before calling the adapter.
- Automated tests use fake credentials and stubbed HTTP transports only.

Real OpenAI execution is opt-in through `.env`:

```dotenv
ENABLE_OPENAI=true
OPENAI_API_KEY=...
```

Then run the worker:

```bash
poetry run python -m apps.worker.app.main
```

The Docker worker mounts `.env` read-only and reads the same runtime keys without
storing provider secrets in `docker-compose.yml`:

```bash
copy .env.example .env
docker compose up visibility-worker
```

## M6 Insights Deterministic Extraction

Insights-service now turns stored raw visibility responses into versioned,
evidence-linked derived records:

- `POST /api/v1/extractions/raw-responses/{raw_response_id}` creates or reuses
  a completed extraction run for one raw response.
- `POST /api/v1/extractions/run-batches/{run_batch_id}` extracts every raw
  response in a run batch and stores a versioned visibility summary.
- `GET /api/v1/extraction-runs/{extraction_run_id}` returns mentions and
  citations for one extraction run.
- `GET /api/v1/summaries` returns filterable visibility summaries.
- Mentions and citations include `raw_response_id`, source, offsets, and snippet
  evidence in `evidence_json`.
- Rerunning the same raw response and extraction version is idempotent.

M6 is deterministic only: no LLM extraction, no scheduler, and no React UI work.
Raw visibility rows remain immutable inputs.

## M7 UI API Dashboard

The React/Vite dashboard is now API-backed instead of static:

- Config tab reads brands, prompt sets, prompts, providers, credentials, rate
  limits, and models from config-service.
- Queue tab reads queue counts and run batches from visibility-service and can
  create a run from selected brand/prompt set.
- Visibility tab reads raw responses with search, pagination, and detail view.
- Insights tab reads summaries and extraction-run evidence from insights-service.
- Every tab includes loading, empty, error, and refresh states for local service
  development.

Web service URLs can be overridden with Vite variables:

```bash
VITE_CONFIG_SERVICE_URL=http://localhost:8001
VITE_VISIBILITY_SERVICE_URL=http://localhost:8002
VITE_INSIGHTS_SERVICE_URL=http://localhost:8003
```

Run the dashboard locally:

```bash
cd apps/web
npm run dev -- --host 127.0.0.1
```

## M8 Docker E2E Polish

The repo now has a deterministic end-to-end smoke path for the local demo:

- seeds or reuses Brandlight config, competitors, prompts, fake provider, model,
  credential metadata, and rate limits
- creates a visibility run from the active config snapshot
- processes the run through the fake provider worker
- persists raw visibility responses
- runs deterministic insights extraction and writes a summary
- prints the run IDs and evidence counts as JSON

Start the local stack:

```bash
docker compose up -d postgres config-service visibility-service insights-service web
```

Run the smoke command against the local Postgres database. It uses
`AI_VISIBILITY_DEMO_DATABASE_URL` from `.env` when present, otherwise it falls
back to `DATABASE_URL`.

```bash
poetry run demo-e2e
```

For an already migrated database, skip migrations:

```bash
poetry run demo-e2e --skip-migrations
```

The Vite UI can call local backend APIs through default local CORS origins:

```bash
AI_VISIBILITY_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

`AI_VISIBILITY_DEMO_FAKE_TOKEN` can be set when you want the demo credential
metadata to use a specific local fake token value; it is optional and not needed
for provider execution.

## M9 UI Demo Polish

The dashboard now opens with a live demo overview showing:

- active Brandlight setup
- latest run status
- stored raw evidence count
- extracted mention totals

The Insights tab can trigger deterministic extraction for the latest succeeded
visibility run with the existing insights-service API. The Visibility tab now
shows raw response IDs, run item IDs, idempotency keys, request JSON, and
response JSON for evidence review.

## M10 Config Authoring UI

The Config tab now supports demo-critical configuration writes through existing
config-service APIs:

- create provider credentials with write-only token input and redacted readback
- create prompts under existing prompt sets
- create new active prompt versions without deleting prompt history
- create provider-level or model-level rate-limit policies

After each successful write, the Config tab refreshes the live configuration
data. Token values are cleared after credential submission and are never shown in
the credential list.

## M11 OpenAI Model Sync

Config-service can now discover available OpenAI models and reconcile them into
the DB-backed model registry:

- `POST /api/v1/providers/{provider_id}/models/sync` calls OpenAI
  `GET /v1/models` through the shared discovery client.
- Existing model rows keep local `enabled_for_visibility` and rate-limit
  assignments.
- Newly discovered models are available but disabled for visibility until
  explicitly enabled.
- Previously known models missing from the provider response are marked
  unavailable instead of deleted.
- The Config tab exposes a `Sync OpenAI models` action in the Model limits
  panel and refreshes registry data after a successful sync.

Real model sync reads the same repository root `.env` key as runtime execution:

```dotenv
OPENAI_API_KEY=...
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
