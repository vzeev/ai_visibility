# Brandlight Visibility Demo Architecture Proposal

status: `pending_user_approval`
scope: architecture only; no implementation authorized

## 1. Problem Summary

Build an interview-quality AI visibility demo that proves senior engineering judgment:

- configuration is the source of truth for brands, competitors, products, prompt sets, schedules, and enabled models
- visibility collection runs asynchronously across configured OpenAI models
- raw model responses are preserved as evidence
- insights are derived from raw data without pretending derived signals are the same as raw truth
- the UI exposes config, queue state, raw visibility data, and insight results

The demo should feel like a small data platform around unstable AI outputs, not a simple synchronous LLM wrapper.

## 2. Assumptions And Constraints

Facts from the user:

- Stack: Python, Poetry, React, Vite, Postgres, Alembic.
- Tests: unit, service, integration.
- Desired services: `config`, `visibility`, `insights`, and React/Vite UI.
- Reference repo: Finfrax.
- Implementation cannot start until architecture is approved.

Assumptions:

- Python backend services use FastAPI because the Finfrax reference uses Python FastAPI service packages.
- The first slice is local/demo oriented, not production multi-tenant SaaS.
- OpenAI is the only provider for the first slice, but model/provider boundaries should allow later provider expansion.
- "All available models" means discover all models available to the configured OpenAI API key and store them in a registry, then run only models explicitly enabled for the demo.

Constraints:

- Do not hard-code current model names as durable truth; model availability changes.
- Do not call external APIs in automated tests; use fake adapters.
- Do not put OpenAI API keys in source, Docker images, test fixtures, logs, or raw response records.
- Do not implement auth/RBAC in the first slice unless explicitly approved later.

## 3. Requirements

Functional requirements:

- Manage brands, aliases, competitors, products, prompt sets, prompts, model registry entries, and schedules.
- Manage provider API credentials through the UI as write-only/redacted secret configuration.
- Store prompts to ask in the database as versioned configuration, editable through the UI.
- Configure rate limits per provider/model, including concurrency, requests per minute, token budget, and retry policy.
- Sync OpenAI model availability into local configuration.
- Create visibility run batches from selected config snapshots.
- Queue prompt/model execution asynchronously.
- Persist raw request metadata, raw response JSON, extracted output text, status, usage, latency, and errors.
- Search and paginate raw visibility responses.
- Extract brand mentions, competitor mentions, citations/URLs, sentiment labels, and visibility summary signals.
- Show UI tabs: Config, Queue, Visibility, Insights.

Non-functional requirements:

- Evidence-first: every insight links back to raw response evidence.
- Reproducible: tests use deterministic fake OpenAI responses.
- Observable: queue states, errors, retries, latency, and usage are visible.
- Incremental: repo, contracts, migrations, Docker, services, and UI can be delivered in bounded slices.
- Simple enough for interview demo: avoid production-only infrastructure until needed.

Priority order:

1. Correct truth boundaries and raw-to-derived lineage.
2. Stable local developer/demo workflow.
3. Clear UI workflow and service observability.
4. Upgrade path for scale and providers.

## 4. Scale Estimates

MVP demo scale:

| Dimension | MVP assumption |
|---|---:|
| Brands | 1-5 |
| Competitors per brand | 3-10 |
| Prompt sets | 1-5 |
| Prompts | 20-200 |
| Enabled models per run | 2-10 |
| Raw responses | 100-5,000 |
| Queue concurrency | 1-5 workers |
| Retention | keep all raw data locally |

Scaling pressure points:

- Prompt x model x schedule multiplication can create cost and rate-limit pressure quickly.
- Raw response search will need indexes on brand, prompt, model, run status, created time, and text search.
- Derived insights should be recomputable from raw responses when extraction logic changes.

## 5. Proposed Repository Shape

Planned after approval:

```text
contracts/
  README.md
  openapi.yaml
  database.sql
  enums.md
openspec/
  README.md
  config.yaml
  changes/
    m1-ai-visibility-demo-foundation/
      proposal.md
      design.md
      tasks.md
      specs/
  specs/
docs/
  decisions/
    architecture.md
infra/
  docker/
    python-service.Dockerfile
alembic/
  alembic.ini
  env.py
  versions/
apps/
  config_service/
  visibility_service/
  insights_service/
  worker/
  shared/
  web/
tests/
  unit/
  services/
  integration/
scripts/
```

Python service package shape mirrors Finfrax:

```text
app/
  main.py
  api/
  clients/
  db/
  domain/
  schemas/
  services/
tests/
```

## 6. Service Boundaries

### Config Service

Owns durable configuration truth:

