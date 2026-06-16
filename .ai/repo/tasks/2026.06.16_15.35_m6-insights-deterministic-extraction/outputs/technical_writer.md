# Technical Writer Output

## Scope Updated

- README M6 section.
- OpenAPI contract for M6 extraction endpoints and response schemas.
- OpenSpec M6 task checklist.
- Skeleton checker required paths and markers.

## Documentation Notes

- README explains synchronous API usage and explicitly states deterministic-only
  extraction, no scheduler, no React UI, and immutable raw inputs.
- OpenAPI now includes extraction trigger endpoints, extraction-run lookup,
  filterable summaries, and derived record schemas.

## Checks

- `poetry run precommit` passed after documentation and contract updates.
- `poetry run test-all` passed.

## Handoff

completed_work: M6 docs and contracts aligned with implementation.
key_decisions: keep README concise and API-focused.
deviations_from_plan: none.
open_concerns: none.
important_findings: contract now reflects M6 endpoints rather than placeholder
summaries only.
recommended_next_actions: manager closure sync.
verification_status: completed.
