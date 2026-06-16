# M5 OpenAI Runtime Readiness Spec

## ADDED Requirements

### Requirement: OpenAI Adapter Uses Provider-Neutral Contract

The system SHALL provide an OpenAI Responses API adapter that implements the
existing `AIProviderAdapter` contract.

#### Scenario: OpenAI Response Succeeds

- **WHEN** the OpenAI adapter receives an `AIRequest`
- **THEN** it sends a Responses API-shaped request
- **AND** returns an `AIResponse` with normalized output text, usage, raw
  request JSON, raw response JSON, latency, and provider response id.

### Requirement: Runtime Credentials Fail Closed

OpenAI runtime credentials SHALL be resolved through a dedicated abstraction and
missing credentials SHALL fail closed.

#### Scenario: Credential Is Missing

- **WHEN** an OpenAI request is attempted without a runtime token
- **THEN** the adapter raises a retryable provider error
- **AND** no token or secret reference is written to raw request/response data.

### Requirement: Provider Errors Are Classified

The OpenAI adapter SHALL classify retryable and non-retryable provider failures.

#### Scenario: OpenAI Rate Limit

- **WHEN** OpenAI returns HTTP 429
- **THEN** the adapter raises a retryable provider error.

#### Scenario: Non-Retryable Client Error

- **WHEN** OpenAI returns another 4xx response
- **THEN** the adapter raises a non-retryable provider error.

### Requirement: Worker Checks Configured Rate Limits

The visibility worker SHALL check configured provider/model rate-limit policy
before adapter execution.

#### Scenario: Policy Is Not Eligible

- **WHEN** a run item is claimed before its policy is eligible
- **THEN** the worker records a retryable `rate_limit` error
- **AND** the item becomes throttled using M3 retry rules.

### Requirement: Automated Tests Stay Offline

M5 automated tests SHALL NOT call real OpenAI network endpoints.

#### Scenario: Adapter Is Tested

- **WHEN** adapter tests run
- **THEN** they use stubbed HTTP transports and fake runtime credentials.
