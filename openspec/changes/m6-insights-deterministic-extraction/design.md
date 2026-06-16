# M6 Design

## Runtime Shape

```text
insights-service
  -> deterministic extraction engine
  -> insights repository
  -> visibility/config read models
  -> insights.* tables
```

## Key Decisions

- M6 uses deterministic extraction only: alias/string matching, citation URL
  parsing, and summary aggregation over persisted raw responses.
- Extraction is versioned at write time through `extraction_version`; reruns for
  the same raw response and version are idempotent.
- Evidence links are explicit, not implied. Mention, citation, and summary
  payloads store raw-response references and evidence snippets/offset metadata.
- Raw responses stay immutable. M6 only reads `visibility.*` and writes
  `insights.*`.
- The first execution path can be synchronous through the insights-service API;
  worker orchestration can be added later without changing the persisted model.

## Verification

- Unit tests validate deterministic mention, citation, and summary extraction.
- Service tests validate extraction APIs, idempotent reruns, and evidence-link
  persistence against an isolated test database.
- Integration tests validate the insights flow against the Alembic-managed
  Postgres schema.
