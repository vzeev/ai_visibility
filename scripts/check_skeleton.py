from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    ".pre-commit-config.yaml",
    ".env.example",
    "docker-compose.yml",
    "docker-compose.test.yml",
    "pyproject.toml",
    "contracts/openapi.yaml",
    "contracts/database.sql",
    "docs/decisions/architecture.md",
    "openspec/config.yaml",
    "openspec/changes/m1-ai-visibility-demo-foundation/specs/m1-ai-visibility-demo-foundation/spec.md",
    "alembic/alembic.ini",
    "alembic/env.py",
    "alembic/versions/20260616_0924_initial_foundation.py",
    "apps/config_service/app/main.py",
    "apps/visibility_service/app/main.py",
    "apps/insights_service/app/main.py",
    "apps/worker/app/main.py",
    "apps/shared/ai/provider.py",
    "apps/shared/ai/idempotency.py",
    "apps/shared/ai/rate_limits.py",
    "apps/shared/ai/secrets.py",
    "apps/web/package.json",
    "apps/web/src/app/App.tsx",
    "scripts/run_web_check.py",
]

REQUIRED_MARKERS = {
    ".pre-commit-config.yaml": [
        "pre-commit-hooks",
        "ruff-pre-commit",
        "PyCQA/bandit",
        "pyright-python",
        "skeleton-check",
        "web-typecheck",
    ],
    "pyproject.toml": [
        "pre-commit =",
        "doctor =",
        "fix =",
        "precommit =",
        "test-integration =",
        "test-service =",
        "test-servcie =",
        "[tool.bandit]",
    ],
    "contracts/database.sql": [
        "CREATE TABLE config.prompts",
        "CREATE TABLE config.provider_credentials",
        "CREATE TABLE config.rate_limit_policies",
        "idempotency_key text NOT NULL UNIQUE",
        "CREATE TABLE visibility.raw_responses",
        "CREATE TABLE insights.extracted_mentions",
    ],
    "contracts/openapi.yaml": [
        "/api/v1/provider-credentials:",
        "writeOnly: true",
        "/api/v1/rate-limits:",
        "/api/v1/raw-responses:",
    ],
    "apps/shared/ai/provider.py": [
        "class AIProviderAdapter",
        "class FakeAIProviderAdapter",
    ],
    "apps/shared/ai/idempotency.py": [
        "build_run_item_idempotency_key",
        "build_raw_response_idempotency_key",
    ],
    "apps/web/src/app/App.tsx": [
        "Config",
        "Queue",
        "Visibility",
        "Insights",
    ],
}


def main() -> int:
    missing_paths = [path for path in REQUIRED_PATHS if not (REPO_ROOT / path).exists()]
    marker_failures: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                marker_failures.append(f"{relative_path}: missing marker {marker!r}")

    if missing_paths or marker_failures:
        for path in missing_paths:
            print(f"missing required path: {path}")
        for failure in marker_failures:
            print(failure)
        return 1

    print("AI visibility foundation skeleton check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
