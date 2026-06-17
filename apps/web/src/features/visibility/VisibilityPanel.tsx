import { useEffect, useMemo, useRef, useState, type RefObject } from "react";
import { EmptyState, ErrorState, LoadingState } from "../../components/DataState";
import { services, visibilityApi, type RawResponseItem } from "../../lib/api";
import { useAsyncData } from "../../lib/useAsyncData";

const PAGE_SIZE = 8;

export function VisibilityPanel({
  focusedRawResponseId
}: {
  focusedRawResponseId?: string | null;
}) {
  const [query, setQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(focusedRawResponseId ?? null);
  const detailRef = useRef<HTMLElement | null>(null);
  const state = useAsyncData(
    () => visibilityApi.rawResponses({ q: query, limit: PAGE_SIZE, offset }),
    [query, offset]
  );
  const focusedState = useAsyncData(
    () => (focusedRawResponseId ? visibilityApi.rawResponse(focusedRawResponseId) : Promise.resolve(null)),
    [focusedRawResponseId]
  );

  useEffect(() => {
    if (!focusedRawResponseId) {
      return;
    }
    setSelectedId(focusedRawResponseId);
    setQuery("");
    setOffset(0);
    const frame = window.requestAnimationFrame(scrollDetailIntoView);
    const timer = window.setTimeout(scrollDetailIntoView, 80);
    return () => {
      window.cancelAnimationFrame(frame);
      window.clearTimeout(timer);
    };
  }, [focusedRawResponseId]);

  const selected = useMemo(() => {
    const pageSelected = state.data?.items.find((item) => item.id === selectedId) ?? null;
    const focusedSelected =
      focusedState.data && focusedState.data.id === selectedId ? focusedState.data : null;
    if (focusedSelected) {
      return focusedSelected;
    }
    if (pageSelected) {
      return pageSelected;
    }
    return selectedId ? null : state.data?.items[0] ?? null;
  }, [focusedState.data, selectedId, state.data]);

  useEffect(() => {
    if (!focusedRawResponseId || selected?.id !== focusedRawResponseId || focusedState.isLoading) {
      return;
    }
    const timer = window.setTimeout(scrollDetailIntoView, 0);
    return () => window.clearTimeout(timer);
  }, [focusedRawResponseId, focusedState.isLoading, selected?.id]);

  function scrollDetailIntoView() {
    const node = detailRef.current;
    if (!node) {
      return;
    }
    const stickyHeaderOffset = 96;
    const targetTop = node.getBoundingClientRect().top + window.scrollY - stickyHeaderOffset;
    window.scrollTo({ top: Math.max(0, targetTop), behavior: "auto" });
  }

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
  const modelSummaries = summarizeModels(page.items);

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
          <div className="raw-list" data-cy="raw-response-list">
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

      <div className="panel" data-cy="model-comparison">
        <div className="panel-header">
          <h2>Current-page model comparison</h2>
        </div>
        <div className="record-list">
          {modelSummaries.map((model) => (
            <div className="compact-row" key={model.modelId}>
              <div>
                <strong>{model.modelId}</strong>
                <span>{model.count} raw responses</span>
              </div>
              <span className="badge neutral">{model.averageLatencyMs}ms avg</span>
            </div>
          ))}
          {modelSummaries.length === 0 ? (
            <EmptyState title="No model data" description="Create a run to compare model outputs." />
          ) : null}
        </div>
      </div>

      <RawResponseDetail
        detailRef={detailRef}
        item={selected}
        isLoading={
          Boolean(selectedId && selectedId === focusedRawResponseId) &&
          focusedState.isLoading &&
          !focusedState.data
        }
        error={selectedId === focusedRawResponseId ? focusedState.error : null}
        onRetry={() => void focusedState.reload()}
      />
    </section>
  );
}

function RawResponseDetail({
  detailRef,
  error,
  isLoading,
  item,
  onRetry
}: {
  detailRef: RefObject<HTMLElement | null>;
  error: string | null;
  isLoading: boolean;
  item: RawResponseItem | null;
  onRetry: () => void;
}) {
  return (
    <aside className="panel detail-panel" data-cy="raw-response-detail" ref={detailRef}>
      {isLoading ? <LoadingState title="Opening linked raw response" /> : null}
      {error ? (
        <ErrorState
          title="Linked raw response unavailable"
          description={error}
          onAction={onRetry}
        />
      ) : null}
      {!isLoading && !error && !item ? (
        <EmptyState title="No response selected" description="Select a raw response to inspect." />
      ) : null}
      {!isLoading && !error && item ? (
        <>
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
              <dt>Run item</dt>
              <dd className="mono-cell">{item.run_item_id}</dd>
            </div>
            <div>
              <dt>Idempotency key</dt>
              <dd className="mono-cell">{item.idempotency_key}</dd>
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
          <h3>Raw response</h3>
          <pre>{jsonPreview(item.raw_response_json)}</pre>
        </>
      ) : null}
    </aside>
  );
}

function jsonPreview(value: Record<string, unknown>): string {
  return JSON.stringify(value, null, 2);
}

function summarizeModels(items: RawResponseItem[]) {
  const grouped = new Map<string, { count: number; latency: number }>();
  for (const item of items) {
    const current = grouped.get(item.model_id) ?? { count: 0, latency: 0 };
    grouped.set(item.model_id, {
      count: current.count + 1,
      latency: current.latency + item.latency_ms
    });
  }
  return [...grouped.entries()].map(([modelId, value]) => ({
    modelId,
    count: value.count,
    averageLatencyMs: Math.round(value.latency / value.count)
  }));
}
