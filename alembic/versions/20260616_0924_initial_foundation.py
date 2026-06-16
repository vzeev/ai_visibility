"""Initial AI visibility foundation schema."""

from __future__ import annotations

from alembic import op

revision = "20260616_0924"
down_revision = None
branch_labels = None
depends_on = None

CONTRACT_SQL = """
CREATE SCHEMA IF NOT EXISTS config;
CREATE SCHEMA IF NOT EXISTS visibility;
CREATE SCHEMA IF NOT EXISTS insights;

CREATE TABLE config.brands (
    id uuid PRIMARY KEY,
    name text NOT NULL,
    website_url text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (name)
);

CREATE TABLE config.brand_aliases (
    id uuid PRIMARY KEY,
    brand_id uuid NOT NULL REFERENCES config.brands(id),
    alias text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (brand_id, alias)
);

CREATE TABLE config.competitors (
    id uuid PRIMARY KEY,
    brand_id uuid NOT NULL REFERENCES config.brands(id),
    name text NOT NULL,
    website_url text,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (brand_id, name)
);

CREATE TABLE config.products (
    id uuid PRIMARY KEY,
    brand_id uuid NOT NULL REFERENCES config.brands(id),
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (brand_id, name)
);

CREATE TABLE config.prompt_sets (
    id uuid PRIMARY KEY,
    brand_id uuid NOT NULL REFERENCES config.brands(id),
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (brand_id, name)
);

CREATE TABLE config.prompts (
    id uuid PRIMARY KEY,
    prompt_set_id uuid NOT NULL REFERENCES config.prompt_sets(id),
    name text NOT NULL,
    intent text NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (prompt_set_id, name)
);

CREATE TABLE config.prompt_versions (
    id uuid PRIMARY KEY,
    prompt_id uuid NOT NULL REFERENCES config.prompts(id),
    version integer NOT NULL,
    prompt_text text NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (prompt_id, version)
);

CREATE TABLE config.providers (
    id uuid PRIMARY KEY,
    provider_key text NOT NULL UNIQUE,
    display_name text NOT NULL,
    provider_kind text NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE config.provider_credentials (
    id uuid PRIMARY KEY,
    provider_id uuid NOT NULL REFERENCES config.providers(id),
    label text NOT NULL,
    status text NOT NULL,
    secret_ref text,
    redacted_fingerprint text NOT NULL,
    last_tested_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (provider_id, label)
);

CREATE TABLE config.rate_limit_policies (
    id uuid PRIMARY KEY,
    provider_id uuid NOT NULL REFERENCES config.providers(id),
    model_id text,
    max_concurrent_requests integer NOT NULL,
    requests_per_minute integer NOT NULL,
    tokens_per_minute integer,
    min_delay_ms integer NOT NULL DEFAULT 0,
    max_retries integer NOT NULL DEFAULT 3,
    backoff_base_ms integer NOT NULL DEFAULT 1000,
    backoff_max_ms integer NOT NULL DEFAULT 60000,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (provider_id, model_id)
);

CREATE TABLE config.model_registry (
    id uuid PRIMARY KEY,
    provider_id uuid NOT NULL REFERENCES config.providers(id),
    model_id text NOT NULL,
    display_name text NOT NULL,
    owned_by text,
    is_available boolean NOT NULL DEFAULT true,
    enabled_for_visibility boolean NOT NULL DEFAULT false,
    rate_limit_policy_id uuid REFERENCES config.rate_limit_policies(id),
    capability_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    discovered_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (provider_id, model_id)
);

CREATE TABLE config.schedules (
    id uuid PRIMARY KEY,
    prompt_set_id uuid NOT NULL REFERENCES config.prompt_sets(id),
    name text NOT NULL,
    frequency_cron text NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE visibility.run_batches (
    id uuid PRIMARY KEY,
    brand_id uuid NOT NULL,
    prompt_set_id uuid NOT NULL,
    config_snapshot_json jsonb NOT NULL,
    status text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz,
    completed_at timestamptz
);

CREATE TABLE visibility.run_items (
    id uuid PRIMARY KEY,
    run_batch_id uuid NOT NULL REFERENCES visibility.run_batches(id),
    prompt_version_id uuid NOT NULL,
    provider_id uuid NOT NULL,
    model_registry_id uuid NOT NULL,
    sample_index integer NOT NULL DEFAULT 0,
    idempotency_key text NOT NULL UNIQUE,
    status text NOT NULL,
    attempt_count integer NOT NULL DEFAULT 0,
    max_attempts integer NOT NULL DEFAULT 3,
    lease_expires_at timestamptz,
    next_attempt_at timestamptz NOT NULL DEFAULT now(),
    last_error text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE visibility.raw_responses (
    id uuid PRIMARY KEY,
    run_item_id uuid NOT NULL REFERENCES visibility.run_items(id),
    idempotency_key text NOT NULL UNIQUE,
    provider_id uuid NOT NULL,
    model_id text NOT NULL,
    provider_response_id text,
    prompt_text text NOT NULL,
    output_text text NOT NULL,
    raw_request_json jsonb NOT NULL,
    raw_response_json jsonb NOT NULL,
    usage_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    latency_ms integer NOT NULL,
    status text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE visibility.model_errors (
    id uuid PRIMARY KEY,
    run_item_id uuid NOT NULL REFERENCES visibility.run_items(id),
    provider_id uuid NOT NULL,
    model_id text NOT NULL,
    error_type text NOT NULL,
    error_message text NOT NULL,
    retryable boolean NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE insights.extraction_runs (
    id uuid PRIMARY KEY,
    raw_response_id uuid NOT NULL REFERENCES visibility.raw_responses(id),
    extraction_version text NOT NULL,
    status text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz,
    UNIQUE (raw_response_id, extraction_version)
);

CREATE TABLE insights.extracted_mentions (
    id uuid PRIMARY KEY,
    extraction_run_id uuid NOT NULL REFERENCES insights.extraction_runs(id),
    entity_type text NOT NULL,
    entity_name text NOT NULL,
    mention_text text NOT NULL,
    sentiment_label text NOT NULL,
    confidence numeric(5, 4) NOT NULL,
    evidence_json jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE insights.extracted_citations (
    id uuid PRIMARY KEY,
    extraction_run_id uuid NOT NULL REFERENCES insights.extraction_runs(id),
    url text NOT NULL,
    domain text NOT NULL,
    title text,
    evidence_json jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE insights.visibility_summaries (
    id uuid PRIMARY KEY,
    brand_id uuid NOT NULL,
    run_batch_id uuid NOT NULL REFERENCES visibility.run_batches(id),
    extraction_version text NOT NULL,
    summary_json jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (brand_id, run_batch_id, extraction_version)
);

CREATE INDEX idx_visibility_raw_responses_created_at ON visibility.raw_responses(created_at);
CREATE INDEX idx_visibility_raw_responses_model ON visibility.raw_responses(model_id);
CREATE INDEX idx_visibility_run_items_status ON visibility.run_items(status, next_attempt_at);
"""


def upgrade() -> None:
    for statement in CONTRACT_SQL.split(";\n"):
        normalized = statement.strip()
        if normalized:
            op.execute(normalized)


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS insights CASCADE")
    op.execute("DROP SCHEMA IF EXISTS visibility CASCADE")
    op.execute("DROP SCHEMA IF EXISTS config CASCADE")
