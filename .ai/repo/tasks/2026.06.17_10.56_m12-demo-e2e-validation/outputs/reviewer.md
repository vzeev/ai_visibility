# Reviewer Output - M12 Demo E2E Validation

Findings: none blocking.

Reviewed risks:

- Cypress uses deterministic intercepts and does not call real OpenAI.
- UI selectors are additive and do not change app behavior.
- `web-e2e` starts and stops only the Vite process it creates.
- Demo docs do not claim production security or AI-assisted extraction as
  already implemented.

Follow-up repo-wide reviewer findings on 2026-06-17:

- `run_web_e2e.py` could leak a Vite process if readiness wait failed.
- `run_web_e2e.py` lacked the Windows npm fallback used by `run_web_check.py`.
- Demo docs still made raw `npm run cy:run` the primary browser validation path.
- Visibility model comparison aggregated only the current page while looking
  global.
- DB fallback still pointed at port `5432` after the local default moved to
  `55433`.

All five findings were fixed and revalidated.

Residual risk:

- Cypress 15.17.0 emits an `allowCypressEnv` warning from upstream defaults.
  Tests still pass; this can be revisited if Cypress config/API changes.

verdict: approved after follow-up fixes.
