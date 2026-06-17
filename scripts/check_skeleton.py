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
    "alembic/versions/20260616_2018_model_registry_created_at.py",
    "apps/config_service/app/main.py",
    "apps/visibility_service/app/main.py",
    "apps/insights_service/app/main.py",
    "apps/insights_service/app/db/models.py",
    "apps/insights_service/app/db/repository.py",
    "apps/insights_service/app/db/session.py",
    "apps/insights_service/app/domain/extractor.py",
    "apps/worker/app/main.py",
    "apps/config_service/app/db/models.py",
    "apps/config_service/app/db/repository.py",
    "apps/config_service/app/db/session.py",
    "apps/visibility_service/app/db/models.py",
    "apps/visibility_service/app/db/repository.py",
    "apps/visibility_service/app/db/session.py",
    "apps/shared/ai/provider.py",
    "apps/shared/ai/credentials.py",
    "apps/shared/ai/idempotency.py",
    "apps/shared/ai/model_discovery.py",
    "apps/shared/ai/openai_provider.py",
    "apps/shared/ai/rate_limits.py",
    "apps/shared/http/cors.py",
    "apps/shared/runtime/env.py",
    "apps/shared/ai/secrets.py",
    "apps/worker/app/visibility_worker.py",
    "apps/web/package.json",
    "apps/web/src/app/App.tsx",
    "apps/web/src/components/DataState.tsx",
    "apps/web/src/features/overview/DemoOverview.tsx",
    "apps/web/src/lib/api.ts",
    "apps/web/src/lib/useAsyncData.ts",
    "apps/web/src/vite-env.d.ts",
    "scripts/run_web_check.py",
    "scripts/ai_visibility_tools/demo_e2e.py",
    "tests/services/test_cors.py",
    "tests/services/test_config_service_api.py",
    "tests/services/test_demo_e2e.py",
    "tests/services/test_visibility_service_api.py",
    "tests/services/test_visibility_worker.py",
    "tests/services/test_insights_service_api.py",
    "tests/integration/test_config_service_postgres.py",
    "tests/integration/test_visibility_service_postgres.py",
    "tests/integration/test_visibility_worker_postgres.py",
    "tests/integration/test_insights_service_postgres.py",
    "tests/unit/test_insights_extractor.py",
    "tests/unit/test_db_reset_safety.py",
    "tests/unit/test_openai_provider_adapter.py",
    "tests/unit/test_openai_model_discovery.py",
    "tests/unit/test_runtime_env.py",
    "tests/unit/test_worker_runtime.py",
    "openspec/changes/m2-db-backed-config-service/specs/m2-db-backed-config-service/spec.md",
    "openspec/changes/m3-visibility-queue-raw-persistence/specs/m3-visibility-queue-raw-persistence/spec.md",
    "openspec/changes/m4-visibility-worker-fake-provider/specs/m4-visibility-worker-fake-provider/spec.md",
    "openspec/changes/m5-openai-runtime-readiness/specs/m5-openai-runtime-readiness/spec.md",
    "openspec/changes/m6-insights-deterministic-extraction/specs/m6-insights-deterministic-extraction/spec.md",
    "openspec/changes/m7-ui-api-dashboard/specs/m7-ui-api-dashboard/spec.md",
    "openspec/changes/m8-docker-e2e-polish/specs/m8-docker-e2e-polish/spec.md",
    "openspec/changes/m9-ui-demo-polish/specs/m9-ui-demo-polish/spec.md",
    "openspec/changes/m10-config-authoring-ui/specs/m10-config-authoring-ui/spec.md",
    "openspec/changes/m11-openai-model-sync/specs/m11-openai-model-sync/spec.md",
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
        "demo-e2e =",
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
        "CREATE TABLE config.model_registry",
        "discovered_at timestamptz NOT NULL DEFAULT now()",
        "idempotency_key text NOT NULL UNIQUE",
        "CREATE TABLE visibility.raw_responses",
        "CREATE TABLE insights.extracted_mentions",
    ],
    "contracts/openapi.yaml": [
        "/api/v1/prompt-sets:",
        "/api/v1/providers:",
        "/api/v1/provider-credentials:",
        "writeOnly: true",
        "/api/v1/rate-limits:",
        "/api/v1/models:",
        "/api/v1/providers/{provider_id}/models/sync:",
        "ModelSyncResponse:",
        "/api/v1/queue/claim:",
        "/api/v1/queue/items/{run_item_id}/complete:",
        "RawResponseItem:",
        "/api/v1/raw-responses:",
        "/api/v1/extractions/raw-responses/{raw_response_id}:",
        "/api/v1/extractions/run-batches/{run_batch_id}:",
        "ExtractionRun:",
    ],
    "apps/config_service/app/db/repository.py": [
        "class ConfigRepository",
        "create_provider_credential",
        "create_prompt_version",
        "create_rate_limit",
        "sync_models",
    ],
    "apps/config_service/app/api/routes.py": [
        "/providers/{provider_id}/models/sync",
        "get_model_discovery_client",
        "ModelSyncResponse",
    ],
    "apps/visibility_service/app/db/repository.py": [
        "class VisibilityRepository",
        "claim_next_item",
        "record_model_error",
        "record_raw_response",
        "build_ai_request",
        "build_raw_response_idempotency_key",
    ],
    "apps/shared/ai/provider.py": [
        "class AIProviderAdapter",
        "class FakeAIProviderAdapter",
    ],
    "apps/shared/ai/credentials.py": [
        "class EnvironmentCredentialResolver",
        "class StaticCredentialResolver",
        "MissingProviderCredentialError",
    ],
    "apps/shared/ai/model_discovery.py": [
        "class OpenAIModelDiscoveryClient",
        "OPENAI_MODELS_ENDPOINT",
        "class DiscoveredModel",
        "ModelDiscoveryError",
    ],
    "apps/shared/ai/openai_provider.py": [
        "class OpenAIResponsesAdapter",
        "OPENAI_RESPONSES_ENDPOINT",
        "store",
        "Authorization",
        "AIProviderError",
    ],
    "apps/shared/ai/idempotency.py": [
        "build_run_item_idempotency_key",
        "build_raw_response_idempotency_key",
    ],
    "apps/shared/ai/rate_limits.py": [
        "class RateLimitPolicy",
        "class InMemoryRateLimitGate",
        "rate_limit_policy_from_mapping",
    ],
    "apps/shared/http/cors.py": [
        "AI_VISIBILITY_CORS_ORIGINS",
        "CORSMiddleware",
        "http://localhost:5173",
    ],
    "apps/shared/runtime/env.py": [
        "bootstrap_repo_env",
        "load_repo_env",
        "find_repo_env",
        "DEFAULT_REPO_ENV_KEYS",
        "_parse_dotenv_lines",
    ],
    "docker-compose.yml": [
        "VITE_CONFIG_SERVICE_URL",
        "VITE_VISIBILITY_SERVICE_URL",
        "VITE_INSIGHTS_SERVICE_URL",
        "AI_VISIBILITY_CORS_ORIGINS",
        "visibility-worker",
    ],
    "apps/worker/app/visibility_worker.py": [
        "class VisibilityWorker",
        "process_one",
        "process_batch",
        "OpenAIResponsesAdapter",
        "rate_limit_policy_from_mapping",
        "FakeAIProviderAdapter",
        "record_raw_response",
        "record_model_error",
    ],
    "apps/insights_service/app/domain/extractor.py": [
        "class DeterministicInsightExtractor",
        "DEFAULT_EXTRACTION_VERSION",
        "EntityAliases",
    ],
    "apps/insights_service/app/db/repository.py": [
        "class InsightsRepository",
        "extract_raw_response",
        "extract_run_batch",
        "raw_response_id",
        "VisibilitySummary",
    ],
    "apps/insights_service/app/api/routes.py": [
        "/extractions/raw-responses/{raw_response_id}",
        "/extractions/run-batches/{run_batch_id}",
        "/summaries",
    ],
    "apps/web/src/app/App.tsx": [
        "Config",
        "Queue",
        "Visibility",
        "Insights",
        "DemoOverview",
    ],
    "apps/web/src/lib/api.ts": [
        "VITE_CONFIG_SERVICE_URL",
        "VITE_VISIBILITY_SERVICE_URL",
        "VITE_INSIGHTS_SERVICE_URL",
        "configApi",
        "visibilityApi",
        "insightsApi",
        "extractRunBatch",
        "createCredential",
        "createPromptVersion",
        "createRateLimit",
        "syncModels",
        "ModelSyncResponse",
    ],
    "apps/web/src/features/overview/DemoOverview.tsx": [
        "Demo brand",
        "Raw evidence",
        "Insights",
        "visibilityApi.rawResponses",
    ],
    "apps/web/src/features/config/ConfigPanel.tsx": [
        "configApi",
        "Config service unavailable",
        "Active setup",
        "Config authoring",
        "Save credential",
        "Create prompt",
        "Activate new version",
        "Create rate limit",
        "Sync OpenAI models",
    ],
    "apps/web/src/features/queue/QueuePanel.tsx": [
        "visibilityApi.createRun",
        "Create visibility run",
    ],
    "apps/web/src/features/visibility/VisibilityPanel.tsx": [
        "visibilityApi.rawResponses",
        "Evidence detail",
        "Idempotency key",
    ],
    "apps/web/src/features/insights/InsightsPanel.tsx": [
        "insightsApi.summaries",
        "Extraction evidence",
        "Analyze latest run",
    ],
    "scripts/ai_visibility_tools/demo_e2e.py": [
        "seed_brandlight_demo",
        "run_brandlight_demo_smoke",
        "VisibilityWorker",
        "InsightsRepository",
        "AI_VISIBILITY_DEMO_DATABASE_URL",
    ],
    "tests/services/test_cors.py": [
        "http://localhost:5173",
        "access-control-allow-origin",
    ],
    "tests/services/test_demo_e2e.py": [
        "seed_brandlight_demo",
        "run_brandlight_demo_smoke",
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
