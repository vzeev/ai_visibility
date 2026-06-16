# Domain Steward Output

domain_verdict: `PASS_WITH_CONDITIONS`

## Scope Reviewed

Reviewed `artifacts/spec/architecture_proposal.md` and `artifacts/contracts/implementation_contract.v1.md` for truth-boundary safety around configuration, raw AI visibility evidence, and derived insights.

## Premise Check

- user_premise_check: `partially_supported`
- basis: architecture artifacts and source summary
- confidence: `medium`
- challenge_required: `yes`

The system may measure and summarize AI visibility, but should not present a single AI answer or unvalidated extraction as business truth.

## Invariant Summary

- Config state defines planned runs.
- A visibility run uses a config snapshot so historical runs remain explainable.
- Raw model responses are immutable evidence.
- Insights are derived, versioned, and recomputable.
- UI summaries must link back to raw evidence and extraction version.
- Raw AI output is untrusted input, not authoritative product truth.

## Boundary Map Review

- `config-service`: source of truth for brands, competitors, products, prompt definitions, model registry, and schedules.
- `visibility-service`: source of truth for collection jobs, statuses, raw request/response payloads, and model usage evidence.
- `insights-service`: source of truth for derived extraction and summary outputs.
- `worker`: execution mechanism only; it should not own domain semantics.
- `web`: presentation only; it should not create hidden truth transitions.

## Truth-Boundary Risks

- If config edits overwrite historical run context, old results become misleading.
- If insights overwrite raw data, reprocessing and auditability are lost.
- If the UI presents visibility summaries without raw drilldown, trust is weakened.
- If extraction logic changes without versioning, trend changes become ambiguous.

## Conditions For Implementation

- Persist config snapshot references or snapshot payloads with every run batch.
- Make raw response records append-only after capture.
- Include `extraction_version` on derived insight records.
- Keep source links from summaries back to raw response IDs.
- Label derived metrics as computed signals, not verified facts.

## Checks Run

- Document review only; no runtime checks.

## Rich Handoff

completed_work: Reviewed truth boundaries and domain invariants.
key_decisions: Architecture is acceptable if config/raw/derived layers stay separate.
deviations_from_plan: None.
open_concerns: Need implementation to preserve snapshot and extraction-version fields.
important_findings: Raw-to-derived lineage is the critical domain invariant.
recommended_next_actions: Carry invariants into contracts and migration design before coding.
verification_status: Design-level pass; implementation not verified.
