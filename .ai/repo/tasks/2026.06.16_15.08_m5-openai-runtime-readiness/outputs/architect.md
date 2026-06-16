# Architect Output

## Scope

Defined M5 as OpenAI runtime readiness behind the existing provider-neutral
adapter boundary.

## Premise Check

- user_premise_check: `accepted`
- basis: M4 worker exists and official OpenAI Responses API schema was reviewed.
- confidence: `high`

## Key Decisions

- Add OpenAI as an adapter implementation, not worker-specific logic.
- Resolve runtime credentials through a small abstraction; use environment
  variables for M5.
- Keep tests offline with mocked HTTP transports and fake tokens.
- Carry configured rate-limit policy into run snapshots and check it before
  adapter execution.

## Handoff

completed_work: M5 contract and OpenSpec plan created.
key_decisions: no real OpenAI calls in tests; real calls opt-in at runtime.
deviations_from_plan: none.
open_concerns: encrypted secret storage and model discovery remain later slices.
recommended_next_actions: implement adapter, credential resolver, rate-limit
gate, tests, and docs.
verification_status: contract-only, later implemented by developer.
