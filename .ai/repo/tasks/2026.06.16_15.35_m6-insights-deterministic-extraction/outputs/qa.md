# QA Output

## Verdict

Approved.

## Acceptance Criteria Mapping

- Raw-response extraction API creates completed extraction runs: covered by
  `tests/services/test_insights_service_api.py`.
- Run-batch extraction creates a versioned summary: covered by service and
  Postgres integration tests.
- Same-version reruns are idempotent: service test asserts one extraction run,
  two mentions, and one citation after repeated calls.
- Evidence links include raw response IDs and offsets: service tests assert raw
  response IDs; unit tests cover deterministic span behavior.
- Raw responses remain immutable inputs: repository only writes `insights.*`;
  integration validates against the existing Alembic schema.

## Evidence

- `poetry run test-unit` passed with 17 tests.
- `poetry run test-service` passed with 14 tests.
- `poetry run test-integration` passed skip path with 4 skipped tests.
- Docker-backed `poetry run test-integration` passed with 4 tests.
- `poetry run precommit` passed.
- `poetry run test-all` passed.

## Warnings

- Existing FastAPI/Starlette TestClient deprecation warning remains.
- Existing Alembic `path_separator` deprecation warning remains.

## Handoff

completed_work: QA validation completed.
key_decisions: approve M6 acceptance criteria.
deviations_from_plan: none.
open_concerns: no blockers.
important_findings: clean Postgres test run required disabling the M6 seed model
for visibility to avoid interfering with older tests.
recommended_next_actions: technical writer and manager closure sync.
verification_status: approved.
