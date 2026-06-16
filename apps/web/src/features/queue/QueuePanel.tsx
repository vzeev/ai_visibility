import { useState } from "react";
import { EmptyState, ErrorState, LoadingState } from "../../components/DataState";
import { configApi, services, visibilityApi, type PromptSet } from "../../lib/api";
import { useAsyncData } from "../../lib/useAsyncData";

export function QueuePanel() {
  const state = useAsyncData(loadQueueData, []);
  const [brandId, setBrandId] = useState("");
  const [promptSetId, setPromptSetId] = useState("");
  const [sampleCount, setSampleCount] = useState(1);
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  if (state.isLoading && !state.data) {
    return <LoadingState title="Loading visibility queue" />;
  }

  if (state.error) {
    return (
      <ErrorState
        title="Visibility APIs unavailable"
        description={`${state.error}. Expected ${services.visibilityBaseUrl} and ${services.configBaseUrl}.`}
        onAction={() => void state.reload()}
      />
    );
  }

  if (!state.data) {
    return (
      <EmptyState
        title="No queue data"
        description="Refresh after starting local services."
        actionLabel="Refresh"
        onAction={() => void state.reload()}
      />
    );
  }

  const { queue, runs, brands, promptSets } = state.data;
  const selectedBrandId = brandId || brands[0]?.id || "";
  const promptSetsForBrand = promptSets.filter((set) => set.brand_id === selectedBrandId);
  const selectedPromptSetId = promptSetId || promptSetsForBrand[0]?.id || promptSets[0]?.id || "";

  async function createRun() {
    if (!selectedBrandId || !selectedPromptSetId) {
      setCreateError("Select a brand and prompt set first.");
      return;
    }
    setIsCreating(true);
    setCreateError(null);
    try {
      await visibilityApi.createRun({
        brand_id: selectedBrandId,
        prompt_set_id: selectedPromptSetId,
        sample_count: sampleCount,
        max_attempts: 3
      });
      await state.reload();
    } catch (caught) {
      setCreateError(caught instanceof Error ? caught.message : "Run creation failed");
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <section className="content-grid">
      <Metric label="Pending" value={queue.pending} />
      <Metric label="Running" value={queue.running} />
      <Metric label="Throttled" value={queue.throttled} />
      <Metric label="Succeeded" value={queue.succeeded} />

      <div className="panel span-2">
        <div className="panel-header">
          <h2>Create visibility run</h2>
          <button type="button" onClick={() => void state.reload()}>
            Refresh
          </button>
        </div>
        <div className="form-grid">
          <label>
            Brand
            <select
              value={selectedBrandId}
              onChange={(event) => {
                setBrandId(event.target.value);
                setPromptSetId("");
              }}
            >
              {brands.map((brand) => (
                <option key={brand.id} value={brand.id}>
                  {brand.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Prompt set
            <select
              value={selectedPromptSetId}
              onChange={(event) => setPromptSetId(event.target.value)}
            >
              {promptSetsForBrand.length === 0 ? (
                <option value="">No prompt sets</option>
              ) : (
                promptSetsForBrand.map((set) => (
                  <option key={set.id} value={set.id}>
                    {set.name}
                  </option>
                ))
              )}
            </select>
          </label>
          <label>
            Samples
            <input
              min={1}
              max={10}
              type="number"
              value={sampleCount}
              onChange={(event) => setSampleCount(Number(event.target.value))}
            />
          </label>
          <div className="form-action">
            <button type="button" disabled={isCreating} onClick={() => void createRun()}>
              {isCreating ? "Creating" : "Create run"}
            </button>
          </div>
        </div>
        {createError ? <p className="inline-error">{createError}</p> : null}
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Queue health</h2>
        </div>
        <div className="queue-health">
          <div>
            <span>Failed</span>
            <strong>{queue.failed}</strong>
          </div>
          <div>
            <span>Total active</span>
            <strong>{queue.pending + queue.running + queue.throttled}</strong>
          </div>
        </div>
      </div>

      <div className="panel span-3">
        <div className="panel-header">
          <h2>Run batches</h2>
        </div>
        {runs.length === 0 ? (
          <EmptyState title="No run batches" description="Create a run to populate the queue." />
        ) : (
          <table>
            <thead>
              <tr>
                <th>Run</th>
                <th>Brand</th>
                <th>Prompt set</th>
                <th>Status</th>
                <th>Items</th>
              </tr>
            </thead>
            <tbody>
              {runs.slice(0, 12).map((run) => (
                <tr key={run.id}>
                  <td className="mono-cell">{shortId(run.id)}</td>
                  <td>{nameById(brands, run.brand_id)}</td>
                  <td>{promptSetName(promptSets, run.prompt_set_id)}</td>
                  <td>
                    <span className={`badge ${run.status}`}>{run.status}</span>
                  </td>
                  <td>{run.item_count ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
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

async function loadQueueData() {
  const [queue, runs, brands, promptSets] = await Promise.all([
    visibilityApi.queue(),
    visibilityApi.runs(),
    configApi.brands(),
    configApi.promptSets()
  ]);
  return { queue, runs, brands, promptSets };
}

function nameById(items: Array<{ id: string; name: string }>, id: string): string {
  return items.find((item) => item.id === id)?.name ?? shortId(id);
}

function promptSetName(promptSets: PromptSet[], id: string): string {
  return promptSets.find((set) => set.id === id)?.name ?? shortId(id);
}

function shortId(id: string): string {
  return id.slice(0, 8);
}
