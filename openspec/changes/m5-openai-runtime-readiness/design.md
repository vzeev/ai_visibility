# M5 Design

## Runtime Shape

```text
visibility-worker
  -> rate-limit policy resolver
  -> credential resolver
  -> OpenAIResponsesAdapter / FakeAIProviderAdapter
  -> VisibilityRepository.record_raw_response / record_model_error
```

## Key Decisions

- Real OpenAI execution is an adapter implementation, not worker-specific
  branching.
- Environment-backed token resolution is enough for M5. Config-service still
  owns credential metadata; encrypted secret material can be added later.
- Raw request JSON must not include authorization headers or token material.
- Rate-limit checks are deterministic and testable. M5 throttles when a policy
  is not currently eligible; it does not add sleeps or a distributed limiter.
- Automated tests use `httpx.MockTransport` and fake credentials only.

## Official API Mapping

- Request endpoint: `POST https://api.openai.com/v1/responses`.
- Request fields used by M5: `model`, `input`, optional `instructions`,
  optional `max_output_tokens`, optional `temperature`, optional `text.format`,
  `store=false`, and metadata.
- Response fields normalized by M5: `id`, `model`, `output` text parts,
  `usage`, and raw response JSON.

## Verification

- Unit tests validate adapter request/response/error mapping and rate-limit
  policy eligibility.
- Service tests validate worker behavior with fake OpenAI adapter inputs.
- Integration tests stay opt-in for Postgres and do not call OpenAI.
