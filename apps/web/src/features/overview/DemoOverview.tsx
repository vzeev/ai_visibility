import { configApi, insightsApi, services, visibilityApi, type RunBatch } from "../../lib/api";
import { useAsyncData } from "../../lib/useAsyncData";

export function DemoOverview() {
  const state = useAsyncData(loadOverview, []);

  if (state.isLoading && !state.data) {
    return (
      <section className="demo-overview" aria-label="Demo readiness">
        <div className="overview-tile">
          <span>Pipeline</span>
          <strong>Loading</strong>
        </div>
      </section>
    );
  }

  if (state.error) {
    return (
      <section className="demo-overview" aria-label="Demo readiness">
        <div className="overview-tile warning">
          <span>Services</span>
          <strong>Offline</strong>
          <em>{services.configBaseUrl}</em>
        </div>
      </section>
    );
  }

  if (!state.data) {
    return null;
  }

  const { brandName, enabledModelCount, latestRun, promptCount, queueActive, rawCount, summary } =
    state.data;
  const brandMentions = numberValue(summary?.summary_json.brand_mentions);
  const competitorMentions = numberValue(summary?.summary_json.competitor_mentions);

  return (
    <section className="demo-overview" aria-label="Demo readiness">
      <div className="overview-tile primary">
        <span>Demo brand</span>
        <strong>{brandName}</strong>
        <em>
          {promptCount} prompts · {enabledModelCount} models
        </em>
      </div>
      <div className="overview-tile">
        <span>Latest run</span>
        <strong>{latestRun ? latestRun.status : "No runs"}</strong>
        <em>{latestRun ? shortId(latestRun.id) : `${queueActive} active items`}</em>
      </div>
      <div className="overview-tile">
        <span>Raw evidence</span>
        <strong>{rawCount}</strong>
        <em>stored responses</em>
      </div>
      <div className="overview-tile insight">
        <span>Insights</span>
        <strong>{brandMentions + competitorMentions}</strong>
        <em>{summary ? `${brandMentions} brand · ${competitorMentions} competitor` : "No summary"}</em>
      </div>
    </section>
  );
}

async function loadOverview() {
  const [brands, prompts, models, queue, runs, rawPage, summaries] = await Promise.all([
    configApi.brands(),
    configApi.prompts(),
    configApi.models(),
    visibilityApi.queue(),
    visibilityApi.runs(),
    visibilityApi.rawResponses({ limit: 1, offset: 0 }),
    insightsApi.summaries()
  ]);
  const primaryBrand = brands.find((brand) => brand.name === "Brandlight") ?? brands[0] ?? null;
  const latestRun = runs[0] ?? null;
  const summary = summaries[0] ?? null;
  return {
    brandName: primaryBrand?.name ?? "No brand",
    enabledModelCount: models.filter((model) => model.enabled_for_visibility).length,
    latestRun,
    promptCount: prompts.length,
    queueActive: queue.pending + queue.running + queue.throttled,
    rawCount: rawPage.total,
    summary
  };
}

function shortId(id: string): string {
  return id.slice(0, 8);
}

function numberValue(value: unknown): number {
  return typeof value === "number" ? value : 0;
}
