# M11 OpenAI Model Sync Proposal

## Summary

Add a config-service model synchronization path that discovers OpenAI models through `GET /v1/models` and upserts them into the local model registry for explicit operator enablement.

## Motivation

The architecture requires a dynamic model registry because OpenAI model availability changes. M10 made the Config tab writable but left provider model sync unimplemented.

## Non-Goals

- Do not run real OpenAI calls in automated tests.
- Do not enable all discovered models automatically.
- Do not add credential testing, auth/RBAC, or edit/delete model management.
- Do not infer rich model capabilities beyond safe provider metadata.

## Source Links

- Architecture: `docs/decisions/architecture.md`
- M10 reconciliation: `.ai/repo/tasks/2026.06.16_21.32_m10-config-authoring-ui/artifacts/reconciliation/final_reconciliation.md`
- OpenAI API: `GET https://api.openai.com/v1/models`

