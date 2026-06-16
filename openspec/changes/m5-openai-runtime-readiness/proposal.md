# M5 OpenAI Runtime Readiness

## Summary

Add real OpenAI Responses API runtime readiness behind the existing
provider-neutral adapter boundary, while keeping tests fake/offline.

## Goals

- Implement an OpenAI adapter that maps into the existing `AIProviderAdapter`.
- Resolve OpenAI runtime credentials without exposing tokens in API responses,
  logs, raw payloads, or tests.
- Gate worker execution through configured provider/model rate-limit policy.
- Keep fake adapter as the default automated-test execution path.

## Non-Goals

- No automated real OpenAI network calls.
- No UI changes.
- No model discovery sync.
- No encrypted secret storage migration.
- No insights extraction.

## Architecture References

- `docs/decisions/architecture.md`
- `apps/shared/ai/provider.py`
- `apps/shared/ai/rate_limits.py`
- `apps/worker/app/visibility_worker.py`
- Official OpenAI Responses API schema for `POST /v1/responses`.
