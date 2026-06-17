import { useState } from "react";
import { ConfigPanel } from "../features/config/ConfigPanel";
import { InsightsPanel } from "../features/insights/InsightsPanel";
import { DemoOverview } from "../features/overview/DemoOverview";
import { QueuePanel } from "../features/queue/QueuePanel";
import { VisibilityPanel } from "../features/visibility/VisibilityPanel";

type TabId = "config" | "queue" | "visibility" | "insights";

const tabs: Array<{ id: TabId; label: string }> = [
  { id: "config", label: "Config" },
  { id: "queue", label: "Queue" },
  { id: "visibility", label: "Visibility" },
  { id: "insights", label: "Insights" }
];

export function App() {
  const [activeTab, setActiveTab] = useState<TabId>("config");
  const [focusedRawResponseId, setFocusedRawResponseId] = useState<string | null>(null);

  function openRawResponse(rawResponseId: string) {
    setFocusedRawResponseId(rawResponseId);
    setActiveTab("visibility");
  }

  function selectTab(tabId: TabId) {
    if (tabId === activeTab) {
      return;
    }
    setActiveTab(tabId);
    window.requestAnimationFrame(() => {
      window.scrollTo({ top: 0, behavior: "auto" });
    });
  }

  return (
    <div className="app-shell">
      <aside className="side-rail">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true" />
          <div>
            <strong>Brandlight</strong>
            <span>Enterprise AI search</span>
          </div>
        </div>

        <nav className="tab-list" aria-label="Primary">
          {tabs.map((tab) => (
            <button
              className={tab.id === activeTab ? "tab-button active" : "tab-button"}
              data-cy={`tab-${tab.id}`}
              key={tab.id}
              onClick={() => selectTab(tab.id)}
              type="button"
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-panel">
        <header className="top-bar">
          <div>
            <p className="eyebrow">AI search visibility</p>
            <h1>Visibility for enterprise brands</h1>
          </div>
          <div className="header-actions" aria-label="Dashboard filters">
            <span className="filter-chip">Israel</span>
            <span className="filter-chip">All engines</span>
            <span className="filter-chip">Last 30 days</span>
            <div className="status-strip" aria-label="System status">
              <span className="status-dot" />
              <span>Local foundation</span>
            </div>
          </div>
        </header>

        <DemoOverview />

        <div className="tab-panel" hidden={activeTab !== "config"}>
          <ConfigPanel />
        </div>
        <div className="tab-panel" hidden={activeTab !== "queue"}>
          <QueuePanel />
        </div>
        <div className="tab-panel" hidden={activeTab !== "visibility"}>
          <VisibilityPanel focusedRawResponseId={focusedRawResponseId} />
        </div>
        <div className="tab-panel" hidden={activeTab !== "insights"}>
          <InsightsPanel onOpenRawResponse={openRawResponse} />
        </div>
      </main>
    </div>
  );
}
