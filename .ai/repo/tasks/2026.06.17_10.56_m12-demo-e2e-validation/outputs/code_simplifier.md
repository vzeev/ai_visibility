# Code Simplifier Output - M12 Demo E2E Validation

No extra refactor pass was required beyond targeted cleanup:

- Cypress test data is kept in one spec because the suite currently validates
  one interview journey.
- `run_web_e2e.py` owns Vite startup and Cypress execution so shell-specific
  Windows env fixes do not leak into README commands.
- Demo docs are split by presentation purpose: architecture, technical
  implementation, and main flow.

Follow-up repo-wide simplifier findings on 2026-06-17:

- Docker web startup used `npm install` instead of deterministic `npm ci`.
- Browser demo URL was split between `localhost` and `127.0.0.1`.
- README referenced a non-existent `insights-worker`.
- Public command surface still documented the typo alias `test-servcie`.

All four findings were fixed and revalidated.

verdict: approved after follow-up fixes.
