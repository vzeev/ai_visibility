const models = [
  { provider: "OpenAI", model: "gpt-5-main", rpm: 40, enabled: true },
  { provider: "OpenAI", model: "gpt-5-mini", rpm: 90, enabled: true },
  { provider: "OpenAI", model: "o-series-reasoning", rpm: 12, enabled: false }
];

const prompts = [
  "Which AI visibility platforms should a B2B marketing team evaluate?",
  "Compare Brandlight with enterprise competitors for share of voice.",
  "What sources are cited when AI systems describe Brandlight?"
];

const modules = [
  "Visibility & Insights",
  "Technical Health",
  "Content",
  "Partnerships",
  "Agentic Commerce",
  "Ads"
];

export function ConfigPanel() {
  return (
    <section className="content-grid config-grid">
      <div className="panel span-2">
        <div className="panel-header">
          <h2>Brand setup</h2>
          <button type="button">Save</button>
        </div>
        <div className="form-grid">
          <label>
            Brand
            <input defaultValue="Brandlight" />
          </label>
          <label>
            Website
            <input defaultValue="https://brandlight.ai" />
          </label>
          <label>
            Competitors
            <textarea defaultValue={"Profound\nScrunch AI\nPeec AI"} />
          </label>
          <label>
            Products
            <textarea defaultValue={"AI search visibility\nEnterprise answer analytics"} />
          </label>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Provider token</h2>
          <button type="button">Test</button>
        </div>
        <label className="stacked-field">
          OpenAI API token
          <input placeholder="sk-..." type="password" />
        </label>
        <p className="muted">Stored as a write-only secret with redacted fingerprint metadata.</p>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Brandlight modules</h2>
          <button type="button">Select</button>
        </div>
        <div className="module-list">
          {modules.map((module) => (
            <span className="module-chip" key={module}>
              {module}
            </span>
          ))}
        </div>
      </div>

      <div className="panel span-2">
        <div className="panel-header">
          <h2>Prompt set</h2>
          <button type="button">Add prompt</button>
        </div>
        <div className="prompt-list">
          {prompts.map((prompt) => (
            <div className="prompt-row" key={prompt}>
              <span>{prompt}</span>
              <strong>v1</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Model limits</h2>
          <button type="button">Edit</button>
        </div>
        <div className="model-list">
          {models.map((item) => (
            <div className="model-row" key={item.model}>
              <div>
                <strong>{item.model}</strong>
                <span>{item.provider}</span>
              </div>
              <span className={item.enabled ? "badge success" : "badge neutral"}>{item.rpm} rpm</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
