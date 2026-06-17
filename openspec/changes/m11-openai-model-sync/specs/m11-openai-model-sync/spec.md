# M11 OpenAI Model Sync Spec

## ADDED Requirements

### Requirement: OpenAI Model Discovery

The system SHALL discover OpenAI model metadata through the OpenAI Models API without exposing runtime credentials.

#### Scenario: Discover models from OpenAI

- GIVEN `OPENAI_API_KEY` is configured
- WHEN config-service syncs an OpenAI provider
- THEN it calls `GET /v1/models`
- AND it normalizes each returned model id and owner into discovered-model records
- AND it does not store or return the API token.

### Requirement: Model Registry Sync

The config service SHALL upsert discovered provider models into the local registry without automatically enabling them for visibility runs.

#### Scenario: Create newly discovered models

- GIVEN a provider has no local model registry entry for a discovered model
- WHEN model sync completes
- THEN config-service creates the registry entry
- AND `is_available` is true
- AND `enabled_for_visibility` is false.

#### Scenario: Preserve operator model settings

- GIVEN an existing model has `enabled_for_visibility` or a rate-limit policy configured
- WHEN model sync sees that model again
- THEN config-service updates provider metadata
- AND preserves the operator enablement and rate-limit policy.

#### Scenario: Mark missing models unavailable

- GIVEN a provider has an existing model registry entry
- WHEN model sync no longer receives that model id
- THEN config-service marks the model unavailable
- AND does not delete the model row.

### Requirement: Config UI Model Sync

The Config tab SHALL let an operator trigger OpenAI model sync and inspect refreshed registry state.

#### Scenario: Sync models from Config tab

- GIVEN an OpenAI provider exists
- WHEN the operator clicks sync models
- THEN the UI calls the sync endpoint
- AND refreshes the config data
- AND shows discovered, created, updated, and unavailable counts.

