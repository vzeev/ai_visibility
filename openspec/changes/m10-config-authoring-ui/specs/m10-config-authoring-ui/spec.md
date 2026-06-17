# M10 Config Authoring UI Spec

## ADDED Requirements

### Requirement: Provider Credential Authoring

The Config tab SHALL let an operator add provider credentials without exposing token values after submission.

#### Scenario: Create provider credential

- GIVEN at least one provider exists
- WHEN the operator selects a provider, enters a credential label, enters a token, and submits
- THEN config-service creates the credential
- AND the UI refreshes the credential list
- AND the token value is not displayed in readback or success state.

### Requirement: Prompt Authoring

The Config tab SHALL let an operator create prompts and new prompt versions.

#### Scenario: Create prompt

- GIVEN at least one prompt set exists
- WHEN the operator enters prompt name, intent, text, and submits
- THEN config-service creates the prompt with active version 1
- AND the UI refreshes the prompt list.

#### Scenario: Create prompt version

- GIVEN at least one prompt exists
- WHEN the operator selects a prompt, enters new prompt text, and submits
- THEN config-service creates a new active prompt version
- AND the UI refreshes the prompt list with the new version number.

### Requirement: Rate-Limit Authoring

The Config tab SHALL let an operator create provider-level or model-level rate-limit policies.

#### Scenario: Create rate-limit policy

- GIVEN at least one provider exists
- WHEN the operator submits provider, optional model id, request, token, delay, retry, and backoff settings
- THEN config-service creates the rate-limit policy
- AND the UI refreshes the policy count and model-limit area.
