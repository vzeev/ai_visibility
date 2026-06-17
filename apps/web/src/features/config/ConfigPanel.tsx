import { type FormEvent, useState } from "react";

import { EmptyState, ErrorState, LoadingState } from "../../components/DataState";
import {
  configApi,
  services,
  type ModelRegistry,
  type Provider,
  type RateLimitPolicy
} from "../../lib/api";
import { useAsyncData } from "../../lib/useAsyncData";

type FormKey = "credential" | "prompt" | "version" | "rateLimit" | "modelSync";

type FormMessage = {
  form: FormKey;
  kind: "success" | "error";
  text: string;
};

const defaultCredentialForm = {
  providerId: "",
  label: "",
  token: ""
};

const defaultPromptForm = {
  promptSetId: "",
  name: "",
  intent: "brand_visibility",
  promptText: ""
};

const defaultVersionForm = {
  promptId: "",
  promptText: ""
};

const defaultRateLimitForm = {
  providerId: "",
  modelId: "",
  maxConcurrentRequests: "1",
  requestsPerMinute: "10",
  tokensPerMinute: "",
  minDelayMs: "0",
  maxRetries: "3",
  backoffBaseMs: "1000",
  backoffMaxMs: "60000"
};

export function ConfigPanel() {
  const state = useAsyncData(loadConfigData, []);
  const [credentialForm, setCredentialForm] = useState(defaultCredentialForm);
  const [promptForm, setPromptForm] = useState(defaultPromptForm);
  const [versionForm, setVersionForm] = useState(defaultVersionForm);
  const [rateLimitForm, setRateLimitForm] = useState(defaultRateLimitForm);
  const [saving, setSaving] = useState<FormKey | null>(null);
  const [formMessage, setFormMessage] = useState<FormMessage | null>(null);

  if (state.isLoading && !state.data) {
    return <LoadingState title="Loading configuration" />;
  }

  if (state.error) {
    return (
      <ErrorState
        title="Config service unavailable"
        description={`${state.error}. Expected ${services.configBaseUrl}.`}
        onAction={() => void state.reload()}
      />
    );
  }

  const data = state.data;
  if (!data) {
    return (
      <EmptyState
        title="No configuration loaded"
        description="Refresh after starting config-service."
        actionLabel="Refresh"
        onAction={() => void state.reload()}
      />
    );
  }

  const activeModels = data.models.filter((model) => model.enabled_for_visibility);
  const activePromptCount = data.prompts.length;
  const demoBrand = data.brands.find((brand) => brand.name === "Brandlight") ?? data.brands[0];
  const demoPromptSets = demoBrand
    ? data.promptSets.filter((set) => set.brand_id === demoBrand.id)
    : [];
  const selectedCredentialProviderId =
    credentialForm.providerId || data.providers[0]?.id || "";
  const selectedPromptSetId = promptForm.promptSetId || data.promptSets[0]?.id || "";
  const selectedPromptId = versionForm.promptId || data.prompts[0]?.id || "";
  const selectedRateLimitProviderId =
    rateLimitForm.providerId || data.providers[0]?.id || "";
  const selectedOpenAiProvider = data.providers.find(
    (provider) => provider.provider_key === "openai"
  );

  async function submitCredential(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const label = credentialForm.label.trim();
    const token = credentialForm.token.trim();
    if (!selectedCredentialProviderId || !label || !token) {
      setFormMessage({
        form: "credential",
        kind: "error",
        text: "Provider, label, and token are required."
      });
      return;
    }

    setSaving("credential");
    setFormMessage(null);
    try {
      await configApi.createCredential({
        provider_id: selectedCredentialProviderId,
        label,
        token
      });
      setCredentialForm({ providerId: selectedCredentialProviderId, label: "", token: "" });
      setFormMessage({
        form: "credential",
        kind: "success",
        text: "Credential saved. Token input cleared."
      });
      await state.reload();
    } catch (error) {
      setFormMessage({ form: "credential", kind: "error", text: errorText(error) });
    } finally {
      setSaving(null);
      setCredentialForm((current) => ({ ...current, token: "" }));
    }
  }

  async function submitPrompt(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const name = promptForm.name.trim();
    const intent = promptForm.intent.trim();
    const promptText = promptForm.promptText.trim();
    if (!selectedPromptSetId || !name || !intent || !promptText) {
      setFormMessage({
        form: "prompt",
        kind: "error",
        text: "Prompt set, name, intent, and prompt text are required."
      });
      return;
    }

    setSaving("prompt");
    setFormMessage(null);
    try {
      await configApi.createPrompt({
        prompt_set_id: selectedPromptSetId,
        name,
        intent,
        prompt_text: promptText
      });
      setPromptForm({
        promptSetId: selectedPromptSetId,
        name: "",
        intent: promptForm.intent,
        promptText: ""
      });
      setFormMessage({ form: "prompt", kind: "success", text: "Prompt created." });
      await state.reload();
    } catch (error) {
      setFormMessage({ form: "prompt", kind: "error", text: errorText(error) });
    } finally {
      setSaving(null);
    }
  }

  async function submitPromptVersion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const promptText = versionForm.promptText.trim();
    if (!selectedPromptId || !promptText) {
      setFormMessage({
        form: "version",
        kind: "error",
        text: "Prompt and new prompt text are required."
      });
      return;
    }

    setSaving("version");
    setFormMessage(null);
    try {
      await configApi.createPromptVersion(selectedPromptId, { prompt_text: promptText });
      setVersionForm({ promptId: selectedPromptId, promptText: "" });
      setFormMessage({ form: "version", kind: "success", text: "Prompt version activated." });
      await state.reload();
    } catch (error) {
      setFormMessage({ form: "version", kind: "error", text: errorText(error) });
    } finally {
      setSaving(null);
    }
  }

  async function submitRateLimit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedRateLimitProviderId) {
      setFormMessage({
        form: "rateLimit",
        kind: "error",
        text: "Provider is required."
      });
      return;
    }

    setSaving("rateLimit");
    setFormMessage(null);
    try {
      await configApi.createRateLimit({
        provider_id: selectedRateLimitProviderId,
        model_id: cleanOptionalText(rateLimitForm.modelId),
        max_concurrent_requests: positiveNumber(rateLimitForm.maxConcurrentRequests),
        requests_per_minute: positiveNumber(rateLimitForm.requestsPerMinute),
        tokens_per_minute: optionalPositiveNumber(rateLimitForm.tokensPerMinute),
        min_delay_ms: nonNegativeNumber(rateLimitForm.minDelayMs),
        max_retries: nonNegativeNumber(rateLimitForm.maxRetries),
        backoff_base_ms: nonNegativeNumber(rateLimitForm.backoffBaseMs),
        backoff_max_ms: nonNegativeNumber(rateLimitForm.backoffMaxMs)
      });
      setRateLimitForm({
        ...defaultRateLimitForm,
        providerId: selectedRateLimitProviderId
      });
      setFormMessage({ form: "rateLimit", kind: "success", text: "Rate limit created." });
      await state.reload();
    } catch (error) {
      setFormMessage({ form: "rateLimit", kind: "error", text: errorText(error) });
    } finally {
      setSaving(null);
    }
  }

  async function syncOpenAiModels() {
    if (!selectedOpenAiProvider) {
      setFormMessage({
        form: "modelSync",
        kind: "error",
        text: "OpenAI provider is not configured."
      });
      return;
    }

    setSaving("modelSync");
    setFormMessage(null);
    try {
      const result = await configApi.syncModels(selectedOpenAiProvider.id);
      setFormMessage({
        form: "modelSync",
        kind: "success",
        text: `Synced ${result.discovered_count} models. Created ${result.created_count}, updated ${result.updated_count}, unavailable ${result.unavailable_count}.`
      });
      await state.reload();
    } catch (error) {
      setFormMessage({ form: "modelSync", kind: "error", text: errorText(error) });
    } finally {
      setSaving(null);
    }
  }

  return (
    <section className="content-grid config-grid">
      <div className="metric-card">
        <span>Brands</span>
        <strong>{data.brands.length}</strong>
      </div>
      <div className="metric-card">
        <span>Prompt versions</span>
        <strong>{activePromptCount}</strong>
      </div>
      <div className="metric-card">
        <span>Enabled models</span>
        <strong>{activeModels.length}</strong>
      </div>
      <div className="metric-card">
        <span>Rate policies</span>
        <strong>{data.rateLimits.length}</strong>
      </div>

      {demoBrand ? (
        <div className="panel span-3 demo-focus" data-cy="config-active-setup">
          <div>
            <p className="eyebrow">Active setup</p>
            <h2>{demoBrand.name}</h2>
            <p className="muted">{demoBrand.website_url ?? "No website configured"}</p>
          </div>
          <div className="readiness-strip" aria-label="Configuration readiness">
            <ReadinessPill
              label="Prompt sets"
              value={demoPromptSets.length}
              ready={demoPromptSets.length > 0}
            />
            <ReadinessPill label="Prompts" value={data.prompts.length} ready={data.prompts.length > 0} />
            <ReadinessPill label="Models" value={activeModels.length} ready={activeModels.length > 0} />
            <ReadinessPill
              label="Credentials"
              value={data.credentials.length}
              ready={data.credentials.length > 0}
            />
          </div>
        </div>
      ) : null}

      <div className="panel span-3 authoring-panel" data-cy="config-authoring">
        <div className="panel-header toolbar-header">
          <div>
            <p className="eyebrow">Config authoring</p>
            <h2>Prompts, credentials, and rate limits</h2>
          </div>
          <button type="button" onClick={() => void state.reload()}>
            Refresh
          </button>
        </div>

        <div className="authoring-grid">
          <form className="authoring-section" onSubmit={(event) => void submitCredential(event)}>
            <div>
              <h3>Provider credential</h3>
              <p className="muted compact-muted">Token input is write-only. Readback stays redacted.</p>
            </div>
            <label>
              Provider
              <select
                disabled={data.providers.length === 0 || saving === "credential"}
                value={selectedCredentialProviderId}
                onChange={(event) =>
                  setCredentialForm({ ...credentialForm, providerId: event.target.value })
                }
              >
                {data.providers.length === 0 ? <option value="">No providers</option> : null}
                {data.providers.map((provider) => (
                  <option key={provider.id} value={provider.id}>
                    {provider.display_name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Label
              <input
                value={credentialForm.label}
                onChange={(event) =>
                  setCredentialForm({ ...credentialForm, label: event.target.value })
                }
                placeholder="OpenAI interview demo token"
              />
            </label>
            <label>
              Token
              <input
                autoComplete="off"
                type="password"
                value={credentialForm.token}
                onChange={(event) =>
                  setCredentialForm({ ...credentialForm, token: event.target.value })
                }
                placeholder="sk-..."
              />
            </label>
            <FormMessageView message={formMessage} form="credential" />
            <button type="submit" disabled={saving === "credential" || data.providers.length === 0}>
              {saving === "credential" ? "Saving" : "Save credential"}
            </button>
          </form>

          <form className="authoring-section" onSubmit={(event) => void submitPrompt(event)}>
            <div>
              <h3>New prompt</h3>
              <p className="muted compact-muted">Creates an active version 1 under a prompt set.</p>
            </div>
            <label>
              Prompt set
              <select
                disabled={data.promptSets.length === 0 || saving === "prompt"}
                value={selectedPromptSetId}
                onChange={(event) =>
                  setPromptForm({ ...promptForm, promptSetId: event.target.value })
                }
              >
                {data.promptSets.length === 0 ? <option value="">No prompt sets</option> : null}
                {data.promptSets.map((promptSet) => (
                  <option key={promptSet.id} value={promptSet.id}>
                    {promptSet.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Name
              <input
                value={promptForm.name}
                onChange={(event) => setPromptForm({ ...promptForm, name: event.target.value })}
                placeholder="Brand comparison"
              />
            </label>
            <label>
              Intent
              <input
                value={promptForm.intent}
                onChange={(event) => setPromptForm({ ...promptForm, intent: event.target.value })}
                placeholder="brand_visibility"
              />
            </label>
            <label>
              Prompt text
              <textarea
                value={promptForm.promptText}
                onChange={(event) =>
                  setPromptForm({ ...promptForm, promptText: event.target.value })
                }
                placeholder="Ask the model how buyers should compare Brandlight..."
              />
            </label>
            <FormMessageView message={formMessage} form="prompt" />
            <button type="submit" disabled={saving === "prompt" || data.promptSets.length === 0}>
              {saving === "prompt" ? "Creating" : "Create prompt"}
            </button>
          </form>

          <form className="authoring-section" onSubmit={(event) => void submitPromptVersion(event)}>
            <div>
              <h3>Prompt version</h3>
              <p className="muted compact-muted">Adds a new active version without deleting history.</p>
            </div>
            <label>
              Prompt
              <select
                disabled={data.prompts.length === 0 || saving === "version"}
                value={selectedPromptId}
                onChange={(event) =>
                  setVersionForm({ ...versionForm, promptId: event.target.value })
                }
              >
                {data.prompts.length === 0 ? <option value="">No prompts</option> : null}
                {data.prompts.map((prompt) => (
                  <option key={prompt.id} value={prompt.id}>
                    {prompt.name} v{prompt.active_version.version}
                  </option>
                ))}
              </select>
            </label>
            <label>
              New prompt text
              <textarea
                value={versionForm.promptText}
                onChange={(event) =>
                  setVersionForm({ ...versionForm, promptText: event.target.value })
                }
                placeholder="Updated question wording..."
              />
            </label>
            <FormMessageView message={formMessage} form="version" />
            <button type="submit" disabled={saving === "version" || data.prompts.length === 0}>
              {saving === "version" ? "Activating" : "Activate new version"}
            </button>
          </form>

          <form className="authoring-section" onSubmit={(event) => void submitRateLimit(event)}>
            <div>
              <h3>Rate-limit policy</h3>
              <p className="muted compact-muted">Leave model blank for provider default limits.</p>
            </div>
            <label>
              Provider
              <select
                disabled={data.providers.length === 0 || saving === "rateLimit"}
                value={selectedRateLimitProviderId}
                onChange={(event) =>
                  setRateLimitForm({ ...rateLimitForm, providerId: event.target.value })
                }
              >
                {data.providers.length === 0 ? <option value="">No providers</option> : null}
                {data.providers.map((provider) => (
                  <option key={provider.id} value={provider.id}>
                    {provider.display_name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Model id
              <input
                list="config-model-ids"
                value={rateLimitForm.modelId}
                onChange={(event) =>
                  setRateLimitForm({ ...rateLimitForm, modelId: event.target.value })
                }
                placeholder="optional, for example gpt-5-main"
              />
            </label>
            <datalist id="config-model-ids">
              {data.models.map((model) => (
                <option key={model.id} value={model.model_id} />
              ))}
            </datalist>
            <div className="number-grid">
              <NumberField
                label="Concurrency"
                min={1}
                value={rateLimitForm.maxConcurrentRequests}
                onChange={(value) =>
                  setRateLimitForm({ ...rateLimitForm, maxConcurrentRequests: value })
                }
              />
              <NumberField
                label="Requests/min"
                min={1}
                value={rateLimitForm.requestsPerMinute}
                onChange={(value) =>
                  setRateLimitForm({ ...rateLimitForm, requestsPerMinute: value })
                }
              />
              <NumberField
                label="Tokens/min"
                min={1}
                value={rateLimitForm.tokensPerMinute}
                onChange={(value) =>
                  setRateLimitForm({ ...rateLimitForm, tokensPerMinute: value })
                }
              />
              <NumberField
                label="Min delay ms"
                min={0}
                value={rateLimitForm.minDelayMs}
                onChange={(value) => setRateLimitForm({ ...rateLimitForm, minDelayMs: value })}
              />
              <NumberField
                label="Max retries"
                min={0}
                value={rateLimitForm.maxRetries}
                onChange={(value) => setRateLimitForm({ ...rateLimitForm, maxRetries: value })}
              />
              <NumberField
                label="Backoff base"
                min={0}
                value={rateLimitForm.backoffBaseMs}
                onChange={(value) => setRateLimitForm({ ...rateLimitForm, backoffBaseMs: value })}
              />
              <NumberField
                label="Backoff max"
                min={0}
                value={rateLimitForm.backoffMaxMs}
                onChange={(value) => setRateLimitForm({ ...rateLimitForm, backoffMaxMs: value })}
              />
            </div>
            <FormMessageView message={formMessage} form="rateLimit" />
            <button type="submit" disabled={saving === "rateLimit" || data.providers.length === 0}>
              {saving === "rateLimit" ? "Creating" : "Create rate limit"}
            </button>
          </form>
        </div>
      </div>

      <div className="panel span-2">
        <div className="panel-header">
          <h2>Brands and prompt sets</h2>
          <button type="button" onClick={() => void state.reload()}>
            Refresh
          </button>
        </div>
        {data.brands.length === 0 ? (
          <EmptyState title="No brands" description="Create brands through config-service API." />
        ) : (
          <div className="record-list">
            {data.brands.map((brand) => {
              const promptSets = data.promptSets.filter((set) => set.brand_id === brand.id);
              return (
                <article className="record-row" key={brand.id}>
                  <div>
                    <span className="badge neutral">{promptSets.length} prompt sets</span>
                    <h3>{brand.name}</h3>
                    <p>{brand.website_url ?? "No website configured"}</p>
                  </div>
                  <div className="stacked-meta">
                    {promptSets.slice(0, 3).map((set) => (
                      <span key={set.id}>{set.name}</span>
                    ))}
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Provider credentials</h2>
        </div>
        {data.credentials.length === 0 ? (
          <EmptyState
            title="No credentials"
            description="Tokens are write-only and only redacted metadata is shown."
          />
        ) : (
          <div className="record-list">
            {data.credentials.map((credential) => (
              <div className="compact-row" key={credential.id}>
                <div>
                  <strong>{credential.label}</strong>
                  <span>{providerName(data.providers, credential.provider_id)}</span>
                  <span className="mono-cell">{credential.redacted_fingerprint}</span>
                </div>
                <span className="badge success">{credential.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="panel span-2">
        <div className="panel-header">
          <h2>Prompts</h2>
        </div>
        {data.prompts.length === 0 ? (
          <EmptyState title="No prompts" description="Prompt versions will appear here." />
        ) : (
          <div className="prompt-list">
            {data.prompts.map((prompt) => (
              <div className="prompt-row" key={prompt.id}>
                <div>
                  <strong>{prompt.name}</strong>
                  <p>{prompt.active_version.prompt_text}</p>
                </div>
                <span className="badge neutral">v{prompt.active_version.version}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Model limits</h2>
          <button
            type="button"
            data-cy="sync-openai-models"
            disabled={!selectedOpenAiProvider || saving === "modelSync"}
            onClick={() => void syncOpenAiModels()}
          >
            {saving === "modelSync" ? "Syncing" : "Sync OpenAI models"}
          </button>
        </div>
        <FormMessageView message={formMessage} form="modelSync" />
        <div className="model-list">
          {data.models.map((model) => (
            <div className="model-row" key={model.id}>
              <div>
                <strong>{model.model_id}</strong>
                <span>{providerName(data.providers, model.provider_id)}</span>
              </div>
              <ModelBadge model={model} />
            </div>
          ))}
          <div className="subsection-divider" />
          {data.rateLimits.map((policy) => (
            <RateLimitRow
              key={policy.id ?? `${policy.provider_id}:${policy.model_id ?? "default"}`}
              policy={policy}
              providers={data.providers}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

function ReadinessPill({ label, ready, value }: { label: string; ready: boolean; value: number }) {
  return (
    <span className={ready ? "readiness-pill ready" : "readiness-pill"}>
      {label}
      <strong>{value}</strong>
    </span>
  );
}

function FormMessageView({ form, message }: { form: FormKey; message: FormMessage | null }) {
  if (!message || message.form !== form) {
    return null;
  }
  return (
    <p className={message.kind === "success" ? "inline-success" : "inline-error"}>
      {message.text}
    </p>
  );
}

function NumberField({
  label,
  min,
  onChange,
  value
}: {
  label: string;
  min: number;
  onChange: (value: string) => void;
  value: string;
}) {
  return (
    <label>
      {label}
      <input
        min={min}
        type="number"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

async function loadConfigData() {
  const [brands, promptSets, prompts, providers, credentials, rateLimits, models] =
    await Promise.all([
      configApi.brands(),
      configApi.promptSets(),
      configApi.prompts(),
      configApi.providers(),
      configApi.credentials(),
      configApi.rateLimits(),
      configApi.models()
    ]);
  return { brands, promptSets, prompts, providers, credentials, rateLimits, models };
}

function providerName(providers: Provider[], providerId: string): string {
  return providers.find((provider) => provider.id === providerId)?.display_name ?? "Unknown";
}

function ModelBadge({ model }: { model: ModelRegistry }) {
  if (!model.is_available) {
    return <span className="badge throttled">unavailable</span>;
  }
  return (
    <span className={model.enabled_for_visibility ? "badge success" : "badge neutral"}>
      {model.enabled_for_visibility ? "enabled" : "disabled"}
    </span>
  );
}

function RateLimitRow({
  policy,
  providers
}: {
  policy: RateLimitPolicy;
  providers: Provider[];
}) {
  return (
    <div className="model-row">
      <div>
        <strong>{policy.model_id ?? "Provider default"}</strong>
        <span>{providerName(providers, policy.provider_id)}</span>
      </div>
      <span className="badge neutral">
        {policy.requests_per_minute}/min, {policy.max_concurrent_requests} concurrent
      </span>
    </div>
  );
}

function cleanOptionalText(value: string): string | null {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function positiveNumber(value: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 1) {
    throw new Error("Positive numeric fields must be at least 1.");
  }
  return Math.trunc(parsed);
}

function optionalPositiveNumber(value: string): number | null {
  if (!value.trim()) {
    return null;
  }
  return positiveNumber(value);
}

function nonNegativeNumber(value: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 0) {
    throw new Error("Non-negative numeric fields must be 0 or greater.");
  }
  return Math.trunc(parsed);
}

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : "Request failed";
}
