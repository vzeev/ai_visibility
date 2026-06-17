# M8 Docker E2E Polish

## Summary

Add a reproducible local/demo path that proves the full Brandlight AI visibility loop under Docker-backed Postgres:
config seed, visibility queue creation, fake-provider worker processing, raw response persistence, insights extraction, and API/UI-readable results.

## Why

M1-M7 built the foundations, backend services, deterministic worker, OpenAI-ready adapter, insights extraction, and API-backed UI. The interview demo now needs an operator-grade way to start the stack and prove that all pieces work together with meaningful Brandlight demo data.

## Scope

- Deterministic Brandlight demo seed data.
- End-to-end smoke command for config -> visibility -> worker -> raw -> insights.
- Docker/local service wiring polish, including web/backend URLs and CORS defaults.
- Tests for the smoke workflow and runtime wiring.
- README and task checklist updates.

## Non-Goals

- Real paid model calls.
- Production queue infrastructure.
- Authentication.
- New dashboard redesign.

## References

- M7 UI API dashboard change: `openspec/changes/m7-ui-api-dashboard`
