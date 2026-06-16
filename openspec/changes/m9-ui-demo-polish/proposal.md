# M9 UI Demo Polish

## Summary

Polish the React/Vite dashboard so the local Brandlight demo presents a clear, credible pipeline story: configuration readiness, queue/run status, raw evidence, and extracted insights.

## Why

M8 proved the full Docker-backed data flow. M9 turns that working backend state into a stronger interview demo surface by making the dashboard easier to scan and by adding a UI-triggered deterministic insights action for the latest completed run.

## Scope

- Live demo overview across config, queue/raw, and insights.
- Config, Visibility, and Insights panel polish.
- Insights action using the existing run-batch extraction endpoint.
- Responsive/browser validation.

## Non-Goals

- Real model calls from the UI.
- Auth/RBAC.
- New production deployment work.
- Full dashboard redesign.

## References

- M8 change: `openspec/changes/m8-docker-e2e-polish`
- Architecture: `.ai/repo/tasks/2026.06.16_08.02_brandlight-visibility-architecture/artifacts/spec/architecture_proposal.md`
- Implementation contract: `.ai/repo/tasks/2026.06.16_20.46_m9-ui-demo-polish/artifacts/contracts/implementation_contract.v1.md`
