# M1 Design

## Runtime Shape

```text
apps/web
  -> config-service
  -> visibility-service
  -> insights-service

worker
  -> provider-neutral AI adapter
  -> Postgres
```

## Key Decisions

- Prompts are config-owned, versioned DB records.
- Provider API credentials are configured from the UI but read back only as
  redacted metadata.
- Rate limits are config-owned per provider/model policy records.
- Provider calls go through `AIProviderAdapter`.
- Raw response writes are idempotent by deterministic keys.

## Verification

- Skeleton verification checks required files and contract markers.
- Unit tests cover shared adapter/idempotency/rate-limit helpers.
- Docker Compose config validates local infrastructure wiring.
