# Security Output

security_verdict: `PASS_WITH_HARDENING_REQUIREMENTS`

## Scope Reviewed

Reviewed proposed service boundaries, OpenAI integration, raw data storage, Docker/Postgres assumptions, and UI rendering implications.

## Blocking Findings

None at architecture stage.

## Hardening Requirements

- Read `OPENAI_API_KEY` only from environment variables or a local secret mechanism.
- If API tokens are configured through the UI, the UI/API must be write-only for secret values and return only redacted metadata after save.
- UI-managed provider tokens must be encrypted at rest or stored outside the DB behind a secret-reference abstraction; plaintext token storage is not accepted.
- Never log API keys, authorization headers, full environment dumps, or secret-bearing exception objects.
- Add `.env` to `.gitignore` and provide `.env.example` only.
- Treat raw model output as untrusted text in the UI; do not render it as HTML.
- Put request-size limits on API endpoints that accept prompt text or raw payload filters.
- Ensure fake/test adapters are the default in automated tests.
- Avoid exposing Postgres outside local dev unless explicitly needed.
- If auth/RBAC is postponed, document that this is a local single-operator demo constraint.

## Attack Scenarios Considered

- Secret leakage through logs or committed files.
- Cross-site scripting through raw model output.
- Cost/rate-limit abuse if run creation is unbounded.
- Secret disclosure through provider credential readback, browser state, logs, or raw response payloads.
- Prompt/config payloads causing oversized requests or worker overload.
- Confusion between raw untrusted output and trusted insight data.

## Checks Run

- Architecture security review only; no runtime checks.

## Rich Handoff

completed_work: Reviewed security boundaries.
key_decisions: No blocker, but implementation must include secret, raw-output, and cost-control safeguards.
deviations_from_plan: None.
open_concerns: Auth/RBAC deferral needs explicit user approval.
important_findings: Raw LLM output is both a product artifact and an untrusted input.
recommended_next_actions: Carry hardening requirements into contracts and first implementation tasks.
verification_status: Design-level pass; implementation not verified.
