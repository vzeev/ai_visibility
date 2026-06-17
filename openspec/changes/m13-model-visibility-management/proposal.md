# M13 Model Visibility Management

## Why

OpenAI model sync creates real model registry rows, but newly synced models are disabled by default. The demo operator currently cannot enable a real OpenAI model or disable the fake model from the UI, so creating a run continues to produce fake-provider evidence.

## What

- Add a config-service API to update `enabled_for_visibility` for an existing model registry row.
- Add Config tab controls to enable or disable individual models.
- Preserve the existing model sync behavior: newly discovered models remain disabled until the operator explicitly enables them.
- Keep credentials out of browser-visible model management.

## Non-goals

- Delete model rows.
- Bulk enable all OpenAI models.
- Change provider credential storage.
- Add auth/RBAC.
