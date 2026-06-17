# Developer Output - M12 Demo E2E Validation

Implemented:

- Cypress config and main demo spec.
- Web scripts: `cy:open`, `cy:run`, `test:e2e`.
- Root scripts: `demo-check`, `web-e2e`.
- Demo docs under `docs/demo/`.
- Stable `data-cy` selectors for the main workflow.
- Queue run expansion summary.
- Visibility model comparison summary.
- Deterministic extraction label in normal and empty insights states.
- Unit coverage for the demo-check script.
- README and skeleton check updates.

notes:

- The first Cypress attempt exposed missing Windows env vars in the shell and a
  user-cache permission requirement. `scripts/run_web_e2e.py` now sets the
  needed env defaults and starts Vite automatically when the UI is not already
  running.