- brands and aliases
- competitors and competitor aliases
- products
- prompt sets and prompt versions
- model registry and enabled model selection
- provider registry and model/provider capability settings
- provider API credential metadata, with write-only secret update from the UI and redacted readback
- per-model rate-limit policy
- schedules and run templates

The visibility service must take a config snapshot when creating a run. Later config edits must not rewrite the meaning of historical runs.

Prompts are first-class configuration records, not code constants. The UI should support creating prompt sets, editing prompt text, activating a prompt version, and disabling prompts without deleting historical run context.

### Visibility Service

Owns collection state and raw evidence:

- run batches
- run items
- queue state
- model adapter request/response records
- raw OpenAI response payloads
- usage and latency data
- retry/error metadata
- raw-data idempotency records and deduplication keys

It should expose queue and raw-data APIs for the UI and downstream services.

### Insights Service

Owns derived outputs:

- extraction jobs
- extraction version metadata
- brand mentions
- competitor mentions
- citations/URLs/domains
- sentiment labels
- visibility summaries

It should never mutate raw visibility records. Derived records must reference raw response IDs.

### Worker

Use one Python worker package/process initially:

- `visibility-worker`: claims queued visibility run items and calls OpenAI adapters.
- `insights-worker`: can initially be a mode of the same worker image or a second Compose service using the same package.

This keeps runtime operations clear while avoiding a premature external scheduler.

### Web UI

React/Vite app under `apps/web`.

Tabs:

- Config: brands, competitors, products, prompts, models, schedules.
- Queue: run batches, item statuses, retry/error state, latency, usage.
- Visibility: raw responses with search, filters, pagination, and detail drawer.
- Insights: derived mentions, citations, sentiment, summary metrics, evidence drilldown.

## 7. OpenAI API Boundary

Official OpenAI API evidence used:

- `GET /v1/models` lists currently available models and basic information.
- `POST /v1/responses` creates model responses and returns response status, model, output, usage, and errors.
- Structured Outputs support JSON Schema-constrained outputs for extraction when supported; for deterministic metrics, still validate and version extracted data.

Provider/model boundary:

- All AI providers are hidden behind one internal adapter interface.
- Visibility calling logic depends only on the internal adapter contract, not on OpenAI-specific request/response code.
- OpenAI is the first provider implementation, using the Responses API for prompt execution.
- Future providers must map into the same request/result DTOs before they can be scheduled.
- Provider-specific raw payloads may be stored for debugging, but business logic consumes normalized response records.

Common adapter contract:

```text
AIProviderAdapter.run_prompt(
  provider_config,
  model_config,
  credential_ref,
  prompt_request
) -> AIProviderResult
```

Normalized request fields:

- provider id
- model id
- prompt text and prompt version id
- run item id and idempotency key
- timeout
- optional temperature/top-p/max-output settings when supported

Normalized result fields:

- provider response id when available
- normalized status
- output text
- raw response JSON
- usage metadata
- latency
- finish/error details

MVP OpenAI design:

- A `model_registry` table stores discovered OpenAI models.
- A model must be marked `enabled_for_visibility = true` before the worker calls it.
- Each enabled model has a `rate_limit_policy_id` or inline rate-limit config.
- Provider credentials are configured from the UI, but readback is redacted and runtime access uses a secret reference.
- Raw request and response JSON are persisted for evidence and debugging, excluding credentials.
- Tests use `FakeAIProviderAdapter` with deterministic responses.

API credential handling:

- UI can create, rotate, disable, and test provider credentials.
- UI never receives the stored token after save.
- Config service stores either encrypted secret material or a local secret reference, depending on the approved implementation slice.
- Credential records store metadata such as provider, label, status, created/updated timestamps, last tested timestamp, and redacted fingerprint.
- Runtime services request credentials through a config-service method that returns only what the worker needs at execution time.

Rate-limit handling:

- Rate limits are configuration, not hard-coded constants.
- Minimum model-level settings: `max_concurrent_requests`, `requests_per_minute`, `tokens_per_minute`, `min_delay_ms`, `max_retries`, `backoff_base_ms`, `backoff_max_ms`.
- Provider-level defaults apply when a model has no override.
- Workers must enforce rate limits before calling adapters and surface throttled state in the Queue tab.

Raw-data idempotency:

- A raw response is uniquely identified by a deterministic idempotency key derived from run batch, prompt version, provider, model, config snapshot, and scheduled attempt scope.
- Successful duplicate writes must be ignored or return the already stored raw response.
- Retries for the same run item must not create multiple successful raw responses unless the contract explicitly models repeated samples.
- If repeated sampling is later supported, sample index becomes part of the idempotency key.

Why not literally execute every listed model by default:

- Some listed models may not be suitable for text Responses API usage.
- Account availability, model capabilities, cost, and rate limits vary.
- Running all discovered models can make the demo slow, expensive, and flaky.

