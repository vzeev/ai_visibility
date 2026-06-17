# M13 Design

## Flow

```text
Config tab model list
  -> PATCH /api/v1/models/{model_registry_id}/visibility
  -> ConfigRepository.update_model_visibility(...)
  -> config.model_registry.enabled_for_visibility
  -> Queue tab run creation snapshots enabled models only
```

## Decisions

- Use a dedicated visibility-toggle route instead of a broad model update route to keep the demo-safe surface narrow.
- Require the model row to be available before it can be enabled; unavailable rows may still be disabled.
- Keep fake-provider rows manageable through the same toggle instead of adding provider-specific cleanup logic.
- The UI refreshes config data after every toggle so counts and queue-planning numbers stay accurate.

## Validation

- Config-service API test covers enabling and disabling a model.
- Cypress demo fixture covers a model toggle control.
- Web build/type check verifies the frontend contract.
