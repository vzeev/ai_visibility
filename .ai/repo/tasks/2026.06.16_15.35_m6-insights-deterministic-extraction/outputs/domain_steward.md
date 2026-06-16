# Domain Steward Output

## Domain Verdict

Approved for implementation with lineage constraints.

## Invariant Summary

- `visibility.raw_responses` is immutable evidence.
- `insights.*` records are derived state and must be versioned.
- Derived records must link to their source raw response through
  `extraction_runs.raw_response_id` and evidence JSON.
- Summaries must be recomputable from raw responses and extraction artifacts for
  a given extraction version.

## Boundary Map

- visibility service owns raw collection and raw response persistence.
- insights service reads visibility/config data and writes only insights data.
- UI/API clients may read derived summaries, but those summaries are not source
  of truth.

## Truth Boundary Risks

- Deterministic extraction is a heuristic, not semantic truth. Labels and counts
  must remain tied to `extraction_version`.
- Citation URLs extracted from model text are claims made by the model response,
  not verified external facts.
- Sentiment labels are basic deterministic classifications and should be treated
  as explainable signals, not ground truth.

## Required Guardrails

- Do not mutate raw response rows.
- Include raw response IDs in mention/citation evidence and summary payloads.
- Reuse same-version extraction runs or replace their derived rows without
  duplicate version rows.

## Handoff

completed_work: domain invariants and truth boundaries reviewed.
key_decisions: M6 can proceed if lineage/versioning guardrails are implemented.
deviations_from_plan: none.
open_concerns: none blocking.
important_findings: summaries must not hide raw evidence IDs.
recommended_next_actions: implement against contract and verify idempotency.
verification_status: approved before implementation.
