# System Architecture Demo

Use this document to explain why the project is shaped as a small evidence-first
AI visibility platform.

## One-Sentence Story

A marketing or product operator defines what to measure, the system runs the
measurement asynchronously across configured AI models, stores raw AI responses
as immutable evidence, and derives explainable insights from that evidence.

## Service Boundaries

```text
React/Vite UI
  -> Config service
  -> Visibility service
  -> Insights service

Visibility worker
  -> provider-neutral AI adapter
  -> OpenAI or fake provider

Postgres
  -> config schema
  -> visibility schema
  -> insights schema
```

## Responsibilities

- Config service owns brands, products, competitors, prompt sets, prompt
  versions, provider metadata, model registry entries, and rate limits.
- Visibility service owns run batches, run items, queue state, model errors,
  raw requests, raw responses, usage, latency, and idempotency keys.
- Worker owns execution only. It claims queue items, consults rate limits, calls
  the provider-neutral adapter, and writes results through the visibility
  service persistence path.
- Insights service owns derived extraction runs, mentions, citations, summaries,
  and extraction versions.
- UI owns the operator workflow: Config, Queue, Visibility, and Insights.

## Data Lineage

```text
Config records
  -> immutable run snapshot
  -> queue item
  -> provider-neutral AI request
  -> raw response evidence
  -> extraction run
  -> visibility summary
```

## Important Bullets

- Config can change, but historical run snapshots keep their meaning.
- Prompts are versioned DB records, not source-code constants.
- Raw responses are immutable evidence.
- Raw response writes are idempotent by run/prompt/provider/model/sample.
- Insights are derived, versioned, and traceable to raw response IDs.
- Provider/model execution is behind one adapter contract.
- Rate limits are configurable per provider/model.
- Automated tests use fake providers or Cypress intercepts, not real OpenAI
  calls.
