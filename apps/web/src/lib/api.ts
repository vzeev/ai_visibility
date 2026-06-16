export type Brand = {
  id: string;
  name: string;
  website_url: string | null;
};

export type PromptSet = {
  id: string;
  brand_id: string;
  name: string;
  description: string;
  is_active: boolean;
};

export type Prompt = {
  id: string;
  prompt_set_id: string;
  name: string;
  intent: string;
  active_version: {
    id: string;
    prompt_id: string;
    version: number;
    prompt_text: string;
  };
};

export type Provider = {
  id: string;
  provider_key: string;
  display_name: string;
  provider_kind: string;
  is_active: boolean;
};

export type ProviderCredential = {
  id: string;
  provider_id: string;
  label: string;
  status: string;
  redacted_fingerprint: string;
  last_tested_at: string | null;
};

export type RateLimitPolicy = {
  id: string;
  provider_id: string;
  model_id: string | null;
  max_concurrent_requests: number;
  requests_per_minute: number;
  tokens_per_minute: number | null;
  min_delay_ms: number;
  max_retries: number;
};

export type ModelRegistry = {
  id: string;
  provider_id: string;
  model_id: string;
  display_name: string;
  owned_by: string | null;
  is_available: boolean;
  enabled_for_visibility: boolean;
  rate_limit_policy_id: string | null;
  capability_json: Record<string, unknown>;
};

export type RunBatch = {
  id: string;
  brand_id: string;
  prompt_set_id: string;
  status: string;
  item_count?: number | null;
};

export type QueueState = {
  pending: number;
  running: number;
  succeeded: number;
  failed: number;
  throttled: number;
};

export type RawResponseItem = {
  id: string;
  run_item_id: string;
  idempotency_key: string;
  provider_id: string;
  model_id: string;
  provider_response_id: string | null;
  prompt_text: string;
  output_text: string;
  raw_request_json: Record<string, unknown>;
  raw_response_json: Record<string, unknown>;
  usage_json: Record<string, unknown>;
  latency_ms: number;
  status: string;
};

export type RawResponsePage = {
  items: RawResponseItem[];
  total: number;
  query: string | null;
  limit: number;
  offset: number;
};

export type ExtractedMention = {
  id: string;
  extraction_run_id: string;
  entity_type: string;
  entity_name: string;
  mention_text: string;
  sentiment_label: string;
  confidence: string | number;
  evidence_json: Record<string, unknown>;
};

export type ExtractedCitation = {
  id: string;
  extraction_run_id: string;
  url: string;
  domain: string;
  title: string | null;
  evidence_json: Record<string, unknown>;
};

export type ExtractionRun = {
  id: string;
  raw_response_id: string;
  extraction_version: string;
  status: string;
  completed_at: string | null;
  mentions: ExtractedMention[];
  citations: ExtractedCitation[];
};

export type VisibilitySummary = {
  id: string;
  brand_id: string;
  run_batch_id: string;
  extraction_version: string;
  summary_json: Record<string, unknown>;
};

const configBaseUrl = serviceBaseUrl("VITE_CONFIG_SERVICE_URL", "http://localhost:8001");
const visibilityBaseUrl = serviceBaseUrl(
  "VITE_VISIBILITY_SERVICE_URL",
  "http://localhost:8002"
);
const insightsBaseUrl = serviceBaseUrl("VITE_INSIGHTS_SERVICE_URL", "http://localhost:8003");

export const services = {
  configBaseUrl,
  visibilityBaseUrl,
  insightsBaseUrl
};

export const configApi = {
  brands: () => getJson<Brand[]>(configBaseUrl, "/api/v1/brands"),
  promptSets: () => getJson<PromptSet[]>(configBaseUrl, "/api/v1/prompt-sets"),
  prompts: () => getJson<Prompt[]>(configBaseUrl, "/api/v1/prompts"),
  providers: () => getJson<Provider[]>(configBaseUrl, "/api/v1/providers"),
  credentials: () => getJson<ProviderCredential[]>(configBaseUrl, "/api/v1/provider-credentials"),
  rateLimits: () => getJson<RateLimitPolicy[]>(configBaseUrl, "/api/v1/rate-limits"),
  models: () => getJson<ModelRegistry[]>(configBaseUrl, "/api/v1/models")
};

export const visibilityApi = {
  queue: () => getJson<QueueState>(visibilityBaseUrl, "/api/v1/queue"),
  runs: () => getJson<RunBatch[]>(visibilityBaseUrl, "/api/v1/runs"),
  createRun: (payload: {
    brand_id: string;
    prompt_set_id: string;
    sample_count: number;
    max_attempts: number;
  }) => postJson<RunBatch>(visibilityBaseUrl, "/api/v1/runs", payload),
  rawResponses: (params: { q?: string; limit: number; offset: number }) => {
    const query = new URLSearchParams({
      limit: String(params.limit),
      offset: String(params.offset)
    });
    if (params.q?.trim()) {
      query.set("q", params.q.trim());
    }
    return getJson<RawResponsePage>(visibilityBaseUrl, `/api/v1/raw-responses?${query}`);
  }
};

export const insightsApi = {
  summaries: () => getJson<VisibilitySummary[]>(insightsBaseUrl, "/api/v1/summaries"),
  extractionRun: (id: string) =>
    getJson<ExtractionRun>(insightsBaseUrl, `/api/v1/extraction-runs/${id}`)
};

async function getJson<T>(baseUrl: string, path: string): Promise<T> {
  return requestJson<T>(baseUrl, path, { method: "GET" });
}

async function postJson<T>(baseUrl: string, path: string, payload: unknown): Promise<T> {
  return requestJson<T>(baseUrl, path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

async function requestJson<T>(baseUrl: string, path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${response.status} ${response.statusText}${detail ? `: ${detail}` : ""}`);
  }
  return (await response.json()) as T;
}

function serviceBaseUrl(envKey: string, fallback: string): string {
  const env = import.meta.env as Record<string, string | undefined>;
  return (env[envKey] ?? fallback).replace(/\/$/, "");
}
