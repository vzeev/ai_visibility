# M11 OpenAI Model Sync Design

## Runtime Flow

```text
Config tab
  -> POST /api/v1/providers/{provider_id}/models/sync
  -> config-service model sync route
  -> ModelDiscoveryClient
  -> OpenAI GET /v1/models
  -> ConfigRepository.sync_models(...)
  -> config.model_registry
```

## Decisions

- Use a provider-neutral discovery DTO/protocol so future providers can reuse the sync route shape.
- Keep OpenAI network code behind a small client that accepts an injectable `httpx.AsyncClient` for tests.
- Resolve runtime OpenAI credentials through the existing `EnvironmentCredentialResolver`.
- New models are available but disabled for visibility by default.
- Existing model enablement and rate-limit policy assignments are preserved on sync.
- Missing previously known models are marked unavailable instead of deleted.

## Verification

- OpenAI client tests use `httpx.MockTransport`.
- Config-service API tests use a fake discovery client.
- Frontend sync action is covered by typecheck/build.

