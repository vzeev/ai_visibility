# AI Visibility Architecture Decisions

This file is the canonical in-repo register for accepted architecture decisions.
Task artifacts under `.ai/repo/tasks/` remain audit history, not the primary
lookup place for current architecture.

Product and interview-preparation context currently lives outside the repository
in the Brandlight notes folder:

```text
C:\VladimirSoskin\Dropbox\Documents\личное\фин\obsidian\projects\!future\teamlead\brandlight
```

This repository records implementation-facing decisions needed to keep code,
contracts, tests, local infrastructure, and the demo UI coherent.

## ADR-001: Product Truth And Repo Mirrors

Status: accepted.

Product and interview context stays in the external Brandlight notes folder. The
repo keeps local mirrors and implementation artifacts under:

- `contracts/` for API, database, and enum interface contracts.
- `openspec/` for behavior changes and accepted behavior specs.
- `docs/` for human-facing architecture, workflows, decisions, and runbooks.
- `.ai/repo/tasks/` for agent audit history only.

Accepted implementation deltas that materially change the product story or demo
positioning should be reflected back into the owning Brandlight notes before the
demo is treated as complete.

Sources: adapted from Finfrax `ADR-001`; Brandlight architecture task artifacts.

## ADR-002: Contract-First Implementation

Status: accepted.

Implementation follows contracts. Contracts do not follow implementation.

Before code relies on a new endpoint, database object, API field, enum, or
generated model, update the relevant local contract file first:

- `contracts/openapi.yaml`
- `contracts/database.sql`
- `contracts/enums.md`

OpenSpec changes describe proposed behavior before it is implemented. Accepted
behavior is promoted into `openspec/specs/` only after implementation and
verification are complete.

Sources: adapted from Finfrax `ADR-002`; `artifacts/contracts/implementation_contract.v1.md`.

## ADR-003: Source Naming Versus Service Identity

Status: accepted.

Source folders use import-safe names:

- `apps/config_service`
- `apps/visibility_service`
- `apps/insights_service`
- `apps/worker`
- `apps/shared`
- `apps/web`

External service identities remain hyphenated in Compose, OpenAPI, URLs, logs,
and product language:

- `config-service`
- `visibility-service`
- `insights-service`
- `worker`
- `web`

Current source directory responsibilities:

- `apps/config_service`: Python FastAPI config service. It owns brands,
  competitors, products, prompt sets, prompt versions, model registry entries,
  enabled model selections, and schedules.
- `apps/visibility_service`: Python FastAPI visibility service. It owns run
  batches, run items, queue state, raw model responses, model errors, usage,
  latency, retry state, and raw-data search/pagination APIs.
- `apps/insights_service`: Python FastAPI insights service. It owns extraction
  jobs, extraction versions, mentions, citations, sentiment, and visibility
  summaries derived from raw visibility evidence.
- `apps/worker`: Python worker entrypoint for background visibility collection
  and insight extraction. It executes work but does not own product truth.
- `apps/shared`: shared stateless DTOs, schemas, HTTP helpers, observability
  helpers, and infrastructure helpers safe for every service to import.
- `apps/web`: React/Vite frontend workspace. It owns browser UI code, frontend
  tests, visual styling, and the Config, Queue, Visibility, and Insights tabs.

Generated folders such as `__pycache__`, `dist`, `.pytest_cache`, and
`node_modules` are not architecture and must not be documented as application
boundaries.

Sources: adapted from Finfrax `ADR-003`; `artifacts/spec/architecture_proposal.md`.

## ADR-004: Python Service Layout

Status: accepted.

Python services use this package shape:

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

Responsibilities:

- `api/`: HTTP route handlers.
- `clients/`: outbound service or external-system clients, including OpenAI
  adapters where relevant.
- `db/`: service-owned persistence, ORM models, repositories, and DB facades.
- `domain/`: domain rules independent of HTTP and storage.
- `schemas/`: service-local request/response DTOs.
- `services/`: application orchestration.
- `main.py`: FastAPI app entrypoint.

Root-level `apps/*.py` business modules are not an approved implementation
location.

Sources: adapted from Finfrax `ADR-004`; `artifacts/spec/architecture_proposal.md`.

## ADR-005: Shared And Support Package Boundaries

Status: accepted.

`apps/shared` is for deployable, stateless shared Python code:

- shared DTO/schema packages
- stateless infrastructure helpers safe for every service to import
- shared HTTP, error, security, observability, and test-fixture helper types

Service business logic does not belong in `apps/shared`.

If a future `apps/support` package is added, it is non-deployable local/test
support only. It must not become the normal runtime path for accepted behavior.

Sources: adapted from Finfrax `ADR-005`; Brandlight architecture task artifacts.

## ADR-006: ORM And DTO Boundaries

Status: accepted.

Runtime services use SQLAlchemy ORM mapped models for declared tables and views.
Alembic remains the migration and DDL owner. ORM models mirror
`contracts/database.sql`; they do not define schema truth.

