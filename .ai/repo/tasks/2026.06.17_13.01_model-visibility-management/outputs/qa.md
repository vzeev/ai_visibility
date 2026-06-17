# QA Output

## Verdict

Approved for the requested demo gap.

## Acceptance Criteria

- Available model can be enabled: covered by `test_model_visibility_can_be_enabled_and_disabled`.
- Enabled model can be disabled: covered by `test_model_visibility_can_be_enabled_and_disabled`.
- Unavailable model cannot be enabled: covered by `test_unavailable_model_cannot_be_enabled_for_visibility`.
- UI exposes model controls: covered by Cypress click on `toggle-model-gpt-disabled`.
- Existing demo journey still works: `poetry run web-e2e` passed.

## Evidence

- Config-service service tests: 7 passed.
- Web TypeScript/build: passed.
- Cypress demo spec: 1 passed.

## Open Concerns

- Manual operator still needs to sync OpenAI models and choose which real model to enable.