## 8. Queue Strategy

Recommended MVP: Postgres-backed queue.

Core behavior:

- `visibility.run_items` has statuses: `pending`, `leased`, `running`, `succeeded`, `failed`, `retrying`, `cancelled`.
- Workers claim jobs with a transaction and row locking.
- Each item has `attempt_count`, `max_attempts`, `lease_expires_at`, `next_attempt_at`, `idempotency_key`, and `last_error`.
- Stuck leased jobs become retryable after lease expiry.
- A run item is idempotent by `(run_batch_id, prompt_snapshot_id, model_id)`.

Alternatives:

| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| Postgres queue | no extra infra, auditable, easy demo, transactional | not ideal for high-throughput distributed jobs | use for MVP |
| Redis/Celery | familiar async stack, better worker ergonomics | extra infra and failure mode; more moving parts | phase 2 if needed |
| Temporal/Dagster/Airflow | strong workflow semantics | too heavy for interview demo | reject for MVP |

## 9. Data Model

Logical schemas:

```text
config.*
visibility.*
insights.*
```

Core config tables:

- `config.brands`
- `config.brand_aliases`
- `config.competitors`
- `config.products`
- `config.prompt_sets`
- `config.prompts`
- `config.prompt_versions`
- `config.model_registry`
- `config.schedules`

Core visibility tables:

- `visibility.run_batches`
- `visibility.run_items`
- `visibility.raw_responses`
- `visibility.model_errors`

Core insights tables:

- `insights.extraction_runs`
- `insights.extracted_mentions`
- `insights.extracted_citations`
- `insights.visibility_summaries`

Important invariants:

- Raw responses are immutable after capture except for metadata corrections explicitly tracked by migration or repair scripts.
- Derived insight rows include `extraction_version`.
- Run batches store a config snapshot reference or embedded snapshot JSON so historical results remain explainable.
- UI summaries never become the source of truth; they are read models over raw and derived records.

## 10. API Contracts

Minimal API surface:

```text
config-service
  GET    /healthz
  GET    /api/v1/brands
  POST   /api/v1/brands
  GET    /api/v1/prompts
  POST   /api/v1/prompts
  POST   /api/v1/models/sync
  GET    /api/v1/models
  PATCH  /api/v1/models/{model_id}
  GET    /api/v1/schedules
  POST   /api/v1/schedules

visibility-service
  GET    /healthz
  POST   /api/v1/runs
  GET    /api/v1/runs
  GET    /api/v1/runs/{run_batch_id}
  GET    /api/v1/queue
  GET    /api/v1/raw-responses
  GET    /api/v1/raw-responses/{raw_response_id}

insights-service
  GET    /healthz
  POST   /api/v1/extractions
  GET    /api/v1/extractions
  GET    /api/v1/mentions
  GET    /api/v1/citations
  GET    /api/v1/summaries
```

API responses should use concrete Pydantic DTOs. Open JSON is allowed only for explicitly raw external payload storage and should be isolated from known response DTOs.

## 11. Critical Flow Walkthrough

Primary flow:

1. User configures a brand, competitors, prompt set, and enabled models in the Config tab.
2. UI calls `config-service` to save configuration.
3. User starts a visibility run.
4. UI calls `visibility-service POST /api/v1/runs`.
5. Visibility service reads config via `config-service`, creates a run batch, snapshots relevant config, and inserts run items.
6. Visibility worker claims pending run items.
7. Worker calls OpenAI Responses API through an adapter.
8. Worker persists raw response JSON, output text, usage, status, latency, and errors.
9. Insights service or worker creates extraction jobs for new raw responses.
10. Insights extraction combines deterministic matching with optional structured LLM extraction, then writes derived records.
11. UI Queue tab shows progress; Visibility tab shows raw responses; Insights tab shows derived results and links back to raw evidence.

## 12. Bottlenecks And Failure Handling

OpenAI API failures:

- timeout: mark attempt failed, retry with exponential backoff
- rate limit: retry after delay and reduce concurrency
- invalid model: disable model or mark registry entry as unavailable after repeated failures
- API key missing: worker fails closed and surfaces configuration error

Queue failures:

- worker crash: lease expires and job becomes retryable
- duplicate worker claim: row locking and idempotency key prevent duplicate persisted success
- permanent failure: item moves to `failed` after max attempts

Data failures:

- extraction bug: create a new extraction version and reprocess from raw responses
- partial run: show partial results; do not hide failed items from Queue tab
- schema drift: contracts and Alembic migrations must be updated before code uses new fields

Consistency model:

- config writes are strongly consistent in Postgres
- visibility collection and insights are eventually consistent after run creation
- raw response persistence is append-only evidence
- insights are recomputable derived state

## 13. Tradeoffs And Alternatives

### Architecture Options

