# Implementation Contract v1

## Objective

Allow the operator to switch visibility execution from fake models to selected real OpenAI models without direct database edits.

## In Scope

- Config-service endpoint to update `enabled_for_visibility` for one model row.
- Repository validation that unavailable models cannot be enabled.
- Config tab model-list controls for enable/disable.
- Frontend refresh after toggling a model.
- Targeted tests and Cypress fixture coverage.

## Out Of Scope

- Model deletion.
- Bulk model selection.
- Provider creation UI.
- Credential testing or auth.
- Changing OpenAI runtime adapter behavior.

## Acceptance Criteria

- Available models can be enabled through API and UI.
- Enabled models can be disabled through API and UI.
- Unavailable models cannot be enabled.
- Queue planning uses the refreshed enabled model count after toggles.
- Existing fake model rows can be disabled through the same UI.

## Verification Method

- Run config-service API tests for model visibility update.
- Run frontend build/type check.
- Update Cypress fixture to cover model visibility controls.

## Risks

- Existing backend containers must be rebuilt for the new endpoint to be available.
- Old browser data may still show fake raw responses until a new run is created after toggling models.
