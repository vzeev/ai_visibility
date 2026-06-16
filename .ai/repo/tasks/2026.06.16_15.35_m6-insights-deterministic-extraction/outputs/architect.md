# Architect Output

## Scope

M6 is a backend-only insights slice. It uses the existing foundation schema and
adds application behavior around deterministic extraction and query APIs.

## Premise Check

- user_premise_check: `accepted`
- basis: completed raw visibility milestones and existing `insights.*` tables.
- confidence: `high`
- challenge_required: `yes`; derived records must stay versioned and
  evidence-linked.

## Key Decisions

- Do not add a migration unless tests prove the existing schema is insufficient.
- Keep extractor deterministic and isolated from HTTP/DB concerns.
- Use read-only projections for `config.*` and `visibility.*` tables inside the
  insights service.
- Reuse completed extraction runs for idempotent same-version reruns.
- Build summaries from persisted extraction artifacts so the API can explain the
  aggregate with raw-response and extraction-run IDs.

## Verification Strategy

- Unit: extractor functions.
- Service: FastAPI routes with attached SQLite schemas.
- Integration: Alembic-managed Postgres schema.
- Aggregate: pre-commit and test-all.

## Risks

- Cross-schema foreign keys can be awkward in SQLite tests; ORM models should not
  rely on them where repository joins are explicit.
- Alias matching must be case-insensitive but should avoid substring matches
  inside larger words.

## Handoff

completed_work: M6 implementation contract created.
key_decisions: deterministic-only extraction, existing schema, idempotent reuse.
deviations_from_plan: none.
open_concerns: validation still pending.
important_findings: schema already contains M6 tables.
recommended_next_actions: run domain review, then implement repository/API/tests.
verification_status: architecture verified by repo inspection, code not yet verified.
