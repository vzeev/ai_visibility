# M3 Visibility Queue And Raw Persistence Spec

## ADDED Requirements

### Requirement: Run Creation From Config Snapshot

Visibility-service SHALL create run batches from durable config records and store
an immutable config snapshot on each run batch.

#### Scenario: Run Is Created

- **WHEN** a client creates a run for a brand and prompt set
- **THEN** visibility-service stores a run batch with a config snapshot
- **AND** creates run items for active prompt versions and enabled models.

### Requirement: Queue State And Claiming

Visibility-service SHALL expose queue counts and allow a worker to claim pending
run items.

#### Scenario: Item Is Claimed

- **WHEN** a worker claims the next available item
- **THEN** the item status becomes `running`
- **AND** its attempt count increases.

### Requirement: Idempotent Raw Persistence

Visibility-service SHALL persist raw responses idempotently.

#### Scenario: Completion Is Replayed

- **WHEN** a completed item is submitted again with the same raw provider
  response
- **THEN** visibility-service returns the existing raw response
- **AND** no duplicate raw response row is created.

### Requirement: Retry And Failure Recording

Visibility-service SHALL record model errors and transition item status based on
retryability and attempt limits.

#### Scenario: Attempts Are Exhausted

- **WHEN** a retryable item fails after reaching max attempts
- **THEN** the item status becomes `failed`
- **AND** a model error row records the failure.

### Requirement: Raw Search And Pagination

Visibility-service SHALL expose raw responses with query search and pagination.

#### Scenario: Raw Response Is Searchable

- **WHEN** a client searches raw responses by text
- **THEN** matching raw responses are returned with total count, limit, and
  offset metadata.
