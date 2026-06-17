const brandId = "brand-1";
const promptSetId = "prompt-set-1";
const promptId = "prompt-1";
const providerId = "provider-1";
const runBatchId = "run-batch-1";
const rawResponseId = "raw-response-1";
const runItemId = "run-item-1";
const extractionRunId = "extraction-run-1";
const summaryId = "summary-1";

const brands = [{ id: brandId, name: "Brandlight", website_url: "https://www.brandlight.ai/" }];
const promptSets = [
  {
    id: promptSetId,
    brand_id: brandId,
    name: "Brandlight interview demo prompts",
    description: "Demo prompts",
    is_active: true
  }
];
const prompts = [
  {
    id: promptId,
    prompt_set_id: promptSetId,
    name: "Category recommendation",
    intent: "commercial",
    active_version: {
      id: "prompt-version-1",
      prompt_id: promptId,
      version: 1,
      prompt_text: "Which AI visibility platforms should a B2B marketing leader evaluate?"
    }
  },
  {
    id: "prompt-2",
    prompt_set_id: promptSetId,
    name: "Competitor comparison",
    intent: "competitive",
    active_version: {
      id: "prompt-version-2",
      prompt_id: "prompt-2",
      version: 1,
      prompt_text: "Compare Brandlight with Profound and Peec AI."
    }
  }
];
const providers = [
  {
    id: providerId,
    provider_key: "openai",
    display_name: "OpenAI",
    provider_kind: "llm",
    is_active: true
  }
];
const credentials = [
  {
    id: "credential-1",
    provider_id: providerId,
    label: "local demo token",
    status: "active",
    redacted_fingerprint: "sk-...demo",
    last_tested_at: null
  }
];
const rateLimits = [
  {
    id: "rate-limit-1",
    provider_id: providerId,
    model_id: "gpt-demo",
    max_concurrent_requests: 2,
    requests_per_minute: 60,
    tokens_per_minute: null,
    min_delay_ms: 0,
    max_retries: 3,
    backoff_base_ms: 1000,
    backoff_max_ms: 60000
  }
];
const models = [
  {
    id: "model-1",
    provider_id: providerId,
    model_id: "gpt-demo",
    display_name: "GPT Demo",
    owned_by: "openai",
    is_available: true,
    enabled_for_visibility: true,
    rate_limit_policy_id: "rate-limit-1",
    capability_json: { responses: true }
  },
  {
    id: "model-2",
    provider_id: providerId,
    model_id: "gpt-disabled",
    display_name: "GPT Disabled",
    owned_by: "openai",
    is_available: true,
    enabled_for_visibility: false,
    rate_limit_policy_id: null,
    capability_json: { responses: true }
  }
];
const queue = { pending: 1, running: 0, succeeded: 2, failed: 0, throttled: 1 };
const runs = [
  {
    id: runBatchId,
    brand_id: brandId,
    prompt_set_id: promptSetId,
    status: "succeeded",
    created_at: "2026-06-17T09:30:00.000Z",
    item_count: 2
  }
];
const rawPage = {
  items: [
    {
      id: rawResponseId,
      run_item_id: runItemId,
      idempotency_key: "run-batch-1:prompt-version-1:gpt-demo:0",
      provider_id: providerId,
      model_id: "gpt-demo",
      provider_response_id: "resp-demo",
      prompt_text: prompts[0].active_version.prompt_text,
      output_text:
        "Brandlight is a strong AI visibility platform. Profound is a competitor. Source: https://www.brandlight.ai/.",
      raw_request_json: { model: "gpt-demo", input: prompts[0].active_version.prompt_text },
      raw_response_json: { id: "resp-demo", output_text: "Brandlight is visible." },
      usage_json: { input_tokens: 18, output_tokens: 42 },
      latency_ms: 321,
      status: "succeeded"
    }
  ],
  total: 1,
  query: null,
  limit: 8,
  offset: 0
};
const summaries = [
  {
    id: summaryId,
    brand_id: brandId,
    run_batch_id: runBatchId,
    extraction_version: "deterministic-v1",
    summary_json: {
      raw_response_count: 1,
      raw_response_ids: [rawResponseId],
      extraction_run_ids: [extractionRunId],
      brand_mentions: 1,
      competitor_mentions: 1,
      citation_domains: { "brandlight.ai": 1 },
      entity_mentions: { brand: { Brandlight: 1 }, competitor: { Profound: 1 } },
      models: ["gpt-demo"]
    }
  }
];
const extractionRun = {
  id: extractionRunId,
  raw_response_id: rawResponseId,
  extraction_version: "deterministic-v1",
  status: "completed",
  completed_at: "2026-06-17T08:00:00Z",
  mentions: [
    {
      id: "mention-1",
      extraction_run_id: extractionRunId,
      entity_type: "brand",
      entity_name: "Brandlight",
      mention_text: "Brandlight",
      sentiment_label: "positive",
      confidence: "1.0",
      evidence_json: { snippet: "Brandlight is a strong AI visibility platform." }
    }
  ],
  citations: [
    {
      id: "citation-1",
      extraction_run_id: extractionRunId,
      url: "https://www.brandlight.ai/",
      domain: "brandlight.ai",
      title: null,
      evidence_json: { snippet: "Source: https://www.brandlight.ai/." }
    }
  ]
};

