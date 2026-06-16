# M9 UI Demo Polish Spec

## ADDED Requirements

### Requirement: Live Demo Overview

The dashboard SHALL show a live overview of demo readiness across configuration, queue/raw evidence, and insights.

#### Scenario: Open dashboard with seeded demo data

- GIVEN local services are running and M8 demo data exists
- WHEN the operator opens the dashboard
- THEN the first screen shows Brandlight config readiness, latest run status, raw response count, and insight summary count.

### Requirement: Raw Evidence Drilldown

The Visibility tab SHALL make raw evidence suitable for demo inspection.

#### Scenario: Inspect raw response

- GIVEN raw responses exist
- WHEN the operator selects a raw response
- THEN the detail panel shows raw response ID, run item ID, idempotency key, model, provider response ID, usage, raw request, and raw response.

### Requirement: UI-triggered Deterministic Extraction

The Insights tab SHALL let the operator run deterministic extraction for the latest completed visibility run.

#### Scenario: Analyze latest completed run

- GIVEN a succeeded visibility run exists with raw responses
- WHEN the operator triggers analysis from the Insights tab
- THEN the UI calls the existing insights run-batch extraction API
- AND refreshes summaries after the request succeeds
- AND presents inline success or error state.
