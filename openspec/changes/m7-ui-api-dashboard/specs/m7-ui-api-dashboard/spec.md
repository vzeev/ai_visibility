# M7 UI API Dashboard Spec

## ADDED Requirements

### Requirement: UI Reads Config Service Data

The dashboard Config tab SHALL read brands, prompt sets, prompts, providers,
credentials, rate limits, and models from config-service APIs.

#### Scenario: Config APIs Are Available

- **WHEN** the Config tab loads successfully
- **THEN** it shows API-backed configuration records
- **AND** it exposes refresh and empty/error states.

### Requirement: UI Shows Queue State And Run Creation

The Queue tab SHALL display visibility queue counts and run batches from
visibility-service APIs.

#### Scenario: Queue APIs Are Available

- **WHEN** the Queue tab loads successfully
- **THEN** it shows pending, running, throttled, succeeded, and failed counts
- **AND** it shows recent run batches
- **AND** it can create a run from selected brand and prompt set IDs.

### Requirement: UI Searches Raw Visibility Responses

The Visibility tab SHALL read raw responses through the visibility-service search
and pagination API.

#### Scenario: User Searches Raw Responses

- **WHEN** a user enters a search query
- **THEN** the UI requests filtered raw responses
- **AND** shows pagination and a readable detail view.

### Requirement: UI Reads Insights Summaries

The Insights tab SHALL read visibility summaries and extraction run details from
insights-service APIs.

#### Scenario: Insights Summaries Exist

- **WHEN** insights-service returns summaries
- **THEN** the UI shows aggregate counts, entity mentions, citation domains, raw
  response references, and extraction run detail.

### Requirement: UI Handles API Unavailability

The dashboard SHALL remain usable when one or more local backend services are
not running.

#### Scenario: API Request Fails

- **WHEN** a tab request fails
- **THEN** the tab shows a clear error state and a refresh action
- **AND** the rest of the dashboard shell remains usable.
