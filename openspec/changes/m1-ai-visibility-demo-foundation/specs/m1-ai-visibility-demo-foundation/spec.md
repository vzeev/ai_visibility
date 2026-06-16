# M1 AI Visibility Demo Foundation Spec

## ADDED Requirements

### Requirement: Contract-First Foundation

The repository SHALL contain OpenSpec, API contract, database contract, and enum
contract files before backend service code depends on behavior.

#### Scenario: Contracts Exist

- **WHEN** a developer opens the repository
- **THEN** `contracts/openapi.yaml`, `contracts/database.sql`, and
  `contracts/enums.md` are present
- **AND** the active OpenSpec change references them.

### Requirement: Config-Owned Prompts

The system SHALL model prompts as config-owned, versioned database records.

#### Scenario: Prompt Version Is Snapshotted

- **WHEN** a visibility run is created
- **THEN** the selected prompt version identity is captured for every run item.

### Requirement: Provider-Neutral AI Adapter

The system SHALL define one normalized adapter contract for AI provider calls.

#### Scenario: Provider Implementation Changes

- **WHEN** a provider-specific API client is replaced
- **THEN** visibility scheduling and raw persistence logic continue to consume
  the same normalized request/result DTOs.

### Requirement: Raw Response Idempotency

The system SHALL define deterministic idempotency keys for raw visibility
responses.

#### Scenario: Worker Retries A Completed Item

- **WHEN** a worker retries a run item that already produced a successful raw
  response
- **THEN** the duplicate write is ignored or returns the existing raw response
- **AND** no conflicting second successful raw response is created.

### Requirement: UI-Managed Secret Configuration

The system SHALL allow provider tokens to be configured from the UI without
exposing saved token values in read APIs.

#### Scenario: Credential Is Saved

- **WHEN** the UI saves a provider token
- **THEN** later reads return only credential metadata and a redacted fingerprint
- **AND** the token value is not returned.