Known service request/response payloads use concrete Pydantic DTOs before JSON
serialization and after JSON parsing. Broad `dict[str, object]` containers are
not an approved shape for known domain payloads.

Open JSON is allowed only where the contract explicitly defines an open payload
object, such as raw external model request/response payloads, model error
metadata, or extraction debug metadata.

Shared contract-shaped DTOs live under `apps/shared/schemas`. Service-local
persistence entrypoints live under each service's `app/db` package.

Raw OpenAI output is untrusted external input. It may be stored as raw evidence,
but it must not silently become derived insight truth without validation,
extraction versioning, and a link back to the raw response.

Sources: adapted from Finfrax `ADR-006`; domain steward output for the
Brandlight architecture task.

## ADR-007: Config-Owned Prompts, Provider Credentials, And Rate Limits

Status: accepted.

Prompts to ask are configuration, not source-code constants. They are created,
edited, enabled, disabled, versioned, and selected from the UI, then persisted in
the config schema.

Provider credentials are also part of configuration, but the secret value is a
write-only secret. UI and API read operations may return credential metadata,
status, label, provider, redacted fingerprint, and last-test state, but must not
return the saved token value.

Rate limits are configurable per provider and model. Provider defaults apply
when a model has no override. The minimum rate-limit policy shape is:

- max concurrent requests
- requests per minute
- tokens per minute
- minimum delay between calls
- max retries
- backoff base and cap

Visibility workers must consult these config records before executing model
calls. Rate-limit behavior must be visible in queue state so throttled work is
explainable in the UI.

Sources: owner decision on 2026-06-16; architecture proposal follow-up.

## ADR-008: Provider-Neutral AI Adapter Boundary

Status: accepted.

Any AI API must be wrapped behind the same internal adapter contract. Scheduling,
queue, idempotency, raw persistence, and insight-triggering logic must not depend
on provider-specific SDKs, API URLs, response shapes, or model quirks.

Provider implementations map their native API into normalized internal request
and result DTOs. OpenAI is the first provider, but it is not allowed to leak
OpenAI-specific assumptions into the common visibility execution path.

The common adapter result must include normalized status, output text, raw
response payload, usage metadata, latency, provider response id when available,
and normalized error details.

Sources: owner decision on 2026-06-16; architecture proposal follow-up.

## ADR-009: Raw Visibility Data Idempotency

Status: accepted.

Raw visibility data must be idempotent. A retry, worker restart, duplicate queue
claim, or repeated API response write must not create conflicting successful raw
records for the same intended measurement.

The raw-response idempotency key is derived from:

- run batch
- prompt version
- provider
- model
- config snapshot
- sample index when repeated sampling is explicitly supported

The database contract must enforce uniqueness for this key. Duplicate successful
writes should return the existing raw response or fail cleanly without corrupting
run state.

Sources: owner decision on 2026-06-16; architecture proposal follow-up.

## ADR-010: Brandlight Website-Aligned UI

Status: accepted.

The demo UI should visually align with the official public Brandlight website,
`https://www.brandlight.ai/`, so the interview audience immediately recognizes
the product context.

The UI should mimic the public site's enterprise AI-visibility product language:

- light, polished enterprise dashboard feel
- strong blue/cyan accent system
- dashboard-first composition with visible scores, trend charts, filters, and
  evidence tables
- language around AI visibility, engines, citations, intent, competitors,
  technical health, and enterprise command-center workflows
- visible product-module language aligned to the official site, including
  Visibility & Insights, Technical Health, Content, Partnerships, Agentic
  Commerce, and Ads
- clear drilldown from high-level scores to raw prompts, model answers,
  citations, and extracted evidence

The UI should not blindly copy proprietary assets, logos, customer logos,
testimonials, or exact screenshots from the public site unless those assets are
explicitly supplied and approved for use. The goal is credible visual alignment,
not asset cloning.

Implementation implications:

- `apps/web` should define design tokens before building feature screens.
- The first visible UI should be the usable dashboard/application shell, not a
  marketing landing page.
- Dashboard cards and tables should be compact, restrained, and built for
  repeated operational use.
- Product screenshots and demo seed data should use the AI visibility domain:
  ChatGPT/Gemini/Perplexity-style engine filters, visibility scores, sentiment,
  competitor comparison, prompt intent, citation sources, queue status, and raw
  evidence.

Sources: owner decision on 2026-06-16; official Brandlight homepage
`https://www.brandlight.ai/` reviewed on 2026-06-16; Brandlight architecture
task artifacts.

## Deferred Decisions

These are intentionally not finalized yet:

- Whether the MVP uses a Postgres-backed queue only, or starts with Redis/Celery.
- Whether auth/RBAC is included before or after the interview demo foundation.
- Whether per-service PostgreSQL login roles are implemented in the first slice
  or deferred to hardening.
- The exact OpenAI model capability-filtering rules for enabled visibility
  models.
- Whether UI-managed token secret material is encrypted in Postgres for the
  local demo or stored outside the DB behind a secret-reference abstraction.
- The production deployment target and CI provider.
