const mentions = [
  { label: "Brand mentions", value: "68", delta: "+12%" },
  { label: "Competitor mentions", value: "44", delta: "-3%" },
  { label: "Citation domains", value: "19", delta: "+5" }
];

const entities = [
  { name: "Brandlight", share: 68 },
  { name: "Profound", share: 52 },
  { name: "Scrunch AI", share: 47 },
  { name: "Peec AI", share: 34 }
];

export function InsightsPanel() {
  return (
    <section className="content-grid">
      {mentions.map((item) => (
        <div className="metric-card" key={item.label}>
          <span>{item.label}</span>
          <strong>{item.value}</strong>
          <em>{item.delta}</em>
        </div>
      ))}

      <div className="panel span-2">
        <div className="panel-header">
          <h2>Share of answer</h2>
          <button type="button">Export</button>
        </div>
        <div className="bar-stack">
          {entities.map((entity) => (
            <div className="bar-row" key={entity.name}>
              <span>{entity.name}</span>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${entity.share}%` }} />
              </div>
              <strong>{entity.share}%</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Extraction quality</h2>
          <button type="button">Review</button>
        </div>
        <div className="quality-ring" aria-label="Extraction confidence 92 percent">
          <strong>92%</strong>
          <span>confidence</span>
        </div>
      </div>
    </section>
  );
}
