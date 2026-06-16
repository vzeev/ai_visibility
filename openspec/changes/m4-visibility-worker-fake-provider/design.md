# M4 Design

## Runtime Shape

```text
visibility-worker
  -> VisibilityRepository.claim_next_item
  -> VisibilityRepository.build_ai_request
  -> AIProviderAdapter.complete
  -> VisibilityRepository.record_raw_response / record_model_error
  -> Postgres
```

## Key Decisions

- The worker owns orchestration only. Queue state transitions and raw
  idempotency remain in `VisibilityRepository`.
- `AIRequest` construction is exposed as a repository method so worker code does
  not depend on private snapshot parsing internals.
- The fake adapter is the default provider execution path for M4.
- Configured provider/model identifiers are preserved in the request and raw
  evidence even when fake execution is used.
- Batch processing is explicitly bounded by `max_items`; M4 does not introduce
  a daemon loop.

## Verification

- Service tests use SQLite with attached schemas.
- Integration tests run against Alembic-backed Postgres when
  `AI_VISIBILITY_TEST_DATABASE_URL` is set.
- Pre-commit validates formatting, static checks, skeleton coverage, and test
  commands.
