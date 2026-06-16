# Product Owner Output

mode_used: `pre_architecture_product_framing`
verdict: `PASS_WITH_BOUNDED_SCOPE`

## Scope Reviewed

Reviewed the user's requested demo shape, the two Brandlight preparation notes, and the Finfrax reference conventions. This pass frames what the demo should prove before architecture locks implementation details.

## Premise Check

- user_premise_check: `partially_supported`
- basis: user instruction plus Brandlight notes and Finfrax repo evidence
- confidence: `medium`
- challenge_required: `yes`

The requested direction is product-fit coherent: an AI visibility demo can credibly show data-heavy SaaS judgment, async collection, raw evidence preservation, extraction, and dashboard thinking. The premise that the service should query "all available models" needs narrowing for MVP stability, cost, rate limits, and reproducibility.

## Product Framing

Target user for the demo:

- Interviewer evaluating senior/full-stack/technical-lead capability.
- Secondary imagined product user: marketing or brand operator who needs explainable AI visibility evidence.

User problem:

- AI answers are unstable, opaque, and distributed across models. A brand team needs repeatable measurement, raw evidence, extraction lineage, and a dashboard that explains why a visibility signal exists.

Desired outcome:

- In a short demo, the system should prove that raw AI responses are preserved, processing is observable, extracted insights are versioned enough to trust, and UI drilldowns connect high-level insights back to raw prompts and model runs.

Critical journey:

1. Configure brands, competitors, products, prompts, models, and schedule settings.
2. Enqueue visibility runs from that configuration.
3. Track queue/run status while workers collect model responses.
4. Inspect raw prompt/model outputs with search and pagination.
5. Run or view insights that extract brand mentions, competitors, citations, sentiment, and visibility summaries.

## Product Non-Goals

- Do not build a production Brandlight clone.
- Do not implement website crawling, server-log analysis, citation influence graph, or content optimization in the first slice.
- Do not add enterprise auth, billing, roles, or multi-customer hierarchy unless explicitly approved later.
- Do not claim model outputs are objective truth; expose them as measured evidence.
- Do not hide extraction assumptions behind a single opaque score.

## Workflow Traps

- Treating raw AI output and derived insights as the same truth layer.
- Calling external models synchronously from UI/API requests.
- Letting prompt quality drift without versioning or configuration history.
- Building dashboards that cannot drill down to prompt, model, raw answer, and extraction version.
- Overbuilding microservices or queue infrastructure before the demo proves the core loop.

## Smallest Meaningful Slice

The smallest useful approved implementation should be:

- one Compose-backed local stack
- one Postgres database
- three Python FastAPI service boundaries: `config-service`, `visibility-service`, `insights-service`
- one Python worker process for visibility collection and insight processing
- one React/Vite app with the four requested tabs
- contracts/OpenSpec/migrations before app behavior
- tests at unit, service, and integration levels

This is broad enough to demonstrate architecture and ownership, but narrow enough to finish as an interview-quality system.

## Product Risks

- Value risk: a dashboard without raw evidence drilldown looks generic.
- Usability risk: queue and visibility tabs can become internal-debug surfaces unless status, filters, and errors are clear.
- Feasibility risk: external model APIs introduce cost, rate limits, and flaky network dependencies; demo needs fake/stub adapters for tests.
- Business-viability risk: "all available models" can become expensive and unstable; MVP should support a model registry and enable selected models.

## Handoff Notes

- Architect should design explicit truth boundaries: config truth, raw visibility evidence, derived insight outputs.
- Architect should choose a queue approach that is simple now but has a credible upgrade path.
- Architect should include an evidence drilldown path in the API/data model, not only dashboard aggregates.

## Checks Run

- Read source notes and Finfrax reference files.
- No tests run; this is pre-implementation product framing.

## Rich Handoff

completed_work: Product framing for architecture.
key_decisions: Treat demo as AI visibility data platform; preserve raw evidence; keep first slice bounded.
deviations_from_plan: None.
open_concerns: Need user approval on MVP scope and "all models" interpretation.
important_findings: The strongest demo signal is explainable pipeline and raw-to-insight lineage.
recommended_next_actions: Architect should draft the architecture, contracts, data model, and approval-ready implementation slice.
verification_status: Partially verified by source review; runtime behavior not applicable yet.