| Option | Description | Pros | Cons | Verdict |
|---|---|---|---|---|
| A | Single FastAPI modular monolith | fastest to build, simplest local runtime | does not show requested service boundaries or queue ownership clearly | reject |
| B | Three FastAPI services plus worker and Postgres queue | matches requested shape, credible boundaries, manageable ops | more boilerplate than monolith | recommend |
| C | Three services plus Redis/Celery and gateway | closer to larger production architecture | more moving parts and less time for core evidence flow | defer |

Recommendation: Option B.

### Cross-Service Data Access

Recommended:

- Services own schemas.
- Cross-service behavior goes through APIs.
- Derived records can keep logical references to raw response IDs, but insights service should not mutate visibility records.

Accepted simplification:

- All services may share one local Postgres database in MVP.
- Strict per-service DB roles can be a hardening slice after the demo foundation passes.

### Insights Extraction

Recommended pipeline:

1. deterministic alias/fuzzy matching for known brands and competitors
2. URL/domain parsing for citations
3. optional Structured Outputs extraction for classification and sentiment
4. validation against Pydantic DTOs
5. versioned persistence

Rejected shortcut:

- Pure LLM extraction as the only metric source. It is less stable and harder to explain.

## 14. Security And Observability

Security baseline:

- Store `OPENAI_API_KEY` only in environment variables or local `.env`, never in source.
- Add `.env` to `.gitignore` before implementation.
- Redact API keys and authorization headers from logs.
- Limit request body size for API endpoints.
- Validate all request DTOs with Pydantic.
- Do not expose Postgres outside local development unless explicitly needed.
- Treat raw model output as untrusted content in UI; render as text, not HTML.

Observability baseline:

- structured logs include `request_id`, `service`, `run_batch_id`, `run_item_id`, `model_id`, `status`, `duration_ms`
- queue metrics: pending/running/succeeded/failed/retrying counts
- worker metrics: attempts, retries, failures, latency, token usage
- API metrics: request count, latency, error count
- UI queue tab surfaces user-facing operational state

## 15. Delivery Plan

Phase 0: repo foundation after architecture approval

- create OpenSpec skeleton
- create contracts skeleton
- create root Poetry project
- create Docker Compose with Postgres and app service placeholders
- create Alembic skeleton and initial migration
- create app package skeletons
- create verification scripts

Phase 1: config service

- implement config schema, DTOs, API, migrations, tests
- implement model registry sync contract with fake OpenAI tests

Phase 2: visibility queue and raw collection

- implement run batches, run items, worker claim loop, fake adapter
- add OpenAI adapter behind environment-gated runtime path
- persist raw response evidence

Phase 3: insights service

- implement deterministic extraction
- add extraction versioning and evidence links
- optionally add structured-output extraction after deterministic baseline

Phase 4: React/Vite UI

- implement Config, Queue, Visibility, Insights tabs
- add search, filters, pagination, detail views, and error states

Phase 5: integration polish

- run Docker-backed integration test through config -> run -> fake collection -> extraction -> UI/API read path
- update docs and OpenSpec specs after acceptance

## 16. Validation Plan

Unit tests:

- prompt expansion and config validation
- model registry filtering and enabled model selection
- queue claim/idempotency logic
- deterministic mention/citation extraction
- DTO validation

Service tests:

- config API with test database
- visibility run creation and queue state transitions
- worker fake adapter success/failure/retry paths
- insights extraction over stored raw responses

Integration tests:

- Compose stack boots Postgres, migrations, services, worker
- fake OpenAI adapter end-to-end run creates raw responses and insights
- API-level test verifies UI-facing queries: queue, raw search/pagination, insight summaries
- frontend build and component tests for the four tabs
- later browser test once UI workflow exists

## 17. Risks And Open Questions

Risks:

- External API calls can make demos flaky; fake adapter and seeded demo data are mandatory.
- OpenAI model availability changes; model registry must be dynamic.
- Three services may be more than needed for the first code slice; keep boundaries thin.
- UI can become a debug console; product framing should keep evidence drilldown user-oriented.

Open questions for user approval:

1. Do you approve interpreting "all available models" as "discover all available models, but run only enabled compatible models"?
2. Do you approve using a Postgres-backed queue for MVP instead of Redis/Celery?
3. Do you approve postponing auth/RBAC and per-service DB roles until after the demo foundation works?
4. Do you want the first implementation slice to create repo/OpenSpec/Docker/Postgres/service skeleton only, or include the first working config API too?

## Source Links

- OpenAI Models endpoint: `https://api.openai.com/v1/models`
- OpenAI Responses endpoint: `https://api.openai.com/v1/responses`
- OpenAI Structured Outputs guide: `https://developers.openai.com/api/docs/guides/structured-outputs`
