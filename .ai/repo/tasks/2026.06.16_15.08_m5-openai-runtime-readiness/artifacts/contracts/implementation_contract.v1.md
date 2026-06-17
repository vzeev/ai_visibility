# M5 Implementation Contract V1

## Objective

Make the visibility worker ready for real OpenAI execution while keeping all
automated tests deterministic and offline.

## User Premise Check

- user_premise_check: `accepted`
- basis: M4 fake-provider worker exists, M2 config owns credentials/rate limits,
  and official OpenAI Responses API schema is available.
- confidence: `high`
- challenge_required: `no`

## In Scope

- Add a credential resolver abstraction for provider runtime tokens.
- Support environment-backed OpenAI runtime credentials keyed by provider.
- Add an `OpenAIResponsesAdapter` that implements `AIProviderAdapter` using
  `POST /v1/responses`.
- Normalize OpenAI responses into the existing `AIResponse` DTO.
- Map OpenAI/http failures to `AIProviderError` without leaking tokens.
- Add a worker rate-limit gate using configured provider/model policies from
  the config snapshot.
- Update worker adapter selection so OpenAI can be enabled explicitly while the
  fake adapter remains the default for tests.
- Add offline unit/service tests with stub HTTP transports and fake credentials.
- Update README, OpenSpec, skeleton checks, and audit artifacts.

## Out Of Scope

- No automated real OpenAI network calls.
- No encrypted-at-rest secret store migration.
- No model discovery sync implementation.
- No UI changes.
- No insights extraction.
- No production distributed rate limiter.

## Acceptance Criteria

1. OpenAI runtime calls are available through the existing provider-neutral
   adapter interface.
2. The adapter creates Responses API-shaped requests and normalizes successful
   responses into `AIResponse`.
3. Missing credentials fail closed as retryable provider errors without exposing
   secrets.
4. HTTP 429 maps to a retryable provider error; 4xx non-rate-limit responses
   map to non-retryable provider errors.
5. Worker execution checks configured provider/model rate-limit policy before
   adapter execution and records rate-limit throttling through M3 error rules.
6. Automated tests remain offline and deterministic.

## Verification Method

- `poetry run test-unit`
- `poetry run test-service`
- `poetry run test-integration` with no DB URL to verify skip behavior.
- `poetry run test-integration` against `docker-compose.test.yml` Postgres.
- `poetry run precommit`
- `poetry run test-all`

## Dependencies And Prerequisites

- Existing M2 config tables and M4 worker path.
- Official OpenAI Responses API schema for request/response mapping.
- Runtime real OpenAI calls require an environment token in `OPENAI_API_KEY`.

## Risks And Likely Failure Modes

- Accidentally logging or persisting tokens.
- Treating all OpenAI HTTP failures as retryable and causing useless retries.
- Building rate-limit behavior that requires wall-clock sleeps in tests.
- Growing the worker into provider-specific logic instead of keeping the adapter
  boundary clean.

## Evidence Ledger

- claim: Responses API creates model responses through `POST /v1/responses`.
  claim_type: `external_fact`
  source_or_artifact: `https://api.openai.com/v1/responses` OpenAPI schema
  verification_status: `verified`
- claim: Responses return `id`, `output`, `usage`, and status/error fields.
  claim_type: `external_fact`
  source_or_artifact: `https://api.openai.com/v1/responses` OpenAPI schema
  verification_status: `verified`
- claim: M2 credential storage stores secret references and redacted
  fingerprints, not plaintext token readback.
  claim_type: `repo_fact`
  source_or_artifact: `apps/config_service/app/db/repository.py`
  verification_status: `verified`

## Open Questions Or Assumptions

- Assumption: M5 may use environment-backed runtime token resolution; a durable
  encrypted secret store is a later slice.

## Approval Status And Version History

- v1 approved for implementation by user request: "ok, implement m5".
