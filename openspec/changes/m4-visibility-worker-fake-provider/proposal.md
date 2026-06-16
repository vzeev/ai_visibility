# M4 Visibility Worker Fake Provider

## Summary

Implement the first worker execution path for the visibility queue using the
provider-neutral fake AI adapter.

## Goals

- Process pending visibility run items outside the HTTP route layer.
- Build provider-neutral AI requests from immutable config snapshots.
- Persist fake provider responses as raw visibility evidence.
- Record provider failures through existing queue retry/failure rules.
- Keep the worker bounded and testable.

## Non-Goals

- No real provider network calls.
- No long-running scheduler or process supervisor.
- No rate-limit execution engine.
- No insights extraction.
- No UI changes.

## Architecture References

- `docs/decisions/architecture.md`
- `apps/shared/ai/provider.py`
- `apps/visibility_service/app/db/repository.py`
- `.ai/repo/tasks/2026.06.16_14.43_m4-visibility-worker-fake-provider/artifacts/contracts/implementation_contract.v1.md`
