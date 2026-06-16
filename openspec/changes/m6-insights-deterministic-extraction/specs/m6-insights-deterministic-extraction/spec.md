# M6 Insights Deterministic Extraction Spec

## ADDED Requirements

### Requirement: Deterministic Extraction Creates Versioned Insight Runs

The insights service SHALL create a versioned extraction run for persisted raw
visibility responses.

#### Scenario: Extraction Run Is Created

- **WHEN** a client requests extraction for a raw response or run batch
- **THEN** the system creates or reuses an `insights.extraction_runs` record
- **AND** the record stores the requested `extraction_version`
- **AND** the raw response remains unchanged.

### Requirement: Mention Records Link Back To Raw Evidence

Deterministic mention extraction SHALL persist brand and competitor mentions
with evidence that references the originating raw response.

#### Scenario: Mention Evidence Is Stored

- **WHEN** deterministic extraction finds a mention in response output text
- **THEN** it stores an `insights.extracted_mentions` row
- **AND** `evidence_json` includes the originating `raw_response_id`
- **AND** the stored mention text comes from the raw response content.

### Requirement: Citation Records Are Parsed Deterministically

The insights service SHALL extract citations and domains from raw response
content without relying on an LLM.

#### Scenario: Citation URL Appears In Output

- **WHEN** the raw response output contains one or more URLs
- **THEN** the system stores `insights.extracted_citations` rows with normalized
  `url`, `domain`, and evidence references to the originating raw response.

### Requirement: Visibility Summaries Remain Evidence-Linked Derived State

The insights service SHALL persist versioned visibility summaries derived from
raw responses and extracted artifacts.

#### Scenario: Summary Is Built For A Run Batch

- **WHEN** extraction completes for raw responses in a run batch
- **THEN** the service stores an `insights.visibility_summaries` row for that
  brand/run batch/version combination
- **AND** the summary payload includes raw response ids and aggregate counts
  needed to explain the derived result.

### Requirement: Extraction Reruns Are Idempotent Per Version

Extraction for the same raw response and extraction version SHALL be idempotent.

#### Scenario: Same Version Is Requested Again

- **WHEN** extraction is requested again for the same raw response and
  `extraction_version`
- **THEN** the existing extraction run and derived rows are reused or replaced
  without creating duplicate version rows for that raw response/version pair.
