# Manager Output

## Scope

- M6 backend-only insights slice.
- No React UI changes.
- Preserve raw visibility immutability.
- All derived insight records must reference raw response ids.

## Decisions

- Selected flow: `openspec-feature-implementation`.
- Selected artifact profile: `audit_full`.
- Added `domain_steward` because M6 changes derived-truth handling and evidence lineage.
- Tracker lifecycle is `not_applicable`; no explicit external tracker is present.

## Active Risks

- Insights extraction must not silently invent durable truth beyond deterministic rules.
- Existing contracts already define `insights.*` tables; implementation must match them or deliberately reconcile drift.
- Reviewer, security, QA, and final reconciliation remain mandatory before closure.
