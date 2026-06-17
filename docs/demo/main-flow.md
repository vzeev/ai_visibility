# Main Demo Flow

This is the live interview walkthrough.

## 1. Start With The Product Problem

Brands need to know how AI systems describe them, which competitors appear, and
which sources/citations influence answers. The key product constraint is that AI
answers are unstable, so the system must preserve raw evidence and make derived
insights traceable.

## 2. Show Architecture

Open `docs/demo/system-architecture.md`.

Narrate:

- Config is source of truth for what to measure.
- Visibility is source of truth for raw collection evidence.
- Insights are derived and versioned.
- Worker execution is async and provider-neutral.

## 3. Show Implementation Discipline

Open `docs/demo/technical-implementation.md`.

Narrate:

- OpenSpec captured each milestone.
- Contracts and migrations came before runtime behavior.
- Tests are layered: unit, service, integration, Cypress.

## 4. Run Or Validate The Stack

```bash
poetry run dev
poetry run demo-e2e --skip-migrations
poetry run demo-check
```

Open:

```text
http://127.0.0.1:5173
```

## 5. Config Tab

Show:

- Brandlight as the demo brand.
- Prompt sets and prompt versions.
- Provider credential metadata with redacted token readback.
- Rate-limit policies.
- OpenAI model sync.
- Model enable/disable controls. Disable fake/demo models and enable the real
  OpenAI model selected for the walkthrough.

Talking point:

> Prompts, models, credentials, and rate limits are configuration, not code.

## 6. Queue Tab

Show:

- Queue counts.
- Run creation.
- Expansion from prompts x enabled models x sample count.
- Run batches and statuses.

Talking point:

> The queue makes rate limits, retries, and failures observable instead of
> hiding model execution behind one synchronous API call.

## 7. Visibility Tab

Show:

- Searchable raw responses.
- Model comparison summary.
- Raw response ID.
- Run item ID.
- Idempotency key.
- Raw request JSON.
- Raw response JSON.
- Usage and latency.

Talking point:

> The raw response is the evidence. Everything else is derived from it.

## 8. Insights Tab

Show:

- Deterministic extraction summary.
- Brand mentions.
- Competitor mentions.
- Citation domains.
- Evidence links.
- Extraction run details.

Talking point:

> Deterministic extraction is intentionally repeatable. AI-assisted extraction
> can be added later behind the same raw-to-derived versioned boundary.

## 9. Automated Browser Validation

Run:

```bash
poetry run web-e2e
```

For direct web workspace debugging, after the Vite app is already running:

```bash
cd apps/web
npm run cy:run
```

The Cypress test uses deterministic API intercepts and validates the same
operator journey: Overview, Config, Queue, Visibility, and Insights.
