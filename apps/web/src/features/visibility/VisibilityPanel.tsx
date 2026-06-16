import { useMemo, useState } from "react";
import { EmptyState, ErrorState, LoadingState } from "../../components/DataState";
import { services, visibilityApi, type RawResponseItem } from "../../lib/api";
import { useAsyncData } from "../../lib/useAsyncData";

const PAGE_SIZE = 8;

export function VisibilityPanel() {
  const [query, setQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const state = useAsyncData(
    () => visibilityApi.rawResponses({ q: query, limit: PAGE_SIZE, offset }),
    [query, offset]
  );

  const selected = useMemo(() => {
    return state.data?.items.find((item) => item.id === selectedId) ?? state.data?.items[0] ?? null;
  }, [selectedId, state.data]);

  if (state.isLoading && !state.data) {
    return <LoadingState title="Loading raw visibility responses" />;
  }

  if (state.error) {
    return (
      <ErrorState
        title="Visibility service unavailable"
        description={`${state.error}. Expected ${services.visibilityBaseUrl}.`}
        onAction={() => void state.reload()}
      />
    );
  }

  const page = state.data;
  if (!page) {
    return (
      <EmptyState
        title="No raw response data"
        description="Refresh after visibility-service is running."
        actionLabel="Refresh"
        onAction={() => void state.reload()}
      />
    );
  }

  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;
  const totalPages = Math.max(1, Math.ceil(page.total / PAGE_SIZE));

  return (
    <section className="content-grid">
      <div className="panel span-2">
        <div className="panel-header toolbar-header">
          <div>
            <h2>Raw model responses</h2>
            <p className="muted">{page.total} responses indexed</p>
          </div>
          <div className="toolbar-controls">
            <input
              aria-label="Search raw responses"
              className="search-input"
              onChange={(event) => {
                setQuery(event.target.value);
                setOffset(0);
              }}
              placeholder="Search model, prompt, or output"
              value={query}
            />
            <button type="button" onClick={() => void state.reload()}>
              Refresh
            </button>
          </div>
        </div>

        {page.items.length === 0 ? (
          <EmptyState
            title="No matching raw responses"
            description="Adjust the search query or create a visibility run."
          />
        ) : (
          <div className="raw-list">
            {page.items.map((row) => (
              <button
                className={row.id === selected?.id ? "raw-row active" : "raw-row"}
                key={row.id}
                onClick={() => setSelectedId(row.id)}
                type="button"
              >
                <div>
                  <span className="badge neutral">{row.model_id}</span>
                  <h3>{row.prompt_text}</h3>
                  <p>{row.output_text}</p>
                </div>
                <span className="mono-cell">{row.latency_ms}ms</span>
              </button>
            ))}
          </div>
        )}

        <div className="pagination-bar">
          <button
            type="button"
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
          >
            Previous
          </button>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <button
            type="button"
            disabled={offset + PAGE_SIZE >= page.total}
            onClick={() => setOffset(offset + PAGE_SIZE)}
          >
            Next
          </button>
        </div>
      </div>

      <RawResponseDetail item={selected} />
    </section>
  );
}

function RawResponseDetail({ item }: { item: RawResponseItem | null }) {
  if (!item) {
    return (
      <div className="panel">
        <EmptyState title="No response selected" description="Select a raw response to inspect." />
      </div>
    );
  }

  return (
    <aside className="panel detail-panel">
      <div className="panel-header">
        <h2>Evidence detail</h2>
        <span className="badge success">{item.status}</span>
      </div>
      <dl className="detail-list">
        <div>
          <dt>Raw response</dt>
          <dd className="mono-cell">{item.id}</dd>
        </div>
        <div>
          <dt>Provider response</dt>
          <dd>{item.provider_response_id ?? "not provided"}</dd>
        </div>
        <div>
          <dt>Model</dt>
          <dd>{item.model_id}</dd>
        </div>
        <div>
          <dt>Usage</dt>
          <dd>{jsonPreview(item.usage_json)}</dd>
        </div>
      </dl>
      <h3>Output</h3>
      <p className="response-text">{item.output_text}</p>
      <h3>Raw request</h3>
      <pre>{jsonPreview(item.raw_request_json)}</pre>
    </aside>
  );
}

function jsonPreview(value: Record<string, unknown>): string {
  return JSON.stringify(value, null, 2);
}
