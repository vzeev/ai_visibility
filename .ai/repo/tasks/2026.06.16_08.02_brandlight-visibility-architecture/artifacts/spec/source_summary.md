# Source Summary

## User Request

- Build a stable simple interview-demo service.
- Initialize the current repo properly, including OpenSpec, Docker, and Postgres.
- Prepare architecture before implementation.
- Do not start implementation until the user approves the architecture.
- Target shape: Python config service, Python visibility service, Python insights service, React/Vite UI.
- Required technical choices: Python, Poetry, React, Vite, Postgres, Alembic, unit/service/integration tests.
- Reference technical decisions from `c:\Repos\2026.05.15_finfrax\`.

## Brandlight Notes Reviewed

Source files:

- `C:\VladimirSoskin\Dropbox\Documents\личное\фин\obsidian\projects\!future\teamlead\brandlight\Brandlight Offline CEO Interview Preparation.md`
- `C:\VladimirSoskin\Dropbox\Documents\личное\фин\obsidian\projects\!future\teamlead\brandlight\brandlight_vp_rnd_technical_interview_prep.md`

Relevant source-backed themes:

- Brandlight is framed in the notes as an enterprise AI visibility platform, not a simple LLM wrapper.
- The core product problem is trusted measurement around unstable AI answers: prompts, AI engine/model responses, raw answers, citations/sources, brand and competitor mentions, sentiment, scores, dashboards, and recommendations.
- The interview goal is to show calm senior judgment: reduce ambiguity, preserve raw facts, expose assumptions, and build explainable data-heavy B2B SaaS workflows.
- The VP R&D prep specifically emphasizes:
  - controlled prompt universe by category, persona, geography, language, and funnel stage
  - AI answer collection through adapters with rate limits, retries, idempotency, and raw storage
  - extraction/enrichment that combines deterministic matching, aliases, fuzzy logic, URL/domain parsing, and structured LLM extraction
  - versioned extraction logic and raw-data preservation for reprocessing
  - metrics that aggregate across runs, engines, prompt groups, and time windows
  - enterprise drilldown from score to prompt, answer, citation/source, and extraction result
  - dashboard performance with server-side filtering, pagination, pre-aggregations, and prepared APIs

## Finfrax Reference Reviewed

Source files inspected:

- `c:\Repos\2026.05.15_finfrax\README.md`
- `c:\Repos\2026.05.15_finfrax\docs\decisions\architecture.md`
- `c:\Repos\2026.05.15_finfrax\pyproject.toml`
- `c:\Repos\2026.05.15_finfrax\docker-compose.yml`
- `c:\Repos\2026.05.15_finfrax\docker-compose.test.yml`
- `c:\Repos\2026.05.15_finfrax\openspec\README.md`
- `c:\Repos\2026.05.15_finfrax\openspec\config.yaml`
- `c:\Repos\2026.05.15_finfrax\contracts\README.md`
- `c:\Repos\2026.05.15_finfrax\docs\workflows\contract-workflow.md`
- `c:\Repos\2026.05.15_finfrax\infra\docker\python-service.Dockerfile`
- `c:\Repos\2026.05.15_finfrax\alembic\env.py`
- `c:\Repos\2026.05.15_finfrax\apps\ai_service\app\api\routes.py`
- `c:\Repos\2026.05.15_finfrax\apps\web\package.json`

Patterns to mirror:

- Root Poetry project for Python runtime dependencies, dev tooling, and command wrappers.
- Import-safe source directories under `apps/`; external service names can stay hyphenated in Docker, URLs, logs, and product text.
- Python FastAPI service layout:

```text
app/
  main.py
  api/
  clients/
  db/
  domain/
  schemas/
  services/
tests/
```

- Service business logic stays out of shared packages; shared code is stateless helpers and DTOs only.
- Alembic owns durable database schema; ORM models mirror the contract rather than inventing schema truth.
- OpenSpec `changes/` holds proposed behavior; `specs/` holds accepted durable baseline.
- Compose stack uses health-gated Postgres/Redis/migrations before app service health.
- Test harness separates unit, service, and integration checks.
- Web workspace is isolated under `apps/web` with Vite, React, TypeScript, and Vitest.

Patterns to simplify for this repo:

- Use Python-only backend services for the MVP instead of Finfrax's Go gateway exception.
- Start without full enterprise auth/RBAC unless the user approves adding it later.
- Use one Postgres database with service-owned schemas first; separate DB roles can be a later hardening slice.
- Use an in-Postgres queue or a minimal worker loop first; Redis/Celery can be a phase-two decision if the queue pressure justifies it.

## Source Boundaries

- Brandlight public/company facts are taken from user-supplied notes, not independently re-verified during this task.
- The architecture should not claim to represent Brandlight's internal system.
- The architecture is for an interview demo inspired by the source notes.
- No implementation files, OpenSpec files, Docker files, migrations, or app code may be created until user approval.
