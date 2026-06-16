import { EmptyState, ErrorState, LoadingState } from "../../components/DataState";
import { configApi, services, type ModelRegistry, type Provider } from "../../lib/api";
import { useAsyncData } from "../../lib/useAsyncData";

export function ConfigPanel() {
  const state = useAsyncData(loadConfigData, []);

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
        <div className="panel span-3 demo-focus">
          <div>
            <p className="eyebrow">Active setup</p>
            <h2>{demoBrand.name}</h2>
            <p className="muted">{demoBrand.website_url ?? "No website configured"}</p>
          </div>
          <div className="readiness-strip" aria-label="Configuration readiness">
            <ReadinessPill label="Prompt sets" value={demoPromptSets.length} ready={demoPromptSets.length > 0} />
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
        </div>
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
