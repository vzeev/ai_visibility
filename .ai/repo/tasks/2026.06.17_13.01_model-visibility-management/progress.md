# Progress

task_goal: Implement operator controls to enable real OpenAI models and disable fake models so visibility runs produce real OpenAI evidence.

path_context: installed_consumer

selected_flow: openspec-feature-implementation

selected_artifact_profile: audit_standard

flow_approval: User requested "ok, implement the gaps" after runtime investigation showed OpenAI was enabled but only the fake model was enabled in config.

tracker: not_active

delegation_availability: direct Codex implementation; no external tracker.

current_stage: closure_ready

scope:
- Add model visibility update API.
- Add Config tab controls to enable/disable model rows.
- Keep model sync and credential handling unchanged.

blockers: none

completed_work:
- Added config-service model visibility update API.
- Added Config tab model enable/disable controls.
- Updated OpenSpec M13, README, and demo flow docs.
- Added targeted backend and Cypress coverage.

checks_run:
- `c:\Users\vladi\.local\bin\poetry.exe run python -m pytest tests/services/test_config_service_api.py` - passed
- `npm run build` from `apps/web` - passed
- `c:\Users\vladi\.local\bin\poetry.exe run web-check` - passed
- `c:\Users\vladi\.local\bin\poetry.exe run web-e2e` - passed
- `c:\Users\vladi\.local\bin\poetry.exe run python scripts/check_skeleton.py` - passed

expected_runtime_follow_up:
- Rebuild/restart Docker services.
- In Config tab, sync OpenAI models if not already synced.
- Disable `brandlight-fake-v1`.
- Enable one selected OpenAI model.
- Create a new run, wait for worker processing, then refresh Visibility tab.

artifact_index:
- OpenSpec proposal: openspec/changes/m13-model-visibility-management/proposal.md
- OpenSpec design: openspec/changes/m13-model-visibility-management/design.md
- OpenSpec tasks: openspec/changes/m13-model-visibility-management/tasks.md
- OpenSpec spec: openspec/changes/m13-model-visibility-management/specs/m13-model-visibility-management/spec.md
- Contract: .ai/repo/tasks/2026.06.17_13.01_model-visibility-management/artifacts/contracts/implementation_contract.v1.md
- Developer output: .ai/repo/tasks/2026.06.17_13.01_model-visibility-management/outputs/developer.md
- Reviewer output: .ai/repo/tasks/2026.06.17_13.01_model-visibility-management/outputs/reviewer.md
- Security output: .ai/repo/tasks/2026.06.17_13.01_model-visibility-management/outputs/security.md
- QA output: .ai/repo/tasks/2026.06.17_13.01_model-visibility-management/outputs/qa.md
- Technical writer output: .ai/repo/tasks/2026.06.17_13.01_model-visibility-management/outputs/technical_writer.md

verification_plan:
- config-service API tests
- web build
- Cypress/demo fixture update if practical
