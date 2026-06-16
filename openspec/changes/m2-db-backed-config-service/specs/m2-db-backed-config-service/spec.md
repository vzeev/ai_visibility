# M2 DB-Backed Config Service Spec

## ADDED Requirements

### Requirement: DB-Backed Config CRUD

Config-service SHALL persist configuration writes to the config database schema
and return subsequent reads from database state.

#### Scenario: Brand Is Persisted

- **WHEN** a client creates a brand through config-service
- **THEN** the response contains the created brand identity
- **AND** a later brand list includes that brand.

### Requirement: Prompt Versioning

Config-service SHALL store prompts as prompt records with versioned prompt text.

#### Scenario: Prompt Text Changes

- **WHEN** a client updates prompt text
- **THEN** config-service creates the next prompt version
- **AND** marks the new version as active
- **AND** reads return the new active version.

### Requirement: Write-Only Provider Credentials

Config-service SHALL accept provider tokens as write-only inputs and never return
saved token values in API responses.

#### Scenario: Credential Is Created

- **WHEN** a client creates a provider credential with a token
- **THEN** the response includes credential metadata and redacted fingerprint
- **AND** the response does not include the token value.

### Requirement: Rate Limit And Model Registry Configuration

Config-service SHALL persist provider/model rate-limit policy and model registry
configuration needed by later visibility execution.

#### Scenario: Model Is Enabled

- **WHEN** a client creates or updates a model registry entry with visibility
  enabled
- **THEN** config-service persists the enabled state
- **AND** later reads return the enabled state and associated model metadata.
