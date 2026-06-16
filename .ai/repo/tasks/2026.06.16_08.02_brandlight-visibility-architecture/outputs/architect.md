# Architect Output

verdict: `APPROVAL_READY_WITH_OPEN_QUESTIONS`

## Scope Reviewed

Reviewed the user request, product framing, Brandlight source summary, Finfrax reference patterns, OpenAI model/Responses/Structured Outputs docs, and the `system_design` flow requirements.

## Key Architecture Decision

Recommend a three-service FastAPI architecture plus a worker and Postgres-backed queue for the first implementation:

```text
React/Vite UI
  -> config-service       -> config schema
  -> visibility-service   -> visibility schema + queue state + raw evidence
  -> insights-service     -> insights schema + derived extraction outputs

visibility-worker
  -> OpenAI Responses API adapter
  -> visibility raw response storage

insights-worker
  -> deterministic extraction + optional structured-output extraction
  -> insights derived records
```

This matches the requested shape while staying simpler than a production microservice platform.

## Architecture Artifacts

- Full proposal: `artifacts/spec/architecture_proposal.md`
- Implementation contract draft: `artifacts/contracts/implementation_contract.v1.md`

## Important Decisions

- Use OpenSpec and contracts before implementation, mirroring Finfrax's contract-first discipline.
- Use dynamic OpenAI model registry from `/v1/models`; do not hard-code "all models".
- Use Responses API for visibility collection.
- Use Structured Outputs only as an optional extraction helper, not the sole source of metrics.
- Use Postgres queue first; defer Redis/Celery until queue pressure or worker ergonomics justify it.
- Keep raw responses immutable and insights versioned/recomputable.
- Skip production auth/RBAC in MVP unless the user explicitly approves adding it.

## Alternatives Compared

| Option | Result |
|---|---|
| Single FastAPI monolith | too small to show requested boundaries |
| Three FastAPI services + worker + Postgres queue | recommended MVP |
| Three services + Redis/Celery + gateway | credible later, too much for first demo slice |

## Risks

- External API calls are flaky/costly; fake adapter is mandatory for tests and demos.
- Three service boundaries add boilerplate; keep APIs thin and contracts explicit.
- UI can become an internal debug console; evidence drilldown must stay user-oriented.
- If "all models" is literal runtime behavior, it can break stability; model registry enablement is the safer interpretation.

## Checks Run

- Source review of Brandlight notes and Finfrax reference files.
- Official OpenAI docs/spec checks:
  - OpenAI `/v1/models`
  - OpenAI `/v1/responses`
  - Structured Outputs guide
- No runtime tests; no implementation exists yet.

## Handoff Notes

Block implementation until the user approves:

1. The recommended architecture.
2. Dynamic model registry interpretation of "all available models".
3. Postgres-backed queue for MVP.
4. First implementation slice scope.

## Rich Handoff

completed_work: Architecture proposal and implementation contract v1 drafted.
key_decisions: Three FastAPI services plus worker; Postgres queue; raw evidence boundary; dynamic model registry.
deviations_from_plan: None.
open_concerns: User must approve architecture before implementation; first slice scope needs confirmation.
important_findings: The strongest interview signal is raw-to-insight lineage plus operationally visible queue state.
recommended_next_actions: Run design reviews, then ask user for architecture approval and first-slice decision.
verification_status: Architecture evidence is source-backed; implementation verification is not applicable yet.
