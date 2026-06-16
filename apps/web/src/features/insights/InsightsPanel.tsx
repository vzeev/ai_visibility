import { useMemo, useState } from "react";
import { EmptyState, ErrorState, LoadingState } from "../../components/DataState";
import { insightsApi, services, type ExtractionRun, type VisibilitySummary } from "../../lib/api";
import type { AsyncState } from "../../lib/useAsyncData";
import { useAsyncData } from "../../lib/useAsyncData";

export function InsightsPanel() {
  const summariesState = useAsyncData(() => insightsApi.summaries(), []);
  const [selectedSummaryId, setSelectedSummaryId] = useState<string | null>(null);

  const selectedSummary = useMemo(() => {
    return (
      summariesState.data?.find((summary) => summary.id === selectedSummaryId) ??
      summariesState.data?.[0] ??
      null
    );
  }, [selectedSummaryId, summariesState.data]);

  const extractionRunId = firstString(summaryArray(selectedSummary, "extraction_run_ids"));
  const extractionState = useAsyncData(
    () => (extractionRunId ? insightsApi.extractionRun(extractionRunId) : Promise.resolve(null)),
    [extractionRunId]
  );

  if (summariesState.isLoading && !summariesState.data) {
    return <LoadingState title="Loading insights" />;
  }

  if (summariesState.error) {
    return (
      <ErrorState
        title="Insights service unavailable"
        description={`${summariesState.error}. Expected ${services.insightsBaseUrl}.`}
        onAction={() => void summariesState.reload()}
      />
    );
  }

  const summaries = summariesState.data ?? [];
  if (summaries.length === 0) {
    return (
      <EmptyState
        title="No insights yet"
        description="Run deterministic extraction from insights-service after raw responses exist."
        actionLabel="Refresh"
        onAction={() => void summariesState.reload()}
      />
    );
  }

  const summaryJson = selectedSummary?.summary_json ?? {};

  return (
    <section className="content-grid">
      <Metric label="Brand mentions" value={numberValue(summaryJson.brand_mentions)} />
      <Metric label="Competitor mentions" value={numberValue(summaryJson.competitor_mentions)} />
      <Metric label="Citation domains" value={objectKeys(summaryJson.citation_domains).length} />

      <div className="panel span-2">
        <div className="panel-header">
          <div>
            <h2>Visibility summaries</h2>
            <p className="muted">{summaries.length} extraction summaries</p>
          </div>
          <button type="button" onClick={() => void summariesState.reload()}>
            Refresh
          </button>
        </div>
        <div className="summary-list">
          {summaries.map((summary) => (
            <button
              className={summary.id === selectedSummary?.id ? "summary-row active" : "summary-row"}
              key={summary.id}
              type="button"
              onClick={() => setSelectedSummaryId(summary.id)}
            >
              <div>
                <strong>{summary.extraction_version}</strong>
                <span className="mono-cell">{summary.run_batch_id.slice(0, 8)}</span>
              </div>
              <span className="badge neutral">
                {numberValue(summary.summary_json.raw_response_count)} raw
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Citation domains</h2>
        </div>
        <Breakdown value={summaryJson.citation_domains} />
      </div>

      <div className="panel span-2">
        <div className="panel-header">
          <h2>Entity mentions</h2>
        </div>
        <EntityMentions value={summaryJson.entity_mentions} />
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Evidence links</h2>
        </div>
        <div className="reference-list">
          {summaryArray(selectedSummary, "raw_response_ids")
            .slice(0, 6)
            .map((id) => (
              <span className="mono-cell reference-chip" key={id}>
                {id.slice(0, 8)}
              </span>
            ))}
        </div>
      </div>

      <ExtractionDetail state={extractionState} />
    </section>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ExtractionDetail({ state }: { state: AsyncState<ExtractionRun | null> }) {
  if (state.isLoading && !state.data) {
    return <LoadingState title="Loading extraction evidence" />;
  }
  if (state.error) {
    return (
      <ErrorState
        title="Extraction run unavailable"
        description={state.error}
        onAction={() => void state.reload()}
      />
    );
  }
  if (!state.data) {
    return (
      <div className="panel span-3">
        <EmptyState title="No extraction run selected" description="Select a summary with evidence." />
      </div>
    );
  }

  return (
    <div className="panel span-3">
      <div className="panel-header">
        <div>
          <h2>Extraction evidence</h2>
          <p className="muted">{state.data.extraction_version}</p>
        </div>
        <span className="badge success">{state.data.status}</span>
      </div>
      <div className="evidence-grid">
        <div>
          <h3>Mentions</h3>
          <div className="record-list">
            {state.data.mentions.map((mention) => (
              <article className="compact-row" key={mention.id}>
                <div>
                  <strong>{mention.entity_name}</strong>
                  <span>{evidenceSnippet(mention.evidence_json)}</span>
                </div>
                <span className={`badge ${mention.sentiment_label}`}>{mention.sentiment_label}</span>
              </article>
            ))}
          </div>
        </div>
        <div>
          <h3>Citations</h3>
          <div className="record-list">
            {state.data.citations.map((citation) => (
              <article className="compact-row" key={citation.id}>
                <div>
                  <strong>{citation.domain}</strong>
                  <span>{citation.url}</span>
                </div>
                <span className="badge neutral">url</span>
              </article>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function EntityMentions({ value }: { value: unknown }) {
  if (!isRecord(value)) {
    return <EmptyState title="No entity data" description="Summary has no entity mention map." />;
  }
  const groups = Object.entries(value).filter(([, group]) => isRecord(group));
  if (groups.length === 0) {
    return <EmptyState title="No entity mentions" description="Extraction found no mentions." />;
  }
  return (
    <div className="bar-stack">
      {groups.flatMap(([groupName, group]) =>
        Object.entries(group as Record<string, unknown>).map(([name, count]) => (
          <div className="bar-row" key={`${groupName}-${name}`}>
            <span>{name}</span>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{ width: `${Math.min(100, numberValue(count) * 20)}%` }}
              />
            </div>
            <strong>{numberValue(count)}</strong>
          </div>
        ))
      )}
    </div>
  );
}

function Breakdown({ value }: { value: unknown }) {
  if (!isRecord(value) || Object.keys(value).length === 0) {
    return <EmptyState title="No citations" description="No citation domains were extracted." />;
  }
  return (
    <div className="record-list">
      {Object.entries(value).map(([domain, count]) => (
        <div className="compact-row" key={domain}>
          <strong>{domain}</strong>
          <span className="badge neutral">{numberValue(count)}</span>
        </div>
      ))}
    </div>
  );
}

function summaryArray(summary: VisibilitySummary | null, key: string): string[] {
  const value = summary?.summary_json[key];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function firstString(values: string[]): string | null {
  return values.length > 0 ? values[0] : null;
}

function objectKeys(value: unknown): string[] {
  return isRecord(value) ? Object.keys(value) : [];
}

function numberValue(value: unknown): number {
  return typeof value === "number" ? value : 0;
}

function evidenceSnippet(value: Record<string, unknown>): string {
  return typeof value.snippet === "string" ? value.snippet : "No snippet";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
