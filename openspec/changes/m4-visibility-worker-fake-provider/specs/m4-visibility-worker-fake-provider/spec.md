# M4 Visibility Worker Fake Provider Spec

## ADDED Requirements

### Requirement: Worker Processes One Queued Item

The visibility worker SHALL claim a pending queue item, build a provider-neutral
AI request, call the fake provider adapter, and persist the raw response.

#### Scenario: Pending Item Succeeds

- **WHEN** the worker processes one pending run item
- **THEN** it stores one raw response through the visibility repository
- **AND** the run item status becomes `succeeded`.

### Requirement: Provider-Neutral Request Construction

The visibility repository SHALL expose a public method for constructing an
`AIRequest` from a run item and its config snapshot.

#### Scenario: Worker Builds A Request

- **WHEN** the worker claims a run item
- **THEN** it receives provider key, model id, prompt text, and idempotency
  metadata from the repository
- **AND** it does not parse private snapshot internals directly.

### Requirement: Provider Error Recording

The visibility worker SHALL record provider adapter errors through the existing
model error and retry behavior.

#### Scenario: Retryable Provider Error

- **WHEN** the provider adapter raises a retryable error
- **THEN** the worker records a model error
- **AND** the run item remains eligible for retry until max attempts are
  exhausted.

### Requirement: Bounded Batch Processing

The visibility worker SHALL support bounded batch execution.

#### Scenario: Batch Limit Is Reached

- **WHEN** `max_items` is lower than the number of pending queue items
- **THEN** the worker processes no more than `max_items`.

#### Scenario: Queue Is Empty

- **WHEN** no queue item is available
- **THEN** the worker returns an idle result and stops the batch.
