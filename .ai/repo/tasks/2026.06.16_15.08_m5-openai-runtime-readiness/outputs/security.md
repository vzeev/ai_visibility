# Security Output

## Scope Reviewed

- Current working tree changes around `.env` loading, OpenAI API key handling,
  `docker-compose.yml`, README guidance, and integration/unit tests.
- Secret values were not inspected.

## Verdict

Pass after remediation.

## Findings Resolved

1. Medium credential-precedence risk resolved.
   - Fix:
     `bootstrap_repo_env()` now treats repo `.env` values for `OPENAI_API_KEY`
     and `ENABLE_OPENAI` as authoritative for local repo entry points, so an
     inherited generic key cannot silently override the project file.
   - Regression coverage:
     `tests/unit/test_runtime_env.py` verifies repo `.env` precedence and
     `EnvironmentCredentialResolver` behavior, and
     `tests/unit/test_worker_runtime.py` verifies `ENABLE_OPENAI` activates the
     OpenAI worker path.

2. Medium destructive integration reset risk resolved.
   - Fix:
     `reset_postgres_schema()` now requires `AI_VISIBILITY_ALLOW_DB_RESET=true`,
     a local PostgreSQL host, and a database name containing `test`.
   - Regression coverage:
     `tests/unit/test_db_reset_safety.py` covers missing guard, remote URL,
     non-test database, and accepted local test URL cases.

## Hardening Notes

- Low: the worker mounts the repo `.env` into the container instead of
  only the OpenAI runtime secret.
  - References:
    - `docker-compose.yml:72-73`
    - `.env.example:7-24`
    - `README.md:165-169`
  - Risk:
    Any code execution inside the worker container can read every value in the
    mounted dotenv file, not just `OPENAI_API_KEY`.
  - Suggested fix:
    Use a dedicated worker-only env file or Docker secrets so the container gets
    only the keys it actually needs.

- Resolved: `load_repo_env()` no longer imports every syntactically valid key
  from `.env`.
  - References:
    - `apps/shared/runtime/env.py`
  - Fix:
    Dotenv loading is restricted to `DEFAULT_REPO_ENV_KEYS`; generic process
    controls such as proxy or CA variables are ignored by default.

## Handoff

completed_work: reviewed current working tree security impact and remediations
without reading secret values.
key_decisions: generic env names remain accepted, but repo `.env` wins for
local runtime entry points; destructive test resets require an explicit guard
and local test database target.
deviations_from_plan: none.
open_concerns: worker `.env` mount remains a defense-in-depth item; README now
documents the required `.env` file before Docker worker execution.
recommended_next_actions: consider Docker secrets or a worker-only env file if
the demo grows beyond local interview use.
verification_status: passing after remediation.
