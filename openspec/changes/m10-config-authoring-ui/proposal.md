# M10 Config Authoring UI

## Summary

Add safe authoring controls to the Config tab for provider credentials, prompts, prompt versions, and rate-limit policies using existing config-service APIs.

## Why

The architecture requires configuration to be the source of truth. M7 and M9 made configuration visible, but not editable from the UI. M10 closes the most important demo gap: operators can configure tokens, prompts, and rate limits without leaving the dashboard.

## Scope

- Provider credential create form with write-only token input.
- Prompt create form.
- Prompt version create form.
- Provider/model rate-limit create form.
- API client methods, UI state handling, docs, and checks.

## Non-Goals

- Credential test calls.
- Provider model discovery.
- Record editing/deletion.
- Real provider execution.
- Auth/RBAC.

## References

- Architecture: `.ai/repo/tasks/2026.06.16_08.02_brandlight-visibility-architecture/artifacts/spec/architecture_proposal.md`
- Implementation contract: `.ai/repo/tasks/2026.06.16_21.32_m10-config-authoring-ui/artifacts/contracts/implementation_contract.v1.md`
