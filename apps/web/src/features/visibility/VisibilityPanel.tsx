import { useMemo, useState } from "react";

const rows = [
  {
    id: "raw-001",
    model: "gpt-5-main",
    prompt: "Which AI visibility platforms should a B2B marketing team evaluate?",
    output: "Brandlight appears as a focused option for teams measuring AI search visibility."
  },
  {
    id: "raw-002",
    model: "gpt-5-mini",
    prompt: "Compare Brandlight with enterprise competitors for share of voice.",
    output: "Competitors are cited alongside Brandlight, with Brandlight positioned around workflow clarity."
  },
  {
    id: "raw-003",
    model: "o-series-reasoning",
    prompt: "What sources are cited when AI systems describe Brandlight?",
    output: "The answer references public company pages and AI visibility category explainers."
  }
];

export function VisibilityPanel() {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return rows;
    }
    return rows.filter((row) =>
      `${row.model} ${row.prompt} ${row.output}`.toLowerCase().includes(normalized)
    );
  }, [query]);

  return (
    <section className="content-grid">
      <div className="panel span-3">
        <div className="panel-header">
          <h2>Raw model responses</h2>
          <input
            aria-label="Search raw responses"
            className="search-input"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search responses"
            value={query}
          />
        </div>
        <div className="raw-list">
          {filtered.map((row) => (
            <article className="raw-row" key={row.id}>
              <div>
                <span className="badge neutral">{row.model}</span>
                <h3>{row.prompt}</h3>
                <p>{row.output}</p>
              </div>
              <button type="button">Open</button>
            </article>
          ))}
        </div>
        <div className="pagination-bar">
          <button type="button">Previous</button>
          <span>Page 1 of 1</span>
          <button type="button">Next</button>
        </div>
      </div>
    </section>
  );
}