describe("Brandlight interview demo", () => {
  beforeEach(() => {
    cy.intercept("GET", "**/api/v1/brands", brands).as("brands");
    cy.intercept("GET", "**/api/v1/prompt-sets", promptSets).as("promptSets");
    cy.intercept("GET", "**/api/v1/prompts", prompts).as("prompts");
    cy.intercept("GET", "**/api/v1/providers", providers).as("providers");
    cy.intercept("GET", "**/api/v1/provider-credentials", credentials).as("credentials");
    cy.intercept("GET", "**/api/v1/rate-limits", rateLimits).as("rateLimits");
    cy.intercept("GET", "**/api/v1/models", models).as("models");
    cy.intercept("GET", "**/api/v1/queue", queue).as("queue");
    cy.intercept("GET", "**/api/v1/runs", runs).as("runs");
    cy.intercept("GET", "**/api/v1/raw-responses?*", rawPage).as("rawResponses");
    cy.intercept("GET", "**/api/v1/summaries", summaries).as("summaries");
    cy.intercept("GET", `**/api/v1/extraction-runs/${extractionRunId}`, extractionRun).as(
      "extractionRun"
    );
    cy.intercept("POST", "**/api/v1/runs", runs[0]).as("createRun");
    cy.intercept("POST", "**/api/v1/providers/*/models/sync", {
      provider_id: providerId,
      provider_key: "openai",
      discovered_count: 2,
      created_count: 0,
      updated_count: 2,
      unavailable_count: 0,
      models
    }).as("syncModels");
    cy.intercept("PATCH", "**/api/v1/models/*/visibility", {
      ...models[1],
      enabled_for_visibility: true
    }).as("updateModelVisibility");
    cy.intercept("POST", `**/api/v1/extractions/run-batches/${runBatchId}`, {
      run_batch_id: runBatchId,
      extraction_version: "deterministic-v1",
      raw_response_count: 1,
      extraction_run_count: 1,
      summary: summaries[0]
    }).as("extractRun");
  });

  it("shows the main demo workflow from config to evidence-linked insights", () => {
    cy.visit("/");

    cy.get('[data-cy="overview-brand"]').contains("Brandlight");
    cy.get('[data-cy="overview-raw-evidence"]').contains("1");
    cy.get('[data-cy="overview-insights"]').contains("2");

    cy.get('[data-cy="tab-config"]').click();
    cy.get('[data-cy="config-active-setup"]').contains("https://www.brandlight.ai/");
    cy.get('[data-cy="config-authoring"]').contains("Prompts config");
    cy.get('[data-cy="config-authoring"]').contains("Demo prompt questions");
    cy.contains("Providers config");
    cy.get('[data-cy="prompt-version-text"]').should(
      "have.value",
      prompts[0].active_version.prompt_text
    );
    cy.get('[data-cy="sync-openai-models"]').click();
    cy.wait("@syncModels");
    cy.contains("Synced 2 models");
    cy.get('[data-cy="toggle-model-gpt-disabled"]').click();
    cy.wait("@updateModelVisibility");
    cy.contains("gpt-disabled enabled for visibility runs");

    cy.get('[data-cy="tab-queue"]').click();
    cy.get('[data-cy="queue-run-expansion"]').contains("2 prompts");
    cy.get('[data-cy="queue-run-expansion"]').contains("1 enabled models");
    cy.get('[data-cy="create-run"]').click();
    cy.wait("@createRun");
    cy.get('[data-cy="reload-run-batches"]').click();
    cy.get('[data-cy="run-batches"]').contains("succeeded");
    cy.get('[data-cy="run-batches"]').contains("Timestamp");

    cy.get('[data-cy="tab-visibility"]').click();
    cy.get('[data-cy="model-comparison"]').contains("gpt-demo");
    cy.get('[data-cy="raw-response-list"]').contains("Brandlight is a strong AI visibility platform");
    cy.get('[data-cy="raw-response-detail"]').contains("Idempotency key");
    cy.get('[data-cy="raw-response-detail"]').contains("run-batch-1:prompt-version-1:gpt-demo:0");

    cy.get('[data-cy="tab-insights"]').click();
    cy.get('[data-cy="insights-extraction-mode"]').contains("Deterministic extraction");
    cy.get('[data-cy="analyze-latest-run"]').click();
    cy.wait("@extractRun");
    cy.get('[data-cy="insights-summary-list"]').contains("deterministic-v1");
    cy.get('[data-cy="extraction-evidence"]').contains("Brandlight");
    cy.get('[data-cy="extraction-evidence"]').contains("brandlight.ai");
  });
});
