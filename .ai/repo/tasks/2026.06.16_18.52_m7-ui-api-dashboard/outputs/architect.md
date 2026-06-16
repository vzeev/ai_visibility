# Architect Output

## Scope

M7 is a frontend integration slice over existing local service APIs. It should
not expand backend semantics beyond the existing Config, Visibility, and
Insights endpoints.

## Decisions

- Use a lightweight typed `fetch` client and local React hooks.
- Keep service URLs configurable via Vite env variables with localhost defaults.
- Treat failed service requests as expected local-development states.
- Keep the UI dense, scan-friendly, and operational rather than marketing-like.

## Verification

- TypeScript test/build.
- Precommit/test-all.
- Browser screenshot checks for desktop and mobile.

## Handoff

completed_work: M7 implementation contract and architecture direction created.
key_decisions: typed fetch client, no new dependency, real error states.
deviations_from_plan: none.
open_concerns: services may not be running during browser validation.
important_findings: existing UI is fully static and needs replacement.
recommended_next_actions: product framing then frontend implementation.
verification_status: architecture ready.
