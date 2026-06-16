# Technical Writer Output

docs_summary: `approval-ready architecture handoff`

## What Was Produced

The architecture package is ready for user review:

- `artifacts/spec/source_summary.md`
- `artifacts/spec/architecture_proposal.md`
- `artifacts/contracts/implementation_contract.v1.md`
- `outputs/product_owner.md`
- `outputs/architect.md`
- `outputs/domain_steward.md`
- `outputs/reviewer.md`
- `outputs/security.md`
- `outputs/qa.md`

## Recommended Architecture In One Page

Use a Python/FastAPI monorepo with root Poetry tooling, Postgres, Alembic, Docker Compose, and React/Vite UI.

Runtime shape:

```text
React/Vite UI
  -> config-service
  -> visibility-service
  -> insights-service

visibility-worker
  -> OpenAI Responses API
  -> raw response storage

insights-worker
  -> deterministic extraction
  -> optional OpenAI Structured Outputs extraction
  -> versioned insights
```

Core design decisions:

- `config-service` owns brands, competitors, products, prompts, model registry, and schedules.
- `visibility-service` owns run batches, queue state, raw model responses, errors, latency, and usage.
- `insights-service` owns derived mentions, citations, sentiment, and summaries.
- Raw responses are immutable evidence.
- Insights are versioned and recomputable.
- The UI must drill down from insights to raw responses.
- OpenAI models are discovered dynamically through the models endpoint and explicitly enabled before execution.
- Postgres queue is the MVP default; Redis/Celery is deferred.
- Auth/RBAC is deferred unless the user explicitly approves adding it.

## Approval Question

Do you approve this architecture, with these default decisions?

1. Interpret "all available models" as dynamic discovery plus explicit enablement.
2. Use a Postgres-backed queue for MVP.
3. Defer auth/RBAC and per-service DB roles until after the demo foundation works.
4. Start implementation with foundation-first slice: OpenSpec, contracts, Poetry, Docker/Postgres, Alembic, service skeletons, Vite skeleton, and verification scaffolding.

## Implementation Handoff

If approved, the developer should start from:

- `artifacts/contracts/implementation_contract.v1.md`
- `artifacts/spec/architecture_proposal.md`

The first implementation pass must not call OpenAI. It should create the repo foundation and deterministic verification path first.

## Checks Run

- Documentation packaging only; no runtime checks.

## Follow-Up: Architecture Decision Register

After user request, created `docs/decisions/architecture.md` as the durable
repo architecture decision register.

The file adapts the initial Finfrax architecture decisions to this AI visibility
repo and adds `ADR-007: Brandlight Website-Aligned UI`, recording the user
decision that the demo UI should visually align with the official Brandlight
website.

## Rich Handoff

completed_work: Packaged architecture into approval-ready summary.
key_decisions: Foundation-first implementation after approval; no OpenAI runtime calls in first slice; durable architecture decisions now live in `docs/decisions/architecture.md`.
deviations_from_plan: None.
open_concerns: Await user architecture approval and first-slice decision.
important_findings: The demo should prove raw-to-derived lineage and queue observability.
recommended_next_actions: Ask user for approval before any implementation.
verification_status: Documentation ready; implementation not started.
