# Brandlight AI Visibility Demo

## System Diagram

```mermaid
flowchart LR
  UI[React Vite UI] --> Config[Config Service]
  UI --> Visibility[Visibility Service]
  UI --> Insights[Insights Service]

  Config --> DB[(Postgres)]
  Visibility --> DB
  Insights --> DB

  Visibility --> Worker[Visibility Worker]
  Worker --> Adapter[Provider Adapter]
  Adapter --> OpenAI[OpenAI API]
  Adapter --> Fake[Demo Provider]
```

## Evidence Pipeline

```mermaid
flowchart LR
  C[Config: brand, product, prompts, models, rate limits]
  S[Run snapshot]
  Q[Queue items]
  A[AI request]
  R[Immutable raw response]
  I[Versioned insights]
  E[Evidence link back to response]

  C --> S --> Q --> A --> R --> I --> E
```

## Service Boundaries

```mermaid
flowchart TB
  subgraph Config
    Brands[Brands and products]
    Prompts[Prompt versions]
    Models[Provider models and rate limits]
    Tokens[Provider tokens]
  end

  subgraph Visibility
    Batches[Run batches]
    Queue[Run items]
    Raw[Raw requests and responses]
    Idem[Idempotency keys]
  end

  subgraph Insights
    Extract[Extraction runs]
    Mentions[Brand and competitor mentions]
    Domains[Citation domains]
    Links[Evidence links]
  end

  Config --> Visibility --> Insights
```

## Live Demo Flow

```mermaid
flowchart LR
  Start[Architecture]
  ConfigTab[Config tab]
  QueueTab[Queue tab]
  VisibilityTab[Visibility tab]
  InsightsTab[Insights tab]
  Source[Jump to raw source]

  Start --> ConfigTab --> QueueTab --> VisibilityTab --> InsightsTab --> Source
```

## Critical Talking Points

- Config is the source of truth: brands, products, prompts, models, tokens, and rate limits are database configuration, not code constants.
- Visibility is evidence-first: every AI answer is stored as an immutable raw response with request payload, provider metadata, usage, latency, and idempotency key.
- Provider calls are isolated behind one adapter contract, so execution logic does not depend on OpenAI-specific API details.
- Queue execution is async and observable: batches, items, retries, failures, and model status are visible in the UI.
- Insights are derived and versioned: deterministic extraction produces repeatable numbers and links every finding back to raw response evidence.
- OpenSpec was used milestone by milestone to capture intended behavior before implementation.
